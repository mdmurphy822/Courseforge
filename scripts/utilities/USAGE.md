# Slideforge Utilities Usage Guide

This guide demonstrates how to use the ValidationResult pattern and common utilities in Slideforge scripts.

## ValidationResult

The `ValidationResult` class provides a unified pattern for accumulating validation errors and warnings instead of fail-fast behavior.

### Basic Usage

```python
from scripts.utilities import ValidationResult

# Create a new validation result
result = ValidationResult()

# Add errors (marks result as invalid)
result.add_error("Missing required field: title")
result.add_error("Invalid slide type", context={"slide_index": 3})

# Add warnings (doesn't invalidate)
result.add_warning("Title is too short")

# Add info messages
result.add_info("Processing 15 slides")

# Check validity
if not result.valid:
    print(f"Validation failed with {result.error_count} errors")
    for error in result.errors:
        print(f"  - {error}")
```

### Structured Issues

For more detailed validation with severity levels and suggestions:

```python
from scripts.utilities import ValidationResult, ValidationSeverity

result = ValidationResult()

result.add_issue(
    message="Slide has too many bullets (10 found, max 6)",
    severity=ValidationSeverity.ERROR,
    path="sections[0].slides[2]",
    rule_id="SIX_SIX_RULE",
    suggestion="Split into 2 slides"
)

# Access structured issues
for issue in result.critical_issues:
    print(f"{issue.severity.value}: {issue.message}")
    if issue.suggestion:
        print(f"  Suggestion: {issue.suggestion}")
```

### Merging Results

Combine multiple validation results:

```python
result1 = ValidationResult()
result1.add_error("Schema error")

result2 = ValidationResult()
result2.add_warning("Missing notes")

# Merge result2 into result1
result1.merge(result2)

print(result1.to_summary())
```

### Integration with Existing Validators

The ValidationResult works alongside existing validators:

```python
from scripts.validators import StructureValidator, SchemaValidator
from scripts.utilities import ValidationResult

# Run existing validators
struct_validator = StructureValidator()
struct_result = struct_validator.validate(presentation_data)

schema_validator = SchemaValidator()
schema_result = schema_validator.validate(presentation_data)

# Create unified result
unified = ValidationResult()

# Convert structure errors to unified format
for error in struct_result.errors:
    unified.add_error(
        error.message,
        context={"path": error.path, "severity": error.severity.value}
    )

# Convert schema errors
for error in schema_result.errors:
    unified.add_error(error.message, context={"path": error.path})

# Print comprehensive report
unified.print_report()
```

### Serialization

Convert results to dictionaries for JSON output:

```python
result = ValidationResult()
result.add_error("Test error")
result.add_warning("Test warning")

# Get dictionary representation
data = result.to_dict()

import json
print(json.dumps(data, indent=2))
```

## Common Utilities

### Slug Generation

Convert titles to URL-safe slugs for file naming:

```python
from scripts.utilities import generate_slug, ensure_unique_slug
from pathlib import Path

# Generate slug
slug = generate_slug("Introduction to Python Programming")
# Result: "introduction-to-python-programming"

# Ensure uniqueness in directory
output_dir = Path("/exports/presentations")
unique_slug = ensure_unique_slug(slug, output_dir, ".pptx")
# Result: "introduction-to-python-programming-2" if original exists
```

### Repository Root Detection

Find the repository root automatically:

```python
from scripts.utilities import get_repo_root, get_slideforge_root

# Find root by looking for CLAUDE.md
root = get_repo_root()
if root:
    print(f"Repository root: {root}")

    # Access project directories
    templates_dir = root / "templates" / "pptx"
    schemas_dir = root / "schemas" / "presentation"

# Or use the convenience function (raises error if not found)
try:
    root = get_slideforge_root()
    exports_dir = root / "exports"
except RuntimeError as e:
    print(f"Error: {e}")
```

### File Validation

Validate file existence and readability:

```python
from scripts.utilities import validate_file_exists, validate_directory_exists
from pathlib import Path

# Check if file exists
schema_path = Path("schemas/presentation/presentation_schema.json")
result = validate_file_exists(schema_path, file_type="schema")

if result.valid:
    print(f"Schema found at: {schema_path}")
else:
    print(f"Errors: {result.errors}")

# Check/create directory
output_dir = Path("/exports/new_project")
result = validate_directory_exists(output_dir, create=True)
```

### Filename Sanitization

Clean filenames for cross-platform compatibility:

```python
from scripts.utilities import sanitize_filename

# Remove invalid characters
filename = sanitize_filename("My Presentation: Part 1.pptx")
# Result: "My Presentation Part 1.pptx"

# Respect max length
long_name = "A" * 300 + ".pptx"
clean = sanitize_filename(long_name, max_length=200)
```

