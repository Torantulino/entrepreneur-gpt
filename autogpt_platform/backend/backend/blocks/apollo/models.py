from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel

from backend.data.model import SchemaField


class PrimaryPhone(BaseModel):
    """A primary phone in Apollo"""

    number: str
    source: str
    sanitized_number: str


class SenorityLevels(str, Enum):
    """Seniority levels in Apollo"""

    OWNER = "owner"
    FOUNDER = "founder"
    C_SUITE = "c_suite"
    PARTNER = "partner"
    VP = "vp"
    HEAD = "head"
    DIRECTOR = "director"
    MANAGER = "manager"
    SENIOR = "senior"
    ENTRY = "entry"
    INTERN = "intern"


class ContactEmailStatuses(str, Enum):
    """Contact email statuses in Apollo"""

    VERIFIED = "verified"
    UNVERIFIED = "unverified"
    LIKELY_TO_ENGAGE = "likely_to_engage"
    UNAVAILABLE = "unavailable"


class RuleConfigStatus(BaseModel):
    """A rule config status in Apollo"""

    _id: str
    created_at: str
    rule_action_config_id: str
    rule_config_id: str
    status_cd: str
    updated_at: str
    id: str
    key: str


class ContactCampaignStatus(BaseModel):
    """A contact campaign status in Apollo"""

    id: str
    emailer_campaign_id: str
    send_email_from_user_id: str
    inactive_reason: str
    status: str
    added_at: str
    added_by_user_id: str
    finished_at: str
    paused_at: str
    auto_unpause_at: str
    send_email_from_email_address: str
    send_email_from_email_account_id: str
    manually_set_unpause: str
    failure_reason: str
    current_step_id: str
    in_response_to_emailer_message_id: str
    cc_emails: str
    bcc_emails: str
    to_emails: str


class Account(BaseModel):
    """An account in Apollo"""

    id: str
    name: str
    website_url: str
    blog_url: str
    angellist_url: str
    linkedin_url: str
    twitter_url: str
    facebook_url: str
    primary_phone: PrimaryPhone
    languages: list[str]
    alexa_ranking: int
    phone: str
    linkedin_uid: str
    founded_year: int
    publicly_traded_symbol: str
    publicly_traded_exchange: str
    logo_url: str
    chrunchbase_url: str
    primary_domain: str
    domain: str
    team_id: str
    organization_id: str
    account_stage_id: str
    source: str
    original_source: str
    creator_id: str
    owner_id: str
    created_at: str
    phone_status: str
    hubspot_id: str
    salesforce_id: str
    crm_owner_id: str
    parent_account_id: str
    sanitized_phone: str
    # no listed type on the API docs
    account_playbook_statues: list[Any]
    account_rule_config_statuses: list[RuleConfigStatus]
    existence_level: str
    label_ids: list[str]
    typed_custom_fields: Any
    custom_field_errors: Any
    modality: str
    source_display_name: str
    salesforce_record_id: str
    crm_record_url: str


class ContactEmail(BaseModel):
    """A contact email in Apollo"""

    email: str = ""
    email_md5: str = ""
    email_sha256: str = ""
    email_status: str = ""
    email_source: str = ""
    extrapolated_email_confidence: str = ""
    position: int = 0
    email_from_customer: str = ""
    free_domain: bool = True


class EmploymentHistory(BaseModel):
    """An employment history in Apollo"""

    class Config:
        extra = "allow"
        arbitrary_types_allowed = True
        from_attributes = True
        populate_by_name = True

    _id: Optional[str] = None
    created_at: Optional[str] = None
    current: Optional[bool] = None
    degree: Optional[str] = None
    description: Optional[str] = None
    emails: Optional[str] = None
    end_date: Optional[str] = None
    grade_level: Optional[str] = None
    kind: Optional[str] = None
    major: Optional[str] = None
    organization_id: Optional[str] = None
    organization_name: Optional[str] = None
    raw_address: Optional[str] = None
    start_date: Optional[str] = None
    title: Optional[str] = None
    updated_at: Optional[str] = None
    id: Optional[str] = None
    key: Optional[str] = None


class Breadcrumb(BaseModel):
    """A breadcrumb in Apollo"""

    label: Optional[str] = "N/A"
    signal_field_name: Optional[str] = "N/A"
    value: str | list | None = "N/A"
    display_name: Optional[str] = "N/A"


class TypedCustomField(BaseModel):
    """A typed custom field in Apollo"""

    id: Optional[str] = "N/A"
    value: Optional[str] = "N/A"


