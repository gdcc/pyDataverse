# Contributing Guide

## Where to Start?

All contributions—bug reports, fixes, documentation improvements, enhancements, and ideas—are welcome.

If you're new to open source or pyDataverse, browse the GitHub issues, especially:

- Issues labeled **beginner**
- Issues labeled **docs**
- Issues that are **unassigned**

If you want to work on an issue, assign it to yourself (or comment if you cannot assign).  
If you stop working on it, unassign so others can continue.

This project follows the **pyDataverse Code of Conduct**.  
Be respectful, supportive, and nice to each other.

---

## Bug Reports, Enhancement Requests, and Other Issues

Bug reports help make pyDataverse more stable. Before creating an issue:

- Confirm the bug still exists on the `main` branch.
- Search existing issues and PRs.
- Consider whether you can develop a fix.

Issue templates include:

- Bug report  
- Feature request  
- Other issues  

You can also contribute by:

- Sharing knowledge in issues/PRs  
- Reviewing PRs  
- Talking about pyDataverse  

---

## Working With the Code

### Version Control, Git, and GitHub

The code is hosted on GitHub.  
You need a GitHub account and Git installed.

Helpful resources:

- GitHub help pages  
- GitHub flow  
- Git flow  

### Getting Started With Git

GitHub provides setup instructions.

### Forking

Fork the repository and clone your fork:

```bash
git clone https://github.com/YOUR_USER_NAME/pyDataverse.git
cd pyDataverse
git remote add upstream https://github.com/gdcc/pyDataverse.git
```

### Creating a Development Environment

pyDataverse uses **poetry** for dependency management.

```bash
poetry install --with=dev
poetry run python3 -c "import pyDataverse; print(pyDataverse.__version__)"
```

Enter the virtual environment:

```bash
poetry shell
```

Build docs:

```bash
poetry run tox -e docs
```

### Creating a Branch

```bash
git checkout main
git checkout -b BRANCH_NAME
```

Keep your `main` branch updated:

```bash
git checkout main
git pull --rebase upstream
```

---

## Contributing to the Documentation

Documentation is written in **reStructuredText** and built with **Sphinx**.

### About the Documentation

Two parts:

- Docstrings in the code  
- Files in `pyDataverse/doc/`  

Docstrings follow the **NumPy Docstring Standard**.

### How to Build the Documentation

```bash
poetry run tox -e docs
```

Open:

```
docs/build/html/index.html
```

Serve locally:

```bash
poetry run python3 -m http.server -d docs/build/html -b 127.1 8090
```

### Pushing Documentation Changes

Docs are built automatically by Read the Docs when changes land on `main`.

---

## Contributing to the Code Base

### Code Standards

- Follow PEP8  
- Use Black and ruff  
- Use absolute imports  
- Use f-strings  

### Pre-commit

Install hooks:

```bash
poetry run pre-commit install
```

### Type Hints

Use PEP 484 type hints.

Validate with:

```bash
poetry run tox -e mypy
```

### Testing With Continuous Integration

Tests run automatically on CI.

### Test-driven Development

Write tests before writing code.  
pyDataverse uses **pytest** and **tox**.

### Running the Test Suite

Using Docker:

```bash
sh run-tests.sh
```

Manual setup requires environment variables:

```
API_TOKEN=SECRET
API_TOKEN_SUPERUSER=SECRET
BASE_URL=http://localhost:8080
DV_VERSION=6.3
```

Run tests:

```bash
poetry run env $(cat local-test.env .env | grep -v '^#' | xargs) tox -e py3
```

Coverage:

```bash
poetry run tox -e coverage
```

---

## Contributing Your Changes

### Committing Your Code

Checklist:

- On the correct branch  
- Tests pass  
- Style checks pass  

Add files:

```bash
git add path/to/file.py
```

Commit:

```bash
git commit
```

### Pushing Your Changes

```bash
git push origin BRANCH_NAME
```

### Review Your Code

Open a pull request via GitHub’s UI.

### Make the Pull Request

Follow the PR template.

### Updating Your Pull Request

```bash
git push origin BRANCH_NAME
```

To merge upstream changes:

```bash
git checkout BRANCH_NAME
git fetch upstream
git merge upstream/develop
```

### Delete Your Merged Branch

```bash
git branch -d BRANCH_NAME
git push origin --delete BRANCH_NAME
```

---

## Tips for a Successful Pull Request

- Reference an open issue  
- Include tests  
- Keep PRs small  
- Ensure CI is green  
- Update your PR regularly  

---

## What Happens After the Pull Request

### Reviewing the Pull Request

Maintainers assign labels, milestones, and reviewers.

### Create a Release

Steps include:

- Define issues and version  
- Create milestone  
- Review and test  
- Write release notes  
- Tag release (e.g., `v0.3.0`)  
- Upload to PyPI and conda-forge  

Semantic versioning is used.

