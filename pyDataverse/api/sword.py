from enum import Enum

from pydantic import ConfigDict, Field, computed_field, field_validator

from .api import Api


class SwordApiVersion(Enum):
    """Enumeration of supported SWORD API versions.

    Attributes:
        V1_1: Version 1.1 of the SWORD API.
    """

    V1_1 = "v1.1"


class SwordApi(Api):
    """Class to access Dataverse's SWORD API.

    Args:
        sword_api_version: SWORD API version. Defaults to 'v1.1'.

    Attributes:
        base_url_api_sword: Description of attribute `base_url_api_sword`.
        base_url: Description of attribute `base_url`.
        native_api_version: Description of attribute `native_api_version`.
        sword_api_version: SWORD API version.
    """

    sword_api_version: SwordApiVersion = Field(
        default=SwordApiVersion.V1_1,
        description="The SWORD API version to use.",
    )

    model_config: ConfigDict = ConfigDict(
        use_enum_values=True,
    )

    @computed_field
    @property
    def api_base_url(self) -> str:
        return self.base_url_api

    @field_validator("sword_api_version")
    @classmethod
    def validate_sword_api_version(cls, v):
        if not isinstance(v, str):
            raise ValueError("sword_api_version {0} is not a string.".format(v))
        return v

    @computed_field(return_type=str)
    def base_url_api_sword(self):
        if self.base_url and self.sword_api_version:
            return "{0}/dvn/api/data-deposit/{1}".format(
                self.base_url, self.sword_api_version.value
            )
        else:
            return self.base_url

    def get_service_document(self):
        url = self._assemble_url("swordv2/service-document")
        return self.get_request(url, auth=True)
