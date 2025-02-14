from pathlib import Path

from prisma.models import User

from backend.blocks.basic import StoreValueBlock
from backend.blocks.block import BlockInstallationBlock
from backend.blocks.http import SendWebRequestBlock
from backend.blocks.llm import AITextGeneratorBlock
from backend.blocks.text import ExtractTextInformationBlock, FillTextTemplateBlock
from backend.data.graph import Graph, Link, Node, create_graph
from backend.data.user import get_or_create_user
from backend.util.test import SpinTestServer, wait_execution

sample_block_modules = {
    "llm": "Block that calls the AI model to generate text.",
    "basic": "Block that does basic operations.",
    "text": "Blocks that do text operations.",
    "reddit": "Blocks that interacts with Reddit.",
}
sample_block_codes = {}
for module, description in sample_block_modules.items():
    current_dir = Path(__file__).parent
    file_path = current_dir.parent / "blocks" / f"{module}.py"
    with open(file_path, "r") as f:
        code = "\n".join(["```python", f.read(), "```"])
        sample_block_codes[module] = f"[Example: {description}]\n{code}"


async def create_test_user() -> User:
    test_user_data = {
        "sub": "ef3b97d7-1161-4eb4-92b2-10c24fb154c1",
        "email": "testuser@example.com",
        "name": "Test User",
    }
    user = await get_or_create_user(test_user_data)
    return user


