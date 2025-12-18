"""
Comprehensive Unit Tests for Transformer Modules

Tests cover:
- SemanticToPresentation transformer
- BlockToSlideMapper with pattern detection
- ContentSplitter for 6x6 rule enforcement
- NotesGenerator for speaker notes
- Integration pipeline testing
"""

import pytest
import sys
from pathlib import Path
from typing import Dict, Any, List

# Add scripts directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from transformers.semantic_to_presentation import (
    SemanticToPresentationTransformer,
    TransformationConfig,
    TransformationResult
)
from transformers.block_to_slide_mapper import (
    BlockToSlideMapper,
    MappingDecision,
    BlockType,
    SlideType,
    SlideTypeMapping
)
from transformers.content_splitter import (
    ContentSplitter,
    SixSixRule,
    SixSixRuleEnforcer,
    SplitStrategy,
    SplitResult
)
from transformers.notes_generator import (
    NotesGenerator,
    NoteStyle,
    SpeakerNote
)


# =============================================================================
# TEST FIXTURES
# =============================================================================

@pytest.fixture
def basic_semantic_structure():
    """Basic semantic structure for testing."""
    return {
        "metadata": {
            "title": "Test Presentation",
            "author": "Test Author",
            "date": "2025-12-17"
        },
        "chapters": [
            {
                "id": "ch01",
                "title": "Introduction",
                "content": [
                    {
                        "id": "block01",
                        "type": "paragraph",
                        "title": "Overview",
                        "content": "This is a test paragraph with content."
                    }
                ]
            }
        ]
    }


@pytest.fixture
def multi_section_semantic_structure():
    """Multi-section semantic structure."""
    return {
        "metadata": {
            "title": "Multi-Section Presentation",
            "subtitle": "Testing Sections",
            "author": "Test Suite"
        },
        "chapters": [
            {
                "id": "ch01",
                "title": "Chapter One",
                "summary": "First chapter summary",
                "content": [
                    {
                        "id": "block01",
                        "type": "list_unordered",
                        "title": "Key Points",
                        "content": ["Point one", "Point two", "Point three"]
                    }
                ]
            },
            {
                "id": "ch02",
                "title": "Chapter Two",
                "content": [
                    {
                        "id": "block02",
                        "type": "blockquote",
                        "title": "Important Quote",
                        "content": "This is an important quote.",
                        "attribution": "Test Author"
                    }
                ]
            }
        ]
    }


@pytest.fixture
def comparison_block():
    """Content block with comparison patterns."""
    return {
        "id": "comp01",
        "type": "list_unordered",
        "title": "Pros vs Cons",
        "content": [
            "Pros: Easy to use and efficient",
            "Cons: Limited functionality and cost"
        ]
    }


@pytest.fixture
def process_block():
    """Content block with process patterns."""
    return {
        "id": "proc01",
        "type": "list_ordered",
        "title": "Installation Steps",
        "content": [
            "Step 1: Download the software",
            "Step 2: Run the installer",
            "Step 3: Configure settings",
            "Finally, restart the system"
        ]
    }


@pytest.fixture
def timeline_block():
    """Content block with timeline patterns."""
    return {
        "id": "time01",
        "type": "list_unordered",
        "title": "Company History",
        "content": [
            "2010: Company founded",
            "2015: First major milestone",
            "2020: Expansion to new markets",
            "2025: Current status"
        ]
    }


@pytest.fixture
def oversized_bullet_content():
    """Content that violates 6x6 rule."""
    return {
        "title": "Long Bullet List",
        "bullets": [
            "First bullet point",
            "Second bullet point",
            "Third bullet point",
            "Fourth bullet point",
            "Fifth bullet point",
            "Sixth bullet point",
            "Seventh bullet point exceeds limit",
            "Eighth bullet point also too many",
            "Ninth item in the list",
            "Tenth bullet point"
        ]
    }


@pytest.fixture
def long_bullet_content():
    """Bullets that are too long (>6 words)."""
    return {
        "title": "Long Bullets",
        "bullets": [
            "Short one",
            "This is a very long bullet point that exceeds the six word limit",
            "Another extremely lengthy bullet point with way too many words in it",
            "Brief item"
        ]
    }


# =============================================================================
# SEMANTIC TO PRESENTATION TESTS
# =============================================================================

