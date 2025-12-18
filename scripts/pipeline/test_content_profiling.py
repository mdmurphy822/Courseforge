#!/usr/bin/env python3
"""Test content profiling functionality"""

import json
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from pipeline.manifest import (
    extract_presentation_profile,
    calculate_vocabulary_richness,
    calculate_content_complexity
)


def test_extract_presentation_profile():
    """Test profile extraction from sample presentation"""

    # Sample presentation
    presentation = {
        "metadata": {
            "title": "Test Presentation",
            "author": "Test Author"
        },
        "sections": [
            {
                "title": "Introduction",
                "slides": [
                    {
                        "type": "title",
                        "title": "Welcome to Testing",
                        "content": {
                            "subtitle": "A comprehensive guide"
                        },
                        "notes": "This is an introduction slide."
                    },
                    {
                        "type": "content",
                        "title": "Key Points",
                        "content": {
                            "bullets": [
                                "First important point here",
                                "Second critical detail",
                                "Third essential item",
                                "Fourth key concept",
                                "Fifth major topic"
                            ]
                        },
                        "notes": "Review these points carefully."
                    }
                ]
            },
            {
                "title": "Main Content",
                "slides": [
                    {
                        "type": "two_content",
                        "title": "Comparison",
                        "content": {
                            "left_title": "Pros",
                            "left": [
                                "Advantage one",
                                "Advantage two",
                                "Advantage three"
                            ],
                            "right_title": "Cons",
                            "right": [
                                "Disadvantage one",
                                "Disadvantage two"
                            ]
                        }
                    },
                    {
                        "type": "table",
                        "title": "Data Summary",
                        "content": {
                            "headers": ["Item", "Value", "Status"],
                            "rows": [
                                ["Alpha", "100", "Active"],
                                ["Beta", "200", "Pending"]
                            ]
                        },
                        "notes": "Table shows current metrics."
                    },
                    {
                        "type": "image",
                        "title": "Visual Example",
                        "content": {
                            "image_path": "/path/to/image.png",
                            "alt_text": "Sample diagram"
                        }
                    },
                    {
                        "type": "data_viz",
                        "title": "Statistics",
                        "content": {
                            "chart_type": "column_clustered",
                            "chart_data": {
                                "categories": ["Q1", "Q2", "Q3"],
                                "series": [
                                    {
                                        "name": "Sales",
                                        "values": [100, 150, 200]
                                    }
                                ]
                            }
                        },
                        "notes": "Chart displays quarterly trends."
                    }
                ]
            }
        ]
    }

    print("Testing extract_presentation_profile()...")
    profile = extract_presentation_profile(presentation)

    print(f"\n✓ Total Slides: {profile.total_slides}")
    print(f"✓ Total Sections: {profile.total_sections}")
    print(f"✓ Total Words: {profile.total_words}")
    print(f"✓ Total Characters: {profile.total_characters}")
    print(f"✓ Slide Type Distribution: {profile.slide_type_distribution}")
    print(f"✓ Section Sizes: {profile.section_sizes}")
    print(f"✓ Speaker Notes Coverage: {profile.speaker_notes_coverage:.2%}")
    print(f"✓ Average Bullets Per Slide: {profile.average_bullets_per_slide:.2f}")
    print(f"✓ Average Words Per Bullet: {profile.average_words_per_bullet:.2f}")
    print(f"✓ 6x6 Compliance: {profile.six_by_six_compliance:.2%}")
    print(f"✓ Vocabulary Richness: {profile.vocabulary_richness:.3f}")
    print(f"✓ Average Sentence Length: {profile.average_sentence_length:.2f}")
    print(f"✓ Images Count: {profile.images_count}")
    print(f"✓ Tables Count: {profile.tables_count}")
    print(f"✓ Charts Count: {profile.charts_count}")

    # Verify expectations
    assert profile.total_slides == 6, f"Expected 6 slides, got {profile.total_slides}"
    assert profile.total_sections == 2, f"Expected 2 sections, got {profile.total_sections}"
    assert profile.speaker_notes_coverage > 0, "Should have some notes coverage"
    assert profile.images_count == 1, f"Expected 1 image, got {profile.images_count}"
    assert profile.tables_count == 1, f"Expected 1 table, got {profile.tables_count}"
    assert profile.charts_count == 1, f"Expected 1 chart, got {profile.charts_count}"

    print("\n✓ All assertions passed!")


def test_vocabulary_richness():
    """Test vocabulary richness calculation"""

    print("\nTesting calculate_vocabulary_richness()...")

    texts = [
        "The quick brown fox jumps over the lazy dog",
        "The fox is quick and brown",
        "The dog is lazy"
    ]

    richness = calculate_vocabulary_richness(texts)
    print(f"✓ Type-Token Ratio: {richness:.3f}")

    # With repetition, richness should be < 1.0
    assert 0 < richness < 1.0, f"Expected ratio between 0 and 1, got {richness}"

    print("✓ Test passed!")


def test_content_complexity():
    """Test content complexity calculation"""

    print("\nTesting calculate_content_complexity()...")

    presentation = {
        "sections": [
            {
                "slides": [
                    {
                        "title": "Simple Test",
                        "content": {
                            "bullets": [
                                "This is a short sentence.",
                                "Another brief statement here.",
                                "A third concise point."
                            ]
                        },
                        "notes": "These are simple sentences for testing."
                    }
                ]
            }
        ]
    }

    complexity = calculate_content_complexity(presentation)

    print(f"✓ Average Sentence Length: {complexity['average_sentence_length']}")
    print(f"✓ Vocabulary Diversity: {complexity['vocabulary_diversity']}")
    print(f"✓ Reading Level: {complexity['reading_level']}")

    assert 'average_sentence_length' in complexity
    assert 'vocabulary_diversity' in complexity
    assert 'reading_level' in complexity
    assert complexity['reading_level'] in ['basic', 'intermediate', 'advanced']

    print("✓ Test passed!")


def test_to_dict():
    """Test profile serialization"""

    print("\nTesting PresentationProfile.to_dict()...")

    from pipeline.manifest import PresentationProfile

    profile = PresentationProfile(
        total_slides=10,
        total_sections=3,
        total_words=500,
        slide_type_distribution={"content": 7, "title": 1, "section_header": 2}
    )

    data = profile.to_dict()

    print(f"✓ Serialized profile: {json.dumps(data, indent=2)}")

    # Test round-trip
    profile2 = PresentationProfile.from_dict(data)
    assert profile2.total_slides == profile.total_slides
    assert profile2.total_sections == profile.total_sections

    print("✓ Serialization test passed!")


if __name__ == '__main__':
    print("=" * 60)
    print("Content Profiling Test Suite")
    print("=" * 60)

    try:
        test_extract_presentation_profile()
        test_vocabulary_richness()
        test_content_complexity()
        test_to_dict()

        print("\n" + "=" * 60)
        print("✓ ALL TESTS PASSED")
        print("=" * 60)

    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
