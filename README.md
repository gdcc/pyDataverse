[![PyPI](https://img.shields.io/pypi/v/pyDataverse.svg)](https://pypi.org/project/pyDataverse/) ![Build Status](https://github.com/gdcc/pyDataverse/actions/workflows/test_build.yml/badge.svg) [![Coverage Status](https://coveralls.io/repos/github/gdcc/pyDataverse/badge.svg)](https://coveralls.io/github/gdcc/pyDataverse) [![Documentation Status](https://readthedocs.org/projects/pydataverse/badge/?version=latest)](https://pydataverse.readthedocs.io/en/latest) ![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pydataverse.svg) [![GitHub](https://img.shields.io/github/license/gdcc/pydataverse.svg)](https://opensource.org/licenses/MIT) [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black) [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.4664557.svg)](https://doi.org/10.5281/zenodo.4664557)

# pyDataverse

[![Project Status: Unsupported – The project has reached a stable, usable state but the author(s) have ceased all work on it. A new maintainer may be desired.](https://www.repostatus.org/badges/latest/active.svg)](https://www.repostatus.org/#active)

pyDataverse is a Python module for [Dataverse](http://dataverse.org).
It helps to access the Dataverse [API's](http://guides.dataverse.org/en/latest/api/index.html) and manipulate, validate, import and export all Dataverse data-types (Dataverse, Dataset, Datafile).

**Find out more: [Read the Docs](https://pydataverse.readthedocs.io/en/latest/)**

## Running the tests

To run pyDataverse's tests locally, you need to install docker and docker-compose. This will spin up a local Dataverse instance and run the tests against it. You can run the tests with:

```bash
sh run_tests.sh
```

By default local tests are using the python `3.11` slim image. However, you can change the python version by providing a valid version via the `-p` keyword argument. For example, to run the tests with python `3.9`:

```bash
sh run_tests.sh -p 3.9
```

## Chat with us!

If you are interested in the development of pyDataverse, we invite you to join us for a chat on our [Zulip Channel](https://dataverse.zulipchat.com/#narrow/stream/377090-python). This is the perfect place to discuss and exchange ideas about the development of pyDataverse. Whether you need help or have ideas to share, feel free to join us!

## PyDataverse Working Group

We have formed a working group to exchange ideas and collaborate on pyDataverse. There is a bi-weekly meeting planned for this purpose, and you are welcome to join us by clicking the following [WebEx meeting link](https://unistuttgart.webex.com/unistuttgart/j.php?MTID=m322473ae7c744792437ce854422e52a3). For a list of all the scheduled dates, please refer to the [Dataverse Community calendar](https://calendar.google.com/calendar/u/1?cid=Y191ZG40dG9ubTQwMWtnampyZTRqbDRqYTBjc0Bncm91cC5jYWxlbmRhci5nb29nbGUuY29t).
