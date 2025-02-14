from collections import defaultdict
from datetime import datetime, timezone
from multiprocessing import Manager
from typing import Any, AsyncGenerator, Generator, Generic, Optional, Type, TypeVar

from prisma import Json
from prisma.enums import AgentExecutionStatus
from prisma.errors import PrismaError
from prisma.models import (
    AgentGraphExecution,
    AgentNodeExecution,
    AgentNodeExecutionInputOutput,
)
from pydantic import BaseModel

from backend.data.block import BlockData, BlockInput, CompletedBlockOutput
from backend.data.includes import EXECUTION_RESULT_INCLUDE, GRAPH_EXECUTION_INCLUDE
from backend.data.queue import AsyncRedisEventBus, RedisEventBus
from backend.server.v2.store.exceptions import DatabaseError
from backend.util import mock, type
from backend.util.settings import Config


class GraphExecutionEntry(BaseModel):
    user_id: str
    graph_exec_id: str
    graph_id: str
    graph_version: int
    start_node_execs: list["NodeExecutionEntry"]


class NodeExecutionEntry(BaseModel):
    user_id: str
    graph_exec_id: str
    graph_id: str
    node_exec_id: str
    node_id: str
    block_id: str
    data: BlockInput


ExecutionStatus = AgentExecutionStatus

T = TypeVar("T")


class ExecutionQueue(Generic[T]):
    """
    Queue for managing the execution of agents.
    This will be shared between different processes
    """

    def __init__(self):
        self.queue = Manager().Queue()

    def add(self, execution: T) -> T:
        self.queue.put(execution)
        return execution

    def get(self) -> T:
        return self.queue.get()

    def empty(self) -> bool:
        return self.queue.empty()


class ExecutionResult(BaseModel):
    graph_id: str
    graph_version: int
    graph_exec_id: str
    node_exec_id: str
    node_id: str
    block_id: str
    status: ExecutionStatus
    input_data: BlockInput
    output_data: CompletedBlockOutput
    add_time: datetime
    queue_time: datetime | None
    start_time: datetime | None
    end_time: datetime | None

    @staticmethod
    def from_graph(graph: AgentGraphExecution):
        return ExecutionResult(
            graph_id=graph.agentGraphId,
            graph_version=graph.agentGraphVersion,
            graph_exec_id=graph.id,
            node_exec_id="",
            node_id="",
            block_id="",
            status=graph.executionStatus,
            # TODO: Populate input_data & output_data from AgentNodeExecutions
            #       Input & Output comes AgentInputBlock & AgentOutputBlock.
            input_data={},
            output_data={},
            add_time=graph.createdAt,
            queue_time=graph.createdAt,
            start_time=graph.startedAt,
            end_time=graph.updatedAt,
        )

    @staticmethod
    def from_db(execution: AgentNodeExecution):
        if execution.executionData:
            # Execution that has been queued for execution will persist its data.
            input_data = type.convert(execution.executionData, dict[str, Any])
        else:
            # For incomplete execution, executionData will not be yet available.
            input_data: BlockInput = defaultdict()
            for data in execution.Input or []:
                input_data[data.name] = type.convert(data.data, Type[Any])

        output_data: CompletedBlockOutput = defaultdict(list)
        for data in execution.Output or []:
            output_data[data.name].append(type.convert(data.data, Type[Any]))

        graph_execution: AgentGraphExecution | None = execution.AgentGraphExecution

        return ExecutionResult(
            graph_id=graph_execution.agentGraphId if graph_execution else "",
            graph_version=graph_execution.agentGraphVersion if graph_execution else 0,
            graph_exec_id=execution.agentGraphExecutionId,
            block_id=execution.AgentNode.agentBlockId if execution.AgentNode else "",
            node_exec_id=execution.id,
            node_id=execution.agentNodeId,
            status=execution.executionStatus,
            input_data=input_data,
            output_data=output_data,
            add_time=execution.addedTime,
            queue_time=execution.queuedTime,
            start_time=execution.startedTime,
            end_time=execution.endedTime,
        )


# --------------------- Model functions --------------------- #


