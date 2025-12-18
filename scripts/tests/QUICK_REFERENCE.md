# Pipeline Integration Tests - Quick Reference

## Test File Location
`/home/bacon/Desktop/Slideforge/scripts/tests/test_pipeline_integration.py`

## All 29 Tests

### TestFullPipeline (5 tests)
```bash
# Test complete Markdown → PPTX workflow
pytest tests/test_pipeline_integration.py::TestFullPipeline::test_full_pipeline_markdown_input -v

# Test complete JSON → PPTX workflow
pytest tests/test_pipeline_integration.py::TestFullPipeline::test_full_pipeline_json_input -v

# Test pipeline with theme selection
pytest tests/test_pipeline_integration.py::TestFullPipeline::test_full_pipeline_with_theme -v

# Test pipeline with quality validation enabled
pytest tests/test_pipeline_integration.py::TestFullPipeline::test_full_pipeline_with_validation -v

# Test validation-only mode (no PPTX generation)
pytest tests/test_pipeline_integration.py::TestFullPipeline::test_validate_only_mode -v
```

### TestStageIsolation (6 tests)
```bash
# Test content loading and format detection
pytest tests/test_pipeline_integration.py::TestStageIsolation::test_ingestion_stage -v

# Test semantic structure extraction
pytest tests/test_pipeline_integration.py::TestStageIsolation::test_extraction_stage -v

# Test presentation schema transformation
pytest tests/test_pipeline_integration.py::TestStageIsolation::test_transformation_stage -v

# Test template/theme selection
pytest tests/test_pipeline_integration.py::TestStageIsolation::test_template_selection_stage -v

# Test quality validation
pytest tests/test_pipeline_integration.py::TestStageIsolation::test_validation_stage -v

# Test PPTX file generation
pytest tests/test_pipeline_integration.py::TestStageIsolation::test_generation_stage -v
```

### TestErrorHandling (4 tests)
```bash
# Test invalid JSON/content handling
pytest tests/test_pipeline_integration.py::TestErrorHandling::test_pipeline_invalid_input -v

# Test missing input file handling
pytest tests/test_pipeline_integration.py::TestErrorHandling::test_pipeline_missing_file -v

# Test validation failure scenarios
pytest tests/test_pipeline_integration.py::TestErrorHandling::test_pipeline_validation_failure -v

# Test partial result recovery on failure
pytest tests/test_pipeline_integration.py::TestErrorHandling::test_pipeline_partial_recovery -v
```

### TestManifestIntegration (6 tests)
```bash
# Test manifest initialization
pytest tests/test_pipeline_integration.py::TestManifestIntegration::test_manifest_creation -v

# Test stage execution tracking
pytest tests/test_pipeline_integration.py::TestManifestIntegration::test_manifest_stage_tracking -v

# Test source provenance capture
pytest tests/test_pipeline_integration.py::TestManifestIntegration::test_manifest_provenance -v

# Test manifest save/load functionality
pytest tests/test_pipeline_integration.py::TestManifestIntegration::test_manifest_persistence -v

# Test quality metrics tracking
pytest tests/test_pipeline_integration.py::TestManifestIntegration::test_manifest_quality_metadata -v

# Test processing log maintenance
pytest tests/test_pipeline_integration.py::TestManifestIntegration::test_manifest_processing_log -v
```

### TestFixtureIntegration (3 tests)
```bash
# Test with minimal_5_slides.json fixture
pytest tests/test_pipeline_integration.py::TestFixtureIntegration::test_integration_minimal_fixture -v

# Test with all_slide_types.json fixture
pytest tests/test_pipeline_integration.py::TestFixtureIntegration::test_integration_all_types_fixture -v

# Test with complex_50_slides.json fixture
pytest tests/test_pipeline_integration.py::TestFixtureIntegration::test_integration_complex_fixture -v
```

### TestConfigIntegration (3 tests)
```bash
# Test configuration respect and storage
pytest tests/test_pipeline_integration.py::TestConfigIntegration::test_pipeline_with_config -v

# Test metadata override behavior
pytest tests/test_pipeline_integration.py::TestConfigIntegration::test_pipeline_config_override -v

# Test quality settings enforcement
pytest tests/test_pipeline_integration.py::TestConfigIntegration::test_pipeline_quality_settings -v
```

### TestPerformance (2 tests)
```bash
# Test execution time tracking
pytest tests/test_pipeline_integration.py::TestPerformance::test_pipeline_timing_tracking -v

# Test individual stage timing
pytest tests/test_pipeline_integration.py::TestPerformance::test_stage_duration_tracking -v
```

## Common Test Commands

### Run all tests
```bash
cd scripts
pytest tests/test_pipeline_integration.py -v
```

### Run all tests in a specific class
```bash
pytest tests/test_pipeline_integration.py::TestFullPipeline -v
pytest tests/test_pipeline_integration.py::TestStageIsolation -v
pytest tests/test_pipeline_integration.py::TestErrorHandling -v
pytest tests/test_pipeline_integration.py::TestManifestIntegration -v
```

### Run tests by keyword
```bash
# All tests with 'manifest' in the name
pytest tests/test_pipeline_integration.py -k 'manifest' -v

# All tests with 'error' in the name
pytest tests/test_pipeline_integration.py -k 'error' -v

# All tests with 'stage' in the name
pytest tests/test_pipeline_integration.py -k 'stage' -v

# All tests with 'fixture' in the name
pytest tests/test_pipeline_integration.py -k 'fixture' -v
```

### Run with different output modes
```bash
# Quiet (only show failures)
pytest tests/test_pipeline_integration.py -q

# Very verbose
pytest tests/test_pipeline_integration.py -vv

# Show print statements
pytest tests/test_pipeline_integration.py -s

# Short traceback
pytest tests/test_pipeline_integration.py --tb=short

# No traceback
pytest tests/test_pipeline_integration.py --tb=no
```

### Run with coverage
```bash
# Text coverage report
pytest tests/test_pipeline_integration.py --cov=pipeline

# HTML coverage report
pytest tests/test_pipeline_integration.py --cov=pipeline --cov-report=html

# Open HTML report
firefox htmlcov/index.html
```

## Alternative Runners

### Basic runner (no pytest required)
```bash
cd scripts/tests
python3 run_pipeline_tests_basic.py
```

### Validation only
```bash
cd scripts/tests
python3 validate_pipeline_tests.py
```

## Test Categories by Purpose

### Smoke Tests (Quick validation)
```bash
pytest tests/test_pipeline_integration.py::TestFullPipeline::test_full_pipeline_markdown_input -v
pytest tests/test_pipeline_integration.py::TestManifestIntegration::test_manifest_creation -v
```

### Comprehensive Tests (Full coverage)
```bash
pytest tests/test_pipeline_integration.py -v
```

### Error Testing (Edge cases)
```bash
pytest tests/test_pipeline_integration.py::TestErrorHandling -v
```

### Performance Testing
```bash
pytest tests/test_pipeline_integration.py::TestPerformance -v
```

## Expected Execution Times

- Single test: ~1-3 seconds
- Test class (5-6 tests): ~5-15 seconds
- All tests (29 tests): ~45-60 seconds
- Basic runner (5 tests): ~10-15 seconds
- Validation only: < 1 second

## Test Fixtures Used

```
fixtures/sample_presentations/
├── minimal_5_slides.json        # Used by test_integration_minimal_fixture
├── all_slide_types.json         # Used by test_integration_all_types_fixture
└── complex_50_slides.json       # Used by test_integration_complex_fixture
```

## Helper Functions Available

```python
# Test data creation
create_sample_markdown(path)  # Generate sample Markdown file
create_sample_json(path)      # Generate sample JSON presentation

# Validation
validate_pptx_output(path)    # Verify PPTX file is valid
validate_manifest(path)        # Verify manifest file is valid
```

## Pytest Markers (Future)

When adding markers to tests:

```python
@pytest.mark.slow         # Mark slow tests
@pytest.mark.integration  # Mark integration tests
@pytest.mark.unit         # Mark unit tests
```

Run marked tests:
```bash
pytest tests/test_pipeline_integration.py -m slow
pytest tests/test_pipeline_integration.py -m integration
```

## Continuous Integration

### GitHub Actions
```yaml
- name: Run pipeline tests
  run: |
    cd scripts
    pytest tests/test_pipeline_integration.py -v --tb=short
```

### GitLab CI
```yaml
test:
  script:
    - cd scripts
    - pytest tests/test_pipeline_integration.py -v
```

## Troubleshooting Quick Fixes

### Import errors
```bash
cd scripts  # Must be in scripts directory
```

### Missing dependencies
```bash
pip install pytest python-pptx Pillow beautifulsoup4 jsonschema
```

### Permission errors
```bash
rm -rf /tmp/pytest-*
```

### Can't find fixtures
```bash
ls scripts/tests/fixtures/sample_presentations/
```

---

**Quick Start:**
1. `cd scripts`
2. `pytest tests/test_pipeline_integration.py -v`

**Documentation:**
- Full guide: `PIPELINE_TESTS_README.md`
- Summary: `PIPELINE_INTEGRATION_TESTS_SUMMARY.md`
- This file: `QUICK_REFERENCE.md`
