# Issue #241 — `TypeError: issubclass() arg 1 must be a class` when using `"identifier_scheme": "ORCID"`

| Field | Value |
| --- | --- |
| Status | Fixed on branch `fix/241-identifier-scheme-issubclass` (verification complete) |
| Labels | `type:bug`, `status:incoming` |
| Reporter | `pdurbin` (with `@liujinjie111`) |
| Affected version | `0.4.0beta1` @ `7f56e21` (also reproduced on later local tree) |
| Environment | Python 3.13 / 3.14; any OS; any reachable Dataverse for metadata schema fetch |
| Issue URL | https://github.com/gdcc/pyDataverse/issues/241 |
| Docs / example | https://gdcc.github.io/pyDataverse/high-level/dataverse/ |
| Local verification commit | `f3765cc` (workspace tree used for analysis) |
| Local package path | `/Users/shihuayu/Documents/GitHub/pyDataverse/pyDataverse` |
| How to implement | Follow §8 Steps 0–7 in order; every fix must pass §10.6 acceptance criteria |
| Multi-agent mode | See §8.0 for parallel split; verification remains mandatory |
| HTML verification report | `docs/issues/241-identifier-scheme-fix-verification.html` |

---

## 1. Executive summary

Creating a dataset with an author that includes the optional controlled-vocabulary field
`"identifier_scheme": "ORCID"` raises:

```text
TypeError: issubclass() arg 1 must be a class
```

The crash does **not** happen while assigning the author dict into the citation metadata block.
It happens later, when the dataset is converted into the Dataverse create payload —
`Dataset.to_dataverse_create_dict()` → `MetadataBlockBase.to_metadata_block()` →
`CompoundField.to_metadata_fields()` → `MetadataBlockBase._process_field_value()`.

Root cause:

1. Controlled-vocabulary (CV) fields are modeled as
   `Optional[Annotated[str, AfterValidator(...)]]` in
   `pyDataverse/dataverse/connect/builder.py`.
2. Nested CV fields such as `authorIdentifierScheme` therefore have a non-class
   `field_info.dtype` after optional unwrapping (`Annotated[...]`).
3. `_process_field_value()` calls `issubclass(field_info.dtype, CompoundField)` **without**
   checking `isinstance(dtype, type)` first.
4. Python raises `TypeError` because `issubclass()` requires arg 1 to be a class.

This is **not ORCID-specific**. Any non-empty controlled-vocabulary child field inside a compound
field triggers the same failure (verified with `contributor.contributorType`). Omitting the field
“works” only because empty values are skipped before `_process_field_value` runs, which is why the
reporter can create a dataset without Identifier Type.

---

## 2. Reporter symptoms (verbatim behavior)

### 2.1 What the reporter did

Followed the high-level “create dataset” docs and used:

```python
authors=[
    {
        "name": "Jane Smith",
        "affiliation": "University of Science",
        "identifier_scheme": "ORCID",  # <-- triggers the error
        "identifier": "0000-0000-0000-0000",
    }
]
```

### 2.2 What worked / failed

| Case | Result |
| --- | --- |
| `"identifier_scheme": "ORCID"` uncommented | `TypeError: issubclass() arg 1 must be a class` during create/upload serialization |
| `"identifier_scheme"` commented out | Dataset creates successfully, but Dataverse UI shows no Identifier Type |

Reporter also noted that Identifier Type is a controlled vocabulary dropdown in the Dataverse UI
(ORCID, ISNI, LCNA, VIAF, GND, etc.).

### 2.3 Reporter stacktrace (annotated)

```text
Traceback (most recent call last):
  File ".../create_dataset.py", line 20, in <module>
    dataset = dv.create_dataset(... collection=":root")
  File ".../pyDataverse/dataverse/dataverse.py", line 597, in create_dataset
    dataset.upload_to_collection(collection)
  File ".../pyDataverse/dataverse/dataset.py", line 732, in upload_to_collection
    metadata=self.to_dataverse_create_dict(),
  File ".../pyDataverse/dataverse/dataset.py", line 758, in to_dataverse_create_dict
    metadata_blocks[name] = block.to_metadata_block()
  File ".../pyDataverse/dataverse/connect/metadata.py", line 165, in to_metadata_block
    processed_value = self._process_field_value(value, field_info)
  File ".../pyDataverse/dataverse/connect/metadata.py", line 297, in _process_field_value
    return [field.to_metadata_fields() for field in value]
  File ".../pyDataverse/dataverse/connect/metadata.py", line 523, in to_metadata_fields
    processed_value = self._process_field_value(value, field_info)
  File ".../pyDataverse/dataverse/connect/metadata.py", line 295, in _process_field_value
    if issubclass(field_info.dtype, CompoundField):
TypeError: issubclass() arg 1 must be a class
```

Frame meaning:

1. `create_dataset` optionally uploads immediately (`upload_to_collection=True` by default).
2. Upload builds the create body via `to_dataverse_create_dict()`.
3. Citation `author` is a multiple compound field → list of `CompoundField` instances.
4. Outer `_process_field_value` correctly detects the author list as compound and calls
   `to_metadata_fields()` on each author.
5. Inside each author, child fields are processed again. When the child is
   `authorIdentifierScheme`, `field_info.dtype` is `Annotated[...]`, and `issubclass` raises.

---

## 3. Local reproduction (verified)

### 3.1 Preconditions

- Local checkout of pyDataverse (verified with package path
  `/Users/shihuayu/Documents/GitHub/pyDataverse/pyDataverse`).
- Network access to a Dataverse installation that can serve metadata-block schemas
  (public metadata endpoints are enough). Verified against
  `https://demo.dataverse.org`.
- **No API token required** for the serialization-only reproduction below.
  A token is required only if you also want a live upload.

### 3.2 Minimal verifiable reproduction (no upload)

This isolates the exact failing function without mutating a remote collection:

