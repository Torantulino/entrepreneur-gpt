from typing import Literal

from pydantic import SecretStr

from backend.data.model import APIKeyCredentials, CredentialsField, CredentialsMetaInput
from backend.integrations.providers import ProviderName

ApolloCredentials = APIKeyCredentials
ApolloCredentialsInput = CredentialsMetaInput[
    Literal[ProviderName.APOLLO],
    Literal["api_key"],
]

TEST_CREDENTIALS = APIKeyCredentials(
    id="01234567-89ab-cdef-0123-456789abcdef",
    provider="apollo",
    api_key=SecretStr("mock-apollo-api-key"),
    title="Mock Apollo API key",
    expires_at=None,
)
TEST_CREDENTIALS_INPUT = {
    "provider": TEST_CREDENTIALS.provider,
    "id": TEST_CREDENTIALS.id,
    "type": TEST_CREDENTIALS.type,
    "title": TEST_CREDENTIALS.title,
}


def ApolloCredentialsField() -> ApolloCredentialsInput:
    """
    Creates a Apollo credentials input on a block.
    """
    return CredentialsField(
        description="The Apollo integration can be used with an API Key.",
    )
