ARG PYTHON_VERSION=3.11
FROM python:${PYTHON_VERSION}-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install pyDataverse with all optional extras from this repository.
COPY pyproject.toml README.md /app/
COPY pyDataverse /app/pyDataverse
COPY tests /app/tests
RUN python -m pip install --upgrade pip && \
    python -m pip install uv && \
    uv pip install --system ".[tests,mcp]"

# Run tests by default.
CMD ["pytest", "-v"]
