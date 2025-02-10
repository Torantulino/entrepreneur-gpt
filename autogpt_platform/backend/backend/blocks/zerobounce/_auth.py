from typing import Literal

from pydantic import SecretStr

from backend.data.model import APIKeyCredentials, CredentialsField, CredentialsMetaInput
from backend.integrations.providers import ProviderName

ZeroBounceCredentials = APIKeyCredentials
ZeroBounceCredentialsInput = CredentialsMetaInput[
    Literal[ProviderName.ZEROBOUNCE],
    Literal["api_key"],
]

TEST_CREDENTIALS = APIKeyCredentials(
    id="01234567-89ab-cdef-0123-456789abcdef",
    provider="zerobounce",
    api_key=SecretStr("mock-zerobounce-api-key"),
    title="Mock ZeroBounce API key",
    expires_at=None,
)
TEST_CREDENTIALS_INPUT = {
    "provider": TEST_CREDENTIALS.provider,
    "id": TEST_CREDENTIALS.id,
    "type": TEST_CREDENTIALS.type,
    "title": TEST_CREDENTIALS.title,
}


def ZeroBounceCredentialsField() -> ZeroBounceCredentialsInput:
    """
    Creates a ZeroBounce credentials input on a block.
    """
    return CredentialsField(
        description="The ZeroBounce integration can be used with an API Key.",
    )
