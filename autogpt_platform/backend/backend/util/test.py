import logging
import time
import uuid
from typing import Sequence, cast

from backend.data import db
from backend.data.block import Block, BlockSchema, initialize_blocks
from backend.data.execution import ExecutionResult, ExecutionStatus
from backend.data.model import _BaseCredentials
from backend.data.user import create_default_user
from backend.executor import DatabaseManager, ExecutionManager, ExecutionScheduler
from backend.notifications.notifications import NotificationManager
from backend.server.rest_api import AgentServer
from backend.server.utils import get_user_id

log = logging.getLogger(__name__)


class SpinTestServer:
    def __init__(self):
        self.db_api = DatabaseManager()
        self.exec_manager = ExecutionManager()
        self.agent_server = AgentServer()
        self.scheduler = ExecutionScheduler()
        self.notif_manager = NotificationManager()

    @staticmethod
    def test_get_user_id():
        return "3e53486c-cf57-477e-ba2a-cb02dc828e1a"

    async def __aenter__(self):
        self.setup_dependency_overrides()
        self.db_api.__enter__()
        self.agent_server.__enter__()
        self.exec_manager.__enter__()
        self.scheduler.__enter__()
        self.notif_manager.__enter__()

        await db.connect()
        await initialize_blocks()
        await create_default_user()

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await db.disconnect()

        self.scheduler.__exit__(exc_type, exc_val, exc_tb)
        self.exec_manager.__exit__(exc_type, exc_val, exc_tb)
        self.agent_server.__exit__(exc_type, exc_val, exc_tb)
        self.db_api.__exit__(exc_type, exc_val, exc_tb)
        self.notif_manager.__exit__(exc_type, exc_val, exc_tb)

    def setup_dependency_overrides(self):
        # Override get_user_id for testing
        self.agent_server.set_test_dependency_overrides(
            {get_user_id: self.test_get_user_id}
        )


async def wait_execution(
    user_id: str,
    graph_id: str,
    graph_exec_id: str,
    timeout: int = 30,
) -> Sequence[ExecutionResult]:
    async def is_execution_completed():
        status = await AgentServer().test_get_graph_run_status(graph_exec_id, user_id)
        log.info(f"Execution status: {status}")
        if status == ExecutionStatus.FAILED:
            log.info("Execution failed")
            raise Exception("Execution failed")
        if status == ExecutionStatus.TERMINATED:
            log.info("Execution terminated")
            raise Exception("Execution terminated")
        return status == ExecutionStatus.COMPLETED

    # Wait for the executions to complete
    for i in range(timeout):
        if await is_execution_completed():
            graph_exec = await AgentServer().test_get_graph_run_results(
                graph_id, graph_exec_id, user_id
            )
            return graph_exec.node_executions
        time.sleep(1)

    assert False, "Execution did not complete in time."


def execute_block_test(block: Block):
    prefix = f"[Test-{block.name}]"

    if not block.test_input or not block.test_output:
        log.info(f"{prefix} No test data provided")
        return
    if not isinstance(block.test_input, list):
        block.test_input = [block.test_input]
    if not isinstance(block.test_output, list):
        block.test_output = [block.test_output]

    output_index = 0
    log.info(f"{prefix} Executing {len(block.test_input)} tests...")
    prefix = " " * 4 + prefix

    for mock_name, mock_obj in (block.test_mock or {}).items():
        log.info(f"{prefix} mocking {mock_name}...")
        if hasattr(block, mock_name):
            setattr(block, mock_name, mock_obj)
        else:
            log.info(f"{prefix} mock {mock_name} not found in block")

    # Populate credentials argument(s)
    extra_exec_kwargs: dict = {
        "graph_id": str(uuid.uuid4()),
        "node_id": str(uuid.uuid4()),
        "graph_exec_id": str(uuid.uuid4()),
        "node_exec_id": str(uuid.uuid4()),
        "user_id": str(uuid.uuid4()),
    }
    input_model = cast(type[BlockSchema], block.input_schema)
    credentials_input_fields = input_model.get_credentials_fields()
    if len(credentials_input_fields) == 1 and isinstance(
        block.test_credentials, _BaseCredentials
    ):
        field_name = next(iter(credentials_input_fields))
        extra_exec_kwargs[field_name] = block.test_credentials
    elif credentials_input_fields and block.test_credentials:
        if not isinstance(block.test_credentials, dict):
            raise TypeError(f"Block {block.name} has no usable test credentials")
        else:
            for field_name in credentials_input_fields:
                if field_name in block.test_credentials:
                    extra_exec_kwargs[field_name] = block.test_credentials[field_name]

    for input_data in block.test_input:
        log.info(f"{prefix} in: {input_data}")

        for output_name, output_data in block.execute(input_data, **extra_exec_kwargs):
            if output_index >= len(block.test_output):
                raise ValueError(
                    f"{prefix} produced output more than expected {output_index} >= {len(block.test_output)}:\nOutput Expected:\t\t{block.test_output}\nFailed Output Produced:\t('{output_name}', {output_data})\nNote that this may not be the one that was unexpected, but it is the first that triggered the extra output warning"
                )
            ex_output_name, ex_output_data = block.test_output[output_index]

            def compare(data, expected_data):
                if data == expected_data:
                    is_matching = True
                elif isinstance(expected_data, type):
                    is_matching = isinstance(data, expected_data)
                elif callable(expected_data):
                    is_matching = expected_data(data)
                else:
                    is_matching = False

                mark = "✅" if is_matching else "❌"
                log.info(f"{prefix} {mark} comparing `{data}` vs `{expected_data}`")
                if not is_matching:
                    raise ValueError(
                        f"{prefix}: wrong output {data} vs {expected_data}\n"
                        f"Output Expected:\t\t{block.test_output}\n"
                        f"Failed Output Produced:\t('{output_name}', {output_data})"
                    )

            compare(output_data, ex_output_data)
            compare(output_name, ex_output_name)
            output_index += 1

    if output_index < len(block.test_output):
        raise ValueError(
            f"{prefix} produced output less than expected. output_index={output_index}, len(block.test_output)={len(block.test_output)}"
        )
