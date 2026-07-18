"""Loop-aware synchronous runner for pyDataverse coroutines.

This replaces the previous global ``nest_asyncio.apply()`` approach, which breaks on
Python 3.14 (the ``loop=`` keyword removed in CPython bpo-39529).
"""

from __future__ import annotations

import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Coroutine, TypeVar

T = TypeVar("T")

# Single worker so nested/concurrent sync calls from within a running loop are
# serialized onto one dedicated background loop.
_EXECUTOR = ThreadPoolExecutor(max_workers=1, thread_name_prefix="pyDataverse-async")


def run_async(coro: "Coroutine[Any, Any, T]") -> T:
    """Run *coro* to completion from synchronous code.

    - If there is no running event loop, use ``asyncio.run`` directly.
    - If a loop is already running (e.g. Jupyter/IPython or an async caller),
      offload the coroutine to a dedicated worker thread that runs it on a fresh
      event loop via ``asyncio.run``.

    Correctness constraint: the coroutine must create and await its own
    event-loop-bound resources (e.g. an ``httpx.AsyncClient``) *inside* the
    coroutine body. Because the thread-offload path runs the coroutine on a
    fresh loop in the worker thread, any resource created on a different loop
    and then awaited here would fail. pyDataverse satisfies this because every
    sync wrapper creates its async client within the coroutine that is passed
    to ``run_async``.
    """
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        # No running loop in this thread: safe to drive the coroutine directly.
        return asyncio.run(coro)

    # A loop is already running in this thread. We cannot call asyncio.run here,
    # so run the coroutine on a fresh loop inside a dedicated worker thread.
    return _EXECUTOR.submit(asyncio.run, coro).result()
