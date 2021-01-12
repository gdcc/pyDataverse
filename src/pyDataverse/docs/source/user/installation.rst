.. _user_installation:

Installation
=================

There are different options on how to install a Python package, mostly depending
on your prefered tools and what you want to do with it. The easiest
way is in most cases to use `pip <https://pypi.org/project/pip/>`_.


.. _user_installation_requirements:

Requirements
-----------------------------

.. include:: ../snippets/requirements.rst


.. _user_installation_pip:

Pip
-----------------------------

To install pyDataverse, simply run this simple
`pip <https://pypi.org/project/pip/>`_ command in your terminal of choice:

.. code-block:: shell

    pip install -U pyDataverse


.. _user_installation_source-code:

Source Code
-----------------------------

PyDataverse is actively developed on GitHub, where the code is
`always available <https://github.com/GDCC/pyDataverse>`_.

You can either clone the public repository:

.. code-block:: shell

    git clone git://github.com/GDCC/pyDataverse.git

Or install via pip from the branch or commit you want (in this case the `develop` branch):

.. code-block:: shell

    pip install -U git+https://github.com/GDCC/pyDataverse.git@develop


Or, download the `tarball <https://github.com/GDCC/pyDataverse/tarball/master>`_:

.. code-block:: shell

    curl -OL https://github.com/GDCC/pyDataverse/tarball/master
    # optionally, zipball is also available (for Windows users).

Once you have a copy of the source, you can embed it in your own Python
package,

.. code-block:: shell

    cd pyDataverse
    pip install .

Or install it in editable mode into your site-packages (for pyDataverse development):

Although not required, it’s common to locally install your project in
“editable” or “develop” mode while you’re working on it. This allows your
project to be both installed and editable in project form.

.. code-block:: shell

    cd pyDataverse
    pip install -e .

Although somewhat cryptic, -e is short for --editable, and . refers to the
current working directory, so together, it means to install the current
directory (i.e. your project) in editable mode. This will also install
any dependencies declared with “install_requires” and any scripts declared
with “console_scripts”. Dependencies will be installed in the usual,
non-editable mode.

.. _user_installation_pipenv:

Pipenv
-----------------------------

`Pipenv <https://pipenv.pypa.io/en/latest/>`_ combines pip and virtualenv.

.. code-block:: shell

    pipenv install pyDataverse


.. _user_installation_test:

Test if installed properly
-----------------------------

Enter Python and look if the installation was done properly:

>>> import pyDataverse as pdv
>>> pdv.__name__
'pyDataverse'

.. _user_installation_next:

Next
-----------------------------

- :ref:`user_basic-usage`
