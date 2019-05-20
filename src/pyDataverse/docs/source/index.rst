pyDataverse
=========================================

Release v\ |version|.

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


Developer Documentation
-----------------------------

If you are looking for information on a specific function, class, or method,
this part of the documentation is for you.

.. toctree::
   :maxdepth: 2

   developer
