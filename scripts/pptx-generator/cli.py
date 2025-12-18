#!/usr/bin/env python3
"""
Slideforge CLI - Command-line interface for PPTX generation and validation.

Usage:
    slideforge validate <file>          Validate presentation JSON
    slideforge inspect <file>           Show presentation statistics
    slideforge generate -i <json> -o <pptx>  Generate PPTX from JSON
    slideforge catalog themes           List available themes
    slideforge info                     Show version and configuration
"""

import sys
from pathlib import Path

import click

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from commands.validate import validate
from commands.inspect import inspect_cmd
from commands.generate import generate
from commands.catalog import catalog

__version__ = "1.0.0"


@click.group()
@click.version_option(version=__version__, prog_name="slideforge")
@click.pass_context
def cli(ctx):
    """Slideforge - AI-powered presentation generator.

    Generate professional PowerPoint presentations from structured content.
    """
    ctx.ensure_object(dict)
    ctx.obj['root'] = Path(__file__).parent.parent.parent


# Register command groups
cli.add_command(validate)
cli.add_command(inspect_cmd, name='inspect')
cli.add_command(generate)
cli.add_command(catalog)


@cli.command()
@click.pass_context
def info(ctx):
    """Show Slideforge version and configuration."""
    root = ctx.obj['root']

    click.echo(f"Slideforge v{__version__}")
    click.echo(f"Root: {root}")
    click.echo()

    # Show available schemas
    schemas_dir = root / "schemas" / "presentation"
    if schemas_dir.exists():
        schemas = list(schemas_dir.glob("*.json"))
        click.echo(f"Schemas: {len(schemas)} available")
        for schema in schemas:
            click.echo(f"  - {schema.name}")

    # Show available themes
    themes_dir = root / "templates" / "pptx" / "themes"
    if themes_dir.exists():
        themes = list(themes_dir.glob("*.json"))
        click.echo(f"\nThemes: {len(themes)} available")
        for theme in themes:
            click.echo(f"  - {theme.stem}")


def main():
    """Entry point for CLI."""
    cli(obj={})


if __name__ == "__main__":
    main()
