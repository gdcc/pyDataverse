Contributor Guide
=========================================

.. contents:: Table of Contents
  :local:

.. _contributing_get-started:

Where to Start?
-----------------------------

All contributions, bug reports, bug fixes, documentation improvements,
enhancements, and ideas are welcome!

If you are new to open-source development or pyDataverse, we recommend going
through the `GitHub issues <https://github.com/gdcc/pyDataverse/issues>`_,
to find issues that interest you. There are a number of issues listed under
`beginner <https://github.com/gdcc/pyDataverse/labels/info%3Abeginner>`_,
`docs <https://github.com/gdcc/pyDataverse/labels/pkg%3Adocs>`_
and `unassigned issues <https://github.com/gdcc/pyDataverse/issues?q=is%3Aopen++no%3Aassignee+>`_.
where you could start.
Once you've found an interesting issue, you can return here to
get your development environment setup.

When you start working on an issue, it’s a good idea to assign the issue
to yourself so that nobody else duplicates the work on it. GitHub restricts
assigning issues to maintainers of the project only. To let us know, please
add a comment to the issue so that everyone knows that you are working
on the issue.

If for whatever reason you
are not able to continue working with the issue, please try to unassign it so that
other people know it’s available again. You can periodically check the list of assigned issues,
since people may not be working in them anymore. If you want to work on one that
is assigned, feel free to kindly ask the current assignee if you can take it
(please allow at least a week of inactivity before considering work in the issue
discontinued).

This project and everyone participating in it is governed by the pyDataverse
`Code of Conduct <https://github.com/gdcc/pyDataverse/blob/master/CODE_OF_CONDUCT.md>`_.
By participating, you are expected to uphold this code. Please report
unacceptable behaviour (see :ref:`community_contact`).

**Be respectful, supportive and nice to each other!**

.. _contributing_create-issues:

Bug reports, enhancement requests and other issues
----------------------------------------------------

Bug reports are an important part of making pyDataverse more stable. Having
a complete bug report will allow others to reproduce the bug and provide
insight into fixing the issue.

Trying the bug-producing code out on the ``master`` branch is often a
worthwhile exercise to confirm the bug still exists. It is also worth
searching existing bug reports and pull requests to see if the issue
has already been reported and/or fixed.

Other reasons to create an issue could be:

* suggesting new features
* sharing an idea
* giving feedback

Please check some things before creating an issue:

* Your issue may already be reported! Please search on the `issue tracker <https://github.com/gdcc/pyDataverse/issues>`_ before creating one.
* Is this something you can **develop**? Send a pull request!

Once you have clicked `New issue <https://github.com/gdcc/pyDataverse/issues>`_,
you have to choose one of the issue templates:

* Bug report (`template <https://github.com/gdcc/pyDataverse/blob/master/.github/ISSUE_TEMPLATE/bug-template.md>`_)
* Feature request (`template <https://github.com/gdcc/pyDataverse/blob/master/.github/ISSUE_TEMPLATE/feature-template.md>`_)
* Issue: all other issues, except bug reports and feature requests (`template  <https://github.com/gdcc/pyDataverse/blob/master/.github/ISSUE_TEMPLATE/issue-template.md>`_)

After selecting the appropriate template, you will see some explanatory text. Follow it
step-by-step. After clicking `Submit new issue`, the issue will then show up
to the pyDataverse community and be open to comments/ideas from others.

Besides creating an issue, you also can contribute in many other ways by:

* sharing your knowledge in Issues and Pull Requests
* reviewing `pull requests <https://github.com/gdcc/pyDataverse/pulls>`_
* talking about pyDataverse and sharing it with others


.. _contributing_working-with-code:

Working with the code
-----------------------------

Now that you have an issue you want to fix, an enhancement to add, or
documentation to improve, you need to learn how to work with GitHub
and the pyDataverse code base.


.. _contributing_working-with-code_version-control:

Version control, Git, and GitHub
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To the new user, working with Git is one of the more daunting aspects
of contributing to pyDataverse. It can very quickly become overwhelming, but
sticking to the guidelines below will help keep the process straightforward
and mostly trouble free. As always, if you are having difficulties please
feel free to ask for help.

The code is hosted on `GitHub <https://github.com/>`_. To contribute you will need
to sign up for a `free GitHub account <https://github.com/signup/free>`_.
We use `Git <https://git-scm.com/>`_ for version control to allow many people to
work together on the project.

