#!/usr/bin/env python3
"""
Pipeline CLI for Slideforge

Command-line interface for the end-to-end presentation generation pipeline.

Usage:
    # Full pipeline - generate presentation from content
    python -m scripts.pipeline generate input.md output.pptx --theme corporate

    # Validate presentation JSON
    python -m scripts.pipeline validate presentation.json

    # Resume from checkpoint
    python -m scripts.pipeline generate input.md output.pptx --resume-from transformation

    # Extract and profile content only
    python -m scripts.pipeline extract input.md --output semantic.json

    # List available templates
    python -m scripts.pipeline templates
"""

import argparse
import sys
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional

# Add parent directory for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.pipeline.orchestrator import (
    Pipeline,
    PipelineConfig,
    PipelineResult,
    run_pipeline
)
from scripts.pipeline.manifest import PipelineManifest

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def cmd_generate(args) -> int:
    """Execute the full generation pipeline."""
    input_path = Path(args.input)
    output_path = Path(args.output)

    if not input_path.exists():
        logger.error(f"Input file not found: {input_path}")
        return 1

    # Build configuration
    config = PipelineConfig(
        input_path=str(input_path),
        output_path=str(output_path),
        template_name=args.theme,
        template_path=args.template,
        generate_notes=not args.no_notes,
        strict_validation=args.strict,
        save_intermediates=args.save_intermediates,
        manifest_path=args.manifest
    )

    logger.info(f"Starting pipeline: {input_path} -> {output_path}")

    # Run pipeline
    try:
        if args.resume_from:
            result = run_pipeline(config, resume_from=args.resume_from)
        else:
            result = run_pipeline(config)

        # Report results
        if result.success:
            logger.info(f"Pipeline completed successfully!")
            logger.info(f"Output: {result.output_path}")
            logger.info(f"Total slides: {result.slide_count}")
            logger.info(f"Quality score: {result.quality_score:.1f}/100")

            if result.warnings:
                logger.warning(f"Warnings ({len(result.warnings)}):")
                for warning in result.warnings[:5]:
                    logger.warning(f"  - {warning}")
                if len(result.warnings) > 5:
                    logger.warning(f"  ... and {len(result.warnings) - 5} more")

            return 0
        else:
            logger.error("Pipeline failed!")
            for error in result.errors:
                logger.error(f"  - {error}")
            return 1

    except Exception as e:
        logger.exception(f"Pipeline error: {e}")
        return 1


def cmd_validate(args) -> int:
    """Validate a presentation JSON file."""
    input_path = Path(args.input)

    if not input_path.exists():
        logger.error(f"Input file not found: {input_path}")
        return 1

    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            presentation = json.load(f)
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON: {e}")
        return 1

    # Import validators
    from scripts.validators import (
        StructureValidator,
        SchemaValidator,
        SemanticValidator
    )

    logger.info(f"Validating: {input_path}")

    # Level 1: Structure validation
    logger.info("Level 1: Structure validation...")
    structure_validator = StructureValidator(strict=args.strict)
    structure_result = structure_validator.validate(presentation)

    if not structure_result.valid:
        logger.error("Structure validation failed!")
        for error in structure_result.errors:
            logger.error(f"  [{error.severity.value}] {error.path}: {error.message}")
        if not args.continue_on_error:
            return 1
    else:
        logger.info(f"  Passed ({structure_result.warning_count} warnings)")

    # Level 2: Schema validation
    logger.info("Level 2: Schema validation...")
    schema_path = Path(__file__).parent.parent.parent / "schemas" / "presentation" / "presentation_schema.json"
    schema_validator = SchemaValidator(schema_path=schema_path if schema_path.exists() else None)
    schema_result = schema_validator.validate(presentation)

    if not schema_result.valid:
        logger.error("Schema validation failed!")
        for error in schema_result.errors:
            logger.error(f"  {error.path}: {error.message}")
        if not args.continue_on_error:
            return 1
    else:
        logger.info(f"  Passed ({schema_result.error_count} errors)")

    # Level 3: Semantic validation
    logger.info("Level 3: Semantic validation...")
    semantic_validator = SemanticValidator()
    semantic_result = semantic_validator.validate(presentation, strict=args.strict)

    if not semantic_result.valid:
        logger.warning("Semantic validation found issues:")
        for issue in semantic_result.issues[:10]:
            logger.warning(f"  [{issue.severity.value}] {issue.location}: {issue.message}")
        if len(semantic_result.issues) > 10:
            logger.warning(f"  ... and {len(semantic_result.issues) - 10} more")

    # Print summary
    metrics = semantic_result.metrics
    logger.info("\n=== Validation Summary ===")
    logger.info(f"Total slides: {metrics.total_slides}")
    logger.info(f"Sections: {metrics.total_sections}")
    logger.info(f"Slide types used: {', '.join(metrics.slide_types_used)}")
    logger.info(f"Notes coverage: {metrics.notes_coverage:.0%}")
    logger.info(f"6x6 violations: {metrics.six_six_violations}")
    logger.info(f"Overall score: {metrics.overall_score:.1f}/100")

    if args.output:
        # Save validation report
        report = {
            "input": str(input_path),
            "timestamp": datetime.now().isoformat(),
            "structure": structure_result.to_dict(),
            "schema": schema_result.to_dict(),
            "semantic": semantic_result.to_dict()
        }

        output_path = Path(args.output)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        logger.info(f"Report saved: {output_path}")

    # Return based on overall validity
    if structure_result.valid and schema_result.valid:
        if semantic_result.valid or not args.strict:
            return 0
    return 1


