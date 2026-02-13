# pyDataverse

[![PyPI](https://img.shields.io/pypi/v/pyDataverse.svg)](https://pypi.org/project/pyDataverse/)
[![Conda Version](https://img.shields.io/conda/vn/conda-forge/pydataverse.svg)](https://anaconda.org/conda-forge/pydataverse/)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://pypi.org/project/pyDataverse/)
[![GitHub](https://img.shields.io/github/license/gdcc/pydataverse.svg)](https://opensource.org/licenses/MIT)

pyDataverse is a Python client library for [Dataverse](https://dataverse.org). It gives you a modern, Pythonic interface to work with Dataverse collections, datasets, and files without dealing with raw HTTP requests for common workflows.

Read the full documentation: [pydataverse.readthedocs.io](https://pydataverse.readthedocs.io/en/latest/)

## Why pyDataverse

- **High-level workflow API** for connecting to instances, browsing collections, and managing datasets/files
- **Low-level API access** when you need direct control over Dataverse endpoints
- **Metadata-friendly dataset creation** with helpers for common citation and subject fields
- **Filesystem-style file operations** using familiar `open()` and context manager patterns
- **Optional MCP integration** for tool-based workflows and agent interoperability

## Installation

Use Python 3.10+ and install in a virtual environment.
Choose one package manager (`pip`, `uv`, or `poetry`) for a given environment.

```bash
python -m venv .venv
source .venv/bin/activate
```

### pip

Install from PyPI:

```bash
python -m pip install pyDataverse
```

Install from local source (repository checkout):

```bash
python -m pip install .
```

Install with test dependencies:

```bash
python -m pip install ".[tests]"
```

### uv

Install from PyPI:

```bash
uv pip install pyDataverse
```

Install from local source (repository checkout):

```bash
uv pip install .
```

Install with test dependencies:

```bash
uv sync --extra tests
```

### poetry

Install runtime dependencies:

```bash
poetry install
```

Install with test dependencies:

```bash
poetry install --extras tests
```

## Quickstart (High-Level API)

These examples follow the current high-level API usage shown in the docs.

### 1) Connect, get a collection, create a dataset

```python
from pyDataverse import Dataverse

dv = Dataverse(base_url="https://demo.dataverse.org")
collection = dv.collections["my_collection"]

dataset = collection.create_dataset(
    title="My Dataset Title",
    description="Short dataset description",
    authors=authors,
    contacts=contacts,
    subjects=["Computer Science"],
)

# Add metadata to the dataset
dataset["citation"]["subtitle"] = "Subtitle for my dataset"
dataset["otherBlock"]["otherField"] = "Other value"

dataset.update_metadata()

# Upload a file to the dataset
with dataset.open("data/example.txt", mode="w") as f:
    f.write("Hello, world!")

dataset.publish()
dataset.open_in_browser()
```

This connects to the demo instance, selects one collection, and prepares a dataset locally so you can refine metadata and files before uploading.

### 2) Connect from DOI URL, fetch dataset, read a file with `with`

```python
from pyDataverse.dataverse.dataset import Dataset

DOI_URL = "https://doi.org/10.18419/DARUS-5539"
dataverse, dataset = Dataset.from_doi_url(DOI_URL)

with dataset.open("data/example.txt", mode="r") as f:
    text = f.read()
```

This resolves the Dataverse and dataset directly from a DOI URL, then reads a dataset file using the safe `with` context manager pattern.

## Running tests

To run local `pyDataverse` tests against a self-hosted Dataverse instance:

1. Clone Dataverse: <https://github.com/IQSS/dataverse>
2. Optionally check out a specific release tag, or use `develop`
3. Start Dataverse containers from the Dataverse repo (see: <https://guides.dataverse.org/en/latest/container/dev-usage.html>)

Example in the Dataverse repository:

```bash
docker compose -f docker-compose-dev.yml up -d
```

Then run `pyDataverse` tests from this repository using the simple test runner:

```bash
export BASE_URL=http://localhost:8080
export API_TOKEN=<your_api_token>
# Optional (defaults to API_TOKEN)
export API_TOKEN_SUPERUSER=<your_superuser_token>
# Optional (defaults to 3.11)
export PYTHON_VERSION=3.12

./run-tests.sh
```

`run-tests.sh` builds the local test image and runs `pytest` in a container. If `BASE_URL` uses `localhost` or `127.0.0.1`, it is automatically mapped for container access to your host Dataverse instance.

For detailed Dataverse container development workflows, see:

- Dataverse repo: <https://github.com/IQSS/dataverse>
- Dev container usage: <https://guides.dataverse.org/en/latest/container/dev-usage.html>

## Chat with us

If you are interested in the development of pyDataverse, we invite you to join us for a chat on our [Zulip Channel](https://dataverse.zulipchat.com/#narrow/stream/377090-python). This is the perfect place to discuss and exchange ideas about the development of pyDataverse. Whether you need help or have ideas to share, feel free to join us!

## PyDataverse Working Group

We have formed a [pyDataverse working group](https://py.gdcc.io) to exchange ideas and collaborate on pyDataverse. There is a bi-weekly meeting planned for this purpose, and you are welcome to join us by clicking the following [WebEx meeting link](https://unistuttgart.webex.com/unistuttgart/j.php?MTID=m322473ae7c744792437ce854422e52a3). For a list of all the scheduled dates, please refer to the [Dataverse Community calendar](https://calendar.google.com/calendar/embed?src=c_udn4tonm401kgjjre4jl4ja0cs%40group.calendar.google.com&ctz=America%2FNew_York).