```bash
cd /Users/shihuayu/Documents/GitHub/pyDataverse
uv run python - <<'PY'
from pyDataverse import Dataverse

dv = Dataverse(base_url="https://demo.dataverse.org")
dataset = dv.create_dataset(
    title="Issue 241 Reproduction Dataset",
    description="Reproducing TypeError with identifier_scheme ORCID",
    authors=[{
        "name": "Jane Smith",
        "affiliation": "University of Science",
        "identifier_scheme": "ORCID",
        "identifier": "0000-0000-0000-0000",
    }],
    contacts=[{
        "name": "Jane Smith",
        "email": "jane.smith@university.edu",
        "affiliation": "University of Science",
    }],
    subjects=["Computer and Information Science", "Engineering"],
    upload_to_collection=False,  # stop before HTTP create; still hit serialization
)

# This is the same conversion path used by upload_to_collection()
dataset.to_dataverse_create_dict()
PY
```

#### Expected (broken) output

```text
ℹ NativeApi: Connected to https://demo.dataverse.org
ℹ Fetching metadata blocks...
ℹ Dataset factory initialized
Traceback (most recent call last):
  ...
  File ".../pyDataverse/dataverse/connect/metadata.py", line 295, in _process_field_value
    if issubclass(field_info.dtype, CompoundField):
TypeError: issubclass() arg 1 must be a class
```

### 3.3 Control case (scheme omitted)

```bash
uv run python - <<'PY'
from pyDataverse import Dataverse

dv = Dataverse(base_url="https://demo.dataverse.org")
dataset = dv.create_dataset(
    title="Issue 241 Control Dataset",
    description="Without identifier_scheme",
    authors=[{
        "name": "Jane Smith",
        "affiliation": "University of Science",
        "identifier": "0000-0000-0000-0000",
    }],
    contacts=[{"name": "Jane Smith", "email": "jane.smith@university.edu"}],
    subjects=["Computer and Information Science"],
    upload_to_collection=False,
)
body = dataset.to_dataverse_create_dict()
print("OK", type(body).__name__)
PY
```

#### Expected (current) output

```text
OK DatasetCreateBody
```

Author payload contains `authorName`, `authorAffiliation`, and `authorIdentifier`, but **no**
`authorIdentifierScheme`.

### 3.4 Broader reproduction (not ORCID-specific)

```bash
uv run python - <<'PY'
from pyDataverse import Dataverse

dv = Dataverse(base_url="https://demo.dataverse.org")
ds = dv._internal_create_blank_dataset()
citation = ds.metadata_blocks["citation"]
citation["title"] = "Contributor CV child test"
citation["subject"] = ["Computer and Information Science"]
citation["dsDescription"].append({"dsDescriptionValue": "test"})
citation["author"].append({"authorName": "A"})
citation["datasetContact"].append({
    "datasetContactName": "A",
    "datasetContactEmail": "a@b.com",
})
citation["contributor"].append({
    "contributorName": "Helper",
    "contributorType": "Data Collector",  # nested controlled vocabulary
})
ds.to_dataverse_create_dict()
PY
```

#### Expected (broken) output

Same `TypeError: issubclass() arg 1 must be a class`.

This proves the defect is:

> any non-empty controlled-vocabulary field nested inside a compound field

not a special ORCID string-handling bug.

### 3.5 Live upload reproduction (optional; needs token)

If `API_TOKEN` is available (and optionally `DATAVERSE_URL` / `BASE_URL`):

```bash
export API_TOKEN="..."
export DATAVERSE_URL="https://demo.dataverse.org"   # or local Dataverse
uv run python - <<'PY'
import os
from pyDataverse import Dataverse

dv = Dataverse(
    base_url=os.environ.get("DATAVERSE_URL", "https://demo.dataverse.org"),
    api_token=os.environ["API_TOKEN"],
)
dv.create_dataset(
    title="Issue 241 Live Upload Reproduction",
    description="...",
    authors=[{
        "name": "Jane Smith",
        "affiliation": "University of Science",
        "identifier_scheme": "ORCID",
        "identifier": "0000-0000-0000-0000",
    }],
    contacts=[{"name": "Jane Smith", "email": "jane.smith@university.edu"}],
    subjects=["Computer and Information Science"],
    collection=":root",          # or another writable collection alias
    upload_to_collection=True,   # default; matches reporter path
)
PY
```

This should fail on the same `_process_field_value` frame before the create HTTP request is sent.

---

## 4. Repository architecture relevant to this bug

| Layer | Location | Role in this bug |
| --- | --- | --- |
| High-level API | `pyDataverse/dataverse/dataverse.py` | `create_dataset()` maps user keys (`identifier_scheme`) to Dataverse field names (`authorIdentifierScheme`) and may upload |
| Dataset serialization | `pyDataverse/dataverse/dataset.py` | `to_dataverse_create_dict()` converts each metadata block |
| Dynamic model builder | `pyDataverse/dataverse/connect/builder.py` | Builds Pydantic models from Dataverse metadata-block schemas; CV fields become `Annotated[...]` |
| Metadata runtime | `pyDataverse/dataverse/connect/metadata.py` | Serializes blocks/compound fields into Dataverse create/edit payloads |
| Field descriptors | `pyDataverse/dataverse/connect/field.py` | `FieldInfo.dtype` / `parent_class` / `json_schema_extra.type_class` |

### 4.1 How author metadata is populated

In `create_dataset` / `_internal_create_dataset`:

```650:658:pyDataverse/dataverse/dataverse.py
        for author in authors:
            assert "name" in author, "Name is required"
            dataset.metadata_blocks["citation"]["author"].append(
                {
                    "authorName": author["name"],
                    "authorAffiliation": author.get("affiliation", None),
                    "authorIdentifierScheme": author.get("identifier_scheme", None),
                    "authorIdentifier": author.get("identifier", None),
                }
            )
```

Important:

- Assignment into the dynamic author compound model **succeeds**.
- Validation of `"ORCID"` against the controlled vocabulary also **succeeds** (via `AfterValidator`).
- The failure is later, during **export** to Dataverse JSON.