def cmd_extract(args) -> int:
    """Extract and profile content without generating presentation."""
    input_path = Path(args.input)

    if not input_path.exists():
        logger.error(f"Input file not found: {input_path}")
        return 1

    # Import extractor
    try:
        from scripts.semantic_structure_extractor import SemanticStructureExtractor
    except ImportError:
        # Try alternate import path
        sys.path.insert(0, str(Path(__file__).parent.parent / "semantic-structure-extractor"))
        from semantic_structure_extractor import SemanticStructureExtractor

    logger.info(f"Extracting content from: {input_path}")

    # Read input
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Detect format and extract
    extractor = SemanticStructureExtractor()

    if args.profile:
        # Full extraction with profiling
        result = extractor.extract_with_profiling(content)
        logger.info(f"Extracted with profiling")

        if "profile" in result:
            profile = result["profile"]
            logger.info(f"  Difficulty: {profile.get('difficulty_level', 'unknown')}")
            logger.info(f"  Concepts: {len(profile.get('concepts', []))}")
            logger.info(f"  Word count: {profile.get('word_count', 0)}")
    else:
        result = extractor.extract(content)
        logger.info(f"Basic extraction complete")

    # Save output
    output_path = Path(args.output) if args.output else input_path.with_suffix('.semantic.json')

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    logger.info(f"Output saved: {output_path}")
    return 0


def cmd_transform(args) -> int:
    """Transform semantic structure to presentation format."""
    input_path = Path(args.input)

    if not input_path.exists():
        logger.error(f"Input file not found: {input_path}")
        return 1

    # Load semantic structure
    with open(input_path, 'r', encoding='utf-8') as f:
        semantic = json.load(f)

    # Import transformer
    from scripts.transformers import SemanticToPresentationTransformer, TransformationConfig
    from scripts.transformers.notes_generator import NoteStyle
    from scripts.transformers.content_splitter import SplitStrategy

    # Configure transformer
    config = TransformationConfig(
        max_bullets=args.max_bullets,
        max_words_per_bullet=args.max_words,
        generate_notes=not args.no_notes,
        notes_style=NoteStyle(args.notes_style),
        split_strategy=SplitStrategy(args.split_strategy),
        create_section_headers=not args.no_section_headers,
        create_title_slide=not args.no_title_slide
    )

    transformer = SemanticToPresentationTransformer(config)
    result = transformer.transform(semantic, str(input_path))

    # Save output
    output_path = Path(args.output) if args.output else input_path.with_suffix('.presentation.json')
    result.save(output_path)

    # Report
    logger.info(f"Transformation complete!")
    logger.info(f"  Slides: {result.quality_metrics.get('totalSlides', 0)}")
    logger.info(f"  Sections: {result.quality_metrics.get('totalSections', 0)}")
    logger.info(f"  Quality score: {result.quality_metrics.get('validationScore', 0):.1f}")
    logger.info(f"Output: {output_path}")

    if result.warnings:
        for warning in result.warnings:
            logger.warning(f"  Warning: {warning}")

    return 0


def cmd_templates(args) -> int:
    """List available templates."""
    catalog_path = Path(__file__).parent.parent.parent / "templates" / "pptx" / "master_catalog.json"

    if not catalog_path.exists():
        logger.error("Template catalog not found")
        return 1

    with open(catalog_path, 'r', encoding='utf-8') as f:
        catalog = json.load(f)

    templates = catalog.get("templates", {})

    print("\n=== Available Templates ===\n")

    for template_id, template in templates.items():
        classification = template.get("classification", {})
        file_info = template.get("file", {})

        status = "OK" if Path(file_info.get("path", "")).exists() else "MISSING"

        print(f"  [{status}] {template_id}")
        print(f"         Name: {template.get('name', template_id)}")
        print(f"         Domain: {classification.get('domain', 'general')}")
        print(f"         Formality: {classification.get('formality', 'neutral')}")
        print(f"         Description: {template.get('description', 'No description')[:60]}")
        print()

    # Show indexes
    indexes = catalog.get("indexes", {})
    if args.verbose:
        print("\n=== Template Indexes ===\n")
        for index_name, index_data in indexes.items():
            print(f"  {index_name}:")
            for key, values in index_data.items():
                print(f"    {key}: {', '.join(values)}")
            print()

    print(f"Default template: {catalog.get('default_template', 'corporate')}")
    print("\nUsage: python -m scripts.pipeline generate input.md output.pptx --theme corporate")

    return 0


