import ast
import logging
from abc import ABC
from enum import Enum, EnumMeta
from json import JSONDecodeError
from types import MappingProxyType
from typing import TYPE_CHECKING, Any, List, Literal, NamedTuple

from pydantic import SecretStr

from backend.integrations.providers import ProviderName

if TYPE_CHECKING:
    from enum import _EnumMemberT

import anthropic
import ollama
import openai
from groq import Groq

from backend.data.block import Block, BlockCategory, BlockOutput, BlockSchema
from backend.data.model import (
    APIKeyCredentials,
    CredentialsField,
    CredentialsMetaInput,
    SchemaField,
)
from backend.util import json
from backend.util.settings import BehaveAs, Settings
from backend.util.text import TextFormatter

logger = logging.getLogger(__name__)
fmt = TextFormatter()

LLMProviderName = Literal[
    ProviderName.ANTHROPIC,
    ProviderName.GROQ,
    ProviderName.OLLAMA,
    ProviderName.OPENAI,
    ProviderName.OPEN_ROUTER,
    ProviderName.AIML_API,
]
AICredentials = CredentialsMetaInput[LLMProviderName, Literal["api_key"]]

TEST_CREDENTIALS = APIKeyCredentials(
    id="ed55ac19-356e-4243-a6cb-bc599e9b716f",
    provider="openai",
    api_key=SecretStr("mock-openai-api-key"),
    title="Mock OpenAI API key",
    expires_at=None,
)
TEST_CREDENTIALS_INPUT = {
    "provider": TEST_CREDENTIALS.provider,
    "id": TEST_CREDENTIALS.id,
    "type": TEST_CREDENTIALS.type,
    "title": TEST_CREDENTIALS.title,
}


def AICredentialsField() -> AICredentials:
    return CredentialsField(
        description="API key for the LLM provider.",
        discriminator="model",
        discriminator_mapping={
            model.value: model.metadata.provider for model in LlmModel
        },
    )


class ModelMetadata(NamedTuple):
    provider: str
    context_window: int
    max_output_tokens: int | None


class LlmModelMeta(EnumMeta):
    @property
    def __members__(
        self: type["_EnumMemberT"],
    ) -> MappingProxyType[str, "_EnumMemberT"]:
        if Settings().config.behave_as == BehaveAs.LOCAL:
            members = super().__members__
            return members
        else:
            removed_providers = ["ollama"]
            existing_members = super().__members__
            members = {
                name: member
                for name, member in existing_members.items()
                if LlmModel[name].provider not in removed_providers
            }
            return MappingProxyType(members)


class LlmModel(str, Enum, metaclass=LlmModelMeta):
    # OpenAI models
    O3_MINI = "o3-mini"
    O1 = "o1"
    O1_PREVIEW = "o1-preview"
    O1_MINI = "o1-mini"
    GPT4O_MINI = "gpt-4o-mini"
    GPT4O = "gpt-4o"
    GPT4_TURBO = "gpt-4-turbo"
    GPT3_5_TURBO = "gpt-3.5-turbo"
    # Anthropic models
    CLAUDE_3_5_SONNET = "claude-3-5-sonnet-latest"
    CLAUDE_3_5_HAIKU = "claude-3-5-haiku-latest"
    CLAUDE_3_HAIKU = "claude-3-haiku-20240307"
    # AI/ML API models
    AIML_API_QWEN2_5_72B = "Qwen/Qwen2.5-72B-Instruct-Turbo"
    AIML_API_LLAMA3_1_70B = "nvidia/llama-3.1-nemotron-70b-instruct"
    AIML_API_LLAMA3_3_70B = "meta-llama/Llama-3.3-70B-Instruct-Turbo"
    AIML_API_META_LLAMA_3_1_70B = "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo"
    AIML_API_LLAMA_3_2_3B = "meta-llama/Llama-3.2-3B-Instruct-Turbo"
    # Groq models
    GEMMA2_9B = "gemma2-9b-it"
    LLAMA3_3_70B = "llama-3.3-70b-versatile"
    LLAMA3_1_8B = "llama-3.1-8b-instant"
    LLAMA3_70B = "llama3-70b-8192"
    LLAMA3_8B = "llama3-8b-8192"
    MIXTRAL_8X7B = "mixtral-8x7b-32768"
    # Groq preview models
    DEEPSEEK_LLAMA_70B = "deepseek-r1-distill-llama-70b"
    # Ollama models
    OLLAMA_LLAMA3_3 = "llama3.3"
    OLLAMA_LLAMA3_2 = "llama3.2"
    OLLAMA_LLAMA3_8B = "llama3"
    OLLAMA_LLAMA3_405B = "llama3.1:405b"
    OLLAMA_DOLPHIN = "dolphin-mistral:latest"
    # OpenRouter models
    GEMINI_FLASH_1_5 = "google/gemini-flash-1.5"
    GROK_BETA = "x-ai/grok-beta"
    MISTRAL_NEMO = "mistralai/mistral-nemo"
    COHERE_COMMAND_R_08_2024 = "cohere/command-r-08-2024"
    COHERE_COMMAND_R_PLUS_08_2024 = "cohere/command-r-plus-08-2024"
    EVA_QWEN_2_5_32B = "eva-unit-01/eva-qwen-2.5-32b"
    DEEPSEEK_CHAT = "deepseek/deepseek-chat"  # Actually: DeepSeek V3
    PERPLEXITY_LLAMA_3_1_SONAR_LARGE_128K_ONLINE = (
        "perplexity/llama-3.1-sonar-large-128k-online"
    )
    QWEN_QWQ_32B_PREVIEW = "qwen/qwq-32b-preview"
    NOUSRESEARCH_HERMES_3_LLAMA_3_1_405B = "nousresearch/hermes-3-llama-3.1-405b"
    NOUSRESEARCH_HERMES_3_LLAMA_3_1_70B = "nousresearch/hermes-3-llama-3.1-70b"
    AMAZON_NOVA_LITE_V1 = "amazon/nova-lite-v1"
    AMAZON_NOVA_MICRO_V1 = "amazon/nova-micro-v1"
    AMAZON_NOVA_PRO_V1 = "amazon/nova-pro-v1"
    MICROSOFT_WIZARDLM_2_8X22B = "microsoft/wizardlm-2-8x22b"
    GRYPHE_MYTHOMAX_L2_13B = "gryphe/mythomax-l2-13b"

    @property
    def metadata(self) -> ModelMetadata:
        return MODEL_METADATA[self]

    @property
    def provider(self) -> str:
        return self.metadata.provider

    @property
    def context_window(self) -> int:
        return self.metadata.context_window

    @property
    def max_output_tokens(self) -> int | None:
        return self.metadata.max_output_tokens