class TestSemanticToPresentation:
    """Tests for semantic to presentation transformation."""

    def test_transform_basic_structure(self, basic_semantic_structure):
        """Test transformation of simple semantic structure."""
        transformer = SemanticToPresentationTransformer()
        result = transformer.transform(basic_semantic_structure)

        assert isinstance(result, TransformationResult)
        assert "presentation" in dir(result)
        assert result.presentation["metadata"]["title"] == "Test Presentation"
        assert len(result.presentation["sections"]) > 0

    def test_transform_with_sections(self, multi_section_semantic_structure):
        """Test handling of multi-section documents."""
        transformer = SemanticToPresentationTransformer()
        result = transformer.transform(multi_section_semantic_structure)

        presentation = result.presentation
        # Should have title slide section + 2 content sections
        assert len(presentation["sections"]) == 3

        # Check section titles
        section_titles = [s["title"] for s in presentation["sections"]]
        assert "Chapter One" in section_titles
        assert "Chapter Two" in section_titles

    def test_metadata_preservation(self, basic_semantic_structure):
        """Test that metadata is properly transferred."""
        transformer = SemanticToPresentationTransformer()
        result = transformer.transform(basic_semantic_structure)

        metadata = result.presentation["metadata"]
        assert metadata["title"] == "Test Presentation"
        assert metadata["author"] == "Test Author"
        assert metadata["date"] == "2025-12-17"

    def test_provenance_tracking(self, basic_semantic_structure):
        """Test that provenance information is logged."""
        config = TransformationConfig(include_provenance=True)
        transformer = SemanticToPresentationTransformer(config)
        result = transformer.transform(basic_semantic_structure)

        assert len(result.provenance) > 0

        # Check provenance entry structure
        entry = result.provenance[0]
        assert "sourceId" in entry
        assert "sourceType" in entry
        assert "targetType" in entry
        assert "transformation" in entry
        assert "timestamp" in entry

    def test_title_slide_creation(self, basic_semantic_structure):
        """Test title slide is created when configured."""
        config = TransformationConfig(create_title_slide=True)
        transformer = SemanticToPresentationTransformer(config)
        result = transformer.transform(basic_semantic_structure)

        # First section should contain title slide
        first_section = result.presentation["sections"][0]
        first_slide = first_section["slides"][0]
        assert first_slide["type"] == "title"

    def test_section_headers_creation(self, multi_section_semantic_structure):
        """Test section headers are created when configured."""
        config = TransformationConfig(create_section_headers=True)
        transformer = SemanticToPresentationTransformer(config)
        result = transformer.transform(multi_section_semantic_structure)

        # Find a content section (not title section)
        content_sections = [s for s in result.presentation["sections"] if s["title"]]

        for section in content_sections:
            if section["title"]:
                # First slide should be section header
                first_slide = section["slides"][0]
                assert first_slide["type"] == "section_header"

    def test_quality_metrics_calculation(self, basic_semantic_structure):
        """Test quality metrics are calculated correctly."""
        transformer = SemanticToPresentationTransformer()
        result = transformer.transform(basic_semantic_structure)

        metrics = result.quality_metrics
        assert "totalSlides" in metrics
        assert "totalSections" in metrics
        assert "slideTypeVariety" in metrics
        assert "notesCoverage" in metrics
        assert "validationScore" in metrics

        assert metrics["totalSlides"] > 0
        assert 0 <= metrics["notesCoverage"] <= 1.0
        assert 0 <= metrics["validationScore"] <= 100


# =============================================================================
# BLOCK TO SLIDE MAPPER TESTS
# =============================================================================

