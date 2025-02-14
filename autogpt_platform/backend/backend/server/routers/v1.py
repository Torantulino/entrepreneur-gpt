import asyncio
import logging
from collections import defaultdict
from datetime import datetime
from typing import TYPE_CHECKING, Annotated, Any, Sequence

import pydantic
import stripe
from autogpt_libs.auth.middleware import auth_middleware
from autogpt_libs.feature_flag.client import feature_flag
from autogpt_libs.utils.cache import thread_cached
from fastapi import APIRouter, Body, Depends, HTTPException, Request, Response
from typing_extensions import Optional, TypedDict

import backend.data.block
import backend.server.integrations.router
import backend.server.routers.analytics
import backend.server.v2.library.db as library_db
from backend.data import graph as graph_db
from backend.data.api_key import (
    APIKeyError,
    APIKeyNotFoundError,
    APIKeyPermissionError,
    APIKeyWithoutHash,
    generate_api_key,
    get_api_key_by_id,
    list_user_api_keys,
    revoke_api_key,
    suspend_api_key,
    update_api_key_permissions,
)
from backend.data.block import BlockInput, CompletedBlockOutput
from backend.data.credit import (
    AutoTopUpConfig,
    TransactionHistory,
    get_auto_top_up,
    get_block_costs,
    get_stripe_customer_id,
    get_user_credit_model,
    set_auto_top_up,
)
from backend.data.user import get_or_create_user
from backend.executor import ExecutionManager, ExecutionScheduler, scheduler
from backend.integrations.creds_manager import IntegrationCredentialsManager
from backend.integrations.webhooks.graph_lifecycle_hooks import (
    on_graph_activate,
    on_graph_deactivate,
)
from backend.server.model import (
    CreateAPIKeyRequest,
    CreateAPIKeyResponse,
    CreateGraph,
    ExecuteGraphResponse,
    RequestTopUp,
    SetGraphActiveVersion,
    UpdatePermissionsRequest,
)
from backend.server.utils import get_user_id
from backend.util.service import get_service_client
from backend.util.settings import Settings

if TYPE_CHECKING:
    from backend.data.model import Credentials


@thread_cached
def execution_manager_client() -> ExecutionManager:
    return get_service_client(ExecutionManager)


@thread_cached
def execution_scheduler_client() -> ExecutionScheduler:
    return get_service_client(ExecutionScheduler)


settings = Settings()
logger = logging.getLogger(__name__)
integration_creds_manager = IntegrationCredentialsManager()

_user_credit_model = get_user_credit_model()

# Define the API routes
v1_router = APIRouter()

v1_router.include_router(
    backend.server.integrations.router.router,
    prefix="/integrations",
    tags=["integrations"],
)

v1_router.include_router(
    backend.server.routers.analytics.router,
    prefix="/analytics",
    tags=["analytics"],
    dependencies=[Depends(auth_middleware)],
)


########################################################
##################### Auth #############################
########################################################


@v1_router.post("/auth/user", tags=["auth"], dependencies=[Depends(auth_middleware)])
async def get_or_create_user_route(user_data: dict = Depends(auth_middleware)):
    user = await get_or_create_user(user_data)
    return user.model_dump()


########################################################
##################### Blocks ###########################
########################################################


@v1_router.get(path="/blocks", tags=["blocks"], dependencies=[Depends(auth_middleware)])
def get_graph_blocks() -> Sequence[dict[Any, Any]]:
    blocks = [block() for block in backend.data.block.get_blocks().values()]
    costs = get_block_costs()
    return [{**b.to_dict(), "costs": costs.get(b.id, [])} for b in blocks]


@v1_router.post(
    path="/blocks/{block_id}/execute",
    tags=["blocks"],
    dependencies=[Depends(auth_middleware)],
)
def execute_graph_block(block_id: str, data: BlockInput) -> CompletedBlockOutput:
    obj = backend.data.block.get_block(block_id)
    if not obj:
        raise HTTPException(status_code=404, detail=f"Block #{block_id} not found.")

    output = defaultdict(list)
    for name, data in obj.execute(data):
        output[name].append(data)
    return output


