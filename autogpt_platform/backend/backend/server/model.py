import enum
from typing import Any, List, Optional, Union

import pydantic

import backend.data.graph
from backend.data.api_key import APIKeyPermission, APIKeyWithoutHash


class Methods(enum.Enum):
    SUBSCRIBE = "subscribe"
    UNSUBSCRIBE = "unsubscribe"
    EXECUTION_EVENT = "execution_event"
    ERROR = "error"
    HEARTBEAT = "heartbeat"


class WsMessage(pydantic.BaseModel):
    method: Methods
    data: Optional[Union[dict[str, Any], list[Any], str]] = None
    success: bool | None = None
    channel: str | None = None
    error: str | None = None


class ExecutionSubscription(pydantic.BaseModel):
    graph_id: str
    graph_version: int


class ExecuteGraphResponse(pydantic.BaseModel):
    graph_exec_id: str


class CreateGraph(pydantic.BaseModel):
    template_id: str | None = None
    template_version: int | None = None
    graph: backend.data.graph.Graph | None = None


class CreateAPIKeyRequest(pydantic.BaseModel):
    name: str
    permissions: List[APIKeyPermission]
    description: Optional[str] = None


class CreateAPIKeyResponse(pydantic.BaseModel):
    api_key: APIKeyWithoutHash
    plain_text_key: str


class SetGraphActiveVersion(pydantic.BaseModel):
    active_graph_version: int


class UpdatePermissionsRequest(pydantic.BaseModel):
    permissions: List[APIKeyPermission]


class RequestTopUp(pydantic.BaseModel):
    credit_amount: int
