from typing import Dict, Set

from fastapi import WebSocket

from backend.data import execution
from backend.server.model import Methods, WsMessage


class ConnectionManager:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self.subscriptions: Dict[int, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        for subscribers in self.subscriptions.values():
            subscribers.discard(websocket)

    async def subscribe(self, graph_id: str, graph_version: int, websocket: WebSocket):
        key = hash((graph_id, graph_version))
        if key not in self.subscriptions:
            self.subscriptions[key] = set()
        self.subscriptions[key].add(websocket)

    async def unsubscribe(
        self, graph_id: str, graph_version: int, websocket: WebSocket
    ):
        key = hash((graph_id, graph_version))
        if key in self.subscriptions:
            self.subscriptions[key].discard(websocket)
            if not self.subscriptions[key]:
                del self.subscriptions[key]

    async def send_execution_result(self, result: execution.ExecutionResult):
        key = hash((result.graph_id, result.graph_version))
        if key in self.subscriptions:
            message = WsMessage(
                method=Methods.EXECUTION_EVENT,
                channel=str(key),
                data=result.model_dump(),
            ).model_dump_json()
            for connection in self.subscriptions[key]:
                await connection.send_text(message)