### 4.2 How controlled vocabulary fields are typed

`cv_field_to_pydantic_attr()` intentionally avoids Enums for performance and builds:

```243:279:pyDataverse/dataverse/connect/builder.py
@lru_cache(maxsize=4096)
def _cv_type_from_values(values: Tuple[str, ...], *, multiple: bool) -> Any:
    ...
    return Annotated[str, AfterValidator(_validate_scalar)]
```

For optional scalar CV fields:

```python
cv_type = Optional[Annotated[str, AfterValidator(...)]]
```

Verified runtime annotation on the generated `author` model:

```text
authorIdentifierScheme:
  typing.Annotated[str, AfterValidator(...)] | None
  typeClass=controlledVocabulary
```

Primitive siblings remain plain optionals:

```text
authorName:        str | None          (primitive)
authorAffiliation: str | None          (primitive)
authorIdentifier:  str | None          (primitive)
```

### 4.3 How dtype is extracted before `issubclass`

```245:274:pyDataverse/dataverse/connect/metadata.py
    def _extract_info(cls, name: str) -> FieldInfo:
        field_info = cls.model_fields[name]
        dtype = field_info.annotation
        multiple = cls._is_multiple_type(dtype)
        if multiple:
            dtype = cls._extract_inner_type(dtype)
        dtype = cls._unwrap_optional(dtype)
        return FieldInfo(
            dtype=dtype,
            parent_class=cls._get_parent_class(dtype),
            multiple=multiple,
            json_schema_extra=...,
        )
```

`_unwrap_optional()` removes `None` from `Union` / `|`, leaving:

```text
Annotated[str, AfterValidator(...)]
```

`_get_parent_class()` returns `None` for that object because it has no `__bases__`.

Verified extraction for each author child:

| Field | Extracted `dtype` | `isinstance(dtype, type)` | `issubclass(dtype, CompoundField)` |
| --- | --- | --- | --- |
| `authorName` | `str` | True | False |
| `authorAffiliation` | `str` | True | False |
| `authorIdentifier` | `str` | True | False |
| `authorIdentifierScheme` | `Annotated[str, AfterValidator(...)]` | **False** | **raises TypeError** |

---

## 5. Exact failure path (step by step)

```text
create_dataset(identifier_scheme="ORCID")
  └─ _internal_create_dataset()
       └─ citation.author.append({authorIdentifierScheme: "ORCID", ...})   # OK
  └─ upload_to_collection()   # or explicit to_dataverse_create_dict()
       └─ Dataset.to_dataverse_create_dict()
            └─ citation.to_metadata_block()
                 └─ _process_field_value(author_list, FieldInfo(dtype=ValidatingList[author]))
                      └─ [author.to_metadata_fields() for author in author_list]
                           └─ for each non-empty child field:
                                field_info = _extract_info(child_name)
                                _process_field_value(child_value, field_info)
                                  └─ issubclass(field_info.dtype, CompoundField)
                                       # dtype is Annotated[...] for CV children
                                       # TypeError: issubclass() arg 1 must be a class
```

### 5.1 Why empty scheme does not crash

`CompoundField.to_metadata_fields()` skips empty values first:

```518:523:pyDataverse/dataverse/connect/metadata.py
        for name, value in self:
            if self._is_value_empty(value):
                continue
            field_info = self._extract_info(name)
            processed_value = self._process_field_value(value, field_info)
```

If `identifier_scheme` is omitted, `authorIdentifierScheme` is `None` / empty → skipped → never calls
`issubclass` on the Annotated dtype. That is why the “comment out ORCID” workaround succeeds and why
Identifier Type is missing in the UI.

### 5.2 Why top-level controlled vocabularies still work

Top-level CV fields such as `subject` are processed as ordinary values in
`to_metadata_block()`. They never need the “is this a nested CompoundField?” branch in a way that
depends on Annotated dtype subclass checks for the CV annotation itself. Nested CV children inside
compound fields are the special case that hits the unguarded `issubclass`.

### 5.3 Inconsistency already present in the same file

Safe patterns already exist nearby:

```204:205:pyDataverse/dataverse/connect/metadata.py
        if isinstance(dtype, type) and issubclass(dtype, ValidatingList):
```

```223:223:pyDataverse/dataverse/connect/metadata.py
        if isinstance(dtype, type) and issubclass(dtype, ValidatingList):
```

And elsewhere the module deliberately avoids fragile class checks for forward references by using
`value.__class__.__name__ == "CompoundField"`.

`_process_field_value()` is the outlier: it calls bare `issubclass(field_info.dtype, CompoundField)`.

---

## 6. Root cause statement (precise)

**Defect:** `MetadataBlockBase._process_field_value()` assumes `field_info.dtype` is always a class
suitable for `issubclass()`.

**Triggering type construction:** Controlled-vocabulary fields are represented as
`Annotated[str, AfterValidator(...)]` (optionally wrapped in `Optional[...]`) by
`_cv_type_from_values()` in `builder.py`.

**Triggering runtime condition:** A nested CV field inside a compound field is non-empty, so
serialization reaches `_process_field_value()` with `dtype = Annotated[...]`.

**Direct failing expression:**

```python
issubclass(field_info.dtype, CompoundField)
```

**Why the user-facing symptom mentions ORCID:** The high-level docs example uses
`identifier_scheme="ORCID"`, which populates `authorIdentifierScheme`, the nested CV child of
`author`. ORCID is merely the common value that exercises the broken path.

---

## 7. Specific solution

### 7.1 Design goals

1. Allow nested controlled-vocabulary values (e.g. ORCID Identifier Type) to serialize.
2. Preserve correct compound-field recursion for real nested `CompoundField` values.
3. Match existing defensive `isinstance(dtype, type)` guards in the same module
   (`_is_multiple_type` / `_extract_inner_type` at lines 204 and 223).