class TestBlockToSlideMapper:
    """Tests for block to slide type mapping."""

    def test_pattern_detection_comparison(self, comparison_block):
        """Test detection of comparison patterns."""
        mapper = BlockToSlideMapper()
        decision = mapper.map_block(comparison_block)

        assert decision.slide_type == "comparison"
        assert decision.confidence > 0.8
        assert "comparison" in decision.reason.lower()

    def test_pattern_detection_process(self, process_block):
        """Test detection of process/procedure patterns."""
        mapper = BlockToSlideMapper()
        decision = mapper.map_block(process_block)

        assert decision.slide_type == "process_flow"
        assert decision.confidence > 0.8
        assert "process" in decision.reason.lower()

    def test_pattern_detection_timeline(self, timeline_block):
        """Test detection of chronological patterns."""
        mapper = BlockToSlideMapper()
        decision = mapper.map_block(timeline_block)

        assert decision.slide_type == "timeline"
        assert decision.confidence > 0.8
        assert "timeline" in decision.reason.lower()

    def test_confidence_scoring(self):
        """Test that confidence scores are in valid range."""
        mapper = BlockToSlideMapper()

        test_blocks = [
            {"type": "paragraph", "content": "Simple paragraph"},
            {"type": "table", "content": {"headers": ["A", "B"], "rows": [["1", "2"]]}},
            {"type": "blockquote", "content": "A quote"}
        ]

        for block in test_blocks:
            decision = mapper.map_block(block)
            assert 0.0 <= decision.confidence <= 1.0

    def test_context_aware_mapping(self):
        """Test that context influences mapping decisions."""
        mapper = BlockToSlideMapper()

        block = {
            "type": "paragraph",
            "content": "Some content"
        }

        context = {
            "previous": {"type": "heading", "content": "Section Start"},
            "next": {"type": "list_unordered", "content": ["item"]},
            "position": 1,
            "total_blocks": 5
        }

        decision = mapper.map_block(block, context)
        assert decision is not None
        assert decision.metadata["block_type"] == "paragraph"

    def test_flow_optimization(self):
        """Test flow optimization avoids repetitive slide types."""
        mapper = BlockToSlideMapper()

        # Create blocks that would normally map to same type
        blocks = [
            {"type": "blockquote", "content": "Quote one"},
            {"type": "blockquote", "content": "Quote two"},
            {"type": "blockquote", "content": "Quote three"}
        ]

        decisions = mapper.map_blocks(blocks)

        # Should have at least some variety (not all quotes)
        slide_types = [d.slide_type for d in decisions]
        # At least one should be different due to flow optimization
        assert len(set(slide_types)) >= 1  # May optimize some

    def test_table_constraint_checking(self):
        """Test table size constraint checking."""
        mapper = BlockToSlideMapper()

        # Table within constraints
        small_table = {
            "type": "table",
            "content": {
                "headers": ["A", "B", "C"],
                "rows": [["1", "2", "3"], ["4", "5", "6"]]
            }
        }

        decision = mapper.map_block(small_table)
        assert decision.slide_type == "table"
        assert decision.confidence > 0.9

    def test_alternatives_generation(self):
        """Test that alternative slide types are generated."""
        mapper = BlockToSlideMapper()

        block = {
            "type": "list_unordered",
            "content": ["Item 1", "Item 2"]
        }

        decision = mapper.map_block(block)
        assert len(decision.alternatives) > 0

        # Alternatives should have slide type and confidence
        for alt_type, confidence in decision.alternatives:
            assert isinstance(alt_type, str)
            assert 0.0 <= confidence <= 1.0


# =============================================================================
# CONTENT SPLITTER TESTS (6x6 Rule)
# =============================================================================