MODEL_METADATA = {
    # https://platform.openai.com/docs/models
    LlmModel.O3_MINI: ModelMetadata("openai", 200000, 100000),  # o3-mini-2025-01-31
    LlmModel.O1: ModelMetadata("openai", 200000, 100000),  # o1-2024-12-17
    LlmModel.O1_PREVIEW: ModelMetadata(
        "openai", 128000, 32768
    ),  # o1-preview-2024-09-12
    LlmModel.O1_MINI: ModelMetadata("openai", 128000, 65536),  # o1-mini-2024-09-12
    LlmModel.GPT4O_MINI: ModelMetadata(
        "openai", 128000, 16384
    ),  # gpt-4o-mini-2024-07-18
    LlmModel.GPT4O: ModelMetadata("openai", 128000, 16384),  # gpt-4o-2024-08-06
    LlmModel.GPT4_TURBO: ModelMetadata(
        "openai", 128000, 4096
    ),  # gpt-4-turbo-2024-04-09
    LlmModel.GPT3_5_TURBO: ModelMetadata("openai", 16385, 4096),  # gpt-3.5-turbo-0125
    # https://docs.anthropic.com/en/docs/about-claude/models
    LlmModel.CLAUDE_3_5_SONNET: ModelMetadata(
        "anthropic", 200000, 8192
    ),  # claude-3-5-sonnet-20241022
    LlmModel.CLAUDE_3_5_HAIKU: ModelMetadata(
        "anthropic", 200000, 8192
    ),  # claude-3-5-haiku-20241022
    LlmModel.CLAUDE_3_HAIKU: ModelMetadata(
        "anthropic", 200000, 4096
    ),  # claude-3-haiku-20240307
    # https://docs.aimlapi.com/api-overview/model-database/text-models
    LlmModel.AIML_API_QWEN2_5_72B: ModelMetadata("aiml_api", 32000, 8000),
    LlmModel.AIML_API_LLAMA3_1_70B: ModelMetadata("aiml_api", 128000, 40000),
    LlmModel.AIML_API_LLAMA3_3_70B: ModelMetadata("aiml_api", 128000, None),
    LlmModel.AIML_API_META_LLAMA_3_1_70B: ModelMetadata("aiml_api", 131000, 2000),
    LlmModel.AIML_API_LLAMA_3_2_3B: ModelMetadata("aiml_api", 128000, None),
    # https://console.groq.com/docs/models
    LlmModel.GEMMA2_9B: ModelMetadata("groq", 8192, None),
    LlmModel.LLAMA3_3_70B: ModelMetadata("groq", 128000, 32768),
    LlmModel.LLAMA3_1_8B: ModelMetadata("groq", 128000, 8192),
    LlmModel.LLAMA3_70B: ModelMetadata("groq", 8192, None),
    LlmModel.LLAMA3_8B: ModelMetadata("groq", 8192, None),
    LlmModel.MIXTRAL_8X7B: ModelMetadata("groq", 32768, None),
    LlmModel.DEEPSEEK_LLAMA_70B: ModelMetadata("groq", 128000, None),
    # https://ollama.com/library
    LlmModel.OLLAMA_LLAMA3_3: ModelMetadata("ollama", 8192, None),
    LlmModel.OLLAMA_LLAMA3_2: ModelMetadata("ollama", 8192, None),
    LlmModel.OLLAMA_LLAMA3_8B: ModelMetadata("ollama", 8192, None),
    LlmModel.OLLAMA_LLAMA3_405B: ModelMetadata("ollama", 8192, None),
    LlmModel.OLLAMA_DOLPHIN: ModelMetadata("ollama", 32768, None),
    # https://openrouter.ai/models
    LlmModel.GEMINI_FLASH_1_5: ModelMetadata("open_router", 1000000, 8192),
    LlmModel.GROK_BETA: ModelMetadata("open_router", 131072, 131072),
    LlmModel.MISTRAL_NEMO: ModelMetadata("open_router", 128000, 4096),
    LlmModel.COHERE_COMMAND_R_08_2024: ModelMetadata("open_router", 128000, 4096),
    LlmModel.COHERE_COMMAND_R_PLUS_08_2024: ModelMetadata("open_router", 128000, 4096),
    LlmModel.EVA_QWEN_2_5_32B: ModelMetadata("open_router", 16384, 4096),
    LlmModel.DEEPSEEK_CHAT: ModelMetadata("open_router", 64000, 2048),
    LlmModel.PERPLEXITY_LLAMA_3_1_SONAR_LARGE_128K_ONLINE: ModelMetadata(
        "open_router", 127072, 127072
    ),
    LlmModel.QWEN_QWQ_32B_PREVIEW: ModelMetadata("open_router", 32768, 32768),
    LlmModel.NOUSRESEARCH_HERMES_3_LLAMA_3_1_405B: ModelMetadata(
        "open_router", 131000, 4096
    ),
    LlmModel.NOUSRESEARCH_HERMES_3_LLAMA_3_1_70B: ModelMetadata(
        "open_router", 12288, 12288
    ),
    LlmModel.AMAZON_NOVA_LITE_V1: ModelMetadata("open_router", 300000, 5120),
    LlmModel.AMAZON_NOVA_MICRO_V1: ModelMetadata("open_router", 128000, 5120),
    LlmModel.AMAZON_NOVA_PRO_V1: ModelMetadata("open_router", 300000, 5120),
    LlmModel.MICROSOFT_WIZARDLM_2_8X22B: ModelMetadata("open_router", 65536, 4096),
    LlmModel.GRYPHE_MYTHOMAX_L2_13B: ModelMetadata("open_router", 4096, 4096),
}

