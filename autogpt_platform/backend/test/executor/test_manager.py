import logging

import autogpt_libs.auth.models
import fastapi.responses
import pytest
from prisma.models import User

import backend.server.v2.library.model
import backend.server.v2.store.model
from backend.blocks.basic import AgentInputBlock, FindInDictionaryBlock, StoreValueBlock
from backend.blocks.maths import CalculatorBlock, Operation
from backend.data import execution, graph
from backend.server.model import CreateGraph
from backend.server.rest_api import AgentServer
from backend.usecases.sample import create_test_graph, create_test_user
from backend.util.test import SpinTestServer, wait_execution

logger = logging.getLogger(__name__)


async def create_graph(s: SpinTestServer, g: graph.Graph, u: User) -> graph.Graph:
    logger.info(f"Creating graph for user {u.id}")
    return await s.agent_server.test_create_graph(CreateGraph(graph=g), u.id)


async def execute_graph(
    agent_server: AgentServer,
    test_graph: graph.Graph,
    test_user: User,
    input_data: dict,
    num_execs: int = 4,
) -> str:
    logger.info(f"Executing graph {test_graph.id} for user {test_user.id}")
    logger.info(f"Input data: {input_data}")

    # --- Test adding new executions --- #
    response = await agent_server.test_execute_graph(
        user_id=test_user.id,
        graph_id=test_graph.id,
        graph_version=test_graph.version,
        node_input=input_data,
    )
    graph_exec_id = response.graph_exec_id
    logger.info(f"Created execution with ID: {graph_exec_id}")

    # Execution queue should be empty
    logger.info("Waiting for execution to complete...")
    result = await wait_execution(test_user.id, test_graph.id, graph_exec_id, 30)
    logger.info(f"Execution completed with {len(result)} results")
    assert len(result) == num_execs
    return graph_exec_id


async def assert_sample_graph_executions(
    agent_server: AgentServer,
    test_graph: graph.Graph,
    test_user: User,
    graph_exec_id: str,
):
    logger.info(f"Checking execution results for graph {test_graph.id}")
    graph_run = await agent_server.test_get_graph_run_results(
        test_graph.id,
        graph_exec_id,
        test_user.id,
    )

    output_list = [{"result": ["Hello"]}, {"result": ["World"]}]
    input_list = [
        {
            "name": "input_1",
            "value": "Hello",
        },
        {
            "name": "input_2",
            "value": "World",
        },
    ]

    # Executing StoreValueBlock
    exec = graph_run.node_executions[0]
    logger.info(f"Checking first StoreValueBlock execution: {exec}")
    assert exec.status == execution.ExecutionStatus.COMPLETED
    assert exec.graph_exec_id == graph_exec_id
    assert (
        exec.output_data in output_list
    ), f"Output data: {exec.output_data} and {output_list}"
    assert (
        exec.input_data in input_list
    ), f"Input data: {exec.input_data} and {input_list}"
    assert exec.node_id in [test_graph.nodes[0].id, test_graph.nodes[1].id]

    # Executing StoreValueBlock
    exec = graph_run.node_executions[1]
    logger.info(f"Checking second StoreValueBlock execution: {exec}")
    assert exec.status == execution.ExecutionStatus.COMPLETED
    assert exec.graph_exec_id == graph_exec_id
    assert (
        exec.output_data in output_list
    ), f"Output data: {exec.output_data} and {output_list}"
    assert (
        exec.input_data in input_list
    ), f"Input data: {exec.input_data} and {input_list}"
    assert exec.node_id in [test_graph.nodes[0].id, test_graph.nodes[1].id]

    # Executing FillTextTemplateBlock
    exec = graph_run.node_executions[2]
    logger.info(f"Checking FillTextTemplateBlock execution: {exec}")
    assert exec.status == execution.ExecutionStatus.COMPLETED
    assert exec.graph_exec_id == graph_exec_id
    assert exec.output_data == {"output": ["Hello, World!!!"]}
    assert exec.input_data == {
        "format": "{{a}}, {{b}}{{c}}",
        "values": {"a": "Hello", "b": "World", "c": "!!!"},
        "values_#_a": "Hello",
        "values_#_b": "World",
        "values_#_c": "!!!",
    }
    assert exec.node_id == test_graph.nodes[2].id

    # Executing PrintToConsoleBlock
    exec = graph_run.node_executions[3]
    logger.info(f"Checking PrintToConsoleBlock execution: {exec}")
    assert exec.status == execution.ExecutionStatus.COMPLETED
    assert exec.graph_exec_id == graph_exec_id
    assert exec.output_data == {"status": ["printed"]}
    assert exec.input_data == {"text": "Hello, World!!!"}
    assert exec.node_id == test_graph.nodes[3].id