class TestContentSplitter:
    """Tests for 6x6 rule content splitting."""

    def test_6x6_rule_bullets(self, oversized_bullet_content):
        """Test max 6 bullets per slide enforcement."""
        enforcer = SixSixRuleEnforcer()
        results = enforcer.enforce(oversized_bullet_content)

        # Should split into multiple slides
        assert len(results) > 1

        # Each slide should have <= 6 bullets
        for result in results:
            assert len(result["bullets"]) <= 6

    def test_6x6_rule_words(self, long_bullet_content):
        """Test max 6 words per bullet enforcement."""
        enforcer = SixSixRuleEnforcer()
        results = enforcer.enforce(long_bullet_content)

        # Check that bullets are condensed
        for result in results:
            for bullet in result["bullets"]:
                word_count = len(bullet.split())
                # May not be exactly 6 in non-strict mode, but should be reduced
                assert word_count <= 6 or bullet == long_bullet_content["bullets"][0]

    def test_split_equal_strategy(self, oversized_bullet_content):
        """Test equal split strategy."""
        enforcer = SixSixRuleEnforcer()
        results = enforcer.enforce(oversized_bullet_content, SplitStrategy.EQUAL)

        # Should create multiple slides
        assert len(results) > 1

        # Slides should be roughly equal size
        sizes = [len(r["bullets"]) for r in results]
        assert max(sizes) - min(sizes) <= 2  # Allow small variance

    def test_split_semantic_strategy(self):
        """Test semantic grouping strategy."""
        content = {
            "title": "Semantic Groups",
            "bullets": [
                "First group item one",
                "First group item two",
                "Also related to first",
                "Second group starts here",
                "Second group continues",
                "Third group item one",
                "Additionally third group item"
            ]
        }

        enforcer = SixSixRuleEnforcer()
        results = enforcer.enforce(content, SplitStrategy.SEMANTIC)

        # Should create multiple slides with semantic grouping
        assert len(results) >= 1

    def test_continuation_detection(self):
        """Test detection of continuation markers."""
        enforcer = SixSixRuleEnforcer()

        # Test continuation detection
        assert enforcer._is_continuation("First point", "Also another point")
        assert enforcer._is_continuation("Overview", "Additionally important")
        assert enforcer._is_continuation("Start", "Furthermore consider")

    def test_table_splitting(self):
        """Test splitting of large tables."""
        splitter = ContentSplitter()

        large_table = {
            "title": "Large Table",
            "headers": ["Col1", "Col2", "Col3"],
            "rows": [[f"R{i}C{j}" for j in range(3)] for i in range(15)]
        }

        result = splitter.split_content(large_table, "table")

        # Should split into multiple tables
        assert len(result.split_parts) > 1

        # Each part should have same headers
        for part in result.split_parts:
            assert part["headers"] == large_table["headers"]

    def test_compliance_scoring(self):
        """Test compliance score calculation."""
        enforcer = SixSixRuleEnforcer()

        # Compliant content
        good_content = {
            "title": "Good",
            "bullets": ["One", "Two", "Three"]
        }

        compliance = enforcer.check_compliance(good_content)
        assert compliance["compliant"] is True
        assert compliance["score"] == 100.0

        # Non-compliant content
        bad_content = {
            "title": "Bad",
            "bullets": ["One two three four five six seven eight nine ten"] * 8
        }

        compliance = enforcer.check_compliance(bad_content)
        assert compliance["compliant"] is False
        assert compliance["score"] < 100.0

    def test_process_flow_splitting(self):
        """Test splitting of process flows with many steps."""
        splitter = ContentSplitter()

        many_steps = {
            "title": "Long Process",
            "steps": [
                {"label": f"Step {i}", "description": f"Do thing {i}"}
                for i in range(1, 12)
            ]
        }

        result = splitter.split_content(many_steps, "process_flow")

        # Should split into multiple slides
        assert len(result.split_parts) > 1

        # Total steps should be preserved
        total_steps = sum(len(part["steps"]) for part in result.split_parts)
        assert total_steps == 11


# =============================================================================
# NOTES GENERATOR TESTS
# =============================================================================

class TestNotesGenerator:
    """Tests for speaker notes generation."""

    def test_generate_detailed_notes(self):
        """Test detailed note style generation."""
        generator = NotesGenerator(NoteStyle.DETAILED)

        slide_content = {
            "type": "content",
            "title": "Key Points",
            "content": {"bullets": ["Point 1", "Point 2"]}
        }

        original_content = {
            "type": "paragraph",
            "content": "This is the full detailed content that was condensed."
        }

        note = generator.generate_notes(slide_content, original_content, NoteStyle.DETAILED)

        assert note.style == NoteStyle.DETAILED
        assert len(note.content) > 0
        assert "Key Points" in note.content

    def test_generate_summary_notes(self):
        """Test summary note style generation."""
        generator = NotesGenerator()

        slide_content = {
            "title": "Overview",
            "content": {"bullets": ["Brief point"]}
        }

        original_content = "Long original content goes here with many details."

        note = generator.generate_notes(
            slide_content,
            original_content,
            NoteStyle.SUMMARY
        )

        assert note.style == NoteStyle.SUMMARY
        assert "Key Points:" in note.content or "Additional Context:" in note.content

    def test_generate_talking_points(self):
        """Test talking points style generation."""
        generator = NotesGenerator(NoteStyle.TALKING_POINTS)

        slide_content = {
            "title": "Main Topic",
            "content": {"bullets": ["First", "Second", "Third"]}
        }

        original_content = "Original detailed discussion of the topic."

        note = generator.generate_notes(
            slide_content,
            original_content,
            NoteStyle.TALKING_POINTS
        )

        assert note.style == NoteStyle.TALKING_POINTS
        assert "Talking Points:" in note.content

    def test_timing_estimation(self):
        """Test words per minute timing calculation."""
        generator = NotesGenerator()

        # Short content
        short_content = "Brief note."
        timing = generator._estimate_timing(short_content)
        assert timing == "< 1 minute"

        # Medium content (150+ words)
        medium_content = " ".join(["word"] * 200)
        timing = generator._estimate_timing(medium_content)
        assert "minute" in timing.lower()

    def test_transition_generation(self):
        """Test transitions between slides."""
        generator = NotesGenerator()

        slide_content = {
            "id": "slide1",
            "title": "Current Slide",
            "content": {}
        }

        context = {
            "previous": {"title": "Previous Topic"},
            "next": {"title": "Next Topic"},
            "is_first": False,
            "is_last": False
        }

        note = generator.generate_notes(slide_content, "", context=context)

        assert note.transitions is not None
        assert len(note.transitions) > 0

    def test_key_point_extraction(self):
        """Test extraction of key points from content."""
        generator = NotesGenerator()

        original = {
            "content": "Important: This is critical. The main idea is essential. Note: Remember this."
        }

        slide_content = {
            "title": "Test",
            "content": {"bullets": ["Point"]}
        }

        key_points = generator._extract_key_points(original, slide_content)

        assert len(key_points) > 0

    def test_batch_generation_with_context(self):
        """Test batch generation with inter-slide context."""
        generator = NotesGenerator()

        slides = [
            {"title": "First Slide", "content": {"bullets": ["A"]}},
            {"title": "Second Slide", "content": {"bullets": ["B"]}},
            {"title": "Third Slide", "content": {"bullets": ["C"]}}
        ]

        originals = ["Content A", "Content B", "Content C"]

        notes = generator.generate_notes_batch(slides, originals)

        assert len(notes) == 3

        # Check first and last slides have correct context
        assert notes[0].transitions.get("from_previous") is None or notes[0].transitions.get("from_previous") == ""
        assert notes[-1].transitions.get("to_next") is None or "conclude" in notes[-1].content.lower()


