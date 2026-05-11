"""Recursive evidence file scanner with basic metadata extraction."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd
import pdfplumber

from evidencepack.models import FileRecord, FileStatus, FileType


EXTENSION_TYPES = {
    ".pdf": FileType.PDF,
    ".xlsx": FileType.XLSX,
    ".xls": FileType.XLS,
    ".csv": FileType.CSV,
    ".docx": FileType.DOCX,
    ".png": FileType.PNG,
    ".jpg": FileType.JPG,
    ".jpeg": FileType.JPG,
    ".txt": FileType.TXT,
}


def detect_file_type(path: Path) -> FileType:
    """Detect a file type from its extension."""
    return EXTENSION_TYPES.get(path.suffix.lower(), FileType.UNSUPPORTED)


def status_for_file_type(file_type: FileType) -> FileStatus:
    """Return the initial scanner status for a file type."""
    if file_type in {FileType.PNG, FileType.JPG}:
        return FileStatus.UNSUPPORTED_IMAGE
    if file_type in {FileType.UNSUPPORTED, FileType.UNSUPPORTED_IMAGE}:
        return FileStatus.UNSUPPORTED
    return FileStatus.PENDING


def is_stale(
    modified_at: datetime,
    stale_days: int = 90,
    now: datetime | None = None,
) -> bool:
    """Return whether a timestamp is older than the stale-day threshold."""
    reference_time = now or datetime.now()
    return (reference_time - modified_at).days > stale_days


def extract_basic_metadata(path: Path, file_type: FileType) -> dict[str, Any]:
    """Extract simple file-level metadata for supported document types."""
    if file_type == FileType.PDF:
        with pdfplumber.open(path) as pdf:
            return {"page_count": len(pdf.pages)}
    if file_type in {FileType.XLSX, FileType.XLS}:
        excel_file = pd.ExcelFile(path)
        return {"sheet_count": len(excel_file.sheet_names)}
    if file_type == FileType.CSV:
        dataframe = pd.read_csv(path)
        return {"row_count": len(dataframe)}
    return {}


def build_file_record(path: Path, root: Path, stale_days: int = 90) -> FileRecord:
    """Build a FileRecord for one filesystem path."""
    file_type = detect_file_type(path)
    relative_path = _relative_posix_path(path, root)
    filename = path.name
    status = status_for_file_type(file_type)
    size_bytes = 0
    modified_at = datetime.fromtimestamp(0)
    metadata: dict[str, Any] = {}

    try:
        stat = path.stat()
        size_bytes = stat.st_size
        modified_at = datetime.fromtimestamp(stat.st_mtime)
        metadata = extract_basic_metadata(path, file_type)
        return FileRecord(
            path=relative_path,
            filename=filename,
            file_type=file_type,
            size_bytes=size_bytes,
            modified_at=modified_at,
            status=status,
            page_count=metadata.get("page_count"),
            sheet_count=metadata.get("sheet_count"),
            row_count=metadata.get("row_count"),
            is_stale=is_stale(modified_at, stale_days=stale_days),
            metadata=metadata,
        )
    except Exception as exc:
        return FileRecord(
            path=relative_path,
            filename=filename,
            file_type=file_type,
            size_bytes=size_bytes,
            modified_at=modified_at,
            status=FileStatus.UNREADABLE,
            is_stale=is_stale(modified_at, stale_days=stale_days),
            error=str(exc),
            metadata=metadata,
        )


def scan_directory(folder: Path | str, stale_days: int = 90) -> list[FileRecord]:
    """Recursively scan a directory and return deterministic FileRecord objects."""
    root = Path(folder)
    if not root.exists():
        raise FileNotFoundError(f"Folder does not exist: {root}")
    if not root.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {root}")

    files = sorted((path for path in root.rglob("*") if path.is_file()), key=lambda p: _relative_posix_path(p, root))
    return [build_file_record(path, root, stale_days=stale_days) for path in files]


def _relative_posix_path(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.name

