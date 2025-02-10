import base64
import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING, Optional

from pydantic import SecretStr

if TYPE_CHECKING:
    from backend.executor.database import DatabaseManager

from autogpt_libs.utils.cache import thread_cached
from autogpt_libs.utils.synchronize import RedisKeyedMutex

from backend.data.model import (
    APIKeyCredentials,
    Credentials,
    OAuth2Credentials,
    OAuthState,
    UserIntegrations,
)
from backend.util.settings import Settings

settings = Settings()

# This is an overrride since ollama doesn't actually require an API key, but the creddential system enforces one be attached
ollama_credentials = APIKeyCredentials(
    id="744fdc56-071a-4761-b5a5-0af0ce10a2b5",
    provider="ollama",
    api_key=SecretStr("FAKE_API_KEY"),
    title="Use Credits for Ollama",
    expires_at=None,
)

revid_credentials = APIKeyCredentials(
    id="fdb7f412-f519-48d1-9b5f-d2f73d0e01fe",
    provider="revid",
    api_key=SecretStr(settings.secrets.revid_api_key),
    title="Use Credits for Revid",
    expires_at=None,
)
ideogram_credentials = APIKeyCredentials(
    id="760f84fc-b270-42de-91f6-08efe1b512d0",
    provider="ideogram",
    api_key=SecretStr(settings.secrets.ideogram_api_key),
    title="Use Credits for Ideogram",
    expires_at=None,
)
replicate_credentials = APIKeyCredentials(
    id="6b9fc200-4726-4973-86c9-cd526f5ce5db",
    provider="replicate",
    api_key=SecretStr(settings.secrets.replicate_api_key),
    title="Use Credits for Replicate",
    expires_at=None,
)
openai_credentials = APIKeyCredentials(
    id="53c25cb8-e3ee-465c-a4d1-e75a4c899c2a",
    provider="openai",
    api_key=SecretStr(settings.secrets.openai_api_key),
    title="Use Credits for OpenAI",
    expires_at=None,
)
anthropic_credentials = APIKeyCredentials(
    id="24e5d942-d9e3-4798-8151-90143ee55629",
    provider="anthropic",
    api_key=SecretStr(settings.secrets.anthropic_api_key),
    title="Use Credits for Anthropic",
    expires_at=None,
)
groq_credentials = APIKeyCredentials(
    id="4ec22295-8f97-4dd1-b42b-2c6957a02545",
    provider="groq",
    api_key=SecretStr(settings.secrets.groq_api_key),
    title="Use Credits for Groq",
    expires_at=None,
)
did_credentials = APIKeyCredentials(
    id="7f7b0654-c36b-4565-8fa7-9a52575dfae2",
    provider="d_id",
    api_key=SecretStr(settings.secrets.did_api_key),
    title="Use Credits for D-ID",
    expires_at=None,
)
jina_credentials = APIKeyCredentials(
    id="7f26de70-ba0d-494e-ba76-238e65e7b45f",
    provider="jina",
    api_key=SecretStr(settings.secrets.jina_api_key),
    title="Use Credits for Jina",
    expires_at=None,
)
unreal_credentials = APIKeyCredentials(
    id="66f20754-1b81-48e4-91d0-f4f0dd82145f",
    provider="unreal",
    api_key=SecretStr(settings.secrets.unreal_speech_api_key),
    title="Use Credits for Unreal",
    expires_at=None,
)
open_router_credentials = APIKeyCredentials(
    id="b5a0e27d-0c98-4df3-a4b9-10193e1f3c40",
    provider="open_router",
    api_key=SecretStr(settings.secrets.open_router_api_key),
    title="Use Credits for Open Router",
    expires_at=None,
)
fal_credentials = APIKeyCredentials(
    id="6c0f5bd0-9008-4638-9d79-4b40b631803e",
    provider="fal",
    api_key=SecretStr(settings.secrets.fal_api_key),
    title="Use Credits for FAL",
    expires_at=None,
)
exa_credentials = APIKeyCredentials(
    id="96153e04-9c6c-4486-895f-5bb683b1ecec",
    provider="exa",
    api_key=SecretStr(settings.secrets.exa_api_key),
    title="Use Credits for Exa search",
    expires_at=None,
)
e2b_credentials = APIKeyCredentials(
    id="78d19fd7-4d59-4a16-8277-3ce310acf2b7",
    provider="e2b",
    api_key=SecretStr(settings.secrets.e2b_api_key),
    title="Use Credits for E2B",
    expires_at=None,
)
nvidia_credentials = APIKeyCredentials(
    id="96b83908-2789-4dec-9968-18f0ece4ceb3",
    provider="nvidia",
    api_key=SecretStr(settings.secrets.nvidia_api_key),
    title="Use Credits for Nvidia",
    expires_at=None,
)
screenshotone_credentials = APIKeyCredentials(
    id="3b1bdd16-8818-4bc2-8cbb-b23f9a3439ed",
    provider="screenshotone",
    api_key=SecretStr(settings.secrets.screenshotone_api_key),
    title="Use Credits for ScreenshotOne",
    expires_at=None,
)
mem0_credentials = APIKeyCredentials(
    id="ed55ac19-356e-4243-a6cb-bc599e9b716f",
    provider="mem0",
    api_key=SecretStr(settings.secrets.mem0_api_key),
    title="Use Credits for Mem0",
    expires_at=None,
)

