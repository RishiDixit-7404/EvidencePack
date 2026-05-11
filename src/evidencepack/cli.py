"""Command line interface for EvidencePack."""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from evidencepack.inventory import write_inventory
from evidencepack.scanner import scan_directory

DISCLAIMER = (
    "EvidencePack is for evidence organisation and pre-review only; "
    "it is not an audit certification tool."
)

app = typer.Typer(
    help=(
        "Local-first audit evidence binder CLI and MCP server.\n\n"
        f"{DISCLAIMER}"
    )
)
console = Console(width=140)


@app.command()
def scan(
    folder: Path,
    controls: Optional[Path] = None,
    threshold: float = 0.6,
    stale_days: int = 90,
    no_llm: bool = False,
    output_dir: Path = Path("output"),
) -> None:
    """Scan an evidence folder and write inventory.json."""
    _ = controls, threshold
    try:
        records = scan_directory(folder, stale_days=stale_days)
        inventory_file = write_inventory(records, output_dir=output_dir)
    except (FileNotFoundError, NotADirectoryError, OSError) as exc:
        console.print(f"[bold red]Scan failed:[/bold red] {exc}")
        raise typer.Exit(code=1) from None

    table = Table(title="Evidence Inventory")
    table.add_column("File", no_wrap=True)
    table.add_column("Type", no_wrap=True)
    table.add_column("Size Bytes", justify="right")
    table.add_column("Modified", no_wrap=True)
    table.add_column("Status", no_wrap=True)
    table.add_column("Metadata")

    for record in records:
        metadata = ", ".join(f"{key}={value}" for key, value in record.metadata.items())
        table.add_row(
            record.path,
            record.file_type.value,
            str(record.size_bytes),
            record.modified_at.isoformat(timespec="seconds"),
            record.status.value,
            metadata or "-",
        )

    console.print(table)
    console.print(
        Panel(
            "\n".join(
                [
                    f"Total files: {len(records)}",
                    f"Inventory: {inventory_file}",
                    f"Stale threshold: {stale_days} days",
                    f"LLM disabled: {no_llm}",
                ]
            ),
            title="Scan Complete",
        )
    )


@app.command()
def report(folder: Path, output_dir: Path = Path("output")) -> None:
    """Placeholder for generating reports."""
    console.print(
        "[bold cyan]Report placeholder[/bold cyan]: "
        f"folder={folder}, output_dir={output_dir}"
    )


@app.command()
def gaps(folder: Path) -> None:
    """Placeholder for gap analysis."""
    console.print(f"[bold cyan]Gaps placeholder[/bold cyan]: folder={folder}")


@app.command()
def mcp(folder: Path, port: int = 8765) -> None:
    """Placeholder for starting the MCP server."""
    console.print(
        "[bold cyan]MCP placeholder[/bold cyan]: "
        f"folder={folder}, port={port}"
    )


@app.command()
def demo() -> None:
    """Placeholder for demo project creation."""
    console.print("[bold cyan]Demo placeholder[/bold cyan]: demo setup will be added in Task 02.")


if __name__ == "__main__":
    app()
