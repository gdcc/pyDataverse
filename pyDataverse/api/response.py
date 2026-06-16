from pydantic import BaseModel, Field
from enum import Enum
from typing import Optional

from typing_extensions import Self


class Status(Enum):
    """Enumeration of API response status values.

    Attributes:
        OK: Indicates a successful API response.
        ERROR: Indicates an error occurred during the API request.
    """

    OK = "OK"
    ERROR = "ERROR"


class APIResponse(BaseModel):
    """Base model for API responses from the Dataverse API.

    This class represents the standard structure of responses returned by
    the Dataverse API, containing status information, data payload, and
    optional error messages.

    Attributes:
        status (Status): The status of the API response (OK or ERROR).
        data (dict): The data payload returned by the API.
        message (Optional[str]): Optional message, typically used for error descriptions.
    """

    status: Status
    data: dict | list = Field(default_factory=dict)
    message: Optional[str] = None

    @classmethod
    def from_out_of_format(cls, data: dict | list, status_code: int) -> Self:
        """Create an APIResponse from a dictionary or list.

        This method is used to create an APIResponse from a dictionary or list.
        """
        return cls(
            status=Status.OK if status_code == 200 else Status.ERROR,
            data=data,
            message=None,
        )
