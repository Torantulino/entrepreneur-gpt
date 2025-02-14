import datetime
from typing import Any

import prisma.models
import pydantic

import backend.data.block as block_model
import backend.data.graph as graph_model
import backend.server.model as server_model


class LibraryAgent(pydantic.BaseModel):
    id: str  # Changed from agent_id to match GraphMeta

    agent_id: str
    agent_version: int  # Changed from agent_version to match GraphMeta

    preset_id: str | None

    updated_at: datetime.datetime

    name: str
    description: str

    # Made input_schema and output_schema match GraphMeta's type
    input_schema: dict[str, Any]  # Should be BlockIOObjectSubSchema in frontend
    output_schema: dict[str, Any]  # Should be BlockIOObjectSubSchema in frontend

    is_favorite: bool
    is_created_by_user: bool

    is_latest_version: bool

    @staticmethod
    def from_db(agent: prisma.models.LibraryAgent):
        if not agent.Agent:
            raise ValueError("AgentGraph is required")

        graph = graph_model.GraphModel.from_db(agent.Agent)

        agent_updated_at = agent.Agent.updatedAt
        lib_agent_updated_at = agent.updatedAt

        # Take the latest updated_at timestamp either when the graph was updated or the library agent was updated
        updated_at = (
            max(agent_updated_at, lib_agent_updated_at)
            if agent_updated_at
            else lib_agent_updated_at
        )

        return LibraryAgent(
            id=agent.id,
            agent_id=agent.agentId,
            agent_version=agent.agentVersion,
            updated_at=updated_at,
            name=graph.name,
            description=graph.description,
            input_schema=graph.input_schema,
            output_schema=graph.output_schema,
            is_favorite=agent.isFavorite,
            is_created_by_user=agent.isCreatedByUser,
            is_latest_version=graph.is_active,
            preset_id=agent.AgentPreset.id if agent.AgentPreset else None,
        )


class LibraryAgentPreset(pydantic.BaseModel):
    id: str
    updated_at: datetime.datetime

    agent_id: str
    agent_version: int

    name: str
    description: str

    is_active: bool

    inputs: block_model.BlockInput

    @staticmethod
    def from_db(preset: prisma.models.AgentPreset):
        input_data: block_model.BlockInput = {}

        for preset_input in preset.InputPresets or []:
            input_data[preset_input.name] = preset_input.data

        return LibraryAgentPreset(
            id=preset.id,
            updated_at=preset.updatedAt,
            agent_id=preset.agentId,
            agent_version=preset.agentVersion,
            name=preset.name,
            description=preset.description,
            is_active=preset.isActive,
            inputs=input_data,
        )


class LibraryAgentPresetResponse(pydantic.BaseModel):
    presets: list[LibraryAgentPreset]
    pagination: server_model.Pagination


class CreateLibraryAgentPresetRequest(pydantic.BaseModel):
    name: str
    description: str
    inputs: block_model.BlockInput
    agent_id: str
    agent_version: int
    is_active: bool
