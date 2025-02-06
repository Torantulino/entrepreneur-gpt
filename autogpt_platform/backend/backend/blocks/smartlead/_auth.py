from typing import Literal

from pydantic import SecretStr

from backend.data.model import APIKeyCredentials, CredentialsField, CredentialsMetaInput
from backend.integrations.providers import ProviderName

SmartLeadCredentials = APIKeyCredentials
SmartLeadCredentialsInput = CredentialsMetaInput[
    Literal[ProviderName.SMARTLEAD],
    Literal["api_key"],
]

TEST_CREDENTIALS = APIKeyCredentials(
    id="01234567-89ab-cdef-0123-456789abcdef",
    provider="smartlead",
    api_key=SecretStr("mock-smartlead-api-key"),
    title="Mock SmartLead API key",
    expires_at=None,
)
TEST_CREDENTIALS_INPUT = {
    "provider": TEST_CREDENTIALS.provider,
    "id": TEST_CREDENTIALS.id,
    "type": TEST_CREDENTIALS.type,
    "title": TEST_CREDENTIALS.title,
}


def SmartLeadCredentialsField() -> SmartLeadCredentialsInput:
    """
    Creates a SmartLead credentials input on a block.
    """
    return CredentialsField(
        description="The SmartLead integration can be used with an API Key.",
    )
