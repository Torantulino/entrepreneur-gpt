import logging
from collections import defaultdict
from typing import Any, Sequence

from autogpt_libs.utils.cache import thread_cached
from fastapi import APIRouter, Depends, HTTPException
from prisma.enums import APIKeyPermission

import backend.data.block
from backend.data import execution as execution_db
from backend.data import graph as graph_db
from backend.data.api_key import APIKey
from backend.data.block import BlockInput, CompletedBlockOutput
from backend.executor import ExecutionManager
from backend.server.external.middleware import require_permission
from backend.util.service import get_service_client
from backend.util.settings import Settings


@thread_cached
def execution_manager_client() -> ExecutionManager:
    return get_service_client(ExecutionManager)


settings = Settings()
logger = logging.getLogger(__name__)

v1_router = APIRouter()


@v1_router.get(
    path="/blocks",
    tags=["blocks"],
    dependencies=[Depends(require_permission(APIKeyPermission.READ_BLOCK))],
)
def get_graph_blocks() -> Sequence[dict[Any, Any]]:
    blocks = [block() for block in backend.data.block.get_blocks().values()]
    return [b.to_dict() for b in blocks]


@v1_router.post(
    path="/blocks/{block_id}/execute",
    tags=["blocks"],
    dependencies=[Depends(require_permission(APIKeyPermission.EXECUTE_BLOCK))],
)
def execute_graph_block(
    block_id: str,
    data: BlockInput,
    api_key: APIKey = Depends(require_permission(APIKeyPermission.EXECUTE_BLOCK)),
) -> CompletedBlockOutput:
    obj = backend.data.block.get_block(block_id)
    if not obj:
        raise HTTPException(status_code=404, detail=f"Block #{block_id} not found.")

    output = defaultdict(list)
    for name, data in obj.execute(data):
        output[name].append(data)
    return output


@v1_router.post(
    path="/graphs/{graph_id}/execute/{graph_version}",
    tags=["graphs"],
)
def execute_graph(
    graph_id: str,
    graph_version: int,
    node_input: dict[Any, Any],
    api_key: APIKey = Depends(require_permission(APIKeyPermission.EXECUTE_GRAPH)),
) -> dict[str, Any]:
    try:
        graph_exec = execution_manager_client().add_execution(
            graph_id,
            graph_version=graph_version,
            data=node_input,
            user_id=api_key.user_id,
        )
        return {"id": graph_exec.graph_exec_id}
    except Exception as e:
        msg = e.__str__().encode().decode("unicode_escape")
        raise HTTPException(status_code=400, detail=msg)


@v1_router.get(
    path="/graphs/{graph_id}/executions/{graph_exec_id}/results",
    tags=["graphs"],
)
async def get_graph_execution_results(
    graph_id: str,
    graph_exec_id: str,
    api_key: APIKey = Depends(require_permission(APIKeyPermission.READ_GRAPH)),
) -> dict:
    graph = await graph_db.get_graph(graph_id, user_id=api_key.user_id)
    if not graph:
        raise HTTPException(status_code=404, detail=f"Graph #{graph_id} not found.")

    results = await execution_db.get_execution_results(graph_exec_id)

    return {
        "execution_id": graph_exec_id,
        "nodes": [
            {
                "node_id": result.node_id,
                "input": (
                    result.input_data.get("value")
                    if "value" in result.input_data
                    else result.input_data
                ),
                "output": result.output_data.get(
                    "response", result.output_data.get("result", [])
                ),
            }
            for result in results
        ],
    }
