import datetime
import enum
import json
import typing

import prisma.enums
import prisma.models
import pydantic

import backend.data.block
import backend.data.graph
import backend.server.model


class AgentStatus(str, enum.Enum):
    # The agent has completed all runs
    COMPLETED = "COMPLETED"
    # An agent is running, but not all runs have completed
    HEALTHY = "HEALTHY"
    # An agent is waiting to start or waiting for another reason
    WAITING = "WAITING"
    # An agent is in an error state
    ERROR = "ERROR"


class LibraryAgent(pydantic.BaseModel):
    id: str  # Changed from agent_id to match GraphMeta

    agent_id: str
    agent_version: int  # Changed from agent_version to match GraphMeta

    image_url: str

    creator_name: str  # from profile
    creator_image_url: str  # from profile

    status: AgentStatus

    updated_at: datetime.datetime

    name: str  # from graph
    description: str  # from graph

    # Made input_schema and output_schema match GraphMeta's type
    input_schema: dict[str, typing.Any]  # Should be BlockIOObjectSubSchema in frontend

    new_output: bool
    can_access_graph: bool

    is_latest_version: bool

    @staticmethod
    def from_db(agent: prisma.models.LibraryAgent):
        if not agent.Agent:
            raise ValueError("AgentGraph is required")

        graph = backend.data.graph.GraphModel.from_db(agent.Agent)

        agent_updated_at = agent.Agent.updatedAt
        lib_agent_updated_at = agent.updatedAt

        name = graph.name
        description = graph.description
        image_url = agent.image_url if agent.image_url else ""
        if agent.Creator:
            creator_name = agent.Creator.name
            creator_image_url = (
                agent.Creator.avatarUrl if agent.Creator.avatarUrl else ""
            )
        else:
            creator_name = "Unknown"
            creator_image_url = ""

        # Take the latest updated_at timestamp either when the graph was updated or the library agent was updated
        updated_at = (
            max(agent_updated_at, lib_agent_updated_at)
            if agent_updated_at
            else lib_agent_updated_at
        )

        # Getting counts as expecting more refined logic for determining status
        status_counts = {status: 0 for status in prisma.enums.AgentExecutionStatus}
        new_output = False

        runs_since = datetime.datetime.now(datetime.UTC) - datetime.timedelta(days=7)
        if not agent.Agent.AgentGraphExecution:
            status = AgentStatus.COMPLETED
        else:
            for execution in agent.Agent.AgentGraphExecution:
                if runs_since > execution.createdAt:
                    if (
                        execution.executionStatus
                        == prisma.enums.AgentExecutionStatus.COMPLETED
                    ):
                        new_output = True
                    status_counts[execution.executionStatus] += 1

            if status_counts[prisma.enums.AgentExecutionStatus.FAILED] > 0:
                status = AgentStatus.ERROR
            elif status_counts[prisma.enums.AgentExecutionStatus.QUEUED] > 0:
                status = AgentStatus.WAITING
            elif status_counts[prisma.enums.AgentExecutionStatus.RUNNING] > 0:
                status = AgentStatus.HEALTHY
            else:
                status = AgentStatus.COMPLETED

        return LibraryAgent(
            id=agent.id,
            agent_id=agent.agentId,
            agent_version=agent.agentVersion,
            image_url=image_url,
            creator_name=creator_name,
            creator_image_url=creator_image_url,
            name=name,
            description=description,
            status=status,
            updated_at=updated_at,
            input_schema=graph.input_schema,
            new_output=new_output,
            can_access_graph=agent.Agent.userId == agent.userId,
            # TODO: work out how to calculate this efficiently
            is_latest_version=True,
        )


class LibraryAgentResponse:
    agents: typing.List[LibraryAgent]
    pagination: backend.server.model.Pagination  # info


class LibraryAgentPreset(pydantic.BaseModel):
    id: str
    updated_at: datetime.datetime

    agent_id: str
    agent_version: int

    name: str
    description: str

    is_active: bool
    inputs: dict[str, typing.Union[backend.data.block.BlockInput, typing.Any]]

    @staticmethod
    def from_db(preset: prisma.models.AgentPreset):
        input_data = {}

        for data in preset.InputPresets or []:
            input_data[data.name] = json.loads(data.data)

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
    pagination: backend.server.model.Pagination


class CreateLibraryAgentPresetRequest(pydantic.BaseModel):
    name: str
    description: str
    inputs: dict[str, typing.Union[backend.data.block.BlockInput, typing.Any]]
    agent_id: str
    agent_version: int
    is_active: bool
