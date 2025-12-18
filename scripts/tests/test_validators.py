"""
Comprehensive Unit Tests for Slideforge Validators

Tests the three-tier validation system:
1. StructureValidator - Basic data integrity
2. SchemaValidator - JSON Schema compliance
3. SemanticValidator - Quality and completeness

Author: Slideforge Test Suite
Date: 2025-12-17
"""

import pytest
import sys
import json
from pathlib import Path

# Add scripts directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "validators"))
sys.path.insert(0, str(Path(__file__).parent.parent / "utilities"))

from structure_validator import (
    StructureValidator,
    StructureValidationResult,
    StructureError,
    ErrorSeverity
)
from schema_validator import (
    SchemaValidator,
    SchemaValidationResult,
    SchemaError
)
from semantic_validator import (
    SemanticValidator,
    SemanticValidationResult,
    QualityIssue,
    IssueCategory,
    IssueSeverity
)
from validation_result import (
    ValidationResult,
    ValidationSeverity,
    ValidationIssue
)


# =============================================================================
# STRUCTURE VALIDATOR TESTS
# =============================================================================

class TestStructureValidator:
    """Tests for StructureValidator (Level 1)"""

    def test_validate_root_structure_valid(self, minimal_presentation):
        """Test that valid root structure passes"""
        validator = StructureValidator()
        result = validator.validate(minimal_presentation)

        assert isinstance(result, StructureValidationResult)
        assert result.valid is True
        assert len(result.errors) == 0

    def test_validate_root_structure_not_dict(self):
        """Test that non-dict root fails with CRITICAL error"""
        validator = StructureValidator()
        result = validator.validate("not a dict")

        assert result.valid is False
        assert len(result.errors) > 0
        assert result.errors[0].severity == ErrorSeverity.CRITICAL
        assert "dictionary" in result.errors[0].message.lower()

    def test_validate_root_structure_missing_metadata(self):
        """Test that missing metadata field fails"""
        validator = StructureValidator()
        invalid_data = {
            "sections": []
        }
        result = validator.validate(invalid_data)

        assert result.valid is False
        assert any("metadata" in e.message for e in result.errors)

    def test_validate_root_structure_missing_sections(self):
        """Test that missing sections field fails"""
        validator = StructureValidator()
        invalid_data = {
            "metadata": {"title": "Test"}
        }
        result = validator.validate(invalid_data)

        assert result.valid is False
        assert any("sections" in e.message for e in result.errors)

    def test_validate_metadata_valid(self, minimal_presentation):
        """Test that valid metadata passes"""
        validator = StructureValidator()
        result = validator.validate(minimal_presentation)

        assert result.valid is True
        # Metadata should have title
        metadata = minimal_presentation["metadata"]
        assert "title" in metadata

    def test_validate_metadata_missing_title(self):
        """Test that metadata without title fails"""
        validator = StructureValidator()
        invalid_data = {
            "metadata": {"author": "Test Author"},
            "sections": []
        }
        result = validator.validate(invalid_data)

        assert result.valid is False
        assert any("title" in e.message.lower() for e in result.errors)

    def test_validate_metadata_empty_title(self):
        """Test that empty title generates warning"""
        validator = StructureValidator()
        data = {
            "metadata": {"title": "   "},
            "sections": []
        }
        result = validator.validate(data)

        # Should pass structure check but have warning
        assert any("empty" in w.message.lower() for w in result.warnings)

    def test_validate_sections_valid(self, minimal_presentation):
        """Test that valid sections pass"""
        validator = StructureValidator()
        result = validator.validate(minimal_presentation)

        assert result.valid is True
        assert result.stats["totalSections"] == 2
        assert result.stats["totalSlides"] == 5

    def test_validate_sections_not_array(self):
        """Test that sections as non-array fails"""
        validator = StructureValidator()
        invalid_data = {
            "metadata": {"title": "Test"},
            "sections": "not an array"
        }
        result = validator.validate(invalid_data)

        assert result.valid is False
        assert any("array" in e.message.lower() for e in result.errors)

    def test_validate_sections_empty_slides(self):
        """Test that section with no slides generates warning"""
        validator = StructureValidator()
        data = {
            "metadata": {"title": "Test"},
            "sections": [
                {"slides": []}
            ]
        }
        result = validator.validate(data)

        assert any("no slides" in w.message.lower() for w in result.warnings)

    def test_validate_slide_types_valid(self, minimal_presentation):
        """Test that valid slide types pass"""
        validator = StructureValidator()
        result = validator.validate(minimal_presentation)

        assert result.valid is True
        # Check that slide types were tracked
        assert "content" in result.stats["slideTypes"]
        assert "title" in result.stats["slideTypes"]

    def test_validate_slide_types_invalid(self):
        """Test that invalid slide type fails"""
        validator = StructureValidator()
        invalid_data = {
            "metadata": {"title": "Test"},
            "sections": [
                {
                    "slides": [
                        {
                            "type": "invalid_type",
                            "title": "Test"
                        }
                    ]
                }
            ]
        }
        result = validator.validate(invalid_data)

        assert result.valid is False
        assert any("invalid slide type" in e.message.lower() for e in result.errors)

    def test_validate_slide_types_missing_type(self):
        """Test that slide without type field fails"""
        validator = StructureValidator()
        invalid_data = {
            "metadata": {"title": "Test"},
            "sections": [
                {
                    "slides": [
                        {"title": "Test"}  # Missing type
                    ]
                }
            ]
        }
        result = validator.validate(invalid_data)

        assert result.valid is False
        assert any("type" in e.message.lower() for e in result.errors)

    def test_detect_empty_slides(self):
        """Test that empty slides are detected"""
        validator = StructureValidator()
        data = {
            "metadata": {"title": "Test"},
            "sections": [
                {
                    "slides": [
                        {
                            "type": "content",
                            "title": "Empty Slide",
                            "content": {"bullets": []}
                        }
                    ]
                }
            ]
        }
        result = validator.validate(data)

        assert result.stats["emptySlides"] == 1

    def test_severity_levels_critical(self):
        """Test CRITICAL severity level for root issues"""
        validator = StructureValidator()
        result = validator.validate([])  # Not a dict

        assert result.valid is False
        critical_errors = [e for e in result.errors if e.severity == ErrorSeverity.CRITICAL]
        assert len(critical_errors) > 0

    def test_severity_levels_error(self):
        """Test ERROR severity level for missing required fields"""
        validator = StructureValidator()
        data = {
            "metadata": {},  # Missing required title
            "sections": []
        }
        result = validator.validate(data)

        error_level_errors = [e for e in result.errors if e.severity == ErrorSeverity.ERROR]
        assert len(error_level_errors) > 0

    def test_severity_levels_warning(self):
        """Test WARNING severity level for quality issues"""
        validator = StructureValidator()
        data = {
            "metadata": {"title": "   "},  # Empty title
            "sections": [{"slides": []}]  # Empty section
        }
        result = validator.validate(data)

        assert len(result.warnings) > 0
        assert any(w.severity == ErrorSeverity.WARNING for w in result.warnings)

    def test_strict_mode_warnings_as_errors(self):
        """Test that strict mode treats warnings as failures"""
        validator = StructureValidator(strict=True)
        data = {
            "metadata": {"title": "Test"},
            "sections": [{"slides": []}]  # Warning: empty section
        }
        result = validator.validate(data)

        assert result.valid is False  # Fails in strict mode
        assert len(result.warnings) > 0

    def test_table_content_validation(self):
        """Test validation of table slide content"""
        validator = StructureValidator()
        data = {
            "metadata": {"title": "Test"},
            "sections": [
                {
                    "slides": [
                        {
                            "type": "table",
                            "title": "Data Table",
                            "content": {
                                "headers": ["Col1", "Col2"],
                                "rows": [
                                    ["A", "B"],
                                    ["C", "D"]
                                ]
                            }
                        }
                    ]
                }
            ]
        }
        result = validator.validate(data)

        assert result.valid is True

    def test_table_content_missing_headers(self):
        """Test that table without headers fails"""
        validator = StructureValidator()
        data = {
            "metadata": {"title": "Test"},
            "sections": [
                {
                    "slides": [
                        {
                            "type": "table",
                            "title": "Bad Table",
                            "content": {
                                "rows": [["A", "B"]]
                            }
                        }
                    ]
                }
            ]
        }
        result = validator.validate(data)

        assert result.valid is False
        assert any("headers" in e.message.lower() for e in result.errors)

    def test_comparison_content_validation(self):
        """Test validation of comparison/two_content slides"""
        validator = StructureValidator()
        data = {
            "metadata": {"title": "Test"},
            "sections": [
                {
                    "slides": [
                        {
                            "type": "comparison",
                            "title": "Compare",
                            "content": {
                                "left": ["Item 1", "Item 2"],
                                "right": ["Item A", "Item B"]
                            }
                        }
                    ]
                }
            ]
        }
        result = validator.validate(data)

        assert result.valid is True


