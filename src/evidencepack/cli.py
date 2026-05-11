"""Command line interface for EvidencePack."""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

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
console = Console()


@app.command()
def scan(
    folder: Path,
    controls: Optional[Path] = None,
    threshold: float = 0.6,
    stale_days: int = 90,
    no_llm: bool = False,
) -> None:
    """Placeholder for scanning evidence folders."""
    console.print(
        "[bold cyan]Scan placeholder[/bold cyan]: "
        f"folder={folder}, controls={controls}, threshold={threshold}, "
        f"stale_days={stale_days}, no_llm={no_llm}"
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

