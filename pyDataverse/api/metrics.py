import io
from datetime import date
from typing import Annotated, Literal, Optional, Union

import httpx
import pandas as pd
from deprecation import deprecated
from pydantic import computed_field

from ..models.metrics import MetricsResponse
from .api import Api


class MetricsApi(Api):
    """Class to access Dataverse's Metrics API.

    This class provides methods to retrieve various metrics from a Dataverse instance,
    including total counts, historical data, and breakdowns by subject, category, and location.
    """

    @computed_field(return_type=str)
    def api_base_url(self):
        """Get the base URL for API endpoints.

        Returns:
            str: The base URL for metrics API endpoints.
        """
        return f"{self.base_url_api}/info/metrics/"

    def total(
        self,
        data_type: Annotated[
            Literal["dataverses", "datasets", "files", "downloads"],
            "The data type to filter by.",
        ],
        date_to_month: Annotated[
            Optional[Union[str, date]],
            "Optional date in YYYY-MM format (string) or date object for monthly data up to that month.",
        ] = None,
        parent_alias: Annotated[
            Optional[str],
            "Optional Dataverse collection alias to scope the query to a specific sub-collection.",
        ] = None,
    ) -> MetricsResponse:
        """Get total metrics for a specific data type.

        GET https://$SERVER/api/info/metrics/$type
        GET https://$SERVER/api/info/metrics/$type/toMonth/$YYYY-MM

        Args:
            data_type: Can be set to dataverses, datasets, files or downloads.
            date_to_month: Optional date in YYYY-MM format (string) or date object for monthly data up to that month.
            parent_alias: Optional Dataverse collection alias to scope the query to a specific sub-collection.

        Returns:
            MetricsResponse: Response containing the count for the specified data type.
        """
        url = self._assemble_url(f"{data_type}")
        if date_to_month:
            if isinstance(date_to_month, date):
                date_str = date_to_month.strftime("%Y-%m")
            else:
                date_str = date_to_month
            url += f"/toMonth/{date_str}"
        params = {}
        if parent_alias:
            params["parentAlias"] = parent_alias
        return self.get_request(
            url,
            auth=self.auth,
            params=params if params else None,
            use_async=self.client is not None,
            response_model=MetricsResponse,
        )

    def past_days(
        self,
        data_type: Annotated[
            Literal["dataverses", "datasets", "files", "downloads"],
            "The data type to filter by.",
        ],
        days: Annotated[
            Union[int, str], "Number of days to look back (integer or string)."
        ],
        parent_alias: Annotated[
            Optional[str],
            "Optional Dataverse collection alias to scope the query to a specific sub-collection.",
        ] = None,
    ) -> MetricsResponse:
        """Get metrics for past specified number of days.

        http://guides.dataverse.org/en/4.20/api/metrics.html
        GET https://$SERVER/api/info/metrics/$type/pastDays/$days

        Args:
            data_type: Can be set to dataverses, datasets, files or downloads.
            days: Number of days to look back (integer or string).
            parent_alias: Optional Dataverse collection alias to scope the query to a specific sub-collection.

        Returns:
            MetricsResponse: Response containing the count for the specified data type over the past days.
        """
        url = self._assemble_url(f"{data_type}/pastDays/{days}")
        params = {}
        if parent_alias:
            params["parentAlias"] = parent_alias
        return self.get_request(
            url,
            auth=self.auth,
            params=params if params else None,
            use_async=self.client is not None,
            response_model=MetricsResponse,
        )

    @deprecated(
        deprecated_in="0.4.0",
        removed_in="0.5.0",
        details="Use 'get_collections_by_subject' instead.",
    )
    def get_dataverses_by_subject(
        self,
        parent_alias: Annotated[
            Optional[str],
            "Optional Dataverse collection alias to scope the query to a specific sub-collection.",
        ] = None,
    ) -> pd.DataFrame:
        return self.get_collections_by_subject(parent_alias=parent_alias)

    def get_collections_by_subject(
        self,
        parent_alias: Annotated[
            Optional[str],
            "Optional Dataverse collection alias to scope the query to a specific sub-collection.",
        ] = None,
    ) -> pd.DataFrame:
        """Get dataverses grouped by subject.

        GET https://$SERVER/api/info/metrics/dataverses/bySubject

        Args:
            parent_alias: Optional Dataverse collection alias to scope the query to a specific sub-collection.

        Returns:
            pd.DataFrame: DataFrame containing dataverses grouped by subject with counts.
        """
        url = self._assemble_url("dataverses/bySubject")
        params = {}
        if parent_alias:
            params["parentAlias"] = parent_alias
        tab_data = self.get_request(
            url,
            auth=self.auth,
            params=params if params else None,
            use_async=self.client is not None,
        )
        return pd.read_csv(io.StringIO(tab_data))  # type: ignore

    @deprecated(
        deprecated_in="0.4.0",
        removed_in="0.5.0",
        details="Use 'get_collections_by_category' instead.",
    )
    def get_dataverses_by_category(
        self,
        parent_alias: Annotated[
            Optional[str],
            "Optional Dataverse collection alias to scope the query to a specific sub-collection.",
        ] = None,
    ) -> pd.DataFrame:
        return self.get_collections_by_category(parent_alias=parent_alias)

    def get_collections_by_category(
        self,
        parent_alias: Annotated[
            Optional[str],
            "Optional Dataverse collection alias to scope the query to a specific sub-collection.",
        ] = None,
    ) -> pd.DataFrame:
        """Get dataverses grouped by category.

        GET https://$SERVER/api/info/metrics/dataverses/byCategory

        Args:
            parent_alias: Optional Dataverse collection alias to scope the query to a specific sub-collection.

        Returns:
            pd.DataFrame: DataFrame containing dataverses grouped by category with counts.
        """
        url = self._assemble_url("dataverses/byCategory")
        params = {}
        if parent_alias:
            params["parentAlias"] = parent_alias
        tab_data = self.get_request(
            url,
            auth=self.auth,
            params=params if params else None,
            use_async=self.client is not None,
        )
        return pd.read_csv(io.StringIO(tab_data))  # type: ignore

    def get_datasets_by_subject(
        self,
        parent_alias: Annotated[
            Optional[str],
            "Optional Dataverse collection alias to scope the query to a specific sub-collection.",
        ] = None,
    ) -> pd.DataFrame:
        """Get datasets grouped by subject.

        GET https://$SERVER/api/info/metrics/datasets/bySubject

        Args:
            parent_alias: Optional Dataverse collection alias to scope the query to a specific sub-collection.

        Returns:
            pd.DataFrame: DataFrame containing datasets grouped by subject with counts.
        """
        url = self._assemble_url("datasets/bySubject")

        params = {}

        if parent_alias:
            params["parentAlias"] = parent_alias

        tab_data = self.get_request(
            url,
            auth=self.auth,
            params=params if params else None,
            use_async=self.client is not None,
        )

        if isinstance(tab_data, httpx.Response):
            tab_data = tab_data.json()
            print(tab_data)

        return pd.read_csv(io.StringIO(tab_data))  # type: ignore

    def get_datasets_by_data_location(
        self,
        data_location: Annotated[
            Literal["local", "remote", "all"], "The data location to filter by."
        ],
        parent_alias: Annotated[
            Optional[str],
            "Optional Dataverse collection alias to scope the query to a specific sub-collection.",
        ] = None,
    ) -> MetricsResponse:
        """Get datasets by data location.

        GET https://$SERVER/api/info/metrics/datasets/?dataLocation=$location

        Args:
            data_location: The data location to filter by. Can be 'local' (this instance),
                          'remote' (harvested from other instances), or 'all'.
            parent_alias: Optional Dataverse collection alias to scope the query to a specific sub-collection.

        Returns:
            MetricsResponse: Response containing the count of datasets for the specified location.
        """
        params = {"dataLocation": data_location}
        if parent_alias:
            params["parentAlias"] = parent_alias
        url = self._assemble_url("datasets")
        return self.get_request(
            url,
            auth=self.auth,
            params=params,
            use_async=self.client is not None,
            response_model=MetricsResponse,
        )
