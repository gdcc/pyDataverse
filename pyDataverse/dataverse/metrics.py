from __future__ import annotations

import asyncio
from datetime import date
from functools import cached_property
from typing import Any, Dict, Literal, Optional, Union, cast

import pandas as pd
from asyncer import asyncify
from pydantic import BaseModel, Field, model_serializer

from ..api.metrics import MetricsApi

DataType = Literal["dataverses", "datasets", "files", "downloads"]
DataLocation = Literal["local", "remote", "all"]


class Metrics(BaseModel):
    """
    Provides access to Dataverse-level metrics.

    This class fetches and aggregates usage/content metrics from a Dataverse instance using its Metrics API.
    It exposes key metrics and summaries as DataFrames and direct counters, with clear interface and documentation.

    Attributes:
        metrics_api (MetricsApi): The MetricsApi instance used for all metrics API calls.

    Example:
        >>> dv = Dataverse("https://demo.dataverse.org")
        >>> dv.metrics.total("datasets")
        >>> dv.metrics.df  # Summary DataFrame of all core metrics
    """

    metrics_api: MetricsApi = Field(
        ...,
        description="The MetricsApi instance to use for API calls.",
        exclude=True,
        repr=False,
    )
    parent_alias: Optional[str] = Field(
        default=None,
        description="The alias of the parent collection to scope the metrics to.",
    )

    @property
    def collections_by_subject(self) -> pd.DataFrame:
        """
        DataFrame of Dataverse collections grouped by subject.

        Returns:
            pd.DataFrame: Columns: subject, count.
                Rows represent the number of collections per subject.

        Example:
            >>> dv.metrics.collections_by_subject
        """
        return self.metrics_api.get_collections_by_subject(
            parent_alias=self.parent_alias
        )

    @property
    def collections_by_category(self) -> pd.DataFrame:
        """
        DataFrame of collections grouped by category.

        Returns:
            pd.DataFrame: Columns: category, count.
                Shows the number of collections for each category.

        Example:
            >>> dv.metrics.collections_by_category
        """
        return self.metrics_api.get_collections_by_category(
            parent_alias=self.parent_alias
        )

    @model_serializer
    def _serialize_metrics(self) -> Dict[str, Any]:
        """
        Serialize all main metrics for export (e.g., as dict for JSON).

        Returns:
            Dict[str, Any]: Dictionary containing summary metrics, with metric names as keys.
        """
        return asyncio.run(self._serialize_metrics_async())

    async def _serialize_metrics_async(self) -> Dict[str, Any]:
        """Internal async helper to parallelize metric collection."""
        api = self.metrics_api
        data_types = ("dataverses", "datasets", "files", "downloads")
        locations = ("local", "remote", "all")

        # Pre-compute collections to dicts
        tasks = [
            asyncify(api.get_collections_by_subject)(parent_alias=self.parent_alias),
            asyncify(api.get_collections_by_category)(parent_alias=self.parent_alias),
            *[
                asyncify(api.get_datasets_by_data_location)(
                    data_location=loc, parent_alias=self.parent_alias
                )
                for loc in locations
            ],
            *[
                asyncify(api.total)(
                    data_type=cast(DataType, dt), parent_alias=self.parent_alias
                )
                for dt in data_types
            ],
            *[
                asyncify(api.past_days)(
                    data_type=cast(DataType, dt), days=7, parent_alias=self.parent_alias
                )
                for dt in data_types
            ],
        ]

        # Run all tasks in parallel
        results = await asyncio.gather(*tasks)

        # Extract results
        collections_subject, collections_category = results[0], results[1]
        datasets_location = {
            loc: results[2 + i].count for i, loc in enumerate(locations)
        }
        totals = [r.count for r in results[5:9]]
        past_days = [r.count for r in results[9:13]]

        metrics: Dict[str, Any] = {
            "collections_by_subject": collections_subject.to_dict(orient="records"),
            "collections_by_category": collections_category.to_dict(orient="records"),
        }

        for i, data_type in enumerate(data_types):
            metrics[data_type] = {
                "total": totals[i],
                "past_days": past_days[i],
                **({"location": datasets_location} if data_type == "datasets" else {}),
            }

        return metrics

    @cached_property
    def df(self) -> pd.DataFrame:
        """
        DataFrame with a summary of all top-level, site-wide metrics.

        Returns:
            pd.DataFrame: Columns: ['Type', 'Interval', 'Location', 'Count'].
                Includes total and past-7-day counts for dataverses, datasets, files, downloads,
                plus datasets by data location.

        Example:
            >>> dv.metrics.df
        """
        return asyncio.run(self._collect_all_metrics())

    async def _collect_all_metrics(self) -> pd.DataFrame:
        """
        Internal: Collect all top-level metrics in parallel via asyncer.

        Returns:
            pd.DataFrame: Table with columns ['Type', 'Interval', 'Location', 'Count'].
        """
        total_async = asyncify(self.metrics_api.total)
        past_days_async = asyncify(self.metrics_api.past_days)
        location_async = asyncify(self.metrics_api.get_datasets_by_data_location)

        data_types = ["dataverses", "datasets", "files", "downloads"]
        locations = ["local", "remote", "all"]

        tasks = []
        metadata = []
        for dt in data_types:
            tasks.append(
                total_async(
                    data_type=cast(DataType, dt), parent_alias=self.parent_alias
                )
            )  # type: ignore
            metadata.append(("total", dt))
            tasks.append(
                past_days_async(
                    data_type=cast(DataType, dt),
                    days=7,
                    parent_alias=self.parent_alias,
                )
            )  # type: ignore
            metadata.append(("past_days", dt))
        for loc in locations:
            tasks.append(
                location_async(
                    data_location=cast(DataLocation, loc),
                    parent_alias=self.parent_alias,
                )
            )  # type: ignore
            metadata.append(("location", loc))

        results = await asyncio.gather(*tasks)
        rows = []
        for (mtype, loc), result in zip(metadata, results):
            if mtype == "location":
                rows.append(
                    {
                        "Type": "datasets",
                        "Interval": None,
                        "Location": loc,
                        "Count": result.count,
                    }
                )
            else:
                rows.append(
                    {
                        "Type": loc,
                        "Interval": mtype,
                        "Location": None,
                        "Count": result.count,
                    }
                )
        df = pd.DataFrame(rows)
        return df.sort_values("Location").reset_index(drop=True)

    def total(
        self,
        data_type: DataType,
        date_to_month: Optional[Union[str, date]] = None,
    ) -> int:
        """
        Get the total count for a type of entity (e.g., all datasets, files, downloads, dataverses).

        Args:
            data_type: One of 'dataverses', 'datasets', 'files', or 'downloads'.
            date_to_month: Optional (str or date) - If provided, gives the value for a given month ('YYYY-MM' or date object).

        Returns:
            int: Total count for the given type and period.

        Example:
            >>> dv.metrics.total("datasets")
            >>> dv.metrics.total("downloads", "2024-01")  # For a specific month
        """
        return self.metrics_api.total(
            data_type=data_type,
            date_to_month=date_to_month,
            parent_alias=self.parent_alias,
        ).count

    def past_days(
        self,
        data_type: DataType,
        days: Union[int, str],
    ) -> int:
        """
        Number of objects/events for the past number of days.

        Args:
            data_type: Which type ('dataverses', 'datasets', 'files', 'downloads').
            days: Integer or string (e.g., 7, 30) – period to consider.

        Returns:
            int: Count for the given period.

        Example:
            >>> dv.metrics.past_days("datasets", days=30)
        """
        return self.metrics_api.past_days(
            data_type=data_type,
            days=days,
            parent_alias=self.parent_alias,
        ).count

    @cached_property
    def datasets_by_subject(self) -> pd.DataFrame:
        """
        DataFrame of datasets grouped by subject.

        Args:
            date_to_month: Optional (str or date) – for results up to and including a specific month.

        Returns:
            pd.DataFrame: Columns: subject, count.

        Example:
            >>> dv.metrics.datasets_by_subject
        """
        return self.metrics_api.get_datasets_by_subject(
            parent_alias=self.parent_alias,
        )

    def datasets_by_data_location(
        self,
        data_location: DataLocation,
    ) -> int:
        """
        Number of datasets by storage location (local, remote, or all).

        Args:
            data_location: One of 'local', 'remote', or 'all'.

        Returns:
            int: Dataset count for the location.

        Example:
            >>> dv.metrics.datasets_by_data_location("local")
        """
        return self.metrics_api.get_datasets_by_data_location(
            data_location=data_location, parent_alias=self.parent_alias
        ).count

    def dict(self) -> Dict[str, Any]:
        """
        Dictionary of all metrics.
        """
        return asyncio.run(self._serialize_metrics_async())

    def json(self, indent: Optional[int] = 4) -> str:
        """
        JSON string of all metrics.
        """
        return self.model_dump_json(indent=indent)
