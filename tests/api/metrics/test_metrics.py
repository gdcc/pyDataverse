"""Tests for the MetricsApi class.

This module contains comprehensive tests for the Dataverse Metrics API functionality,
including tests for retrieving total metrics, historical data, and various breakdowns
by subject, category, and data location.
"""

import pandas as pd

from pyDataverse.api.metrics import MetricsApi

METRICS_TYPES = ["datasets", "dataverses", "files", "downloads"]


class TestMetrics:
    """Test suite for MetricsApi functionality."""

    def test_total_metrics(self, metrics_api: MetricsApi):
        """Test retrieving total metrics for all supported data types.

        This test verifies that the total metrics endpoint returns valid counts
        for datasets, dataverses, files, and downloads.

        Args:
            metrics_api: Initialized MetricsApi instance.
        """
        for type in METRICS_TYPES:
            metrics = metrics_api.total(data_type=type)  # pyright: ignore[reportArgumentType]
            assert metrics.count >= 0, f"Metrics for {type} should be greater than 0"

    def test_past_days_metrics(self, metrics_api: MetricsApi):
        """Test retrieving metrics for the past N days.

        This test verifies that the past days metrics endpoint returns valid counts
        for all supported data types over a 30-day period.

        Args:
            metrics_api: Initialized MetricsApi instance.
        """
        for type in METRICS_TYPES:
            metrics = metrics_api.past_days(data_type=type, days=30)  # pyright: ignore[reportArgumentType]
            assert metrics.count >= 0, f"Metrics for {type} should be greater than 0"

    def test_get_collections_by_subject(self, metrics_api: MetricsApi):
        """Test retrieving collections grouped by subject.

        This test verifies that the collections by subject endpoint returns
        a valid pandas DataFrame containing the breakdown data.

        Args:
            metrics_api: Initialized MetricsApi instance.
        """
        metrics = metrics_api.get_collections_by_subject()
        assert isinstance(metrics, pd.DataFrame), "Metrics should be a DataFrame"

    def test_get_collections_by_category(self, metrics_api: MetricsApi):
        """Test retrieving collections grouped by category.

        This test verifies that the collections by category endpoint returns
        a valid pandas DataFrame containing the breakdown data.

        Args:
            metrics_api: Initialized MetricsApi instance.
        """
        metrics = metrics_api.get_collections_by_category()
        assert isinstance(metrics, pd.DataFrame), "Metrics should be a DataFrame"

    def test_get_datasets_by_subject(self, metrics_api: MetricsApi):
        """Test retrieving datasets grouped by subject.

        This test verifies that the datasets by subject endpoint returns
        a valid pandas DataFrame containing the breakdown data.

        Args:
            metrics_api: Initialized MetricsApi instance.
        """
        metrics = metrics_api.get_datasets_by_subject()
        assert isinstance(metrics, pd.DataFrame), "Metrics should be a DataFrame"

    def test_get_datasets_by_data_location(self, metrics_api: MetricsApi):
        """Test retrieving datasets by data location.

        This test verifies that the datasets by data location endpoint returns
        valid metrics for local datasets (stored on this Dataverse instance).

        Args:
            metrics_api: Initialized MetricsApi instance.
        """
        metrics = metrics_api.get_datasets_by_data_location(data_location="local")

        assert metrics.count >= 0, "Metrics should be greater than 0"
