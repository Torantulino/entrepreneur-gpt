from enum import Enum
import typing

import pydantic


class LibraryAgent(pydantic.BaseModel):
    id: str  # Changed from agent_id to match GraphMeta
    version: int  # Changed from agent_version to match GraphMeta
    is_active: bool  # Added to match GraphMeta
    name: str
    description: str

    isCreatedByUser: bool
    # Made input_schema and output_schema match GraphMeta's type
    input_schema: dict[str, typing.Any]  # Should be BlockIOObjectSubSchema in frontend
    output_schema: dict[str, typing.Any]  # Should be BlockIOObjectSubSchema in frontend

class LibraryAgentFilter(str, Enum):
    CREATED_AT = "createdAt"
    UPDATED_AT = "updatedAt"
    IS_FAVOURITE = "isFavourite"
    IS_CREATED_BY_USER = "isCreatedByUser"
