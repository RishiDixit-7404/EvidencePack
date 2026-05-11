"""Tests for EvidencePack core data models."""

from __future__ import annotations

import json
from datetime import datetime

import pytest

from evidencepack.models import (
    ControlCitation,
    ControlRecord,
    FileRecord,
    FileStatus,
    FileType,
    GapStatus,
    MatchMethod,
    MatchResult,
    ensure_confidence,
    serialize_model,
)


def test_gap_status_contains_exact_urd_statuses() -> None:
    assert [status.value for status in GapStatus] == [
        "COMPLETE",
        "PARTIAL",
        "MISSING",
        "STALE",
        "AMBIGUOUS",
    ]


def test_file_type_supports_urd_types_and_unsupported_image() -> None:
    assert [file_type.value for file_type in FileType] == [
        "PDF",
        "XLSX",
        "XLS",
        "CSV",
        "DOCX",
        "PNG",
        "JPG",
        "TXT",
        "UNSUPPORTED",
        "UNSUPPORTED_IMAGE",
    ]


def test_file_record_to_dict_serializes_datetime_and_enums() -> None:
    modified_at = datetime(2026, 5, 11, 9, 30, 15)
    record = FileRecord(
        path="demo_evidence/access_policy_v3.pdf",
        filename="access_policy_v3.pdf",
        file_type=FileType.PDF,
        size_bytes=1024,
        modified_at=modified_at,
        status=FileStatus.EXTRACTED,
    )

    data = record.to_dict()

    assert data["modified_at"] == modified_at.isoformat()
    assert data["file_type"] == "PDF"
    assert data["status"] == "EXTRACTED"


def test_control_record_to_dict_returns_expected_keys_and_values() -> None:
    record = ControlRecord(
        control_id="AM-01",
        description="Quarterly user access reviews are performed and documented.",
        required_evidence_type="Policy document, Access review export",
        domain="Access Management",
        keywords=["quarterly", "access", "review"],
    )

    assert record.to_dict() == {
        "control_id": "AM-01",
        "description": "Quarterly user access reviews are performed and documented.",
        "required_evidence_type": "Policy document, Access review export",
        "domain": "Access Management",
        "keywords": ["quarterly", "access", "review"],
    }


@pytest.mark.parametrize("confidence", [0.0, 0.42, 1.0])
def test_match_result_accepts_confidence_between_zero_and_one(confidence: float) -> None:
    result = MatchResult(
        control_id="CM-01",
        filename="ticket_dump_march.csv",
        confidence=confidence,
        source_ref="row 2",
        method=MatchMethod.KEYWORD,
    )

    assert result.confidence == confidence
    assert ensure_confidence(confidence) == confidence


def test_match_result_rejects_confidence_below_zero() -> None:
    with pytest.raises(ValueError, match="confidence must be between 0.0 and 1.0"):
        MatchResult(
            control_id="CM-01",
            filename="ticket_dump_march.csv",
            confidence=-0.01,
            source_ref="row 2",
            method=MatchMethod.KEYWORD,
        )


def test_match_result_rejects_confidence_above_one() -> None:
    with pytest.raises(ValueError, match="confidence must be between 0.0 and 1.0"):
        MatchResult(
            control_id="CM-01",
            filename="ticket_dump_march.csv",
            confidence=1.01,
            source_ref="row 2",
            method=MatchMethod.KEYWORD,
        )


def test_control_citation_to_dict_serializes_nested_matches() -> None:
    citation = ControlCitation(
        control_id="DP-04",
        status=GapStatus.PARTIAL,
        matches=[
            MatchResult(
                control_id="DP-04",
                filename="firewall_rules_screenshot.png",
                confidence=0.7,
                source_ref="image file",
                method=MatchMethod.KEYWORD,
                metadata={"seen_at": datetime(2026, 5, 11, 10, 0, 0)},
            )
        ],
        gap_notes="Image evidence requires manual review in v1.0.",
        suggested_evidence_type="Firewall rules screenshot",
    )

    data = citation.to_dict()

    assert data["status"] == "PARTIAL"
    assert data["matches"] == [
        {
            "control_id": "DP-04",
            "filename": "firewall_rules_screenshot.png",
            "confidence": 0.7,
            "source_ref": "image file",
            "method": "keyword",
            "reason": None,
            "metadata": {"seen_at": "2026-05-11T10:00:00"},
        }
    ]
    json.dumps(data)


def test_serialize_model_handles_primitive_containers() -> None:
    value = {
        "statuses": [GapStatus.COMPLETE, GapStatus.MISSING],
        "timestamp": datetime(2026, 5, 11, 11, 0, 0),
    }

    assert serialize_model(value) == {
        "statuses": ["COMPLETE", "MISSING"],
        "timestamp": "2026-05-11T11:00:00",
    }

