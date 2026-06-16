from functools import cached_property
from typing import List
from urllib.parse import urljoin

import httpx

from pyDataverse.models.hub import InstallationStatus, InstallationStatusResponse

HUB_BASE_URL = "https://hub.dataverse.org/api"


class DataverseHub:
    """API client for interacting with the Dataverse Hub.

    The Dataverse Hub provides information about Dataverse installations
    worldwide, including their status, versions, and metadata.
    """

    @cached_property
    def installations(self) -> List[InstallationStatus]:
        """Retrieve the status of all Dataverse installations.

        Fetches current status information for all registered Dataverse
        installations from the Hub API, including version information,
        build details, and operational status.

        Returns:
            List[InstallationStatus]: A list of installation status objects
                containing details about each Dataverse installation.

        Raises:
            httpx.HTTPStatusError: If the API request fails with an HTTP error.
            httpx.RequestError: If there's a network or connection error.
            ValidationError: If the response data doesn't match the expected schema.
        """
        url = urljoin(HUB_BASE_URL, "api/installations/status")
        response = httpx.get(url)
        response.raise_for_status()

        content = response.json()
        return InstallationStatusResponse.model_validate(content).root
