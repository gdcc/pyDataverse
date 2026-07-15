# Issue #240 — `AsyncLibraryNotFoundError` on Python 3.14 when constructing `Dataverse`

| Field | Value |
| --- | --- |
| Status | Open |
| Labels | `type:bug`, `status:incoming` |
| Reporter | `pdurbin` (with `@liujinjie111`) |
| Affected version | `0.4.0beta1` @ `7f56e21` |
| Environment | Python 3.14.5, macOS |
| Issue URL | https://github.com/gdcc/pyDataverse/issues/240 |
| Analysis commit | `a48ab04` (contains reported commit `7f56e21`) |

---

## 1. Executive summary

On Python 3.14, simply constructing a `Dataverse` object raises:

```
sniffio._impl.AsyncLibraryNotFoundError: unknown async library, or not in async context
```

The crash occurs inside the `Dataverse(...)` **constructor**, not in `create_dataset()` or any later
call. The constructor eagerly prefetches metadata blocks (to pre-build the dataset factory), and that
prefetch drives an async HTTP request through `httpx` / `httpcore` / `anyio` / `sniffio`.

The root cause is `pyDataverse/__init__.py` calling `nest_asyncio.apply()` at import time.
`nest_asyncio` (<= 1.6.0, the currently pinned version) monkey-patches the asyncio event loop using the
`loop=` keyword argument, which was **removed in Python 3.14** (CPython bpo-39529). The patched loop
corrupts asyncio task bookkeeping so that `asyncio.current_task()` returns `None`, which in turn makes
`sniffio` / `anyio` (used transitively by `httpx`) fail to detect the running event loop and raise
`AsyncLibraryNotFoundError`.

Because `nest_asyncio.apply()` is global and every synchronous wrapper in pyDataverse funnels through
`asyncio.run(...)`, the defect is **not** limited to metadata-block prefetch: it affects every sync
entry point that runs a coroutine on Python 3.14. Fixing only `_get_metadata_blocks` is therefore
insufficient.

---

## 2. Reproduction

### 2.1 Preconditions

- Python **3.14** (reproduced on 3.14.5, macOS).
- pyDataverse `0.4.0beta1` (`7f56e21`) installed with its pinned dependencies, notably
  `nest-asyncio` 1.6.0.
- A **reachable** Dataverse instance at the given `base_url`. The constructor performs a live HTTP
  request to fetch metadata blocks; the log line `Fetching metadata blocks...` is emitted immediately
  **before** the crash, confirming the failure happens during the eager prefetch.

### 2.2 Reporter's docs-based script

The reporter followed the "create a dataset" example from the high-level docs:

```python
from pyDataverse import Dataverse

# Connect to your Dataverse installation
dv = Dataverse("https://demo.dataverse.org")   # <-- raises here on Python 3.14

dataset = dv.create_dataset(
    title="My Research Dataset",
    description="A comprehensive dataset ...",
    authors=[{"name": "Jane Smith", "affiliation": "University of Science"}],
    contacts=[{"name": "Jane Smith", "email": "jane.smith@university.edu"}],
    subjects=["Computer and Information Science"],
    collection="my-collection",
)
```

The important observation is that the exception is raised on the `Dataverse(...)` line, **before**
`create_dataset()` is ever reached.

### 2.3 Minimal 2-line repro

```python
from pyDataverse import Dataverse
Dataverse(base_url="https://demo.dataverse.org")  # AsyncLibraryNotFoundError on Python 3.14
```

Running this under Python 3.14 prints `Fetching metadata blocks...` and then raises
`sniffio._impl.AsyncLibraryNotFoundError`.

---

## 3. Observed traceback (annotated)

The signature of this bug is a stack that descends through `asyncio.run(...)`, then through
`nest_asyncio.py`'s patched `run_until_complete`, then into `httpx` -> `httpcore` -> `anyio` ->
`sniffio`, terminating in `AsyncLibraryNotFoundError`. Annotated frame-by-frame and mapped to this
repository:

```text
Traceback (most recent call last):
  File ".../your_script.py", line 3, in <module>
    Dataverse(base_url="https://demo.dataverse.org")
  # pydantic runs the model_validator(mode="after")
  File ".../pyDataverse/dataverse/dataverse.py", line 171, in _setup_api
    self._ensure_factory_initialized()
  File ".../pyDataverse/dataverse/dataverse.py", line 218, in _ensure_factory_initialized
    self._dataset_factory(enum_limit=None)
  File ".../pyDataverse/dataverse/dataverse.py", line 406, in _dataset_factory
    metadata_blocks = asyncio.run(self._get_metadata_blocks())
  # --- nest_asyncio's monkey-patched loop takes over here ---
  File ".../nest_asyncio.py", line ...,  in run
    return loop.run_until_complete(task)
  File ".../nest_asyncio.py", line ...,  in run_until_complete
    ...                                   # patched loop; uses loop= keyword internally
  File ".../pyDataverse/dataverse/dataverse.py", line 708, in _get_metadata_blocks
    results = await asyncio.gather(*tasks)
  File ".../pyDataverse/api/native.py", line 1812, in get_metadatablock
    return self.get_request(url, ..., use_async=self.client is not None, ...)
  File ".../pyDataverse/api/api.py", line 1392, in _async_request
    response: httpx.Response = await method(...)
  # httpx -> httpcore -> anyio -> sniffio
  File ".../sniffio/_impl.py", line ..., in current_async_library
    raise AsyncLibraryNotFoundError(
sniffio._impl.AsyncLibraryNotFoundError: unknown async library, or not in async context
```

Frame mapping:

- **`_setup_api`** — pydantic `@model_validator(mode="after")` that fires during construction.
- **`_ensure_factory_initialized` -> `_dataset_factory`** — eager prefetch of metadata blocks.
- **`asyncio.run(self._get_metadata_blocks())`** — the sync/async boundary.
- **`nest_asyncio.py` frames** — the tell-tale sign. On a healthy interpreter these would be plain
  asyncio frames; here `nest_asyncio`'s patched loop is on the stack.
- **`_get_metadata_blocks` -> `get_metadatablock` -> `_async_request` -> `await method(...)`** — the
  actual `httpx.AsyncClient` request.
- **`sniffio.current_async_library()`** — cannot see the running loop (because
  `asyncio.current_task()` returns `None`) and raises.

---

## 4. Repository architecture

pyDataverse is layered. Synchronous, user-facing classes wrap an async HTTP core:

| Layer | Location | Responsibility |
| --- | --- | --- |
| High-level | `pyDataverse/dataverse/` (`Dataverse`, `Collection`, `Dataset`, `File`, `Metrics`) | Ergonomic, mostly-synchronous object model used in scripts and notebooks |
| Low-level API | `pyDataverse/api/` (`NativeApi`, `SemanticApi`, `MetricsApi`, `DataAccessApi`, `SearchApi`) | Thin wrappers over the Dataverse REST endpoints; own the `httpx` client |
| Models | `pyDataverse/models/` | Pydantic request/response models and metadata-block specifications |
| Filesystem | `pyDataverse/filesystem/` | `fsspec` interface (`DataverseFS`) for file-like access |
| MCP | `pyDataverse/mcp/` | Model Context Protocol server exposing pyDataverse to LLM tooling |

### 4.1 Concurrency model

The library is async underneath but exposes a synchronous surface:

- Each sync wrapper (e.g. `Dataverse._dataset_factory`, `NativeApi.get_datasets`,
  `SemanticApi.get_datasets`, `Metrics.df`, ...) builds a coroutine that opens an
  `httpx.AsyncClient`, issues many requests concurrently via `asyncio.gather`, and closes the client.
- The wrapper then drives that coroutine to completion with **`asyncio.run(...)`**.
- To let those `asyncio.run(...)` calls also work when a loop is *already running* (e.g. inside a
  Jupyter/IPython kernel), the package historically called **`nest_asyncio.apply()`** globally at
  import time. `nest_asyncio` re-enters the running loop instead of raising
  `RuntimeError: asyncio.run() cannot be called from a running event loop`.

This global monkey-patch is exactly what breaks on Python 3.14.

