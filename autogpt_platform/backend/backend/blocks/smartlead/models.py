from enum import Enum

from pydantic import BaseModel

from backend.data.model import SchemaField


class CreateCampaignResponse(BaseModel):
    ok: bool
    id: int
    name: str
    created_at: str


class CreateCampaignRequest(BaseModel):
    name: str
    client_id: str | None = None


class AddLeadsToCampaignResponse(BaseModel):
    ok: bool
    upload_count: int
    total_leads: int
    block_count: int
    duplicate_count: int
    invalid_email_count: int
    invalid_emails: list[str]
    already_added_to_campaign: int
    unsubscribed_leads: list[str]
    is_lead_limit_exhausted: bool
    lead_import_stopped_count: int
    bounce_count: int
    error: str | None = None


class LeadCustomFields(BaseModel):
    """Custom fields for a lead (max 20 fields)"""

    fields: dict[str, str] = SchemaField(
        description="Custom fields for a lead (max 20 fields)",
        max_length=20,
        default={},
    )


class LeadInput(BaseModel):
    """Single lead input data"""

    first_name: str
    last_name: str
    email: str
    phone_number: str | None = None  # Changed from int to str for phone numbers
    company_name: str | None = None
    website: str | None = None
    location: str | None = None
    custom_fields: LeadCustomFields | None = None
    linkedin_profile: str | None = None
    company_url: str | None = None


class LeadUploadSettings(BaseModel):
    """Settings for lead upload"""

    ignore_global_block_list: bool = SchemaField(
        description="Ignore the global block list",
        default=False,
    )
    ignore_unsubscribe_list: bool = SchemaField(
        description="Ignore the unsubscribe list",
        default=False,
    )
    ignore_community_bounce_list: bool = SchemaField(
        description="Ignore the community bounce list",
        default=False,
    )
    ignore_duplicate_leads_in_other_campaign: bool = SchemaField(
        description="Ignore duplicate leads in other campaigns",
        default=False,
    )


class AddLeadsRequest(BaseModel):
    """Request body for adding leads to a campaign"""

    lead_list: list[LeadInput] = SchemaField(
        description="List of leads to add to the campaign",
        max_length=100,
        default=[],
    )
    settings: LeadUploadSettings
    campaign_id: int


class VariantDistributionType(str, Enum):
    MANUAL_EQUAL = "MANUAL_EQUAL"
    MANUAL_PERCENTAGE = "MANUAL_PERCENTAGE"
    AI_EQUAL = "AI_EQUAL"


class WinningMetricProperty(str, Enum):
    OPEN_RATE = "OPEN_RATE"
    CLICK_RATE = "CLICK_RATE"
    REPLY_RATE = "REPLY_RATE"
    POSITIVE_REPLY_RATE = "POSITIVE_REPLY_RATE"


class SequenceDelayDetails(BaseModel):
    delay_in_days: int


class SequenceVariant(BaseModel):
    subject: str
    email_body: str
    variant_label: str
    id: int | None = None  # Optional for creation, required for updates
    variant_distribution_percentage: int | None = None


class Sequence(BaseModel):
    seq_number: int = SchemaField(
        description="The sequence number",
        default=1,
    )
    seq_delay_details: SequenceDelayDetails
    id: int | None = None
    variant_distribution_type: VariantDistributionType | None = None
    lead_distribution_percentage: int | None = SchemaField(
        None, ge=20, le=100
    )  # >= 20% for fair calculation
    winning_metric_property: WinningMetricProperty | None = None
    seq_variants: list[SequenceVariant] | None = None
    subject: str = ""  # blank makes the follow up in the same thread
    email_body: str | None = None


class SaveSequencesRequest(BaseModel):
    sequences: list[Sequence]


class SaveSequencesResponse(BaseModel):
    ok: bool
    message: str = SchemaField(
        description="Message from the API",
        default="",
    )
    data: dict | str | None = None
    error: str | None = None
