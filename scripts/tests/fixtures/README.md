# Test Fixtures

This directory contains test fixtures for Slideforge presentation generation testing.

## Directory Structure

```
fixtures/
├── README.md                          # This file
├── __init__.py                        # Fixture directory paths
├── sample_html/                       # HTML fixtures (accessibility testing)
├── sample_presentations/              # JSON presentation fixtures
│   ├── minimal_5_slides.json          # Minimal valid presentation (5 slides)
│   ├── all_slide_types.json           # All 21 slide types (25 slides)
│   └── complex_50_slides.json         # Large presentation (50 slides)
└── expected_outputs/                  # Expected output files for validation
```

## Presentation Fixtures

### 1. minimal_5_slides.json

A minimal valid presentation with 5 slides for basic functionality testing.

**Structure:**
- 2 sections
- 5 total slides
- Slide types: title, section_header, content, two_content

**Use cases:**
- Basic PPTX generation testing
- Quick validation of core functionality
- Integration testing
- Performance baseline

**Example usage:**
```python
def test_basic_generation(minimal_presentation):
    # minimal_presentation is already loaded JSON
    assert len(minimal_presentation['sections']) == 2
    total_slides = sum(len(s['slides']) for s in minimal_presentation['sections'])
    assert total_slides == 5
```

### 2. all_slide_types.json

Comprehensive presentation demonstrating all 21+ slide types with realistic content.

**Structure:**
- 5 sections
- 25 total slides
- All slide types included

**Slide types covered:**
- Basic: title, section_header, content, two_content, comparison
- Visual: image, quote, blank, image_grid
- Data: table, data_viz, stats_grid
- Process: process_flow, timeline, agenda
- Advanced: comparison_matrix, key_value, callout, cards_grid, key_concept, divider

**Use cases:**
- Layout engine testing
- Slide type rendering validation
- Theme application testing
- Comprehensive feature testing

**Example usage:**
```python
def test_all_layouts(all_slide_types_presentation):
    # Collect all unique slide types
    slide_types = set()
    for section in all_slide_types_presentation['sections']:
        for slide in section['slides']:
            slide_types.add(slide['type'])

    # Verify all types are present
    assert len(slide_types) >= 21
```

### 3. complex_50_slides.json

Large presentation with 50 slides for stress testing and performance evaluation.

**Structure:**
- 5 sections (10 slides each)
- 50 total slides
- Rich content including charts, tables, and various layouts

**Sections:**
1. Introduction (10 slides)
2. Main Content A: Core Architecture Principles (10 slides)
3. Main Content B: Implementation Patterns (10 slides)
4. Advanced Topics: Scaling and Optimization (10 slides)
5. Conclusion (10 slides)

**Use cases:**
- Performance testing
- Stress testing
- Memory usage validation
- Large-scale generation testing
- Section organization testing

**Example usage:**
```python
def test_large_presentation(complex_presentation):
    assert len(complex_presentation['sections']) == 5

    # Verify each section has exactly 10 slides
    for section in complex_presentation['sections']:
        assert len(section['slides']) == 10

    # Test total slide count
    total = sum(len(s['slides']) for s in complex_presentation['sections'])
    assert total == 50
```

## Using Fixtures in Tests

### With pytest

The fixtures are automatically available via `conftest.py`:

```python
def test_presentation_generation(minimal_presentation, presentation_schema):
    """Test using loaded JSON fixture and schema"""
    from jsonschema import validate

    # Validate against schema
    validate(instance=minimal_presentation, schema=presentation_schema)

    # Use the presentation data
    assert minimal_presentation['metadata']['title'] == 'Minimal Test Presentation'


def test_with_file_path(minimal_presentation_path):
    """Test using fixture file path"""
    import json

    with open(minimal_presentation_path, 'r') as f:
        data = json.load(f)

    # Process data...
```

### Available pytest fixtures

From `conftest.py`:

**Loaded JSON fixtures:**
- `minimal_presentation` - Returns loaded JSON dict (5 slides)
- `all_slide_types_presentation` - Returns loaded JSON dict (25 slides)
- `complex_presentation` - Returns loaded JSON dict (50 slides)
- `presentation_schema` - Returns presentation JSON schema

**Path fixtures:**
- `minimal_presentation_path` - Returns Path to minimal_5_slides.json
- `all_slide_types_path` - Returns Path to all_slide_types.json
- `complex_presentation_path` - Returns Path to complex_50_slides.json

### Direct usage

```python
import json
from pathlib import Path

# Load fixture directly
fixture_path = Path(__file__).parent / 'fixtures' / 'sample_presentations' / 'minimal_5_slides.json'
with open(fixture_path, 'r') as f:
    presentation_data = json.load(f)
```

## Schema Validation

All fixtures are validated against `/schemas/presentation/presentation_schema.json`.

To validate a fixture:

```python
from jsonschema import validate, ValidationError

# Load schema and fixture
with open('schemas/presentation/presentation_schema.json') as f:
    schema = json.load(f)

with open('scripts/tests/fixtures/sample_presentations/minimal_5_slides.json') as f:
    presentation = json.load(f)

# Validate
try:
    validate(instance=presentation, schema=schema)
    print("✓ Valid")
except ValidationError as e:
    print(f"✗ Invalid: {e.message}")
```

## Adding New Fixtures

When adding new fixtures:

1. Create the JSON file in `sample_presentations/`
2. Validate against the schema
3. Add a pytest fixture in `conftest.py` if needed
4. Document the fixture in this README
5. Add test coverage in `test_fixtures_validation.py`

### Fixture requirements:

- Must conform to `presentation_schema.json`
- Must include `metadata` with at least a `title`
- Must include `sections` array with at least one section
- Each section must have `slides` array
- Each slide must have a `type` field
- Use realistic content and speaker notes

## Testing Fixtures

Run the fixture validation tests:

```bash
python3 scripts/tests/test_fixtures_validation.py
```

This validates:
- JSON syntax is correct
- Files can be loaded
- Structure matches expected format
- Schema validation passes
- Slide counts are accurate

## Slide Type Reference

| Type | Description | Required Content |
|------|-------------|-----------------|
| title | Opening slide | title, content.subtitle |
| section_header | Section divider | title, content.subtitle (optional) |
| content | Bullet points | title, content.bullets |
| two_content | Two columns | title, content.left, content.right |
| comparison | Labeled comparison | title, content.left_title, content.right_title, left, right |
| image | Image display | title, content.image_path, content.alt_text |
| quote | Quote display | title, content.text, content.attribution |
| blank | Custom content | title |
| table | Data table | title, content.headers, content.rows |
| process_flow | Sequential steps | title, content.steps |
| comparison_matrix | Multi-option comparison | title, content.options, content.criteria |
| timeline | Chronological events | title, content.events |
| key_value | Key-value pairs | title, content.pairs |
| callout | Highlighted boxes | title, content.callouts |
| stats_grid | Statistics cards | title, content.stats |
| cards_grid | Content cards | title, content.cards |
| key_concept | Term definition | title, content.concept_title, content.definition |
| agenda | Meeting agenda | title, content.agenda_items |
| divider | Section divider | title, content.section_number (optional) |
| data_viz | Charts | title, content.chart_type, content.chart_data |
| image_grid | Multiple images | title, content.images |

## Related Documentation

- `/schemas/presentation/presentation_schema.json` - Full JSON schema
- `/docs/slide-design-guide.md` - Slide design best practices
- `/scripts/tests/conftest.py` - Pytest fixture definitions
- `/CLAUDE.md` - Project overview and workflows