---

## 5. Exact failure path (verified)

Construction triggers the pydantic after-validator, which pre-initializes the dataset factory:

```170:189:pyDataverse/dataverse/dataverse.py
    @model_validator(mode="after")
    def _setup_api(self) -> Self:
        """
        Initialize the NativeApi instance after model validation.

        This validator runs after all field validation is complete and sets up
        the internal API client using the provided base_url and api_token.
        It also pre-initializes the dataset factory to prevent race conditions
        when multiple async operations try to fetch datasets simultaneously.

        Returns:
            Self: The validated Dataverse instance
        """
        # Check compatibility with the API version
        self._check_api_version()
        # Only setup APIs if they haven't been initialized yet
        self._ensure_apis_initialized()
        # Pre-initialize the factory to prevent race conditions in async operations
        self._ensure_factory_initialized()
        return self
```

`_ensure_factory_initialized` calls the factory eagerly (this is what turns a lazy prefetch into a
constructor-time network call):

```205:219:pyDataverse/dataverse/dataverse.py
    def _ensure_factory_initialized(self) -> None:
        """
        Ensure the dataset factory is initialized to prevent race conditions.

        This method uses a lock to ensure only one thread initializes the factory
        at a time, preventing concurrent async operations from competing.
        """
        if not self._factory_initialized:
            with self._factory_lock:
                # Double-check pattern: another thread might have initialized it
                if not self._factory_initialized:
                    # Pre-initialize the factory with default enum_limit
                    # This populates the cache and prevents race conditions
                    self._dataset_factory(enum_limit=None)
                    self._factory_initialized = True
```

The factory crosses the sync/async boundary with `asyncio.run`:

```404:406:pyDataverse/dataverse/dataverse.py
        self.native_api.logger.info("Fetching metadata blocks...")

        metadata_blocks = asyncio.run(self._get_metadata_blocks())
```

The coroutine opens the async client and fans out with `asyncio.gather`:

```703:714:pyDataverse/dataverse/dataverse.py
        native_api = self.native_api  # Use property to ensure initialization
        blocks = [block.name for block in native_api.get_metadatablocks(full=False)]
        try:
            native_api._setup_async_client()
            tasks = [native_api.get_metadatablock(block) for block in blocks]
            results: List[MetadatablockSpecification] = await asyncio.gather(*tasks)  # type: ignore
            return {block.name: block for block in results}
        except Exception as e:
            native_api.client = None
            raise e
        finally:
            native_api.client = None
```

`get_metadatablock` routes to the async request path because `self.client` is now set
(`use_async=self.client is not None`):

```1811:1817:pyDataverse/api/native.py
        url = self._assemble_url(f"metadatablocks/{identifier}")
        return self.get_request(
            url,
            auth=self.auth,
            use_async=self.client is not None,
            response_model=metadatablocks.MetadatablockSpecification,
        )
```

Finally, the low-level async request `await`s the `httpx` call, which reaches `sniffio` and fails:

```1391:1397:pyDataverse/api/api.py
        try:
            response: httpx.Response = await method(
                **kwargs,
                auth=self.auth,
                follow_redirects=follow_redirects,
                timeout=self.timeout,
            )
```

---

## 6. Root cause deep dive

### 6.1 Where it starts

```13:13:pyDataverse/__init__.py
import nest_asyncio
```

```28:28:pyDataverse/__init__.py
nest_asyncio.apply()
```

`nest_asyncio.apply()` runs unconditionally at import — i.e. the moment a user does
`from pyDataverse import Dataverse`.

### 6.2 The 5-step causal chain

1. **Import-time patch.** `pyDataverse/__init__.py` calls `nest_asyncio.apply()`, which monkey-patches
   the asyncio event loop / policy so nested `run_until_complete` calls are allowed.
2. **Removed `loop=` keyword.** `nest_asyncio` (<= 1.6.0) implements its patch using the `loop=`
   keyword argument on asyncio primitives. **Python 3.14 removed the long-deprecated `loop=`
   parameter** (CPython bpo-39529), so the patched machinery no longer registers tasks correctly.