########################################################
##################### Credits ##########################
########################################################


@v1_router.get(path="/credits", dependencies=[Depends(auth_middleware)])
async def get_user_credits(
    user_id: Annotated[str, Depends(get_user_id)],
) -> dict[str, int]:
    # Credits can go negative, so ensure it's at least 0 for user to see.
    return {"credits": max(await _user_credit_model.get_credits(user_id), 0)}


@v1_router.post(
    path="/credits", tags=["credits"], dependencies=[Depends(auth_middleware)]
)
async def request_top_up(
    request: RequestTopUp, user_id: Annotated[str, Depends(get_user_id)]
):
    checkout_url = await _user_credit_model.top_up_intent(
        user_id, request.credit_amount
    )
    return {"checkout_url": checkout_url}


@v1_router.patch(
    path="/credits", tags=["credits"], dependencies=[Depends(auth_middleware)]
)
async def fulfill_checkout(user_id: Annotated[str, Depends(get_user_id)]):
    await _user_credit_model.fulfill_checkout(user_id=user_id)
    return Response(status_code=200)


@v1_router.post(
    path="/credits/auto-top-up",
    tags=["credits"],
    dependencies=[Depends(auth_middleware)],
)
async def configure_user_auto_top_up(
    request: AutoTopUpConfig, user_id: Annotated[str, Depends(get_user_id)]
) -> str:
    if request.threshold < 0:
        raise ValueError("Threshold must be greater than 0")
    if request.amount < 500 and request.amount != 0:
        raise ValueError("Amount must be greater than or equal to 500")
    if request.amount < request.threshold:
        raise ValueError("Amount must be greater than or equal to threshold")

    current_balance = await _user_credit_model.get_credits(user_id)

    if current_balance < request.threshold:
        await _user_credit_model.top_up_credits(user_id, request.amount)
    else:
        await _user_credit_model.top_up_credits(user_id, 0)

    await set_auto_top_up(
        user_id, AutoTopUpConfig(threshold=request.threshold, amount=request.amount)
    )
    return "Auto top-up settings updated"


@v1_router.get(
    path="/credits/auto-top-up",
    tags=["credits"],
    dependencies=[Depends(auth_middleware)],
)
async def get_user_auto_top_up(
    user_id: Annotated[str, Depends(get_user_id)]
) -> AutoTopUpConfig:
    return await get_auto_top_up(user_id)


@v1_router.post(path="/credits/stripe_webhook", tags=["credits"])
async def stripe_webhook(request: Request):
    # Get the raw request body
    payload = await request.body()
    # Get the signature header
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.secrets.stripe_webhook_secret
        )
    except ValueError:
        # Invalid payload
        raise HTTPException(status_code=400)
    except stripe.SignatureVerificationError:
        # Invalid signature
        raise HTTPException(status_code=400)

    if (
        event["type"] == "checkout.session.completed"
        or event["type"] == "checkout.session.async_payment_succeeded"
    ):
        await _user_credit_model.fulfill_checkout(
            session_id=event["data"]["object"]["id"]
        )

    return Response(status_code=200)


@v1_router.get(path="/credits/manage", dependencies=[Depends(auth_middleware)])
async def manage_payment_method(
    user_id: Annotated[str, Depends(get_user_id)],
) -> dict[str, str]:
    session = stripe.billing_portal.Session.create(
        customer=await get_stripe_customer_id(user_id),
        return_url=settings.config.frontend_base_url + "/marketplace/credits",
    )
    if not session:
        raise HTTPException(
            status_code=400, detail="Failed to create billing portal session"
        )
    return {"url": session.url}


@v1_router.get(path="/credits/transactions", dependencies=[Depends(auth_middleware)])
async def get_credit_history(
    user_id: Annotated[str, Depends(get_user_id)],
    transaction_time: datetime | None = None,
    transaction_count_limit: int = 100,
) -> TransactionHistory:
    if transaction_count_limit < 1 or transaction_count_limit > 1000:
        raise ValueError("Transaction count limit must be between 1 and 1000")

    return await _user_credit_model.get_transaction_history(
        user_id=user_id,
        transaction_time=transaction_time or datetime.max,
        transaction_count_limit=transaction_count_limit,
    )


