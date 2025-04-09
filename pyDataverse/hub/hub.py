from typing import List, Optional
from pydantic import BaseModel, ConfigDict, TypeAdapter, computed_field
from httpx import Client

from .models import (
    FilterMetrics,
    Installation,
    InstallationVersionInfo,
    InstallationsByCountry,
)

#
# Response models
#
# We are utilizing TypeAdapter to parse the response from the API.
#

# /api/installation
# /api/installation/metrics
# /api/installation/metrics/monthly
installation_response = TypeAdapter(list[Installation])

# /api/installation/status
installation_status_response = TypeAdapter(list[InstallationVersionInfo])

# /api/installation/country
installation_by_country_response = TypeAdapter(list[InstallationsByCountry])


class HubApi(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    base_url: str = "https://hub.dataverse.org/"

    @computed_field
    @property
    def client(self) -> Client:
        return Client(base_url=self.base_url)

    def get_installations(self) -> List[Installation]:
        """Get all installations from the Dataverse Hub.

        Returns:
            List[Installation]: A list of all installations from the Dataverse Hub.
        """

        endpoint = "/api/installation"

        response = self.client.get(endpoint)
        response.raise_for_status()

        return installation_response.validate_python(response.json())

    def get_installation_status(self) -> List[InstallationVersionInfo]:
        """Get the status of all installations from the Dataverse Hub.

        Returns:
            List[InstallationVersionInfo]: A list of all installations from the Dataverse Hub.
        """
        endpoint = "/api/installation/status"

        response = self.client.get(endpoint)
        response.raise_for_status()

        return installation_status_response.validate_python(response.json())

    def get_installations_by_country(self) -> List[InstallationsByCountry]:
        """Get the number of installations by country from the Dataverse Hub.

        Returns:
            List[InstallationsByCountry]: A list of all installations by country from the Dataverse Hub.
        """
        endpoint = "/api/installation/country"

        response = self.client.get(endpoint)
        response.raise_for_status()

        return installation_by_country_response.validate_python(response.json())

    def get_installation_metrics(
        self,
        filter_by: Optional[FilterMetrics] = None,
    ) -> List[Installation]:
        """Get the metrics for all installations from the Dataverse Hub.

        Returns:
            List[FilterMetrics]: A list of all installations from the Dataverse Hub.
        """

        endpoint = "/api/installation/metrics"

        params = {}

        if filter_by:
            params = filter_by.model_dump()

        response = self.client.get(endpoint, params=params)
        response.raise_for_status()

        return installation_response.validate_python(response.json())

    def get_installation_metrics_monthly(
        self,
        from_date: str,
        to_date: str,
        filter_by: Optional[FilterMetrics] = None,
    ) -> List[Installation]:
        """Get the monthly metrics for all installations from the Dataverse Hub."""

        endpoint = "/api/installation/metrics/monthly"

        if not filter_by:
            filter_by = FilterMetrics(
                from_date=from_date,  # type: ignore
                to_date=to_date,  # type: ignore
            )
        else:
            filter_by.from_date = from_date
            filter_by.to_date = to_date

        params = filter_by.model_dump()

        response = self.client.get(endpoint, params=params)
        response.raise_for_status()

        return installation_response.validate_python(response.json())
