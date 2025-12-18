# Validator Test Suite

Comprehensive unit tests for the three-tier Slideforge validation system.

## Test File

**Location**: `/scripts/tests/test_validators.py`

**Total Tests**: 66 test methods across 6 test classes

## Test Coverage

### 1. StructureValidator Tests (21 tests)

Tests for Level 1 validation - structural integrity and data types.

**Key Test Areas**:
- Root structure validation (dict, required fields)
- Metadata validation (title, author, etc.)
- Sections validation (array, non-empty)
- Slide type validation (valid types, required fields)
- Empty slide detection
- Severity level classification (CRITICAL, ERROR, WARNING, INFO)
- Strict mode enforcement
- Special slide types (table, comparison)

### 2. SchemaValidator Tests (13 tests)

Tests for Level 2 validation - JSON Schema compliance.

**Key Test Areas**:
- Schema compliance for valid presentations
- Invalid data type detection
- Required field enforcement
- Enum validation (slide types)
- Error path formatting
- Partial validation (slides, sections)
- Custom schema loading

### 3. SemanticValidator Tests (13 tests)

Tests for Level 3 validation - quality and pedagogical effectiveness.

**Key Test Areas**:
- 6x6 rule compliance (bullets and word count)
- Speaker notes coverage analysis
- Slide type variety checking
- Quality score calculation
- Issue severity classification
- Accessibility checking (alt text)
- Consistency validation
- Recommendation generation

### 4. Integration Tests (5 tests)

Tests for the complete three-tier validation pipeline.

**Key Test Areas**:
- Running all three validators in sequence
- Validation with different fixture types
- ValidationResult accumulation pattern
- Complex presentation handling

### 5. Edge Case Tests (7 tests)

Tests for error handling and boundary conditions.

**Key Test Areas**:
- Malformed data handling
- Empty presentations
- Missing required structures
- Unicode content support
- Deeply nested content
- Null/None value handling
- Extra unknown field handling

### 6. ValidationResult Utility Tests (7 tests)

Tests for the unified validation result pattern.

**Key Test Areas**:
- Result creation and manipulation
- Error/warning/info accumulation
- Structured issue tracking
- Result merging
- Serialization (to_dict)
- Critical issue filtering

## Running the Tests

### With pytest (recommended)

```bash
# Run all validator tests
pytest scripts/tests/test_validators.py -v

# Run specific test class
pytest scripts/tests/test_validators.py::TestStructureValidator -v

# Run specific test method
pytest scripts/tests/test_validators.py::TestStructureValidator::test_validate_root_structure_valid -v

# Run with coverage report
pytest scripts/tests/test_validators.py --cov=scripts/validators --cov-report=html
```

### Without pytest (manual verification)

```bash
# Syntax check
python3 -m py_compile scripts/tests/test_validators.py

# Import verification
python3 -c "
import sys
from pathlib import Path
sys.path.insert(0, 'scripts/validators')
sys.path.insert(0, 'scripts/utilities')
from structure_validator import StructureValidator
from schema_validator import SchemaValidator
from semantic_validator import SemanticValidator
print('✓ All imports successful')
"
```

## Test Fixtures

Tests use fixtures from `/scripts/tests/fixtures/sample_presentations/`:

- **minimal_5_slides.json** - Basic 5-slide presentation for simple tests
- **all_slide_types.json** - Comprehensive presentation with all slide types
- **complex_50_slides.json** - Large presentation for stress testing

## Test Requirements

**Python Packages**:
- pytest >= 7.0.0
- jsonschema >= 4.0.0 (for schema validation)

**Validator Modules**:
- `scripts/validators/structure_validator.py`
- `scripts/validators/schema_validator.py`
- `scripts/validators/semantic_validator.py`
- `scripts/utilities/validation_result.py`

## Expected Test Results

All 66 tests should pass with the current validator implementation:

```
TestStructureValidator: 21 passed
TestSchemaValidator: 13 passed
TestSemanticValidator: 13 passed
TestThreeTierValidation: 5 passed
TestEdgeCases: 7 passed
TestValidationResultUtility: 7 passed

Total: 66 passed
```

## Test Philosophy

These tests follow the **three-tier validation philosophy**:

1. **Structure Validation** - Fast, catches obvious errors early
2. **Schema Validation** - Ensures compliance with presentation schema
3. **Semantic Validation** - Validates quality, completeness, pedagogy

Tests verify that:
- Valid presentations pass all three tiers
- Invalid presentations are caught at the appropriate tier
- Error messages are clear and actionable
- ValidationResult pattern enables error accumulation
- Edge cases are handled gracefully

## Adding New Tests

When adding tests, follow this structure:

```python
class TestYourFeature:
    """Tests for your new feature"""

    def test_feature_valid_case(self, fixture_name):
        """Test that valid input passes"""
        validator = YourValidator()
        result = validator.validate(valid_data)
        assert result.valid is True

    def test_feature_invalid_case(self):
        """Test that invalid input fails"""
        validator = YourValidator()
        result = validator.validate(invalid_data)
        assert result.valid is False
        assert any("expected error" in e.message for e in result.errors)
```

## Maintenance

- Update tests when validator logic changes
- Add tests for new slide types or validation rules
- Keep fixtures synchronized with schema changes
- Document any new test patterns or utilities