A great resource for learning Git: the `GitHub help pages <https://help.github.com/>`_

There are many ways to work with git and Github. Our workflow is inspired by the
`GitHub flow <https://guides.github.com/introduction/flow/>`_ and
`Git flow <https://nvie.com/posts/a-successful-git-branching-model/>`_ approaches.


.. _contributing_working-with-code_git:

Getting started with Git
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

`GitHub has instructions <https://help.github.com/set-up-git-redirect>`_ for
installing git, setting up your SSH key, and configuring git. All these steps
need to be completed before you can work seamlessly between your local
repository and GitHub.


.. _contributing_working-with-code_forking:

Forking
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You will need your own fork to work on the code. Go to the
`pyDataverse project page <https://github.com/gdcc/pyDataverse/>`_ and hit
the Fork button. You will want to clone your fork to your machine:

.. code-block:: shell

  git clone https://github.com/YOUR_USER_NAME/pyDataverse.git
  cd pyDataverse
  git remote add upstream https://github.com/gdcc/pyDataverse.git

This creates the directory `pyDataverse` and connects your repository
to the upstream (main project) pyDataverse repository.


.. _contributing_working-with-code_development-environment:

Creating a development environment
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To test out code changes, you’ll need to build pyDataverse from source,
which requires a Python environment. If you’re making documentation
changes, you can skip to
:ref:`Contributing to the documentation <contributing_documentation>`
, but if you skip creating the development environment you won’t be
able to build the documentation locally before pushing your changes.

**Creating a Python environment**

Create virtual environment.

.. code-block:: shell

  python3 -m venv .venv
  source .venv/bin/activate

Next, add the packages needed. Install at least the `development.txt`
requirements.

.. code-block:: shell

  pip install -r requirements/development.txt

In addition, you can also install certain packages for specific activities,
like ``linting``, ``testing``, ``documentation`` and ``packaging`` as you need.

.. code-block:: shell

  pip install -r requirements/lint.txt
  pip install -r requirements/tests.txt
  pip install -r requirements/docs.txt
  pip install -r requirements/packaging.txt

Now, build and install pyDataverse in editable mode.

.. code-block:: shell

  python setup.py sdist bdist_wheel
  pip install -e .


.. _contributing_working-with-code_create-branch:

Creating a branch
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You want your ``develop`` branch to reflect only release-ready code,
so create a feature branch for making your changes. Use a
descriptive branch name and replace `BRANCH_NAME` with it, e. g.
``shiny-new-feature``.

.. code-block:: shell

  git checkout develop
  git checkout -b BRANCH_NAME

This changes your working directory to the `BRANCH_NAME` branch.
Keep any changes in this branch specific to one bug or feature so it is
clear what the branch brings to pyDataverse. You can have many
branches and switch between them using the git checkout command.

When creating this branch, make sure your ``develop`` branch is up to date
with the latest upstream ``develop`` version. To update your local ``develop``
branch, you can do:

.. code-block:: shell

  git checkout develop
  git pull upstream develop --ff-only

When you want to update the feature branch with changes in ``develop`` after
you created the branch, check the section on
:ref:`updating a PR <contributing_changes_update-pull-request>`.


From here, you now can move forward to 

- contribute to the documentation (see below)
- contribute to the :ref:`code base <contributing_code>`

.. _contributing_documentation:

Contributing to the documentation
-----------------------------------------

Contributing to the documentation benefits everyone who uses pyDataverse.
We encourage you to help us improve the documentation, and you don’t have to
be an expert on pyDataverse to do so! In fact, there are sections of the docs
that are worse off after being written by experts. If something in the docs
doesn’t make sense to you, updating the relevant section after you figure
it out is a great way to ensure it will help the next person.

To find ways to contribute to the documentation, start looking the
`docs issues <https://github.com/gdcc/pyDataverse/labels/pkg%3Adocs>`_.


.. _contributing_documentation_about:

About the pyDataverse documentation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The documentation is written in **reStructuredText**, which is almost
like writing in plain English, and built using
`Sphinx <https://www.sphinx-doc.org>`_.
The Sphinx Documentation provides an
`excellent introduction to reST <https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html>`_.
Review the Sphinx docs to learn how to perform more complex changes to the documentation as well.

Some other important things to know about the docs:

- The pyDataverse documentation consists of two parts:

  - the docstrings in the code itself and
  - the docs in the folder ``src/pyDataverse/doc/``

