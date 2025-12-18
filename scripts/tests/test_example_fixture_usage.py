"""
Example test demonstrating fixture usage
Shows how to use the presentation fixtures in actual tests
"""

import json
from pathlib import Path


def test_example_using_loaded_fixture_manually():
    """Example: Loading fixture manually (without pytest)"""
    from fixtures import SAMPLE_PRESENTATIONS_DIR

    fixture_path = SAMPLE_PRESENTATIONS_DIR / 'minimal_5_slides.json'

    with open(fixture_path, 'r') as f:
        presentation = json.load(f)

    # Test metadata
    assert presentation['metadata']['title'] == 'Minimal Test Presentation'
    assert presentation['metadata']['author'] == 'Slideforge Test Suite'

    # Test structure
    assert len(presentation['sections']) == 2
    total_slides = sum(len(s['slides']) for s in presentation['sections'])
    assert total_slides == 5

    print("✓ Manual fixture loading works")


def test_example_validate_slide_types():
    """Example: Validating all slide types are present"""
    from fixtures import SAMPLE_PRESENTATIONS_DIR

    fixture_path = SAMPLE_PRESENTATIONS_DIR / 'all_slide_types.json'

    with open(fixture_path, 'r') as f:
        presentation = json.load(f)

    # Collect all slide types
    slide_types = set()
    for section in presentation['sections']:
        for slide in section['slides']:
            slide_types.add(slide['type'])

    # Expected slide types (from schema)
    expected_types = {
        'title', 'section_header', 'content', 'two_content', 'comparison',
        'image', 'quote', 'blank', 'table', 'process_flow',
        'comparison_matrix', 'timeline', 'key_value', 'callout',
        'stats_grid', 'cards_grid', 'key_concept', 'agenda',
        'divider', 'data_viz', 'image_grid'
    }

    # Verify all expected types are present
    assert slide_types >= expected_types, f"Missing types: {expected_types - slide_types}"

    print(f"✓ All {len(slide_types)} slide types present")


def test_example_validate_against_schema():
    """Example: Validating fixture against JSON schema"""
    from fixtures import SAMPLE_PRESENTATIONS_DIR

    try:
        from jsonschema import validate, ValidationError
    except ImportError:
        print("⚠ jsonschema not installed, skipping")
        return

    # Load schema
    schema_path = Path(__file__).parent.parent.parent / 'schemas' / 'presentation' / 'presentation_schema.json'
    with open(schema_path, 'r') as f:
        schema = json.load(f)

    # Load fixture
    fixture_path = SAMPLE_PRESENTATIONS_DIR / 'complex_50_slides.json'
    with open(fixture_path, 'r') as f:
        presentation = json.load(f)

    # Validate
    try:
        validate(instance=presentation, schema=schema)
        print("✓ Fixture validates against schema")
    except ValidationError as e:
        print(f"✗ Validation failed: {e.message}")
        raise


def test_example_section_structure():
    """Example: Testing section structure in complex presentation"""
    from fixtures import SAMPLE_PRESENTATIONS_DIR

    fixture_path = SAMPLE_PRESENTATIONS_DIR / 'complex_50_slides.json'

    with open(fixture_path, 'r') as f:
        presentation = json.load(f)

    # Verify 5 sections with 10 slides each
    assert len(presentation['sections']) == 5, "Expected 5 sections"

    for i, section in enumerate(presentation['sections'], 1):
        slides_count = len(section['slides'])
        assert slides_count == 10, f"Section {i} expected 10 slides, got {slides_count}"
        assert 'title' in section, f"Section {i} missing title"

    print("✓ Complex presentation structure validated")


def test_example_speaker_notes():
    """Example: Verifying speaker notes are present"""
    from fixtures import SAMPLE_PRESENTATIONS_DIR

    fixture_path = SAMPLE_PRESENTATIONS_DIR / 'minimal_5_slides.json'

    with open(fixture_path, 'r') as f:
        presentation = json.load(f)

    # Count slides with notes
    slides_with_notes = 0
    total_slides = 0

    for section in presentation['sections']:
        for slide in section['slides']:
            total_slides += 1
            if 'notes' in slide and slide['notes']:
                slides_with_notes += 1

    # All slides should have speaker notes
    assert slides_with_notes == total_slides, \
        f"Only {slides_with_notes}/{total_slides} slides have notes"

    print(f"✓ All {total_slides} slides have speaker notes")


def test_example_chart_data_structure():
    """Example: Validating chart data structure"""
    from fixtures import SAMPLE_PRESENTATIONS_DIR

    fixture_path = SAMPLE_PRESENTATIONS_DIR / 'all_slide_types.json'

    with open(fixture_path, 'r') as f:
        presentation = json.load(f)

    # Find data_viz slides
    chart_slides = []
    for section in presentation['sections']:
        for slide in section['slides']:
            if slide['type'] == 'data_viz':
                chart_slides.append(slide)

    assert len(chart_slides) > 0, "No chart slides found"

    # Validate chart structure
    for slide in chart_slides:
        assert 'content' in slide
        assert 'chart_type' in slide['content']
        assert 'chart_data' in slide['content']

        chart_data = slide['content']['chart_data']
        assert 'categories' in chart_data
        assert 'series' in chart_data
        assert len(chart_data['series']) > 0

        # Verify series data matches categories
        for series in chart_data['series']:
            assert 'name' in series
            assert 'values' in series
            assert len(series['values']) == len(chart_data['categories']), \
                "Series values must match categories length"

    print(f"✓ Validated {len(chart_slides)} chart slides")


# These tests demonstrate how fixtures would be used with pytest
# When pytest is installed, these same tests can use the conftest fixtures:
"""
def test_with_pytest_fixture(minimal_presentation):
    '''Example using pytest fixture from conftest.py'''
    assert minimal_presentation['metadata']['title'] == 'Minimal Test Presentation'
    assert len(minimal_presentation['sections']) == 2


def test_with_schema_fixture(complex_presentation, presentation_schema):
    '''Example using multiple pytest fixtures'''
    from jsonschema import validate
    validate(instance=complex_presentation, schema=presentation_schema)


def test_with_path_fixture(minimal_presentation_path):
    '''Example using path fixture'''
    import json
    with open(minimal_presentation_path) as f:
        data = json.load(f)
    assert data['metadata']['title'] == 'Minimal Test Presentation'
"""


if __name__ == '__main__':
    print("Running Example Fixture Usage Tests")
    print("=" * 70)

    tests = [
        test_example_using_loaded_fixture_manually,
        test_example_validate_slide_types,
        test_example_validate_against_schema,
        test_example_section_structure,
        test_example_speaker_notes,
        test_example_chart_data_structure,
    ]

    for test_func in tests:
        print(f"\n{test_func.__name__}:")
        print(f"  {test_func.__doc__.strip()}")
        try:
            test_func()
        except AssertionError as e:
            print(f"  ✗ Test failed: {e}")
        except Exception as e:
            print(f"  ✗ Error: {e}")

    print("\n" + "=" * 70)
    print("Example tests completed!")
