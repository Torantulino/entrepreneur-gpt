from typing import cast
from unittest.mock import AsyncMock

import pytest
from fastapi import WebSocket, WebSocketDisconnect

from backend.server.conn_manager import ConnectionManager
from backend.server.ws_api import (
    Methods,
    WsMessage,
    handle_subscribe,
    handle_unsubscribe,
    websocket_router,
)


@pytest.fixture
def mock_websocket() -> AsyncMock:
    return AsyncMock(spec=WebSocket)


@pytest.fixture
def mock_manager() -> AsyncMock:
    return AsyncMock(spec=ConnectionManager)


@pytest.mark.asyncio
async def test_websocket_router_subscribe(
    mock_websocket: AsyncMock, mock_manager: AsyncMock
) -> None:
    mock_websocket.receive_text.side_effect = [
        WsMessage(
            method=Methods.SUBSCRIBE,
            data={"graph_id": "test_graph", "graph_version": 1},
        ).model_dump_json(),
        WebSocketDisconnect(),
    ]

    await websocket_router(
        cast(WebSocket, mock_websocket), cast(ConnectionManager, mock_manager)
    )

    mock_manager.connect.assert_called_once_with(mock_websocket)
    mock_manager.subscribe.assert_called_once_with("test_graph", 1, mock_websocket)
    mock_websocket.send_text.assert_called_once()
    assert '"method":"subscribe"' in mock_websocket.send_text.call_args[0][0]
    assert '"success":true' in mock_websocket.send_text.call_args[0][0]
    mock_manager.disconnect.assert_called_once_with(mock_websocket)


@pytest.mark.asyncio
async def test_websocket_router_unsubscribe(
    mock_websocket: AsyncMock, mock_manager: AsyncMock
) -> None:
    mock_websocket.receive_text.side_effect = [
        WsMessage(
            method=Methods.UNSUBSCRIBE,
            data={"graph_id": "test_graph", "graph_version": 1},
        ).model_dump_json(),
        WebSocketDisconnect(),
    ]

    await websocket_router(
        cast(WebSocket, mock_websocket), cast(ConnectionManager, mock_manager)
    )

    mock_manager.connect.assert_called_once_with(mock_websocket)
    mock_manager.unsubscribe.assert_called_once_with("test_graph", 1, mock_websocket)
    mock_websocket.send_text.assert_called_once()
    assert '"method":"unsubscribe"' in mock_websocket.send_text.call_args[0][0]
    assert '"success":true' in mock_websocket.send_text.call_args[0][0]
    mock_manager.disconnect.assert_called_once_with(mock_websocket)


@pytest.mark.asyncio
async def test_websocket_router_invalid_method(
    mock_websocket: AsyncMock, mock_manager: AsyncMock
) -> None:
    mock_websocket.receive_text.side_effect = [
        WsMessage(method=Methods.EXECUTION_EVENT).model_dump_json(),
        WebSocketDisconnect(),
    ]

    await websocket_router(
        cast(WebSocket, mock_websocket), cast(ConnectionManager, mock_manager)
    )

    mock_manager.connect.assert_called_once_with(mock_websocket)
    mock_websocket.send_text.assert_called_once()
    assert '"method":"error"' in mock_websocket.send_text.call_args[0][0]
    assert '"success":false' in mock_websocket.send_text.call_args[0][0]
    mock_manager.disconnect.assert_called_once_with(mock_websocket)


@pytest.mark.asyncio
async def test_handle_subscribe_success(
    mock_websocket: AsyncMock, mock_manager: AsyncMock
) -> None:
    message = WsMessage(
        method=Methods.SUBSCRIBE, data={"graph_id": "test_graph", "graph_version": 1}
    )

    await handle_subscribe(
        cast(WebSocket, mock_websocket), cast(ConnectionManager, mock_manager), message
    )

    mock_manager.subscribe.assert_called_once_with("test_graph", 1, mock_websocket)
    mock_websocket.send_text.assert_called_once()
    assert '"method":"subscribe"' in mock_websocket.send_text.call_args[0][0]
    assert '"success":true' in mock_websocket.send_text.call_args[0][0]


@pytest.mark.asyncio
async def test_handle_subscribe_missing_data(
    mock_websocket: AsyncMock, mock_manager: AsyncMock
) -> None:
    message = WsMessage(method=Methods.SUBSCRIBE)

    await handle_subscribe(
        cast(WebSocket, mock_websocket), cast(ConnectionManager, mock_manager), message
    )

    mock_manager.subscribe.assert_not_called()
    mock_websocket.send_text.assert_called_once()
    assert '"method":"error"' in mock_websocket.send_text.call_args[0][0]
    assert '"success":false' in mock_websocket.send_text.call_args[0][0]


@pytest.mark.asyncio
async def test_handle_unsubscribe_success(
    mock_websocket: AsyncMock, mock_manager: AsyncMock
) -> None:
    message = WsMessage(
        method=Methods.UNSUBSCRIBE, data={"graph_id": "test_graph", "graph_version": 1}
    )

    await handle_unsubscribe(
        cast(WebSocket, mock_websocket), cast(ConnectionManager, mock_manager), message
    )

    mock_manager.unsubscribe.assert_called_once_with("test_graph", 1, mock_websocket)
    mock_websocket.send_text.assert_called_once()
    assert '"method":"unsubscribe"' in mock_websocket.send_text.call_args[0][0]
    assert '"success":true' in mock_websocket.send_text.call_args[0][0]


@pytest.mark.asyncio
async def test_handle_unsubscribe_missing_data(
    mock_websocket: AsyncMock, mock_manager: AsyncMock
) -> None:
    message = WsMessage(method=Methods.UNSUBSCRIBE)

    await handle_unsubscribe(
        cast(WebSocket, mock_websocket), cast(ConnectionManager, mock_manager), message
    )

    mock_manager.unsubscribe.assert_not_called()
    mock_websocket.send_text.assert_called_once()
    assert '"method":"error"' in mock_websocket.send_text.call_args[0][0]
    assert '"success":false' in mock_websocket.send_text.call_args[0][0]