class Pagination(BaseModel):
    """Pagination in Apollo"""

    class Config:
        extra = "allow"  # Allow extra fields
        arbitrary_types_allowed = True  # Allow any type
        from_attributes = True  # Allow from_orm
        populate_by_name = True  # Allow field aliases to work both ways

    page: int = 0
    per_page: int = 0
    total_entries: int = 0
    total_pages: int = 0


class DialerFlags(BaseModel):
    """A dialer flags in Apollo"""

    country_name: str
    country_enabled: bool
    high_risk_calling_enabled: bool
    potential_high_risk_number: bool


class PhoneNumber(BaseModel):
    """A phone number in Apollo"""

    raw_number: str = ""
    sanitized_number: str = ""
    type: str = ""
    position: int = 0
    status: str = ""
    dnc_status: str = ""
    dnc_other_info: str = ""
    dailer_flags: DialerFlags = DialerFlags(
        country_name="",
        country_enabled=True,
        high_risk_calling_enabled=True,
        potential_high_risk_number=True,
    )


class Organization(BaseModel):
    """An organization in Apollo"""

    class Config:
        extra = "allow"
        arbitrary_types_allowed = True
        from_attributes = True
        populate_by_name = True

    id: Optional[str] = "N/A"
    name: Optional[str] = "N/A"
    website_url: Optional[str] = "N/A"
    blog_url: Optional[str] = "N/A"
    angellist_url: Optional[str] = "N/A"
    linkedin_url: Optional[str] = "N/A"
    twitter_url: Optional[str] = "N/A"
    facebook_url: Optional[str] = "N/A"
    primary_phone: Optional[PrimaryPhone] = PrimaryPhone(
        number="N/A", source="N/A", sanitized_number="N/A"
    )
    languages: list[str] = []
    alexa_ranking: Optional[int] = 0
    phone: Optional[str] = "N/A"
    linkedin_uid: Optional[str] = "N/A"
    founded_year: Optional[int] = 0
    publicly_traded_symbol: Optional[str] = "N/A"
    publicly_traded_exchange: Optional[str] = "N/A"
    logo_url: Optional[str] = "N/A"
    chrunchbase_url: Optional[str] = "N/A"
    primary_domain: Optional[str] = "N/A"
    sanitized_phone: Optional[str] = "N/A"
    owned_by_organization_id: Optional[str] = "N/A"
    intent_strength: Optional[str] = "N/A"
    show_intent: bool = True
    has_intent_signal_account: Optional[bool] = True
    intent_signal_account: Optional[str] = "N/A"


class Contact(BaseModel):
    """A contact in Apollo"""

    class Config:
        extra = "allow"
        arbitrary_types_allowed = True
        from_attributes = True
        populate_by_name = True

    contact_roles: list[Any] = []
    id: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    name: Optional[str] = None
    linkedin_url: Optional[str] = None
    title: Optional[str] = None
    contact_stage_id: Optional[str] = None
    owner_id: Optional[str] = None
    creator_id: Optional[str] = None
    person_id: Optional[str] = None
    email_needs_tickling: bool = True
    organization_name: Optional[str] = None
    source: Optional[str] = None
    original_source: Optional[str] = None
    organization_id: Optional[str] = None
    headline: Optional[str] = None
    photo_url: Optional[str] = None
    present_raw_address: Optional[str] = None
    linkededin_uid: Optional[str] = None
    extrapolated_email_confidence: Optional[float] = None
    salesforce_id: Optional[str] = None
    salesforce_lead_id: Optional[str] = None
    salesforce_contact_id: Optional[str] = None
    saleforce_account_id: Optional[str] = None
    crm_owner_id: Optional[str] = None
    created_at: Optional[str] = None
    emailer_campaign_ids: list[str] = []
    direct_dial_status: Optional[str] = None
    direct_dial_enrichment_failed_at: Optional[str] = None
    email_status: Optional[str] = None
    email_source: Optional[str] = None
    account_id: Optional[str] = None
    last_activity_date: Optional[str] = None
    hubspot_vid: Optional[str] = None
    hubspot_company_id: Optional[str] = None
    crm_id: Optional[str] = None
    sanitized_phone: Optional[str] = None
    merged_crm_ids: Optional[str] = None
    updated_at: Optional[str] = None
    queued_for_crm_push: bool = True
    suggested_from_rule_engine_config_id: Optional[str] = None
    email_unsubscribed: Optional[str] = None
    label_ids: list[Any] = []
    has_pending_email_arcgate_request: bool = True
    has_email_arcgate_request: bool = True
    existence_level: Optional[str] = None
    email: Optional[str] = None
    email_from_customer: Optional[str] = None
    typed_custom_fields: list[TypedCustomField] = []
    custom_field_errors: Any = None
    salesforce_record_id: Optional[str] = None
    crm_record_url: Optional[str] = None
    email_status_unavailable_reason: Optional[str] = None
    email_true_status: Optional[str] = None
    updated_email_true_status: bool = True
    contact_rule_config_statuses: list[RuleConfigStatus] = []
    source_display_name: Optional[str] = None
    twitter_url: Optional[str] = None
    contact_campaign_statuses: list[ContactCampaignStatus] = []
    state: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    account: Optional[Account] = None
    contact_emails: list[ContactEmail] = []
    organization: Optional[Organization] = None
    employment_history: list[EmploymentHistory] = []
    time_zone: Optional[str] = None
    intent_strength: Optional[str] = None
    show_intent: bool = True
    phone_numbers: list[PhoneNumber] = []
    account_phone_note: Optional[str] = None
    free_domain: bool = True
    is_likely_to_engage: bool = True
    email_domain_catchall: bool = True
    contact_job_change_event: Optional[str] = None


