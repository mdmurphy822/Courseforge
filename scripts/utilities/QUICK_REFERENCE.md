# Slideforge Utilities - Quick Reference Card

## ValidationResult Pattern

### Import
```python
from scripts.utilities import ValidationResult, ValidationSeverity
```

### Basic Usage
```python
# Create result
result = ValidationResult()

# Add errors (invalidates result)
result.add_error("Missing field: title")
result.add_error("Invalid value", context={"field": "type", "value": "unknown"})

# Add warnings (doesn't invalidate)
result.add_warning("Title is too short")

# Check validity
if not result.valid:
    print(f"Found {result.error_count} errors")
```

### Structured Issues
```python
result.add_issue(
    message="Too many bullets (8 found, max 6)",
    severity=ValidationSeverity.ERROR,
    path="sections[0].slides[2]",
    rule_id="SIX_SIX_RULE",
    suggestion="Split into 2 slides"
)
```

### Merge Results
```python
result1 = ValidationResult()
result2 = ValidationResult()
result1.merge(result2)  # Combine results
```

### Output
```python
result.print_report()           # Pretty print
data = result.to_dict()         # Convert to dict
summary = result.to_summary()   # Get summary string
```

## Common Utilities

### Import
```python
from scripts.utilities import (
    generate_slug,
    ensure_unique_slug,
    get_slideforge_root,
    validate_file_exists,
    validate_directory_exists,
    ensure_output_directory,
    sanitize_filename,
    read_text_file
)
```

### Slug Generation
```python
slug = generate_slug("My Presentation Title")
# → "my-presentation-title"

unique = ensure_unique_slug(slug, output_dir, ".pptx")
# → "my-presentation-title-2" (if original exists)
```

### Repository Navigation
```python
root = get_slideforge_root()
templates = root / "templates" / "pptx"
schemas = root / "schemas" / "presentation"
```

### File Validation
```python
result = validate_file_exists(file_path, "schema")
if result.valid:
    print("File exists and is readable")

result = validate_directory_exists(dir_path, create=True)
```

### File Operations
```python
# Sanitize filename
clean = sanitize_filename("File: Name*.txt")
# → "File Name.txt"

# Read with validation
result = read_text_file(file_path)
if result.valid:
    content = result.context['content']
```

### Output Directory
```python
# Create timestamped project directory
project_dir = ensure_output_directory(
    exports_dir,
    "Presentation Name"
)
# Creates: exports/20251217_143022_presentation-name/
```

## Integration with Validators

### Three-Tier Validation
```python
from scripts.validators import (
    StructureValidator,
    SchemaValidator,
    SemanticValidator
)
from scripts.utilities import ValidationResult, ValidationSeverity

# Run all validators
unified = ValidationResult()

# Structure validation
struct = StructureValidator().validate(data)
for error in struct.errors:
    unified.add_error(error.message, context={"path": error.path})

# Schema validation
schema = SchemaValidator().validate(data)
for error in schema.errors:
    unified.add_error(error.message, context={"path": error.path})

# Semantic validation
semantic = SemanticValidator().validate(data)
for issue in semantic.issues:
    unified.add_issue(
        message=issue.message,
        severity=ValidationSeverity.WARNING,
        path=issue.location
    )

# Comprehensive report
unified.print_report()
```

## Severity Levels

| Level | Use Case |
|-------|----------|
| `CRITICAL` | System failure, cannot continue |
| `ERROR` | Validation failure, must fix |
| `WARNING` | Should fix, doesn't block |
| `INFO` | Informational, optional |

## ValidationResult Properties

| Property | Description |
|----------|-------------|
| `.valid` | Boolean validity status |
| `.errors` | List of error messages |
| `.warnings` | List of warning messages |
| `.info` | List of info messages |
| `.issues` | List of structured ValidationIssue objects |
| `.context` | Dictionary for additional data |
| `.error_count` | Number of errors |
| `.warning_count` | Number of warnings |
| `.critical_issues` | List of critical issues only |

## Common Patterns

### Validate and Process File
```python
result = validate_file_exists(input_file, "presentation")
if not result.valid:
    print(f"Error: {result.errors[0]}")
    return result

# Process file...
result.add_info("Processing completed successfully")
return result
```

### Create Project Structure
```python
root = get_slideforge_root()
exports = root / "exports"

# Create unique project directory
project_dir = ensure_output_directory(exports, project_name)

# Create subdirectories
(project_dir / "01_content_analysis").mkdir()
(project_dir / "02_slide_content").mkdir()
(project_dir / "03_final_output").mkdir()
```

### Accumulate Validation Errors
```python
result = ValidationResult()

for slide in slides:
    if not slide.get("title"):
        result.add_warning(f"Slide {i} missing title")

    bullets = slide.get("content", {}).get("bullets", [])
    if len(bullets) > 6:
        result.add_issue(
            message=f"Too many bullets: {len(bullets)}",
            severity=ValidationSeverity.ERROR,
            path=f"slides[{i}]",
            suggestion="Split into multiple slides"
        )

return result
```

## Testing

Run comprehensive tests:
```bash
python3 scripts/utilities/test_utilities.py
```

Run integration example:
```bash
python3 scripts/utilities/integration_example.py
```

## Documentation

- **Full Usage Guide**: `scripts/utilities/USAGE.md`
- **Module Documentation**: `scripts/utilities/README.md`
- **This Quick Reference**: `scripts/utilities/QUICK_REFERENCE.md`

## Tips

1. Always use `ValidationResult` for validation operations
2. Accumulate errors instead of failing fast
3. Provide context for debugging
4. Use structured issues with rule IDs
5. Merge results from multiple validators
6. Use `get_slideforge_root()` for portable paths
7. Sanitize user-provided filenames
8. Create unique output directories with timestamps