@pytest.mark.asyncio(scope="session")
async def test_agent_execution(server: SpinTestServer):
    logger.info("Starting test_agent_execution")
    test_user = await create_test_user()
    test_graph = await create_graph(server, create_test_graph(), test_user)
    data = {"input_1": "Hello", "input_2": "World"}
    graph_exec_id = await execute_graph(
        server.agent_server,
        test_graph,
        test_user,
        data,
        4,
    )
    await assert_sample_graph_executions(
        server.agent_server, test_graph, test_user, graph_exec_id
    )
    logger.info("Completed test_agent_execution")


@pytest.mark.asyncio(scope="session")
async def test_input_pin_always_waited(server: SpinTestServer):
    """
    This test is asserting that the input pin should always be waited for the execution,
    even when default value on that pin is defined, the value has to be ignored.

    Test scenario:
    StoreValueBlock1
                \\ input
                     >------- FindInDictionaryBlock | input_default: key: "", input: {}
                // key
    StoreValueBlock2
    """
    logger.info("Starting test_input_pin_always_waited")
    nodes = [
        graph.Node(
            block_id=StoreValueBlock().id,
            input_default={"input": {"key1": "value1", "key2": "value2"}},
        ),
        graph.Node(
            block_id=StoreValueBlock().id,
            input_default={"input": "key2"},
        ),
        graph.Node(
            block_id=FindInDictionaryBlock().id,
            input_default={"key": "", "input": {}},
        ),
    ]
    links = [
        graph.Link(
            source_id=nodes[0].id,
            sink_id=nodes[2].id,
            source_name="output",
            sink_name="input",
        ),
        graph.Link(
            source_id=nodes[1].id,
            sink_id=nodes[2].id,
            source_name="output",
            sink_name="key",
        ),
    ]
    test_graph = graph.Graph(
        name="TestGraph",
        description="Test graph",
        nodes=nodes,
        links=links,
    )
    test_user = await create_test_user()
    test_graph = await create_graph(server, test_graph, test_user)
    graph_exec_id = await execute_graph(
        server.agent_server, test_graph, test_user, {}, 3
    )

    logger.info("Checking execution results")
    graph_exec = await server.agent_server.test_get_graph_run_results(
        test_graph.id, graph_exec_id, test_user.id
    )
    assert len(graph_exec.node_executions) == 3
    # FindInDictionaryBlock should wait for the input pin to be provided,
    # Hence executing extraction of "key" from {"key1": "value1", "key2": "value2"}
    assert graph_exec.node_executions[2].status == execution.ExecutionStatus.COMPLETED
    assert graph_exec.node_executions[2].output_data == {"output": ["value2"]}
    logger.info("Completed test_input_pin_always_waited")