4. Keep the change minimal and local; do not redesign CV typing unless needed.
5. Make every fix step **verifiable** with an explicit pass/fail command (see §8–§10).

### 7.2 Key line map (current tree)

| Symbol | File | Lines | Role |
| --- | --- | --- | --- |
| `_is_multiple_type` | `metadata.py` | 190–206 | Already guards `issubclass` with `isinstance(dtype, type)` |
| `_extract_inner_type` | `metadata.py` | 209–226 | Uses `ValidatingList.__item_type__` |
| `_unwrap_optional` | `metadata.py` | 229–243 | Unwraps `Union[..., None]` only; **does not** unwrap `Annotated` |
| `_extract_info` | `metadata.py` | 246–274 | Builds `FieldInfo.dtype` |
| **`_process_field_value`** | `metadata.py` | **276–300** | **Bug site: bare `issubclass` at line 295** |
| `to_metadata_block` | `metadata.py` | 160–167 | Calls `_process_field_value` for top-level fields |
| `CompoundField.to_metadata_fields` | `metadata.py` | 518–529 | Calls `_process_field_value` for nested children |
| `cv_field_to_pydantic_attr` | `builder.py` | 196–240 | Wraps CV types as `Optional[Annotated[...]]` |
| `_cv_type_from_values` | `builder.py` | 243–279 | Builds `Annotated[str, AfterValidator(...)]` |
| `Dataverse.create_dataset` | `dataverse.py` | 538–601 | Default `upload_to_collection=True` |
| author mapping | `dataverse.py` | 650–659 | `identifier_scheme` → `authorIdentifierScheme` |
| `Dataset.upload_to_collection` | `dataset.py` | 704–738 | Calls `to_dataverse_create_dict()` at ~733 |
| `Dataset.to_dataverse_create_dict` | `dataset.py` | 740–772 | Calls `block.to_metadata_block()` at ~757–759 |

### 7.3 Primary code change (required)

**File:** `pyDataverse/dataverse/connect/metadata.py`  
**Function:** `MetadataBlockBase._process_field_value` (currently lines 276–300)

#### Current (broken)

```python
def _process_field_value(self, value: Any, field_info: FieldInfo) -> ...:
    # Check by class name since CompoundField is defined later in this module

    if issubclass(field_info.dtype, CompoundField):  # line 295 — raises on Annotated
        if field_info.multiple and isinstance(value, list):
            return [field.to_metadata_fields() for field in value]
        return value.to_metadata_fields()

    return value
```

#### Fixed (required)

```python
def _process_field_value(self, value: Any, field_info: FieldInfo) -> ...:
    """Process a field value, converting CompoundField instances to metadata dicts.

    Controlled-vocabulary fields are typed as Annotated[str, AfterValidator(...)]
    (see builder._cv_type_from_values). Those typing objects are not classes, so
    issubclass() must be guarded with isinstance(..., type). See issue #241.
    """
    dtype = field_info.dtype
    if isinstance(dtype, type) and issubclass(dtype, CompoundField):
        if field_info.multiple and isinstance(value, list):
            return [field.to_metadata_fields() for field in value]
        return value.to_metadata_fields()

    return value
```

#### Why this is sufficient

| `dtype` kind | Guard result | Behavior |
| --- | --- | --- |
| Generated `CompoundField` subclass | `isinstance` True, `issubclass` True | Recurse via `to_metadata_fields()` |
| Primitive `str` / similar | `isinstance` True, `issubclass` False | Return value unchanged |
| `Annotated[str, AfterValidator(...)]` (CV) | `isinstance` **False** | Skip subclass check; return `"ORCID"` unchanged |

Then `_create_metadata_field()` wraps the string as a Dataverse metadata field with
`typeClass=controlledVocabulary`.

**No change to `builder.py` CV typing is required** for correctness of this bug.

### 7.4 Optional hardening (recommended, not required for #241)

#### Option A — also unwrap `Annotated` in `_extract_info`

```python
@staticmethod
def _unwrap_annotated(dtype: Any) -> Any:
    if get_origin(dtype) is Annotated:  # import Annotated from typing
        args = get_args(dtype)
        return args[0] if args else dtype
    return dtype
```

In `_extract_info` after optional unwrap:

```python
dtype = cls._unwrap_optional(dtype)
dtype = cls._unwrap_annotated(dtype)
```

This makes introspection nicer (`dtype` becomes `str`), but the `isinstance(dtype, type)`
guard in `_process_field_value` remains mandatory for other typing constructs.

#### Option B — decide compound-ness from runtime value / `typeClass`

```python
if field_info.json_schema_extra.type_class == "compound":
    ...
```

or `isinstance(value, CompoundField)`. Prefer the guarded `issubclass` fix as the smallest
behavior-preserving change.

### 7.5 Files that must / must not change

| File | Change? | Reason |
| --- | --- | --- |
| `pyDataverse/dataverse/connect/metadata.py` | **Required** | Guard `issubclass` |
| `tests/dataverse/test_issue_241_identifier_scheme.py` | **Required (new)** | Regression coverage |
| `builder.py` | Optional only | CV `Annotated` design is intentional |
| `dataverse.py` author mapping | No | Already maps `identifier_scheme` correctly |
| `dataset.py` upload path | No | Not the source of the TypeError |
| `pyproject.toml` / `uv.lock` | No | No dependency change |

### 7.6 Regression tests to add

**New file:** `tests/dataverse/test_issue_241_identifier_scheme.py`

Mirror patterns from:

- `tests/dataverse/test_async_run.py` — focused issue regression + docstring
- `tests/dataverse/test_dataset.py::test_to_dataverse_create_dict` (lines 432–534) —
  asserts create-body structure for compound author fields

#### Critical pytest pitfall (must follow)

`tests/conftest.py` lines 22–38 raise `pytest.UsageError` at **session start** unless **all** of
these are set:

```text
BASE_URL
API_TOKEN
API_TOKEN_SUPERUSER
```

`pytest.mark.skipif(not BASE_URL)` alone does **not** bypass that gate. For local runs of the new
file:

