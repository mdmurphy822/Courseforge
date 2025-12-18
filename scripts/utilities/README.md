# Utilities - Helper Scripts and Tools

## Purpose
Collection of utility modules providing shared functionality across Slideforge scripts, including:
- Validation result accumulation pattern
- File and directory operations
- Slug generation and sanitization
- Repository navigation utilities

## Modules

### `validation_result.py`
Unified ValidationResult pattern for accumulating errors and warnings instead of fail-fast behavior. Inspired by LibV2 RAG patterns.

**Key Classes:**
- `ValidationResult`: Main result container with errors, warnings, and context
- `ValidationIssue`: Structured issue with severity, path, and suggestions
- `ValidationSeverity`: Enum for issue severity (CRITICAL, ERROR, WARNING, INFO)

**Key Functions:**
- `create_file_validation_result()`: Helper for file validation results
- `create_schema_validation_result()`: Helper for schema validation results

**Features:**
- Accumulates multiple errors and warnings
- Supports merging of validation results
- Provides structured issues with context
- Includes reporting and serialization methods

### `common.py`
Common utility functions used across Slideforge scripts.

**Key Functions:**

**Slug Generation:**
- `generate_slug(title, max_length=50)`: Convert titles to URL-safe slugs
- `ensure_unique_slug(slug, directory, extension="")`: Ensure slug uniqueness

**Repository Navigation:**
- `get_repo_root(start_path=None)`: Find repository root by looking for CLAUDE.md
- `get_slideforge_root()`: Get Slideforge root (raises error if not found)

**File Validation:**
- `validate_file_exists(path, file_type="")`: Validate file existence and readability
- `validate_directory_exists(path, create=False)`: Validate directory, optionally create

**File Operations:**
- `sanitize_filename(filename, max_length=200)`: Clean filename for cross-platform use
- `find_files_by_pattern(directory, pattern, recursive=False)`: Glob pattern matching
- `read_text_file(path, encoding='utf-8')`: Read text file with validation
- `get_file_size_mb(path)`: Get file size in megabytes

**Path Utilities:**
- `get_relative_path(path, base=None)`: Get relative path from base
- `ensure_output_directory(base_dir, project_name)`: Create unique timestamped directory

**Project Structure:**
- `validate_project_structure(project_dir)`: Validate Slideforge project layout

## Usage Examples

### ValidationResult Pattern

```python
from scripts.utilities import ValidationResult, ValidationSeverity

# Accumulate errors and warnings
result = ValidationResult()
result.add_error("Missing required field: title")
result.add_warning("Title is too short")

# Add structured issues
result.add_issue(
    message="Too many bullets (8 found, max 6)",
    severity=ValidationSeverity.ERROR,
    path="sections[0].slides[2]",
    rule_id="SIX_SIX_RULE",
    suggestion="Split into 2 slides"
)

# Check validity
if not result.valid:
    result.print_report()
```

### Common Utilities

```python
from scripts.utilities import (
    generate_slug,
    ensure_unique_slug,
    get_slideforge_root,
    validate_file_exists,
    ensure_output_directory
)
from pathlib import Path

# Generate slug for file naming
slug = generate_slug("Introduction to Python")
# Result: "introduction-to-python"

# Find repository root
root = get_slideforge_root()
templates_dir = root / "templates" / "pptx"

# Validate file exists
result = validate_file_exists(templates_dir / "default.pptx")
if not result.valid:
    print(f"Template not found: {result.errors}")

# Create timestamped output directory
exports_dir = root / "exports"
project_dir = ensure_output_directory(exports_dir, "My Presentation")
# Creates: exports/20251217_143022_my-presentation/
```

## Integration with Validators

The ValidationResult pattern integrates seamlessly with existing validators:

```python
from scripts.validators import StructureValidator, SchemaValidator, SemanticValidator
from scripts.utilities import ValidationResult

# Run all validators
struct_validator = StructureValidator()
schema_validator = SchemaValidator()
semantic_validator = SemanticValidator()

# Combine results
unified = ValidationResult()

struct_result = struct_validator.validate(data)
for error in struct_result.errors:
    unified.add_error(error.message, context={"path": error.path})

schema_result = schema_validator.validate(data)
for error in schema_result.errors:
    unified.add_error(error.message, context={"path": error.path})

semantic_result = semantic_validator.validate(data)
for issue in semantic_result.issues:
    unified.add_issue(
        message=issue.message,
        severity=ValidationSeverity.WARNING,
        path=issue.location,
        suggestion=issue.suggestion
    )

# Generate comprehensive report
unified.print_report()
```

## Dependencies
- Python 3.7+
- pathlib (built-in)
- dataclasses (built-in, Python 3.7+)
- typing (built-in)
- re (built-in)
- json (built-in)

## Documentation
See `USAGE.md` for comprehensive usage examples and best practices.

## Design Patterns

### LibV2 RAG Pattern Inspiration
The ValidationResult pattern is inspired by LibV2's validator design:
- Accumulate errors instead of fail-fast
- Support merging of multiple validation results
- Provide rich context for debugging
- Clear separation between errors and warnings

### Compatibility
The ValidationResult is designed to work alongside existing Slideforge validators:
- `scripts/validators/structure_validator.py`
- `scripts/validators/schema_validator.py`
- `scripts/validators/semantic_validator.py`

Results from these validators can be converted to unified ValidationResult format for consistent error handling across the codebase.

## Error Handling
All utilities include comprehensive error handling:
- File operations return ValidationResult objects
- Functions raise appropriate exceptions with clear messages
- Context information is preserved for debugging

## Changelog
- v1.0.0 (2025-08-05): Initial organization
- v1.1.0 (2025-12-17): Updated for Slideforge presentation generation
- v1.2.0 (2025-12-17): Added ValidationResult pattern and common utilities library
