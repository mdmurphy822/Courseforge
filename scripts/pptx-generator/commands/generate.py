"""Generate commands for Slideforge CLI."""

import json
from pathlib import Path

import click


@click.command()
@click.option('--input', '-i', 'input_file', required=True,
              type=click.Path(exists=True), help='Input JSON file')
@click.option('--output', '-o', 'output_file', required=True,
              type=click.Path(), help='Output PPTX file')
@click.option('--theme', '-t', type=click.Path(exists=True),
              help='Theme JSON or PPTX template file')
@click.option('--validate/--no-validate', default=True,
              help='Validate input before generation')
@click.option('--force', '-f', is_flag=True,
              help='Overwrite output if exists')
@click.option('--no-cleanup', is_flag=True,
              help='Keep intermediate files after generation')
@click.pass_context
def generate(ctx, input_file, output_file, theme, validate, force, no_cleanup):
    """Generate PPTX from structured JSON content.

    Examples:
        slideforge generate -i content.json -o presentation.pptx
        slideforge generate -i content.json -o output.pptx -t theme.json
    """
    input_path = Path(input_file)
    output_path = Path(output_file)

    # Check output doesn't exist
    if output_path.exists() and not force:
        click.echo(f"Error: Output file already exists: {output_path}", err=True)
        click.echo("Use --force to overwrite", err=True)
        raise SystemExit(1)

    # Load input JSON
    try:
        with open(input_path) as f:
            content = json.load(f)
    except json.JSONDecodeError as e:
        click.echo(f"Error: Invalid JSON - {e}", err=True)
        raise SystemExit(1)

    # Validate if requested
    if validate:
        errors = _validate_content(content)
        if errors:
            click.echo(click.style("Validation errors:", fg='red'))
            for error in errors:
                click.echo(f"  - {error}")
            raise SystemExit(1)

    # Load theme if provided
    theme_config = None
    template_path = None

    if theme:
        theme_path = Path(theme)
        if theme_path.suffix == '.pptx':
            template_path = str(theme_path)
        elif theme_path.suffix == '.json':
            try:
                with open(theme_path) as f:
                    theme_config = json.load(f)
            except json.JSONDecodeError as e:
                click.echo(f"Error: Invalid theme JSON - {e}", err=True)
                raise SystemExit(1)

    # Import generator
    try:
        from pptx_generator import PPTXGenerator
    except ImportError:
        click.echo("Error: Could not import PPTXGenerator", err=True)
        raise SystemExit(1)

    # Generate presentation
    click.echo(f"Generating: {output_path.name}")

    try:
        generator = PPTXGenerator(template_path=template_path)

        if theme_config:
            _apply_theme_config(generator, theme_config)

        generator.create_presentation(content)
        generator.save(str(output_path))

        click.echo(click.style(f"Created: {output_path}", fg='green'))

        # Show summary
        sections = content.get('sections', [])
        slide_count = sum(len(s.get('slides', [])) for s in sections)
        click.echo(f"  Sections: {len(sections)}")
        click.echo(f"  Slides: {slide_count}")

        # Cleanup intermediate files unless --no-cleanup specified
        if not no_cleanup:
            _perform_cleanup(output_path, ctx)

    except Exception as e:
        click.echo(click.style(f"Error: {e}", fg='red'), err=True)
        raise SystemExit(1)


def _validate_content(content: dict) -> list:
    """Basic content validation."""
    errors = []

    if 'metadata' not in content:
        errors.append("Missing 'metadata' field")
    elif 'title' not in content.get('metadata', {}):
        errors.append("Missing 'metadata.title' field")

    if 'sections' not in content:
        errors.append("Missing 'sections' field")
    elif not content.get('sections'):
        errors.append("Presentation has no sections")

    return errors


def _apply_theme_config(generator, config: dict):
    """Apply theme configuration to generator."""
    colors = config.get('colors', {})
    if colors:
        if hasattr(generator, 'theme_colors'):
            for key, value in colors.items():
                if hasattr(generator.theme_colors, key):
                    setattr(generator.theme_colors, key, value)


def _perform_cleanup(output_path: Path, ctx):
    """Perform cleanup of intermediate files after generation.

    Cleans both the project export folder and the shared runtime directory.
    """
    try:
        from cleanup import cleanup_project, cleanup_runtime, CleanupError
    except ImportError:
        # Cleanup module not available, skip silently
        return

    # Determine project folder from output path
    # Expected structure: exports/YYYYMMDD_HHMMSS_topic/03_final_output/presentation.pptx
    # or: exports/YYYYMMDD_HHMMSS_topic/presentation.pptx
    project_folder = output_path.parent
    if project_folder.name == "03_final_output":
        project_folder = project_folder.parent

    # Only cleanup if in an exports-style timestamped folder
    if not project_folder.name[0:8].isdigit():
        # Not a timestamped project folder, skip cleanup
        return

    # Get project root for runtime folder
    root = ctx.obj.get('root', Path(__file__).parent.parent.parent.parent)
    runtime_folder = root / "runtime"

    try:
        # Cleanup project folder
        final_pptx = cleanup_project(project_folder)
        click.echo(click.style("  Cleaned intermediate files", fg='cyan'))

        # Cleanup runtime folder
        if runtime_folder.exists():
            count = cleanup_runtime(runtime_folder)
            if count > 0:
                click.echo(click.style(f"  Cleaned {count} runtime items", fg='cyan'))

    except CleanupError as e:
        click.echo(click.style(f"  Cleanup skipped: {e}", fg='yellow'), err=True)
