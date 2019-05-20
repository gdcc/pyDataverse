Developer Interface
=========================================

.. module:: pyDataverse

This part of the documentation covers all the interfaces of pyDataverse. For
parts where pyDataverse depends on external libraries, we document the most
important right here and provide links to the canonical documentation.

Api Interface
-----------------------------

.. automodule:: pyDataverse.api
   :members:


Utils Interface
-----------------------------

.. automodule:: pyDataverse.utils
  :members:


Exceptions
-----------------------------

.. automodule:: pyDataverse.exceptions
  :members:


Install
-----------------------------

Install from the local git repository:

.. code-block:: shell

    virtualenv venv
    source venv/bin/activate
    pip install -r requirements.txt


Testing
-----------------------------

Before you can execute tests, you need a Dataverse account with an api
token on a working Dataverse instance. We recommend to use
`demo.dataverse.org <https://demo.dataverse.org>`_, but you also can use your
own instance or any other, but beware: To use a production instance can cause
problems.

Before you can run the tests, you have to set the ENV variables for the
Dataverse Api connection. This can be done via creation of a `pytest.ini` file:

.. code-block:: ini

    [pytest]
    env =
        API_TOKEN=**SECRET**
        DATAVERSE_VERSION=4.14
        BASE_URL=https://demo.dataverse.org/

or define them manually in the terminal:

.. code-block:: shell

    export API_TOKEN=**SECRET**
    export DATAVERSE_VERSION=4.14
    export BASE_URL=https://demo.dataverse.org/

To run through all tests (e. g. different python versions, packaging, docs, flake8, etc.), simply call tox from the root directory:

.. code-block:: shell

    tox

When you only want to run one test, e.g. the py36 test:

.. code-block:: shell

    tox -e py36