for model in LlmModel:
    if model not in MODEL_METADATA:
        raise ValueError(f"Missing MODEL_METADATA metadata for model: {model}")


class MessageRole(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


class Message(BlockSchema):
    role: MessageRole
    content: str


class AIBlockBase(Block, ABC):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.prompt = ""

    def merge_llm_stats(self, block: "AIBlockBase"):
        self.merge_stats(block.execution_stats)
        self.prompt = block.prompt


class AIStructuredResponseGeneratorBlock(AIBlockBase):
    class Input(BlockSchema):
        prompt: str = SchemaField(
            description="The prompt to send to the language model.",
            placeholder="Enter your prompt here...",
        )
        expected_format: dict[str, str] = SchemaField(
            description="Expected format of the response. If provided, the response will be validated against this format. "
            "The keys should be the expected fields in the response, and the values should be the description of the field.",
        )
        model: LlmModel = SchemaField(
            title="LLM Model",
            default=LlmModel.GPT4_TURBO,
            description="The language model to use for answering the prompt.",
            advanced=False,
        )
        credentials: AICredentials = AICredentialsField()
        sys_prompt: str = SchemaField(
            title="System Prompt",
            default="",
            description="The system prompt to provide additional context to the model.",
        )
        conversation_history: list[Message] = SchemaField(
            default=[],
            description="The conversation history to provide context for the prompt.",
        )
        retry: int = SchemaField(
            title="Retry Count",
            default=3,
            description="Number of times to retry the LLM call if the response does not match the expected format.",
        )
        prompt_values: dict[str, str] = SchemaField(
            advanced=False,
            default={},
            description="Values used to fill in the prompt. The values can be used in the prompt by putting them in a double curly braces, e.g. {{variable_name}}.",
        )
        max_tokens: int | None = SchemaField(
            advanced=True,
            default=None,
            description="The maximum number of tokens to generate in the chat completion.",
        )

        ollama_host: str = SchemaField(
            advanced=True,
            default="localhost:11434",
            description="Ollama host for local  models",
        )

    class Output(BlockSchema):
        response: dict[str, Any] = SchemaField(
            description="The response object generated by the language model."
        )
        prompt: str = SchemaField(description="The prompt sent to the language model.")
        error: str = SchemaField(description="Error message if the API call failed.")

    def __init__(self):
        super().__init__(
            id="ed55ac19-356e-4243-a6cb-bc599e9b716f",
            description="Call a Large Language Model (LLM) to generate formatted object based on the given prompt.",
            categories={BlockCategory.AI},
            input_schema=AIStructuredResponseGeneratorBlock.Input,
            output_schema=AIStructuredResponseGeneratorBlock.Output,
            test_input={
                "model": LlmModel.GPT4_TURBO,
                "credentials": TEST_CREDENTIALS_INPUT,
                "expected_format": {
                    "key1": "value1",
                    "key2": "value2",
                },
                "prompt": "User prompt",
            },
            test_credentials=TEST_CREDENTIALS,
            test_output=[
                ("response", {"key1": "key1Value", "key2": "key2Value"}),
                ("prompt", str),
            ],
            test_mock={
                "llm_call": lambda *args, **kwargs: (
                    json.dumps(
                        {
                            "key1": "key1Value",
                            "key2": "key2Value",
                        }
                    ),
                    0,
                    0,
                )
            },
        )
        self.prompt = ""

    def llm_call(
        self,
        credentials: APIKeyCredentials,
        llm_model: LlmModel,
        prompt: list[dict],
        json_format: bool,
        max_tokens: int | None,
        ollama_host: str = "localhost:11434",
    ) -> tuple[str, int, int]:
        """
        Args:
            credentials: The API key credentials to use.
            llm_model: The LLM model to use.
            prompt: The prompt to send to the LLM.
            json_format: Whether the response should be in JSON format.
            max_tokens: The maximum number of tokens to generate in the chat completion.
            ollama_host: The host for ollama to use

        Returns:
            The response from the LLM.
            The number of tokens used in the prompt.
            The number of tokens used in the completion.
        """
        provider = llm_model.metadata.provider
        max_tokens = max_tokens or llm_model.max_output_tokens or 4096

        if provider == "openai":
            oai_client = openai.OpenAI(api_key=credentials.api_key.get_secret_value())
            response_format = None

            if llm_model in [LlmModel.O1_MINI, LlmModel.O1_PREVIEW]:
                sys_messages = [p["content"] for p in prompt if p["role"] == "system"]
                usr_messages = [p["content"] for p in prompt if p["role"] != "system"]
                prompt = [
                    {"role": "user", "content": "\n".join(sys_messages)},
                    {"role": "user", "content": "\n".join(usr_messages)},
                ]
            elif json_format:
                response_format = {"type": "json_object"}

            response = oai_client.chat.completions.create(
                model=llm_model.value,
                messages=prompt,  # type: ignore
                response_format=response_format,  # type: ignore
                max_completion_tokens=max_tokens,
            )
            self.prompt = json.dumps(prompt)

            return (
                response.choices[0].message.content or "",
                response.usage.prompt_tokens if response.usage else 0,
                response.usage.completion_tokens if response.usage else 0,
            )
        elif provider == "anthropic":
            system_messages = [p["content"] for p in prompt if p["role"] == "system"]
            sysprompt = " ".join(system_messages)

            messages = []
            last_role = None
            for p in prompt:
                if p["role"] in ["user", "assistant"]:
                    if p["role"] != last_role:
                        messages.append({"role": p["role"], "content": p["content"]})
                        last_role = p["role"]
                    else:
                        # If the role is the same as the last one, combine the content
                        messages[-1]["content"] += "\n" + p["content"]

            client = anthropic.Anthropic(api_key=credentials.api_key.get_secret_value())
            try:
                resp = client.messages.create(
                    model=llm_model.value,
                    system=sysprompt,
                    messages=messages,
                    max_tokens=max_tokens,
                )
                self.prompt = json.dumps(prompt)

                if not resp.content:
                    raise ValueError("No content returned from Anthropic.")

                return (
                    (
                        resp.content[0].name
                        if isinstance(resp.content[0], anthropic.types.ToolUseBlock)
                        else resp.content[0].text
                    ),
                    resp.usage.input_tokens,
                    resp.usage.output_tokens,
                )
            except anthropic.APIError as e:
                error_message = f"Anthropic API error: {str(e)}"
                logger.error(error_message)
                raise ValueError(error_message)
        elif provider == "groq":
            client = Groq(api_key=credentials.api_key.get_secret_value())
            response_format = {"type": "json_object"} if json_format else None
            response = client.chat.completions.create(
                model=llm_model.value,
                messages=prompt,  # type: ignore
                response_format=response_format,  # type: ignore
                max_tokens=max_tokens,
            )
            self.prompt = json.dumps(prompt)
            return (
                response.choices[0].message.content or "",
                response.usage.prompt_tokens if response.usage else 0,
                response.usage.completion_tokens if response.usage else 0,
            )
        elif provider == "ollama":
            client = ollama.Client(host=ollama_host)
            sys_messages = [p["content"] for p in prompt if p["role"] == "system"]
            usr_messages = [p["content"] for p in prompt if p["role"] != "system"]
            response = client.generate(
                model=llm_model.value,
                prompt=f"{sys_messages}\n\n{usr_messages}",
                stream=False,
            )
            self.prompt = json.dumps(prompt)
            return (
                response.get("response") or "",
                response.get("prompt_eval_count") or 0,
                response.get("eval_count") or 0,
            )
        elif provider == "open_router":
            client = openai.OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=credentials.api_key.get_secret_value(),
            )

            response = client.chat.completions.create(
                extra_headers={
                    "HTTP-Referer": "https://agpt.co",
                    "X-Title": "AutoGPT",
                },
                model=llm_model.value,
                messages=prompt,  # type: ignore
                max_tokens=max_tokens,
            )
            self.prompt = json.dumps(prompt)

            # If there's no response, raise an error
            if not response.choices:
                if response:
                    raise ValueError(f"OpenRouter error: {response}")
                else:
                    raise ValueError("No response from OpenRouter.")

            return (
                response.choices[0].message.content or "",
                response.usage.prompt_tokens if response.usage else 0,
                response.usage.completion_tokens if response.usage else 0,
            )
        elif provider == "aiml_api":
            client = openai.OpenAI(
                base_url="https://api.aimlapi.com/v2",
                api_key=credentials.api_key.get_secret_value(),
                default_headers={"X-Project": "AutoGPT"},
            )

            completion = client.chat.completions.create(
                model=llm_model.value,
                messages=prompt,  # type: ignore
                max_tokens=max_tokens,
            )

            return (
                completion.choices[0].message.content or "",
                completion.usage.prompt_tokens if completion.usage else 0,
                completion.usage.completion_tokens if completion.usage else 0,
            )
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")

    def run(
        self, input_data: Input, *, credentials: APIKeyCredentials, **kwargs
    ) -> BlockOutput:
        logger.debug(f"Calling LLM with input data: {input_data}")
        prompt = [p.model_dump() for p in input_data.conversation_history]

        def trim_prompt(s: str) -> str:
            lines = s.strip().split("\n")
            return "\n".join([line.strip().lstrip("|") for line in lines])

        values = input_data.prompt_values
        if values:
            input_data.prompt = fmt.format_string(input_data.prompt, values)
            input_data.sys_prompt = fmt.format_string(input_data.sys_prompt, values)

        if input_data.sys_prompt:
            prompt.append({"role": "system", "content": input_data.sys_prompt})

        if input_data.expected_format:
            expected_format = [
                f'"{k}": "{v}"' for k, v in input_data.expected_format.items()
            ]
            format_prompt = ",\n  ".join(expected_format)
            sys_prompt = trim_prompt(
                f"""
                  |Reply strictly only in the following JSON format:
                  |{{
                  |  {format_prompt}
                  |}}
                """
            )
            prompt.append({"role": "system", "content": sys_prompt})

        if input_data.prompt:
            prompt.append({"role": "user", "content": input_data.prompt})

        def parse_response(resp: str) -> tuple[dict[str, Any], str | None]:
            try:
                parsed = json.loads(resp)
                if not isinstance(parsed, dict):
                    return {}, f"Expected a dictionary, but got {type(parsed)}"
                miss_keys = set(input_data.expected_format.keys()) - set(parsed.keys())
                if miss_keys:
                    return parsed, f"Missing keys: {miss_keys}"
                return parsed, None
            except JSONDecodeError as e:
                return {}, f"JSON decode error: {e}"

        logger.info(f"LLM request: {prompt}")
        retry_prompt = ""
        llm_model = input_data.model

        for retry_count in range(input_data.retry):
            try:
                response_text, input_token, output_token = self.llm_call(
                    credentials=credentials,
                    llm_model=llm_model,
                    prompt=prompt,
                    json_format=bool(input_data.expected_format),
                    ollama_host=input_data.ollama_host,
                    max_tokens=input_data.max_tokens,
                )
                self.merge_stats(
                    {
                        "input_token_count": input_token,
                        "output_token_count": output_token,
                    }
                )
                logger.info(f"LLM attempt-{retry_count} response: {response_text}")

                if input_data.expected_format:
                    parsed_dict, parsed_error = parse_response(response_text)
                    if not parsed_error:
                        yield "response", {
                            k: (
                                json.loads(v)
                                if isinstance(v, str)
                                and v.startswith("[")
                                and v.endswith("]")
                                else (", ".join(v) if isinstance(v, list) else v)
                            )
                            for k, v in parsed_dict.items()
                        }
                        yield "prompt", self.prompt
                        return
                else:
                    yield "response", {"response": response_text}
                    yield "prompt", self.prompt
                    return

                retry_prompt = trim_prompt(
                    f"""
                  |This is your previous error response:
                  |--
                  |{response_text}
                  |--
                  |
                  |And this is the error:
                  |--
                  |{parsed_error}
                  |--
                """
                )
                prompt.append({"role": "user", "content": retry_prompt})
            except Exception as e:
                logger.exception(f"Error calling LLM: {e}")
                retry_prompt = f"Error calling LLM: {e}"
            finally:
                self.merge_stats(
                    {
                        "llm_call_count": retry_count + 1,
                        "llm_retry_count": retry_count,
                    }
                )

        raise RuntimeError(retry_prompt)


