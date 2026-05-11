# EvidencePack

EvidencePack is a local-first audit evidence binder CLI and MCP server for organising evidence folders, preparing pre-review inventories, identifying coverage gaps, and producing future review-ready reports without requiring a cloud backend.

## Install

```bash
python -m pip install -e ".[dev]"
```

## Quickstart

```bash
python scripts/create_demo.py
evidencepack scan ./demo_evidence
evidencepack report ./demo_evidence
evidencepack gaps ./demo_evidence
evidencepack mcp ./demo_evidence --port 8765
evidencepack demo
```

## Demo Evidence

The `demo_evidence/` folder contains seven small synthetic files used for scanner, extractor, matcher, report, and MCP development. Regenerate it at any time with:

```bash
python scripts/create_demo.py
```

## Architecture

EvidencePack will be organised around a Typer CLI, local folder scanner, document extractors, control matching engine, gap analysis, report writers, and an MCP server surface. Implementation details will be added as the scanner, extraction, matching, reporting, and MCP tasks are completed.

## Disclaimer

EvidencePack is for evidence organisation and pre-review only. It is not an audit certification tool and does not replace auditor judgment, formal audit procedures, or professional assurance services.