apollo_credentials = APIKeyCredentials(
    id="544c62b5-1d0f-4156-8fb4-9525f11656eb",
    provider="apollo",
    api_key=SecretStr(settings.secrets.apollo_api_key),
    title="Use Credits for Apollo",
    expires_at=None,
)

smartlead_credentials = APIKeyCredentials(
    id="3bcdbda3-84a3-46af-8fdb-bfd2472298b8",
    provider="smartlead",
    api_key=SecretStr(settings.secrets.smartlead_api_key),
    title="Use Credits for SmartLead",
    expires_at=None,
)

zerobounce_credentials = APIKeyCredentials(
    id="63a6e279-2dc2-448e-bf57-85776f7176dc",
    provider="zerobounce",
    api_key=SecretStr(settings.secrets.zerobounce_api_key),
    title="Use Credits for ZeroBounce",
    expires_at=None,
)

DEFAULT_CREDENTIALS = [
    ollama_credentials,
    revid_credentials,
    ideogram_credentials,
    replicate_credentials,
    openai_credentials,
    anthropic_credentials,
    groq_credentials,
    did_credentials,
    jina_credentials,
    unreal_credentials,
    open_router_credentials,
    fal_credentials,
    exa_credentials,
    e2b_credentials,
    mem0_credentials,
    nvidia_credentials,
    screenshotone_credentials,
    apollo_credentials,
    smartlead_credentials,
    zerobounce_credentials,
]


