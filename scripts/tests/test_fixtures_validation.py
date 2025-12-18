"""
Test fixture validation
Verifies that presentation fixtures are valid and can be loaded
"""

import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_minimal_presentation_fixture():
    """Test that minimal presentation fixture can be loaded"""
    fixture_path = Path(__file__).parent / 'fixtures' / 'sample_presentations' / 'minimal_5_slides.json'

    with open(fixture_path, 'r') as f:
        data = json.load(f)

    # Verify structure
    assert 'metadata' in data
    assert 'sections' in data
    assert data['metadata']['title'] == 'Minimal Test Presentation'

    # Count slides
    total_slides = sum(len(section['slides']) for section in data['sections'])
    assert total_slides == 5, f"Expected 5 slides, got {total_slides}"

    print(f"✓ Minimal presentation fixture valid (5 slides)")


def test_all_slide_types_fixture():
    """Test that all slide types fixture can be loaded"""
    fixture_path = Path(__file__).parent / 'fixtures' / 'sample_presentations' / 'all_slide_types.json'

    with open(fixture_path, 'r') as f:
        data = json.load(f)

    # Verify structure
    assert 'metadata' in data
    assert 'sections' in data
    assert 'theme' in data

    # Count slides
    total_slides = sum(len(section['slides']) for section in data['sections'])

    # Collect unique slide types
    slide_types = set()
    for section in data['sections']:
        for slide in section['slides']:
            slide_types.add(slide['type'])

    print(f"✓ All slide types fixture valid ({total_slides} slides, {len(slide_types)} unique types)")
    print(f"  Types: {sorted(slide_types)}")


def test_complex_presentation_fixture():
    """Test that complex presentation fixture can be loaded"""
    fixture_path = Path(__file__).parent / 'fixtures' / 'sample_presentations' / 'complex_50_slides.json'

    with open(fixture_path, 'r') as f:
        data = json.load(f)

    # Verify structure
    assert 'metadata' in data
    assert 'sections' in data
    assert len(data['sections']) == 5, "Expected 5 sections"

    # Count slides
    total_slides = sum(len(section['slides']) for section in data['sections'])
    assert total_slides == 50, f"Expected 50 slides, got {total_slides}"

    # Verify each section has 10 slides
    for i, section in enumerate(data['sections'], 1):
        section_slides = len(section['slides'])
        assert section_slides == 10, f"Section {i} expected 10 slides, got {section_slides}"

    print(f"✓ Complex presentation fixture valid (50 slides in 5 sections)")


def test_schema_validation():
    """Test that all fixtures validate against the schema"""
    try:
        from jsonschema import validate, ValidationError
    except ImportError:
        print("⚠ jsonschema not installed, skipping schema validation")
        return

    # Load schema
    schema_path = Path(__file__).parent.parent.parent / 'schemas' / 'presentation' / 'presentation_schema.json'
    with open(schema_path, 'r') as f:
        schema = json.load(f)

    # Test each fixture
    fixtures = [
        'minimal_5_slides.json',
        'all_slide_types.json',
        'complex_50_slides.json'
    ]

    fixture_dir = Path(__file__).parent / 'fixtures' / 'sample_presentations'

    for fixture_name in fixtures:
        fixture_path = fixture_dir / fixture_name
        with open(fixture_path, 'r') as f:
            data = json.load(f)

        try:
            validate(instance=data, schema=schema)
            print(f"✓ {fixture_name} validates against schema")
        except ValidationError as e:
            print(f"✗ {fixture_name} schema validation failed: {e.message}")
            raise


if __name__ == '__main__':
    print("Testing Slideforge Presentation Fixtures")
    print("=" * 60)

    try:
        test_minimal_presentation_fixture()
        test_all_slide_types_fixture()
        test_complex_presentation_fixture()
        test_schema_validation()

        print("=" * 60)
        print("All tests passed! ✓")
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