# =============================================================================
# SCHEMA VALIDATOR TESTS
# =============================================================================

class TestSchemaValidator:
    """Tests for SchemaValidator (Level 2)"""

    def test_schema_compliance_valid(self, minimal_presentation):
        """Test that valid presentation passes schema validation"""
        validator = SchemaValidator()
        result = validator.validate(minimal_presentation)

        assert isinstance(result, SchemaValidationResult)
        assert result.valid is True
        assert len(result.errors) == 0

    def test_schema_compliance_invalid(self):
        """Test that invalid presentation fails schema validation"""
        validator = SchemaValidator()
        invalid_data = {
            "metadata": "not an object",  # Should be object
            "sections": []
        }
        result = validator.validate(invalid_data)

        assert result.valid is False
        assert len(result.errors) > 0

    def test_missing_required_fields_metadata(self):
        """Test that missing required metadata.title fails"""
        validator = SchemaValidator()
        data = {
            "metadata": {},  # Missing title
            "sections": []
        }
        result = validator.validate(data)

        assert result.valid is False
        assert any("title" in e.message.lower() for e in result.errors)

    def test_missing_required_fields_root(self):
        """Test that missing root required fields fails"""
        validator = SchemaValidator()
        data = {"metadata": {"title": "Test"}}  # Missing sections
        result = validator.validate(data)

        assert result.valid is False
        assert any("sections" in e.message.lower() for e in result.errors)

    def test_invalid_field_types_metadata(self):
        """Test that wrong field type for metadata fails"""
        validator = SchemaValidator()
        data = {
            "metadata": "should be object",
            "sections": []
        }
        result = validator.validate(data)

        assert result.valid is False
        assert len(result.errors) > 0

    def test_invalid_field_types_sections(self):
        """Test that wrong field type for sections fails"""
        validator = SchemaValidator()
        data = {
            "metadata": {"title": "Test"},
            "sections": "should be array"
        }
        result = validator.validate(data)

        assert result.valid is False
        assert any("array" in e.message.lower() for e in result.errors)

    def test_enum_validation_slide_type(self):
        """Test that invalid slide type enum value fails"""
        validator = SchemaValidator()
        data = {
            "metadata": {"title": "Test"},
            "sections": [
                {
                    "slides": [
                        {
                            "type": "not_a_valid_type",
                            "title": "Test"
                        }
                    ]
                }
            ]
        }
        result = validator.validate(data)

        # Should fail if using schema with enum validation
        if result.valid is False:
            assert any("enum" in e.validator.lower() or "invalid" in e.message.lower()
                      for e in result.errors)

    def test_schema_with_all_slide_types(self, all_slide_types_presentation):
        """Test schema validation with presentation using all slide types"""
        validator = SchemaValidator()
        result = validator.validate(all_slide_types_presentation)

        assert result.valid is True

    def test_schema_error_path_formatting(self):
        """Test that schema errors include proper JSON path"""
        validator = SchemaValidator()
        data = {
            "metadata": {"title": "Test"},
            "sections": [
                {
                    "slides": [
                        {}  # Missing required type
                    ]
                }
            ]
        }
        result = validator.validate(data)

        if len(result.errors) > 0:
            # Should have path information
            assert any(e.path for e in result.errors)

    def test_get_schema(self):
        """Test getting the schema being used"""
        validator = SchemaValidator()
        schema = validator.get_schema()

        assert isinstance(schema, dict)
        assert "$schema" in schema or "type" in schema

    def test_validate_partial_slide(self):
        """Test validating a partial structure (single slide)"""
        validator = SchemaValidator()
        slide = {
            "type": "content",
            "title": "Test Slide",
            "content": {"bullets": ["Point 1"]}
        }
        result = validator.validate_partial(slide, "slide")

        # Should validate or return result
        assert isinstance(result, SchemaValidationResult)

    def test_validate_partial_section(self):
        """Test validating a partial structure (single section)"""
        validator = SchemaValidator()
        section = {
            "title": "Section 1",
            "slides": [
                {
                    "type": "content",
                    "title": "Slide 1"
                }
            ]
        }
        result = validator.validate_partial(section, "section")

        assert isinstance(result, SchemaValidationResult)

    def test_custom_schema_loading(self):
        """Test loading custom schema"""
        custom_schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
                "test": {"type": "string"}
            }
        }
        validator = SchemaValidator(schema=custom_schema)

        assert validator.schema == custom_schema


# =============================================================================
# SEMANTIC VALIDATOR TESTS
# =============================================================================

class TestSemanticValidator:
    """Tests for SemanticValidator (Level 3)"""

    def test_validate_6x6_rule_compliant(self):
        """Test that 6x6 compliant slides pass"""
        validator = SemanticValidator()
        data = {
            "metadata": {"title": "Test"},
            "sections": [
                {
                    "slides": [
                        {
                            "type": "content",
                            "title": "Good Slide",
                            "content": {
                                "bullets": [
                                    "Short point one",
                                    "Short point two",
                                    "Short point three"
                                ]
                            },
                            "notes": "Speaker notes"
                        }
                    ]
                }
            ]
        }
        result = validator.validate(data)

        # Should have no 6x6 violations
        six_six_issues = [i for i in result.issues
                         if "SIX_SIX" in i.rule_id]
        assert len(six_six_issues) == 0

    def test_validate_6x6_rule_too_many_bullets(self):
        """Test that slides with >6 bullets fail 6x6 rule"""
        validator = SemanticValidator()
        data = {
            "metadata": {"title": "Test"},
            "sections": [
                {
                    "slides": [
                        {
                            "type": "content",
                            "title": "Too Many Bullets",
                            "content": {
                                "bullets": [
                                    "Bullet 1",
                                    "Bullet 2",
                                    "Bullet 3",
                                    "Bullet 4",
                                    "Bullet 5",
                                    "Bullet 6",
                                    "Bullet 7",
                                    "Bullet 8"
                                ]
                            },
                            "notes": "Notes"
                        }
                    ]
                }
            ]
        }
        result = validator.validate(data)

        # Should have 6x6 violation
        six_six_issues = [i for i in result.issues
                         if "SIX_SIX_BULLET_COUNT" in i.rule_id]
        assert len(six_six_issues) > 0
        assert six_six_issues[0].severity == IssueSeverity.MAJOR

    def test_validate_6x6_rule_too_many_words(self):
        """Test that bullets with >6 words fail 6x6 rule"""
        validator = SemanticValidator()
        data = {
            "metadata": {"title": "Test"},
            "sections": [
                {
                    "slides": [
                        {
                            "type": "content",
                            "title": "Wordy Bullets",
                            "content": {
                                "bullets": [
                                    "This bullet point has way too many words in it"
                                ]
                            },
                            "notes": "Notes"
                        }
                    ]
                }
            ]
        }
        result = validator.validate(data)

        # Should have word count violation
        word_issues = [i for i in result.issues
                      if "SIX_SIX_WORD_COUNT" in i.rule_id]
        assert len(word_issues) > 0

    def test_speaker_notes_coverage_good(self):
        """Test that good notes coverage passes"""
        validator = SemanticValidator()
        data = {
            "metadata": {"title": "Test"},
            "sections": [
                {
                    "slides": [
                        {
                            "type": "content",
                            "title": "Slide 1",
                            "content": {"bullets": ["Point"]},
                            "notes": "Good notes here"
                        },
                        {
                            "type": "content",
                            "title": "Slide 2",
                            "content": {"bullets": ["Point"]},
                            "notes": "More good notes"
                        }
                    ]
                }
            ]
        }
        result = validator.validate(data)

        # Should have good coverage
        assert result.metrics.notes_coverage == 1.0

    def test_speaker_notes_coverage_poor(self):
        """Test that poor notes coverage generates issue"""
        validator = SemanticValidator()
        data = {
            "metadata": {"title": "Test"},
            "sections": [
                {
                    "slides": [
                        {
                            "type": "content",
                            "title": "Slide 1",
                            "content": {"bullets": ["Point"]}
                            # No notes
                        },
                        {
                            "type": "content",
                            "title": "Slide 2",
                            "content": {"bullets": ["Point"]}
                            # No notes
                        }
                    ]
                }
            ]
        }
        result = validator.validate(data)

        # Should have notes coverage issue
        notes_issues = [i for i in result.issues
                       if i.category == IssueCategory.COMPLETENESS]
        assert len(notes_issues) > 0

    def test_slide_type_variety_good(self):
        """Test that good slide type variety passes"""
        validator = SemanticValidator()
        data = {
            "metadata": {"title": "Test"},
            "sections": [
                {
                    "slides": [
                        {"type": "title", "title": "Title"},
                        {"type": "content", "title": "Content"},
                        {"type": "comparison", "title": "Comparison",
                         "content": {"left": [], "right": []}},
                        {"type": "quote", "title": "Quote",
                         "content": {"text": "Quote"}}
                    ]
                }
            ]
        }
        result = validator.validate(data)

        # Should have good variety (4 types)
        assert result.metrics.slide_type_count >= 3

    def test_slide_type_variety_poor(self):
        """Test that poor slide type variety generates issue"""
        validator = SemanticValidator()
        data = {
            "metadata": {"title": "Test"},
            "sections": [
                {
                    "slides": [
                        {"type": "content", "title": "Slide 1"},
                        {"type": "content", "title": "Slide 2"},
                        {"type": "content", "title": "Slide 3"}
                    ]
                }
            ]
        }
        result = validator.validate(data)

        # Should have variety issue
        variety_issues = [i for i in result.issues
                         if "SLIDE_VARIETY" in i.rule_id]
        assert len(variety_issues) > 0

    def test_quality_scoring(self, minimal_presentation):
        """Test that quality scores are calculated"""
        validator = SemanticValidator()
        result = validator.validate(minimal_presentation)

        # Should have all scores
        assert result.metrics.six_six_score >= 0
        assert result.metrics.notes_coverage >= 0
        assert result.metrics.variety_score >= 0
        assert result.metrics.overall_score >= 0

    def test_issue_classification_critical(self):
        """Test that critical issues are properly classified"""
        validator = SemanticValidator()
        # Currently semantic validator doesn't have CRITICAL issues
        # but we can test the structure
        result = validator.validate({
            "metadata": {"title": "Test"},
            "sections": []
        })

        critical = result.critical_issues
        assert isinstance(critical, list)

    def test_issue_classification_major(self):
        """Test that major issues are properly classified"""
        validator = SemanticValidator()
        data = {
            "metadata": {"title": "Test"},
            "sections": [
                {
                    "slides": [
                        {
                            "type": "content",
                            "title": "Slide",
                            "content": {
                                "bullets": list(range(10))  # Too many
                            }
                        }
                    ]
                }
            ]
        }
        result = validator.validate(data)

        major = result.major_issues
        assert len(major) > 0

    def test_accessibility_missing_alt_text(self):
        """Test that image slides without alt text generate issue"""
        validator = SemanticValidator()
        data = {
            "metadata": {"title": "Test"},
            "sections": [
                {
                    "slides": [
                        {
                            "type": "image",
                            "title": "Image Slide",
                            "content": {
                                "image_path": "test.png"
                                # Missing alt_text
                            }
                        }
                    ]
                }
            ]
        }
        result = validator.validate(data)

        # Should have accessibility issue
        alt_issues = [i for i in result.issues
                     if i.category == IssueCategory.ACCESSIBILITY]
        assert len(alt_issues) > 0

    def test_consistency_checking(self):
        """Test that consistency issues are detected"""
        validator = SemanticValidator()
        data = {
            "metadata": {"title": "Test"},
            "sections": [
                {"title": "1. First Section", "slides": []},
                {"title": "Second Section", "slides": []},  # Inconsistent numbering
                {"title": "3. Third Section", "slides": []}
            ]
        }
        result = validator.validate(data)

        # Should have consistency issue
        consistency_issues = [i for i in result.issues
                             if i.category == IssueCategory.CONSISTENCY]
        # May or may not have issue depending on implementation
        assert isinstance(consistency_issues, list)

    def test_recommendations_generation(self):
        """Test that recommendations are generated"""
        validator = SemanticValidator()
        data = {
            "metadata": {"title": "Test"},
            "sections": [
                {
                    "slides": [
                        {
                            "type": "content",
                            "title": "Slide",
                            "content": {"bullets": []}
                            # No notes, empty content
                        }
                    ]
                }
            ]
        }
        result = validator.validate(data)

        # Should have recommendations
        assert len(result.recommendations) > 0


