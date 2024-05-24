[![PyPI](https://img.shields.io/pypi/v/pyDataverse.svg)](https://pypi.org/project/pyDataverse/) [![Conda Version](https://img.shields.io/conda/vn/conda-forge/pydataverse.svg)](https://anaconda.org/conda-forge/pydataverse/) ![Build Status](https://github.com/gdcc/pyDataverse/actions/workflows/test_build.yml/badge.svg) [![Coverage Status](https://coveralls.io/repos/github/gdcc/pyDataverse/badge.svg)](https://coveralls.io/github/gdcc/pyDataverse) [![Documentation Status](https://readthedocs.org/projects/pydataverse/badge/?version=latest)](https://pydataverse.readthedocs.io/en/latest) <img src="https://img.shields.io/badge/python-3.8 | 3.9 | 3.10 | 3.11-blue.svg" alt="PyPI - Python Version"> [![GitHub](https://img.shields.io/github/license/gdcc/pydataverse.svg)](https://opensource.org/licenses/MIT) [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black) [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.4664557.svg)](https://doi.org/10.5281/zenodo.4664557)

# pyDataverse

[![Project Status: Unsupported – The project has reached a stable, usable state but the author(s) have ceased all work on it. A new maintainer may be desired.](https://www.repostatus.org/badges/latest/active.svg)](https://www.repostatus.org/#active)

pyDataverse is a Python module for [Dataverse](http://dataverse.org).
It helps to access the Dataverse [API's](http://guides.dataverse.org/en/latest/api/index.html) and manipulate, validate, import and export all Dataverse data-types (Dataverse, Dataset, Datafile).

**Find out more: [Read the Docs](https://pydataverse.readthedocs.io/en/latest/)**

# Running tests

In order to run the tests, you need to have a Dataverse instance running. We have prepared a shell script that will start a Dataverse instance using Docker that runs all tests in a clean environment. To run the tests, execute the following command:

```bash
# Defaults to Python 3.11
./run_tests.sh

# To run the tests with a specific Python version
./run_tests.sh -p 3.8
```

Once finished, you can find the test results in the `dv/unit-tests.log` file and in the terminal.

## Manual setup

If you want to run single tests you need to manually set up the environment and set up the necessary environment variables. Please follow the instructions below.

**1. Start the Dataverse instance**

```bash
docker compose \
    -f ./docker/docker-compose-base.yml \
    --env-file local-test.env \
    up -d
```

**2. Set up the environment variables**

```bash
export BASE_URL=http://localhost:8080
export DV_VERSION=6.2 # or any other version
export $(grep "API_TOKEN" "dv/bootstrap.exposed.env")
export API_TOKEN_SUPERUSER=$API_TOKEN
```

**3. Run the test(s) with pytest**

```bash
python -m pytest -v
```

## Chat with us!

If you are interested in the development of pyDataverse, we invite you to join us for a chat on our [Zulip Channel](https://dataverse.zulipchat.com/#narrow/stream/377090-python). This is the perfect place to discuss and exchange ideas about the development of pyDataverse. Whether you need help or have ideas to share, feel free to join us!

## PyDataverse Working Group

We have formed a [pyDataverse working group](https://py.gdcc.io) to exchange ideas and collaborate on pyDataverse. There is a bi-weekly meeting planned for this purpose, and you are welcome to join us by clicking the following [WebEx meeting link](https://unistuttgart.webex.com/unistuttgart/j.php?MTID=m322473ae7c744792437ce854422e52a3). For a list of all the scheduled dates, please refer to the [Dataverse Community calendar](https://calendar.google.com/calendar/embed?src=c_udn4tonm401kgjjre4jl4ja0cs%40group.calendar.google.com&ctz=America%2FNew_York).