3. **Broken task registration.** With the corrupted loop, asyncio's per-loop "current task" bookkeeping
   is not populated, so `asyncio.current_task()` returns `None` while a coroutine is actually running.
4. **Loop detection fails.** `sniffio.current_async_library()` (used by `anyio`, which backs
   `httpx`/`httpcore`) relies on being able to detect the running asyncio loop/task. Seeing no current
   task, it concludes there is no async library in use.
5. **Exception.** `sniffio` raises `AsyncLibraryNotFoundError: unknown async library, or not in async
   context`, which propagates up through `httpcore` -> `httpx` -> `_async_request` -> `asyncio.run` ->
   the `Dataverse` constructor.

### 6.3 Python 3.14 specifics

- CPython bpo-39529 completed the multi-release deprecation of the `loop=` parameter; it is fully
  removed in 3.14. Libraries that still pass `loop=` (directly or via monkey-patching) break.
- `nest_asyncio` is effectively unmaintained (see references), so it has not been updated for the 3.14
  loop changes.

### 6.4 Why this is cross-ecosystem

This is a known break beyond pyDataverse:

- **Chainlit** hit the same `nest_asyncio` + Python 3.14 failure (Chainlit issue #2952).
- **semanticscholar** removed `nest_asyncio` entirely in favor of a thread-based runner
  (semanticscholar PR #116) — the same shape of fix proposed below.
- **IPython/ipykernel** discussed `nest_asyncio` being unmaintained and problematic (ipykernel #1381).

---

## 7. Impact / blast radius

Every synchronous wrapper that calls `asyncio.run(...)` is affected on Python 3.14. Verified call
sites across `pyDataverse/`:

| File | Line | Sync entry point |
| --- | --- | --- |
| `pyDataverse/dataverse/dataverse.py` | 406 | `Dataverse._dataset_factory` (invoked from the constructor via `_ensure_factory_initialized`) |
| `pyDataverse/api/native.py` | 503 | `NativeApi.get_datasets` |
| `pyDataverse/api/native.py` | 2144 | `NativeApi.crawl_collection` |
| `pyDataverse/api/semantic.py` | 278 | `SemanticApi.get_datasets` |
| `pyDataverse/dataverse/collection.py` | 627 | `Collection.graph` |
| `pyDataverse/dataverse/metrics.py` | 85 | `Metrics._serialize_metrics` |
| `pyDataverse/dataverse/metrics.py` | 155 | `Metrics.df` |
| `pyDataverse/dataverse/metrics.py` | 312 | `Metrics.dict` (and therefore `Metrics.json`) |
| `pyDataverse/dataverse/dataset.py` | 487 | `Dataset.graph` |
| `pyDataverse/mcp/server.py` | 304 | `McpServer._all_metadatablocks` |

**Severity: High for Python 3.14.** The very first, unavoidable action a user takes —
`Dataverse(base_url=...)` — fails, so the library is essentially unusable on 3.14. Because the same
`nest_asyncio` corruption underlies all of the sites above, **patching only `_get_metadata_blocks`
would move the crash to the next `asyncio.run` a user hits** (e.g. `get_datasets`, `graph`, metrics)
rather than fixing the library. The fix must remove the global `nest_asyncio.apply()` and replace the
runner uniformly.

Python 3.10–3.13 are unaffected because `nest_asyncio` still functions there.

---

## 8. Solution

### 8.1 Add a shared `run_async` helper

Introduce a single, loop-aware coroutine runner and route every sync wrapper through it. Proposed new
module `pyDataverse/api/utilities/async_run.py`:

```python
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
    """
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        # No running loop in this thread: safe to drive the coroutine directly.
        return asyncio.run(coro)

    # A loop is already running in this thread. We cannot call asyncio.run here,
    # so run the coroutine on a fresh loop inside a dedicated worker thread.
    return _EXECUTOR.submit(asyncio.run, coro).result()
```

**Why the thread offload is correct here.** The dangerous pattern would be creating an
`httpx.AsyncClient` bound to loop A and then awaiting it on loop B. That does **not** happen in
pyDataverse, because the async client is always created **inside the coroutine body** that
`run_async` will drive:

- `Dataverse._get_metadata_blocks` calls `native_api._setup_async_client()` inside the coroutine (see
  §5, lines 703–714), so the client is created on whichever loop ends up running the coroutine.
- `SemanticApi._get_datasets` uses `async with self:` to enter/create the client context inside the
  coroutine:

```284:323:pyDataverse/api/semantic.py
    async def _get_datasets(
        self,
        identifiers: Sequence[str | int],
        batch_size: int,
    ) -> Sequence[Dict[str, Any]]:
        ...
        async with self:
            results = []
```

Because the client is created within the coroutine, when `run_async` offloads to the worker thread the
client is bound to that worker's fresh loop — everything (create, use, close) happens on one loop.
That is what makes the thread offload safe.

**Tradeoff.** With `max_workers=1`, synchronous calls made from inside an already-running loop are
serialized onto a single background loop. This keeps semantics simple and avoids client/loop mismatch;
it does not affect the common script path (no running loop), which continues to use `asyncio.run`
directly. If higher parallelism from within running loops is ever required, the worker count can be
revisited, but single-worker is the safe default.

### 8.2 Remove the global `nest_asyncio` patch

Delete both lines from `pyDataverse/__init__.py`:

```python
# remove:
import nest_asyncio
# remove:
nest_asyncio.apply()
```

### 8.3 Replace every `asyncio.run(...)` call site

Route each verified site (§7) through the new helper. For example, in
`pyDataverse/dataverse/dataverse.py`:

```python
from pyDataverse.api.utilities.async_run import run_async

# before:
metadata_blocks = asyncio.run(self._get_metadata_blocks())
# after:
metadata_blocks = run_async(self._get_metadata_blocks())
```

Apply the same substitution at all sites:

- `pyDataverse/dataverse/dataverse.py:406`
- `pyDataverse/api/native.py:503` and `:2144`
- `pyDataverse/api/semantic.py:278`
- `pyDataverse/dataverse/collection.py:627`
- `pyDataverse/dataverse/metrics.py:85`, `:155`, `:312`
- `pyDataverse/dataverse/dataset.py:487`
- `pyDataverse/mcp/server.py:304`

### 8.4 Remove the dependency and regenerate the lockfile

Delete the pin from `pyproject.toml`:

```toml
# remove from [project].dependencies:
"nest-asyncio>=1.6.0,<2.0.0",
```

Then regenerate the lockfile and confirm nothing still imports it:

```bash
uv lock
rg -n "nest_asyncio|nest-asyncio"   # expect: no matches anywhere in the repo
```

---

## 9. CI changes

Current test matrix:

```1:20:.github/workflows/tests.yml
name: Unit tests
on: [push]

jobs:
  custom_test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12", "3.13"]
    name: Test pyDataverse
    env:
      PORT: 8080
    steps:
      - name: Checkout
        uses: actions/checkout@v5

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
```

Proposed matrix (add 3.14 so the regression is guarded going forward):

```yaml
    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12", "3.13", "3.14"]
```

**Caveat.** Before enabling 3.14 in CI, verify that 3.14 wheels are available for the heavier
dependencies — notably `pandas`, `pymupdf`, and `fastmcp` (the last two live in the `mcp` extra, which
CI installs via `uv pip install --system ".[tests,mcp]"`). If any 3.14 wheels are missing, either wait
for upstream releases or gate the `mcp` extra on 3.14 (for example, run the `mcp` portion only on
<= 3.13 until wheels land) so the 3.14 job does not fail on unrelated build issues.

---

## 10. Verification plan

### 10.1 Automated regression test (both paths)

`pyproject.toml` already enables the two facts this test relies on (both verified):

- `asyncio_mode = "auto"` under `[tool.pytest.ini_options]` (line 67), so `async def` tests run
  without an explicit marker.
- `pytest-asyncio>=1.3.0,<2.0.0` is in the `tests` extra (line 33).

Add a test that exercises **both** code paths of `run_async`:

```python
import asyncio

import pytest

from pyDataverse import Dataverse

BASE_URL = "https://demo.dataverse.org"  # or the CI-provided BASE_URL


def test_construct_dataverse_no_running_loop():
    """Script path: no running loop -> run_async uses asyncio.run directly.

    Regression for issue #240: on Python 3.14 this constructor previously raised
    AsyncLibraryNotFoundError due to nest_asyncio.
    """
    dv = Dataverse(base_url=BASE_URL)
    assert len(dv.metadatablocks) > 0


async def test_construct_dataverse_inside_running_loop():
    """Running-loop path: a live loop is active -> run_async offloads to a worker thread.

    asyncio_mode="auto" makes this coroutine run inside an active event loop, so the
    synchronous Dataverse constructor is invoked while a loop is running.
    """
    assert asyncio.get_running_loop() is not None
    dv = Dataverse(base_url=BASE_URL)
    assert len(dv.metadatablocks) > 0
```

The first test covers the common `asyncio.run` branch; the second, because `asyncio_mode="auto"` runs
it inside an active loop, forces the `run_async` thread-offload branch.

### 10.2 Manual verification matrix

| Scenario | Before fix | After fix |
| --- | --- | --- |
| Python 3.13, script (no running loop) | works | works |
| Python 3.13, sync call from running loop (e.g. notebook) | works (via nest_asyncio) | works (via thread offload) |
| Python 3.14, script (no running loop) | **fails** (`AsyncLibraryNotFoundError`) | works |
| Python 3.14, sync call from running loop | **fails** (`AsyncLibraryNotFoundError`) | works |

### 10.3 Exact shell commands

Reproduce and then confirm the fix:

```bash
# 1. Reproduce on Python 3.14 (expect AsyncLibraryNotFoundError before the fix)
python3.14 -c 'from pyDataverse import Dataverse; Dataverse(base_url="https://demo.dataverse.org")'

# 2. Confirm nest_asyncio is fully removed from the codebase
rg -n "nest_asyncio|nest-asyncio"    # expect no matches

# 3. Install with test + mcp extras and run the full suite
uv pip install --system ".[tests,mcp]" && pytest -vv
```

---

## 11. Alternatives considered

- **Pin or monkey-patch `nest_asyncio`.** Rejected. `nest_asyncio` is unmaintained and its whole
  approach relies on the removed `loop=` keyword; there is no forward-compatible pin, and hand-patching
  it would be fragile across CPython versions.
- **Pin `requires-python` to `<3.14`.** An interim stopgap only. It keeps the current release
  installable for now but does not fix the bug and blocks 3.14 users; it should not be the final
  resolution.
- **Go async-first (expose native async APIs).** A good longer-term roadmap item, but a much larger
  change than warranted for this bug; the sync surface must keep working regardless.
- **`asyncer.syncify` / `anyio.from_thread`.** Worth noting because `asyncer` is **already a
  dependency** (`asyncer>=0.0.10,<0.0.11`, verified in `pyproject.toml` line 21, and `anyio` comes in
  transitively via `httpx`). These provide sync/async bridging primitives and could back `run_async`
  internally. The hand-rolled `ThreadPoolExecutor` helper in §8.1 was chosen for its explicitness and
  zero new dependencies, but an `asyncer`/`anyio`-based implementation is a reasonable equivalent.

---

## 12. Interim user workaround

Until the fix is released, use **Python 3.10, 3.11, 3.12, or 3.13**, where `nest_asyncio` still
functions and the constructor works normally. Avoid Python 3.14 with the current `0.4.0beta1` release.

---

## 13. Acceptance criteria

- [ ] `Dataverse(base_url=...)` constructs successfully on Python 3.14 (script path).
- [ ] Sync pyDataverse calls work when invoked from inside an already-running event loop on 3.14.
- [ ] `import nest_asyncio` and `nest_asyncio.apply()` removed from `pyDataverse/__init__.py`.
- [ ] `nest-asyncio` removed from `pyproject.toml` dependencies and `uv.lock` regenerated.
- [ ] `rg -n "nest_asyncio|nest-asyncio"` returns no matches.
- [ ] All verified `asyncio.run(...)` sites (§7) routed through `run_async`.
- [ ] New regression test covers both the no-loop and running-loop paths and passes on 3.13 and 3.14.
- [ ] CI matrix includes `3.14` (with the `mcp`/wheel caveat resolved).
- [ ] Existing test suite passes on all supported Python versions.

---

## 14. References

- Issue #240 — https://github.com/gdcc/pyDataverse/issues/240
- Chainlit #2952 (`nest_asyncio` + Python 3.14) — https://github.com/Chainlit/chainlit/issues/2952
- semanticscholar PR #116 (removed `nest_asyncio` for a thread-based runner) —
  https://github.com/danielnsilva/semanticscholar/pull/116
- ipython/ipykernel #1381 (`nest_asyncio` unmaintained) —
  https://github.com/ipython/ipykernel/issues/1381
- CPython bpo-39529 (removal of the `loop=` parameter) — https://bugs.python.org/issue39529

---

## 15. Verification log (appendix)

All references were verified against the checkout at commit `a48ab04`. **No line-number corrections
were required — every location stated in the source request matched the actual code.**

| Item | Prompt-stated location | Verified location | Result |
| --- | --- | --- | --- |
| `import nest_asyncio` | `pyDataverse/__init__.py` | line 13 | confirmed |
| `nest_asyncio.apply()` | `pyDataverse/__init__.py` | line 28 | confirmed |
| `requires-python = ">=3.10,<4.0"` | `pyproject.toml` | line 7 | confirmed |
| `nest-asyncio>=1.6.0,<2.0.0` | `pyproject.toml` | line 18 | confirmed |
| `asyncer>=0.0.10,<0.0.11` | `pyproject.toml` | line 21 | confirmed |
| `sniffio>=1.3.1,<2.0.0` | `pyproject.toml` | line 24 | confirmed |
| `pytest-asyncio>=1.3.0,<2.0.0` | `pyproject.toml` (tests extra) | line 33 | confirmed |
| `asyncio_mode = "auto"` | `pyproject.toml` | line 67 | confirmed |
| `_setup_api` model_validator | ~170–189 | 170–189 | confirmed |
| `_ensure_factory_initialized` | ~205–219 | 205–219 | confirmed |
| `asyncio.run(self._get_metadata_blocks())` | ~404–406 | line 406 | confirmed |
| `_get_metadata_blocks` body | ~703–714 | 703–714 | confirmed |
| `await method(...)` in `_async_request` | ~1391–1397 | 1391–1397 | confirmed |
| `get_metadatablock` `use_async=...` | ~1811–1817 | 1811–1817 | confirmed |
| `asyncio.run` — `NativeApi.get_datasets` | native.py:503 | line 503 | confirmed |
| `asyncio.run` — `NativeApi.crawl_collection` | native.py:2144 | line 2144 | confirmed |
| `asyncio.run` — `SemanticApi.get_datasets` | semantic.py:278 | line 278 | confirmed |
| `SemanticApi._get_datasets` `async with self:` | semantic.py | line 323 (def at 284) | confirmed |
| `asyncio.run` — `Collection.graph` | collection.py:627 | line 627 | confirmed |
| `asyncio.run` — `Metrics._serialize_metrics` | metrics.py:85 | line 85 (def at 78) | confirmed |
| `asyncio.run` — `Metrics.df` | metrics.py:155 | line 155 (def at 143) | confirmed |
| `asyncio.run` — `Metrics.dict` | metrics.py:312 | line 312 (def at 308) | confirmed |
| `asyncio.run` — `Dataset.graph` | dataset.py:487 | line 487 (def at 429) | confirmed |
| `asyncio.run` — `McpServer._all_metadatablocks` | mcp/server.py:304 | line 304 (def at 297) | confirmed |
| CI matrix `["3.10","3.11","3.12","3.13"]` | `.github/workflows/tests.yml` | line 9 | confirmed (no 3.14) |
| `nest_asyncio` usages repo-wide | `__init__.py`, `pyproject.toml`, `uv.lock` | `__init__.py` (13, 28), `pyproject.toml` (18), `uv.lock` (1292–1297, 1934, 1975) | confirmed (only these) |
