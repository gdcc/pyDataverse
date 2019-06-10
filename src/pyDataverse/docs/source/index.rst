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

-------------------

pyDataverse is a Python module for `Dataverse <http://dataverse.org>`_.
It uses the `Native API <http://guides.dataverse.org/en/latest/api/native-api.html>`_
and `Data Access API <http://guides.dataverse.org/en/latest/api/dataaccess.html>`_
to create, update and remove Dataverses, Datasets and Datafiles.

-------------------


Quickstart
-----------------------------

**Install**

.. code-block:: shell

    pip install pyDataverse

**Usage**

>>> from pyDataverse.api import Api
>>> # establish connection
>>> base_url = 'http://demo.dataverse.org'
>>> api = Api(base_url)
>>> api.status
'OK'
>>> # get dataverse
>>> dv = 'ecastro'  # dataverse alias or id
>>> resp = api.get_dataverse(dv)
>>> resp.json()['data']['creationDate']
'2015-04-20T09:29:39Z'
>>> # get dataset
>>> resp = api.get_dataset(identifier)
>>> resp.json()['data']['id']
24
>>> # get datafile
>>> datafile_id = '32'  # file id of the datafile
>>> resp = api.get_datafile(datafile_id)
>>> resp
<Response [200]>


Requirements
-----------------------------

pyDataverse officially supports Python 2.7 & 3.4–3.7.

External packages:

- curl


Features
-----------------------------

- Dataverse Api functionalities to create, get, publish and delete Dataverses, Datasets and Datafiles.
- Dataverse data model for easy manipulation and data conversion.
- Utils to support the core functionalities.
- Custom exceptions
- Tests on `Travis CI <https://travis-ci.com/AUSSDA/pyDataverse>`_ (`pytest <https://docs.pytest.org/en/latest/>`_ + `tox <http://tox.readthedocs.io/>`_).
- Open Source (`MIT <https://opensource.org/licenses/MIT>`_)



Community Guide
-----------------------------

This part of the documentation, which is mostly prose, details the
pyDataverse ecosystem and community.

.. toctree::
   :maxdepth: 2

   community/contact
   community/releases


Developer Guide
-----------------------------

If you are looking for information on a specific function, class, or method,
this part of the documentation is for you.

.. toctree::
   :maxdepth: 2

   developer


Contributor Guide
-----------------------------

In the spirit of free software, everyone is encouraged to help improve this project.

Here are some ways you can contribute:

- by reporting bugs
- by suggesting new features
- by translating to a new language
- by writing or editing documentation
- by writing code (**no pull request is too small**: fix typos in the user interface, add code comments, clean up inconsistent whitespace)
- by refactoring code or adding new features (please get in touch with us before you do, so we can syncronize the efforts and prevent misunderstandings)
- by `closing issues <https://github.com/AUSSDA/pyDataverse/issues>`_
- by `reviewing pull requests <https://github.com/AUSSDA/pyDataverse/pulls>`_

When you are ready, submit a `pull request <https://github.com/AUSSDA/pyDataverse>`_.

**Submitting an Issue**

We use the `GitHub issue tracker <https://github.com/AUSSDA/pyDataverse/issues>`_
to track bugs and features. Before submitting a bug report or feature request,
check to make sure it hasn't already been submitted. When submitting a bug report,
please try to provide a screenshot that demonstrates the problem.