async def create_graph_execution(
    graph_id: str,
    graph_version: int,
    nodes_input: list[tuple[str, BlockInput]],
    user_id: str,
    preset_id: str | None = None,
) -> tuple[str, list[ExecutionResult]]:
    """
    Create a new AgentGraphExecution record.
    Returns:
        The id of the AgentGraphExecution and the list of ExecutionResult for each node.
    """
    result = await AgentGraphExecution.prisma().create(
        data={
            "agentGraphId": graph_id,
            "agentGraphVersion": graph_version,
            "executionStatus": ExecutionStatus.QUEUED,
            "AgentNodeExecutions": {
                "create": [  # type: ignore
                    {
                        "agentNodeId": node_id,
                        "executionStatus": ExecutionStatus.INCOMPLETE,
                        "Input": {
                            "create": [
                                {"name": name, "data": Json(data)}
                                for name, data in node_input.items()
                            ]
                        },
                    }
                    for node_id, node_input in nodes_input
                ]
            },
            "userId": user_id,
            "agentPresetId": preset_id,
        },
        include=GRAPH_EXECUTION_INCLUDE,
    )

    return result.id, [
        ExecutionResult.from_db(execution)
        for execution in result.AgentNodeExecutions or []
    ]


async def upsert_execution_input(
    node_id: str,
    graph_exec_id: str,
    input_name: str,
    input_data: Any,
    node_exec_id: str | None = None,
) -> tuple[str, BlockInput]:
    """
    Insert AgentNodeExecutionInputOutput record for as one of AgentNodeExecution.Input.
    If there is no AgentNodeExecution that has no `input_name` as input, create new one.

    Args:
        node_id: The id of the AgentNode.
        graph_exec_id: The id of the AgentGraphExecution.
        input_name: The name of the input data.
        input_data: The input data to be inserted.
        node_exec_id: [Optional] The id of the AgentNodeExecution that has no `input_name` as input. If not provided, it will find the eligible incomplete AgentNodeExecution or create a new one.

    Returns:
        * The id of the created or existing AgentNodeExecution.
        * Dict of node input data, key is the input name, value is the input data.
    """
    existing_execution = await AgentNodeExecution.prisma().find_first(
        where={  # type: ignore
            **({"id": node_exec_id} if node_exec_id else {}),
            "agentNodeId": node_id,
            "agentGraphExecutionId": graph_exec_id,
            "executionStatus": ExecutionStatus.INCOMPLETE,
            "Input": {"every": {"name": {"not": input_name}}},
        },
        order={"addedTime": "asc"},
        include={"Input": True},
    )
    json_input_data = Json(input_data)

    if existing_execution:
        await AgentNodeExecutionInputOutput.prisma().create(
            data={
                "name": input_name,
                "data": json_input_data,
                "referencedByInputExecId": existing_execution.id,
            }
        )
        return existing_execution.id, {
            **{
                input_data.name: type.convert(input_data.data, Type[Any])
                for input_data in existing_execution.Input or []
            },
            input_name: input_data,
        }

    elif not node_exec_id:
        result = await AgentNodeExecution.prisma().create(
            data={
                "agentNodeId": node_id,
                "agentGraphExecutionId": graph_exec_id,
                "executionStatus": ExecutionStatus.INCOMPLETE,
                "Input": {"create": {"name": input_name, "data": json_input_data}},
            }
        )
        return result.id, {input_name: input_data}

    else:
        raise ValueError(
            f"NodeExecution {node_exec_id} not found or already has input {input_name}."
        )


async def upsert_execution_output(
    node_exec_id: str,
    output_name: str,
    output_data: Any,
) -> None:
    """
    Insert AgentNodeExecutionInputOutput record for as one of AgentNodeExecution.Output.
    """
    await AgentNodeExecutionInputOutput.prisma().create(
        data={
            "name": output_name,
            "data": Json(output_data),
            "referencedByOutputExecId": node_exec_id,
        }
    )


async def update_graph_execution_start_time(graph_exec_id: str):
    await AgentGraphExecution.prisma().update(
        where={"id": graph_exec_id},
        data={
            "executionStatus": ExecutionStatus.RUNNING,
            "startedAt": datetime.now(tz=timezone.utc),
        },
    )


