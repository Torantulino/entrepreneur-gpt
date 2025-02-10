from backend.blocks.smartlead.models import (
    AddLeadsRequest,
    AddLeadsToCampaignResponse,
    CreateCampaignRequest,
    CreateCampaignResponse,
    SaveSequencesRequest,
    SaveSequencesResponse,
)
from backend.util.request import Requests


class SmartLeadClient:
    """Client for the SmartLead API"""

    # This api is stupid and requires your api key in the url. DO NOT RAISE ERRORS FOR BAD REQUESTS.
    # FILTER OUT THE API KEY FROM THE ERROR MESSAGE.

    API_URL = "https://server.smartlead.ai/api/v1"

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.requests = Requests()

    def _add_auth_to_url(self, url: str) -> str:
        return f"{url}?api_key={self.api_key}"

    def _handle_error(self, e: Exception) -> str:
        return e.__str__().replace(self.api_key, "API KEY")

    def create_campaign(self, request: CreateCampaignRequest) -> CreateCampaignResponse:
        try:
            response = self.requests.post(
                self._add_auth_to_url(f"{self.API_URL}/campaigns/create"),
                json=request.model_dump(),
            )
            response_data = response.json()
            return CreateCampaignResponse(**response_data)
        except ValueError as e:
            raise ValueError(f"Invalid response format: {str(e)}")
        except Exception as e:
            raise ValueError(f"Failed to create campaign: {self._handle_error(e)}")

    def add_leads_to_campaign(
        self, request: AddLeadsRequest
    ) -> AddLeadsToCampaignResponse:
        try:
            response = self.requests.post(
                self._add_auth_to_url(
                    f"{self.API_URL}/campaigns/{request.campaign_id}/leads"
                ),
                json=request.model_dump(exclude={"campaign_id"}),
            )
            response_data = response.json()
            response_parsed = AddLeadsToCampaignResponse(**response_data)
            if not response_parsed.ok:
                raise ValueError(
                    f"Failed to add leads to campaign: {response_parsed.error}"
                )
            return response_parsed
        except ValueError as e:
            raise ValueError(f"Invalid response format: {str(e)}")
        except Exception as e:
            raise ValueError(
                f"Failed to add leads to campaign: {self._handle_error(e)}"
            )

    def save_campaign_sequences(
        self, campaign_id: int, request: SaveSequencesRequest
    ) -> SaveSequencesResponse:
        """
        Save sequences within a campaign.

        Args:
            campaign_id: ID of the campaign to save sequences for
            request: SaveSequencesRequest containing the sequences configuration

        Returns:
            SaveSequencesResponse with the result of the operation

        Note:
            For variant_distribution_type:
            - MANUAL_EQUAL: Equally distributes variants across leads
            - AI_EQUAL: Requires winning_metric_property and lead_distribution_percentage
            - MANUAL_PERCENTAGE: Requires variant_distribution_percentage in seq_variants
        """
        try:
            response = self.requests.post(
                self._add_auth_to_url(
                    f"{self.API_URL}/campaigns/{campaign_id}/sequences"
                ),
                json=request.model_dump(exclude_none=True),
            )
            return SaveSequencesResponse(**response.json())
        except Exception as e:
            raise ValueError(
                f"Failed to save campaign sequences: {e.__str__().replace(self.api_key, 'API KEY')}"
            )
