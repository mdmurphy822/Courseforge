# Pipeline Integration Tests

Comprehensive end-to-end integration tests for the Slideforge pipeline.

## Overview

The `test_pipeline_integration.py` file contains 29 comprehensive tests covering the full presentation generation pipeline from input to PPTX output.

## Test Coverage

### 1. Full Pipeline Tests (5 tests)
- `test_full_pipeline_markdown_input` - Complete Markdown → PPTX workflow
- `test_full_pipeline_json_input` - Complete JSON → PPTX workflow
- `test_full_pipeline_with_theme` - Pipeline with theme selection
- `test_full_pipeline_with_validation` - Pipeline with quality validation enabled
- `test_validate_only_mode` - Validation-only mode (no PPTX generation)

### 2. Stage Isolation Tests (6 tests)
Tests each pipeline stage independently:
- `test_ingestion_stage` - Content loading and format detection
- `test_extraction_stage` - Semantic structure extraction
- `test_transformation_stage` - Presentation schema transformation
- `test_template_selection_stage` - Template/theme selection
- `test_validation_stage` - Quality validation
- `test_generation_stage` - PPTX file generation

### 3. Error Handling Tests (4 tests)
- `test_pipeline_invalid_input` - Invalid JSON/content handling
- `test_pipeline_missing_file` - Missing input file handling
- `test_pipeline_validation_failure` - Validation failure scenarios
- `test_pipeline_partial_recovery` - Partial result recovery on failure

### 4. Manifest/Provenance Tests (6 tests)
- `test_manifest_creation` - Manifest initialization
- `test_manifest_stage_tracking` - Stage execution tracking
- `test_manifest_provenance` - Source provenance capture
- `test_manifest_persistence` - Manifest save/load functionality
- `test_manifest_quality_metadata` - Quality metrics tracking
- `test_manifest_processing_log` - Processing log maintenance

### 5. Fixture Integration Tests (3 tests)
Tests using standard test fixtures:
- `test_integration_minimal_fixture` - 5-slide minimal presentation
- `test_integration_all_types_fixture` - All slide types demonstration
- `test_integration_complex_fixture` - 50-slide complex presentation

### 6. Configuration Integration Tests (3 tests)
- `test_pipeline_with_config` - Configuration respect and storage
- `test_pipeline_config_override` - Metadata override behavior
- `test_pipeline_quality_settings` - Quality settings enforcement

### 7. Performance Tests (2 tests)
- `test_pipeline_timing_tracking` - Execution time tracking
- `test_stage_duration_tracking` - Individual stage timing

## Running Tests

### Prerequisites

Install test dependencies:

```bash
# Option 1: Using apt (system-wide)
sudo apt install python3-pytest python3-pptx

# Option 2: Using virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Run All Tests

```bash
cd scripts
pytest tests/test_pipeline_integration.py -v
```

### Run Specific Test Class

```bash
# Full pipeline tests
pytest tests/test_pipeline_integration.py::TestFullPipeline -v

# Stage isolation tests
pytest tests/test_pipeline_integration.py::TestStageIsolation -v

# Error handling tests
pytest tests/test_pipeline_integration.py::TestErrorHandling -v

# Manifest tests
pytest tests/test_pipeline_integration.py::TestManifestIntegration -v
```

### Run Specific Test

```bash
pytest tests/test_pipeline_integration.py::TestFullPipeline::test_full_pipeline_markdown_input -v
```

### Run Tests by Keyword

```bash
# Run all tests containing 'manifest'
pytest tests/test_pipeline_integration.py -k 'manifest' -v

# Run all tests containing 'error'
pytest tests/test_pipeline_integration.py -k 'error' -v

# Run all tests containing 'fixture'
pytest tests/test_pipeline_integration.py -k 'fixture' -v
```

### Run with Coverage Report

```bash
pytest tests/test_pipeline_integration.py --cov=pipeline --cov-report=html
```

### Run with Different Verbosity

```bash
# Quiet mode (only show failures)
pytest tests/test_pipeline_integration.py -q

# Very verbose (show all details)
pytest tests/test_pipeline_integration.py -vv

