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


Models Interface
-----------------------------

.. automodule:: pyDataverse.models
  :members:


Utils Interface
-----------------------------

.. automodule:: pyDataverse.utils
  :members:


Exceptions
------------

.. automodule:: pyDataverse.exceptions
  :members:


Install
---------

In order to install pyDataverse (and all of its dependencies) follow the steps below:

Clone `pyDataverse <https://github.com/AUSSDA/pyDataverse.git>`_ repository into local machine
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. code-block:: shell

    $ git clone git@github.com:AUSSDA/pyDataverse.git
    $ cd pyDataverse

Create and enable a virtual environment **(Optional)**
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The more Python projects you have, the more likely it is that you need to
work with different versions of
Python libraries, or even Python itself. Newer versions of libraries for one
project can break compatibility in another project.

Virtual environments are independent groups of Python libraries, one for each
project. Packages installed for one project will not affect other projects or
the operating system's packages.

Python 3 comes bundled with the :mod:`venv` module to create virtual
environments. If you're using a modern version of Python, you can continue on
to the next section.

If you are using Python 2, the :mod:`venv` module is not available. Instead,
install `virtualenv`_:

    On Linux, virtualenv is provided by your package manager:

    .. code-block:: sh

        # Debian, Ubuntu
        $ sudo apt-get install python-virtualenv

        # CentOS, Fedora
        $ sudo yum install python-virtualenv

        # Arch
        $ sudo pacman -S python-virtualenv

    If you are on Mac OS X or Windows, download `get-pip.py`_, then:

    .. code-block:: sh

        $ sudo python2 Downloads/get-pip.py
        $ sudo python2 -m pip install virtualenv

    On Windows, as an administrator:

    .. code-block:: bat

        > \Python27\python.exe Downloads\get-pip.py
        > \Python27\python.exe -m pip install virtualenv

Create an environment
"""""""""""""""""""""""

Create a project folder and a :file:`venv` folder within:

.. code-block:: sh

    $ mkdir myproject
    $ cd myproject
    $ python3 -m venv venv

On Windows:

.. code-block:: bat

    $ py -3 -m venv venv

If you needed to install virtualenv because you are using Python 2, use
the following command instead:

.. code-block:: sh

    $ python2 -m virtualenv venv

On Windows:

.. code-block:: bat

    > \Python27\Scripts\virtualenv.exe venv

Activate the environment
""""""""""""""""""""""""""

Before you work on your project, activate the corresponding environment:

.. code-block:: sh

    $ source venv/bin/activate

On Windows:

.. code-block:: bat

    > venv\Scripts\activate

Your shell prompt will change to show the name of the activated environment.

Install necessary requirements:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: shell

    $ pip install -r deps/tests-requirements.txt
    $ pip install -r deps/lint-requirements.txt
    $ pip install -r deps/docs-requirements.txt
    $ pip install -r deps/packaging-requirements.txt
    $ pip install -e .


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

**Create Coverage Reports**

Run tests with coverage to create html and xml reports as an output. Again, call it via `tox`. This creates the created docs inside `docs/coverage_html/`.

.. code-block:: shell

    tox -e coverage

**Run Coveralls**

To use Coveralls on local development:

.. code-block:: shell

    tox -e coveralls

Documentation
-----------------------------


**Create Sphinx Docs**

Use Sphinx to create class and function documentation out of the doc-strings. You can call it via `tox`. This creates the created docs inside `docs/build`.

.. code-block:: shell

    tox -e docs

.. _virtualenv: https://virtualenv.pypa.io/
.. _get-pip.py: https://bootstrap.pypa.io/get-pip.py
