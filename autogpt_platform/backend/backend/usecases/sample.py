from prisma.models import User

from backend.blocks.basic import AgentInputBlock, PrintToConsoleBlock
from backend.blocks.text import FillTextTemplateBlock
from backend.data import graph
from backend.data.graph import create_graph
from backend.data.user import get_or_create_user
from backend.util.test import SpinTestServer, wait_execution


async def create_test_user(alt_user: bool = False) -> User:
    if alt_user:
        test_user_data = {
            "sub": "3e53486c-cf57-477e-ba2a-cb02dc828e1b",
            "email": "testuser2@example.com",
            "name": "Test User 2",
        }
    else:
        test_user_data = {
            "sub": "ef3b97d7-1161-4eb4-92b2-10c24fb154c1",
            "email": "testuser@example.com",
            "name": "Test User",
        }
    user = await get_or_create_user(test_user_data)
    return user


def create_test_graph() -> graph.Graph:
    """
    InputBlock
               \
                 ---- FillTextTemplateBlock ---- PrintToConsoleBlock
               /
    InputBlock
    """
    nodes = [
        graph.Node(
            block_id=AgentInputBlock().id,
            input_default={"name": "input_1"},
        ),
        graph.Node(
            block_id=AgentInputBlock().id,
            input_default={"name": "input_2"},
        ),
        graph.Node(
            block_id=FillTextTemplateBlock().id,
            input_default={
                "format": "{{a}}, {{b}}{{c}}",
                "values_#_c": "!!!",
            },
        ),
        graph.Node(block_id=PrintToConsoleBlock().id),
    ]
    links = [
        graph.Link(
            source_id=nodes[0].id,
            sink_id=nodes[2].id,
            source_name="result",
            sink_name="values_#_a",
        ),
        graph.Link(
            source_id=nodes[1].id,
            sink_id=nodes[2].id,
            source_name="result",
            sink_name="values_#_b",
        ),
        graph.Link(
            source_id=nodes[2].id,
            sink_id=nodes[3].id,
            source_name="output",
            sink_name="text",
        ),
    ]

    return graph.Graph(
        name="TestGraph",
        description="Test graph",
        nodes=nodes,
        links=links,
    )


async def sample_agent():
    async with SpinTestServer() as server:
        test_user = await create_test_user()
        test_graph = await create_graph(create_test_graph(), test_user.id)
        input_data = {"input_1": "Hello", "input_2": "World"}
        response = await server.agent_server.test_execute_graph(
            graph_id=test_graph.id,
            user_id=test_user.id,
            node_input=input_data,
        )
        print(response)
        result = await wait_execution(
            test_user.id, test_graph.id, response.graph_exec_id, 10
        )
        print(result)


if __name__ == "__main__":
    import asyncio

    asyncio.run(sample_agent())
