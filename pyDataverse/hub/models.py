from __future__ import annotations
from typing_extensions import Self


from datetime import datetime
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)
from typing import ClassVar, Dict, List, Optional, Tuple


# These are the base models for the Dataverse Hub API and form
# the basis for responses and requests of the Dataverse Hub API.


class Installation(BaseModel):
    """A Pydantic model representing a Dataverse installation registered with the Hub.

    This model contains metadata about a specific Dataverse installation, including its
    location, contact information, and configuration details.

    Attributes:
        dv_hub_id (str): Unique identifier for the installation in the Dataverse Hub
        name (str): Name of the Dataverse installation
        description (str): Description of the Dataverse installation
        latitude (float): Geographical latitude of the installation location
        longitude (float): Geographical longitude of the installation location
        hostname (str): Hostname where the Dataverse installation is hosted
        country (str): Country where the installation is located
        continent (str): Continent where the installation is located
        launch_year (int): Year when the installation was launched
        gdcc_member (bool): Whether the installation is a GDCC member
        doi_authority (str): DOI authority used by the installation
        contact_email (str): Contact email for the installation
    """

    model_config = ConfigDict(populate_by_name=True)

    dv_hub_id: str = Field(..., alias="dvHubId")
    name: Optional[str] = None
    description: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    hostname: Optional[str] = None
    country: Optional[str] = None
    continent: Optional[str] = None
    launch_year: Optional[int] = Field(None, alias="launchYear")
    gdcc_member: Optional[bool] = Field(None, alias="gdccMember")
    doi_authority: Optional[str] = Field(None, alias="doiAuthority")
    contact_email: Optional[str] = Field(None, alias="contactEmail")
    metrics: List[InstallationMetrics] = Field(default_factory=list)


class InstallationMetrics(BaseModel):
    """A Pydantic model representing metrics for a Dataverse installation.

    This model contains various metrics related to a Dataverse installation, such as
    the number of files, downloads, datasets, and dataverses.

    Attributes:
        installation (Installation): The Dataverse installation associated with these metrics
        record_date (datetime): The date when the metrics were recorded
        files (int): The number of files in the installation
        downloads (int): The number of downloads from the installation
        datasets (int): The total number of datasets in the installation
        harvested_datasets (int): The number of harvested datasets
        local_datasets (int): The number of local datasets
        dataverses (int): The number of dataverses in the installation
    """

    installation: Optional[Installation] = None
    record_date: Optional[str] = Field(None, alias="recordDate")
    files: Optional[int] = None
    downloads: Optional[int] = None
    datasets: Optional[int] = None
    harvested_datasets: Optional[int] = Field(None, alias="harvestedDatasets")
    local_datasets: Optional[int] = Field(None, alias="localDatasets")
    dataverses: Optional[int] = None


class InstallationVersionInfo(BaseModel):
    """A Pydantic model representing the version of a Dataverse installation.

    Attributes:
        record_id (int): Unique identifier for the version record
        installation (Installation): The Dataverse installation associated with this version
        status (str): The status of the installation version
        version (str): The version of the installation
        build (str): The build information of the installation
        record_date (str): The date when the version information was recorded
    """

    record_id: Optional[int] = Field(None, alias="recordId")
    installation: Optional[Installation] = None
    status: Optional[str] = None
    version: Optional[str] = None
    build: Optional[str] = None
    record_date: Optional[str] = Field(None, alias="recordDate")


class InstallationsByCountry(BaseModel):
    """A Pydantic model representing the number of Dataverse installations by country.

    Attributes:
        country (str): The country where the installations are located
        count (int): The number of installations in the country
        record_date (str): The date when the count was recorded
    """

    country: Optional[str] = None
    count: Optional[int] = Field(
        None, alias="count", description="The number of installations in the country"
    )
    record_date: Optional[str] = Field(
        None, alias="recordDate", description="The date when the count was recorded"
    )