########################################################
##################### Graphs ###########################
########################################################


class DeleteGraphResponse(TypedDict):
    version_counts: int


@v1_router.get(path="/graphs", tags=["graphs"], dependencies=[Depends(auth_middleware)])
async def get_graphs(
    user_id: Annotated[str, Depends(get_user_id)]
) -> Sequence[graph_db.GraphModel]:
    return await graph_db.get_graphs(filter_by="active", user_id=user_id)


@v1_router.get(
    path="/graphs/{graph_id}", tags=["graphs"], dependencies=[Depends(auth_middleware)]
)
@v1_router.get(
    path="/graphs/{graph_id}/versions/{version}",
    tags=["graphs"],
    dependencies=[Depends(auth_middleware)],
)
async def get_graph(
    graph_id: str,
    user_id: Annotated[str, Depends(get_user_id)],
    version: int | None = None,
    hide_credentials: bool = False,
) -> graph_db.GraphModel:
    graph = await graph_db.get_graph(
        graph_id, version, user_id=user_id, for_export=hide_credentials
    )
    if not graph:
        raise HTTPException(status_code=404, detail=f"Graph #{graph_id} not found.")
    return graph


@v1_router.get(
    path="/graphs/{graph_id}/versions",
    tags=["graphs"],
    dependencies=[Depends(auth_middleware)],
)
async def get_graph_all_versions(
    graph_id: str, user_id: Annotated[str, Depends(get_user_id)]
) -> Sequence[graph_db.GraphModel]:
    graphs = await graph_db.get_graph_all_versions(graph_id, user_id=user_id)
    if not graphs:
        raise HTTPException(status_code=404, detail=f"Graph #{graph_id} not found.")
    return graphs


@v1_router.post(
    path="/graphs", tags=["graphs"], dependencies=[Depends(auth_middleware)]
)
async def create_new_graph(
    create_graph: CreateGraph, user_id: Annotated[str, Depends(get_user_id)]
) -> graph_db.GraphModel:
    graph = graph_db.make_graph_model(create_graph.graph, user_id)
    graph.reassign_ids(user_id=user_id, reassign_graph_id=True)

    graph = await graph_db.create_graph(graph, user_id=user_id)

    # Create a library agent for the new graph
    await library_db.create_library_agent(
        graph.id,
        graph.version,
        user_id,
    )

    graph = await on_graph_activate(
        graph,
        get_credentials=lambda id: integration_creds_manager.get(user_id, id),
    )
    return graph


@v1_router.delete(
    path="/graphs/{graph_id}", tags=["graphs"], dependencies=[Depends(auth_middleware)]
)
async def delete_graph(
    graph_id: str, user_id: Annotated[str, Depends(get_user_id)]
) -> DeleteGraphResponse:
    if active_version := await graph_db.get_graph(graph_id, user_id=user_id):

        def get_credentials(credentials_id: str) -> "Credentials | None":
            return integration_creds_manager.get(user_id, credentials_id)

        await on_graph_deactivate(active_version, get_credentials)

    return {"version_counts": await graph_db.delete_graph(graph_id, user_id=user_id)}