```bash
export BASE_URL="${BASE_URL:-https://demo.dataverse.org}"
export API_TOKEN="${API_TOKEN:-unused}"
export API_TOKEN_SUPERUSER="${API_TOKEN_SUPERUSER:-unused}"
```

Serialization-only tests use `upload_to_collection=False` and do not need a real mutable token.
A real token is required only for optional live-upload verification (§10.5).

#### Assert style (pick one and stay consistent)

1. **Alias JSON dicts** (recommended for script-style checks):
   `body = dataset.to_dataverse_create_dict().model_dump(by_alias=True)` then
   `typeName` / `typeClass` / `datasetVersion` / `metadataBlocks`.
2. **Pydantic attribute equality** (like `test_to_dataverse_create_dict`):
   use `type_name` / `type_class` on model objects.

Mixing camelCase and snake_case in the same assertion is a common false failure.

#### Suggested tests

```python
"""Regression tests for issue #241 (nested controlled vocabulary serialization).

Issue #241: setting author identifier_scheme=\"ORCID\" raised
TypeError: issubclass() arg 1 must be a class during to_dataverse_create_dict().
Root cause: unguarded issubclass() on Annotated CV dtypes in _process_field_value.
"""

from __future__ import annotations

import os

from pyDataverse import Dataverse

BASE_URL = os.environ.get("BASE_URL", "https://demo.dataverse.org")


def _author0_from_body(body: dict) -> dict:
    fields = body["datasetVersion"]["metadataBlocks"]["citation"]["fields"]
    author_field = next(f for f in fields if f["typeName"] == "author")
    return author_field["value"][0]


def test_author_identifier_scheme_orcid_serializes():
    """Nested CV authorIdentifierScheme=ORCID must appear in create payload."""
    dv = Dataverse(base_url=BASE_URL)
    dataset = dv.create_dataset(
        title="Issue 241 ORCID serialization",
        description="Nested controlled vocabulary must serialize",
        authors=[{
            "name": "Jane Smith",
            "affiliation": "University of Science",
            "identifier_scheme": "ORCID",
            "identifier": "0000-0000-0000-0000",
        }],
        contacts=[{"name": "Jane Smith", "email": "jane.smith@university.edu"}],
        subjects=["Computer and Information Science"],
        upload_to_collection=False,
    )

    body = dataset.to_dataverse_create_dict().model_dump(by_alias=True)
    author0 = _author0_from_body(body)

    assert "authorIdentifierScheme" in author0
    assert author0["authorIdentifierScheme"]["typeClass"] == "controlledVocabulary"
    assert author0["authorIdentifierScheme"]["value"] == "ORCID"
    assert author0["authorIdentifier"]["value"] == "0000-0000-0000-0000"


def test_contributor_type_nested_cv_serializes():
    """Any nested CV child (not just ORCID) must serialize without TypeError."""
    dv = Dataverse(base_url=BASE_URL)
    ds = dv._internal_create_blank_dataset()
    citation = ds.metadata_blocks["citation"]
    citation["title"] = "Issue 241 contributorType"
    citation["subject"] = ["Computer and Information Science"]
    citation["dsDescription"].append({"dsDescriptionValue": "test"})
    citation["author"].append({"authorName": "A"})
    citation["datasetContact"].append({
        "datasetContactName": "A",
        "datasetContactEmail": "a@b.com",
    })
    citation["contributor"].append({
        "contributorName": "Helper",
        "contributorType": "Data Collector",
    })

    body = ds.to_dataverse_create_dict().model_dump(by_alias=True)
    fields = body["datasetVersion"]["metadataBlocks"]["citation"]["fields"]
    contributor_field = next(f for f in fields if f["typeName"] == "contributor")
    assert contributor_field["value"][0]["contributorType"]["value"] == "Data Collector"


def test_identifier_without_scheme_still_serializes():
    """Control: omitting identifier_scheme still works and omits the CV field."""
    dv = Dataverse(base_url=BASE_URL)
    dataset = dv.create_dataset(
        title="Issue 241 control",
        description="scheme omitted",
        authors=[{
            "name": "Jane Smith",
            "identifier": "0000-0000-0000-0000",
        }],
        contacts=[{"name": "Jane Smith", "email": "jane.smith@university.edu"}],
        subjects=["Computer and Information Science"],
        upload_to_collection=False,
    )
    body = dataset.to_dataverse_create_dict().model_dump(by_alias=True)
    author0 = _author0_from_body(body)
    assert "authorIdentifier" in author0
    assert "authorIdentifierScheme" not in author0
```

#### Optional live-upload test (CI / writable collection)

Use the existing `dataverse` fixture from `tests/conftest.py`, set
`upload_to_collection=True` / `collection="root"` (or CI collection), then fetch the dataset and
assert the author Identifier Type is ORCID. This proves end-to-end behavior but is **not** required
to prove the serialization fix itself.

### 7.7 Docs follow-up (optional)

After the fix merges, the high-level create-dataset ORCID example can remain unchanged. Optionally
add one sentence that Identifier Type is a supported controlled vocabulary on author metadata.

---

## 8. Step-by-step implementation playbook (must be followed in order)

Each step has an **Action**, an **Exact command**, and a **Pass criterion**.
Do not mark a step done unless the pass criterion is met.

### 8.0 Multi-task / sub-agent coordination (required when parallelizing)

This playbook is written so a parent agent (or a human) can assign steps to
sub-agents **without losing verifiability**. Follow these rules:

| Rule | Requirement |
| --- | --- |
| Single source of truth | All diagnosis, fix text, commands, and acceptance criteria live in **this file**. Sub-agents must not invent alternate fix strategies unless this doc is updated first. |
| Ordered gates | Steps **0 → 1 → 2 → 3** are strictly sequential. Later steps depend on earlier pass criteria. |
| Parallelizable work | After Step 1 baseline is captured, a second agent may draft the regression test file (§7.6 / Step 5) **in parallel** with the agent applying Step 2 — but that test agent must **not** claim the bug is fixed until Steps 3–4 pass. |
| No silent “done” | A sub-agent may only report a step complete by pasting: (1) the exact command run, (2) exit code, (3) the pass-criterion evidence (traceback, `PASS:` line, or pytest summary). |
| Verification ownership | The parent agent (or designated verifier agent) re-runs Steps 0, 3, 4, and 5 after all edit agents finish. Edits without re-verification are incomplete. |
| Evidence for PR | Step 7 evidence must include before (Step 1) and after (Steps 3–5). Missing either side = not merge-ready. |

Suggested agent split (optional):

| Agent | Owns | Must return |
| --- | --- | --- |
| A — Baseline | Steps 0–1 | Package path + TypeError traceback |
| B — Fix | Step 2 (and only the §7.3 change) | Diff hunk of `metadata.py` + Step 2 `rg` proof |
| C — Verify serialize | Steps 3–4 | Both `PASS:` lines + no TypeError |
| D — Tests | Step 5 (+ 5b) | New test file path + pytest summary (exit 0) |
| E — Optional live | Step 6 | Dataset PID / UI confirmation that Identifier Type = ORCID |
| Parent — Gate | Step 7 + §10.6 | Checklist all checked; definition of done satisfied |

**Hard stop:** If any pass criterion fails, stop downstream agents, fix the failure, and
re-run from the failed step. Do not “skip verification” to move on.

### Step 0 — Confirm you are editing the intended tree

**Action:** Print the loaded package path.

```bash
cd /Users/shihuayu/Documents/GitHub/pyDataverse
uv run python - <<'PY'
import inspect, pyDataverse
print(inspect.getfile(pyDataverse))
PY
```

**Pass criterion:** Output ends with
`/Documents/GitHub/pyDataverse/pyDataverse/__init__.py` (or the intended checkout path).

**Fail criterion:** Path points at a different install / site-packages copy.

### Step 1 — Capture broken baseline (before editing)

**Action:** Run the ORCID serialization repro **before** changing code.

```bash
uv run python - <<'PY'
from pyDataverse import Dataverse
dv = Dataverse(base_url="https://demo.dataverse.org")
ds = dv.create_dataset(
    title="Issue 241 baseline",
    description="expect TypeError",
    authors=[{
        "name": "Jane Smith",
        "affiliation": "University of Science",
        "identifier_scheme": "ORCID",
        "identifier": "0000-0000-0000-0000",
    }],
    contacts=[{"name": "Jane Smith", "email": "jane.smith@university.edu"}],
    subjects=["Computer and Information Science"],
    upload_to_collection=False,
)
ds.to_dataverse_create_dict()
PY
```

**Pass criterion (baseline):** Process exits non-zero with:

```text
TypeError: issubclass() arg 1 must be a class
```

and the traceback includes
`pyDataverse/dataverse/connect/metadata.py` → `_process_field_value` →
`issubclass(field_info.dtype, CompoundField)`.

Save this output for the PR (“before”).

### Step 2 — Apply the required one-line semantic fix

**Action:** Edit `_process_field_value` in
`pyDataverse/dataverse/connect/metadata.py` as shown in §7.3.

**Pass criterion:** `rg -n "issubclass\\(field_info.dtype, CompoundField\\)" pyDataverse/dataverse/connect/metadata.py`
finds **no** unguarded call; the guarded form
`isinstance(dtype, type) and issubclass(dtype, CompoundField)` is present.

### Step 3 — Re-run the same ORCID command (after fix)

**Action:** Re-run Step 1 command, then assert payload contents:

```bash
uv run python - <<'PY'
from pyDataverse import Dataverse
dv = Dataverse(base_url="https://demo.dataverse.org")
ds = dv.create_dataset(
    title="Issue 241 fixed",
    description="Nested CV serialization works",
    authors=[{
        "name": "Jane Smith",
        "affiliation": "University of Science",
        "identifier_scheme": "ORCID",
        "identifier": "0000-0000-0000-0000",
    }],
    contacts=[{"name": "Jane Smith", "email": "jane.smith@university.edu"}],
    subjects=["Computer and Information Science"],
    upload_to_collection=False,
)
body = ds.to_dataverse_create_dict().model_dump(by_alias=True)
author0 = next(
    f for f in body["datasetVersion"]["metadataBlocks"]["citation"]["fields"]
    if f["typeName"] == "author"
)["value"][0]
scheme = author0["authorIdentifierScheme"]
assert scheme["typeClass"] == "controlledVocabulary", scheme
assert scheme["value"] == "ORCID", scheme
print("PASS: ORCID identifier_scheme serialized")
PY
```

**Pass criterion:** Prints `PASS: ORCID identifier_scheme serialized` and exit code 0.

**Fail criterion:** Any `TypeError`, missing `authorIdentifierScheme`, wrong `typeClass`, or wrong value.

### Step 4 — Verify control + broader nested CV cases

**Action A — scheme omitted still works:**

```bash
uv run python - <<'PY'
from pyDataverse import Dataverse
dv = Dataverse(base_url="https://demo.dataverse.org")
ds = dv.create_dataset(
    title="control",
    description="no scheme",
    authors=[{"name": "Jane Smith", "identifier": "0000-0000-0000-0000"}],
    contacts=[{"name": "Jane Smith", "email": "a@b.com"}],
    subjects=["Computer and Information Science"],
    upload_to_collection=False,
)
body = ds.to_dataverse_create_dict().model_dump(by_alias=True)
author0 = next(
    f for f in body["datasetVersion"]["metadataBlocks"]["citation"]["fields"]
    if f["typeName"] == "author"
)["value"][0]
assert "authorIdentifier" in author0
assert "authorIdentifierScheme" not in author0
print("PASS: control without scheme")
PY
```

**Action B — `contributorType` nested CV:**