class SearchOrganizationsRequest(BaseModel):
    """Request for Apollo's search organizations API"""

    organization_num_empoloyees_range: list[int] = SchemaField(
        description="""The number range of employees working for the company. This enables you to find companies based on headcount. You can add multiple ranges to expand your search results.

Each range you add needs to be a string, with the upper and lower numbers of the range separated only by a comma.""",
        default=[0, 1000000],
    )

    organization_locations: list[str] = SchemaField(
        description="""The location of the company headquarters. You can search across cities, US states, and countries.

If a company has several office locations, results are still based on the headquarters location. For example, if you search chicago but a company's HQ location is in boston, any Boston-based companies will not appearch in your search results, even if they match other parameters.

To exclude companies based on location, use the organization_not_locations parameter.
""",
        default=[],
    )
    organizations_not_locations: list[str] = SchemaField(
        description="""Exclude companies from search results based on the location of the company headquarters. You can use cities, US states, and countries as locations to exclude.

This parameter is useful for ensuring you do not prospect in an undesirable territory. For example, if you use ireland as a value, no Ireland-based companies will appear in your search results.
""",
        default=[],
    )
    q_organization_keyword_tags: list[str] = SchemaField(
        description="""Filter search results based on keywords associated with companies. For example, you can enter mining as a value to return only companies that have an association with the mining industry."""
    )
    q_organization_name: str = SchemaField(
        description="""Filter search results to include a specific company name.

If the value you enter for this parameter does not match with a company's name, the company will not appear in search results, even if it matches other parameters. Partial matches are accepted. For example, if you filter by the value marketing, a company called NY Marketing Unlimited would still be eligible as a search result, but NY Market Analysis would not be eligible."""
    )
    organization_ids: list[str] = SchemaField(
        description="""The Apollo IDs for the companies you want to include in your search results. Each company in the Apollo database is assigned a unique ID.

To find IDs, identify the values for organization_id when you call this endpoint.""",
        default=[],
    )
    max_results: int = SchemaField(
        description="""The maximum number of results to return. If you don't specify this parameter, the default is 100.""",
        default=100,
        ge=1,
        le=50000,
        advanced=True,
    )

    page: int = SchemaField(
        description="""The page number of the Apollo data that you want to retrieve.

Use this parameter in combination with the per_page parameter to make search results for navigable and improve the performance of the endpoint.""",
        default=1,
    )
    per_page: int = SchemaField(
        description="""The number of search results that should be returned for each page. Limited the number of results per page improves the endpoint's performance.

Use the page parameter to search the different pages of data.""",
        default=100,
    )


class SearchOrganizationsResponse(BaseModel):
    """Response from Apollo's search organizations API"""

    breadcrumbs: list[Breadcrumb] = []
    partial_results_only: bool = True
    has_join: bool = True
    disable_eu_prospecting: bool = True
    partial_results_limit: int = 0
    pagination: Pagination = Pagination(
        page=0, per_page=0, total_entries=0, total_pages=0
    )
    # no listed type on the API docs
    accounts: list[Any] = []
    organizations: list[Organization] = []
    models_ids: list[str] = []
    num_fetch_result: Optional[str] = "N/A"
    derived_params: Optional[str] = "N/A"