### Project Directory Creation

Create timestamped project directories:

```python
from scripts.utilities import ensure_output_directory, get_slideforge_root
from pathlib import Path

root = get_slideforge_root()
exports_dir = root / "exports"

# Creates: exports/20251217_143022_presentation-name/
project_dir = ensure_output_directory(exports_dir, "Presentation Name")

# Use the directory
content_dir = project_dir / "02_slide_content"
content_dir.mkdir(parents=True, exist_ok=True)
```

### File Operations

Read text files with validation:

```python
from scripts.utilities import read_text_file, get_file_size_mb
from pathlib import Path

# Read with validation
result = read_text_file(Path("/input/content.md"))

if result.valid:
    content = result.context['content']
    line_count = result.context['line_count']
    print(f"Read {line_count} lines")
else:
    print(f"Failed to read file: {result.errors}")

# Check file size
size_mb = get_file_size_mb(Path("/exports/presentation.pptx"))
if size_mb > 10:
    print(f"Warning: Large file ({size_mb:.2f} MB)")
```

### Project Structure Validation

Validate Slideforge project directories:

```python
from scripts.utilities import validate_project_structure
from pathlib import Path

project_dir = Path("/exports/20251217_143022_presentation")
result = validate_project_structure(project_dir)

if result.valid:
    print("Project structure is valid")
    if 'pptx_files' in result.context:
        print(f"Found PPTX files: {result.context['pptx_files']}")
else:
    print(f"Issues found:")
    for warning in result.warnings:
        print(f"  - {warning}")
```

## Complete Example: Slide Content Validator

Here's a complete example showing how to use ValidationResult in a custom validator:

```python
from pathlib import Path
import json
from scripts.utilities import (
    ValidationResult,
    ValidationSeverity,
    validate_file_exists,
    get_slideforge_root
)

def validate_slide_content(slide_file: Path) -> ValidationResult:
    """Validate slide content JSON file."""
    result = ValidationResult()

    # Check file exists
    file_result = validate_file_exists(slide_file, "slide content")
    result.merge(file_result)

    if not result.valid:
        return result

    # Load and parse JSON
    try:
        with open(slide_file) as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        result.add_error(f"Invalid JSON: {e}", context={"file": str(slide_file)})
        return result

    # Validate required fields
    if "slides" not in data:
        result.add_error("Missing 'slides' field")

    if "metadata" not in data:
        result.add_warning("Missing 'metadata' field")

    # Validate slides
    slides = data.get("slides", [])
    for i, slide in enumerate(slides):
        slide_path = f"slides[{i}]"

        # Check type
        if "type" not in slide:
            result.add_issue(
                message=f"Slide missing 'type' field",
                severity=ValidationSeverity.ERROR,
                path=slide_path
            )

        # Check 6x6 rule
        bullets = slide.get("content", {}).get("bullets", [])
        if len(bullets) > 6:
            result.add_issue(
                message=f"Too many bullets: {len(bullets)} (max 6)",
                severity=ValidationSeverity.WARNING,
                path=f"{slide_path}.content.bullets",
                rule_id="SIX_SIX_BULLETS",
                suggestion="Split into multiple slides"
            )

        # Check word count
        for j, bullet in enumerate(bullets):
            words = len(bullet.split())
            if words > 6:
                result.add_issue(
                    message=f"Bullet too long: {words} words (max 6)",
                    severity=ValidationSeverity.WARNING,
                    path=f"{slide_path}.content.bullets[{j}]",
                    rule_id="SIX_SIX_WORDS",
                    suggestion="Shorten bullet point"
                )

    # Add summary to context
    result.context['total_slides'] = len(slides)
    result.context['validation_complete'] = True

    return result


# Usage
if __name__ == "__main__":
    root = get_slideforge_root()
    slide_file = root / "exports" / "project" / "02_slide_content" / "section_01" / "slides.json"

    result = validate_slide_content(slide_file)
    result.print_report()

    # Exit with appropriate code
    exit(0 if result.valid else 1)
```

## Best Practices

1. **Always use ValidationResult for validation operations**
   - Accumulate all errors instead of failing fast
   - Provide context for debugging

2. **Use structured issues for detailed validation**
   - Include paths, rule IDs, and suggestions
   - Use appropriate severity levels

3. **Merge results from multiple validators**
   - Create comprehensive validation reports
   - Combine structure, schema, and semantic validation

4. **Use utility functions for common tasks**
   - Slug generation for consistent naming
   - File validation before processing
   - Repository root detection for portable paths

5. **Add context to validation results**
   - Store file paths, counts, and metadata
   - Makes debugging easier

6. **Print reports for CLI tools**
   - Use `result.print_report()` for formatted output
   - Use `result.to_dict()` for JSON APIs