```bash
uv run python - <<'PY'
from pyDataverse import Dataverse
dv = Dataverse(base_url="https://demo.dataverse.org")
ds = dv._internal_create_blank_dataset()
c = ds.metadata_blocks["citation"]
c["title"] = "contributorType check"
c["subject"] = ["Computer and Information Science"]
c["dsDescription"].append({"dsDescriptionValue": "test"})
c["author"].append({"authorName": "A"})
c["datasetContact"].append({"datasetContactName": "A", "datasetContactEmail": "a@b.com"})
c["contributor"].append({"contributorName": "Helper", "contributorType": "Data Collector"})
body = ds.to_dataverse_create_dict().model_dump(by_alias=True)
contrib = next(
    f for f in body["datasetVersion"]["metadataBlocks"]["citation"]["fields"]
    if f["typeName"] == "contributor"
)["value"][0]
assert contrib["contributorType"]["value"] == "Data Collector"
print("PASS: nested contributorType")
PY
```

**Pass criterion:** Both scripts print their `PASS: ...` lines.

### Step 5 — Add and run regression tests

**Action:**

1. Create `tests/dataverse/test_issue_241_identifier_scheme.py` using §7.6.
2. Run:

```bash
export BASE_URL="${BASE_URL:-https://demo.dataverse.org}"
export API_TOKEN="${API_TOKEN:-unused}"
export API_TOKEN_SUPERUSER="${API_TOKEN_SUPERUSER:-unused}"
uv run pytest tests/dataverse/test_issue_241_identifier_scheme.py -q
```

**Pass criterion:** All new tests pass (exit code 0).

**Also run** the existing create-dict test to catch accidental compound regressions:

```bash
uv run pytest tests/dataverse/test_dataset.py::TestDataset::test_to_dataverse_create_dict -q
```

**Pass criterion:** Existing test still passes (requires the same three env vars; use a real
`BASE_URL`/`API_TOKEN` pair if the fixture needs a live schema/server).

### Step 6 — Optional live upload verification

**Action:** Only if a writable collection and real token exist:

```bash
export BASE_URL="..."
export API_TOKEN="..."   # real token
uv run python - <<'PY'
import os
from pyDataverse import Dataverse
dv = Dataverse(base_url=os.environ["BASE_URL"], api_token=os.environ["API_TOKEN"])
ds = dv.create_dataset(
    title="Issue 241 live ORCID upload",
    description="End-to-end check",
    authors=[{
        "name": "Jane Smith",
        "affiliation": "University of Science",
        "identifier_scheme": "ORCID",
        "identifier": "0000-0000-0000-0000",
    }],
    contacts=[{"name": "Jane Smith", "email": "jane.smith@university.edu"}],
    subjects=["Computer and Information Science"],
    collection="root",
    upload_to_collection=True,
)
print("created:", ds.persistent_identifier)
fetched = dv.fetch_dataset(ds.persistent_identifier)
print("authors:", fetched.authors)
PY
```

**Pass criterion:** Create succeeds; UI or fetched metadata shows Identifier Type `ORCID`.

### Step 7 — Record evidence for the PR

**Action:** Attach to the PR body:

1. Step 1 “before” traceback excerpt  
2. Step 3 “after” `PASS: ORCID identifier_scheme serialized`  
3. Step 4 both PASS lines  
4. Step 5 pytest summary  
5. `inspect.getfile(pyDataverse)` output proving the tested tree  

**Pass criterion:** Reviewer can re-run Steps 0–5 and get the same pass results.

---

## 9. Implementation checklist (summary)

- [x] Step 0: package path confirmed  
- [x] Step 1: broken baseline captured  
- [x] Step 2: guarded `issubclass` applied in `metadata.py`  
- [x] Step 3: ORCID serialization PASS  
- [x] Step 4: control + `contributorType` PASS  
- [x] Step 5: new regression file added and pytest green  
- [x] Step 5b: `test_to_dataverse_create_dict` still green  
- [ ] Step 6: optional live upload (if credentials available)  
- [x] Step 7: before/after evidence recorded below  

### Step 7 evidence (recorded on `fix/241-identifier-scheme-issubclass`)

**Step 0 path:**
`/Users/shihuayu/Documents/GitHub/pyDataverse/pyDataverse/__init__.py`

**Step 1 before (exit 1):**
```text
TypeError: issubclass() arg 1 must be a class
  File ".../metadata.py", line 295, in _process_field_value
    if issubclass(field_info.dtype, CompoundField):
```

**Step 2:** guarded form present at `metadata.py` ~290:
`isinstance(dtype, type) and issubclass(dtype, CompoundField)`

**Step 3 after:** `PASS: ORCID identifier_scheme serialized`

**Step 4:** `PASS: control without identifier_scheme` and
`PASS: contributorType nested CV serialized`

**Step 5:** `tests/dataverse/test_issue_241_identifier_scheme.py` → **3 passed**

**Step 5b:** `TestDataset::test_to_dataverse_create_dict` → **1 passed**

No dependency / lockfile changes are required for this fix.

---

## 10. Verification plan (must remain reproducible)

### 10.1 Before / after isolation rule

Never trust a “works on my machine” claim without printing the loaded module path (§8 Step 0).
Testing an installed wheel while editing the local tree is the most common false positive.

### 10.2 Broken vs fixed matrix

| Scenario | Before fix | After fix |
| --- | --- | --- |
| `identifier_scheme="ORCID"` + `to_dataverse_create_dict()` | **TypeError** | Serializes ORCID CV field |
| scheme omitted + identifier present | Works (scheme absent) | Works (scheme absent) |
| nested `contributorType` set | **TypeError** | Serializes contributorType |
| top-level `subject` CV | Works | Works |
| existing compound author without scheme (`test_to_dataverse_create_dict`) | Works | Works |

### 10.3 Exact shell commands (copy/paste)

See §8 Steps 0–5. Prefer those over paraphrased commands so results stay comparable.

### 10.4 Pytest / CI notes