@v1_router.put(
    path="/graphs/{graph_id}", tags=["graphs"], dependencies=[Depends(auth_middleware)]
)
async def update_graph(
    graph_id: str,
    graph: graph_db.Graph,
    user_id: Annotated[str, Depends(get_user_id)],
) -> graph_db.GraphModel:
    # Sanity check
    if graph.id and graph.id != graph_id:
        raise HTTPException(400, detail="Graph ID does not match ID in URI")

    # Determine new version
    existing_versions = await graph_db.get_graph_all_versions(graph_id, user_id=user_id)
    if not existing_versions:
        raise HTTPException(404, detail=f"Graph #{graph_id} not found")
    latest_version_number = max(g.version for g in existing_versions)
    graph.version = latest_version_number + 1

    latest_version_graph = next(
        v for v in existing_versions if v.version == latest_version_number
    )
    current_active_version = next((v for v in existing_versions if v.is_active), None)
    if latest_version_graph.is_template != graph.is_template:
        raise HTTPException(
            400, detail="Changing is_template on an existing graph is forbidden"
        )
    graph.is_active = not graph.is_template
    graph = graph_db.make_graph_model(graph, user_id)
    graph.reassign_ids(user_id=user_id)

    new_graph_version = await graph_db.create_graph(graph, user_id=user_id)

    if new_graph_version.is_active:
        # Keep the library agent up to date with the new active version
        await library_db.update_agent_version_in_library(
            user_id, graph.id, graph.version
        )

        def get_credentials(credentials_id: str) -> "Credentials | None":
            return integration_creds_manager.get(user_id, credentials_id)

        # Handle activation of the new graph first to ensure continuity
        new_graph_version = await on_graph_activate(
            new_graph_version,
            get_credentials=get_credentials,
        )
        # Ensure new version is the only active version
        await graph_db.set_graph_active_version(
            graph_id=graph_id, version=new_graph_version.version, user_id=user_id
        )
        if current_active_version:
            # Handle deactivation of the previously active version
            await on_graph_deactivate(
                current_active_version,
                get_credentials=get_credentials,
            )

    return new_graph_version


@v1_router.put(
    path="/graphs/{graph_id}/versions/active",
    tags=["graphs"],
    dependencies=[Depends(auth_middleware)],
)
async def set_graph_active_version(
    graph_id: str,
    request_body: SetGraphActiveVersion,
    user_id: Annotated[str, Depends(get_user_id)],
):
    new_active_version = request_body.active_graph_version
    new_active_graph = await graph_db.get_graph(
        graph_id, new_active_version, user_id=user_id
    )
    if not new_active_graph:
        raise HTTPException(404, f"Graph #{graph_id} v{new_active_version} not found")

    current_active_graph = await graph_db.get_graph(graph_id, user_id=user_id)

    def get_credentials(credentials_id: str) -> "Credentials | None":
        return integration_creds_manager.get(user_id, credentials_id)

    # Handle activation of the new graph first to ensure continuity
    await on_graph_activate(
        new_active_graph,
        get_credentials=get_credentials,
    )
    # Ensure new version is the only active version
    await graph_db.set_graph_active_version(
        graph_id=graph_id,
        version=new_active_version,
        user_id=user_id,
    )

    # Keep the library agent up to date with the new active version
    await library_db.update_agent_version_in_library(
        user_id, new_active_graph.id, new_active_graph.version
    )

    if current_active_graph and current_active_graph.version != new_active_version:
        # Handle deactivation of the previously active version
        await on_graph_deactivate(
            current_active_graph,
            get_credentials=get_credentials,
        )


@v1_router.post(
    path="/graphs/{graph_id}/execute/{graph_version}",
    tags=["graphs"],
    dependencies=[Depends(auth_middleware)],
)
def execute_graph(
    graph_id: str,
    node_input: Annotated[dict[str, Any], Body(..., embed=True, default_factory=dict)],
    user_id: Annotated[str, Depends(get_user_id)],
    graph_version: Optional[int] = None,
) -> ExecuteGraphResponse:
    try:
        graph_exec = execution_manager_client().add_execution(
            graph_id, node_input, user_id=user_id, graph_version=graph_version
        )
        return ExecuteGraphResponse(graph_exec_id=graph_exec.graph_exec_id)
    except Exception as e:
        msg = str(e).encode().decode("unicode_escape")
        raise HTTPException(status_code=400, detail=msg)


