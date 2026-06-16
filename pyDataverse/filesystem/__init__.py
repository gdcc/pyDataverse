"""Filesystem interface for Dataverse."""

from fsspec import register_implementation

from .dvfs import DataverseFS
from .reader import DataverseFileReader
from .writer import DataverseFileWriter

# Register the "dataverse://" protocol for source/editable installs; a packaging
# entry point also registers it on install (clobber keeps both idempotent).
register_implementation("dataverse", DataverseFS, clobber=True)

__all__ = [
    "DataverseFS",
    "DataverseFileReader",
    "DataverseFileWriter",
]
