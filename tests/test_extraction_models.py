"""Tests for shared extraction result models."""

from __future__ import annotations

import json
from datetime import datetime

from evidencepack.models import (
    ChunkType,
    ExtractedChunk,
    ExtractionResult,
    FileStatus,
    FileType,
    chunk_text_for_matching,
    extraction_result_text,
)


def test_chunk_type_contains_exact_values() -> None:
    assert [chunk_type.value for chunk_type in ChunkType] == [
        "text",
        "table",
        "sheet",
        "csv",
        "docx_paragraph",
    ]


def test_extracted_chunk_to_dict_serializes_enums() -> None:
    chunk = ExtractedChunk(
        file_path="demo_evidence/access_policy_v3.pdf",
        filename="access_policy_v3.pdf",
        file_type=FileType.PDF,
        chunk_type=ChunkType.TEXT,
        source_ref="page 1",
        text="Quarterly access review clause.",
    )

    data = chunk.to_dict()

    assert data["file_type"] == "PDF"
    assert data["chunk_type"] == "text"
    assert data["text"] == "Quarterly access review clause."


def test_extraction_result_to_dict_serializes_nested_chunks() -> None:
    extracted_at = datetime(2026, 5, 11, 13, 30, 0)
    result = ExtractionResult(
        file_path="demo_evidence/ticket_dump_march.csv",
        filename="ticket_dump_march.csv",
        file_type=FileType.CSV,
        chunks=[
            ExtractedChunk(
                file_path="demo_evidence/ticket_dump_march.csv",
                filename="ticket_dump_march.csv",
                file_type=FileType.CSV,
                chunk_type=ChunkType.CSV,
                source_ref="rows 1-5",
                table=[["Ticket ID", "Type"], ["IT-2026-0314", "Termination"]],
                metadata={"extracted_at": extracted_at},
            )
        ],
        extracted_at=extracted_at,
        status=FileStatus.EXTRACTED,
    )

    data = result.to_dict()

    assert data["file_type"] == "CSV"
    assert data["status"] == "EXTRACTED"
    assert data["extracted_at"] == "2026-05-11T13:30:00"
    assert data["chunks"][0]["chunk_type"] == "csv"
    assert data["chunks"][0]["metadata"]["extracted_at"] == "2026-05-11T13:30:00"
    json.dumps(data)


def test_chunk_text_for_matching_returns_normal_text() -> None:
    chunk = ExtractedChunk(
        file_path="demo_evidence/meeting_notes_kickoff.docx",
        filename="meeting_notes_kickoff.docx",
        file_type=FileType.DOCX,
        chunk_type=ChunkType.DOCX_PARAGRAPH,
        source_ref="paragraph 4",
        text="Follow-up needed from the client.",
    )

    assert chunk_text_for_matching(chunk) == "Follow-up needed from the client."


def test_chunk_text_for_matching_flattens_table_chunks() -> None:
    chunk = ExtractedChunk(
        file_path="demo_evidence/user_access_export_Q1.xlsx",
        filename="user_access_export_Q1.xlsx",
        file_type=FileType.XLSX,
        chunk_type=ChunkType.TABLE,
        source_ref="sheet Q1 User Access",
        table=[
            ["Username", "Role", "Access Level"],
            ["priya.narayan", "IT Administrator", "Privileged"],
            ["taylor.morgan", None, "Disabled"],
        ],
    )

    assert chunk_text_for_matching(chunk) == (
        "Username | Role | Access Level\n"
        "priya.narayan | IT Administrator | Privileged\n"
        "taylor.morgan | Disabled"
    )


def test_extraction_result_text_joins_multiple_chunks() -> None:
    result = ExtractionResult(
        file_path="demo_evidence/access_policy_v3.pdf",
        filename="access_policy_v3.pdf",
        file_type=FileType.PDF,
        chunks=[
            ExtractedChunk(
                file_path="demo_evidence/access_policy_v3.pdf",
                filename="access_policy_v3.pdf",
                file_type=FileType.PDF,
                chunk_type=ChunkType.TEXT,
                source_ref="page 1",
                text="Quarterly access reviews are performed.",
            ),
            ExtractedChunk(
                file_path="demo_evidence/access_policy_v3.pdf",
                filename="access_policy_v3.pdf",
                file_type=FileType.PDF,
                chunk_type=ChunkType.TABLE,
                source_ref="page 4",
                table=[["Password Policy"], ["Minimum twelve characters"]],
            ),
            ExtractedChunk(
                file_path="demo_evidence/access_policy_v3.pdf",
                filename="access_policy_v3.pdf",
                file_type=FileType.PDF,
                chunk_type=ChunkType.TEXT,
                source_ref="empty",
            ),
        ],
    )

    assert extraction_result_text(result) == (
        "Quarterly access reviews are performed.\n"
        "Password Policy\n"
        "Minimum twelve characters"
    )

