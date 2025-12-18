"""
Structure Validator for Slideforge (Level 1)

Validates data structure integrity before schema validation.
Checks for required fields, correct types, and structural coherence.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Set
from enum import Enum


class ErrorSeverity(Enum):
    """Severity levels for validation errors."""
    CRITICAL = "critical"  # Prevents further processing
    ERROR = "error"        # Must be fixed
    WARNING = "warning"    # Should be fixed
    INFO = "info"          # Informational


@dataclass
class StructureError:
    """A structure validation error."""
    path: str
    message: str
    severity: ErrorSeverity
    actual_value: Any = None
    expected: str = ""
    suggestion: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "path": self.path,
            "message": self.message,
            "severity": self.severity.value,
            "actualValue": str(self.actual_value)[:100] if self.actual_value else None,
            "expected": self.expected,
            "suggestion": self.suggestion
        }


@dataclass
class StructureValidationResult:
    """Result of structure validation."""
    valid: bool
    errors: List[StructureError] = field(default_factory=list)
    warnings: List[StructureError] = field(default_factory=list)
    info: List[StructureError] = field(default_factory=list)
    stats: Dict[str, Any] = field(default_factory=dict)

    @property
    def critical_errors(self) -> List[StructureError]:
        """Get critical errors only."""
        return [e for e in self.errors if e.severity == ErrorSeverity.CRITICAL]

    @property
    def error_count(self) -> int:
        """Total error count."""
        return len(self.errors)

    @property
    def warning_count(self) -> int:
        """Total warning count."""
        return len(self.warnings)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "valid": self.valid,
            "errors": [e.to_dict() for e in self.errors],
            "warnings": [e.to_dict() for e in self.warnings],
            "info": [e.to_dict() for e in self.info],
            "stats": self.stats,
            "summary": {
                "errorCount": self.error_count,
                "warningCount": self.warning_count,
                "criticalCount": len(self.critical_errors)
            }
        }


class StructureValidator:
    """
    Level 1 Validator: Structure Integrity

    Validates:
    - Required fields are present
    - Field types are correct
    - Nested structures are valid
    - References are consistent
    """

    # Required fields at each level
    REQUIRED_FIELDS = {
        "root": ["metadata", "sections"],
        "metadata": ["title"],
        "section": ["slides"],
        "slide": ["type"],
        "content_slide": ["title", "content"],
        "table_content": ["headers", "rows"],
        "comparison_content": ["left", "right"],
        "process_content": ["steps"],
        "timeline_content": ["events"],
        "key_value_content": ["pairs"]
    }

    # Valid slide types
    VALID_SLIDE_TYPES = {
        "title", "section_header", "content", "two_content",
        "comparison", "image", "quote", "blank", "table",
        "process_flow", "comparison_matrix", "timeline", "key_value"
    }

    # Type specifications
    TYPE_SPECS = {
        "title": str,
        "subtitle": str,
        "author": str,
        "date": str,
        "bullets": list,
        "headers": list,
        "rows": list,
        "steps": list,
        "events": list,
        "pairs": list,
        "slides": list,
        "sections": list,
        "keywords": list,
        "left": list,
        "right": list
    }

    def __init__(self, strict: bool = False):
        """
        Initialize validator.

        Args:
            strict: If True, warnings become errors
        """
        self.strict = strict

    def validate(self, presentation: Dict[str, Any]) -> StructureValidationResult:
        """
        Validate presentation structure.

        Args:
            presentation: Presentation dictionary to validate

        Returns:
            StructureValidationResult
        """
        errors = []
        warnings = []
        info = []
        stats = {
            "totalSections": 0,
            "totalSlides": 0,
            "slideTypes": {},
            "emptySlides": 0
        }

        # Check root structure
        root_errors = self._validate_root(presentation)
        errors.extend(root_errors)

        if root_errors:
            # Can't continue if root is invalid
            return StructureValidationResult(
                valid=False,
                errors=errors,
                warnings=warnings,
                info=info,
                stats=stats
            )

        # Validate metadata
        metadata_results = self._validate_metadata(
            presentation.get("metadata", {}),
            "metadata"
        )
        errors.extend(metadata_results["errors"])
        warnings.extend(metadata_results["warnings"])

        # Validate sections
        sections = presentation.get("sections", [])
        stats["totalSections"] = len(sections)

        for i, section in enumerate(sections):
            section_path = f"sections[{i}]"
            section_results = self._validate_section(section, section_path)

            errors.extend(section_results["errors"])
            warnings.extend(section_results["warnings"])
            info.extend(section_results["info"])

            # Update stats
            slides = section.get("slides", [])
            stats["totalSlides"] += len(slides)

            for slide in slides:
                slide_type = slide.get("type", "unknown")
                stats["slideTypes"][slide_type] = stats["slideTypes"].get(slide_type, 0) + 1

                if self._is_empty_slide(slide):
                    stats["emptySlides"] += 1

        # Determine validity
        is_valid = len(errors) == 0

        if self.strict:
            is_valid = is_valid and len(warnings) == 0

        return StructureValidationResult(
            valid=is_valid,
            errors=errors,
            warnings=warnings,
            info=info,
            stats=stats
        )

    def _validate_root(self, presentation: Dict[str, Any]) -> List[StructureError]:
        """Validate root structure."""
        errors = []

        if not isinstance(presentation, dict):
            errors.append(StructureError(
                path="$",
                message="Presentation must be a dictionary/object",
                severity=ErrorSeverity.CRITICAL,
                actual_value=type(presentation).__name__,
                expected="dict"
            ))
            return errors

        # Check required fields
        for field in self.REQUIRED_FIELDS["root"]:
            if field not in presentation:
                errors.append(StructureError(
                    path="$",
                    message=f"Missing required field: {field}",
                    severity=ErrorSeverity.CRITICAL,
                    expected=f"'{field}' field required"
                ))

        # Check sections is a list
        sections = presentation.get("sections")
        if sections is not None and not isinstance(sections, list):
            errors.append(StructureError(
                path="$.sections",
                message="sections must be an array",
                severity=ErrorSeverity.CRITICAL,
                actual_value=type(sections).__name__,
                expected="array"
            ))

        return errors

    def _validate_metadata(
        self,
        metadata: Dict[str, Any],
        path: str
    ) -> Dict[str, List[StructureError]]:
        """Validate metadata structure."""
        errors = []
        warnings = []

        if not isinstance(metadata, dict):
            errors.append(StructureError(
                path=path,
                message="metadata must be an object",
                severity=ErrorSeverity.ERROR,
                actual_value=type(metadata).__name__,
                expected="object"
            ))
            return {"errors": errors, "warnings": warnings}

        # Check required fields
        for field in self.REQUIRED_FIELDS["metadata"]:
            if field not in metadata:
                errors.append(StructureError(
                    path=f"{path}.{field}",
                    message=f"Missing required field: {field}",
                    severity=ErrorSeverity.ERROR,
                    expected=f"'{field}' field required"
                ))

        # Check field types
        for field, expected_type in self.TYPE_SPECS.items():
            if field in metadata:
                value = metadata[field]
                if not isinstance(value, expected_type):
                    warnings.append(StructureError(
                        path=f"{path}.{field}",
                        message=f"Field '{field}' should be {expected_type.__name__}",
                        severity=ErrorSeverity.WARNING,
                        actual_value=type(value).__name__,
                        expected=expected_type.__name__
                    ))

        # Check title is not empty
        title = metadata.get("title", "")
        if isinstance(title, str) and not title.strip():
            warnings.append(StructureError(
                path=f"{path}.title",
                message="Title should not be empty",
                severity=ErrorSeverity.WARNING,
                suggestion="Add a meaningful title"
            ))

        return {"errors": errors, "warnings": warnings}

    def _validate_section(
        self,
        section: Dict[str, Any],
        path: str
    ) -> Dict[str, List[StructureError]]:
        """Validate a section structure."""
        errors = []
        warnings = []
        info = []

        if not isinstance(section, dict):
            errors.append(StructureError(
                path=path,
                message="Section must be an object",
                severity=ErrorSeverity.ERROR,
                actual_value=type(section).__name__,
                expected="object"
            ))
            return {"errors": errors, "warnings": warnings, "info": info}

        # Check required fields
        for field in self.REQUIRED_FIELDS["section"]:
            if field not in section:
                errors.append(StructureError(
                    path=path,
                    message=f"Missing required field: {field}",
                    severity=ErrorSeverity.ERROR,
                    expected=f"'{field}' field required"
                ))

        # Validate slides
        slides = section.get("slides", [])

        if not isinstance(slides, list):
            errors.append(StructureError(
                path=f"{path}.slides",
                message="slides must be an array",
                severity=ErrorSeverity.ERROR,
                actual_value=type(slides).__name__,
                expected="array"
            ))
        elif len(slides) == 0:
            warnings.append(StructureError(
                path=f"{path}.slides",
                message="Section has no slides",
                severity=ErrorSeverity.WARNING,
                suggestion="Add at least one slide to the section"
            ))
        else:
            for i, slide in enumerate(slides):
                slide_path = f"{path}.slides[{i}]"
                slide_results = self._validate_slide(slide, slide_path)
                errors.extend(slide_results["errors"])
                warnings.extend(slide_results["warnings"])
                info.extend(slide_results["info"])

        return {"errors": errors, "warnings": warnings, "info": info}

    def _validate_slide(
        self,
        slide: Dict[str, Any],
        path: str
    ) -> Dict[str, List[StructureError]]:
        """Validate a slide structure."""
        errors = []
        warnings = []
        info = []

        if not isinstance(slide, dict):
            errors.append(StructureError(
                path=path,
                message="Slide must be an object",
                severity=ErrorSeverity.ERROR,
                actual_value=type(slide).__name__,
                expected="object"
            ))
            return {"errors": errors, "warnings": warnings, "info": info}

        # Check required fields
        for field in self.REQUIRED_FIELDS["slide"]:
            if field not in slide:
                errors.append(StructureError(
                    path=path,
                    message=f"Missing required field: {field}",
                    severity=ErrorSeverity.ERROR,
                    expected=f"'{field}' field required"
                ))

        # Validate slide type
        slide_type = slide.get("type")
        if slide_type and slide_type not in self.VALID_SLIDE_TYPES:
            errors.append(StructureError(
                path=f"{path}.type",
                message=f"Invalid slide type: {slide_type}",
                severity=ErrorSeverity.ERROR,
                actual_value=slide_type,
                expected=f"one of: {', '.join(sorted(self.VALID_SLIDE_TYPES))}"
            ))

        # Validate content based on type
        if slide_type:
            content_results = self._validate_slide_content(
                slide.get("content", {}),
                slide_type,
                f"{path}.content"
            )
            errors.extend(content_results["errors"])
            warnings.extend(content_results["warnings"])
            info.extend(content_results["info"])

        # Check for title
        if slide_type not in ["title", "blank"]:
            if "title" not in slide or not slide.get("title"):
                warnings.append(StructureError(
                    path=f"{path}.title",
                    message="Slide should have a title",
                    severity=ErrorSeverity.WARNING,
                    suggestion="Add a descriptive title"
                ))

        return {"errors": errors, "warnings": warnings, "info": info}

    def _validate_slide_content(
        self,
        content: Dict[str, Any],
        slide_type: str,
        path: str
    ) -> Dict[str, List[StructureError]]:
        """Validate slide content based on type."""
        errors = []
        warnings = []
        info = []

        if not isinstance(content, dict):
            if slide_type not in ["blank", "section_header"]:
                errors.append(StructureError(
                    path=path,
                    message="content must be an object",
                    severity=ErrorSeverity.ERROR,
                    actual_value=type(content).__name__,
                    expected="object"
                ))
            return {"errors": errors, "warnings": warnings, "info": info}

        # Type-specific validation
        if slide_type == "content":
            if "bullets" in content:
                bullets_results = self._validate_bullets(content["bullets"], f"{path}.bullets")
                warnings.extend(bullets_results)

        elif slide_type == "table":
            table_results = self._validate_table_content(content, path)
            errors.extend(table_results["errors"])
            warnings.extend(table_results["warnings"])

        elif slide_type in ["two_content", "comparison"]:
            comparison_results = self._validate_comparison_content(content, path)
            errors.extend(comparison_results["errors"])
            warnings.extend(comparison_results["warnings"])

        elif slide_type == "process_flow":
            process_results = self._validate_process_content(content, path)
            errors.extend(process_results["errors"])
            warnings.extend(process_results["warnings"])

        elif slide_type == "timeline":
            timeline_results = self._validate_timeline_content(content, path)
            errors.extend(timeline_results["errors"])
            warnings.extend(timeline_results["warnings"])

        elif slide_type == "key_value":
            kv_results = self._validate_key_value_content(content, path)
            errors.extend(kv_results["errors"])
            warnings.extend(kv_results["warnings"])

        elif slide_type == "quote":
            if "text" not in content and "quote" not in content:
                warnings.append(StructureError(
                    path=path,
                    message="Quote slide should have 'text' field",
                    severity=ErrorSeverity.WARNING
                ))

        elif slide_type == "image":
            if "image_path" not in content:
                warnings.append(StructureError(
                    path=path,
                    message="Image slide should have 'image_path' field",
                    severity=ErrorSeverity.WARNING
                ))

        return {"errors": errors, "warnings": warnings, "info": info}

    def _validate_bullets(self, bullets: Any, path: str) -> List[StructureError]:
        """Validate bullet list."""
        warnings = []

        if not isinstance(bullets, list):
            warnings.append(StructureError(
                path=path,
                message="bullets should be an array",
                severity=ErrorSeverity.WARNING,
                actual_value=type(bullets).__name__,
                expected="array"
            ))
            return warnings

        for i, bullet in enumerate(bullets):
            if not isinstance(bullet, str):
                warnings.append(StructureError(
                    path=f"{path}[{i}]",
                    message="Bullet should be a string",
                    severity=ErrorSeverity.WARNING,
                    actual_value=type(bullet).__name__,
                    expected="string"
                ))

        return warnings

    def _validate_table_content(
        self,
        content: Dict[str, Any],
        path: str
    ) -> Dict[str, List[StructureError]]:
        """Validate table content."""
        errors = []
        warnings = []

        # Check required fields
        if "headers" not in content:
            errors.append(StructureError(
                path=path,
                message="Table requires 'headers' field",
                severity=ErrorSeverity.ERROR,
                expected="headers array"
            ))

        if "rows" not in content:
            errors.append(StructureError(
                path=path,
                message="Table requires 'rows' field",
                severity=ErrorSeverity.ERROR,
                expected="rows array"
            ))

        # Validate headers
        headers = content.get("headers", [])
        if not isinstance(headers, list):
            errors.append(StructureError(
                path=f"{path}.headers",
                message="headers must be an array",
                severity=ErrorSeverity.ERROR,
                actual_value=type(headers).__name__
            ))
        elif len(headers) == 0:
            warnings.append(StructureError(
                path=f"{path}.headers",
                message="Table has no headers",
                severity=ErrorSeverity.WARNING
            ))

        # Validate rows
        rows = content.get("rows", [])
        if not isinstance(rows, list):
            errors.append(StructureError(
                path=f"{path}.rows",
                message="rows must be an array",
                severity=ErrorSeverity.ERROR,
                actual_value=type(rows).__name__
            ))
        else:
            header_count = len(headers) if isinstance(headers, list) else 0
            for i, row in enumerate(rows):
                if not isinstance(row, list):
                    errors.append(StructureError(
                        path=f"{path}.rows[{i}]",
                        message="Each row must be an array",
                        severity=ErrorSeverity.ERROR
                    ))
                elif len(row) != header_count and header_count > 0:
                    warnings.append(StructureError(
                        path=f"{path}.rows[{i}]",
                        message=f"Row has {len(row)} columns, expected {header_count}",
                        severity=ErrorSeverity.WARNING
                    ))

        return {"errors": errors, "warnings": warnings}

    def _validate_comparison_content(
        self,
        content: Dict[str, Any],
        path: str
    ) -> Dict[str, List[StructureError]]:
        """Validate comparison/two_content structure."""
        errors = []
        warnings = []

        if "left" not in content:
            errors.append(StructureError(
                path=path,
                message="Comparison requires 'left' field",
                severity=ErrorSeverity.ERROR
            ))

        if "right" not in content:
            errors.append(StructureError(
                path=path,
                message="Comparison requires 'right' field",
                severity=ErrorSeverity.ERROR
            ))

        # Validate arrays
        for side in ["left", "right"]:
            if side in content and not isinstance(content[side], list):
                errors.append(StructureError(
                    path=f"{path}.{side}",
                    message=f"'{side}' must be an array",
                    severity=ErrorSeverity.ERROR,
                    actual_value=type(content[side]).__name__
                ))

        return {"errors": errors, "warnings": warnings}

    def _validate_process_content(
        self,
        content: Dict[str, Any],
        path: str
    ) -> Dict[str, List[StructureError]]:
        """Validate process flow content."""
        errors = []
        warnings = []

        if "steps" not in content:
            errors.append(StructureError(
                path=path,
                message="Process flow requires 'steps' field",
                severity=ErrorSeverity.ERROR
            ))
            return {"errors": errors, "warnings": warnings}

        steps = content.get("steps", [])
        if not isinstance(steps, list):
            errors.append(StructureError(
                path=f"{path}.steps",
                message="steps must be an array",
                severity=ErrorSeverity.ERROR
            ))
        else:
            for i, step in enumerate(steps):
                if not isinstance(step, dict):
                    warnings.append(StructureError(
                        path=f"{path}.steps[{i}]",
                        message="Each step should be an object with 'label'",
                        severity=ErrorSeverity.WARNING
                    ))
                elif "label" not in step:
                    warnings.append(StructureError(
                        path=f"{path}.steps[{i}]",
                        message="Step should have 'label' field",
                        severity=ErrorSeverity.WARNING
                    ))

        return {"errors": errors, "warnings": warnings}

    def _validate_timeline_content(
        self,
        content: Dict[str, Any],
        path: str
    ) -> Dict[str, List[StructureError]]:
        """Validate timeline content."""
        errors = []
        warnings = []

        if "events" not in content:
            errors.append(StructureError(
                path=path,
                message="Timeline requires 'events' field",
                severity=ErrorSeverity.ERROR
            ))
            return {"errors": errors, "warnings": warnings}

        events = content.get("events", [])
        if not isinstance(events, list):
            errors.append(StructureError(
                path=f"{path}.events",
                message="events must be an array",
                severity=ErrorSeverity.ERROR
            ))
        else:
            for i, event in enumerate(events):
                if not isinstance(event, dict):
                    warnings.append(StructureError(
                        path=f"{path}.events[{i}]",
                        message="Each event should be an object",
                        severity=ErrorSeverity.WARNING
                    ))
                elif "label" not in event:
                    warnings.append(StructureError(
                        path=f"{path}.events[{i}]",
                        message="Event should have 'label' field",
                        severity=ErrorSeverity.WARNING
                    ))

        return {"errors": errors, "warnings": warnings}

    def _validate_key_value_content(
        self,
        content: Dict[str, Any],
        path: str
    ) -> Dict[str, List[StructureError]]:
        """Validate key-value content."""
        errors = []
        warnings = []

        if "pairs" not in content:
            errors.append(StructureError(
                path=path,
                message="Key-value requires 'pairs' field",
                severity=ErrorSeverity.ERROR
            ))
            return {"errors": errors, "warnings": warnings}

        pairs = content.get("pairs", [])
        if not isinstance(pairs, list):
            errors.append(StructureError(
                path=f"{path}.pairs",
                message="pairs must be an array",
                severity=ErrorSeverity.ERROR
            ))
        else:
            for i, pair in enumerate(pairs):
                if not isinstance(pair, dict):
                    warnings.append(StructureError(
                        path=f"{path}.pairs[{i}]",
                        message="Each pair should be an object",
                        severity=ErrorSeverity.WARNING
                    ))
                else:
                    if "key" not in pair:
                        warnings.append(StructureError(
                            path=f"{path}.pairs[{i}]",
                            message="Pair should have 'key' field",
                            severity=ErrorSeverity.WARNING
                        ))
                    if "value" not in pair:
                        warnings.append(StructureError(
                            path=f"{path}.pairs[{i}]",
                            message="Pair should have 'value' field",
                            severity=ErrorSeverity.WARNING
                        ))

        return {"errors": errors, "warnings": warnings}

    def _is_empty_slide(self, slide: Dict[str, Any]) -> bool:
        """Check if a slide has no meaningful content."""
        slide_type = slide.get("type", "")

        if slide_type == "blank":
            return False  # Blank slides are intentionally empty

        content = slide.get("content", {})

        if not content:
            return True

        # Check for content based on type
        if slide_type == "content":
            bullets = content.get("bullets", [])
            return len(bullets) == 0

        if slide_type == "table":
            rows = content.get("rows", [])
            return len(rows) == 0

        if slide_type in ["two_content", "comparison"]:
            left = content.get("left", [])
            right = content.get("right", [])
            return len(left) == 0 and len(right) == 0

        return False
