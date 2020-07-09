.. _homepage:

pyDataverse
=========================================

Release v\ |version|.

.. image:: https://travis-ci.com/AUSSDA/pyDataverse.svg?branch=master
    :target: https://travis-ci.com/AUSSDA/pyDataverse

.. image:: https://img.shields.io/pypi/v/pyDataverse.svg
    :target: https://pypi.org/project/pyDataverse/

.. image:: https://img.shields.io/pypi/wheel/pyDataverse.svg
    :target: https://pypi.org/project/pyDataverse/

.. image:: https://img.shields.io/pypi/pyversions/pyDataverse.svg
    :target: https://pypi.org/project/pyDataverse/

.. image:: https://readthedocs.org/projects/pydataverse/badge/?version=latest
    :target: https://pydataverse.readthedocs.io/en/latest

.. image:: https://coveralls.io/repos/github/AUSSDA/pyDataverse/badge.svg
    :target: https://coveralls.io/github/AUSSDA/pyDataverse

.. image:: https://img.shields.io/github/license/aussda/pydataverse.svg
    :target: https://opensource.org/licenses/MIT

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black

-------------------

**pyDataverse** is a tool to easily connect with the
`Dataverse <http://dataverse.org>`_ world. It helps working with the
`Dataverse API's <http://guides.dataverse.org/en/latest/api/index.html>`_
and its metadata models.

It's a wrapper for the Dataverse API’s to make convenient API calls and offers
Python objects for each of Dataverses own data types: Dataverses, Datasets
and Datafiles.

No matter, if you want to import huge masses of metadata and data into a
Dataverse instance. connect your service with an instance or just want to make
some API calls - **pyDataverse can help you!**


Install
-----------------------------

To install pyDataverse, simply run this simple command in your terminal of choice:

.. code-block:: shell

    pip install pyDataverse


You can find more options at :ref:`user_installation`.

**Requirements**

pyDataverse officially supports Python 3.4–3.7.

Python packages:

- `requests <https://requests.readthedocs.io/en/master/>`_>=2.12.0
- `jsonschema <https://github.com/Julian/jsonschema>`_>=3.2.0


Quickstart
-----------------------------

.. warning::
  Do not execute the examples code on your production instance!

**Import Dataset metadata**

Import metadata coming from Dataverses API JSON format (which is needed for
API uploads).

>>> from pyDataverse.models import Dataset
>>> from pyDataverse.utils import read_file
>>> ds = Dataset()
>>> json_filename = 'tests/data/dataset_upload_min_tutorial_mass-migration.json'
>>> ds.from_json(read_file(json_filename))
>>> ds.get()
{'citation_displayName': 'Citation Metadata', 'title': 'Youth in Austria 2005', 'author': [{'authorName': 'LastAuthor1, FirstAuthor1', 'authorAffiliation': 'AuthorAffiliation1'}], 'datasetContact': [{'datasetContactEmail': 'ContactEmail1@mailinator.com', 'datasetContactName': 'LastContact1, FirstContact1'}], 'dsDescription': [{'dsDescriptionValue': 'DescriptionText'}], 'subject': ['Medicine, Health and Life Sciences']}


**Create Dataset via API**

Create the Dataset via the API. Following variables related to your Dataverse
instance must be changed before you can execute the code:

- BASE_URL: (e. g. ‘https://demo.dataverse.org’))
- API_TOKEN: API token of a Dataverse user with the right to create a Dataset
- DV_PARENT_ALIAS: Alias of the Dataverse, in which the Dataset should be created.

>>> from pyDataverse.api import NativeApi
>>> api = NativeApi('BASE_URL', 'API_TOKEN')
>>> resp = api.create_dataset('DV_PARENT_ALIAS', ds_json)
Dataset with pid 'doi:10.5072/FK2/UTGITX' created.
>>> resp.json()
{'status': 'OK', 'data': {'id': 251, 'persistentId': 'doi:10.5072/FK2/UTGITX'}}


Features
-----------------------------

- Comprehensive API wrapper for all API’s and nearly all endpoints
- Python objects for each Dataverse data type: Dataverse, Dataset and Datafile
- Data conversion to and from Dataverses own API JSON format
- Easy mass imports and exports via pyDataverse’s own CSV format
- Helper functions to handle Dataverse metadata and data
- Custom exceptions
- Tests on `Travis CI <https://travis-ci.com/AUSSDA/pyDataverse>`_ (`pytest <https://docs.pytest.org/en/latest/>`_ + from datetime import date`tox <http://tox.readthedocs.io/>`_)
- Open Source (`MIT <https://opensource.org/licenses/MIT>`_)


User Guide
-----------------------------

.. toctree::
   :maxdepth: 1

   user/installation
   user/basic-usage
   user/advanced-usage
   user/use-cases
   user/faq


Reference / API
-----------------------------

If you are looking for information on a specific class, function, or method,
this part of the documentation is for you.

.. toctree::
   :maxdepth: 2

   reference


Community Guide
-----------------------------

This part of the documentation, which is mostly prose, details the
pyDataverse ecosystem and community.

.. toctree::
   :maxdepth: 1

   community/contact
   community/media
   community/releases


Contributor Guide
-----------------------------

.. toctree::
   :maxdepth: 1

   contributor/index


Thanks!
-----------------------------

To everyone who has contributed to pyDataverse - with an idea, an issue, a
pull request, sharing it with others or by any other means:
Thank you for your support!

Open Source projects in general live from the cooperation of the many and pyDataverse is
standing on the shoulders of so many contributors, so to say thanks is the
least that can be done.

Special thanks to Lars Kaczmirek, Veronika Heider, Christian Bischof, Iris
Butzlaff and everyone else from AUSSDA, Slava Tykhonov and Marion Wittenberg
from DANS and all the people who do an amazing job by developing Dataverse
at IQSS, but especially to Phil Durbin.

pyDataverse is funded by
`AUSSDA - The Austrian Social Science Data Archive <https://aussda.at/ueber-aussda/team/>`_
and the EU Horizon2020 programme
`SSHOC - Social Sciences & Humanities Open Cloud <https://www.sshopencloud.eu/about-sshoc>`_.


License
-----------------------------

Copyright Stefan Kasberger and others, 2019-2020.

Distributed under the terms of the MIT license, pyDataverse is free and open source software.

Full License Text: `LICENSE.txt <https://github.com/AUSSDA/pyDataverse/blob/master/LICENSE.txt>`_
