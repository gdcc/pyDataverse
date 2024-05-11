.. _user_installation:

Installation
=================

.. contents:: Table of Contents
  :local:

There are different options on how to install a Python package, mostly depending
on your preferred tools and what you want to do with it. The easiest
way is in most cases to use pip (see :ref:`below <user_installation_pip>`).


.. _user_installation_requirements:

Requirements
-----------------------------

.. include:: ../snippets/requirements.rst


Installer requirements: `setuptools <https://pypi.org/project/setuptools>`_


.. _user_installation_pip:

Pip
-----------------------------

To install the latest release of pyDataverse from PyPI, simply run this
`pip <https://pypi.org/project/pip/>`_
command in your terminal of choice:

.. include:: ../snippets/pip-install.rst


.. _user_installation_pipenv:

Pipenv
-----------------------------

`Pipenv <https://pipenv.pypa.io/en/latest/>`_ combines pip and virtualenv.

.. code-block:: shell

    pipenv install pyDataverse


.. _user_installation_source-code:


Conda
-----------------------------

pyDataverse is also available through `conda-forge <https://conda-forge.org/>`_.

.. code-block:: shell

    conda install pyDataverse -c conda-forge


Source Code
-----------------------------

PyDataverse is actively developed on GitHub, where the code is
`always available <https://github.com/gdcc/pyDataverse>`_.

You can either clone the public repository:

.. code-block:: shell

    git clone git://github.com/gdcc/pyDataverse.git

Or download the archive of the ``master`` branch as a zip:

.. code-block:: shell

    curl -OL https://github.com/gdcc/pyDataverse/archive/master.zip

Once you have a copy of the source, you can embed it in your own Python
package:

.. code-block:: shell

    cd pyDataverse
    pip install .


.. _user_installation_development:

Development
-----------------------------

To set up your development environment, see
:ref:`contributing_working-with-code_development-environment`.