class SearchPeopleRequest(BaseModel):
    """Request for Apollo's search people API"""

    person_titles: list[str] = SchemaField(
        description="""Job titles held by the people you want to find. For a person to be included in search results, they only need to match 1 of the job titles you add. Adding more job titles expands your search results.

Results also include job titles with the same terms, even if they are not exact matches. For example, searching for marketing manager might return people with the job title content marketing manager.

Use this parameter in combination with the person_seniorities[] parameter to find people based on specific job functions and seniority levels.
""",
        default=[],
        placeholder="marketing manager",
    )
    person_locations: list[str] = SchemaField(
        description="""The location where people live. You can search across cities, US states, and countries.

To find people based on the headquarters locations of their current employer, use the organization_locations parameter.""",
        default=[],
    )
    person_seniorities: list[SenorityLevels] = SchemaField(
        description="""The job seniority that people hold within their current employer. This enables you to find people that currently hold positions at certain reporting levels, such as Director level or senior IC level.

For a person to be included in search results, they only need to match 1 of the seniorities you add. Adding more seniorities expands your search results.

Searches only return results based on their current job title, so searching for Director-level employees only returns people that currently hold a Director-level title. If someone was previously a Director, but is currently a VP, they would not be included in your search results.

Use this parameter in combination with the person_titles[] parameter to find people based on specific job functions and seniority levels.""",
        default=[],
    )
    organization_locations: list[str] = SchemaField(
        description="""The location of the company headquarters for a person's current employer. You can search across cities, US states, and countries.

If a company has several office locations, results are still based on the headquarters location. For example, if you search chicago but a company's HQ location is in boston, people that work for the Boston-based company will not appear in your results, even if they match other parameters.

To find people based on their personal location, use the person_locations parameter.""",
        default=[],
    )
    q_organization_domains: list[str] = SchemaField(
        description="""The domain name for the person's employer. This can be the current employer or a previous employer. Do not include www., the @ symbol, or similar.

You can add multiple domains to search across companies.

  Examples: apollo.io and microsoft.com""",
        default=[],
    )
    contact_email_statuses: list[ContactEmailStatuses] = SchemaField(
        description="""The email statuses for the people you want to find. You can add multiple statuses to expand your search.""",
        default=[],
    )
    organization_ids: list[str] = SchemaField(
        description="""The Apollo IDs for the companies (employers) you want to include in your search results. Each company in the Apollo database is assigned a unique ID.

To find IDs, call the Organization Search endpoint and identify the values for organization_id.""",
        default=[],
    )
    organization_num_empoloyees_range: list[int] = SchemaField(
        description="""The number range of employees working for the company. This enables you to find companies based on headcount. You can add multiple ranges to expand your search results.

Each range you add needs to be a string, with the upper and lower numbers of the range separated only by a comma.""",
        default=[],
    )
    q_keywords: str = SchemaField(
        description="""A string of words over which we want to filter the results""",
        default="",
    )
    page: int = SchemaField(
        description="""The page number of the Apollo data that you want to retrieve.

Use this parameter in combination with the per_page parameter to make search results for navigable and improve the performance of the endpoint.""",
        default=1,
    )
    per_page: int = SchemaField(
        description="""The number of search results that should be returned for each page. Limited the number of results per page improves the endpoint's performance.

Use the page parameter to search the different pages of data.""",
        default=100,
    )
    max_results: int = SchemaField(
        description="""The maximum number of results to return. If you don't specify this parameter, the default is 100.""",
        default=100,
        ge=1,
        le=50000,
        advanced=True,
    )


class SearchPeopleResponse(BaseModel):
    """Response from Apollo's search people API"""

    class Config:
        extra = "allow"  # Allow extra fields
        arbitrary_types_allowed = True  # Allow any type
        from_attributes = True  # Allow from_orm
        populate_by_name = True  # Allow field aliases to work both ways

    breadcrumbs: list[Breadcrumb] = []
    partial_results_only: bool = True
    has_join: bool = True
    disable_eu_prospecting: bool = True
    partial_results_limit: int = 0
    pagination: Pagination = Pagination(
        page=0, per_page=0, total_entries=0, total_pages=0
    )
    contacts: list[Contact] = []
    people: list[Contact] = []
    model_ids: list[str] = []
    num_fetch_result: Optional[str] = "N/A"
    derived_params: Optional[str] = "N/A"
