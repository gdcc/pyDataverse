[![Build Status](https://travis-ci.com/AUSSDA/pyDataverse.svg?branch=master)](https://travis-ci.com/AUSSDA/pyDataverse) [![Coverage Status](https://coveralls.io/repos/github/AUSSDA/pyDataverse/badge.svg?branch=master)](https://coveralls.io/github/AUSSDA/pyDataverse?branch=master)

# pyDataverse

A Python module to work with the Dataverse API. It allows to create, update and remove Dataverses, Datasets and Datafiles via Dataverse's native API. Thanks to the developers of [dataverse-client-python](https://github.com/IQSS/dataverse-client-python), from which the project got inspired from.


**Features**

* Python 2 and 3 (>=2.7)
* Open Source (MIT)
* Many different Dataverse Api Requests (use GET, POST (Curl) and DELETE)
* Utils functions to support the core-functions
* Tests with [pytest](https://docs.pytest.org/en/latest/), [Travis CI](https://travis-ci.com/AUSSDA/pyDataverse) and [tox](http://tox.readthedocs.io/).
* Documentation with [sphinx](http://www.sphinx-doc.org/).
* Custom exceptions


**Copyright**

* Code:  [![GitHub](https://img.shields.io/github/license/aussda/pydataverse.svg)](https://opensource.org/licenses/MIT)
* Documentation:  [![License: CC BY 4.0](https://licensebuttons.net/l/by/4.0/80x15.png)](https://creativecommons.org/licenses/by/4.0/)

## INSTALL

```bash
virtualenv --python=/usr/bin/python3 venv
source venv/bin/activate
pip install -r requirements.txt
```

## USE

**Connect to API**

```python
from pyDataverse.api import Api
base_url = 'http://demo.dataverse.org'
api = Api(base_url)
```
**Get dataverse**

```python
dv = 'ecastro'  # dataverse alias or id
resp = api.get_dataverse(dv)
print(resp.json())
```

**Get dataset**

```python
identifier = 'doi:10.5072/FK2/U6AEZM' # doi of the dataset
resp = api.get_dataset(identifier)
```

**Get datafile**

```python
file_id = '32' # file id of the datafile
resp = api.get_datafile(file_id)
resp.content
```

## DEVELOPMENT

### Testing

```
pytest
```

### Documentation

Use Sphinx to create class and function documentation out of the doc-strings.

```
sphinx-build -b html docs/source docs/build/html
sphinx-apidoc -f -o docs/source ..
make html
```

## CONTRIBUTE

In the spirit of free software, everyone is encouraged to help improve this project.

Here are some ways you can contribute:

- by reporting bugs
- by suggesting new features
- by translating to a new language
- by writing or editing documentation
- by writing code (**no pull request is too small**: fix typos in the user interface, add code comments, clean up inconsistent whitespace)
- by refactoring code or adding new features (please get in touch with us before you do, so we can syncronize the efforts and prevent misunderstandings)
- by [closing issues](https://github.com/AUSSDA/pyDataverse/issues)
- by [reviewing pull requests](https://github.com/AUSSDA/pyDataverse/pulls)

When you are ready, submit a [pull request](https://github.com/AUSSDA/pyDataverse).

### Submitting an Issue

We use the [GitHub issue tracker](https://github.com/OKFNat/lobbyscraper/issues) to track bugs and features. Before submitting a bug report or feature request, check to make sure it hasn't already been submitted. When submitting a bug report, please try to provide a screenshot that demonstrates the problem.
