"""
ValidationResult Utility for Slideforge

Provides a unified validation result pattern that accumulates errors and
warnings instead of fail-fast behavior. Compatible with existing validators
in scripts/validators/ and inspired by LibV2 RAG patterns.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum


class ValidationSeverity(Enum):
    """Severity levels for validation issues."""
    CRITICAL = "critical"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class ValidationIssue:
    """A single validation issue with context."""
    message: str
    severity: ValidationSeverity
    path: str = ""
    context: Dict[str, Any] = field(default_factory=dict)
    rule_id: str = ""
    suggestion: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "message": self.message,
            "severity": self.severity.value,
            "path": self.path,
            "context": self.context,
            "ruleId": self.rule_id,
            "suggestion": self.suggestion
        }


@dataclass
class ValidationResult:
    """
    Result of a validation operation.

    Accumulates errors and warnings instead of fail-fast approach.
    Supports merging multiple validation results and detailed context.

    Example:
        result = ValidationResult()
        result.add_error("Missing title", path="$.metadata.title")
        result.add_warning("Title too short")

        if not result.valid:
            print(f"Found {result.error_count} errors")
            for error in result.errors:
                print(f"  - {error}")
    """

    valid: bool = True
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    info: List[str] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    issues: List[ValidationIssue] = field(default_factory=list)

    @property
    def error_count(self) -> int:
        """Total number of errors."""
        return len(self.errors)

    @property
    def warning_count(self) -> int:
        """Total number of warnings."""
        return len(self.warnings)

    @property
    def info_count(self) -> int:
        """Total number of info messages."""
        return len(self.info)

    @property
    def issue_count(self) -> int:
        """Total number of structured issues."""
        return len(self.issues)

    @property
    def critical_issues(self) -> List[ValidationIssue]:
        """Get only critical issues."""
        return [i for i in self.issues if i.severity == ValidationSeverity.CRITICAL]

    @property
    def error_issues(self) -> List[ValidationIssue]:
        """Get only error-level issues."""
        return [i for i in self.issues if i.severity == ValidationSeverity.ERROR]

    def add_error(self, msg: str, context: Optional[Dict[str, Any]] = None) -> None:
        """
        Add an error message.

        Args:
            msg: Error message
            context: Optional context information (path, value, etc.)
        """
        self.errors.append(msg)
        self.valid = False

        if context:
            # Store context for this error
            if 'errors_context' not in self.context:
                self.context['errors_context'] = []
            self.context['errors_context'].append({
                'message': msg,
                'context': context
            })

    def add_warning(self, msg: str, context: Optional[Dict[str, Any]] = None) -> None:
        """
        Add a warning message.

        Args:
            msg: Warning message
            context: Optional context information
        """
        self.warnings.append(msg)

        if context:
            if 'warnings_context' not in self.context:
                self.context['warnings_context'] = []
            self.context['warnings_context'].append({
                'message': msg,
                'context': context
            })

    def add_info(self, msg: str) -> None:
        """
        Add an informational message.

        Args:
            msg: Info message
        """
        self.info.append(msg)

    def add_issue(
        self,
        message: str,
        severity: ValidationSeverity,
        path: str = "",
        context: Optional[Dict[str, Any]] = None,
        rule_id: str = "",
        suggestion: str = ""
    ) -> None:
        """
        Add a structured validation issue.

        Args:
            message: Issue description
            severity: Severity level
            path: JSON path or location identifier
            context: Additional context information
            rule_id: Rule identifier for this issue
            suggestion: Suggested fix
        """
        issue = ValidationIssue(
            message=message,
            severity=severity,
            path=path,
            context=context or {},
            rule_id=rule_id,
            suggestion=suggestion
        )
        self.issues.append(issue)

        # Also add to appropriate list for backward compatibility
        if severity == ValidationSeverity.CRITICAL or severity == ValidationSeverity.ERROR:
            self.errors.append(message)
            self.valid = False
        elif severity == ValidationSeverity.WARNING:
            self.warnings.append(message)
        elif severity == ValidationSeverity.INFO:
            self.info.append(message)

    def merge(self, other: "ValidationResult") -> None:
        """
        Merge another ValidationResult into this one.

        Args:
            other: Another ValidationResult to merge
        """
        if not other.valid:
            self.valid = False

        self.errors.extend(other.errors)
        self.warnings.extend(other.warnings)
        self.info.extend(other.info)
        self.issues.extend(other.issues)

        # Merge context
        for key, value in other.context.items():
            if key in self.context:
                # If both have the key, combine lists or update dict
                if isinstance(value, list) and isinstance(self.context[key], list):
                    self.context[key].extend(value)
                elif isinstance(value, dict) and isinstance(self.context[key], dict):
                    self.context[key].update(value)
                else:
                    # Store as list of values
                    if not isinstance(self.context[key], list):
                        self.context[key] = [self.context[key]]
                    self.context[key].append(value)
            else:
                self.context[key] = value

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary for serialization.

        Returns:
            Dictionary representation
        """
        return {
            "valid": self.valid,
            "errors": self.errors,
            "warnings": self.warnings,
            "info": self.info,
            "context": self.context,
            "issues": [issue.to_dict() for issue in self.issues],
            "summary": {
                "errorCount": self.error_count,
                "warningCount": self.warning_count,
                "infoCount": self.info_count,
                "issueCount": self.issue_count,
                "criticalCount": len(self.critical_issues)
            }
        }

    def to_summary(self) -> str:
        """
        Generate a human-readable summary.

        Returns:
            Summary string
        """
        if self.valid and not self.warnings and not self.info:
            return "Validation passed with no issues."

        lines = []

        if not self.valid:
            lines.append(f"Validation failed with {self.error_count} error(s)")
        else:
            lines.append("Validation passed")

        if self.warning_count > 0:
            lines.append(f"  - {self.warning_count} warning(s)")

        if self.info_count > 0:
            lines.append(f"  - {self.info_count} info message(s)")

        return "\n".join(lines)

    def print_report(self) -> None:
        """Print a formatted validation report to stdout."""
        print("\n" + "=" * 60)
        print("VALIDATION REPORT")
        print("=" * 60)
        print(self.to_summary())

        if self.errors:
            print("\nERRORS:")
            for i, error in enumerate(self.errors, 1):
                print(f"  {i}. {error}")

        if self.warnings:
            print("\nWARNINGS:")
            for i, warning in enumerate(self.warnings, 1):
                print(f"  {i}. {warning}")

        if self.info:
            print("\nINFO:")
            for i, info_msg in enumerate(self.info, 1):
                print(f"  {i}. {info_msg}")

        if self.issues:
            print(f"\nSTRUCTURED ISSUES ({len(self.issues)}):")
            by_severity = {}
            for issue in self.issues:
                severity = issue.severity.value
                if severity not in by_severity:
                    by_severity[severity] = []
                by_severity[severity].append(issue)

            for severity in ["critical", "error", "warning", "info"]:
                if severity in by_severity:
                    print(f"\n  {severity.upper()}:")
                    for issue in by_severity[severity]:
                        print(f"    - {issue.message}")
                        if issue.path:
                            print(f"      Location: {issue.path}")
                        if issue.suggestion:
                            print(f"      Suggestion: {issue.suggestion}")

        print("\n" + "=" * 60)