class IntegrationCredentialsStore:
    def __init__(self):
        from backend.data.redis import get_redis

        self.locks = RedisKeyedMutex(get_redis())

    @property
    @thread_cached
    def db_manager(self) -> "DatabaseManager":
        from backend.executor.database import DatabaseManager
        from backend.util.service import get_service_client

        return get_service_client(DatabaseManager)

    def add_creds(self, user_id: str, credentials: Credentials) -> None:
        with self.locked_user_integrations(user_id):
            if self.get_creds_by_id(user_id, credentials.id):
                raise ValueError(
                    f"Can not re-create existing credentials #{credentials.id} "
                    f"for user #{user_id}"
                )
            self._set_user_integration_creds(
                user_id, [*self.get_all_creds(user_id), credentials]
            )

    def get_all_creds(self, user_id: str) -> list[Credentials]:
        users_credentials = self._get_user_integrations(user_id).credentials
        all_credentials = users_credentials
        # These will always be added
        all_credentials.append(ollama_credentials)

        # These will only be added if the API key is set
        if settings.secrets.revid_api_key:
            all_credentials.append(revid_credentials)
        if settings.secrets.ideogram_api_key:
            all_credentials.append(ideogram_credentials)
        if settings.secrets.groq_api_key:
            all_credentials.append(groq_credentials)
        if settings.secrets.replicate_api_key:
            all_credentials.append(replicate_credentials)
        if settings.secrets.openai_api_key:
            all_credentials.append(openai_credentials)
        if settings.secrets.anthropic_api_key:
            all_credentials.append(anthropic_credentials)
        if settings.secrets.did_api_key:
            all_credentials.append(did_credentials)
        if settings.secrets.jina_api_key:
            all_credentials.append(jina_credentials)
        if settings.secrets.unreal_speech_api_key:
            all_credentials.append(unreal_credentials)
        if settings.secrets.open_router_api_key:
            all_credentials.append(open_router_credentials)
        if settings.secrets.fal_api_key:
            all_credentials.append(fal_credentials)
        if settings.secrets.exa_api_key:
            all_credentials.append(exa_credentials)
        if settings.secrets.e2b_api_key:
            all_credentials.append(e2b_credentials)
        if settings.secrets.nvidia_api_key:
            all_credentials.append(nvidia_credentials)
        if settings.secrets.screenshotone_api_key:
            all_credentials.append(screenshotone_credentials)
        if settings.secrets.mem0_api_key:
            all_credentials.append(mem0_credentials)
        if settings.secrets.apollo_api_key:
            all_credentials.append(apollo_credentials)
        if settings.secrets.smartlead_api_key:
            all_credentials.append(smartlead_credentials)
        if settings.secrets.zerobounce_api_key:
            all_credentials.append(zerobounce_credentials)
        return all_credentials

    def get_creds_by_id(self, user_id: str, credentials_id: str) -> Credentials | None:
        all_credentials = self.get_all_creds(user_id)
        return next((c for c in all_credentials if c.id == credentials_id), None)

    def get_creds_by_provider(self, user_id: str, provider: str) -> list[Credentials]:
        credentials = self.get_all_creds(user_id)
        return [c for c in credentials if c.provider == provider]

    def get_authorized_providers(self, user_id: str) -> list[str]:
        credentials = self.get_all_creds(user_id)
        return list(set(c.provider for c in credentials))

    def update_creds(self, user_id: str, updated: Credentials) -> None:
        with self.locked_user_integrations(user_id):
            current = self.get_creds_by_id(user_id, updated.id)
            if not current:
                raise ValueError(
                    f"Credentials with ID {updated.id} "
                    f"for user with ID {user_id} not found"
                )
            if type(current) is not type(updated):
                raise TypeError(
                    f"Can not update credentials with ID {updated.id} "
                    f"from type {type(current)} "
                    f"to type {type(updated)}"
                )

            # Ensure no scopes are removed when updating credentials
            if (
                isinstance(updated, OAuth2Credentials)
                and isinstance(current, OAuth2Credentials)
                and not set(updated.scopes).issuperset(current.scopes)
            ):
                raise ValueError(
                    f"Can not update credentials with ID {updated.id} "
                    f"and scopes {current.scopes} "
                    f"to more restrictive set of scopes {updated.scopes}"
                )

            # Update the credentials
            updated_credentials_list = [
                updated if c.id == updated.id else c
                for c in self.get_all_creds(user_id)
            ]
            self._set_user_integration_creds(user_id, updated_credentials_list)

    def delete_creds_by_id(self, user_id: str, credentials_id: str) -> None:
        with self.locked_user_integrations(user_id):
            filtered_credentials = [
                c for c in self.get_all_creds(user_id) if c.id != credentials_id
            ]
            self._set_user_integration_creds(user_id, filtered_credentials)

    def store_state_token(
        self, user_id: str, provider: str, scopes: list[str], use_pkce: bool = False
    ) -> tuple[str, str]:
        token = secrets.token_urlsafe(32)
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)

        (code_challenge, code_verifier) = self._generate_code_challenge()

        state = OAuthState(
            token=token,
            provider=provider,
            code_verifier=code_verifier,
            expires_at=int(expires_at.timestamp()),
            scopes=scopes,
        )

        with self.locked_user_integrations(user_id):

            user_integrations = self._get_user_integrations(user_id)
            oauth_states = user_integrations.oauth_states
            oauth_states.append(state)
            user_integrations.oauth_states = oauth_states

            self.db_manager.update_user_integrations(
                user_id=user_id, data=user_integrations
            )

        return token, code_challenge

    def _generate_code_challenge(self) -> tuple[str, str]:
        """
        Generate code challenge using SHA256 from the code verifier.
        Currently only SHA256 is supported.(In future if we want to support more methods we can add them here)
        """
        code_verifier = secrets.token_urlsafe(128)
        sha256_hash = hashlib.sha256(code_verifier.encode("utf-8")).digest()
        code_challenge = base64.urlsafe_b64encode(sha256_hash).decode("utf-8")
        return code_challenge.replace("=", ""), code_verifier

    def verify_state_token(
        self, user_id: str, token: str, provider: str
    ) -> Optional[OAuthState]:
        with self.locked_user_integrations(user_id):
            user_integrations = self._get_user_integrations(user_id)
            oauth_states = user_integrations.oauth_states

            now = datetime.now(timezone.utc)
            valid_state = next(
                (
                    state
                    for state in oauth_states
                    if state.token == token
                    and state.provider == provider
                    and state.expires_at > now.timestamp()
                ),
                None,
            )

            if valid_state:
                # Remove the used state
                oauth_states.remove(valid_state)
                user_integrations.oauth_states = oauth_states
                self.db_manager.update_user_integrations(user_id, user_integrations)
                return valid_state

        return None

    def _set_user_integration_creds(
        self, user_id: str, credentials: list[Credentials]
    ) -> None:
        integrations = self._get_user_integrations(user_id)
        # Remove default credentials from the list
        credentials = [c for c in credentials if c not in DEFAULT_CREDENTIALS]
        integrations.credentials = credentials
        self.db_manager.update_user_integrations(user_id, integrations)

    def _get_user_integrations(self, user_id: str) -> UserIntegrations:
        integrations: UserIntegrations = self.db_manager.get_user_integrations(
            user_id=user_id
        )
        return integrations

    def locked_user_integrations(self, user_id: str):
        key = (f"user:{user_id}", "integrations")
        return self.locks.locked(key)
