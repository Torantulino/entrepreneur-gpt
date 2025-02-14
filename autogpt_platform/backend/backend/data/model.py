from __future__ import annotations

import base64
import logging
from datetime import datetime, timezone
from typing import (
    TYPE_CHECKING,
    Annotated,
    Any,
    Callable,
    ClassVar,
    Generic,
    Literal,
    Optional,
    TypedDict,
    TypeVar,
    get_args,
)
from uuid import uuid4

from prisma.enums import CreditTransactionType
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    GetCoreSchemaHandler,
    SecretStr,
    field_serializer,
)
from pydantic_core import (
    CoreSchema,
    PydanticUndefined,
    PydanticUndefinedType,
    ValidationError,
    core_schema,
)

from backend.integrations.providers import ProviderName
from backend.util.settings import Secrets

if TYPE_CHECKING:
    from backend.data.block import BlockSchema

T = TypeVar("T")
logger = logging.getLogger(__name__)


class BlockSecret:
    def __init__(self, key: Optional[str] = None, value: Optional[str] = None):
        if value is not None:
            trimmed_value = value.strip()
            if value != trimmed_value:
                logger.debug(BlockSecret.TRIMMING_VALUE_MSG)
            self._value = trimmed_value
            return

        self._value = self.__get_secret(key)
        if self._value is None:
            raise ValueError(f"Secret {key} not found.")
        trimmed_value = self._value.strip()
        if self._value != trimmed_value:
            logger.debug(BlockSecret.TRIMMING_VALUE_MSG)
        self._value = trimmed_value

    TRIMMING_VALUE_MSG: ClassVar[str] = "Provided secret value got trimmed."
    STR: ClassVar[str] = "<secret>"
    SECRETS: ClassVar[Secrets] = Secrets()

    def __repr__(self):
        return BlockSecret.STR

    def __str__(self):
        return BlockSecret.STR

    @staticmethod
    def __get_secret(key: str | None):
        if not key or not hasattr(BlockSecret.SECRETS, key):
            return None
        return getattr(BlockSecret.SECRETS, key)

    def get_secret_value(self):
        trimmed_value = str(self._value).strip()
        if self._value != trimmed_value:
            logger.info(BlockSecret.TRIMMING_VALUE_MSG)
        return trimmed_value

    @classmethod
    def parse_value(cls, value: Any) -> BlockSecret:
        if isinstance(value, BlockSecret):
            return value
        return BlockSecret(value=value)

    @classmethod
    def __get_pydantic_json_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> dict[str, Any]:
        return {
            "type": "string",
        }

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        validate_fun = core_schema.no_info_plain_validator_function(cls.parse_value)
        return core_schema.json_or_python_schema(
            json_schema=validate_fun,
            python_schema=validate_fun,
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda val: BlockSecret.STR
            ),
        )


def SecretField(
    value: Optional[str] = None,
    key: Optional[str] = None,
    title: Optional[str] = None,
    description: Optional[str] = None,
    placeholder: Optional[str] = None,
    **kwargs,
) -> BlockSecret:
    return SchemaField(
        BlockSecret(key=key, value=value),
        title=title,
        description=description,
        placeholder=placeholder,
        secret=True,
        **kwargs,
    )


def SchemaField(
    default: T | PydanticUndefinedType = PydanticUndefined,
    *args,
    default_factory: Optional[Callable[[], T]] = None,
    title: Optional[str] = None,
    description: Optional[str] = None,
    placeholder: Optional[str] = None,
    advanced: Optional[bool] = None,
    secret: bool = False,
    exclude: bool = False,
    hidden: Optional[bool] = None,
    depends_on: list[str] | None = None,
    image_upload: Optional[bool] = None,
    image_output: Optional[bool] = None,
    **kwargs,
) -> T:
    if default is PydanticUndefined and default_factory is None:
        advanced = False
    elif advanced is None:
        advanced = True

    json_extra = {
        k: v
        for k, v in {
            "placeholder": placeholder,
            "secret": secret,
            "advanced": advanced,
            "hidden": hidden,
            "depends_on": depends_on,
            "image_upload": image_upload,
            "image_output": image_output,
        }.items()
        if v is not None
    }

    return Field(
        default,
        *args,
        default_factory=default_factory,
        title=title,
        description=description,
        exclude=exclude,
        json_schema_extra=json_extra,
        **kwargs,
    )  # type: ignore