class FilterMetrics(BaseModel):
    """A Pydantic model representing the filter metrics for a Dataverse installation.

    Attributes:
        filter_name (str): The name of the filter
        filter_value (str): The value of the filter
        dv_hub_id (str): Dataverse installation id for monthly metrics search
        installation_name (str): Name of the installation for monthly metrics search
        country (str): Country of the installation for monthly metrics search
        continent (str): Continent of the installation for monthly metrics search
        launch_year (int): Year of the installation launch for monthly metrics search
        gdcc_member (bool): GDCC member status of the installation for monthly metrics search
        max_files (int): Maximum number of files in the installation for monthly metrics search
        min_files (int): Minimum number of files in the installation for monthly metrics search
        max_datasets (int): Maximum number of datasets in the installation for monthly metrics search
        min_datasets (int): Minimum number of datasets in the installation for monthly metrics search
        max_dataverses (int): Maximum number of dataverses in the installation for monthly metrics search
        min_dataverses (int): Minimum number of dataverses in the installation for monthly metrics search
        max_harvested (int): Maximum number of harvested datasets in the installation for monthly metrics search
        min_harvested (int): Minimum number of harvested datasets in the installation for monthly metrics search
        min_local_datasets (int): Minimum number of local datasets in the installation for monthly metrics search
        max_local_datasets (int): Maximum number of local datasets in the installation for monthly metrics search
        from_date (str): Specified year and month to begin the search
        to_date (str): Specified year and month to limit the search
    """

    model_config = ConfigDict(populate_by_name=True)

    dv_hub_id: Optional[str] = Field(None, alias="dvHubId")
    installation_name: Optional[str] = Field(None, alias="installationName")
    country: Optional[str] = None
    continent: Optional[str] = None
    launch_year: Optional[int] = Field(None, alias="launchYear")
    gdcc_member: Optional[bool] = Field(None, alias="gdccMember")
    max_files: Optional[int] = Field(None, alias="maxFiles")
    min_files: Optional[int] = Field(None, alias="minFiles")
    max_datasets: Optional[int] = Field(None, alias="maxDatasets")
    min_datasets: Optional[int] = Field(None, alias="minDatasets")
    max_dataverses: Optional[int] = Field(None, alias="maxDataverses")
    min_dataverses: Optional[int] = Field(None, alias="minDataverses")
    max_harvested: Optional[int] = Field(None, alias="maxHarvested")
    min_harvested: Optional[int] = Field(None, alias="minHarvested")
    min_local_datasets: Optional[int] = Field(None, alias="minLocalDatasets")
    max_local_datasets: Optional[int] = Field(None, alias="maxLocalDatasets")
    from_date: Optional[str] = Field(None, alias="fromDate")
    to_date: Optional[str] = Field(None, alias="toDate")

    # Data structure to guide the validation of the min/max fields
    _min_max_fields: ClassVar[Dict[str, Tuple[str, str]]] = {
        "files": ("min_files", "max_files"),
        "datasets": ("min_datasets", "max_datasets"),
        "dataverses": ("min_dataverses", "max_dataverses"),
        "harvested": ("min_harvested", "max_harvested"),
        "local_datasets": ("min_local_datasets", "max_local_datasets"),
    }

    @model_validator(mode="after")
    def validate_fields(self) -> Self:
        """General validator to check multiple fields.

        - min/max values
        - from_date must be before to_date
        """

        if self.from_date and self.to_date:
            from_date = self._parse_date(self.from_date)
            to_date = self._parse_date(self.to_date)
            if from_date > to_date:
                raise ValueError("from_date must be before to_date")

        for min_field, max_field in self._min_max_fields.values():
            min_field = getattr(self, min_field)
            max_field = getattr(self, max_field)

            if min_field is None or max_field is None:
                continue

            if min_field > max_field:
                raise ValueError(f"{min_field} must be less than {max_field}")

        return self

    @field_validator("from_date", "to_date")
    def validate_date(cls, value: Optional[str]) -> Optional[str]:
        """Validate the date format"""
        if value is None:
            return None

        parsed_date = cls._parse_date(value)
        if parsed_date > cls._now():
            raise ValueError("Date cannot be in the future")

        return value

    @staticmethod
    def _now() -> datetime:
        """Helper to get current date in YYYY-MM format for validation"""
        return datetime.now()

    @staticmethod
    def _parse_date(date_str: str) -> datetime:
        """Helper to parse YYYY-MM date string"""
        try:
            return datetime.strptime(date_str, "%Y-%m")
        except ValueError:
            raise ValueError("Dates must be in YYYY-MM format")


# Resolve forward references
models = [
    Installation,
    InstallationMetrics,
    InstallationVersionInfo,
    InstallationsByCountry,
]

for model in models:
    model.model_rebuild()