@pytest.mark.asyncio(scope="session")
async def test_static_input_link_on_graph(server: SpinTestServer):
    """
    This test is asserting the behaviour of static input link, e.g: reusable input link.

    Test scenario:
    *StoreValueBlock1*===a=========\\
    *StoreValueBlock2*===a=====\\  ||
    *StoreValueBlock3*===a===*MathBlock*====b / static====*StoreValueBlock5*
    *StoreValueBlock4*=========================================//

    In this test, there will be three input waiting in the MathBlock input pin `a`.
    And later, another output is produced on input pin `b`, which is a static link,
    this input will complete the input of those three incomplete executions.
    """
    logger.info("Starting test_static_input_link_on_graph")
    nodes = [
        graph.Node(block_id=StoreValueBlock().id, input_default={"input": 4}),  # a
        graph.Node(block_id=StoreValueBlock().id, input_default={"input": 4}),  # a
        graph.Node(block_id=StoreValueBlock().id, input_default={"input": 4}),  # a
        graph.Node(block_id=StoreValueBlock().id, input_default={"input": 5}),  # b
        graph.Node(block_id=StoreValueBlock().id),
        graph.Node(
            block_id=CalculatorBlock().id,
            input_default={"operation": Operation.ADD.value},
        ),
    ]
    links = [
        graph.Link(
            source_id=nodes[0].id,
            sink_id=nodes[5].id,
            source_name="output",
            sink_name="a",
        ),
        graph.Link(
            source_id=nodes[1].id,
            sink_id=nodes[5].id,
            source_name="output",
            sink_name="a",
        ),
        graph.Link(
            source_id=nodes[2].id,
            sink_id=nodes[5].id,
            source_name="output",
            sink_name="a",
        ),
        graph.Link(
            source_id=nodes[3].id,
            sink_id=nodes[4].id,
            source_name="output",
            sink_name="input",
        ),
        graph.Link(
            source_id=nodes[4].id,
            sink_id=nodes[5].id,
            source_name="output",
            sink_name="b",
            is_static=True,  # This is the static link to test.
        ),
    ]
    test_graph = graph.Graph(
        name="TestGraph",
        description="Test graph",
        nodes=nodes,
        links=links,
    )
    test_user = await create_test_user()
    test_graph = await create_graph(server, test_graph, test_user)
    graph_exec_id = await execute_graph(
        server.agent_server, test_graph, test_user, {}, 8
    )
    logger.info("Checking execution results")
    graph_exec = await server.agent_server.test_get_graph_run_results(
        test_graph.id, graph_exec_id, test_user.id
    )
    assert len(graph_exec.node_executions) == 8
    # The last 3 executions will be a+b=4+5=9
    for i, exec_data in enumerate(graph_exec.node_executions[-3:]):
        logger.info(f"Checking execution {i+1} of last 3: {exec_data}")
        assert exec_data.status == execution.ExecutionStatus.COMPLETED
        assert exec_data.output_data == {"result": [9]}
    logger.info("Completed test_static_input_link_on_graph")


@pytest.mark.asyncio(scope="session")
async def test_execute_preset(server: SpinTestServer):
    """
    Test executing a preset.

    This test ensures that:
    1. A preset can be successfully executed
    2. The execution results are correct

    Args:
        server (SpinTestServer): The test server instance.
    """
    # Create test graph and user
    nodes = [
        graph.Node(  # 0
            block_id=AgentInputBlock().id,
            input_default={"name": "dictionary"},
        ),
        graph.Node(  # 1
            block_id=AgentInputBlock().id,
            input_default={"name": "selected_value"},
        ),
        graph.Node(  # 2
            block_id=StoreValueBlock().id,
            input_default={"input": {"key1": "Hi", "key2": "Everyone"}},
        ),
        graph.Node(  # 3
            block_id=FindInDictionaryBlock().id,
            input_default={"key": "", "input": {}},
        ),
    ]
    links = [
        graph.Link(
            source_id=nodes[0].id,
            sink_id=nodes[2].id,
            source_name="result",
            sink_name="input",
        ),
        graph.Link(
            source_id=nodes[1].id,
            sink_id=nodes[3].id,
            source_name="result",
            sink_name="key",
        ),
        graph.Link(
            source_id=nodes[2].id,
            sink_id=nodes[3].id,
            source_name="output",
            sink_name="input",
        ),
    ]
    test_graph = graph.Graph(
        name="TestGraph",
        description="Test graph",
        nodes=nodes,
        links=links,
    )
    test_user = await create_test_user()
    test_graph = await create_graph(server, test_graph, test_user)

    # Create preset with initial values
    preset = backend.server.v2.library.model.CreateLibraryAgentPresetRequest(
        name="Test Preset With Clash",
        description="Test preset with clashing input values",
        agent_id=test_graph.id,
        agent_version=test_graph.version,
        inputs={
            "dictionary": {"key1": "Hello", "key2": "World"},
            "selected_value": "key2",
        },
        is_active=True,
    )
    created_preset = await server.agent_server.test_create_preset(preset, test_user.id)

    # Execute preset with overriding values
    result = await server.agent_server.test_execute_preset(
        graph_id=test_graph.id,
        graph_version=test_graph.version,
        preset_id=created_preset.id,
        user_id=test_user.id,
    )

    # Verify execution
    assert result is not None
    graph_exec_id = result["id"]

    # Wait for execution to complete
    executions = await wait_execution(test_user.id, test_graph.id, graph_exec_id)
    assert len(executions) == 4

    # FindInDictionaryBlock should wait for the input pin to be provided,
    # Hence executing extraction of "key" from {"key1": "value1", "key2": "value2"}
    assert executions[3].status == execution.ExecutionStatus.COMPLETED
    assert executions[3].output_data == {"output": ["World"]}


