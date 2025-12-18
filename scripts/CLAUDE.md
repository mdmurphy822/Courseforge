# CLAUDE.md - Scripts Directory Governance

This file provides guidance for creating, managing, and executing scripts in the `/scripts/` directory for PowerPoint presentation generation.

## Repository Purpose - Scripts Context

The `/scripts/` directory contains automation tools for converting structured content into PPTX presentations. All scripts must prioritize reliability, single execution, and atomic operations.

## Core Principles for Script Development

### 1. Atomic Operations (MANDATORY)
- **Single Execution Rule**: Every script executes exactly once per invocation
- **No Intermediate States**: All operations must be atomic - complete success or complete failure
- **Immediate Cleanup**: Any failure triggers immediate cleanup of temporary files
- **Pre-flight Validation**: Validate all inputs before making file system changes

### 2. Reliability Standards
- **Fail-Fast Design**: Detect and report errors immediately
- **Input Validation**: Comprehensive validation before execution
- **Output Verification**: Validate outputs meet specifications
- **Error Logging**: Detailed error reporting with specific failure reasons

### 3. File System Integrity
- **Single Output Files**: Generate exactly one PPTX file per execution
- **No Duplicate Creation**: Prevent numbered duplicate files
- **Collision Detection**: Check for existing outputs before creating
- **Cleanup Responsibility**: Clean up temporary files regardless of outcome

## Script Architecture Standards

### Directory Structure
```
/scripts/
├── CLAUDE.md                 # This governance file
├── README.md                 # Scripts directory documentation
├── requirements.txt          # Python dependencies
├── pptx-generator/           # Core PPTX generation
│   ├── README.md
│   ├── pptx_generator.py
│   ├── config/
│   └── tests/
├── semantic-structure-extractor/  # Content parsing
├── component-applier/        # Layout selection (to adapt)
├── utilities/                # Helper utilities
└── tests/                    # Test infrastructure
```

### Script Naming Conventions
- **Directory Names**: Use kebab-case (e.g., `pptx-generator`, `content-parser`)
- **Script Files**: Use snake_case (e.g., `pptx_generator.py`)
- **Configuration**: Store in `config/` subdirectory as JSON
- **Documentation**: Comprehensive `README.md` in each script directory

## PPTX Generation Requirements

### Critical Success Factors
1. **Valid PPTX Output**: Office Open XML compliant
2. **Theme Application**: Consistent styling throughout
3. **Content Accuracy**: All content from input preserved
4. **Layout Selection**: Appropriate layouts for content types
5. **Single Output**: Exactly one .pptx file per execution

### Modular Script Architecture

#### 1. Content Parser (`content-parser/`)
**Purpose**: Parse various input formats into structured slide data
**Input**: Markdown, JSON, plain text
**Output**: Structured JSON following presentation schema

#### 2. PPTX Generator (`pptx-generator/`)
**Purpose**: Create PowerPoint files from structured content
**Input**: Structured JSON with slide content
**Output**: Single .pptx file
**Dependencies**: python-pptx, Pillow

#### 3. Layout Engine (`slide-layout-engine/`)
**Purpose**: Select optimal layouts for content types
**Input**: Content analysis
**Output**: Layout assignments

## Script Execution Protocol

### Pre-Execution Validation
```python
def validate_execution_environment():
    """Pre-flight checks before execution"""
    # Check output path doesn't exist
    if output_path.exists():
        raise SystemExit(f"Output already exists: {output_path}")

    # Validate inputs
    validate_all_inputs()

    # Check dependencies
    validate_dependencies()
```

### Post-Execution Validation
```python
def validate_outputs():
    """Output validation"""
    # Confirm exactly one output file
    output_files = list(output_dir.glob("*.pptx"))
    if len(output_files) != 1:
        raise SystemExit(f"Expected 1 file, found {len(output_files)}")

    # Validate file format
    validate_pptx_format(output_files[0])
```

## Error Handling Standards

### Failure Classification
- **CRITICAL**: System integrity issues, permission errors
- **HIGH**: Invalid input, missing dependencies
- **MEDIUM**: Quality issues that don't prevent output
- **LOW**: Minor formatting or optimization issues

### Error Response
```python
def handle_error(error_type, message, context):
    """Standardized error handling"""
    log_error(error_type, message, context)
    cleanup_temps()

    if error_type in ['CRITICAL', 'HIGH']:
        raise SystemExit(f"{error_type}: {message}")

    log_warning(message)
```

## Testing Requirements

### Unit Testing
- Minimum 80% code coverage
- Test edge cases and error scenarios
- Mock external dependencies
- Automated test execution

### Integration Testing
- End-to-end PPTX generation
- Template application testing
- Content preservation validation

## Dependencies

```
# requirements.txt
python-pptx>=0.6.21
Pillow>=9.0.0
beautifulsoup4>=4.9.0
lxml>=4.6.0
jsonschema>=4.0.0
PyYAML>=6.0
pytest>=7.0.0
```

## Security Standards

### Input Sanitization
- Validate file paths
- Sanitize user inputs
- Check file types and sizes
- Validate JSON against schemas

### Output Security
- No sensitive information in output
- Validate all file references
- Safe file naming conventions

## Implementation Checklist

### Functional Requirements
- [ ] Generate valid PPTX files
- [ ] Apply themes/templates correctly
- [ ] Preserve all input content
- [ ] Support all slide types
- [ ] Include speaker notes

### Technical Requirements
- [ ] Single execution behavior
- [ ] Atomic operations
- [ ] Comprehensive error handling
- [ ] Complete test coverage

### Quality Requirements
- [ ] Professional documentation
- [ ] Clear usage examples
- [ ] Maintainable code
- [ ] Reliable deployment
