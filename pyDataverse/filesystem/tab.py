from typing import Literal, Optional

import pandas as pd
from pydantic import BaseModel


class TabSpecs(BaseModel):
    """
    Specifications for parsing tabular data files.

    Defines how to parse different types of tabular files (CSV, TSV, Excel, etc.)
    by specifying the delimiter and file type.

    Attributes:
        delimiter: Character used to separate fields (None for spreadsheet formats)
        tab_type: Type of tabular file - either "spreadsheet" or "text"
    """

    delimiter: Optional[str]
    tab_type: Literal["spreadsheet", "text"]

    def parse(
        self,
        path: str,
        api_token: Optional[str] = None,
        **kwargs,
    ):
        """
        Parse a tabular file into a pandas DataFrame.

        Args:
            path: Path or URL to the file to parse
            api_token: Optional Dataverse API token for authenticated access
            **kwargs: Additional arguments passed to pandas read functions

        Returns:
            pandas.DataFrame: Parsed tabular data

        Raises:
            ValueError: If tab_type is not supported

        Example:
            >>> specs = TabSpecs(delimiter=",", tab_type="text")
            >>> df = specs.parse("https://example.com/data.csv", api_token="token")
        """
        request_headers = {}
        if api_token is not None:
            request_headers["X-Dataverse-key"] = api_token

        if self.tab_type == "spreadsheet":
            return pd.read_excel(
                path,
                storage_options=request_headers,
                **kwargs,
            )
        elif self.tab_type == "text":
            return pd.read_csv(
                path,
                delimiter=self.delimiter,
                storage_options=request_headers,
                **kwargs,
            )
        else:
            raise ValueError(f"Invalid tab type: {self.tab_type}")


TABULAR_MIME_TYPES = {
    """
    Mapping of MIME types to their corresponding TabSpecs.
    
    This dictionary defines how different file formats should be parsed
    based on their MIME type. Supports common tabular formats including
    CSV, TSV, and Excel files.
    
    Keys are MIME type strings, values are TabSpecs instances that define
    the parsing parameters for that format.
    """
    # --- CSV / TSV / Text ---
    "text/csv": TabSpecs(
        delimiter=",",
        tab_type="text",
    ),
    "text/tab-separated-values": TabSpecs(
        delimiter="\t",
        tab_type="text",
    ),
    "text/tsv": TabSpecs(
        delimiter="\t",
        tab_type="text",
    ),
    "text/x-comma-separated-values": TabSpecs(
        delimiter=",",
        tab_type="text",
    ),
    "text/x-tab-separated-values": TabSpecs(
        delimiter="\t",
        tab_type="text",
    ),
    # --- Excel ---
    "application/vnd.ms-excel": TabSpecs(
        delimiter=None,
        tab_type="spreadsheet",
    ),
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": TabSpecs(
        delimiter=None,
        tab_type="spreadsheet",
    ),
}
