.. _homepage:

pyDataverse
=========================================

Release v\ |version|.

.. image:: https://img.shields.io/github/v/release/gdcc/pyDataverse
    :target: https://github.com/gdcc/pyDataverse

.. image:: https://img.shields.io/conda/vn/conda-forge/pydataverse.svg
    :target: https://anaconda.org/conda-forge/pydataverse 
    
.. image:: https://travis-ci.com/gdcc/pyDataverse.svg?branch=master
    :target: https://travis-ci.com/gdcc/pyDataverse

.. image:: https://img.shields.io/pypi/v/pyDataverse.svg
    :target: https://pypi.org/project/pyDataverse/

.. image:: https://img.shields.io/pypi/wheel/pyDataverse.svg
    :target: https://pypi.org/project/pyDataverse/

.. image:: https://img.shields.io/pypi/pyversions/pyDataverse.svg
    :target: https://pypi.org/project/pyDataverse/

.. image:: https://readthedocs.org/projects/pydataverse/badge/?version=latest
    :target: https://pydataverse.readthedocs.io/en/latest

.. image:: https://coveralls.io/repos/github/gdcc/pyDataverse/badge.svg
    :target: https://coveralls.io/github/gdcc/pyDataverse

.. image:: https://img.shields.io/github/license/gdcc/pydataverse.svg
    :target: https://opensource.org/licenses/MIT

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black

.. image:: https://zenodo.org/badge/DOI/10.5281/zenodo.4664557.svg
   :target: https://doi.org/10.5281/zenodo.4664557

-------------------

.. _homepage_description:

**pyDataverse** is a Python module for `Dataverse <http://dataverse.org>`_ you can use for:  

- accessing the Dataverse `API's <http://guides.dataverse.org/en/latest/api/index.html>`_
- manipulating and using the Dataverse (meta)data - Dataverses, Datasets, Datafiles

No matter, if you want to import huge masses of data into
Dataverse, test your Dataverse instance after deployment or want to make
basic API calls:
**pyDataverse helps you with Dataverse!**

pyDataverse is fully Open Source and can be used by everybody.

.. image:: https://www.repostatus.org/badges/latest/unsupported.svg
   :alt: Project Status: Unsupported – The project has reached a stable, usable state but the author(s) have ceased all work on it. A new maintainer may be desired.
   :target: https://www.repostatus.org/#unsupported

pyDataverse is not supported right now. A new maintainer or funding is desired. Please contact the author `Stefan Kasberger <https://www.stefankasberger.at>`_, if you want to contribute in some way.

.. _homepage_install:

Install
-----------------------------

To install pyDataverse, simply run this command in your terminal of choice:

.. code-block:: shell

    pip install pyDataverse

Or run this command to install using conda:

.. code-block:: shell

    conda install pyDataverse -c conda-forge

Find more options at :ref:`user_installation`.

**Requirements**

.. include:: snippets/requirements.rst


.. _homepage_quickstart:

Quickstart
-----------------------------

.. include:: snippets/warning_production.rst

**Import Dataset metadata JSON**

To import the metadata of a Dataset from Dataverse's own JSON format,
use :meth:`ds.from_json() <pyDataverse.models.Dataset.from_json>`.
The created :class:`Dataset <pyDataverse.models.Dataset>` can then
be retrieved with :meth:`get() <pyDataverse.models.Dataset.get>`.

For this example, we use the ``dataset.json`` from
``tests/data/user-guide/``
(`GitHub repo <https://github.com/gdcc/pyDataverse/tree/master/tests/data/user-guide>`_)
and place it in the root directory.

::

    >>> from pyDataverse.models import Dataset
    >>> from pyDataverse.utils import read_file
    >>> ds = Dataset()
    >>> ds_filename = "dataset.json"
    >>> ds.from_json(read_file(ds_filename))
    >>> ds.get()
    {'citation_displayName': 'Citation Metadata', 'title': 'Youth in Austria 2005', 'author': [{'authorName': 'LastAuthor1, FirstAuthor1', 'authorAffiliation': 'AuthorAffiliation1'}], 'datasetContact': [{'datasetContactEmail': 'ContactEmail1@mailinator.com', 'datasetContactName': 'LastContact1, FirstContact1'}], 'dsDescription': [{'dsDescriptionValue': 'DescriptionText'}], 'subject': ['Medicine, Health and Life Sciences']}

