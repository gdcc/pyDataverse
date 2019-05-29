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

Install from the local git repository, with all it's dependencies:

.. code-block:: shell

    git clone git@github.com:AUSSDA/pyDataverse.git
    cd pyDataverse
    virtualenv venv
    source venv/bin/activate
    pip install -r tools/tests-requirements.txt
    pip install -r tools/lint-requirements.txt
    pip install -r tools/docs-requirements.txt
    pip install -r tools/packaging-requirements.txt
    pip install -e .


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

To find out more about which tests are available, have a look inside the tox.ini file.


Documentation
-----------------------------


**Create Sphinx Docs**

Use Sphinx to create class and function documentation out of the doc-strings. You can call it via `tox`. This creates the created docs inside `docs/build`.

.. code-block:: shell

    tox -e docs

**Create Coverage Reports**

Run tests with coverage to create html and xml reports as an output. Again, call it via `tox`. This creates the created docs inside `docs/coverage_html/`.

.. code-block:: shell

    tox -e coverage

**Run Coveralls**

To use Coveralls on local development:

.. code-block:: shell

    tox -e coveralls
