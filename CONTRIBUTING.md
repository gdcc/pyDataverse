# pyDataverse – Developer Onboarding Guide

Welcome to the `pyDataverse` development team. This guide walks you through everything you need to start contributing confidently: environment setup, tooling, workflows, testing, documentation, and contribution standards.

---

## 🌱 1. Prerequisites

Before you begin, ensure you have:

- Python 3.12+
- Poetry ≥ 2.1.1
- Git
- Make (optional but recommended)
- A GitHub account (for contributing)

Check your versions:

```bash
python3 --version
poetry --version
git --version
```

## 📦 2. Clone the Repository

```bash
git clone https://github.com/gdcc/pyDataverse.git
cd pyDataverse
```

## 🛠️ 3. Install Dependencies

Install everything using Poetry:

```bash
poetry install
```

Activate the virtual environment:

```bash
poetry shell
```

This installs:

- Runtime dependencies (requests)
- Development tools (pytest, ruff, black, mypy, pyright, sphinx, etc.)

## 🧭 4. Project Structure

```plain
pyDataverse/
├── src/
│   └── pyDataverse/
│       ├── api/
│       │   ├── client.py
│       │   ├── transport.py
│       │   ├── exceptions.py
│       │   └── endpoints/
│       │       ├── datasets.py
│       │       ├── files.py
│       │       ├── search.py
│       │       └── info.py
│       └── ...
├── tests/
│   ├── unit/
│   ├── system/ (optional)
│   └── integration/ (optional)
├── pyproject.toml
└── Makefile
```

Key ideas:

- `src/` contains all library code
- `tests/` mirrors the structure of src
- `docs/` contains Sphinx documentation
- `Makefile` provides shortcuts for common tasks

## 🧪 5. Running Tests

Run all tests:

```bash
make test
```

Or directly:

```bash
poetry run pytest
```

Run with coverage:

```bash
make coverage
```

## 🧹 6. Linting & Formatting

The project uses:

- Ruff (linting)
- Black (formatting)
- Mypy + Pyright (type checking)

Run all linters:

```bash
make lint
```

Auto‑format:

```bash
make format
```

Type checking:

```bash
make typecheck
```

## 🔁 7. Git Workflow

### Branching

Use feature branches:

```bash
feature/<short-description>
bugfix/<issue-number>
refactor/<area>
```

Example:

```bash
feature/add-dataset-versioning
```

### Commit messages

Follow conventional commits:

```bash
feat: add dataset version retrieval
fix: correct file upload metadata handling
refactor: simplify HttpClient retry logic
test: add tests for search endpoint
docs: update API usage examples
```

### Pull Requests

A good PR includes:

- A clear description
- Tests for new or changed behavior
- Passing CI (lint, typecheck, tests)
- Updated documentation if needed

## 🧭 8. Coding Standards

- Follow PEP 8 (enforced by Ruff + Black)
- Use type hints everywhere
- Keep modules small and focused
- Prefer composition over inheritance
- Write tests for every endpoint and transport change
- Avoid side effects in constructors
- Keep public APIs stable and documented

## 🧪 9. Testing Philosophy

- Unit tests should mock all network calls
- Integration tests (optional) can target a real Dataverse instance
- Tests should be deterministic and fast
- Aim for 90%+ coverage on new code
- Use fixtures for repeated setup

## 🧱 10. Adding a New Endpoint

- Create a new file in src/pyDataverse/api/endpoints/
- Implement a class following the existing pattern:
    - Constructor receives HttpClient
    - Methods call self.http.get/post/put/delete
    - Return parsed JSON
- Add unit tests in tests/unit/
- Add documentation in docs/
- Add a convenience method in client.py if appropriate

🚀 12. Releasing a New Version

- Update version in pyproject.toml
- Update CHANGELOG.md
- Run full checks:

```bash
make format
make lint
make typecheck
make test
```

Commit and tag:

```bash
git tag v0.3.6
git push --tags
```

Publish via Poetry:

```bash
poetry publish --build
```

## 🤝 12. Getting Help

If you're stuck:

- Open a GitHub issue
- Ask maintainers
- Check existing tests
- Review the Dataverse API docs

## 🎉 Welcome aboard

This project has a clean architecture, strong tooling, and a friendly workflow.
Once you get into the rhythm — write code, run tests, lint, typecheck, document — contributing becomes smooth and enjoyable.
