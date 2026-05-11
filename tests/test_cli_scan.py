"""CLI tests for the scan command."""

from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from evidencepack.cli import app


runner = CliRunner()


def test_scan_cli_writes_inventory_and_prints_summary(tmp_path: Path) -> None:
    result = runner.invoke(
        app,
        ["scan", "demo_evidence", "--output-dir", str(tmp_path)],
    )

    assert result.exit_code == 0
    assert (tmp_path / "inventory.json").exists()
    assert "access_policy_v3.pdf" in result.output
    assert "firewall_rules_screenshot.png" in result.output
    assert "UNSUPPORTED_IMAGE" in result.output
    assert "inventory.json" in result.output


def test_scan_cli_missing_folder_exits_with_clear_error(tmp_path: Path) -> None:
    result = runner.invoke(
        app,
        ["scan", "missing_demo_evidence", "--output-dir", str(tmp_path)],
    )

    assert result.exit_code == 1
    assert "Scan failed" in result.output
    assert "Folder does not exist" in result.output
    assert "Traceback" not in result.output

