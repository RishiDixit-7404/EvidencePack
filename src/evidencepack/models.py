"""Core data models shared across EvidencePack workflows."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field, is_dataclass
from datetime import datetime
from enum import Enum
from typing import Any


class FileType(str, Enum):
    """Supported evidence file types."""

    PDF = "PDF"
    XLSX = "XLSX"
    XLS = "XLS"
    CSV = "CSV"
    DOCX = "DOCX"
    PNG = "PNG"
    JPG = "JPG"
    TXT = "TXT"
    UNSUPPORTED = "UNSUPPORTED"
    UNSUPPORTED_IMAGE = "UNSUPPORTED_IMAGE"


class FileStatus(str, Enum):
    """Extraction status for an evidence file."""

    PENDING = "PENDING"
    EXTRACTED = "EXTRACTED"
    UNSUPPORTED = "UNSUPPORTED"
    UNSUPPORTED_IMAGE = "UNSUPPORTED_IMAGE"
    UNREADABLE = "UNREADABLE"


class GapStatus(str, Enum):
    """Evidence coverage status for a control."""

    COMPLETE = "COMPLETE"
    PARTIAL = "PARTIAL"
    MISSING = "MISSING"
    STALE = "STALE"
    AMBIGUOUS = "AMBIGUOUS"


class MatchMethod(str, Enum):
    """Method used to match evidence to a control."""

    KEYWORD = "keyword"
    LLM = "llm"
    BOTH = "both"


@dataclass
class FileRecord:
    """Metadata and extraction state for one evidence file."""

    path: str
    filename: str
    file_type: FileType
    size_bytes: int
    modified_at: datetime
    status: FileStatus = FileStatus.PENDING
    page_count: int | None = None
    sheet_count: int | None = None
    row_count: int | None = None
    is_stale: bool = False
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-safe dictionary representation."""
        return serialize_model(self)


@dataclass
class ControlRecord:
    """Control checklist row used for evidence matching."""

    control_id: str
    description: str
    required_evidence_type: str
    domain: str
    keywords: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-safe dictionary representation."""
        return serialize_model(self)


@dataclass
class MatchResult:
    """A candidate evidence match for a control."""

    control_id: str
    filename: str
    confidence: float
    source_ref: str
    method: MatchMethod
    reason: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.confidence = ensure_confidence(self.confidence)

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-safe dictionary representation."""
        return serialize_model(self)


@dataclass
class ControlCitation:
    """Evidence coverage summary and citations for one control."""

    control_id: str
    status: GapStatus
    matches: list[MatchResult] = field(default_factory=list)
    gap_notes: str | None = None
    suggested_evidence_type: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-safe dictionary representation."""
        return serialize_model(self)


def serialize_model(value: Any) -> Any:
    """Recursively convert EvidencePack models into JSON-safe values."""
    if is_dataclass(value) and not isinstance(value, type):
        return serialize_model(asdict(value))
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, list):
        return [serialize_model(item) for item in value]
    if isinstance(value, tuple):
        return [serialize_model(item) for item in value]
    if isinstance(value, dict):
        return {
            serialize_model(key): serialize_model(item)
            for key, item in value.items()
        }
    return value


def ensure_confidence(value: float) -> float:
    """Validate and normalize a match confidence score."""
    confidence = float(value)
    if confidence < 0.0 or confidence > 1.0:
        raise ValueError("confidence must be between 0.0 and 1.0")
    return confidence