class AITextGeneratorBlock(AIBlockBase):
    class Input(BlockSchema):
        prompt: str = SchemaField(
            description="The prompt to send to the language model. You can use any of the {keys} from Prompt Values to fill in the prompt with values from the prompt values dictionary by putting them in curly braces.",
            placeholder="Enter your prompt here...",
        )
        model: LlmModel = SchemaField(
            title="LLM Model",
            default=LlmModel.GPT4_TURBO,
            description="The language model to use for answering the prompt.",
            advanced=False,
        )
        credentials: AICredentials = AICredentialsField()
        sys_prompt: str = SchemaField(
            title="System Prompt",
            default="",
            description="The system prompt to provide additional context to the model.",
        )
        retry: int = SchemaField(
            title="Retry Count",
            default=3,
            description="Number of times to retry the LLM call if the response does not match the expected format.",
        )
        prompt_values: dict[str, str] = SchemaField(
            advanced=False,
            default={},
            description="Values used to fill in the prompt. The values can be used in the prompt by putting them in a double curly braces, e.g. {{variable_name}}.",
        )
        ollama_host: str = SchemaField(
            advanced=True,
            default="localhost:11434",
            description="Ollama host for local  models",
        )
        max_tokens: int | None = SchemaField(
            advanced=True,
            default=None,
            description="The maximum number of tokens to generate in the chat completion.",
        )

    class Output(BlockSchema):
        response: str = SchemaField(
            description="The response generated by the language model."
        )
        prompt: str = SchemaField(description="The prompt sent to the language model.")
        error: str = SchemaField(description="Error message if the API call failed.")

    def __init__(self):
        super().__init__(
            id="1f292d4a-41a4-4977-9684-7c8d560b9f91",
            description="Call a Large Language Model (LLM) to generate a string based on the given prompt.",
            categories={BlockCategory.AI},
            input_schema=AITextGeneratorBlock.Input,
            output_schema=AITextGeneratorBlock.Output,
            test_input={
                "prompt": "User prompt",
                "credentials": TEST_CREDENTIALS_INPUT,
            },
            test_credentials=TEST_CREDENTIALS,
            test_output=[
                ("response", "Response text"),
                ("prompt", str),
            ],
            test_mock={"llm_call": lambda *args, **kwargs: "Response text"},
        )

    def llm_call(
        self,
        input_data: AIStructuredResponseGeneratorBlock.Input,
        credentials: APIKeyCredentials,
    ) -> str:
        block = AIStructuredResponseGeneratorBlock()
        response = block.run_once(input_data, "response", credentials=credentials)
        self.merge_llm_stats(block)
        return response["response"]

    def run(
        self, input_data: Input, *, credentials: APIKeyCredentials, **kwargs
    ) -> BlockOutput:
        object_input_data = AIStructuredResponseGeneratorBlock.Input(
            **{attr: getattr(input_data, attr) for attr in input_data.model_fields},
            expected_format={},
        )
        yield "response", self.llm_call(object_input_data, credentials)
        yield "prompt", self.prompt