def create_test_graph() -> Graph:
    """
            StoreValueBlock (input)
                 ||
                 v
        FillTextTemplateBlock (input query)
                 ||
                 v
         SendWebRequestBlock (browse)
                 ||
                 v
     ------> StoreValueBlock===============
    |           |  |                    ||
    |            --                     ||
    |                                   ||
    |                                   ||
    |                                    v
    |        AITextGeneratorBlock  <===== FillTextTemplateBlock (query)
    |            ||                      ^
    |            v                      ||
    |       ExtractTextInformationBlock             ||
    |            ||                     ||
    |            v                      ||
    ------ BlockInstallationBlock  ======
    """
    # ======= Nodes ========= #
    input_data = Node(block_id=StoreValueBlock().id)
    input_query_constant = Node(
        block_id=StoreValueBlock().id,
        input_default={"data": None},
    )
    input_text_formatter = Node(
        block_id=FillTextTemplateBlock().id,
        input_default={
            "format": "Show me how to make a python code for this query: `{query}`",
        },
    )
    search_http_request = Node(
        block_id=SendWebRequestBlock().id,
        input_default={
            "url": "https://osit-v2.bentlybro.com/search",
        },
    )
    search_result_constant = Node(
        block_id=StoreValueBlock().id,
        input_default={
            "data": None,
        },
    )
    prompt_text_formatter = Node(
        block_id=FillTextTemplateBlock().id,
        input_default={
            "format": """
Write me a full Block implementation for this query: `{query}`

Here is the information I get to write a Python code for that:
{search_result}

Here is your previous attempt:
{previous_attempt}
""",
            "values_#_previous_attempt": "No previous attempt found.",
        },
    )
    code_gen_llm_call = Node(
        block_id=AITextGeneratorBlock().id,
        input_default={
            "sys_prompt": f"""
You are a software engineer and you are asked to write the full class implementation.
The class that you are implementing is extending a class called `Block`.
This class will be used as a node in a graph of other blocks to build a complex system.
This class has a method called `run` that takes an input and returns an output.
It also has an `id` attribute that is a UUID, input_schema, and output_schema.
For UUID, you have to hardcode it, like `d2e2ecd2-9ae6-422d-8dfe-ceca500ce6a6`,
don't use any automatic UUID generation, because it needs to be consistent.
To validate the correctness of your implementation, you can also define a test.
There is `test_input` and `test_output` you can use to validate your implementation.
There is also `test_mock` to mock a helper function on your block class for testing.

Feel free to start your answer by explaining your plan what's required how to test, etc.
But make sure to produce the fully working implementation at the end,
and it should be enclosed within this block format:
```python
<Your implementation here>
```

Here are a couple of sample of the Block class implementation:

{"--------------".join([sample_block_codes[v] for v in sample_block_modules])}
""",
        },
    )
    code_text_parser = Node(
        block_id=ExtractTextInformationBlock().id,
        input_default={
            "pattern": "```python\n(.+?)\n```",
            "group": 1,
        },
    )
    block_installation = Node(
        block_id=BlockInstallationBlock().id,
    )
    nodes = [
        input_data,
        input_query_constant,
        input_text_formatter,
        search_http_request,
        search_result_constant,
        prompt_text_formatter,
        code_gen_llm_call,
        code_text_parser,
        block_installation,
    ]

    # ======= Links ========= #
    links = [
        Link(
            source_id=input_data.id,
            sink_id=input_query_constant.id,
            source_name="output",
            sink_name="input",
        ),
        Link(
            source_id=input_data.id,
            sink_id=input_text_formatter.id,
            source_name="output",
            sink_name="values_#_query",
        ),
        Link(
            source_id=input_query_constant.id,
            sink_id=input_query_constant.id,
            source_name="output",
            sink_name="data",
        ),
        Link(
            source_id=input_text_formatter.id,
            sink_id=search_http_request.id,
            source_name="output",
            sink_name="body_#_query",
        ),
        Link(
            source_id=search_http_request.id,
            sink_id=search_result_constant.id,
            source_name="response_#_reply",
            sink_name="input",
        ),
        Link(  # Loopback for constant block
            source_id=search_result_constant.id,
            sink_id=search_result_constant.id,
            source_name="output",
            sink_name="data",
        ),
        Link(
            source_id=search_result_constant.id,
            sink_id=prompt_text_formatter.id,
            source_name="output",
            sink_name="values_#_search_result",
        ),
        Link(
            source_id=input_query_constant.id,
            sink_id=prompt_text_formatter.id,
            source_name="output",
            sink_name="values_#_query",
        ),
        Link(
            source_id=prompt_text_formatter.id,
            sink_id=code_gen_llm_call.id,
            source_name="output",
            sink_name="prompt",
        ),
        Link(
            source_id=code_gen_llm_call.id,
            sink_id=code_text_parser.id,
            source_name="response",
            sink_name="text",
        ),
        Link(
            source_id=code_text_parser.id,
            sink_id=block_installation.id,
            source_name="positive",
            sink_name="code",
        ),
        Link(
            source_id=block_installation.id,
            sink_id=prompt_text_formatter.id,
            source_name="error",
            sink_name="values_#_previous_attempt",
        ),
        Link(  # Re-trigger search result.
            source_id=block_installation.id,
            sink_id=search_result_constant.id,
            source_name="error",
            sink_name="input",
        ),
        Link(  # Re-trigger search result.
            source_id=block_installation.id,
            sink_id=input_query_constant.id,
            source_name="error",
            sink_name="input",
        ),
    ]

    # ======= Graph ========= #
    return Graph(
        name="BlockAutoGen",
        description="Block auto generation agent",
        nodes=nodes,
        links=links,
    )


async def block_autogen_agent():
    async with SpinTestServer() as server:
        test_user = await create_test_user()
        test_graph = await create_graph(create_test_graph(), user_id=test_user.id)
        input_data = {"input": "Write me a block that writes a string into a file."}
        response = await server.agent_server.test_execute_graph(
            graph_id=test_graph.id,
            user_id=test_user.id,
            node_input=input_data,
        )
        print(response)
        result = await wait_execution(
            graph_id=test_graph.id,
            graph_exec_id=response.graph_exec_id,
            timeout=1200,
            user_id=test_user.id,
        )
        print(result)


if __name__ == "__main__":
    import asyncio

    asyncio.run(block_autogen_agent())
