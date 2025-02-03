from backend.blocks.apollo._api import ApolloClient
from backend.blocks.apollo._auth import (
    TEST_CREDENTIALS,
    TEST_CREDENTIALS_INPUT,
    ApolloCredentials,
    ApolloCredentialsInput,
)
from backend.blocks.apollo.models import (
    Organization,
    PrimaryPhone,
    SearchOrganizationsRequest,
)
from backend.data.block import Block, BlockCategory, BlockOutput, BlockSchema
from backend.data.model import SchemaField


class SearchOrganizationsBlock(Block):
    """Search for organizations in Apollo"""

    class Input(BlockSchema):
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
            description="""Filter search results based on keywords associated with companies. For example, you can enter mining as a value to return only companies that have an association with the mining industry.""",
            default=[],
        )
        q_organization_name: str = SchemaField(
            description="""Filter search results to include a specific company name.

If the value you enter for this parameter does not match with a company's name, the company will not appear in search results, even if it matches other parameters. Partial matches are accepted. For example, if you filter by the value marketing, a company called NY Marketing Unlimited would still be eligible as a search result, but NY Market Analysis would not be eligible.""",
            default="",
            advanced=False,
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
        credentials: ApolloCredentialsInput = SchemaField(
            description="Apollo credentials",
        )

    class Output(BlockSchema):
        organizations: list[Organization] = SchemaField(
            description="List of organizations found",
            default=[],
        )
        organization: Organization = SchemaField(
            description="Each found organization, one at a time",
        )
        error: str = SchemaField(
            description="Error message if the search failed",
            default="",
        )

    def __init__(self):
        super().__init__(
            id="3d71270d-599e-4148-9b95-71b35d2f44f0",
            description="Search for organizations in Apollo",
            categories={BlockCategory.SEARCH},
            input_schema=SearchOrganizationsBlock.Input,
            output_schema=SearchOrganizationsBlock.Output,
            test_credentials=TEST_CREDENTIALS,
            test_input={"query": "Google", "credentials": TEST_CREDENTIALS_INPUT},
            test_output=[
                (
                    "organization",
                    Organization(
                        id="1",
                        name="Google",
                        website_url="https://google.com",
                        blog_url="https://google.com/blog",
                        angellist_url="https://angel.co/google",
                        linkedin_url="https://linkedin.com/company/google",
                        twitter_url="https://twitter.com/google",
                        facebook_url="https://facebook.com/google",
                        primary_phone=PrimaryPhone(
                            source="google",
                            number="1234567890",
                            sanitized_number="1234567890",
                        ),
                        languages=["en"],
                        alexa_ranking=1000,
                        phone="1234567890",
                        linkedin_uid="1234567890",
                        founded_year=2000,
                        publicly_traded_symbol="GOOGL",
                        publicly_traded_exchange="NASDAQ",
                        logo_url="https://google.com/logo.png",
                        chrunchbase_url="https://chrunchbase.com/google",
                        primary_domain="google.com",
                        sanitized_phone="1234567890",
                        owned_by_organization_id="1",
                        intent_strength="strong",
                        show_intent=True,
                        has_intent_signal_account=True,
                        intent_signal_account="1",
                    ),
                ),
                (
                    "organizations",
                    [
                        Organization(
                            id="1",
                            name="Google",
                            website_url="https://google.com",
                            blog_url="https://google.com/blog",
                            angellist_url="https://angel.co/google",
                            linkedin_url="https://linkedin.com/company/google",
                            twitter_url="https://twitter.com/google",
                            facebook_url="https://facebook.com/google",
                            primary_phone=PrimaryPhone(
                                source="google",
                                number="1234567890",
                                sanitized_number="1234567890",
                            ),
                            languages=["en"],
                            alexa_ranking=1000,
                            phone="1234567890",
                            linkedin_uid="1234567890",
                            founded_year=2000,
                            publicly_traded_symbol="GOOGL",
                            publicly_traded_exchange="NASDAQ",
                            logo_url="https://google.com/logo.png",
                            chrunchbase_url="https://chrunchbase.com/google",
                            primary_domain="google.com",
                            sanitized_phone="1234567890",
                            owned_by_organization_id="1",
                            intent_strength="strong",
                            show_intent=True,
                            has_intent_signal_account=True,
                            intent_signal_account="1",
                        ),
                    ],
                ),
            ],
            test_mock={
                "search_organizations": lambda *args, **kwargs: [
                    Organization(
                        id="1",
                        name="Google",
                        website_url="https://google.com",
                        blog_url="https://google.com/blog",
                        angellist_url="https://angel.co/google",
                        linkedin_url="https://linkedin.com/company/google",
                        twitter_url="https://twitter.com/google",
                        facebook_url="https://facebook.com/google",
                        primary_phone=PrimaryPhone(
                            source="google",
                            number="1234567890",
                            sanitized_number="1234567890",
                        ),
                        languages=["en"],
                        alexa_ranking=1000,
                        phone="1234567890",
                        linkedin_uid="1234567890",
                        founded_year=2000,
                        publicly_traded_symbol="GOOGL",
                        publicly_traded_exchange="NASDAQ",
                        logo_url="https://google.com/logo.png",
                        chrunchbase_url="https://chrunchbase.com/google",
                        primary_domain="google.com",
                        sanitized_phone="1234567890",
                        owned_by_organization_id="1",
                        intent_strength="strong",
                        show_intent=True,
                        has_intent_signal_account=True,
                        intent_signal_account="1",
                    )
                ]
            },
        )

    @staticmethod
    def search_organizations(
        query: SearchOrganizationsRequest, credentials: ApolloCredentials
    ) -> list[Organization]:
        client = ApolloClient(credentials)
        return client.search_organizations(query)

    def run(
        self, input_data: Input, *, credentials: ApolloCredentials, **kwargs
    ) -> BlockOutput:
        query = SearchOrganizationsRequest(
            **input_data.model_dump(exclude={"credentials"})
        )
        organizations = self.search_organizations(query, credentials)
        for organization in organizations:
            yield "organization", organization
        yield "organizations", organizations