@pytest.mark.asyncio(scope="session")
async def test_execute_preset_with_clash(server: SpinTestServer):
    """
    Test executing a preset with clashing input data.
    """
    # Create test graph and user
    nodes = [
        graph.Node(  # 0
            block_id=AgentInputBlock().id,
            input_default={"name": "dictionary"},
        ),
        graph.Node(  # 1
            block_id=AgentInputBlock().id,
            input_default={"name": "selected_value"},
        ),
        graph.Node(  # 2
            block_id=StoreValueBlock().id,
            input_default={"input": {"key1": "Hi", "key2": "Everyone"}},
        ),
        graph.Node(  # 3
            block_id=FindInDictionaryBlock().id,
            input_default={"key": "", "input": {}},
        ),
    ]
    links = [
        graph.Link(
            source_id=nodes[0].id,
            sink_id=nodes[2].id,
            source_name="result",
            sink_name="input",
        ),
        graph.Link(
            source_id=nodes[1].id,
            sink_id=nodes[3].id,
            source_name="result",
            sink_name="key",
        ),
        graph.Link(
            source_id=nodes[2].id,
            sink_id=nodes[3].id,
            source_name="output",
            sink_name="input",
        ),
    ]
    test_graph = graph.Graph(
        name="TestGraph",
        description="Test graph",
        nodes=nodes,
        links=links,
    )
    test_user = await create_test_user()
    test_graph = await create_graph(server, test_graph, test_user)

    # Create preset with initial values
    preset = backend.server.v2.library.model.CreateLibraryAgentPresetRequest(
        name="Test Preset With Clash",
        description="Test preset with clashing input values",
        agent_id=test_graph.id,
        agent_version=test_graph.version,
        inputs={
            "dictionary": {"key1": "Hello", "key2": "World"},
            "selected_value": "key2",
        },
        is_active=True,
    )
    created_preset = await server.agent_server.test_create_preset(preset, test_user.id)

    # Execute preset with overriding values
    result = await server.agent_server.test_execute_preset(
        graph_id=test_graph.id,
        graph_version=test_graph.version,
        preset_id=created_preset.id,
        node_input={"selected_value": "key1"},
        user_id=test_user.id,
    )

    # Verify execution
    assert result is not None
    graph_exec_id = result["id"]

    # Wait for execution to complete
    executions = await wait_execution(test_user.id, test_graph.id, graph_exec_id)
    assert len(executions) == 4

    # FindInDictionaryBlock should wait for the input pin to be provided,
    # Hence executing extraction of "key" from {"key1": "value1", "key2": "value2"}
    assert executions[3].status == execution.ExecutionStatus.COMPLETED
    assert executions[3].output_data == {"output": ["Hello"]}


@pytest.mark.asyncio(scope="session")
async def test_store_listing_graph(server: SpinTestServer):
    logger.info("Starting test_agent_execution")
    test_user = await create_test_user()
    test_graph = await create_graph(server, create_test_graph(), test_user)

    store_submission_request = backend.server.v2.store.model.StoreSubmissionRequest(
        agent_id=test_graph.id,
        agent_version=test_graph.version,
        slug="test-slug",
        name="Test name",
        sub_heading="Test sub heading",
        video_url=None,
        image_urls=[],
        description="Test description",
        categories=[],
    )

    store_listing = await server.agent_server.test_create_store_listing(
        store_submission_request, test_user.id
    )

    if isinstance(store_listing, fastapi.responses.JSONResponse):
        assert False, "Failed to create store listing"

    slv_id = (
        store_listing.store_listing_version_id
        if store_listing.store_listing_version_id is not None
        else None
    )

    assert slv_id is not None

    admin_user = await create_test_user(alt_user=True)
    await server.agent_server.test_review_store_listing(
        backend.server.v2.store.model.ReviewSubmissionRequest(
            store_listing_version_id=slv_id,
            is_approved=True,
            comments="Test comments",
        ),
        autogpt_libs.auth.models.User(
            user_id=admin_user.id,
            role="admin",
            email=admin_user.email,
            phone_number="1234567890",
        ),
    )
    alt_test_user = admin_user

    data = {"input_1": "Hello", "input_2": "World"}
    graph_exec_id = await execute_graph(
        server.agent_server,
        test_graph,
        alt_test_user,
        data,
        4,
    )

    await assert_sample_graph_executions(
        server.agent_server, test_graph, alt_test_user, graph_exec_id
    )
    logger.info("Completed test_agent_execution")