- Local pytest always needs `BASE_URL`, `API_TOKEN`, `API_TOKEN_SUPERUSER` because of
  `tests/conftest.py` session gate.
- CI already sets these in `.github/workflows/tests.yml`.
- For serialization-only local iteration, `uv run python` scripts in §8 avoid pytest entirely and
  only need network access to fetch metadata schemas.

### 10.5 Optional live upload verification

With a writable collection and real token, create the dataset and confirm Author → Identifier Type
shows `ORCID` in the Dataverse UI (§8 Step 6).

### 10.6 Acceptance criteria (definition of done)

The fix is **complete and verifiable** only when **all** are true:

1. Step 1 baseline still documents the old TypeError (or is linked from the PR as historical evidence).  
2. Step 3 no longer raises `TypeError`.  
3. Serialized author metadata includes
   `authorIdentifierScheme.value == "ORCID"` and
   `typeClass == "controlledVocabulary"`.  
4. Scheme-omitted control case still serializes.  
5. At least one additional nested CV case (`contributorType`) serializes.  
6. `tests/dataverse/test_issue_241_identifier_scheme.py` exists and passes under pytest with the
   three required env vars set.  
7. `test_to_dataverse_create_dict` still passes.  
8. Package path printed during verification points at the intended checkout.  
9. PR includes before/after command output.

**Verifiability rule (non-negotiable):** Claiming “fixed” without Steps 0 + 3 + 4 + 5 evidence
is invalid, including when work was split across sub-agents. Each completed step must cite the
command and the pass-criterion output. Parent/verifier re-run of Steps 0, 3, 4, and 5 is required
before opening or updating the PR (§8.0).

---

## 11. Impact / risk analysis

| Area | Impact |
| --- | --- |
| High-level `create_dataset` with ORCID / other identifier schemes | Restored; currently broken |
| Any nested CV inside compound metadata | Restored; currently broken when non-empty |
| Top-level CV fields (`subject`, etc.) | No intentional behavior change |
| Empty nested CV fields | Still skipped as empty; unchanged |
| Performance | Negligible (`isinstance` check) |
| API / schema compatibility | No wire-format change beyond successfully emitting the CV field that was previously impossible |

Risk of the guarded fix is low: it only skips `issubclass` for non-class typing objects that could
never legally be `CompoundField` subclasses.

---

## 12. Pitfalls (read before verifying)

1. **Wrong package path.** Always run §8 Step 0. Editable local tree vs installed wheel is the
   most common false positive/negative.
2. **`model_dump` aliases.** Wire JSON uses `datasetVersion`, `metadataBlocks`, `typeName`,
   `typeClass`. Python models use snake_case (`type_name`, `type_class`). Use
   `.model_dump(by_alias=True)` for dict asserts; use attribute names for pydantic equality.
3. **`tests/conftest.py` session gate.** Pytest aborts unless `BASE_URL`, `API_TOKEN`, and
   `API_TOKEN_SUPERUSER` are all set — even for serialization-only tests.
   `skipif(not BASE_URL)` alone does **not** bypass that.
4. **ValidatingList item type.** Prefer creating at least one compound item (`.append(...)`)
   before inspecting item fields; `__item_type__` exists but is easy to misuse.
5. **Empty CV fields look “fixed.”** Omitting `identifier_scheme` never exercised the bug path.
   Always verify with a **non-empty** nested CV value.
6. **Issue #240 confusion.** Python 3.14 async failures are a separate bug. This issue reproduces
   on Python 3.13/3.14 alike once metadata serialization runs.

---

## 13. Related observations useful for reviewers

1. The reporter’s workaround (commenting out `identifier_scheme`) is explained by empty-value
   skipping, not by ORCID being invalid.
2. The docs example is correct; the library serialization path is wrong.
3. `FieldInfo.dtype` is annotated as `Type` in `field.py`, but runtime values can be typing
   constructs. The type hint is aspirational and contributed to the unsafe assumption.
4. Issue #241 is independent of issue #240 (Python 3.14 `AsyncLibraryNotFoundError` /
   `nest_asyncio`). They share a reporter and docs example path, but different root causes.

---

## 14. Suggested PR summary text

```text
Fix nested controlled-vocabulary serialization (issue #241)

Guard issubclass() in MetadataBlockBase._process_field_value so Annotated
controlled-vocabulary dtypes (e.g. authorIdentifierScheme=ORCID) serialize
instead of raising TypeError. Add regression coverage for ORCID and another
nested CV field.
```

---

## 15. Appendix — verified local commands and outcomes

Commands below were executed successfully during analysis against
`https://demo.dataverse.org` using the local package tree.

### A. ORCID path fails

```bash
uv run python - <<'PY'
from pyDataverse import Dataverse
dv = Dataverse(base_url="https://demo.dataverse.org")
ds = dv.create_dataset(
    title="x", description="y",
    authors=[{"name": "Jane Smith", "identifier_scheme": "ORCID", "identifier": "0000-0000-0000-0000"}],
    contacts=[{"name": "Jane Smith", "email": "a@b.com"}],
    subjects=["Computer and Information Science"],
    upload_to_collection=False,
)
ds.to_dataverse_create_dict()
PY
```

Outcome: `TypeError: issubclass() arg 1 must be a class` at
`metadata.py::_process_field_value`.

### B. Control path succeeds

Same as A without `identifier_scheme` → `DatasetCreateBody` returned.

### C. `contributorType` also fails

Setting nested `contributorType="Data Collector"` → same `TypeError`.

### D. Extracted dtype evidence

```text
authorIdentifierScheme extracted dtype:
  typing.Annotated[str, AfterValidator(...)]
isinstance(dtype, type) == False
issubclass(dtype, CompoundField) raises TypeError
```

### E. Instruction for future fixers

Treat §8 as mandatory. A change is not done until every Step 0–5 pass criterion is met and the
evidence is attached to the PR. Optional Step 6 strengthens confidence but does not replace
serialization verification.

This document is the authoritative, verifiable diagnosis and solution plan for issue #241.