class SummaryStyle(Enum):
    CONCISE = "concise"
    DETAILED = "detailed"
    BULLET_POINTS = "bullet points"
    NUMBERED_LIST = "numbered list"


class AITextSummarizerBlock(AIBlockBase):
    class Input(BlockSchema):
        text: str = SchemaField(
            description="The text to summarize.",
            placeholder="Enter the text to summarize here...",
        )
        model: LlmModel = SchemaField(
            title="LLM Model",
            default=LlmModel.GPT4_TURBO,
            description="The language model to use for summarizing the text.",
        )
        focus: str = SchemaField(
            title="Focus",
            default="general information",
            description="The topic to focus on in the summary",
        )
        style: SummaryStyle = SchemaField(
            title="Summary Style",
            default=SummaryStyle.CONCISE,
            description="The style of the summary to generate.",
        )
        credentials: AICredentials = AICredentialsField()
        # TODO: Make this dynamic
        max_tokens: int = SchemaField(
            title="Max Tokens",
            default=4096,
            description="The maximum number of tokens to generate in the chat completion.",
            ge=1,
        )
        chunk_overlap: int = SchemaField(
            title="Chunk Overlap",
            default=100,
            description="The number of overlapping tokens between chunks to maintain context.",
            ge=0,
        )
        ollama_host: str = SchemaField(
            advanced=True,
            default="localhost:11434",
            description="Ollama host for local  models",
        )

    class Output(BlockSchema):
        summary: str = SchemaField(description="The final summary of the text.")
        prompt: str = SchemaField(description="The prompt sent to the language model.")
        error: str = SchemaField(description="Error message if the API call failed.")

    def __init__(self):
        super().__init__(
            id="a0a69be1-4528-491c-a85a-a4ab6873e3f0",
            description="Utilize a Large Language Model (LLM) to summarize a long text.",
            categories={BlockCategory.AI, BlockCategory.TEXT},
            input_schema=AITextSummarizerBlock.Input,
            output_schema=AITextSummarizerBlock.Output,
            test_input={
                "text": "Lorem ipsum..." * 100,
                "credentials": TEST_CREDENTIALS_INPUT,
            },
            test_credentials=TEST_CREDENTIALS,
            test_output=[
                ("summary", "Final summary of a long text"),
                ("prompt", str),
            ],
            test_mock={
                "llm_call": lambda input_data, credentials: (
                    {"final_summary": "Final summary of a long text"}
                    if "final_summary" in input_data.expected_format
                    else {"summary": "Summary of a chunk of text"}
                )
            },
        )

    def run(
        self, input_data: Input, *, credentials: APIKeyCredentials, **kwargs
    ) -> BlockOutput:
        for output in self._run(input_data, credentials):
            yield output

    def _run(self, input_data: Input, credentials: APIKeyCredentials) -> BlockOutput:
        chunks = self._split_text(
            input_data.text, input_data.max_tokens, input_data.chunk_overlap
        )
        summaries = []

        for chunk in chunks:
            chunk_summary = self._summarize_chunk(chunk, input_data, credentials)
            summaries.append(chunk_summary)

        final_summary = self._combine_summaries(summaries, input_data, credentials)
        yield "summary", final_summary
        yield "prompt", self.prompt

    @staticmethod
    def _split_text(text: str, max_tokens: int, overlap: int) -> list[str]:
        words = text.split()
        chunks = []
        chunk_size = max_tokens - overlap

        for i in range(0, len(words), chunk_size):
            chunk = " ".join(words[i : i + max_tokens])
            chunks.append(chunk)

        return chunks

    def llm_call(
        self,
        input_data: AIStructuredResponseGeneratorBlock.Input,
        credentials: APIKeyCredentials,
    ) -> dict:
        block = AIStructuredResponseGeneratorBlock()
        response = block.run_once(input_data, "response", credentials=credentials)
        self.merge_llm_stats(block)
        return response

    def _summarize_chunk(
        self, chunk: str, input_data: Input, credentials: APIKeyCredentials
    ) -> str:
        prompt = f"Summarize the following text in a {input_data.style} form. Focus your summary on the topic of `{input_data.focus}` if present, otherwise just provide a general summary:\n\n```{chunk}```"

        llm_response = self.llm_call(
            AIStructuredResponseGeneratorBlock.Input(
                prompt=prompt,
                credentials=input_data.credentials,
                model=input_data.model,
                expected_format={"summary": "The summary of the given text."},
            ),
            credentials=credentials,
        )

        return llm_response["summary"]

    def _combine_summaries(
        self, summaries: list[str], input_data: Input, credentials: APIKeyCredentials
    ) -> str:
        combined_text = "\n\n".join(summaries)

        if len(combined_text.split()) <= input_data.max_tokens:
            prompt = f"Provide a final summary of the following section summaries in a {input_data.style} form, focus your summary on the topic of `{input_data.focus}` if present:\n\n ```{combined_text}```\n\n Just respond with the final_summary in the format specified."

            llm_response = self.llm_call(
                AIStructuredResponseGeneratorBlock.Input(
                    prompt=prompt,
                    credentials=input_data.credentials,
                    model=input_data.model,
                    expected_format={
                        "final_summary": "The final summary of all provided summaries."
                    },
                ),
                credentials=credentials,
            )

            return llm_response["final_summary"]
        else:
            # If combined summaries are still too long, recursively summarize
            return self._run(
                AITextSummarizerBlock.Input(
                    text=combined_text,
                    credentials=input_data.credentials,
                    model=input_data.model,
                    max_tokens=input_data.max_tokens,
                    chunk_overlap=input_data.chunk_overlap,
                ),
                credentials=credentials,
            ).send(None)[
                1
            ]  # Get the first yielded value