- The docstrings provide a clear explanation of the usage of the individual functions, while the documentation consists of tutorial-like overviews per topic together with some other information (what’s new, installation, this page you're viewing right now, etc).
- The docstrings follow the `Numpy Docstring Standard <https://numpydoc.readthedocs.io/en/latest/format.html>`_.


.. _contributing_documentation_build:

How to build the pyDataverse documentation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Requirements**

First, you need to have a development environment to be able to build pyDataverse
(see the docs on
:ref:`creating a development environment <contributing_working-with-code_development-environment>`
above). Note: The ``docs.txt`` requirements need to be installed.

**Branching**

Normally, you are only allowed to create pull requests
to ``upstream/develop``, so you have to branch-off from it too.

.. code-block:: shell

  git checkout develop
  git checkout -b BRANCH_NAME


There is one exception: If you
want to suggest a change to the docs in the folder
``src/pyDataverse/docs/`` (e. g. fix a typo in
:ref:`User Guide - Basic Usage <user_basic-usage>`),
you can also pull to ``upstream/master``. This means, you have also to
branch-off from the ``master`` branch.

**Building the documentation**

You can create the docs inside ``docs/build/`` by calling ``tox``.

.. code-block:: shell

  tox -e docs

Open the file ``docs/build/html/index.html`` in a web browser to see
the full documentation you just built.


.. _contributing_documentation_pushing-changes:

Pushing documentation changes to GitHub
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Each time, a change in the ``develop`` or ``master`` branch is pushed to GitHub,
the docs automatically get created by Read the Docs.

You can find the rendered documentation at our
`Read the Docs page <https://pydataverse.readthedocs.io/>`_
, the branches at:

- `master <https://pydataverse.readthedocs.io/en/master/>`_
- `develop <https://pydataverse.readthedocs.io/en/develop/>`_

There is also a `latest <https://pydataverse.readthedocs.io/en/latest/>`_
documentation, which is not a branch itself, only a forward to ``master``.

As you do not have the rights to commit directly to the
``develop`` or ``master`` branch, you have to
:ref:`create a pull request <contributing_changes_pull-request>`
to make this happen.


.. _contributing_code:

Contributing to the code base
-----------------------------

Writing good code is not just about what you write. It is also about
how you write it. During testing, several tools will be run to check
your code for stylistic errors. Thus, good style is suggested for
submitting code to pyDataverse.

You can open a Pull Request at any point during the development process:
when you have little or no code but want to share some screenshots or
general ideas, when you're stuck and need help or advice, or when you're
ready for someone to review your work.


.. _contributing_code_standards:

Code standards
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

pyDataverse follows the `PEP8 <https://www.python.org/dev/peps/pep-0008/>`_
standard and uses `Black <https://black.readthedocs.io/en/stable/>`_,
`Flake8 <https://flake8.pycqa.org/en/latest/>`_ and
`pylint <https://www.pylint.org/>`_  to ensure a consistent code format
throughout the project.

**Imports**

In Python 3, absolute imports are recommended.

Import formatting: Imports should be alphabetically sorted within
the sections.


**String formatting**

pyDataverse uses f-strings formatting instead of ‘%’ and ‘.format()’
string formatters.


.. _contributing_code_pre-commit:

Pre-commit
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You can run many of the styling checks manually. However, we encourage
you to use `pre-commit <https://pre-commit.com/>`_ hooks instead to
automatically run ``black`` when you make a git commit.

This can be done by installing ``pre-commit`` (which should
already be installed by ``development.txt``):

.. code-block:: shell

  pip install pre-commit

and then running:

.. code-block:: shell

  pre-commit install

from the root of the pyDataverse repository. Now styling
checks will be run each time you commit changes without your needing to
run each one manually. In addition, using pre-commit will also allow you
to more easily remain up-to-date with our code checks as they change.

To run black alone, use

.. code-block:: shell

  black src/pyDataverse/file_changed.py


.. _contributing_code_type-hints:

Type hints
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

pyDataverse strongly encourages the use of
`PEP 484 <https://www.python.org/dev/peps/pep-0484>`_
style type hints. New development should contain type hints!

**Validating type hints**

pyDataverse uses `mypy <http://mypy-lang.org/>`_ to statically analyze the code base and
type hints. After making any change you can ensure your type hints are correct by running

.. code-block:: shell

  mypy src/pyDataverse/file_changed.py


.. _contributing_code_testing-with-ci:

Testing with continuous integration
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The pyDataverse test suite will run automatically on `Travis-CI <https://travis-ci.org/>`_
continuous integration service, once your pull request is submitted. However,
if you wish to run the test suite on a branch prior to submitting the pull request,
then the continuous integration services need to be hooked to your GitHub repository.
Instructions are `here <http://about.travis-ci.org/docs/user/getting-started/>`_.

A pull-request will be considered for merging when you have an all ‘green’ build.
If any tests are failing, then you will get a red ‘X’, where you can click through
to see the individual failed tests.

You can find the pyDataverse builds on Travis-CI
`here <https://travis-ci.com/github/gdcc/pyDataverse>`_.


.. _contributing_code_test-driven-development:

Test-driven development/code writing
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

pyDataverse is serious about testing and strongly encourages contributors to embrace
`test-driven development (TDD) <https://en.wikipedia.org/wiki/Test-driven_development>`_.
This development process “relies on the repetition of a very short development cycle:
first the developer writes an (initially failing) automated test case that defines a
desired improvement or new function, then produces the minimum amount of code to pass
that test.” So, before actually writing any code, you should write your tests. Often
the test can be taken from the original GitHub issue. However, it is always worth
considering additional use cases and writing corresponding tests.

Adding tests is one of the most common requests after code is pushed to pyDataverse.
Therefore, it is worth getting in the habit of writing tests ahead of time so this
is never an issue.

Like many packages, pyDataverse uses `pytest <https://docs.pytest.org/>`_ and
`tox <https://tox.readthedocs.io/>`_ as test frameworks.

To find open tasks around tests, look at open
`testing issues <https://github.com/gdcc/pyDataverse/labels/pkg%3Atesting>`_.

**Writing tests**

All tests should go into the ``tests/`` subdirectory. This folder contains
many current examples of tests, and we suggest looking to these for inspiration.


Name your tests with a descriptive filename (with prefix ``test_``) and put it
in an appropriate place in the ``tests/`` structure.

Follow the typical pattern of constructing an ``expected`` and comparing versus
the ``result``.


.. _contributing_code_run-test-suite:

Running the test suite
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Setup testing**

Before you can run the tests, you have to define following
environment variables:

- BASE_URL: Base URL of your Dataverse installation, without trailing slash (e. g. ``https://data.aussda.at``))
- API_TOKEN_<USER>: API token of Dataverse installation user with proper rights

  - API_TOKEN_SUPERUSER: Dataverse installation Superuser
  - API_TOKEN_TEST_NO_RIGHTS: New user with no assigned rights (default rights)

.. code-block:: shell

  export API_TOKEN_SUPERUSER=**SECRET**
  export API_TOKEN_TEST_NO_RIGHTS=**SECRET**
  export BASE_URL=https://data.aussda.at

**Using pytest**

The tests can then be run  directly with `pytest <https://docs.pytest.org/>`_
inside your Git clone by typing:

.. code-block:: shell

  pytest

Often it is worth running only a subset of tests first around your changes
before running the entire suite.

The easiest way to do this is with:

.. code-block:: shell

  pytest tests/path/to/test.py -k regex_matching_test_name

**Using tox**

`Tox <https://tox.readthedocs.io/>`_ can be used to execute pre-defined
test suites, e. g. ``py36`` to use and create a Python 3.6 environment to
test all tests available.

.. code-block:: shell

  tox -e py36

You can find the tox environments defined in the
`tox.ini <https://github.com/gdcc/pyDataverse/blob/master/tox.ini>`_.

Some tox tests/builds are also used for the continuous integration tests at Travis-CI
(see :ref:`contributing_code_testing-with-ci`).

**Using Coverage**

pyDataverse supports the usage of code coverage to check how much of the code base
is covered by tests. For this,
`pytest-cov <https://github.com/pytest-dev/pytest-cov>`_ (using
`coverage <https://coverage.readthedocs.io/>`_) and
`coveralls.io <https://coveralls.io/>`_ is used. You can find the coverage
report `here <https://coveralls.io/github/gdcc/pyDataverse>`_.

Run tests with ``coverage`` to create ``html`` and ``xml`` reports as an output. Again,
call it by ``tox``. This creates the generated docs inside ``docs/coverage_html/``.

.. code-block:: shell

  tox -e coverage

For coveralls, use

.. code-block:: shell

  tox -e coveralls


.. _contributing_changes:

Contributing your changes to pyDataverse
-----------------------------------------

.. _contributing_changes_commit:

Committing your code
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Before committing your changes, make clear:

- You are on the right branch
- All tests for your change ran successful
- All style and code checks for your change ran successful (mypy, pylint, flake8)
- Keep style fixes to a separate commit to make your pull request more readable

Once you’ve made changes, you can see them by typing:

.. code-block:: shell

  git status

If you have created a new file, it is not being tracked by git. Add it by typing:

.. code-block:: shell

  git add path/to/file-to-be-added.py

Doing ``git status`` again should give something like:

.. code-block:: shell

  # On branch BRANCH_NAME
  #
  #       modified:   /relative/path/to/file-you-added.py
  #

Finally, commit your changes to your local repository with an explanatory message.

The following defines how a commit message should be structured. Please reference
the relevant GitHub issues in your commit message using #1234.

- a subject line with < 80 chars.
- One blank line.
- Optionally, a commit message body.

pyDataverse uses a
`commit message template <https://github.com/gdcc/pyDataverse/blob/master/.github/.gitmessage.txt>`_
to pre-fill the commit message, once you create a commit. We recommend,
using it for your commit message.

Now, commit your changes in your local repository:

.. code-block:: shell

  git commit


.. _contributing_changes_push:

Pushing your changes
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

When you want your changes to appear publicly on your GitHub page,
push your forked feature branch’s commits:

.. code-block:: shell

  git push origin BRANCH_NAME

Here origin is the default name given to your remote repository on GitHub.
You can see the remote repositories:

.. code-block:: shell

  git remote -v

If you added the upstream repository as described above you will see something like:

.. code-block:: shell

  origin  git@github.com:YOUR_USER_NAME/pyDataverse.git (fetch)
  origin  git@github.com:YOUR_USER_NAME/pyDataverse.git (push)
  upstream        git://github.com/gdcc/pyDataverse.git (fetch)
  upstream        git://github.com/gdcc/pyDataverse.git (push)

Now your code is on GitHub, but it is not yet a part of the pyDataverse project.
For that to happen, a pull request needs to be submitted on GitHub.


.. _contributing_changes_review:

Review your code
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

When you’re ready to ask for a code review, file a pull request.
Before you do, once again make sure that you have followed all the
guidelines outlined in this document regarding code style, tests and
documentation. You should also double check your branch changes against
the branch it was based on:

- Navigate to your repository on GitHub – ``https://github.com/YOUR_USER_NAME/pyDataverse``
- Click on the ``Compare & create pull request`` button for your `BRANCH_NAME`
- Select the base and compare branches, if necessary. This will be ``develop`` and ``BRANCH_NAME``, respectively.


.. _contributing_changes_pull-request:

Finally, make the pull request
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If everything looks good, you are ready to make a pull request. A
pull request is how code from a local repository becomes available
to the GitHub community and can be looked at and eventually merged
into the ``develop`` version. This pull request and its associated changes
will eventually be committed to the ``master`` branch and available in
the next release. To submit a pull request:

- Navigate to your repository on GitHub
- Click on the ``Pull Request`` button
- You can then click on ``Commits`` and ``Files Changed`` to make sure everything looks okay one last time
- Write a description of your changes in the ``Preview Discussion`` tab. A `pull request template <https://github.com/gdcc/pyDataverse/blob/master/.github/PULL_REQUEST_TEMPLATE.md>`_ is used to pre-fill the description. Follow the explainationi in it.
- Click ``Send Pull Request``.

This request then goes to the repository maintainers, and they will review the code.

By using GitHub's @mention system in your Pull Request message, you can
ask for feedback from specific people or teams, whether they're down
the hall or ten time zones away.

Once you send a pull request, we can discuss its potential modifications and
even add more commits to it later on.

There's an excellent tutorial on how Pull Requests work in the
`GitHub Help Center <https://help.github.com/articles/using-pull-requests/>`_.


.. _contributing_changes_update-pull-request:

Updating your pull request
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Based on the review you get on your pull request, you will probably
need to make some changes to the code. In that case, you can make
them in your branch, add a new commit to that branch, push it to
GitHub, and the pull request will be automatically updated. Pushing
them to GitHub again is done by:

.. code-block:: shell

  git push origin BRANCH_NAME

This will automatically update your pull request with the latest code
and restart the
:ref:`Continuous Integration tests <contributing_code_testing-with-ci>`.

Another reason you might need to update your pull request is to solve
conflicts with changes that have been merged into the ``develop`` branch
since you opened your pull request.

To do this, you need to “merge upstream develop“ in your branch:

.. code-block:: shell

  git checkout BRANCH_NAME
  git fetch upstream
  git merge upstream/develop

If there are no conflicts (or they could be fixed automatically), a
file with a default commit message will open, and you can simply save
and quit this file.

If there are merge conflicts, you need to solve those conflicts. See
for example in
`the GitHub tutorial on merge conflicts <https://help.github.com/articles/resolving-a-merge-conflict-using-the-command-line/>`_
for an explanation on how to do this. Once the conflicts are merged
and the files where the conflicts were solved are added, you can run
``git commit`` to save those fixes.

If you have uncommitted changes at the moment you want to update the
branch with ``develop``, you will need to ``stash`` them prior to updating
(see the `stash docs <https://git-scm.com/book/en/v2/Git-Tools-Stashing-and-Cleaning>`_).
This will effectively store your changes and they can be reapplied after updating.

After the feature branch has been update locally, you can now update your
pull request by pushing to the branch on GitHub:

.. code-block:: shell

  git push origin BRANCH_NAME


.. _contributing_changes_delete-merged-branch:

Delete your merged branch (optional)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Once your feature branch is accepted into upstream, you’ll probably
want to get rid of the branch. First, merge upstream develop into your
branch so git knows it is safe to delete your branch:

.. code-block:: shell

  git fetch upstream
  git checkout develop
  git merge upstream/develop

Then you can do:

.. code-block:: shell

  git branch -d BRANCH_NAME

Make sure you use a lower-case -d, or else git won’t warn you if your
feature branch has not actually been merged.

The branch will still exist on GitHub, so to delete it there do:

.. code-block:: shell

  git push origin --delete BRANCH_NAME


.. _contributing_changes_tips:

Tips for a successful pull request
-----------------------------------------

If you have made it to the
:ref:`Review your code <contributing_changes_review>` phase
, one of the core
contributors may take a look. Please note however that a handful of
people are responsible for reviewing all of the contributions, which
can often lead to bottlenecks.

To improve the chances of your pull request being reviewed, you should:

- **Reference an open issue** for non-trivial changes to clarify the PR’s purpose
- **Ensure you have appropriate tests**. These should be the first part of any PR
- **Keep your pull requests as simple as possible**. Larger PRs take longer to review
- **Ensure that CI is in a green state**. Reviewers may not even look otherwise
- Keep :ref:`updating your pull request <contributing_changes_update-pull-request>`, either by request or every few days


.. _contributing_after-pull-request:

What happens after the pull
-----------------------------------------


.. _contributing_after-pull-request_review:

Reviewing the Pull request
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Once a new issue is created, a maintainer adds
`labels <https://github.com/gdcc/pyDataverse/labels>`_
, an assignee and a
`milestone <https://github.com/gdcc/pyDataverse/milestones>`_
to it. Labels are used to separate between issue types and the
status of it, show effected module(s) and to prioritize tasks.
Also at least one responsible person for the next steps is assigned
, and often a milestone too.

The next steps may consist of requests from the assigned person(s)
for further work, questions on
some changes or the okay for the pull request to be merged.

Once all actions are done, including review and documentation, the issue
gets closed. The issue then lives on as an open and transparent
documentation of the work done.


.. _contributing_after-pull-request_create-release:

Create a release
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

First, to plan a release, the maintainers:

- define, which issues are part of it and the version number
- create a new milestone for the release (named after the version number)
- and assign all selected issues to the milestone

Once all issues related to the release are closed (except the ones
related to release activities), the release can be created. This includes:

- review documentation and code changes
- test the release
- write release notes
- write a release announcement
- update version number
- merge ``develop`` to ``master``
- tag release name to commit (e. g. ``v0.3.0``), push branch and create pull request
- upload to `PyPI <https://pypi.org/>`_

You can find the full release history at :ref:`community_history` and on
`GitHub <https://github.com/gdcc/pyDataverse/releases>`_.

**Versioning**

For pyDataverse, `Semantic versioning <https://semver.org/>`_ is used for releases.


.. _contributing_resources:
