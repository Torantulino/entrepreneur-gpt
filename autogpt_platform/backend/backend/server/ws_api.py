import asyncio
import logging
from contextlib import asynccontextmanager

import uvicorn
from autogpt_libs.auth import parse_jwt_token
from fastapi import Depends, FastAPI, WebSocket, WebSocketDisconnect
from starlette.middleware.cors import CORSMiddleware

from backend.data import redis
from backend.data.execution import AsyncRedisExecutionEventBus
from backend.data.user import DEFAULT_USER_ID
from backend.server.conn_manager import ConnectionManager
from backend.server.model import ExecutionSubscription, Methods, WsMessage
from backend.util.service import AppProcess
from backend.util.settings import AppEnvironment, Config, Settings

logger = logging.getLogger(__name__)
settings = Settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    manager = get_connection_manager()
    fut = asyncio.create_task(event_broadcaster(manager))
    fut.add_done_callback(lambda _: logger.info("Event broadcaster stopped"))
    yield


docs_url = "/docs" if settings.config.app_env == AppEnvironment.LOCAL else None
app = FastAPI(lifespan=lifespan, docs_url=docs_url)
_connection_manager = None


def get_connection_manager():
    global _connection_manager
    if _connection_manager is None:
        _connection_manager = ConnectionManager()
    return _connection_manager


async def event_broadcaster(manager: ConnectionManager):
    try:
        redis.connect()
        event_queue = AsyncRedisExecutionEventBus()
        async for event in event_queue.listen():
            await manager.send_execution_result(event)
    except Exception as e:
        logger.exception(f"Event broadcaster error: {e}")
        raise
    finally:
        redis.disconnect()


async def authenticate_websocket(websocket: WebSocket) -> str:
    if not settings.config.enable_auth:
        return DEFAULT_USER_ID

    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=4001, reason="Missing authentication token")
        return ""

    try:
        payload = parse_jwt_token(token)
        user_id = payload.get("sub")
        if not user_id:
            await websocket.close(code=4002, reason="Invalid token")
            return ""
        return user_id
    except ValueError:
        await websocket.close(code=4003, reason="Invalid token")
        return ""


async def handle_subscribe(
    websocket: WebSocket, manager: ConnectionManager, message: WsMessage
):
    if not message.data:
        await websocket.send_text(
            WsMessage(
                method=Methods.ERROR,
                success=False,
                error="Subscription data missing",
            ).model_dump_json()
        )
    else:
        ex_sub = ExecutionSubscription.model_validate(message.data)
        await manager.subscribe(ex_sub.graph_id, ex_sub.graph_version, websocket)
        logger.debug(f"New execution subscription for graph {ex_sub.graph_id}")
        await websocket.send_text(
            WsMessage(
                method=Methods.SUBSCRIBE,
                success=True,
                channel=str(hash((ex_sub.graph_id, ex_sub.graph_version))),
            ).model_dump_json()
        )


async def handle_unsubscribe(
    websocket: WebSocket, manager: ConnectionManager, message: WsMessage
):
    if not message.data:
        await websocket.send_text(
            WsMessage(
                method=Methods.ERROR,
                success=False,
                error="Subscription data missing",
            ).model_dump_json()
        )
    else:
        ex_sub = ExecutionSubscription.model_validate(message.data)
        await manager.unsubscribe(ex_sub.graph_id, ex_sub.graph_version, websocket)
        logger.debug(f"Removed execution subscription for graph {ex_sub.graph_id}")
        await websocket.send_text(
            WsMessage(
                method=Methods.UNSUBSCRIBE,
                success=True,
                channel=str(hash((ex_sub.graph_id, ex_sub.graph_version))),
            ).model_dump_json()
        )


@app.get("/")
async def health():
    return {"status": "healthy"}


@app.websocket("/ws")
async def websocket_router(
    websocket: WebSocket, manager: ConnectionManager = Depends(get_connection_manager)
):
    user_id = await authenticate_websocket(websocket)
    if not user_id:
        return
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message = WsMessage.model_validate_json(data)

            if message.method == Methods.HEARTBEAT:
                await websocket.send_json(
                    {"method": Methods.HEARTBEAT.value, "data": "pong", "success": True}
                )
                continue

            if message.method == Methods.SUBSCRIBE:
                await handle_subscribe(websocket, manager, message)

            elif message.method == Methods.UNSUBSCRIBE:
                await handle_unsubscribe(websocket, manager, message)

            elif message.method == Methods.ERROR:
                logger.error(f"WebSocket Error message received: {message.data}")

            else:
                logger.warning(
                    f"Unknown WebSocket message type {message.method} received: "
                    f"{message.data}"
                )
                await websocket.send_text(
                    WsMessage(
                        method=Methods.ERROR,
                        success=False,
                        error="Message type is not processed by the server",
                    ).model_dump_json()
                )

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.debug("WebSocket client disconnected")


class WebsocketServer(AppProcess):
    def run(self):
        logger.info(f"CORS allow origins: {settings.config.backend_cors_allow_origins}")
        server_app = CORSMiddleware(
            app=app,
            allow_origins=settings.config.backend_cors_allow_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        uvicorn.run(
            server_app,
            host=Config().websocket_server_host,
            port=Config().websocket_server_port,
        )