async def update_graph_execution_stats(
    graph_exec_id: str,
    status: ExecutionStatus,
    stats: dict[str, Any],
) -> ExecutionResult:
    res = await AgentGraphExecution.prisma().update(
        where={"id": graph_exec_id},
        data={
            "executionStatus": status,
            "stats": Json(stats),
        },
    )
    if not res:
        raise ValueError(f"Execution {graph_exec_id} not found.")

    return ExecutionResult.from_graph(res)


async def update_node_execution_stats(node_exec_id: str, stats: dict[str, Any]):
    await AgentNodeExecution.prisma().update(
        where={"id": node_exec_id},
        data={"stats": Json(stats)},
    )


async def update_execution_status(
    node_exec_id: str,
    status: ExecutionStatus,
    execution_data: BlockInput | None = None,
    stats: dict[str, Any] | None = None,
) -> ExecutionResult:
    if status == ExecutionStatus.QUEUED and execution_data is None:
        raise ValueError("Execution data must be provided when queuing an execution.")

    now = datetime.now(tz=timezone.utc)
    data = {
        **({"executionStatus": status}),
        **({"queuedTime": now} if status == ExecutionStatus.QUEUED else {}),
        **({"startedTime": now} if status == ExecutionStatus.RUNNING else {}),
        **({"endedTime": now} if status == ExecutionStatus.FAILED else {}),
        **({"endedTime": now} if status == ExecutionStatus.COMPLETED else {}),
        **({"executionData": Json(execution_data)} if execution_data else {}),
        **({"stats": Json(stats)} if stats else {}),
    }

    res = await AgentNodeExecution.prisma().update(
        where={"id": node_exec_id},
        data=data,  # type: ignore
        include=EXECUTION_RESULT_INCLUDE,
    )
    if not res:
        raise ValueError(f"Execution {node_exec_id} not found.")

    return ExecutionResult.from_db(res)


async def get_execution(
    execution_id: str, user_id: str
) -> Optional[AgentNodeExecution]:
    """
    Get an execution by ID. Returns None if not found.

    Args:
        execution_id: The ID of the execution to retrieve

    Returns:
        The execution if found, None otherwise
    """
    try:
        execution = await AgentNodeExecution.prisma().find_unique(
            where={
                "id": execution_id,
                "userId": user_id,
            }
        )
        return execution
    except PrismaError:
        return None


async def get_execution_results(graph_exec_id: str) -> list[ExecutionResult]:
    executions = await AgentNodeExecution.prisma().find_many(
        where={"agentGraphExecutionId": graph_exec_id},
        include=EXECUTION_RESULT_INCLUDE,
        order=[
            {"queuedTime": "asc"},
            {"addedTime": "asc"},  # Fallback: Incomplete execs has no queuedTime.
        ],
    )
    res = [ExecutionResult.from_db(execution) for execution in executions]
    return res


async def get_executions_in_timerange(
    user_id: str, start_time: str, end_time: str
) -> list[ExecutionResult]:
    try:
        executions = await AgentGraphExecution.prisma().find_many(
            where={
                "AND": [
                    {
                        "startedAt": {
                            "gte": datetime.fromisoformat(start_time),
                            "lte": datetime.fromisoformat(end_time),
                        }
                    },
                    {"userId": user_id},
                ]
            },
            include=GRAPH_EXECUTION_INCLUDE,
        )
        return [ExecutionResult.from_graph(execution) for execution in executions]
    except Exception as e:
        raise DatabaseError(
            f"Failed to get executions in timerange {start_time} to {end_time} for user {user_id}: {e}"
        ) from e


LIST_SPLIT = "_$_"
DICT_SPLIT = "_#_"
OBJC_SPLIT = "_@_"


def parse_execution_output(output: BlockData, name: str) -> Any | None:
    # Allow extracting partial output data by name.
    output_name, output_data = output

    if name == output_name:
        return output_data

    if name.startswith(f"{output_name}{LIST_SPLIT}"):
        index = int(name.split(LIST_SPLIT)[1])
        if not isinstance(output_data, list) or len(output_data) <= index:
            return None
        return output_data[int(name.split(LIST_SPLIT)[1])]

    if name.startswith(f"{output_name}{DICT_SPLIT}"):
        index = name.split(DICT_SPLIT)[1]
        if not isinstance(output_data, dict) or index not in output_data:
            return None
        return output_data[index]

    if name.startswith(f"{output_name}{OBJC_SPLIT}"):
        index = name.split(OBJC_SPLIT)[1]
        if isinstance(output_data, object) and hasattr(output_data, index):
            return getattr(output_data, index)
        return None

    return None


