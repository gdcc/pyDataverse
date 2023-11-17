[![PyPI](https://img.shields.io/pypi/v/pyDataverse.svg)](https://pypi.org/project/pyDataverse/) [![Build Status](https://travis-ci.com/gdcc/pyDataverse.svg?branch=master)](https://travis-ci.com/gdcc/pyDataverse) [![Coverage Status](https://coveralls.io/repos/github/gdcc/pyDataverse/badge.svg)](https://coveralls.io/github/gdcc/pyDataverse) [![Documentation Status](https://readthedocs.org/projects/pydataverse/badge/?version=latest)](https://pydataverse.readthedocs.io/en/latest) ![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pydataverse.svg) [![GitHub](https://img.shields.io/github/license/gdcc/pydataverse.svg)](https://opensource.org/licenses/MIT) [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black) [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.4664557.svg)](https://doi.org/10.5281/zenodo.4664557)

# pyDataverse

[![Project Status: Unsupported – The project has reached a stable, usable state but the author(s) have ceased all work on it. A new maintainer may be desired.](https://www.repostatus.org/badges/latest/unsupported.svg)](https://www.repostatus.org/#unsupported)

pyDataverse is a Python module for [Dataverse](http://dataverse.org).
It helps to access the Dataverse [API's](http://guides.dataverse.org/en/latest/api/index.html) and manipulate, validate, import and export all Dataverse data-types (Dataverse, Dataset, Datafile).

**Find out more: [pyDataverse Documentation](https://pydataverse.readthedocs.io/en/latest/)**

-----
Implementated methods for /api/admin.  These methods are implemented.  They
do not validate input (such as JSON objects), and do not yet have testcases.

/api/admin endpoints:
- [x] .../settings, .../settings/$name
    - [x] get_settings()
    - [x] get_setting(setting)
    - [x] configure_setting(name, value)
    - [x] delete_setting(setting)
- [ ] .../bannerMessage
    - [ ] add_banner_message(messages_JSON)
    - [ ] show_banner_messages()
    - [ ] delete_banner_message(id)
    - [ ] deactive_banner_message(id)
- [x] .../authenticationProviderFactories
    - [x] list_auth_provider_factories()
- [ ] .../authenticationProviders
    - [x] list_auth_providers()
    - [x] add_auth_provider(authProviderJSON)
    - [x] show_auth_provider(identifier)
    - [ ] enable_auth_provider(id)
    - [ ] disable_auth_provider(id)
    - [x] check_auth_provider_enabled(id)
    - [x] delete_auth_provider
- [x] .../roles
    - [x] list_global_roles()
    - [x] create_global_role(roles_JSON)
    - [x] delete_global_role(id)
- [ ] .../list-users
    - [ ] list_users(searchTerm, itemsPerPage, selectedPage, sortKey)
- [ ] .../authenticatedUsers
    - [x] list_user(identifier)
    - [x] create_user(userJSON)
    - [ ] delete_user(id)
    - [x] deactivate_user(id)
- [x] merge user accounts
    - [x] merge_users(dest_acct, source_acct)
- [x] change user identifier
    - [x] change_user_identifier(old_identifier, new_identifier)
- [x] .../superuser/$identifier
    - [x] superuser_toggle(userId)
- [ ] GET /api/users/$USERNAME/traces
    - [ ] show_user_traces(username)
- [ ] POST /api/users/$USERNAME/removeRoles
    - [ ] remove_all_roles(username)
- [x] .../assignments/assignees/$identifier
    - [x] list_role_assignments(identifier)
- [x] .../permissions/$identifier
    - [x] list_permissions(identifier)
- [x] .../assignee/$identifier
    - [x] show_role_assignee(identifier)
- [ ] .../savedsearches
    - [ ] list_searches()
    - [ ] list_search(id)
    - [ ] execute_search(id)
- [ ] .../datasets/integrity
    - [ ] calculate_unf(datasetVerId)
- [ ] .../computeDataFileHashValue
    - [ ] calculate_datafile_checksum(fileId)
    - [ ] validate_current_datafile_checksum(fileId)
- [ ] .../validate/dataset/files/{datasetId}
    - [ ] validate_dataset_files(datasetId)
- [ ] .../updateHashValues(algorithm, batch_size)
    - [ ] update_dataset_hashes(datasetId)
- [ ] .../workflows
    - [ ] list_workflows()
    - [ ] show_workflow(id)
    - [ ] add_workflow(workflowJSON)
    - [ ] delete_workflow(id)
    - [ ] list_default_workflow()
    - [ ] set_default_workflow(workflow_id, workflow_trigger)
    - [ ] unset_default_workflow(trigger_type)
    - [ ] set_workflow_allowed_ip(allowed_list)
    - [ ] get_workflow_allowed_ip()
    - [ ] restore_workflow_default_allowed_ip()
- [ ] .../clearMetricsCache
    - [ ] clear_cached_metrics()
    - [ ] clear_metric_cache(metric_db_name)
- [ ] .../dataverse/{dataverse alias}/addRoleAssignmentsToChildren
    - [ ] inherit_role_assignments(datavserse)
- [ ] /api/licenses
    - [ ] view_licenses_available()
    - [ ] view_dataset_license(id)
    - [ ] add_dataset_license(licenseJSON)
    - [ ] set_dataset_license()
    - [ ] delete_dataset_license(id)
    - [ ] set_dataset_license_sort(id, sort_order)
- [ ] .../templates
    - [ ] list_templates()
    - [ ] list_templates(id)
    - [ ] delete_template(id)
- [ ] .../requestSignedUrl
    - [ ] request_signed_url(url, timeout, http_method, user)
- [ ] .../feedback
    - [ ] send_feedback(feedbackJSON)
- [ ] .../mydata
    - [ ] list_data(role_id, dv_object_type, published_states, per_page)