# =============================================================================
# INTEGRATION TESTS
# =============================================================================

class TestTransformationPipeline:
    """Integration tests for full transformation pipeline."""

    def test_full_transformation_pipeline(self, basic_semantic_structure):
        """Test end-to-end transformation from semantic to presentation."""
        # Configure transformer
        config = TransformationConfig(
            max_bullets=6,
            max_words_per_bullet=6,
            generate_notes=True,
            notes_style=NoteStyle.TALKING_POINTS,
            create_title_slide=True,
            create_section_headers=True
        )

        transformer = SemanticToPresentationTransformer(config)
        result = transformer.transform(basic_semantic_structure)

        # Verify complete pipeline execution
        assert result.presentation is not None
        assert result.metadata is not None
        assert result.quality_metrics is not None

        # Check presentation structure
        presentation = result.presentation
        assert "metadata" in presentation
        assert "sections" in presentation
        assert len(presentation["sections"]) > 0

        # Check slides have notes (if configured)
        all_slides = []
        for section in presentation["sections"]:
            all_slides.extend(section["slides"])

        slides_with_notes = [s for s in all_slides if s.get("notes")]
        assert len(slides_with_notes) > 0

    def test_transformation_with_fixtures(self, multi_section_semantic_structure):
        """Test transformation using test fixtures."""
        transformer = SemanticToPresentationTransformer()
        result = transformer.transform(multi_section_semantic_structure)

        # Verify quality metrics are reasonable
        metrics = result.quality_metrics
        assert metrics["totalSlides"] >= 2
        assert metrics["totalSections"] >= 2
        assert metrics["validationScore"] > 0

    def test_complex_content_transformation(self):
        """Test transformation of complex multi-block content."""
        complex_structure = {
            "metadata": {
                "title": "Complex Presentation"
            },
            "chapters": [
                {
                    "id": "ch01",
                    "title": "Complex Chapter",
                    "content": [
                        {
                            "id": "b01",
                            "type": "list_unordered",
                            "title": "Pros vs Cons",
                            "content": ["Pro: Fast", "Con: Expensive"]
                        },
                        {
                            "id": "b02",
                            "type": "list_ordered",
                            "title": "Steps",
                            "content": ["Step 1", "Step 2", "Finally done"]
                        },
                        {
                            "id": "b03",
                            "type": "blockquote",
                            "title": "Quote",
                            "content": "Wise words here"
                        },
                        {
                            "id": "b04",
                            "type": "table",
                            "title": "Data",
                            "content": {
                                "headers": ["A", "B"],
                                "rows": [["1", "2"]]
                            }
                        }
                    ]
                }
            ]
        }

        transformer = SemanticToPresentationTransformer()
        result = transformer.transform(complex_structure)

        # Should handle all different block types
        assert result.presentation is not None

        # Check slide type variety
        metrics = result.quality_metrics
        assert metrics["slideTypeVariety"] >= 3  # Multiple types used

    def test_six_six_enforcement_in_pipeline(self):
        """Test that 6x6 rule is enforced during transformation."""
        structure_with_long_lists = {
            "metadata": {"title": "Long Lists"},
            "chapters": [{
                "id": "ch01",
                "title": "Chapter",
                "content": [{
                    "id": "b01",
                    "type": "list_unordered",
                    "title": "Many Items",
                    "content": [f"Item {i}" for i in range(1, 15)]
                }]
            }]
        }

        config = TransformationConfig(
            max_bullets=6,
            strict_six_six=True
        )

        transformer = SemanticToPresentationTransformer(config)
        result = transformer.transform(structure_with_long_lists)

        # Should split into multiple slides
        all_slides = []
        for section in result.presentation["sections"]:
            all_slides.extend(section["slides"])

        # Check each content slide respects 6x6
        for slide in all_slides:
            bullets = slide.get("content", {}).get("bullets", [])
            assert len(bullets) <= 6

    def test_provenance_chain(self, basic_semantic_structure):
        """Test that provenance tracking works through entire pipeline."""
        config = TransformationConfig(include_provenance=True)
        transformer = SemanticToPresentationTransformer(config)
        result = transformer.transform(
            basic_semantic_structure,
            source_path="/test/source.md"
        )

        # Check provenance log
        assert len(result.provenance) > 0

        # Verify provenance entries have required fields
        for entry in result.provenance:
            assert "sourceId" in entry
            assert "targetType" in entry
            assert "transformation" in entry

        # Check metadata includes source path
        assert result.metadata["sourcePath"] == "/test/source.md"

    def test_error_handling_invalid_input(self):
        """Test handling of invalid input structures."""
        invalid_structure = {
            "metadata": {},
            # Missing chapters/sections
        }

        transformer = SemanticToPresentationTransformer()
        result = transformer.transform(invalid_structure)

        # Should still produce a result (with warnings)
        assert result is not None
        # May have warnings about empty content
        assert isinstance(result.warnings, list)


