[![Build Status](https://travis-ci.com/AUSSDA/pyDataverse.svg?branch=master)](https://travis-ci.com/AUSSDA/pyDataverse) [![Documentation Status](https://readthedocs.org/projects/pydataverse/badge/?version=latest)](https://pydataverse.readthedocs.io/en/latest) [![GitHub](https://img.shields.io/github/license/aussda/pydataverse.svg)](https://opensource.org/licenses/MIT)

# pyDataverse

pyDataverse is a Python module for [Dataverse](http://dataverse.org/). It uses the [Native API](http://guides.dataverse.org/en/latest/api/native-api.html) and [Data Access API](http://guides.dataverse.org/en/latest/api/dataaccess.html). It allows to create, update and remove Dataverses, Datasets and Datafiles via Dataverse's native API. Thanks to the developers of [dataverse-client-python](https://github.com/IQSS/dataverse-client-python), from which the project got inspired from.


**Features**

* Open Source ([MIT](https://opensource.org/licenses/MIT))
* `api.py`: Dataverse Api functionalities to create, get, publish and delete Dataverses, Datasets and Datafiles.
* `utils.py`: Functions to support the core functionalities.
* `exceptions.py`: Custom exceptions
* `tests/*`: Tests on [Travis CI](https://travis-ci.com/AUSSDA/pyDataverse) ([pytest](https://docs.pytest.org/en/latest/) + [tox](http://tox.readthedocs.io/)).
* [Documentation](https://pydataverse.readthedocs.io/en/latest/)
* Python 2 and 3 (>=2.7)


**Copyright**

* Sourcecode:  [![GitHub](https://img.shields.io/github/license/aussda/pydataverse.svg)](https://opensource.org/licenses/MIT)
* Documentation:  [![License: CC BY 4.0](https://licensebuttons.net/l/by/4.0/80x15.png)](https://creativecommons.org/licenses/by/4.0/)

## QUICKSTART

**Requirements**

* curl

**Install**

```shell
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
```

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
identifier = 'doi:10.5072/FK2/U6AEZM'  # doi of the dataset
resp = api.get_dataset(identifier)
```

**Get datafile**

```python
datafile_id = '32'  # file id of the datafile
resp = api.get_datafile(datafile_id)
print(resp.content)
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

We use the [GitHub issue tracker](https://github.com/AUSSDA/pyDataverse/issues) to track bugs and features. Before submitting a bug report or feature request, check to make sure it hasn't already been submitted. When submitting a bug report, please try to provide a screenshot that demonstrates the problem.

## DEVELOPMENT

### Install

```bash
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Testing

[Tox](http://tox.readthedocs.io/) together with [pytest](https://docs.pytest.org/en/latest/) is used für testing.

First, you need to set the needed ENV variables. You can create a `pytest.ini` file with the ENV variables in it:
```ini
[pytest]
env =
    API_TOKEN=**SECRET**
    DATAVERSE_VERSION=4.8.4
    BASE_URL=https://data.aussda.at
    ```

Or define them manually:
```shell
export API_TOKEN=**SECRET**
export DATAVERSE_VERSION=4.8.4
export BASE_URL=https://data.aussda.at
```

To run through all tests (e. g. different python versions, packaging, docs, flake8, etc.), simply call tox from the root directory:
```shell
tox
```

When you only want to run one test, e.g. the py36 test:
```shell
tox -e py36
```

### Documentation

**Create Sphinx Docs**

Use Sphinx to create class and function documentation out of the doc-strings. You can call it via `tox`. This creates the created docs inside `docs/build`.

```
tox -e docs
```

**Create Coverage Reports**

Run tests with coverage to create html and xml reports as an output. Again, call it via `tox`. This creates the created docs inside `docs/coverage_html/`.
```shell
tox -e coverage
```

**Run Coveralls**

To use Coveralls on local development:
```shell
tox -e coveralls
```
