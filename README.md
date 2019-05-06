[![Build Status](https://travis-ci.com/AUSSDA/pyDataverse.svg?branch=master)](https://travis-ci.com/AUSSDA/pyDataverse) [![Coverage Status](https://coveralls.io/repos/github/AUSSDA/pyDataverse/badge.svg?branch=master)](https://coveralls.io/github/AUSSDA/pyDataverse?branch=master)

# pyDataverse

A Python wrapper to work with the Dataverse API. It allows to create, update and remove Dataverses, Datasets and Datafiles via Dataverse's native API. The module is developed by [Stefan Kasberger](http://stefankasberger.at) for [AUSSDA - The Austrian Social Science Data Archive](http://aussda.at/). Thanks to the developers of [dataverse-client-python](https://github.com/IQSS/dataverse-client-python), from which the project got inspired.


**Features**

* Tests written in [pytest](https://docs.pytest.org/en/latest/) and tested via [Travis CI](https://travis-ci.com/AUSSDA/pyDataverse).
* auto-generated documentation through functions and class documentation with [sphinx](http://www.sphinx-doc.org/).


**Copyright**

* Code:  ![GitHub](https://img.shields.io/github/license/aussda/pydataverse.svg)
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
host = 'www.dataverse.org'
auth_token = '' # your Dataverse API authentication token
api = Api(host, auth_token)
```
**Get dataverse**

```python
dv = ''  # dataverse alias or id
resp = api.get_dataverse(dv)
```

**Get dataset**

```python
doi = '' # doi of the dataset
resp = api.get_dataset(doi)
```

**Get datafile**

```python
file_id = '' # file id of the datafile
resp = api.get_datafile(file_id, 'content')
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


## COPYRIGHT
