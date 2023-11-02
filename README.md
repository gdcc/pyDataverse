[![PyPI](https://img.shields.io/pypi/v/pyDataverse.svg)](https://pypi.org/project/pyDataverse/) [![Build Status](https://travis-ci.com/gdcc/pyDataverse.svg?branch=master)](https://travis-ci.com/gdcc/pyDataverse) [![Coverage Status](https://coveralls.io/repos/github/gdcc/pyDataverse/badge.svg)](https://coveralls.io/github/gdcc/pyDataverse) [![Documentation Status](https://readthedocs.org/projects/pydataverse/badge/?version=latest)](https://pydataverse.readthedocs.io/en/latest) ![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pydataverse.svg) [![GitHub](https://img.shields.io/github/license/gdcc/pydataverse.svg)](https://opensource.org/licenses/MIT) [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black) [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.4664557.svg)](https://doi.org/10.5281/zenodo.4664557)

# pyDataverse

[![Project Status: Unsupported – The project has reached a stable, usable state but the author(s) have ceased all work on it. A new maintainer may be desired.](https://www.repostatus.org/badges/latest/unsupported.svg)](https://www.repostatus.org/#unsupported)

pyDataverse is a Python module for [Dataverse](http://dataverse.org).
It helps to access the Dataverse [API's](http://guides.dataverse.org/en/latest/api/index.html) and manipulate, validate, import and export all Dataverse data-types (Dataverse, Dataset, Datafile).

**Find out more: [pyDataverse Documentation](https://pydataverse.readthedocs.io/en/latest/)**

-----

/api/admin endpoints:
- [ ] .../settings
- [ ] .../settings/$name
- [ ] .../bannerMessage
- [ ] .../authenticationProviderFactories
- [ ] .../authenticationProviders
- [ ] .../authenticationProviders/$id/
- [ ] .../authenticationProviders/$id/enabled
- [ ] .../roles
- [ ] .../roles/$id
- [ ] .../list-users
    - [ ] searchTerm
    - [ ] itemsPerPage
    - [ ] selectedPage
    - [ ] sortKey
- [ ] .../authenticatedUsers/$identifier
- [ ] .../authenticatedUsers
- [ ] merge user accounts
- [ ] change user identifier
- [ ] .../superuser/$identifier
- [ ] .../authenticatedUsers/$identifier
- [ ] .../authenticatedUsers/$USERNAME/deactivate
- [ ] GET /api/users/$USERNAME/traces
- [ ] POST /api/users/$USERNAME/removeRoles
- [ ] .../assignments/assignees/$identifier
- [ ] .../permissions/$identifier
- [ ] .../assignee/$identifier
- [ ] .../savedsearches
- [ ] .../savedsearches/makelinks
- [ ] .../datasets/integrity
- [ ] .../computeDataFileHashValue
- [ ] .../validate/dataset/files/{datasetId}
- [ ] .../validate/datasets
- [ ] .../workflows
- [ ] .../workflows/$id
- [ ] .../workflows/default
- [ ] .../workflows/ip-whitelist
- [ ] .../clearMetricsCache
- [ ] .../dataverse/{dataverse alias}/addRoleAssignmentsToChildren
- [ ] /api/licenses
