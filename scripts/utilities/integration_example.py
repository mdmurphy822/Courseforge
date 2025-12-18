#!/usr/bin/env python3
"""
Integration Example: Using ValidationResult with Existing Validators

This example demonstrates how to use the new ValidationResult utility
with the existing three-tier validation system (structure, schema, semantic).
"""

import sys
import json
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.validators import (
    StructureValidator,
    SchemaValidator,
    SemanticValidator
)
from scripts.utilities import (
    ValidationResult,
    ValidationSeverity,
    get_slideforge_root,
    validate_file_exists
)


def validate_presentation_comprehensive(data: dict) -> ValidationResult:
    """
    Run all three validation tiers and combine results into a unified ValidationResult.

    Args:
        data: Presentation data dictionary

    Returns:
        Unified ValidationResult with all issues
    """
    result = ValidationResult()
    result.context['validation_tiers'] = ['structure', 'schema', 'semantic']

    # Tier 1: Structure Validation
    print("Running structure validation...")
    struct_validator = StructureValidator(strict=False)
    struct_result = struct_validator.validate(data)

    # Convert structure errors to unified format
    for error in struct_result.errors:
        result.add_issue(
            message=error.message,
            severity=ValidationSeverity.ERROR if error.severity.value == "error" else ValidationSeverity.CRITICAL,
            path=error.path,
            rule_id=f"STRUCT_{error.path.replace('.', '_').upper()}",
            suggestion=error.suggestion
        )

    # Convert structure warnings
    for warning in struct_result.warnings:
        result.add_issue(
            message=warning.message,
            severity=ValidationSeverity.WARNING,
            path=warning.path,
            suggestion=warning.suggestion
        )

    result.context['structure_stats'] = struct_result.stats

    # Tier 2: Schema Validation
    print("Running schema validation...")
    schema_validator = SchemaValidator()
    schema_result = schema_validator.validate(data)

    # Convert schema errors
    for error in schema_result.errors:
        result.add_issue(
            message=error.message,
            severity=ValidationSeverity.ERROR,
            path=error.path,
            rule_id=f"SCHEMA_{error.validator.upper()}",
            context={'schema_path': error.schema_path}
        )

    result.context['schema_version'] = schema_result.schema_version

    # Tier 3: Semantic Validation (Quality)
    print("Running semantic validation...")
    semantic_validator = SemanticValidator()
    semantic_result = semantic_validator.validate(data, strict=False)

    # Convert semantic issues
    for issue in semantic_result.issues:
        severity_map = {
            'critical': ValidationSeverity.CRITICAL,
            'major': ValidationSeverity.ERROR,
            'minor': ValidationSeverity.WARNING,
            'suggestion': ValidationSeverity.INFO
        }

        result.add_issue(
            message=issue.message,
            severity=severity_map.get(issue.severity.value, ValidationSeverity.WARNING),
            path=issue.location,
            rule_id=issue.rule_id,
            suggestion=issue.suggestion,
            context={'category': issue.category.value}
        )

    result.context['quality_metrics'] = semantic_result.metrics.to_dict()
    result.context['recommendations'] = semantic_result.recommendations

    return result


def main():
    """Run example validation."""
    print("=" * 70)
    print("ValidationResult Integration Example")
    print("=" * 70)

    # Create sample presentation data
    sample_data = {
        "metadata": {
            "title": "Sample Presentation",
            "author": "Test Author",
            "date": "2025-12-17"
        },
        "sections": [
            {
                "title": "Introduction",
                "slides": [
                    {
                        "type": "title",
                        "title": "Sample Presentation",
                        "content": {
                            "subtitle": "A Test Presentation"
                        }
                    },
                    {
                        "type": "content",
                        "title": "Overview",
                        "content": {
                            "bullets": [
                                "First point",
                                "Second point",
                                "Third point",
                                "Fourth point",
                                "Fifth point",
                                "Sixth point",
                                "Seventh point",  # Violates 6x6 rule
                                "Eighth point"
                            ]
                        },
                        "notes": "This slide has too many bullets"
                    },
                    {
                        "type": "content",
                        "title": "Details",
                        "content": {
                            "bullets": [
                                "This is a very long bullet point that contains way too many words",  # Violates 6x6
                                "Short point"
                            ]
                        }
                        # Missing notes - will trigger warning
                    }
                ]
            }
        ]
    }

    print("\nValidating sample presentation data...\n")

    # Run comprehensive validation
    result = validate_presentation_comprehensive(sample_data)

    # Print detailed report
    result.print_report()

    # Show context information
    print("\nVALIDATION CONTEXT:")
    print(f"  - Tiers: {', '.join(result.context.get('validation_tiers', []))}")

    if 'structure_stats' in result.context:
        stats = result.context['structure_stats']
        print(f"  - Total Slides: {stats.get('totalSlides', 0)}")
        print(f"  - Total Sections: {stats.get('totalSections', 0)}")

    if 'quality_metrics' in result.context:
        metrics = result.context['quality_metrics']
        print(f"  - Overall Score: {metrics.get('overallScore', 0):.1f}/100")
        print(f"  - 6x6 Violations: {metrics.get('sixSixViolations', 0)}")

    # Show recommendations
    if result.context.get('recommendations'):
        print("\nRECOMMENDATIONS:")
        for i, rec in enumerate(result.context['recommendations'], 1):
            print(f"  {i}. {rec}")

    # Demonstrate serialization
    print("\n" + "=" * 70)
    print("JSON Export Example")
    print("=" * 70)

    result_dict = result.to_dict()
    print(json.dumps({
        'valid': result_dict['valid'],
        'summary': result_dict['summary'],
        'error_sample': result_dict['errors'][:2] if result_dict['errors'] else [],
        'context_keys': list(result_dict['context'].keys())
    }, indent=2))

    # Return appropriate exit code
    return 0 if result.valid else 1


if __name__ == "__main__":
    sys.exit(main())