class AIConversationBlock(AIBlockBase):
    class Input(BlockSchema):
        messages: List[Message] = SchemaField(
            description="List of messages in the conversation.", min_length=1
        )
        model: LlmModel = SchemaField(
            title="LLM Model",
            default=LlmModel.GPT4_TURBO,
            description="The language model to use for the conversation.",
        )
        credentials: AICredentials = AICredentialsField()
        max_tokens: int | None = SchemaField(
            advanced=True,
            default=None,
            description="The maximum number of tokens to generate in the chat completion.",
        )
        ollama_host: str = SchemaField(
            advanced=True,
            default="localhost:11434",
            description="Ollama host for local  models",
        )

    class Output(BlockSchema):
        response: str = SchemaField(
            description="The model's response to the conversation."
        )
        prompt: str = SchemaField(description="The prompt sent to the language model.")
        error: str = SchemaField(description="Error message if the API call failed.")

    def __init__(self):
        super().__init__(
            id="32a87eab-381e-4dd4-bdb8-4c47151be35a",
            description="Advanced LLM call that takes a list of messages and sends them to the language model.",
            categories={BlockCategory.AI},
            input_schema=AIConversationBlock.Input,
            output_schema=AIConversationBlock.Output,
            test_input={
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "Who won the world series in 2020?"},
                    {
                        "role": "assistant",
                        "content": "The Los Angeles Dodgers won the World Series in 2020.",
                    },
                    {"role": "user", "content": "Where was it played?"},
                ],
                "model": LlmModel.GPT4_TURBO,
                "credentials": TEST_CREDENTIALS_INPUT,
            },
            test_credentials=TEST_CREDENTIALS,
            test_output=[
                (
                    "response",
                    "The 2020 World Series was played at Globe Life Field in Arlington, Texas.",
                ),
                ("prompt", str),
            ],
            test_mock={
                "llm_call": lambda *args, **kwargs: "The 2020 World Series was played at Globe Life Field in Arlington, Texas."
            },
        )

    def llm_call(
        self,
        input_data: AIStructuredResponseGeneratorBlock.Input,
        credentials: APIKeyCredentials,
    ) -> str:
        block = AIStructuredResponseGeneratorBlock()
        response = block.run_once(input_data, "response", credentials=credentials)
        self.merge_llm_stats(block)
        return response["response"]

    def run(
        self, input_data: Input, *, credentials: APIKeyCredentials, **kwargs
    ) -> BlockOutput:
        response = self.llm_call(
            AIStructuredResponseGeneratorBlock.Input(
                prompt="",
                credentials=input_data.credentials,
                model=input_data.model,
                conversation_history=input_data.messages,
                max_tokens=input_data.max_tokens,
                expected_format={},
                ollama_host=input_data.ollama_host,
            ),
            credentials=credentials,
        )

        yield "response", response
        yield "prompt", self.prompt


