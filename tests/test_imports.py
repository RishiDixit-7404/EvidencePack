"""Smoke tests for the initial EvidencePack scaffold."""


def test_cli_imports() -> None:
    from evidencepack.cli import app

    assert app is not None

