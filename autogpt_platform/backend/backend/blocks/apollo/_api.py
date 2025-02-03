import logging
from typing import List

from backend.blocks.apollo._auth import ApolloCredentials
from backend.blocks.apollo.models import (
    Contact,
    Organization,
    SearchOrganizationsRequest,
    SearchOrganizationsResponse,
    SearchPeopleRequest,
    SearchPeopleResponse,
)
from backend.util.request import Requests

logger = logging.getLogger(name=__name__)


class ApolloClient:
    """Client for the Apollo API"""

    API_URL = "https://api.apollo.io/api/v1"

    def __init__(self, credentials: ApolloCredentials):
        self.credentials = credentials
        self.requests = Requests()

    def _get_headers(self) -> dict[str, str]:
        return {"x-api-key": self.credentials.api_key.get_secret_value()}

    def search_people(self, query: SearchPeopleRequest) -> List[Contact]:
        """Search for people in Apollo"""
        response = self.requests.get(
            f"{self.API_URL}/mixed_people/search",
            headers=self._get_headers(),
            params=query.model_dump(exclude={"credentials", "max_results"}),
        )
        parsed_response = SearchPeopleResponse(**response.json())
        if parsed_response.pagination.total_entries == 0:
            return []

        people = parsed_response.people

        # handle pagination
        if (
            query.max_results is not None
            and query.max_results < parsed_response.pagination.total_entries
            and len(people) < query.max_results
        ):
            while (
                len(people) < query.max_results
                and query.page < parsed_response.pagination.total_pages
                and len(parsed_response.people) > 0
            ):
                query.page += 1
                response = self.requests.get(
                    f"{self.API_URL}/mixed_people/search",
                    headers=self._get_headers(),
                    params=query.model_dump(exclude={"credentials", "max_results"}),
                )
                parsed_response = SearchPeopleResponse(**response.json())
                people.extend(parsed_response.people[: query.max_results - len(people)])

        logger.info(f"Found {len(people)} people")
        return people[: query.max_results] if query.max_results else people

    def search_organizations(
        self, query: SearchOrganizationsRequest
    ) -> List[Organization]:
        """Search for organizations in Apollo"""
        response = self.requests.get(
            f"{self.API_URL}/mixed_companies/search",
            headers=self._get_headers(),
            params=query.model_dump(exclude={"credentials", "max_results"}),
        )
        parsed_response = SearchOrganizationsResponse(**response.json())
        if parsed_response.pagination.total_entries == 0:
            return []

        organizations = parsed_response.organizations

        # handle pagination
        if (
            query.max_results is not None
            and query.max_results < parsed_response.pagination.total_entries
            and len(organizations) < query.max_results
        ):
            while (
                len(organizations) < query.max_results
                and query.page < parsed_response.pagination.total_pages
                and len(parsed_response.organizations) > 0
            ):
                query.page += 1
                response = self.requests.get(
                    f"{self.API_URL}/mixed_companies/search",
                    headers=self._get_headers(),
                    params=query.model_dump(exclude={"credentials", "max_results"}),
                )
                parsed_response = SearchOrganizationsResponse(**response.json())
                organizations.extend(
                    parsed_response.organizations[
                        : query.max_results - len(organizations)
                    ]
                )

        logger.info(f"Found {len(organizations)} organizations")
        return (
            organizations[: query.max_results] if query.max_results else organizations
        )
