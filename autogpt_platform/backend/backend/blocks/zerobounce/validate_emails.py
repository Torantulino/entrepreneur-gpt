from typing import Optional

from pydantic import BaseModel
from zerobouncesdk.zb_validate_response import (
    ZBValidateResponse,
    ZBValidateStatus,
    ZBValidateSubStatus,
)

from backend.blocks.zerobounce._api import ZeroBounceClient
from backend.blocks.zerobounce._auth import (
    TEST_CREDENTIALS,
    TEST_CREDENTIALS_INPUT,
    ZeroBounceCredentials,
    ZeroBounceCredentialsInput,
)
from backend.data.block import Block, BlockCategory, BlockOutput, BlockSchema
from backend.data.model import SchemaField


class Response(BaseModel):
    address: str = SchemaField(
        description="The email address you are validating.", default="N/A"
    )
    status: ZBValidateStatus = SchemaField(
        description="The status of the email address.", default=ZBValidateStatus.unknown
    )
    sub_status: ZBValidateSubStatus = SchemaField(
        description="The sub-status of the email address.",
        default=ZBValidateSubStatus.none,
    )
    account: Optional[str] = SchemaField(
        description="The portion of the email address before the '@' symbol.",
        default="N/A",
    )
    domain: Optional[str] = SchemaField(
        description="The portion of the email address after the '@' symbol."
    )
    did_you_mean: Optional[str] = SchemaField(
        description="Suggestive Fix for an email typo",
        default=None,
    )
    domain_age_days: Optional[str] = SchemaField(
        description="Age of the email domain in days or [null].",
        default=None,
    )
    free_email: Optional[bool] = SchemaField(
        description="Whether the email address is a free email provider.", default=False
    )
    mx_found: Optional[bool] = SchemaField(
        description="Whether the MX record was found.", default=False
    )
    mx_record: Optional[str] = SchemaField(
        description="The MX record of the email address.", default=None
    )
    smtp_provider: Optional[str] = SchemaField(
        description="The SMTP provider of the email address.", default=None
    )
    firstname: Optional[str] = SchemaField(
        description="The first name of the email address.", default=None
    )
    lastname: Optional[str] = SchemaField(
        description="The last name of the email address.", default=None
    )
    gender: Optional[str] = SchemaField(
        description="The gender of the email address.", default=None
    )
    city: Optional[str] = SchemaField(
        description="The city of the email address.", default=None
    )
    region: Optional[str] = SchemaField(
        description="The region of the email address.", default=None
    )
    zipcode: Optional[str] = SchemaField(
        description="The zipcode of the email address.", default=None
    )
    country: Optional[str] = SchemaField(
        description="The country of the email address.", default=None
    )


class ValidateEmailsBlock(Block):
    """Search for people in Apollo"""

    class Input(BlockSchema):
        email: str = SchemaField(
            description="Email to validate",
        )
        ip_address: str = SchemaField(
            description="IP address to validate",
            default="",
        )
        credentials: ZeroBounceCredentialsInput = SchemaField(
            description="ZeroBounce credentials",
        )

    class Output(BlockSchema):
        response: Response = SchemaField(
            description="Response from ZeroBounce",
        )
        error: str = SchemaField(
            description="Error message if the search failed",
            default="",
        )

    def __init__(self):
        super().__init__(
            id="e3950439-fa0b-40e8-b19f-e0dca0bf5853",
            description="Validate emails",
            categories={BlockCategory.SEARCH},
            input_schema=ValidateEmailsBlock.Input,
            output_schema=ValidateEmailsBlock.Output,
            test_credentials=TEST_CREDENTIALS,
            test_input={
                "credentials": TEST_CREDENTIALS_INPUT,
                "email": "test@test.com",
            },
            test_output=[
                (
                    "response",
                    Response(
                        address="test@test.com",
                        status=ZBValidateStatus.valid,
                        sub_status=ZBValidateSubStatus.allowed,
                        account="test",
                        domain="test.com",
                        did_you_mean=None,
                        domain_age_days=None,
                        free_email=False,
                        mx_found=False,
                        mx_record=None,
                        smtp_provider=None,
                    ),
                )
            ],
            test_mock={
                "validate_email": lambda email, ip_address, credentials: ZBValidateResponse(
                    data={
                        "address": email,
                        "status": ZBValidateStatus.valid,
                        "sub_status": ZBValidateSubStatus.allowed,
                        "account": "test",
                        "domain": "test.com",
                        "did_you_mean": None,
                        "domain_age_days": None,
                        "free_email": False,
                        "mx_found": False,
                        "mx_record": None,
                        "smtp_provider": None,
                    }
                )
            },
        )

    @staticmethod
    def validate_email(
        email: str, ip_address: str, credentials: ZeroBounceCredentials
    ) -> ZBValidateResponse:
        client = ZeroBounceClient(credentials.api_key.get_secret_value())
        return client.validate_email(email, ip_address)

    def run(
        self,
        input_data: Input,
        *,
        credentials: ZeroBounceCredentials,
        **kwargs,
    ) -> BlockOutput:
        response: ZBValidateResponse = self.validate_email(
            input_data.email, input_data.ip_address, credentials
        )

        response_model = Response(**response.__dict__)

        yield "response", response_model
