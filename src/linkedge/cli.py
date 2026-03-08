"""CLI interface for linkedge."""

from __future__ import annotations

import platform
import subprocess
from typing import Annotated

import typer

app = typer.Typer(
    name="linkedge",
    help="Generate LinkedIn profile banner images with QR codes.",
    no_args_is_help=True,
)


@app.command()
def generate(
    name: Annotated[str, typer.Option("--name", help="Your display name")],
    title: Annotated[str, typer.Option("--title", help="Your professional title")],
    url: Annotated[str, typer.Option("--url", help="LinkedIn profile URL for QR code")],
    color: Annotated[
        str, typer.Option("--color", help="Background color: hex code or palette name")
    ],
    tagline: Annotated[
        str | None, typer.Option("--tagline", help="Optional tagline or keywords")
    ] = None,
    qr_position: Annotated[
        str, typer.Option("--qr-position", help="QR code position: right/left/corner-br/corner-bl")
    ] = "right",
    pattern: Annotated[
        str, typer.Option("--pattern", help="Pattern overlay: none/grid/dots/lines")
    ] = "none",
    output: Annotated[
        str, typer.Option("--output", "-o", help="Output file path")
    ] = "banner.png",
    fmt: Annotated[
        str, typer.Option("--format", "-f", help="Output format: png/jpg")
    ] = "png",
    preview: Annotated[
        bool, typer.Option("--preview", help="Open image after generation")
    ] = False,
) -> None:
    """Generate a LinkedIn banner image."""
    from rich.console import Console

    from linkedge.exceptions import LinkedgeError
    from linkedge.generator import generate_banner, save_banner
    from linkedge.models import BannerConfig

    console = Console()

    try:
        config = BannerConfig(
            name=name,
            title=title,
            tagline=tagline,
            url=url,
            color=color,
            qr_position=qr_position,  # type: ignore[arg-type]
            pattern=pattern,  # type: ignore[arg-type]
            output=output,
            format=fmt,  # type: ignore[arg-type]
            preview=preview,
        )

        console.print("[bold]Generating banner...[/bold]")
        banner = generate_banner(config)
        path = save_banner(banner, config.output, config.format)
        console.print(f"[green]Banner saved to {path}[/green]")

        if preview:
            _open_preview(str(path))

    except LinkedgeError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(code=1) from None
    except Exception as e:
        console.print(f"[bold red]Unexpected error:[/bold red] {e}")
        raise typer.Exit(code=1) from None


@app.command()
def palettes() -> None:
    """List available color palettes."""
    from rich.console import Console
    from rich.table import Table

    from linkedge.palette import PALETTES

    console = Console()
    table = Table(title="Available Palettes")
    table.add_column("Name", style="bold")
    table.add_column("Hex")
    table.add_column("Preview")

    for name, hex_val in PALETTES.items():
        table.add_row(name, hex_val, f"[on {hex_val}]       [/on {hex_val}]")

    console.print(table)


def _open_preview(path: str) -> None:
    """Open the generated image with the system viewer."""
    system = platform.system()
    try:
        if system == "Darwin":
            subprocess.run(["open", path], check=True)
        elif system == "Linux":
            subprocess.run(["xdg-open", path], check=True)
        elif system == "Windows":
            subprocess.run(["start", path], check=True, shell=True)
    except (subprocess.SubprocessError, FileNotFoundError):
        pass  # Silently skip if preview fails


def main() -> None:
    """Entry point."""
    app()
