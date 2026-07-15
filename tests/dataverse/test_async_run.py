"""Regression tests for issue #240 and the ``run_async`` helper.

Issue #240: on Python 3.14 constructing a ``Dataverse`` raised
``sniffio._impl.AsyncLibraryNotFoundError`` because ``nest_asyncio.apply()`` was
called at import time and ``nest_asyncio`` relies on the ``loop=`` keyword that
CPython removed in 3.14. The fix replaces the global ``nest_asyncio`` patch with
the loop-aware :func:`pyDataverse.api.utilities.async_run.run_async` runner.

These tests exercise BOTH code paths of ``run_async``:

- the *no running loop* (script) path, which drives the coroutine with
  ``asyncio.run`` directly, and
- the *running loop* path, which offloads the coroutine to a dedicated worker
  thread running a fresh event loop.

The direct ``run_async`` unit tests need no network. The integration-style
``Dataverse`` construction tests need a live Dataverse instance and are skipped
cleanly when ``BASE_URL``/``API_TOKEN`` are not set.
"""

import asyncio
import os
import threading

import pytest

from pyDataverse import Dataverse
from pyDataverse.api.utilities.async_run import run_async

BASE_URL = os.environ.get("BASE_URL", "https://demo.dataverse.org")
API_TOKEN = os.environ.get("API_TOKEN")

_requires_server = pytest.mark.skipif(
    not os.environ.get("BASE_URL"),
    reason="Requires a live Dataverse instance (set BASE_URL/API_TOKEN).",
)


# --------------------------------------------------------------------------- #
# Direct unit tests of run_async (no network required).
# --------------------------------------------------------------------------- #


def test_run_async_no_running_loop_returns_result():
    """Script path: with no running loop, run_async uses asyncio.run directly."""

    async def _coro() -> int:
        return 21 + 21

    assert run_async(_coro()) == 42


def test_run_async_no_running_loop_runs_on_calling_thread():
    """Without a running loop the coroutine runs on the calling thread."""
    main_thread_id = threading.get_ident()

    async def _coro() -> int:
        return threading.get_ident()

    assert run_async(_coro()) == main_thread_id


async def test_run_async_inside_running_loop_returns_result():
    """Running-loop path: asyncio_mode="auto" runs this inside an active loop.

    run_async must detect the running loop and offload the coroutine to the
    dedicated worker thread instead of raising
    ``RuntimeError: asyncio.run() cannot be called from a running event loop``.
    """
    assert asyncio.get_running_loop() is not None

    async def _coro() -> int:
        return 21 + 21

    assert run_async(_coro()) == 42


async def test_run_async_inside_running_loop_uses_worker_thread():
    """Inside a running loop the coroutine is offloaded to a worker thread."""
    assert asyncio.get_running_loop() is not None
    main_thread_id = threading.get_ident()

    async def _coro() -> int:
        return threading.get_ident()

    worker_thread_id = run_async(_coro())
    assert worker_thread_id != main_thread_id


# --------------------------------------------------------------------------- #
# Integration-style regression tests (require a live Dataverse instance).
# --------------------------------------------------------------------------- #


@_requires_server
def test_construct_dataverse_no_running_loop():
    """Script path: no running loop -> run_async uses asyncio.run directly.

    Regression for issue #240: on Python 3.14 this constructor previously raised
    AsyncLibraryNotFoundError due to nest_asyncio.
    """
    dv = Dataverse(base_url=BASE_URL, api_token=API_TOKEN)
    assert len(dv.metadatablocks) > 0


@_requires_server
async def test_construct_dataverse_inside_running_loop():
    """Running-loop path: a live loop is active -> run_async offloads to a worker thread.

    asyncio_mode="auto" makes this coroutine run inside an active event loop, so the
    synchronous Dataverse constructor is invoked while a loop is running.
    """
    assert asyncio.get_running_loop() is not None
    dv = Dataverse(base_url=BASE_URL, api_token=API_TOKEN)
    assert len(dv.metadatablocks) > 0