# Show output from print statements
pytest tests/test_pipeline_integration.py -s
```

## Test Fixtures

Tests use the following fixtures from `conftest.py`:

- `temp_output_dir` - Temporary directory for output files
- `minimal_presentation_path` - Path to 5-slide minimal test fixture
- `all_slide_types_path` - Path to all slide types test fixture
- `complex_presentation_path` - Path to 50-slide complex test fixture

## Test Utilities

Helper functions provided:

- `create_sample_markdown(path)` - Generate sample Markdown file
- `create_sample_json(path)` - Generate sample JSON presentation
- `validate_pptx_output(path)` - Validate PPTX file integrity
- `validate_manifest(path)` - Validate manifest file

## Expected Outcomes

### Successful Test Run

```
======================== test session starts ========================
collected 29 items

tests/test_pipeline_integration.py::TestFullPipeline::test_full_pipeline_markdown_input PASSED [  3%]
tests/test_pipeline_integration.py::TestFullPipeline::test_full_pipeline_json_input PASSED [  6%]
...
======================== 29 passed in 45.23s ========================
```

### Test Artifacts

Each test run creates temporary artifacts:

```
/tmp/pytest-*/
├── test_full_pipeline_markdown_input/
│   ├── input.md
│   ├── output.pptx
│   └── output_manifest.json
├── test_stage_isolation/
│   ├── ingestion_test.md
│   └── ...
└── ...
```

All temporary files are automatically cleaned up after tests complete.

## Continuous Integration

### GitHub Actions Example

```yaml
name: Pipeline Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      - name: Install dependencies
        run: |
          pip install -r scripts/requirements.txt
      - name: Run pipeline tests
        run: |
          cd scripts
          pytest tests/test_pipeline_integration.py -v --tb=short
```

## Troubleshooting

### Import Errors

If you see import errors:

```bash
# Ensure you're in the scripts directory
cd scripts

# Run tests from scripts directory
pytest tests/test_pipeline_integration.py -v
```

### Missing Dependencies

If tests fail due to missing dependencies:

```bash
# Install all dependencies
pip install python-pptx Pillow beautifulsoup4 jsonschema pytest
```

### Permission Errors

If you see permission errors on temporary files:

```bash
# Clean up any stale temp directories
rm -rf /tmp/pytest-*
```

### Template Not Found

If template selection fails:

```bash
# Ensure template files exist
ls scripts/pptx-generator/templates/
```

## Validation Script

To validate test structure without running pytest:

```bash
cd scripts/tests
python3 validate_pipeline_tests.py
```

This script analyzes the test file structure and confirms all expected test classes and methods are present.

## Test File Organization

```
test_pipeline_integration.py
├── Imports and Setup (lines 1-30)
├── Helper Functions (lines 33-95)
├── TestFullPipeline (lines 98-200)
├── TestStageIsolation (lines 203-350)
├── TestErrorHandling (lines 353-450)
├── TestManifestIntegration (lines 453-580)
├── TestFixtureIntegration (lines 583-660)
├── TestConfigIntegration (lines 663-730)
└── TestPerformance (lines 733-800)
```

## Contributing

When adding new tests:

1. Follow existing naming conventions (`test_*`)
2. Add comprehensive docstrings
3. Use appropriate test fixtures
4. Clean up temporary files
5. Add assertions for both success and failure cases
6. Update this README with new test descriptions

## Related Documentation

- [Pipeline Orchestrator](../pipeline/orchestrator.py) - Main pipeline implementation
- [Manifest System](../pipeline/manifest.py) - Provenance tracking
- [Test Fixtures](fixtures/sample_presentations/) - Standard test data
- [Getting Started Guide](../../docs/getting-started.md) - Project setup

## Support

For issues or questions:

1. Check the [Troubleshooting Guide](../../docs/troubleshooting.md)
2. Review test logs for specific error messages
3. Validate test fixture files are present and valid
4. Ensure all dependencies are installed

---

**Last Updated:** 2025-12-17
**Test Count:** 29 tests across 7 test classes
**Coverage:** Full pipeline, stage isolation, error handling, manifest tracking, fixtures, configuration, and performance
