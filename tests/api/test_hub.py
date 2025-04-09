import pytest
from pydantic import ValidationError

from pyDataverse.hub.hub import HubApi
from pyDataverse.hub.models import (
    Installation,
    InstallationVersionInfo,
    InstallationsByCountry,
)


class TestHub:
    def test_get_installations(self):
        """Test retrieving all Dataverse installations.

        Verifies that the get_installations() method returns a non-empty list of Installation objects.
        """
        hub = HubApi()
        installations = hub.get_installations()
        assert len(installations) > 0
        assert all(
            isinstance(installation, Installation) for installation in installations
        )

    def test_get_installation_status(self):
        """Test retrieving installation version status information.

        Verifies that get_installation_status() returns a non-empty list of InstallationVersionInfo objects.
        """
        hub = HubApi()
        installation_status = hub.get_installation_status()
        assert len(installation_status) > 0
        assert all(
            isinstance(installation, InstallationVersionInfo)
            for installation in installation_status
        )

    def test_get_installations_by_country(self):
        """Test retrieving installation counts grouped by country.

        Verifies that get_installations_by_country() returns a non-empty list of InstallationsByCountry objects.
        """
        hub = HubApi()
        installations_by_country = hub.get_installations_by_country()
        assert len(installations_by_country) > 0
        assert all(
            isinstance(installation, InstallationsByCountry)
            for installation in installations_by_country
        )

    def test_get_installation_metrics_no_filter(self):
        """Test retrieving installation metrics without any filters.

        Verifies that get_installation_metrics() returns a non-empty list of Installation objects.
        """
        hub = HubApi()
        installation_metrics = hub.get_installation_metrics()
        assert len(installation_metrics) > 0
        assert all(
            isinstance(installation, Installation)
            for installation in installation_metrics
        )

    def test_get_installation_metrics_monthly(self):
        """Test retrieving monthly installation metrics with date filters.

        Verifies that get_installation_metrics_monthly() returns a non-empty list of Installation objects
        when given valid from_date and to_date parameters.
        """
        hub = HubApi()
        installation_metrics = hub.get_installation_metrics_monthly(
            from_date="2020-01", to_date="2020-01"
        )
        assert len(installation_metrics) > 0
        assert all(
            isinstance(installation, Installation)
            for installation in installation_metrics
        )

    def test_filter_future_dates(self):
        """Test that filtering with future dates raises an error.

        Verifies that get_installation_metrics_monthly() raises a ValueError when the to_date
        is set to a future date.
        """
        hub = HubApi()

        with pytest.raises(ValidationError):
            hub.get_installation_metrics_monthly(from_date="2020-01", to_date="2040-01")

    def test_filter_invalid_date_format(self):
        """Test that invalid date formats raise an error.

        Verifies that get_installation_metrics_monthly() raises a ValidationError when dates
        are not in the required YYYY-MM format.
        """
        hub = HubApi()

        with pytest.raises(ValidationError):
            hub.get_installation_metrics_monthly(
                from_date="2020-01-10", to_date="2040-01-20"
            )

    def test_filter_from_is_past_to_date(self):
        """Test that from_date cannot be later than to_date.

        Verifies that get_installation_metrics_monthly() raises a ValueError when from_date
        is chronologically after to_date.
        """
        hub = HubApi()

        with pytest.raises(ValidationError):
            hub.get_installation_metrics_monthly(from_date="2040-01", to_date="2020-01")
