import contextlib
import logging
from typing import Any, Optional

import autogpt_libs.auth.models
import fastapi
import fastapi.responses
import starlette.middleware.cors
import uvicorn
from autogpt_libs.feature_flag.client import (
    initialize_launchdarkly,
    shutdown_launchdarkly,
)

import backend.data.block
import backend.data.db
import backend.data.graph
import backend.data.user
import backend.server.routers.v1
import backend.server.v2.library.db
import backend.server.v2.library.model
import backend.server.v2.library.routes
import backend.server.v2.store.model
import backend.server.v2.store.routes
import backend.util.service
import backend.util.settings
from backend.server.external.api import external_app

settings = backend.util.settings.Settings()
logger = logging.getLogger(__name__)

logging.getLogger("autogpt_libs").setLevel(logging.INFO)


@contextlib.contextmanager
def launch_darkly_context():
    if settings.config.app_env != backend.util.settings.AppEnvironment.LOCAL:
        initialize_launchdarkly()
        try:
            yield
        finally:
            shutdown_launchdarkly()
    else:
        yield


@contextlib.asynccontextmanager
async def lifespan_context(app: fastapi.FastAPI):
    await backend.data.db.connect()
    await backend.data.block.initialize_blocks()
    await backend.data.user.migrate_and_encrypt_user_integrations()
    await backend.data.graph.fix_llm_provider_credentials()
    with launch_darkly_context():
        yield
    await backend.data.db.disconnect()


docs_url = (
    "/docs"
    if settings.config.app_env == backend.util.settings.AppEnvironment.LOCAL
    else None
)

app = fastapi.FastAPI(
    title="AutoGPT Agent Server",
    description=(
        "This server is used to execute agents that are created by the "
        "AutoGPT system."
    ),
    summary="AutoGPT Agent Server",
    version="0.1",
    lifespan=lifespan_context,
    docs_url=docs_url,
)


def handle_internal_http_error(status_code: int = 500, log_error: bool = True):
    def handler(request: fastapi.Request, exc: Exception):
        if log_error:
            logger.exception(f"{request.method} {request.url.path} failed: {exc}")
        return fastapi.responses.JSONResponse(
            content={
                "message": f"{request.method} {request.url.path} failed",
                "detail": str(exc),
            },
            status_code=status_code,
        )

    return handler


app.add_exception_handler(ValueError, handle_internal_http_error(400))
app.add_exception_handler(Exception, handle_internal_http_error(500))
app.include_router(backend.server.routers.v1.v1_router, tags=["v1"], prefix="/api")
app.include_router(
    backend.server.v2.store.routes.router, tags=["v2"], prefix="/api/store"
)
app.include_router(
    backend.server.v2.library.routes.router, tags=["v2"], prefix="/api/library"
)

app.mount("/external-api", external_app)


@app.get(path="/health", tags=["health"], dependencies=[])
async def health():
    return {"status": "healthy"}


class AgentServer(backend.util.service.AppProcess):
    def run(self):
        server_app = starlette.middleware.cors.CORSMiddleware(
            app=app,
            allow_origins=settings.config.backend_cors_allow_origins,
            allow_credentials=True,
            allow_methods=["*"],  # Allows all methods
            allow_headers=["*"],  # Allows all headers
        )
        uvicorn.run(
            server_app,
            host=backend.util.settings.Config().agent_api_host,
            port=backend.util.settings.Config().agent_api_port,
        )

    @staticmethod
    async def test_execute_graph(
        graph_id: str,
        user_id: str,
        graph_version: Optional[int] = None,
        node_input: Optional[dict[str, Any]] = None,
    ):
        return backend.server.routers.v1.execute_graph(
            user_id=user_id,
            graph_id=graph_id,
            graph_version=graph_version,
            node_input=node_input or {},
        )

    @staticmethod
    async def test_get_graph(
        graph_id: str,
        graph_version: int,
        user_id: str,
    ):
        return await backend.server.routers.v1.get_graph(
            graph_id, user_id, graph_version
        )

    @staticmethod
    async def test_create_graph(
        create_graph: backend.server.routers.v1.CreateGraph,
        user_id: str,
    ):
        return await backend.server.routers.v1.create_new_graph(create_graph, user_id)

    @staticmethod
    async def test_get_graph_run_status(graph_exec_id: str, user_id: str):
        execution = await backend.data.graph.get_execution_meta(
            user_id=user_id, execution_id=graph_exec_id
        )
        if not execution:
            raise ValueError(f"Execution {graph_exec_id} not found")
        return execution.status

    @staticmethod
    async def test_get_graph_run_results(
        graph_id: str, graph_exec_id: str, user_id: str
    ):
        return await backend.server.routers.v1.get_graph_execution(
            graph_id, graph_exec_id, user_id
        )

    @staticmethod
    async def test_delete_graph(graph_id: str, user_id: str):
        await backend.server.v2.library.db.delete_library_agent_by_graph_id(
            graph_id=graph_id, user_id=user_id
        )
        return await backend.server.routers.v1.delete_graph(graph_id, user_id)

    @staticmethod
    async def test_get_presets(user_id: str, page: int = 1, page_size: int = 10):
        return await backend.server.v2.library.routes.presets.get_presets(
            user_id=user_id, page=page, page_size=page_size
        )

    @staticmethod
    async def test_get_preset(preset_id: str, user_id: str):
        return await backend.server.v2.library.routes.presets.get_preset(
            preset_id=preset_id, user_id=user_id
        )

    @staticmethod
    async def test_create_preset(
        preset: backend.server.v2.library.model.CreateLibraryAgentPresetRequest,
        user_id: str,
    ):
        return await backend.server.v2.library.routes.presets.create_preset(
            preset=preset, user_id=user_id
        )

    @staticmethod
    async def test_update_preset(
        preset_id: str,
        preset: backend.server.v2.library.model.CreateLibraryAgentPresetRequest,
        user_id: str,
    ):
        return await backend.server.v2.library.routes.presets.update_preset(
            preset_id=preset_id, preset=preset, user_id=user_id
        )

    @staticmethod
    async def test_delete_preset(preset_id: str, user_id: str):
        return await backend.server.v2.library.routes.presets.delete_preset(
            preset_id=preset_id, user_id=user_id
        )

    @staticmethod
    async def test_execute_preset(
        graph_id: str,
        graph_version: int,
        preset_id: str,
        user_id: str,
        node_input: Optional[dict[str, Any]] = None,
    ):
        return await backend.server.v2.library.routes.presets.execute_preset(
            graph_id=graph_id,
            graph_version=graph_version,
            preset_id=preset_id,
            node_input=node_input or {},
            user_id=user_id,
        )

    @staticmethod
    async def test_create_store_listing(
        request: backend.server.v2.store.model.StoreSubmissionRequest, user_id: str
    ):
        return await backend.server.v2.store.routes.create_submission(request, user_id)

    @staticmethod
    async def test_review_store_listing(
        request: backend.server.v2.store.model.ReviewSubmissionRequest,
        user: autogpt_libs.auth.models.User,
    ):
        return await backend.server.v2.store.routes.review_submission(request, user)

    def set_test_dependency_overrides(self, overrides: dict):
        app.dependency_overrides.update(overrides)
