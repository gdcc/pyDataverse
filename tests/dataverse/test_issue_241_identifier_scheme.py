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
        authors=[
            {
                "name": "Jane Smith",
                "affiliation": "University of Science",
                "identifier_scheme": "ORCID",
                "identifier": "0000-0000-0000-0000",
            }
        ],
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
    citation["datasetContact"].append(
        {
            "datasetContactName": "A",
            "datasetContactEmail": "a@b.com",
        }
    )
    citation["contributor"].append(
        {
            "contributorName": "Helper",
            "contributorType": "Data Collector",
        }
    )

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
        authors=[
            {
                "name": "Jane Smith",
                "identifier": "0000-0000-0000-0000",
            }
        ],
        contacts=[{"name": "Jane Smith", "email": "jane.smith@university.edu"}],
        subjects=["Computer and Information Science"],
        upload_to_collection=False,
    )
    body = dataset.to_dataverse_create_dict().model_dump(by_alias=True)
    author0 = _author0_from_body(body)
    assert "authorIdentifier" in author0
    assert "authorIdentifierScheme" not in author0
