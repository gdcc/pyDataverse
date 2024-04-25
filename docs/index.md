---
hide:
  - navigation
---

# PyDataverse

[![PyPI](https://img.shields.io/pypi/v/pyDataverse.svg)](https://pypi.org/project/pyDataverse/) ![Build Status](https://github.com/gdcc/pyDataverse/actions/workflows/test_build.yml/badge.svg) [![GitHub](https://img.shields.io/github/license/gdcc/pydataverse.svg)](https://opensource.org/licenses/MIT) [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black) [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.4664557.svg)](https://doi.org/10.5281/zenodo.4664557)

PyDataverse is an open source Python module for
[Dataverse](http://dataverse.org). It helps to access the Dataverse [API's](http://guides.dataverse.org/en/latest/api/index.html) and manipulate, validate, import and export all Dataverse data-types (Dataverse, Dataset, Datafile).

No matter, if you want to import huge masses of data into Dataverse,
test your Dataverse instance after deployment or want to make basic API
calls - _PyDataverse helps you with Dataverse!_

## Features

- Comprehensive API wrapper for all Dataverse API's and most of
  their endpoints
- Data models for each of Dataverses data types: Dataverse,
  Dataset and Datafile
- Data conversion to and from Dataverse's own JSON format for API
  uploads
- Easy mass imports and exports through CSV templates
- Utils with helper functions
- Documented examples and functionalities
- Custom exceptions
- Tested ([GitHub Actions](https://github.com/gdcc/pyDataverse/actions/workflows/test_build.yml)) and
  documented ([MKdocs-Material](https://pydataverse.readthedocs.io/))
- Open Source ([MIT](https://opensource.org/licenses/MIT))

## Installation

To install pyDataverse, simply run this command in your terminal of
choice:

```shell
pip install pyDataverse
```

Find more options at `user_installation`{.interpreted-text role="ref"}.

### Requirements

Python packages required:

- [httpx](https://www.python-httpx.org)\>=0.26.0
- [jsonschema](https://github.com/Julian/jsonschema)\>=3.2.0

## Quickstart

!!! warning
    Do not execute the example code on a Dataverse production instance, unless 100% sure!

### Import Dataset metadata JSON

To import the metadata of a Dataset from Dataverse's own JSON format, use `ds.from_json()`. The created `Dataset` can then be retrieved with the `get()` method.

For this example, we use the `dataset.json` from
`tests/data/user-guide/` ([GitHub
repo](https://github.com/gdcc/pyDataverse/tree/master/tests/data/user-guide))
and place it in the root directory.

=== "Python"
    ```python
    from pyDataverse.models import Dataset
    from pyDataverse.utils import read_file

    ds = Dataset()
    ds_filename = "dataset.json"
    ds.from_json(read_file(ds_filename))
    ds.get()
    ```
=== "Output"
    ```python
    {
        'citation_displayName': 'Citation Metadata',
        'title': 'Youth in Austria 2005',
        'author': [
            {
                'authorName': 'LastAuthor1, FirstAuthor1',
                'authorAffiliation': 'AuthorAffiliation1'
            }
        ],
        'datasetContact': [
            {
                'datasetContactEmail': 'ContactEmail1@mailinator.com',
                'datasetContactName': 'LastContact1, FirstContact1'
            }
        ],
        'dsDescription': [
            {
                'dsDescriptionValue': 'DescriptionText'
            }
        ],
        'subject': ['Medicine, Health and Life Sciences']
    }
    ```

### Create Dataset by API

To access Dataverse's Native API, you first have to instantiate `NativeApi`. Then create the Dataset through the API with `create_dataset()`.

This returns, as all API functions do, a `httpx.Response` object, with the DOI inside `data`.

Replace following variables with your own instance data before you execute the lines:

- `BASE_URL`: Base URL of your Dataverse instance, without trailing slash (e. g. `https://data.aussda.at`))
- `API_TOKEN`: API token of a Dataverse user with proper rights to create a Dataset
- `DV_PARENT_ALIAS`: Alias of the Dataverse, the Dataset should be attached to.

=== "Python"
    ```python
    from pyDataverse.api import NativeApi

    api = NativeApi(BASE_URL, API_TOKEN)

    response = api.create_dataset(DV_PARENT_ALIAS, ds.json())
    response.raise_for_status() # Raise an exception if the request was unsuccessful

    print(resp.json())
    ```
=== "Output"
    ```bash
    Dataset with pid 'doi:10.5072/FK2/UTGITX' created.

    {
        'status': 'OK',
        'data': {
            'id': 251,
            'persistentId': 'doi:10.5072/FK2/UTGITX'
        }
    }
    ```

For more tutorials, check out
`User Guide - Basic Usage <user_basic-usage>`{.interpreted-text
role="ref"} and
`User Guide - Advanced Usage <user_advanced-usage>`{.interpreted-text
role="ref"}.

## User Guide

user/installation user/basic-usage user/advanced-usage user/use-cases
user/csv-templates user/faq Wiki
\<<https://github.com/gdcc/pyDataverse/wiki>\> user/resources
:::

## Reference / API

If you are looking for information on a specific class, function, or
method, this part of the documentation is for you.

## Community Guide

This part of the documentation, which is mostly prose, details the
pyDataverse ecosystem and community.

## Contributor Guide

## Thanks!

To everyone who has contributed to pyDataverse - with an idea, an issue,
a pull request, developing used tools, sharing it with others or by any
other means: **Thank you for your support!**

Open Source projects live from the cooperation of the many and
pyDataverse is no exception to that, so to say thank you is the least
that can be done.

Special thanks to Lars Kaczmirek, Veronika Heider, Christian Bischof,
Iris Butzlaff and everyone else from AUSSDA, Slava Tykhonov and Marion
Wittenberg from DANS and all the people who do an amazing job by
developing Dataverse at IQSS, but especially to Phil Durbin for it\'s
support from the first minute.

pyDataverse is funded by [AUSSDA - The Austrian Social Science Data
Archive](https://aussda.at) and through the EU Horizon2020 programme
[SSHOC - Social Sciences & Humanities Open
Cloud](https://www.sshopencloud.eu/about-sshoc) (T5.2).

# License {#homepage_license}

Copyright Stefan Kasberger and others, 2019-2021.

Distributed under the terms of the MIT license, pyDataverse is free and
open source software.

Full License Text:
[LICENSE.txt](https://github.com/GDCC/pyDataverse/blob/master/LICENSE.txt)