class _BaseCredentials(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    provider: str
    title: Optional[str]

    @field_serializer("*")
    def dump_secret_strings(value: Any, _info):
        if isinstance(value, SecretStr):
            return value.get_secret_value()
        return value


class OAuth2Credentials(_BaseCredentials):
    type: Literal["oauth2"] = "oauth2"
    username: Optional[str]
    """Username of the third-party service user that these credentials belong to"""
    access_token: SecretStr
    access_token_expires_at: Optional[int]
    """Unix timestamp (seconds) indicating when the access token expires (if at all)"""
    refresh_token: Optional[SecretStr]
    refresh_token_expires_at: Optional[int]
    """Unix timestamp (seconds) indicating when the refresh token expires (if at all)"""
    scopes: list[str]
    metadata: dict[str, Any] = Field(default_factory=dict)

    def auth_header(self) -> str:
        return f"Bearer {self.access_token.get_secret_value()}"


class APIKeyCredentials(_BaseCredentials):
    type: Literal["api_key"] = "api_key"
    api_key: SecretStr
    expires_at: Optional[int] = Field(
        default=None,
        description="Unix timestamp (seconds) indicating when the API key expires (if at all)",
    )
    """Unix timestamp (seconds) indicating when the API key expires (if at all)"""

    def auth_header(self) -> str:
        return f"Bearer {self.api_key.get_secret_value()}"


class UserPasswordCredentials(_BaseCredentials):
    type: Literal["user_password"] = "user_password"
    username: SecretStr
    password: SecretStr

    def auth_header(self) -> str:
        # Converting the string to bytes using encode()
        # Base64 encoding it with base64.b64encode()
        # Converting the resulting bytes back to a string with decode()
        return f"Basic {base64.b64encode(f'{self.username.get_secret_value()}:{self.password.get_secret_value()}'.encode()).decode()}"


Credentials = Annotated[
    OAuth2Credentials | APIKeyCredentials | UserPasswordCredentials,
    Field(discriminator="type"),
]


CredentialsType = Literal["api_key", "oauth2", "user_password"]


class OAuthState(BaseModel):
    token: str
    provider: str
    expires_at: int
    code_verifier: Optional[str] = None
    """Unix timestamp (seconds) indicating when this OAuth state expires"""
    scopes: list[str]


class UserMetadata(BaseModel):
    integration_credentials: list[Credentials] = Field(default_factory=list)
    integration_oauth_states: list[OAuthState] = Field(default_factory=list)


class UserMetadataRaw(TypedDict, total=False):
    integration_credentials: list[dict]
    integration_oauth_states: list[dict]


class UserIntegrations(BaseModel):
    credentials: list[Credentials] = Field(default_factory=list)
    oauth_states: list[OAuthState] = Field(default_factory=list)


CP = TypeVar("CP", bound=ProviderName)
CT = TypeVar("CT", bound=CredentialsType)


def is_credentials_field_name(field_name: str) -> bool:
    return field_name == "credentials" or field_name.endswith("_credentials")


class CredentialsMetaInput(BaseModel, Generic[CP, CT]):
    id: str
    title: Optional[str] = None
    provider: CP
    type: CT

    @classmethod
    def allowed_providers(cls) -> tuple[ProviderName, ...]:
        return get_args(cls.model_fields["provider"].annotation)

    @classmethod
    def allowed_cred_types(cls) -> tuple[CredentialsType, ...]:
        return get_args(cls.model_fields["type"].annotation)

    @classmethod
    def validate_credentials_field_schema(cls, model: type["BlockSchema"]):
        """Validates the schema of a credentials input field"""
        field_name = next(
            name for name, type in model.get_credentials_fields().items() if type is cls
        )
        field_schema = model.jsonschema()["properties"][field_name]
        try:
            schema_extra = _CredentialsFieldSchemaExtra[CP, CT].model_validate(
                field_schema
            )
        except ValidationError as e:
            if "Field required [type=missing" not in str(e):
                raise

            raise TypeError(
                "Field 'credentials' JSON schema lacks required extra items: "
                f"{field_schema}"
            ) from e

        if len(cls.allowed_providers()) > 1 and not schema_extra.discriminator:
            raise TypeError(
                f"Multi-provider CredentialsField '{field_name}' "
                "requires discriminator!"
            )

    @staticmethod
    def _add_json_schema_extra(schema, cls: CredentialsMetaInput):
        schema["credentials_provider"] = cls.allowed_providers()
        schema["credentials_types"] = cls.allowed_cred_types()

    model_config = ConfigDict(
        json_schema_extra=_add_json_schema_extra,  # type: ignore
    )


class _CredentialsFieldSchemaExtra(BaseModel, Generic[CP, CT]):
    # TODO: move discrimination mechanism out of CredentialsField (frontend + backend)
    credentials_provider: list[CP]
    credentials_scopes: Optional[list[str]] = None
    credentials_types: list[CT]
    discriminator: Optional[str] = None
    discriminator_mapping: Optional[dict[str, CP]] = None


def CredentialsField(
    required_scopes: set[str] = set(),
    *,
    discriminator: Optional[str] = None,
    discriminator_mapping: Optional[dict[str, Any]] = None,
    title: Optional[str] = None,
    description: Optional[str] = None,
    **kwargs,
) -> CredentialsMetaInput:
    """
    `CredentialsField` must and can only be used on fields named `credentials`.
    This is enforced by the `BlockSchema` base class.
    """

    field_schema_extra = {
        k: v
        for k, v in {
            "credentials_scopes": list(required_scopes) or None,
            "discriminator": discriminator,
            "discriminator_mapping": discriminator_mapping,
        }.items()
        if v is not None
    }

    return Field(
        title=title,
        description=description,
        json_schema_extra=field_schema_extra,  # validated on BlockSchema init
        **kwargs,
    )


class ContributorDetails(BaseModel):
    name: str = Field(title="Name", description="The name of the contributor.")


class AutoTopUpConfig(BaseModel):
    amount: int
    """Amount of credits to top up."""
    threshold: int
    """Threshold to trigger auto top up."""


class UserTransaction(BaseModel):
    transaction_key: str = ""
    transaction_time: datetime = datetime.min.replace(tzinfo=timezone.utc)
    transaction_type: CreditTransactionType = CreditTransactionType.USAGE
    amount: int = 0
    balance: int = 0
    description: str | None = None
    usage_graph_id: str | None = None
    usage_execution_id: str | None = None
    usage_node_count: int = 0
    usage_start_time: datetime = datetime.max.replace(tzinfo=timezone.utc)


class TransactionHistory(BaseModel):
    transactions: list[UserTransaction]
    next_transaction_time: datetime | None


class RefundRequest(BaseModel):
    id: str
    user_id: str
    transaction_key: str
    amount: int
    reason: str
    result: str | None = None
    status: str
    created_at: datetime
    updated_at: datetime