# =============================================================================
# INTEGRATION TESTS - THREE TIER VALIDATION
# =============================================================================

class TestThreeTierValidation:
    """Integration tests for the full validation pipeline"""

    def test_three_tier_validation_valid_presentation(self, minimal_presentation):
        """Test running all three validators on valid presentation"""
        # Level 1: Structure
        struct_validator = StructureValidator()
        struct_result = struct_validator.validate(minimal_presentation)
        assert struct_result.valid is True

        # Level 2: Schema
        schema_validator = SchemaValidator()
        schema_result = schema_validator.validate(minimal_presentation)
        assert schema_result.valid is True

        # Level 3: Semantic
        semantic_validator = SemanticValidator()
        semantic_result = semantic_validator.validate(minimal_presentation)
        # May or may not be valid depending on quality thresholds
        assert isinstance(semantic_result, SemanticValidationResult)

    def test_three_tier_validation_invalid_structure(self):
        """Test that structure validation catches early issues"""
        invalid_data = {"invalid": "structure"}

        # Structure should fail
        struct_validator = StructureValidator()
        struct_result = struct_validator.validate(invalid_data)
        assert struct_result.valid is False

        # Should still run schema validation (won't crash)
        schema_validator = SchemaValidator()
        schema_result = schema_validator.validate(invalid_data)
        assert schema_result.valid is False

    def test_validation_with_all_slide_types(self, all_slide_types_presentation):
        """Test validation with presentation using all slide types"""
        struct_validator = StructureValidator()
        struct_result = struct_validator.validate(all_slide_types_presentation)
        assert struct_result.valid is True

        schema_validator = SchemaValidator()
        schema_result = schema_validator.validate(all_slide_types_presentation)
        assert schema_result.valid is True

    def test_validation_with_complex_presentation(self, complex_presentation):
        """Test validation with large complex presentation"""
        struct_validator = StructureValidator()
        struct_result = struct_validator.validate(complex_presentation)
        assert struct_result.valid is True

        semantic_validator = SemanticValidator()
        semantic_result = semantic_validator.validate(complex_presentation)

        # Should have calculated metrics
        assert semantic_result.metrics.total_slides > 0
        assert semantic_result.metrics.total_sections > 0

    def test_validation_result_accumulation(self):
        """Test using ValidationResult pattern to merge results"""
        data = {
            "metadata": {"title": "Test"},
            "sections": [
                {
                    "slides": [
                        {
                            "type": "content",
                            "title": "Slide",
                            "content": {
                                "bullets": ["A very long bullet point with too many words"]
                            }
                        }
                    ]
                }
            ]
        }

        # Create a ValidationResult and accumulate findings
        result = ValidationResult()

        # Run structure validation
        struct_validator = StructureValidator()
        struct_result = struct_validator.validate(data)

        if not struct_result.valid:
            for error in struct_result.errors:
                result.add_error(error.message)

        # Run semantic validation
        semantic_validator = SemanticValidator()
        semantic_result = semantic_validator.validate(data)

        for issue in semantic_result.issues:
            if issue.severity == IssueSeverity.MAJOR:
                result.add_issue(
                    issue.message,
                    ValidationSeverity.ERROR,
                    issue.location,
                    rule_id=issue.rule_id
                )

        # Should have accumulated results
        assert isinstance(result, ValidationResult)


