# pyDataverse

A Python wrapper for the Dataverse API. Developed by [Stefan Kasberger](http://stefankasberger.at) for [AUSSDA - The Austrian Social Science Data Archive](http://aussda.at/).


**Features**

* Tests written in [pytest](https://docs.pytest.org/en/latest/) and tested via [Travis CI](URL). Test coverage by [pytest-cov](https://pypi.org/project/pytest-cov/) and [python-coveralls](https://github.com/z4r/python-coveralls), viewable on [coveralls.io](URL).
* auto-generated documentation through functions and class documentation with [sphinx](http://www.sphinx-doc.org/).


**Copyright**

* Code:  [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
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
cd src/pyDataverse/docs/
sphinx-build -b html source build
sphinx-apidoc -f -o source ..
make html
```


## CONTRIBUTE


## COPYRIGHT
