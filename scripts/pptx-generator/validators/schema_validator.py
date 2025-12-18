"""Schema validation for Slideforge presentations.

Validates JSON content against presentation and theme schemas.
"""

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

try:
    import jsonschema
    from jsonschema import Draft7Validator, ValidationError
    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False


@dataclass
class SchemaValidationResult:
    """Result of schema validation."""
    valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    schema_path: Optional[str] = None


def validate_schema(
    data: dict,
    schema_path: Path,
    strict: bool = False
) -> SchemaValidationResult:
    """Validate data against a JSON schema.

    Args:
        data: Dictionary to validate
        schema_path: Path to JSON schema file
        strict: Enable strict validation mode

    Returns:
        SchemaValidationResult with validation status and errors
    """
    result = SchemaValidationResult(valid=True, schema_path=str(schema_path))

    if not HAS_JSONSCHEMA:
        result.warnings.append("jsonschema not installed, skipping validation")
        return result

    if not schema_path.exists():
        result.valid = False
        result.errors.append(f"Schema file not found: {schema_path}")
        return result

    try:
        with open(schema_path) as f:
            schema = json.load(f)
    except json.JSONDecodeError as e:
        result.valid = False
        result.errors.append(f"Invalid schema JSON: {e}")
        return result

    # Create validator
    validator = Draft7Validator(schema)

    # Collect all errors
    errors = list(validator.iter_errors(data))

    if errors:
        result.valid = False
        for error in errors:
            path = " -> ".join(str(p) for p in error.absolute_path) or "root"
            result.errors.append(f"{path}: {error.message}")

    # Additional strict checks
    if strict and result.valid:
        _strict_validation(data, result)

    return result


def _strict_validation(data: dict, result: SchemaValidationResult):
    """Apply strict validation rules beyond schema requirements."""
    # Check for recommended fields
    metadata = data.get('metadata', {})

    if not metadata.get('author'):
        result.warnings.append("Missing recommended field: metadata.author")

    if not metadata.get('date'):
        result.warnings.append("Missing recommended field: metadata.date")

    if not metadata.get('subject'):
        result.warnings.append("Missing recommended field: metadata.subject")

    # Check sections have titles
    for i, section in enumerate(data.get('sections', [])):
        if not section.get('title'):
            result.warnings.append(f"Section {i+1} missing title")


def validate_presentation_schema(
    data: dict,
    root_path: Path
) -> SchemaValidationResult:
    """Validate against presentation schema.

    Args:
        data: Presentation data dictionary
        root_path: Project root path

    Returns:
        SchemaValidationResult
    """
    schema_path = root_path / "schemas" / "presentation" / "presentation_schema.json"
    return validate_schema(data, schema_path)


def validate_theme_schema(
    data: dict,
    root_path: Path
) -> SchemaValidationResult:
    """Validate against theme schema.

    Args:
        data: Theme data dictionary
        root_path: Project root path

    Returns:
        SchemaValidationResult
    """
    schema_path = root_path / "schemas" / "presentation" / "theme_schema.json"
    return validate_schema(data, schema_path)
