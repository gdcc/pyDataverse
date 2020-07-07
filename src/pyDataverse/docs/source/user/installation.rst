.. _user_installation:

Installation
=================

There are different options on how to install a Python package, mostly depending
on your prefered tools and what you want to do with it. The easiest
way is in most cases to use `pip <https://pypi.org/project/pip/>`_.


Requirements
-----------------------------

pyDataverse officially supports Python 3.4–3.7.

Python packages:

- requests>=2.12.0
- jsonschema>=3.2.0


Pip
-----------------------------

To install pyDataverse, simply run this simple
`pip <https://pypi.org/project/pip/>`_ command in your terminal of choice:

.. code-block:: shell

    pip install -U pyDataverse


Source Code
-----------------------------

PyDataverse is actively developed on GitHub, where the code is
`always available <https://github.com/AUSSDA/pyDataverse>`_.

You can either clone the public repository:

.. code-block:: shell

    git clone git://github.com/aussda/pyDataverse.git

Or install via pip from the branch or commit you want (in this case the `develop` branch):

.. code-block:: shell

    pip install -U git+https://github.com/aussda/pyDataverse.git@develop


Or, download the `tarball <https://github.com/aussda/pyDataverse/tarball/master>`_:

.. code-block:: shell

    curl -OL https://github.com/aussda/pyDataverse/tarball/master
    # optionally, zipball is also available (for Windows users).

Once you have a copy of the source, you can embed it in your own Python
package,

.. code-block:: shell

    cd pyDataverse
    pip install .

Or install it in editable mode into your site-packages (for pyDataverse development):

.. code-block:: shell

    cd pyDataverse
    pip install -e .


Pipenv
-----------------------------

`Pipenv <https://pipenv.pypa.io/en/latest/>`_ combines pip and virtualenv.

.. code-block:: shell

    pipenv install pyDataverse


Test if installed properly
-----------------------------

Enter Python and look if the installation was done properly:

>>> import pyDataverse as pdv
>>> pdv.__name__
'pyDataverse'

Next
-----------------------------

- :ref:`user_basic-usage`
