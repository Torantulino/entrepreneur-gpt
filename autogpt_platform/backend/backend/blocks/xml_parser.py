from gravitasml.parser import Parser
from gravitasml.token import tokenize

from backend.data.block import Block, BlockOutput, BlockSchema
from backend.data.model import SchemaField


class XMLParserBlock(Block):
    class Input(BlockSchema):
        input_xml: str = SchemaField(description="input xml to be parsed")

    class Output(BlockSchema):
        parsed_xml: dict = SchemaField(description="output parsed xml to dict")
        error: str = SchemaField(description="Error in parsing")

    def __init__(self):
        super().__init__(
            id="286380af-9529-4b55-8be0-1d7c854abdb5",
            description="Parses XML using gravitasml to tokenize and coverts it to dict",
            input_schema=XMLParserBlock.Input,
            output_schema=XMLParserBlock.Output,
            test_input={"input_xml": "<tag1><tag2>content</tag2></tag1>"},
            test_output=[
                ("parsed_xml", {"tag1": {"tag2": "content"}}),
            ],
        )

    def run(self, input_data: Input, **kwargs) -> BlockOutput:
        try:
            tokens = tokenize(input_data.input_xml)
            parser = Parser(tokens)
            parsed_result = parser.parse()
            yield "parsed_xml", parsed_result
        except ValueError as val_e:
            raise ValueError(f"Validation error for dict:{val_e}") from val_e
        except SyntaxError as syn_e:
            raise SyntaxError(f"Error in input xml syntax: {syn_e}") from syn_e