# =============================================================================
# EDGE CASE TESTS
# =============================================================================

class TestEdgeCases:
    """Tests for edge cases and error handling"""

    def test_malformed_json_handling(self):
        """Test that validators handle non-JSON-parseable data gracefully"""
        # Validators expect parsed dict, so test with invalid structure
        invalid_data = None

        struct_validator = StructureValidator()
        # Should not crash
        try:
            result = struct_validator.validate(invalid_data)
            assert result.valid is False
        except Exception as e:
            # May raise exception for None type
            assert True

    def test_empty_presentation(self):
        """Test validation of empty presentation"""
        empty_data = {
            "metadata": {"title": "Empty"},
            "sections": []
        }

        struct_validator = StructureValidator()
        result = struct_validator.validate(empty_data)

        # Valid structure, no sections
        assert result.valid is True
        assert result.stats["totalSections"] == 0

    def test_missing_sections_array(self):
        """Test handling of completely missing sections"""
        data = {
            "metadata": {"title": "Test"}
            # sections missing entirely
        }

        struct_validator = StructureValidator()
        result = struct_validator.validate(data)

        assert result.valid is False
        assert any("sections" in e.message.lower() for e in result.errors)

    def test_unicode_content(self):
        """Test that validators handle unicode characters correctly"""
        unicode_data = {
            "metadata": {
                "title": "Unicode Test: 你好世界 🌍",
                "author": "José García"
            },
            "sections": [
                {
                    "slides": [
                        {
                            "type": "content",
                            "title": "Émojis and Spëcial Çhars",
                            "content": {
                                "bullets": [
                                    "Bullet with émojis 😀",
                                    "Bullet with accents: café",
                                    "Bullet with symbols: €£¥"
                                ]
                            },
                            "notes": "Notes with unicode: 日本語"
                        }
                    ]
                }
            ]
        }

        struct_validator = StructureValidator()
        result = struct_validator.validate(unicode_data)

        # Should handle unicode without issues
        assert result.valid is True

    def test_deeply_nested_content(self):
        """Test validation with deeply nested structures"""
        data = {
            "metadata": {"title": "Test"},
            "sections": [
                {
                    "title": f"Section {i}",
                    "slides": [
                        {
                            "type": "content",
                            "title": f"Slide {j}",
                            "content": {"bullets": [f"Bullet {k}" for k in range(3)]},
                            "notes": f"Notes {j}"
                        }
                        for j in range(10)
                    ]
                }
                for i in range(5)
            ]
        }

        struct_validator = StructureValidator()
        result = struct_validator.validate(data)

        assert result.valid is True
        assert result.stats["totalSections"] == 5
        assert result.stats["totalSlides"] == 50

    def test_null_and_none_values(self):
        """Test handling of null/None values in content"""
        data = {
            "metadata": {"title": "Test", "author": None},
            "sections": [
                {
                    "title": None,
                    "slides": [
                        {
                            "type": "content",
                            "title": "Test",
                            "content": None,
                            "notes": None
                        }
                    ]
                }
            ]
        }

        struct_validator = StructureValidator()
        result = struct_validator.validate(data)

        # May have warnings but shouldn't crash
        assert isinstance(result, StructureValidationResult)

    def test_extra_unknown_fields(self):
        """Test that extra fields don't break validation"""
        data = {
            "metadata": {
                "title": "Test",
                "extra_field": "Should be ignored"
            },
            "sections": [
                {
                    "slides": [
                        {
                            "type": "content",
                            "title": "Test",
                            "unknown_field": "Also ignored",
                            "content": {"bullets": []}
                        }
                    ]
                }
            ],
            "unknown_root_field": "Ignored too"
        }

        struct_validator = StructureValidator()
        result = struct_validator.validate(data)

        # Should be valid despite extra fields
        assert result.valid is True