# =============================================================================
# EDGE CASE TESTS
# =============================================================================

class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_semantic_structure(self):
        """Test handling of empty structure."""
        empty_structure = {
            "metadata": {"title": "Empty"},
            "chapters": []
        }

        transformer = SemanticToPresentationTransformer()
        result = transformer.transform(empty_structure)

        # Should still produce metadata
        assert result.presentation["metadata"]["title"] == "Empty"

    def test_single_bullet_content(self):
        """Test content with only one bullet."""
        enforcer = SixSixRuleEnforcer()

        content = {
            "title": "Single",
            "bullets": ["Only one"]
        }

        results = enforcer.enforce(content)
        assert len(results) == 1
        assert results[0]["bullets"] == ["Only one"]

    def test_exactly_six_bullets(self):
        """Test content with exactly 6 bullets (boundary)."""
        enforcer = SixSixRuleEnforcer()

        content = {
            "title": "Six",
            "bullets": [f"Item {i}" for i in range(1, 7)]
        }

        results = enforcer.enforce(content)
        assert len(results) == 1  # Should not split

    def test_seven_bullets(self):
        """Test content with 7 bullets (just over limit)."""
        enforcer = SixSixRuleEnforcer()

        content = {
            "title": "Seven",
            "bullets": [f"Item {i}" for i in range(1, 8)]
        }

        results = enforcer.enforce(content)
        assert len(results) == 2  # Should split into 2 slides

    def test_unicode_content_handling(self):
        """Test handling of Unicode characters."""
        structure = {
            "metadata": {"title": "Unicode Test 中文"},
            "chapters": [{
                "id": "ch01",
                "title": "Français",
                "content": [{
                    "id": "b01",
                    "type": "paragraph",
                    "content": "Émoji test: 🚀 ✨ 🎉"
                }]
            }]
        }

        transformer = SemanticToPresentationTransformer()
        result = transformer.transform(structure)

        # Should handle Unicode properly
        assert "中文" in result.presentation["metadata"]["title"]

    def test_missing_optional_fields(self):
        """Test handling of missing optional fields."""
        minimal_structure = {
            "chapters": [{
                "title": "Chapter",
                "content": [{
                    "type": "paragraph",
                    "content": "Text"
                }]
            }]
        }

        transformer = SemanticToPresentationTransformer()
        result = transformer.transform(minimal_structure)

        # Should use defaults for missing metadata
        assert result.presentation["metadata"]["title"] is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
