"""Inventory JSON helpers for scanned evidence files."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from evidencepack.models import FileRecord


def ensure_output_dir(output_dir: Path | str = Path("output")) -> Path:
    """Create and return the EvidencePack output directory."""
    path = Path(output_dir)
    path.mkdir(parents=True, exist_ok=True)
    return path


def inventory_path(output_dir: Path | str = Path("output")) -> Path:
    """Return the inventory path inside an output directory."""
    return ensure_output_dir(output_dir) / "inventory.json"


def records_to_inventory(records: list[FileRecord]) -> list[dict[str, Any]]:
    """Convert file records into JSON-safe inventory dictionaries."""
    return [record.to_dict() for record in records]


def write_inventory(
    records: list[FileRecord],
    output_dir: Path | str = Path("output"),
) -> Path:
    """Write inventory.json and return its path."""
    path = inventory_path(output_dir)
    inventory = records_to_inventory(records)
    path.write_text(json.dumps(inventory, indent=2), encoding="utf-8")
    return path


def load_inventory(output_dir: Path | str = Path("output")) -> list[dict[str, Any]]:
    """Load inventory.json from an output directory."""
    path = Path(output_dir) / "inventory.json"
    if not path.exists():
        raise FileNotFoundError(f"Inventory file does not exist: {path}")

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid inventory JSON: {path}") from exc

    if not isinstance(data, list):
        raise ValueError(f"Inventory JSON must contain a list: {path}")
    return data