def cmd_manifest(args) -> int:
    """View or manage pipeline manifests."""
    manifest_path = Path(args.manifest)

    if not manifest_path.exists():
        logger.error(f"Manifest not found: {manifest_path}")
        return 1

    manifest = PipelineManifest.load(manifest_path)
    summary = manifest.get_summary()

    print("\n=== Pipeline Manifest ===\n")
    print(f"ID: {summary['id']}")
    print(f"Created: {summary['created']}")
    print(f"Source: {summary['source']}")
    print(f"Output: {summary['output']}")
    print(f"Template: {summary['template']}")
    print(f"Stages completed: {summary['stages_completed']}")
    print(f"Success: {summary['success']}")
    print(f"Quality score: {summary['quality_score']}")
    print(f"Total slides: {summary['total_slides']}")

    if args.verbose:
        print("\n--- Processing Steps ---")
        for step in manifest.processing_steps:
            status = "OK" if step.success else "FAILED"
            print(f"  [{status}] {step.stage} ({step.duration_ms:.0f}ms)")
            if step.errors:
                for error in step.errors:
                    print(f"       Error: {error}")
            if step.warnings:
                for warning in step.warnings:
                    print(f"       Warning: {warning}")

    return 0


def main():
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(
        description="Slideforge Pipeline CLI - Transform content into presentations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate presentation from markdown
  python -m scripts.pipeline generate content.md presentation.pptx --theme corporate

  # Validate a presentation JSON
  python -m scripts.pipeline validate presentation.json --strict

  # Extract content with profiling
  python -m scripts.pipeline extract document.md --profile --output semantic.json

  # List available templates
  python -m scripts.pipeline templates
"""
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Generate command
    gen_parser = subparsers.add_parser('generate', help='Generate presentation from content')
    gen_parser.add_argument('input', help='Input file (markdown, HTML, or JSON)')
    gen_parser.add_argument('output', help='Output PPTX file path')
    gen_parser.add_argument('--theme', '-t', help='Template theme name')
    gen_parser.add_argument('--template', help='Path to custom template PPTX')
    gen_parser.add_argument('--no-notes', action='store_true', help='Skip speaker notes generation')
    gen_parser.add_argument('--strict', action='store_true', help='Strict validation mode')
    gen_parser.add_argument('--save-intermediates', action='store_true', help='Save intermediate files')
    gen_parser.add_argument('--manifest', help='Path to save pipeline manifest')
    gen_parser.add_argument('--resume-from', choices=['extraction', 'transformation', 'template_selection', 'validation', 'generation'], help='Resume from specific stage')
    gen_parser.set_defaults(func=cmd_generate)

    # Validate command
    val_parser = subparsers.add_parser('validate', help='Validate presentation JSON')
    val_parser.add_argument('input', help='Presentation JSON file')
    val_parser.add_argument('--output', '-o', help='Save validation report to file')
    val_parser.add_argument('--strict', action='store_true', help='Strict validation mode')
    val_parser.add_argument('--continue-on-error', action='store_true', help='Continue validation even after errors')
    val_parser.set_defaults(func=cmd_validate)

    # Extract command
    ext_parser = subparsers.add_parser('extract', help='Extract semantic structure from content')
    ext_parser.add_argument('input', help='Input content file')
    ext_parser.add_argument('--output', '-o', help='Output JSON file')
    ext_parser.add_argument('--profile', action='store_true', help='Include content profiling')
    ext_parser.set_defaults(func=cmd_extract)

    # Transform command
    trans_parser = subparsers.add_parser('transform', help='Transform semantic structure to presentation')
    trans_parser.add_argument('input', help='Semantic JSON file')
    trans_parser.add_argument('--output', '-o', help='Output presentation JSON file')
    trans_parser.add_argument('--max-bullets', type=int, default=6, help='Max bullets per slide')
    trans_parser.add_argument('--max-words', type=int, default=6, help='Max words per bullet')
    trans_parser.add_argument('--no-notes', action='store_true', help='Skip notes generation')
    trans_parser.add_argument('--notes-style', choices=['detailed', 'summary', 'talking_points', 'script', 'minimal'], default='talking_points', help='Speaker notes style')
    trans_parser.add_argument('--split-strategy', choices=['equal', 'semantic', 'threshold', 'priority'], default='semantic', help='Content splitting strategy')
    trans_parser.add_argument('--no-section-headers', action='store_true', help='Skip section header slides')
    trans_parser.add_argument('--no-title-slide', action='store_true', help='Skip title slide')
    trans_parser.set_defaults(func=cmd_transform)

    # Templates command
    temp_parser = subparsers.add_parser('templates', help='List available templates')
    temp_parser.set_defaults(func=cmd_templates)

    # Manifest command
    man_parser = subparsers.add_parser('manifest', help='View pipeline manifest')
    man_parser.add_argument('manifest', help='Manifest JSON file')
    man_parser.set_defaults(func=cmd_manifest)

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    if not args.command:
        parser.print_help()
        return 0

    return args.func(args)


if __name__ == '__main__':
    sys.exit(main())
