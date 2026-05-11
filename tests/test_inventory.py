"""Tests for inventory JSON output."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from evidencepack.inventory import load_inventory, write_inventory
from evidencepack.scanner import scan_directory


def test_write_inventory_writes_valid_json_to_output_dir(tmp_path: Path) -> None:
    records = scan_directory("demo_evidence")

    path = write_inventory(records, output_dir=tmp_path)

    assert path == tmp_path / "inventory.json"
    assert path.exists()
    data = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(data, list)
    assert data == load_inventory(tmp_path)


def test_inventory_contains_json_safe_demo_scan_values(tmp_path: Path) -> None:
    records = scan_directory("demo_evidence")
    path = write_inventory(records, output_dir=tmp_path)
    inventory = json.loads(path.read_text(encoding="utf-8"))
    by_path = {record["path"]: record for record in inventory}

    assert len(inventory) == 7
    for record in inventory:
        assert {
            "path",
            "filename",
            "file_type",
            "size_bytes",
            "modified_at",
            "status",
            "metadata",
        }.issubset(record)
        json.dumps(record)

    assert by_path["firewall_rules_screenshot.png"]["status"] == "UNSUPPORTED_IMAGE"
    assert by_path["access_policy_v3.pdf"]["page_count"] == 4
    assert by_path["access_policy_v3.pdf"]["metadata"]["page_count"] == 4
    assert by_path["user_access_export_Q1.xlsx"]["sheet_count"] >= 1
    assert by_path["ticket_dump_march.csv"]["row_count"] >= 1


def test_load_inventory_raises_when_missing(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        load_inventory(tmp_path)


def test_load_inventory_raises_for_invalid_json(tmp_path: Path) -> None:
    (tmp_path / "inventory.json").write_text("{not-json", encoding="utf-8")

    with pytest.raises(ValueError, match="Invalid inventory JSON"):
        load_inventory(tmp_path)


def test_load_inventory_raises_when_json_is_not_list(tmp_path: Path) -> None:
    (tmp_path / "inventory.json").write_text('{"path": "demo"}', encoding="utf-8")

    with pytest.raises(ValueError, match="must contain a list"):
        load_inventory(tmp_path)

