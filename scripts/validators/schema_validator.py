"""
Schema Validator for Slideforge (Level 2)

Validates presentation data against JSON Schema.
Provides detailed error reporting with path information.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from pathlib import Path
import json

try:
    import jsonschema
    from jsonschema import Draft7Validator, ValidationError
    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False


@dataclass
class SchemaError:
    """A schema validation error."""
    path: str
    message: str
    schema_path: str = ""
    validator: str = ""
    value: Any = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "path": self.path,
            "message": self.message,
            "schemaPath": self.schema_path,
            "validator": self.validator,
            "value": str(self.value)[:100] if self.value is not None else None
        }


@dataclass
class SchemaValidationResult:
    """Result of schema validation."""
    valid: bool
    errors: List[SchemaError] = field(default_factory=list)
    schema_version: str = ""
    schema_id: str = ""

    @property
    def error_count(self) -> int:
        """Total error count."""
        return len(self.errors)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "valid": self.valid,
            "errors": [e.to_dict() for e in self.errors],
            "errorCount": self.error_count,
            "schemaVersion": self.schema_version,
            "schemaId": self.schema_id
        }


class SchemaValidator:
    """
    Level 2 Validator: JSON Schema Compliance

    Validates presentation data against the presentation schema.
    Provides detailed error messages with JSON paths.
    """

    # Default schema (embedded for independence)
    DEFAULT_SCHEMA = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "$id": "https://slideforge.dev/schemas/presentation.json",
        "title": "Slideforge Presentation Schema",
        "type": "object",
        "properties": {
            "metadata": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "subtitle": {"type": "string"},
                    "author": {"type": "string"},
                    "date": {"type": "string"},
                    "subject": {"type": "string"},
                    "keywords": {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                },
                "required": ["title"]
            },
            "theme": {
                "type": "object",
                "properties": {
                    "template_path": {"type": "string"},
                    "colors": {"type": "object"},
                    "fonts": {"type": "object"}
                }
            },
            "sections": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "slides": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "type": {
                                        "type": "string",
                                        "enum": [
                                            "title", "section_header", "content",
                                            "two_content", "comparison", "image",
                                            "quote", "blank", "table", "process_flow",
                                            "comparison_matrix", "timeline", "key_value"
                                        ]
                                    },
                                    "title": {"type": "string"},
                                    "content": {"type": "object"},
                                    "notes": {"type": "string"}
                                },
                                "required": ["type"]
                            }
                        }
                    },
                    "required": ["slides"]
                }
            }
        },
        "required": ["metadata", "sections"]
    }

    def __init__(
        self,
        schema: Optional[Dict[str, Any]] = None,
        schema_path: Optional[Path] = None
    ):
        """
        Initialize validator with schema.

        Args:
            schema: Schema dictionary to use
            schema_path: Path to schema file (takes precedence)
        """
        self.schema = self._load_schema(schema, schema_path)
        self.schema_version = self.schema.get("$schema", "")
        self.schema_id = self.schema.get("$id", "")

        if HAS_JSONSCHEMA:
            self.validator_class = Draft7Validator
        else:
            self.validator_class = None

    def _load_schema(
        self,
        schema: Optional[Dict[str, Any]],
        schema_path: Optional[Path]
    ) -> Dict[str, Any]:
        """Load schema from file or use provided/default."""
        if schema_path:
            try:
                with open(schema_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (FileNotFoundError, json.JSONDecodeError) as e:
                print(f"Warning: Could not load schema from {schema_path}: {e}")
                return schema or self.DEFAULT_SCHEMA

        return schema or self.DEFAULT_SCHEMA

    def validate(self, presentation: Dict[str, Any]) -> SchemaValidationResult:
        """
        Validate presentation against schema.

        Args:
            presentation: Presentation dictionary to validate

        Returns:
            SchemaValidationResult
        """
        if not HAS_JSONSCHEMA:
            # Fall back to basic validation without jsonschema
            return self._basic_validate(presentation)

        errors = []
        validator = self.validator_class(self.schema)

        for error in validator.iter_errors(presentation):
            schema_error = self._convert_error(error)
            errors.append(schema_error)

        return SchemaValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            schema_version=self.schema_version,
            schema_id=self.schema_id
        )

    def _convert_error(self, error: 'ValidationError') -> SchemaError:
        """Convert jsonschema error to SchemaError."""
        # Build JSON path from path elements
        path_parts = []
        for part in error.absolute_path:
            if isinstance(part, int):
                path_parts.append(f"[{part}]")
            else:
                if path_parts:
                    path_parts.append(f".{part}")
                else:
                    path_parts.append(part)

        json_path = "$" + "".join(path_parts) if path_parts else "$"

        # Build schema path
        schema_path_parts = []
        for part in error.absolute_schema_path:
            if isinstance(part, int):
                schema_path_parts.append(f"[{part}]")
            else:
                schema_path_parts.append(f"/{part}")

        schema_path = "#" + "".join(schema_path_parts)

        # Generate user-friendly message
        message = self._format_error_message(error)

        return SchemaError(
            path=json_path,
            message=message,
            schema_path=schema_path,
            validator=error.validator,
            value=error.instance
        )

    def _format_error_message(self, error: 'ValidationError') -> str:
        """Format a user-friendly error message."""
        if error.validator == "required":
            missing = error.validator_value
            if isinstance(missing, list):
                return f"Missing required field(s): {', '.join(missing)}"
            return f"Missing required field: {missing}"

        if error.validator == "type":
            expected = error.validator_value
            actual = type(error.instance).__name__
            return f"Expected {expected}, got {actual}"

        if error.validator == "enum":
            allowed = error.validator_value
            return f"Value must be one of: {', '.join(str(v) for v in allowed)}"

        if error.validator == "minLength":
            return f"String is too short (minimum {error.validator_value} characters)"

        if error.validator == "maxLength":
            return f"String is too long (maximum {error.validator_value} characters)"

        if error.validator == "minItems":
            return f"Array has too few items (minimum {error.validator_value})"

        if error.validator == "maxItems":
            return f"Array has too many items (maximum {error.validator_value})"

        if error.validator == "pattern":
            return f"String does not match required pattern: {error.validator_value}"

        if error.validator == "additionalProperties":
            return f"Additional property not allowed: {error.validator_value}"

        # Default to jsonschema message
        return error.message

    def _basic_validate(self, presentation: Dict[str, Any]) -> SchemaValidationResult:
        """Basic validation without jsonschema library."""
        errors = []

        # Check root type
        if not isinstance(presentation, dict):
            errors.append(SchemaError(
                path="$",
                message="Presentation must be an object",
                validator="type"
            ))
            return SchemaValidationResult(valid=False, errors=errors)

        # Check required fields
        for field in ["metadata", "sections"]:
            if field not in presentation:
                errors.append(SchemaError(
                    path="$",
                    message=f"Missing required field: {field}",
                    validator="required"
                ))

        # Check metadata
        metadata = presentation.get("metadata")
        if metadata is not None:
            if not isinstance(metadata, dict):
                errors.append(SchemaError(
                    path="$.metadata",
                    message="metadata must be an object",
                    validator="type"
                ))
            elif "title" not in metadata:
                errors.append(SchemaError(
                    path="$.metadata",
                    message="Missing required field: title",
                    validator="required"
                ))

        # Check sections
        sections = presentation.get("sections")
        if sections is not None:
            if not isinstance(sections, list):
                errors.append(SchemaError(
                    path="$.sections",
                    message="sections must be an array",
                    validator="type"
                ))
            else:
                for i, section in enumerate(sections):
                    section_errors = self._basic_validate_section(section, i)
                    errors.extend(section_errors)

        return SchemaValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            schema_version="basic",
            schema_id="slideforge-basic"
        )

    def _basic_validate_section(
        self,
        section: Dict[str, Any],
        index: int
    ) -> List[SchemaError]:
        """Basic validation for a section."""
        errors = []
        path = f"$.sections[{index}]"

        if not isinstance(section, dict):
            errors.append(SchemaError(
                path=path,
                message="Section must be an object",
                validator="type"
            ))
            return errors

        if "slides" not in section:
            errors.append(SchemaError(
                path=path,
                message="Missing required field: slides",
                validator="required"
            ))
            return errors

        slides = section.get("slides")
        if not isinstance(slides, list):
            errors.append(SchemaError(
                path=f"{path}.slides",
                message="slides must be an array",
                validator="type"
            ))
        else:
            for i, slide in enumerate(slides):
                slide_errors = self._basic_validate_slide(slide, f"{path}.slides[{i}]")
                errors.extend(slide_errors)

        return errors

    def _basic_validate_slide(
        self,
        slide: Dict[str, Any],
        path: str
    ) -> List[SchemaError]:
        """Basic validation for a slide."""
        errors = []

        if not isinstance(slide, dict):
            errors.append(SchemaError(
                path=path,
                message="Slide must be an object",
                validator="type"
            ))
            return errors

        if "type" not in slide:
            errors.append(SchemaError(
                path=path,
                message="Missing required field: type",
                validator="required"
            ))
            return errors

        valid_types = [
            "title", "section_header", "content", "two_content",
            "comparison", "image", "quote", "blank", "table",
            "process_flow", "comparison_matrix", "timeline", "key_value"
        ]

        slide_type = slide.get("type")
        if slide_type not in valid_types:
            errors.append(SchemaError(
                path=f"{path}.type",
                message=f"Invalid slide type: {slide_type}",
                validator="enum",
                value=slide_type
            ))

        return errors

    def get_schema(self) -> Dict[str, Any]:
        """Get the schema being used."""
        return self.schema

    def validate_partial(
        self,
        data: Dict[str, Any],
        path: str
    ) -> SchemaValidationResult:
        """
        Validate a partial structure (e.g., just a slide).

        Args:
            data: Data to validate
            path: Schema path to validate against (e.g., "slide", "section")

        Returns:
            SchemaValidationResult
        """
        # Extract the relevant part of the schema
        sub_schema = self._get_sub_schema(path)

        if sub_schema is None:
            return SchemaValidationResult(
                valid=False,
                errors=[SchemaError(
                    path="$",
                    message=f"Unknown schema path: {path}",
                    validator="internal"
                )]
            )

        # Create a temporary validator
        if HAS_JSONSCHEMA:
            validator = self.validator_class(sub_schema)
            errors = []

            for error in validator.iter_errors(data):
                errors.append(self._convert_error(error))

            return SchemaValidationResult(
                valid=len(errors) == 0,
                errors=errors,
                schema_version=self.schema_version,
                schema_id=f"{self.schema_id}#{path}"
            )

        return SchemaValidationResult(valid=True, errors=[])

    def _get_sub_schema(self, path: str) -> Optional[Dict[str, Any]]:
        """Get a sub-schema by path."""
        if path == "slide":
            return self.schema.get("properties", {}).get("sections", {}).get(
                "items", {}
            ).get("properties", {}).get("slides", {}).get("items", {})

        if path == "section":
            return self.schema.get("properties", {}).get("sections", {}).get("items", {})

        if path == "metadata":
            return self.schema.get("properties", {}).get("metadata", {})

        return None
