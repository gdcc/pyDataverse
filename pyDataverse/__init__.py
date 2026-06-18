"""Find out more at https://github.com/GDCC/pyDataverse.

Copyright 2019 Stefan Kasberger

Licensed under the MIT License.
"""

from __future__ import absolute_import

import warnings
from importlib.metadata import PackageNotFoundError, version

import nest_asyncio

from .api.search import QueryOptions
from .dataverse import Collection, Dataset, Dataverse, File

# Suppress pkg_resources deprecation warnings from fs package
# These warnings come from a third-party dependency and cannot be fixed
# in this codebase.
warnings.filterwarnings(
    "ignore",
    message=".*pkg_resources.*",
    category=DeprecationWarning,
)


nest_asyncio.apply()

__author__ = "Stefan Kasberger"
__email__ = "stefan.kasberger@univie.ac.at"
__copyright__ = "Copyright (c) 2019 Stefan Kasberger"
__license__ = "MIT License"

__url__ = "https://github.com/GDCC/pyDataverse"
__download_url__ = "https://pypi.python.org/pypi/pyDataverse"
__description__ = "A Python module for Dataverse."

try:
    __version__ = version("pyDataverse")
except PackageNotFoundError:
    raise RuntimeError("pyDataverse is not installed")

__all__ = [
    "Dataset",
    "Dataverse",
    "Collection",
    "File",
    "QueryOptions",
]
