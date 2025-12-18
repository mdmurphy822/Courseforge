"""Catalog commands for Slideforge CLI."""

import json
from pathlib import Path

import click


@click.group()
def catalog():
    """Browse themes and examples catalog."""
    pass


@catalog.command('themes')
@click.option('--json-output', '-j', is_flag=True, help='Output as JSON')
@click.pass_context
def list_themes(ctx, json_output):
    """List available themes."""
    root = ctx.obj.get('root', Path(__file__).parent.parent.parent.parent)
    themes_dir = root / "templates" / "pptx" / "themes"

    if not themes_dir.exists():
        click.echo("No themes directory found", err=True)
        raise SystemExit(1)

    # Check for catalog.json first
    catalog_path = themes_dir / "catalog.json"
    if catalog_path.exists():
        with open(catalog_path) as f:
            catalog_data = json.load(f)
            themes = catalog_data.get('themes', [])
    else:
        # Scan for theme files
        themes = []
        for theme_file in themes_dir.glob("*.json"):
            if theme_file.name == "catalog.json":
                continue
            try:
                with open(theme_file) as f:
                    data = json.load(f)
                themes.append({
                    'id': theme_file.stem,
                    'name': data.get('name', theme_file.stem),
                    'description': data.get('description', ''),
                    'category': data.get('category', 'general'),
                    'config_path': str(theme_file.relative_to(root))
                })
            except json.JSONDecodeError:
                continue

    if json_output:
        click.echo(json.dumps({'themes': themes}, indent=2))
        return

    click.echo(f"\nAvailable Themes ({len(themes)})")
    click.echo("=" * 50)

    if not themes:
        click.echo("No themes found")
        return

    for theme in themes:
        click.echo(f"\n  {theme['name']}")
        click.echo(f"    ID: {theme['id']}")
        if theme.get('description'):
            click.echo(f"    {theme['description']}")
        if theme.get('category'):
            click.echo(f"    Category: {theme['category']}")


@catalog.command('examples')
@click.option('--json-output', '-j', is_flag=True, help='Output as JSON')
@click.pass_context
def list_examples(ctx, json_output):
    """List example presentations."""
    root = ctx.obj.get('root', Path(__file__).parent.parent.parent.parent)
    examples_dir = root / "templates" / "pptx" / "examples"

    if not examples_dir.exists():
        click.echo("No examples directory found", err=True)
        raise SystemExit(1)

    examples = []
    for example_file in examples_dir.glob("*.json"):
        try:
            with open(example_file) as f:
                data = json.load(f)
            metadata = data.get('metadata', {})
            sections = data.get('sections', [])
            slide_count = sum(len(s.get('slides', [])) for s in sections)

            examples.append({
                'filename': example_file.name,
                'title': metadata.get('title', example_file.stem),
                'description': metadata.get('subject', ''),
                'sections': len(sections),
                'slides': slide_count,
                'path': str(example_file.relative_to(root))
            })
        except json.JSONDecodeError:
            continue

    if json_output:
        click.echo(json.dumps({'examples': examples}, indent=2))
        return

    click.echo(f"\nExample Presentations ({len(examples)})")
    click.echo("=" * 50)

    if not examples:
        click.echo("No examples found")
        return

    for ex in examples:
        click.echo(f"\n  {ex['title']}")
        click.echo(f"    File: {ex['filename']}")
        if ex.get('description'):
            click.echo(f"    {ex['description']}")
        click.echo(f"    {ex['sections']} sections, {ex['slides']} slides")


@catalog.command('stats')
@click.pass_context
def show_stats(ctx):
    """Show repository statistics."""
    root = ctx.obj.get('root', Path(__file__).parent.parent.parent.parent)

    stats = {
        'themes': 0,
        'examples': 0,
        'exports': 0,
        'schemas': 0
    }

    # Count themes
    themes_dir = root / "templates" / "pptx" / "themes"
    if themes_dir.exists():
        stats['themes'] = len(list(themes_dir.glob("*.json"))) - (
            1 if (themes_dir / "catalog.json").exists() else 0
        )

    # Count examples
    examples_dir = root / "templates" / "pptx" / "examples"
    if examples_dir.exists():
        stats['examples'] = len(list(examples_dir.glob("*.json")))

    # Count exports
    exports_dir = root / "exports"
    if exports_dir.exists():
        stats['exports'] = len([d for d in exports_dir.iterdir() if d.is_dir()])

    # Count schemas
    schemas_dir = root / "schemas" / "presentation"
    if schemas_dir.exists():
        stats['schemas'] = len(list(schemas_dir.glob("*.json")))

    click.echo("\nSlideforge Repository Statistics")
    click.echo("=" * 50)
    click.echo(f"Themes: {stats['themes']}")
    click.echo(f"Examples: {stats['examples']}")
    click.echo(f"Exports: {stats['exports']}")
    click.echo(f"Schemas: {stats['schemas']}")