def merge_execution_input(data: BlockInput) -> BlockInput:
    """
    Merge all dynamic input pins which described by the following pattern:
    - <input_name>_$_<index> for list input.
    - <input_name>_#_<index> for dict input.
    - <input_name>_@_<index> for object input.
    This function will construct pins with the same name into a single list/dict/object.
    """

    # Merge all input with <input_name>_$_<index> into a single list.
    items = list(data.items())

    for key, value in items:
        if LIST_SPLIT not in key:
            continue
        name, index = key.split(LIST_SPLIT)
        if not index.isdigit():
            raise ValueError(f"Invalid key: {key}, #{index} index must be an integer.")

        data[name] = data.get(name, [])
        if int(index) >= len(data[name]):
            # Pad list with empty string on missing indices.
            data[name].extend([""] * (int(index) - len(data[name]) + 1))
        data[name][int(index)] = value

    # Merge all input with <input_name>_#_<index> into a single dict.
    for key, value in items:
        if DICT_SPLIT not in key:
            continue
        name, index = key.split(DICT_SPLIT)
        data[name] = data.get(name, {})
        data[name][index] = value

    # Merge all input with <input_name>_@_<index> into a single object.
    for key, value in items:
        if OBJC_SPLIT not in key:
            continue
        name, index = key.split(OBJC_SPLIT)
        if name not in data or not isinstance(data[name], object):
            data[name] = mock.MockObject()
        setattr(data[name], index, value)

    return data


async def get_latest_execution(node_id: str, graph_eid: str) -> ExecutionResult | None:
    execution = await AgentNodeExecution.prisma().find_first(
        where={
            "agentNodeId": node_id,
            "agentGraphExecutionId": graph_eid,
            "executionStatus": {"not": ExecutionStatus.INCOMPLETE},  # type: ignore
        },
        order={"queuedTime": "desc"},
        include=EXECUTION_RESULT_INCLUDE,
    )
    if not execution:
        return None
    return ExecutionResult.from_db(execution)


async def get_incomplete_executions(
    node_id: str, graph_eid: str
) -> list[ExecutionResult]:
    executions = await AgentNodeExecution.prisma().find_many(
        where={
            "agentNodeId": node_id,
            "agentGraphExecutionId": graph_eid,
            "executionStatus": ExecutionStatus.INCOMPLETE,
        },
        include=EXECUTION_RESULT_INCLUDE,
    )
    return [ExecutionResult.from_db(execution) for execution in executions]


# --------------------- Event Bus --------------------- #

config = Config()


class RedisExecutionEventBus(RedisEventBus[ExecutionResult]):
    Model = ExecutionResult

    @property
    def event_bus_name(self) -> str:
        return config.execution_event_bus_name

    def publish(self, res: ExecutionResult):
        self.publish_event(res, f"{res.graph_id}/{res.graph_exec_id}")

    def listen(
        self, graph_id: str = "*", graph_exec_id: str = "*"
    ) -> Generator[ExecutionResult, None, None]:
        for execution_result in self.listen_events(f"{graph_id}/{graph_exec_id}"):
            yield execution_result


class AsyncRedisExecutionEventBus(AsyncRedisEventBus[ExecutionResult]):
    Model = ExecutionResult

    @property
    def event_bus_name(self) -> str:
        return config.execution_event_bus_name

    async def publish(self, res: ExecutionResult):
        await self.publish_event(res, f"{res.graph_id}/{res.graph_exec_id}")

    async def listen(
        self, graph_id: str = "*", graph_exec_id: str = "*"
    ) -> AsyncGenerator[ExecutionResult, None]:
        async for execution_result in self.listen_events(f"{graph_id}/{graph_exec_id}"):
            yield execution_result