@v1_router.post(
    path="/graphs/{graph_id}/executions/{graph_exec_id}/stop",
    tags=["graphs"],
    dependencies=[Depends(auth_middleware)],
)
async def stop_graph_run(
    graph_exec_id: str, user_id: Annotated[str, Depends(get_user_id)]
) -> graph_db.GraphExecution:
    if not await graph_db.get_execution_meta(
        user_id=user_id, execution_id=graph_exec_id
    ):
        raise HTTPException(404, detail=f"Agent execution #{graph_exec_id} not found")

    await asyncio.to_thread(
        lambda: execution_manager_client().cancel_execution(graph_exec_id)
    )

    # Retrieve & return canceled graph execution in its final state
    result = await graph_db.get_execution(execution_id=graph_exec_id, user_id=user_id)
    if not result:
        raise HTTPException(
            500,
            detail=f"Could not fetch graph execution #{graph_exec_id} after stopping",
        )
    return result


@v1_router.get(
    path="/executions",
    tags=["graphs"],
    dependencies=[Depends(auth_middleware)],
)
async def get_graphs_executions(
    user_id: Annotated[str, Depends(get_user_id)],
) -> list[graph_db.GraphExecutionMeta]:
    return await graph_db.get_graphs_executions(user_id=user_id)


@v1_router.get(
    path="/graphs/{graph_id}/executions",
    tags=["graphs"],
    dependencies=[Depends(auth_middleware)],
)
async def get_graph_executions(
    graph_id: str,
    user_id: Annotated[str, Depends(get_user_id)],
) -> list[graph_db.GraphExecutionMeta]:
    return await graph_db.get_graph_executions(graph_id=graph_id, user_id=user_id)


@v1_router.get(
    path="/graphs/{graph_id}/executions/{graph_exec_id}",
    tags=["graphs"],
    dependencies=[Depends(auth_middleware)],
)
async def get_graph_execution(
    graph_id: str,
    graph_exec_id: str,
    user_id: Annotated[str, Depends(get_user_id)],
) -> graph_db.GraphExecution:
    graph = await graph_db.get_graph(graph_id, user_id=user_id)
    if not graph:
        raise HTTPException(status_code=404, detail=f"Graph #{graph_id} not found.")

    result = await graph_db.get_execution(execution_id=graph_exec_id, user_id=user_id)
    if not result:
        raise HTTPException(status_code=404, detail=f"Graph #{graph_id} not found.")

    return result


########################################################
##################### Schedules ########################
########################################################


class ScheduleCreationRequest(pydantic.BaseModel):
    cron: str
    input_data: dict[Any, Any]
    graph_id: str
    graph_version: int


@v1_router.post(
    path="/schedules",
    tags=["schedules"],
    dependencies=[Depends(auth_middleware)],
)
async def create_schedule(
    user_id: Annotated[str, Depends(get_user_id)],
    schedule: ScheduleCreationRequest,
) -> scheduler.JobInfo:
    graph = await graph_db.get_graph(
        schedule.graph_id, schedule.graph_version, user_id=user_id
    )
    if not graph:
        raise HTTPException(
            status_code=404,
            detail=f"Graph #{schedule.graph_id} v.{schedule.graph_version} not found.",
        )

    return await asyncio.to_thread(
        lambda: execution_scheduler_client().add_execution_schedule(
            graph_id=schedule.graph_id,
            graph_version=graph.version,
            cron=schedule.cron,
            input_data=schedule.input_data,
            user_id=user_id,
        )
    )


@v1_router.delete(
    path="/schedules/{schedule_id}",
    tags=["schedules"],
    dependencies=[Depends(auth_middleware)],
)
def delete_schedule(
    schedule_id: str,
    user_id: Annotated[str, Depends(get_user_id)],
) -> dict[Any, Any]:
    execution_scheduler_client().delete_schedule(schedule_id, user_id=user_id)
    return {"id": schedule_id}


@v1_router.get(
    path="/schedules",
    tags=["schedules"],
    dependencies=[Depends(auth_middleware)],
)
def get_execution_schedules(
    user_id: Annotated[str, Depends(get_user_id)],
    graph_id: str | None = None,
) -> list[scheduler.JobInfo]:
    return execution_scheduler_client().get_execution_schedules(
        user_id=user_id,
        graph_id=graph_id,
    )


########################################################
#####################  API KEY ##############################
########################################################