def create_file_validation_result(
    file_path: str,
    exists: bool = True,
    readable: bool = True,
    file_type: str = ""
) -> ValidationResult:
    """
    Create a ValidationResult for file validation.

    Args:
        file_path: Path to the file
        exists: Whether file exists
        readable: Whether file is readable
        file_type: Expected file type

    Returns:
        ValidationResult with appropriate errors/warnings
    """
    result = ValidationResult()
    result.context['file_path'] = file_path
    result.context['file_type'] = file_type

    if not exists:
        result.add_error(
            f"File not found: {file_path}",
            context={'path': file_path, 'exists': False}
        )
    elif not readable:
        result.add_error(
            f"File not readable: {file_path}",
            context={'path': file_path, 'readable': False}
        )
    else:
        result.add_info(f"File exists and is readable: {file_path}")

    return result


def create_schema_validation_result(
    data: Any,
    schema_name: str,
    schema_valid: bool = True,
    errors: Optional[List[str]] = None
) -> ValidationResult:
    """
    Create a ValidationResult for schema validation.

    Args:
        data: Data that was validated
        schema_name: Name of the schema
        schema_valid: Whether validation passed
        errors: List of validation errors

    Returns:
        ValidationResult
    """
    result = ValidationResult(valid=schema_valid)
    result.context['schema'] = schema_name

    if errors:
        for error in errors:
            result.add_error(error)
    elif schema_valid:
        result.add_info(f"Data validates against schema: {schema_name}")

    return result