class AIListGeneratorBlock(AIBlockBase):
    class Input(BlockSchema):
        focus: str | None = SchemaField(
            description="The focus of the list to generate.",
            placeholder="The top 5 most interesting news stories in the data.",
            default=None,
            advanced=False,
        )
        source_data: str | None = SchemaField(
            description="The data to generate the list from.",
            placeholder="News Today: Humans land on Mars: Today humans landed on mars. -- AI wins Nobel Prize: AI wins Nobel Prize for solving world hunger. -- New AI Model: A new AI model has been released.",
            default=None,
            advanced=False,
        )
        model: LlmModel = SchemaField(
            title="LLM Model",
            default=LlmModel.GPT4_TURBO,
            description="The language model to use for generating the list.",
            advanced=True,
        )
        credentials: AICredentials = AICredentialsField()
        max_retries: int = SchemaField(
            default=3,
            description="Maximum number of retries for generating a valid list.",
            ge=1,
            le=5,
        )
        max_tokens: int | None = SchemaField(
            advanced=True,
            default=None,
            description="The maximum number of tokens to generate in the chat completion.",
        )
        ollama_host: str = SchemaField(
            advanced=True,
            default="localhost:11434",
            description="Ollama host for local  models",
        )

    class Output(BlockSchema):
        generated_list: List[str] = SchemaField(description="The generated list.")
        list_item: str = SchemaField(
            description="Each individual item in the list.",
        )
        prompt: str = SchemaField(description="The prompt sent to the language model.")
        error: str = SchemaField(
            description="Error message if the list generation failed."
        )

    def __init__(self):
        super().__init__(
            id="9c0b0450-d199-458b-a731-072189dd6593",
            description="Generate a Python list based on the given prompt using a Large Language Model (LLM).",
            categories={BlockCategory.AI, BlockCategory.TEXT},
            input_schema=AIListGeneratorBlock.Input,
            output_schema=AIListGeneratorBlock.Output,
            test_input={
                "focus": "planets",
                "source_data": (
                    "Zylora Prime is a glowing jungle world with bioluminescent plants, "
                    "while Kharon-9 is a harsh desert planet with underground cities. "
                    "Vortexia's constant storms power floating cities, and Oceara is a water-covered world home to "
                    "intelligent marine life. On icy Draknos, ancient ruins lie buried beneath its frozen landscape, "
                    "drawing explorers to uncover its mysteries. Each planet showcases the limitless possibilities of "
                    "fictional worlds."
                ),
                "model": LlmModel.GPT4_TURBO,
                "credentials": TEST_CREDENTIALS_INPUT,
                "max_retries": 3,
            },
            test_credentials=TEST_CREDENTIALS,
            test_output=[
                (
                    "generated_list",
                    ["Zylora Prime", "Kharon-9", "Vortexia", "Oceara", "Draknos"],
                ),
                ("prompt", str),
                ("list_item", "Zylora Prime"),
                ("list_item", "Kharon-9"),
                ("list_item", "Vortexia"),
                ("list_item", "Oceara"),
                ("list_item", "Draknos"),
            ],
            test_mock={
                "llm_call": lambda input_data, credentials: {
                    "response": "['Zylora Prime', 'Kharon-9', 'Vortexia', 'Oceara', 'Draknos']"
                },
            },
        )

    def llm_call(
        self,
        input_data: AIStructuredResponseGeneratorBlock.Input,
        credentials: APIKeyCredentials,
    ) -> dict[str, str]:
        llm_block = AIStructuredResponseGeneratorBlock()
        response = llm_block.run_once(input_data, "response", credentials=credentials)
        self.merge_llm_stats(llm_block)
        return response

    @staticmethod
    def string_to_list(string):
        """
        Converts a string representation of a list into an actual Python list object.
        """
        logger.debug(f"Converting string to list. Input string: {string}")
        try:
            # Use ast.literal_eval to safely evaluate the string
            python_list = ast.literal_eval(string)
            if isinstance(python_list, list):
                logger.debug(f"Successfully converted string to list: {python_list}")
                return python_list
            else:
                logger.error(f"The provided string '{string}' is not a valid list")
                raise ValueError(f"The provided string '{string}' is not a valid list.")
        except (SyntaxError, ValueError) as e:
            logger.error(f"Failed to convert string to list: {e}")
            raise ValueError("Invalid list format. Could not convert to list.")

    def run(
        self, input_data: Input, *, credentials: APIKeyCredentials, **kwargs
    ) -> BlockOutput:
        logger.debug(f"Starting AIListGeneratorBlock.run with input data: {input_data}")

        # Check for API key
        api_key_check = credentials.api_key.get_secret_value()
        if not api_key_check:
            raise ValueError("No LLM API key provided.")

        # Prepare the system prompt
        sys_prompt = """You are a Python list generator. Your task is to generate a Python list based on the user's prompt. 
            |Respond ONLY with a valid python list. 
            |The list can contain strings, numbers, or nested lists as appropriate. 
            |Do not include any explanations or additional text.

            |Valid Example string formats:

            |Example 1:
            |```
            |['1', '2', '3', '4']
            |```

            |Example 2:
            |```
            |[['1', '2'], ['3', '4'], ['5', '6']]
            |```

            |Example 3:
            |```
            |['1', ['2', '3'], ['4', ['5', '6']]]
            |```

            |Example 4:
            |```
            |['a', 'b', 'c']
            |```

            |Example 5:
            |```
            |['1', '2.5', 'string', 'True', ['False', 'None']]
            |```

            |Do not include any explanations or additional text, just respond with the list in the format specified above.
            """
        # If a focus is provided, add it to the prompt
        if input_data.focus:
            prompt = f"Generate a list with the following focus:\n<focus>\n\n{input_data.focus}</focus>"
        else:
            # If there's source data
            if input_data.source_data:
                prompt = "Extract the main focus of the source data to a list.\ni.e if the source data is a news website, the focus would be the news stories rather than the social links in the footer."
            else:
                # No focus or source data provided, generat a random list
                prompt = "Generate a random list."

        # If the source data is provided, add it to the prompt
        if input_data.source_data:
            prompt += f"\n\nUse the following source data to generate the list from:\n\n<source_data>\n\n{input_data.source_data}</source_data>\n\nDo not invent fictional data that is not present in the source data."
        # Else, tell the LLM to synthesize the data
        else:
            prompt += "\n\nInvent the data to generate the list from."

        for attempt in range(input_data.max_retries):
            try:
                logger.debug("Calling LLM")
                llm_response = self.llm_call(
                    AIStructuredResponseGeneratorBlock.Input(
                        sys_prompt=sys_prompt,
                        prompt=prompt,
                        credentials=input_data.credentials,
                        model=input_data.model,
                        expected_format={},  # Do not use structured response
                        ollama_host=input_data.ollama_host,
                    ),
                    credentials=credentials,
                )

                logger.debug(f"LLM response: {llm_response}")

                # Extract Response string
                response_string = llm_response["response"]
                logger.debug(f"Response string: {response_string}")

                # Convert the string to a Python list
                logger.debug("Converting string to Python list")
                parsed_list = self.string_to_list(response_string)
                logger.debug(f"Parsed list: {parsed_list}")

                # If we reach here, we have a valid Python list
                logger.debug("Successfully generated a valid Python list")
                yield "generated_list", parsed_list
                yield "prompt", self.prompt

                # Yield each item in the list
                for item in parsed_list:
                    yield "list_item", item
                return

            except Exception as e:
                logger.error(f"Error in attempt {attempt + 1}: {str(e)}")
                if attempt == input_data.max_retries - 1:
                    logger.error(
                        f"Failed to generate a valid Python list after {input_data.max_retries} attempts"
                    )
                    raise RuntimeError(
                        f"Failed to generate a valid Python list after {input_data.max_retries} attempts. Last error: {str(e)}"
                    )
                else:
                    # Add a retry prompt
                    logger.debug("Preparing retry prompt")
                    prompt = f"""
                    The previous attempt failed due to `{e}`
                    Generate a valid Python list based on the original prompt.
                    Remember to respond ONLY with a valid Python list as per the format specified earlier.
                    Original prompt: 
                    ```{prompt}```
                    
                    Respond only with the list in the format specified with no commentary or apologies.
                    """
                    logger.debug(f"Retry prompt: {prompt}")

        logger.debug("AIListGeneratorBlock.run completed")