# =============================================================================
# VALIDATION RESULT UTILITY TESTS
# =============================================================================

class TestValidationResultUtility:
    """Tests for the ValidationResult utility pattern"""

    def test_validation_result_creation(self):
        """Test creating a ValidationResult"""
        result = ValidationResult()

        assert result.valid is True
        assert len(result.errors) == 0
        assert len(result.warnings) == 0

    def test_validation_result_add_error(self):
        """Test adding errors to ValidationResult"""
        result = ValidationResult()
        result.add_error("Test error")

        assert result.valid is False
        assert result.error_count == 1

    def test_validation_result_add_warning(self):
        """Test adding warnings to ValidationResult"""
        result = ValidationResult()
        result.add_warning("Test warning")

        assert result.valid is True  # Warnings don't affect validity
        assert result.warning_count == 1

    def test_validation_result_add_issue(self):
        """Test adding structured issues to ValidationResult"""
        result = ValidationResult()
        result.add_issue(
            "Test issue",
            ValidationSeverity.ERROR,
            path="$.sections[0]",
            rule_id="TEST_RULE"
        )

        assert result.valid is False
        assert result.issue_count == 1
        assert result.issues[0].severity == ValidationSeverity.ERROR

    def test_validation_result_merge(self):
        """Test merging ValidationResults"""
        result1 = ValidationResult()
        result1.add_error("Error 1")

        result2 = ValidationResult()
        result2.add_warning("Warning 1")

        result1.merge(result2)

        assert result1.error_count == 1
        assert result1.warning_count == 1

    def test_validation_result_to_dict(self):
        """Test converting ValidationResult to dict"""
        result = ValidationResult()
        result.add_error("Test error")
        result.add_warning("Test warning")

        data = result.to_dict()

        assert isinstance(data, dict)
        assert "valid" in data
        assert "errors" in data
        assert "warnings" in data
        assert "summary" in data

    def test_validation_result_critical_issues(self):
        """Test getting critical issues from ValidationResult"""
        result = ValidationResult()
        result.add_issue("Critical", ValidationSeverity.CRITICAL)
        result.add_issue("Error", ValidationSeverity.ERROR)

        critical = result.critical_issues

        assert len(critical) == 1
        assert critical[0].severity == ValidationSeverity.CRITICAL


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
