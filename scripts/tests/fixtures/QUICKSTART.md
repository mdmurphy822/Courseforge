# Slideforge Test Fixtures - Quick Start Guide

## Overview

Three presentation fixtures are available for testing:

- **minimal_5_slides.json** - 5 slides for basic testing
- **all_slide_types.json** - 25 slides covering all 21 slide types
- **complex_50_slides.json** - 50 slides for stress testing

## Quick Usage

### With pytest fixtures (Recommended)

```python
def test_my_feature(minimal_presentation):
    """Test using pytest fixture - already loaded"""
    assert minimal_presentation['metadata']['title'] == 'Minimal Test Presentation'
    assert len(minimal_presentation['sections']) == 2
```

### Direct import

```python
from fixtures import SAMPLE_PRESENTATIONS_DIR
import json

# Load any fixture
with open(SAMPLE_PRESENTATIONS_DIR / 'minimal_5_slides.json') as f:
    presentation = json.load(f)
```

## Available Pytest Fixtures

### Loaded JSON (Ready to use)

- `minimal_presentation` - 5 slides
- `all_slide_types_presentation` - 25 slides, all types
- `complex_presentation` - 50 slides
- `presentation_schema` - JSON schema

### Paths (For custom loading)

- `minimal_presentation_path`
- `all_slide_types_path`
- `complex_presentation_path`

## Common Test Patterns

### Validate Against Schema

```python
def test_schema_validation(minimal_presentation, presentation_schema):
    from jsonschema import validate
    validate(instance=minimal_presentation, schema=presentation_schema)
```

### Test Slide Count

```python
def test_slide_count(complex_presentation):
    total = sum(len(s['slides']) for s in complex_presentation['sections'])
    assert total == 50
```

### Test All Slide Types

```python
def test_slide_types(all_slide_types_presentation):
    types = set()
    for section in all_slide_types_presentation['sections']:
        for slide in section['slides']:
            types.add(slide['type'])

    assert len(types) >= 21  # All slide types present
```

### Test PPTX Generation

```python
def test_pptx_generation(minimal_presentation, tmp_path):
    output_path = tmp_path / 'test.pptx'

    # Your PPTX generator
    generate_pptx(minimal_presentation, output_path)

    assert output_path.exists()
    assert output_path.stat().st_size > 0
```

## Which Fixture to Use?

| Test Type | Use |
|-----------|-----|
| Unit tests | `minimal_presentation` |
| Integration tests | `minimal_presentation` or `all_slide_types_presentation` |
| Feature tests | `all_slide_types_presentation` |
| Stress tests | `complex_presentation` |
| Performance tests | `complex_presentation` |

## Fixture Details

### minimal_5_slides.json
- **Sections:** 2
- **Slides:** 5
- **Types:** title, section_header, content, two_content
- **Best for:** Quick validation, CI/CD

### all_slide_types.json
- **Sections:** 5
- **Slides:** 25
- **Types:** All 21 types
- **Best for:** Layout testing, comprehensive validation

### complex_50_slides.json
- **Sections:** 5 (10 slides each)
- **Slides:** 50
- **Types:** 18 types
- **Best for:** Performance testing, stress testing

## Running Tests

```bash
# Validate fixtures
python3 scripts/tests/test_fixtures_validation.py

# Run example tests
python3 scripts/tests/test_example_fixture_usage.py

# With pytest (when installed)
pytest scripts/tests/ -v
```

## More Information

See [README.md](README.md) for comprehensive documentation.