@v1_router.post(
    "/api-keys",
    response_model=CreateAPIKeyResponse,
    tags=["api-keys"],
    dependencies=[Depends(auth_middleware)],
)
async def create_api_key(
    request: CreateAPIKeyRequest, user_id: Annotated[str, Depends(get_user_id)]
) -> CreateAPIKeyResponse:
    """Create a new API key"""
    try:
        api_key, plain_text = await generate_api_key(
            name=request.name,
            user_id=user_id,
            permissions=request.permissions,
            description=request.description,
        )
        return CreateAPIKeyResponse(api_key=api_key, plain_text_key=plain_text)
    except APIKeyError as e:
        logger.error(f"Failed to create API key: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@v1_router.get(
    "/api-keys",
    response_model=list[APIKeyWithoutHash] | dict[str, str],
    tags=["api-keys"],
    dependencies=[Depends(auth_middleware)],
)
async def get_api_keys(
    user_id: Annotated[str, Depends(get_user_id)]
) -> list[APIKeyWithoutHash]:
    """List all API keys for the user"""
    try:
        return await list_user_api_keys(user_id)
    except APIKeyError as e:
        logger.error(f"Failed to list API keys: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@v1_router.get(
    "/api-keys/{key_id}",
    response_model=APIKeyWithoutHash,
    tags=["api-keys"],
    dependencies=[Depends(auth_middleware)],
)
async def get_api_key(
    key_id: str, user_id: Annotated[str, Depends(get_user_id)]
) -> APIKeyWithoutHash:
    """Get a specific API key"""
    try:
        api_key = await get_api_key_by_id(key_id, user_id)
        if not api_key:
            raise HTTPException(status_code=404, detail="API key not found")
        return api_key
    except APIKeyError as e:
        logger.error(f"Failed to get API key: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@v1_router.delete(
    "/api-keys/{key_id}",
    response_model=APIKeyWithoutHash,
    tags=["api-keys"],
    dependencies=[Depends(auth_middleware)],
)
@feature_flag("api-keys-enabled")
async def delete_api_key(
    key_id: str, user_id: Annotated[str, Depends(get_user_id)]
) -> Optional[APIKeyWithoutHash]:
    """Revoke an API key"""
    try:
        return await revoke_api_key(key_id, user_id)
    except APIKeyNotFoundError:
        raise HTTPException(status_code=404, detail="API key not found")
    except APIKeyPermissionError:
        raise HTTPException(status_code=403, detail="Permission denied")
    except APIKeyError as e:
        logger.error(f"Failed to revoke API key: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@v1_router.post(
    "/api-keys/{key_id}/suspend",
    response_model=APIKeyWithoutHash,
    tags=["api-keys"],
    dependencies=[Depends(auth_middleware)],
)
@feature_flag("api-keys-enabled")
async def suspend_key(
    key_id: str, user_id: Annotated[str, Depends(get_user_id)]
) -> Optional[APIKeyWithoutHash]:
    """Suspend an API key"""
    try:
        return await suspend_api_key(key_id, user_id)
    except APIKeyNotFoundError:
        raise HTTPException(status_code=404, detail="API key not found")
    except APIKeyPermissionError:
        raise HTTPException(status_code=403, detail="Permission denied")
    except APIKeyError as e:
        logger.error(f"Failed to suspend API key: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@v1_router.put(
    "/api-keys/{key_id}/permissions",
    response_model=APIKeyWithoutHash,
    tags=["api-keys"],
    dependencies=[Depends(auth_middleware)],
)
@feature_flag("api-keys-enabled")
async def update_permissions(
    key_id: str,
    request: UpdatePermissionsRequest,
    user_id: Annotated[str, Depends(get_user_id)],
) -> Optional[APIKeyWithoutHash]:
    """Update API key permissions"""
    try:
        return await update_api_key_permissions(key_id, user_id, request.permissions)
    except APIKeyNotFoundError:
        raise HTTPException(status_code=404, detail="API key not found")
    except APIKeyPermissionError:
        raise HTTPException(status_code=403, detail="Permission denied")
    except APIKeyError as e:
        logger.error(f"Failed to update API key permissions: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
