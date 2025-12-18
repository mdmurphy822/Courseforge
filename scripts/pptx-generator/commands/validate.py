"""Validation commands for Slideforge CLI."""

import json
from pathlib import Path

import click

# Import validators when available
try:
    from validators.schema_validator import validate_schema
    from validators.quality_validator import validate_quality
except ImportError:
    validate_schema = None
    validate_quality = None


@click.group()
def validate():
    """Validate presentation files."""
    pass


@validate.command('schema')
@click.argument('file', type=click.Path(exists=True))
@click.option('--strict', is_flag=True, help='Enable strict validation mode')
@click.pass_context
def validate_schema_cmd(ctx, file, strict):
    """Validate JSON file against presentation schema.

    FILE: Path to presentation JSON file
    """
    file_path = Path(file)

    try:
        with open(file_path) as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        click.echo(f"Error: Invalid JSON - {e}", err=True)
        raise SystemExit(1)

    root = ctx.obj.get('root', Path(__file__).parent.parent.parent.parent)
    schema_path = root / "schemas" / "presentation" / "presentation_schema.json"

    if not schema_path.exists():
        click.echo(f"Error: Schema not found at {schema_path}", err=True)
        raise SystemExit(1)

    # Use validator if available, otherwise basic check
    if validate_schema:
        result = validate_schema(data, schema_path, strict=strict)
        if result.valid:
            click.echo(click.style("Schema validation passed", fg='green'))
        else:
            click.echo(click.style("Schema validation failed", fg='red'))
            for error in result.errors:
                click.echo(f"  - {error}")
            raise SystemExit(1)
    else:
        # Basic validation using jsonschema
        try:
            import jsonschema
            with open(schema_path) as f:
                schema = json.load(f)
            jsonschema.validate(data, schema)
            click.echo(click.style("Schema validation passed", fg='green'))
        except jsonschema.ValidationError as e:
            click.echo(click.style("Schema validation failed", fg='red'))
            click.echo(f"  - {e.message}")
            raise SystemExit(1)


@validate.command('presentation')
@click.argument('file', type=click.Path(exists=True))
@click.option('--verbose', '-v', is_flag=True, help='Show detailed output')
@click.pass_context
def validate_presentation_cmd(ctx, file, verbose):
    """Full presentation validation including 6x6 rule.

    FILE: Path to presentation JSON file
    """
    file_path = Path(file)

    try:
        with open(file_path) as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        click.echo(f"Error: Invalid JSON - {e}", err=True)
        raise SystemExit(1)

    errors = []
    warnings = []

    # Check metadata
    if 'metadata' not in data:
        errors.append("Missing required 'metadata' field")
    elif 'title' not in data.get('metadata', {}):
        errors.append("Missing required 'metadata.title' field")

    # Check sections
    sections = data.get('sections', [])
    if not sections:
        errors.append("Presentation has no sections")

    total_slides = 0
    six_six_violations = 0

    for si, section in enumerate(sections):
        slides = section.get('slides', [])
        total_slides += len(slides)

        for sli, slide in enumerate(slides):
            slide_id = f"Section {si+1}, Slide {sli+1}"

            # Check slide type
            slide_type = slide.get('type', 'content')

            # Check 6x6 rule for bullet lists
            content = slide.get('content', {})
            bullets = content.get('bullets', [])

            if len(bullets) > 6:
                six_six_violations += 1
                warnings.append(f"{slide_id}: {len(bullets)} bullets (exceeds 6)")

            for bi, bullet in enumerate(bullets):
                word_count = len(bullet.split())
                if word_count > 6:
                    six_six_violations += 1
                    warnings.append(f"{slide_id}, bullet {bi+1}: {word_count} words (exceeds 6)")

            # Check left/right columns
            for col in ['left', 'right']:
                col_items = content.get(col, [])
                if len(col_items) > 6:
                    six_six_violations += 1
                    warnings.append(f"{slide_id}: {col} column has {len(col_items)} items (exceeds 6)")

            # Check speaker notes presence
            if not slide.get('notes') and slide_type in ['content', 'two_content', 'comparison']:
                if verbose:
                    warnings.append(f"{slide_id}: No speaker notes")

    # Report results
    click.echo(f"\nValidation Results for: {file_path.name}")
    click.echo("=" * 50)
    click.echo(f"Sections: {len(sections)}")
    click.echo(f"Total slides: {total_slides}")
    click.echo(f"6x6 violations: {six_six_violations}")

    if errors:
        click.echo(click.style(f"\nErrors: {len(errors)}", fg='red'))
        for error in errors:
            click.echo(f"  - {error}")

    if warnings and verbose:
        click.echo(click.style(f"\nWarnings: {len(warnings)}", fg='yellow'))
        for warning in warnings:
            click.echo(f"  - {warning}")

    if errors:
        click.echo(click.style("\nValidation FAILED", fg='red', bold=True))
        raise SystemExit(1)
    elif six_six_violations > 0:
        click.echo(click.style(f"\nValidation PASSED with {six_six_violations} warnings", fg='yellow', bold=True))
    else:
        click.echo(click.style("\nValidation PASSED", fg='green', bold=True))


@validate.command('theme')
@click.argument('file', type=click.Path(exists=True))
@click.pass_context
def validate_theme_cmd(ctx, file):
    """Validate theme configuration file.

    FILE: Path to theme JSON file
    """
    file_path = Path(file)

    try:
        with open(file_path) as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        click.echo(f"Error: Invalid JSON - {e}", err=True)
        raise SystemExit(1)

    root = ctx.obj.get('root', Path(__file__).parent.parent.parent.parent)
    schema_path = root / "schemas" / "presentation" / "theme_schema.json"

    if schema_path.exists():
        try:
            import jsonschema
            with open(schema_path) as f:
                schema = json.load(f)
            jsonschema.validate(data, schema)
            click.echo(click.style("Theme validation passed", fg='green'))
        except jsonschema.ValidationError as e:
            click.echo(click.style("Theme validation failed", fg='red'))
            click.echo(f"  - {e.message}")
            raise SystemExit(1)
    else:
        # Basic checks
        required = ['name', 'colors']
        missing = [r for r in required if r not in data]
        if missing:
            click.echo(click.style("Theme validation failed", fg='red'))
            click.echo(f"  Missing required fields: {', '.join(missing)}")
            raise SystemExit(1)
        click.echo(click.style("Theme validation passed (basic)", fg='green'))