**Create Dataset by API**

To access Dataverse's Native API, you first have to instantiate
:class:`NativeApi <pyDataverse.api.NativeApi>`. Then create the
Dataset through the API with
:meth:`create_dataset() <pyDataverse.api.NativeApi.create_dataset>`.

This returns, as all API functions do, a
:class:`httpx.Response <httpx.Response>` object, with the
DOI inside ``data``.

Replace following variables with your own instance data
before you execute the lines:

- BASE_URL: Base URL of your Dataverse instance, without trailing slash (e. g. ``https://data.aussda.at``))
- API_TOKEN: API token of a Dataverse user with proper rights to create a Dataset
- DV_PARENT_ALIAS: Alias of the Dataverse, the Dataset should be attached to.

::

    >>> from pyDataverse.api import NativeApi
    >>> api = NativeApi(BASE_URL, API_TOKEN)
    >>> resp = api.create_dataset(DV_PARENT_ALIAS, ds.json())
    Dataset with pid 'doi:10.5072/FK2/UTGITX' created.
    >>> resp.json()
    {'status': 'OK', 'data': {'id': 251, 'persistentId': 'doi:10.5072/FK2/UTGITX'}}


For more tutorials, check out
:ref:`User Guide - Basic Usage <user_basic-usage>` and
:ref:`User Guide - Advanced Usage <user_advanced-usage>`.


.. _homepage_features:

Features
-----------------------------

- **Comprehensive API wrapper** for all Dataverse API’s and most of their endpoints
- **Data models** for each of Dataverses data types: **Dataverse, Dataset and Datafile**
- Data conversion to and from Dataverse's own JSON format for API uploads
- **Easy mass imports and exports through CSV templates**
- Utils with helper functions
- **Documented** examples and functionalities
- Custom exceptions
- Tested (`Travis CI <https://travis-ci.com/gdcc/pyDataverse>`_) and documented (`Read the Docs <https://pydataverse.readthedocs.io/>`_)
- Open Source (`MIT <https://opensource.org/licenses/MIT>`_)


.. _homepage_user-guide:

User Guide
-----------------------------

.. toctree::
   :maxdepth: 3

   user/installation
   user/basic-usage
   user/advanced-usage
   user/use-cases
   user/csv-templates
   user/faq
   Wiki <https://github.com/gdcc/pyDataverse/wiki>
   user/resources


.. _homepage_reference:

Reference / API
-----------------------------

If you are looking for information on a specific class, function, or method,
this part of the documentation is for you.

.. toctree::
   :maxdepth: 2

   reference


.. _homepage_community-guide:

Community Guide
-----------------------------

This part of the documentation, which is mostly prose, details the
pyDataverse ecosystem and community.

.. toctree::
   :maxdepth: 1

   community/contact
   community/releases


.. _homepage_contributor-guide:

Contributor Guide
-----------------------------

.. toctree::
   :maxdepth: 2

   contributing/contributing


.. _homepage_thanks:

Thanks!
-----------------------------

To everyone who has contributed to pyDataverse - with an idea, an issue, a
pull request, developing used tools, sharing it with others or by any other means:
**Thank you for your support!**

Open Source projects live from the cooperation of the many and pyDataverse is
no exception to that, so to say thank you is the least that can be done.

Special thanks to Lars Kaczmirek, Veronika Heider, Christian Bischof, Iris
Butzlaff and everyone else from AUSSDA, Slava Tykhonov and Marion Wittenberg
from DANS and all the people who do an amazing job by developing Dataverse
at IQSS, but especially to Phil Durbin for it's support from the first minute.

pyDataverse is funded by
`AUSSDA - The Austrian Social Science Data Archive <https://aussda.at>`_
and through the EU Horizon2020 programme
`SSHOC - Social Sciences & Humanities Open Cloud <https://www.sshopencloud.eu/about-sshoc>`_
(T5.2).


.. _homepage_license:

License
-----------------------------

Copyright Stefan Kasberger and others, 2019-2021.

Distributed under the terms of the MIT license, pyDataverse is free and open source software.

Full License Text: `LICENSE.txt <https://github.com/GDCC/pyDataverse/blob/master/LICENSE.txt>`_
