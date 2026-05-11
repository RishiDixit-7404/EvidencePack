"""Tests for recursive evidence scanning."""

from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from evidencepack.models import FileStatus, FileType
from evidencepack.scanner import (
    detect_file_type,
    is_stale,
    scan_directory,
    status_for_file_type,
)


@pytest.mark.parametrize(
    ("filename", "expected"),
    [
        ("policy.pdf", FileType.PDF),
        ("POLICY.PDF", FileType.PDF),
        ("access.xlsx", FileType.XLSX),
        ("legacy.xls", FileType.XLS),
        ("tickets.csv", FileType.CSV),
        ("notes.docx", FileType.DOCX),
        ("image.png", FileType.PNG),
        ("photo.jpg", FileType.JPG),
        ("photo.jpeg", FileType.JPG),
        ("README.txt", FileType.TXT),
    ],
)
def test_detect_file_type_maps_supported_extensions(filename: str, expected: FileType) -> None:
    assert detect_file_type(Path(filename)) == expected


def test_detect_file_type_maps_unknown_extension_to_unsupported() -> None:
    assert detect_file_type(Path("archive.zip")) == FileType.UNSUPPORTED


@pytest.mark.parametrize("file_type", [FileType.PNG, FileType.JPG])
def test_image_file_types_get_unsupported_image_status(file_type: FileType) -> None:
    assert status_for_file_type(file_type) == FileStatus.UNSUPPORTED_IMAGE


@pytest.mark.parametrize("file_type", [FileType.UNSUPPORTED, FileType.UNSUPPORTED_IMAGE])
def test_unsupported_file_types_get_unsupported_status(file_type: FileType) -> None:
    assert status_for_file_type(file_type) == FileStatus.UNSUPPORTED


@pytest.mark.parametrize(
    "file_type",
    [
        FileType.PDF,
        FileType.XLSX,
        FileType.XLS,
        FileType.CSV,
        FileType.DOCX,
        FileType.TXT,
    ],
)
def test_supported_extractable_file_types_get_pending_status(file_type: FileType) -> None:
    assert status_for_file_type(file_type) == FileStatus.PENDING


def test_is_stale_uses_fixed_now() -> None:
    now = datetime(2026, 5, 11, 12, 0, 0)

    assert is_stale(now - timedelta(days=91), stale_days=90, now=now)
    assert not is_stale(now - timedelta(days=90), stale_days=90, now=now)


def test_scan_directory_returns_demo_records_with_metadata() -> None:
    records = scan_directory(Path("demo_evidence"))
    by_path = {record.path: record for record in records}

    assert len(records) == 7
    assert set(by_path) == {
        "access_policy_v3.pdf",
        "control_matrix_draft.xlsx",
        "controls.xlsx",
        "firewall_rules_screenshot.png",
        "meeting_notes_kickoff.docx",
        "ticket_dump_march.csv",
        "user_access_export_Q1.xlsx",
    }

    policy = by_path["access_policy_v3.pdf"]
    assert policy.file_type == FileType.PDF
    assert policy.page_count == 4
    assert policy.metadata["page_count"] == 4

    access_export = by_path["user_access_export_Q1.xlsx"]
    assert access_export.file_type == FileType.XLSX
    assert access_export.sheet_count >= 1
    assert access_export.metadata["sheet_count"] >= 1

    tickets = by_path["ticket_dump_march.csv"]
    assert tickets.file_type == FileType.CSV
    assert tickets.row_count >= 1
    assert tickets.metadata["row_count"] >= 1

    firewall = by_path["firewall_rules_screenshot.png"]
    assert firewall.file_type == FileType.PNG
    assert firewall.status == FileStatus.UNSUPPORTED_IMAGE
    assert firewall.metadata == {}


def test_scan_directory_raises_for_missing_path() -> None:
    with pytest.raises(FileNotFoundError):
        scan_directory(Path("missing_demo_evidence"))


def test_scan_directory_raises_for_file_path() -> None:
    with pytest.raises(NotADirectoryError):
        scan_directory(Path("demo_evidence") / "ticket_dump_march.csv")


def test_scanner_file_record_to_dict_is_json_safe() -> None:
    record = scan_directory(Path("demo_evidence"))[0]
    data = record.to_dict()

    assert data["path"] == record.path
    assert isinstance(data["modified_at"], str)
    json.dumps(data)

