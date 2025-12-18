#!/usr/bin/env python3
"""
Comprehensive Pipeline Integration Tests for Slideforge

Tests the full end-to-end workflow from input to PPTX generation,
including stage isolation, error handling, and manifest tracking.

Test Coverage:
1. Full pipeline tests (Markdown -> PPTX, JSON -> PPTX)
2. Stage isolation tests (each stage independently)
3. Error handling tests (invalid input, missing files, validation failures)
4. Manifest/provenance tests (tracking and persistence)
5. Integration tests with test fixtures
6. Configuration integration tests
"""

import pytest
import json
import sys
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

# Add pipeline to path
sys.path.insert(0, str(Path(__file__).parent.parent / "pipeline"))
sys.path.insert(0, str(Path(__file__).parent.parent / "semantic-structure-extractor"))
sys.path.insert(0, str(Path(__file__).parent.parent / "pptx-generator"))
sys.path.insert(0, str(Path(__file__).parent.parent / "utilities"))

from orchestrator import Pipeline, PipelineConfig, PipelineResult, StageResult
from manifest import (
    PipelineManifest,
    ProcessingStep,
    ProvenanceEntry,
    QualityMetadata,
    create_manifest,
    load_manifest
)


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def create_sample_markdown(path: Path) -> None:
    """Create a sample markdown file for testing."""
    content = """# Test Presentation

## Introduction

This is a test presentation for pipeline integration testing.

### Key Points

- First important point
- Second key concept
- Third critical idea

## Main Content

### Overview

This section provides an overview of the main content.

### Details

More detailed information goes here.

## Conclusion

Summary of the presentation.
"""
    path.write_text(content, encoding='utf-8')


def create_sample_json(path: Path) -> None:
    """Create a sample JSON presentation for testing."""
    presentation = {
        "metadata": {
            "title": "Test Presentation",
            "subtitle": "Pipeline Integration Test",
            "author": "Slideforge Test Suite",
            "date": "2025-12-17"
        },
        "sections": [
            {
                "title": "Introduction",
                "slides": [
                    {
                        "type": "title",
                        "title": "Test Presentation",
                        "content": {"subtitle": "Pipeline Integration Test"},
                        "notes": "Title slide for testing"
                    }
                ]
            },
            {
                "title": "Content",
                "slides": [
                    {
                        "type": "content",
                        "title": "Key Points",
                        "content": {
                            "bullets": ["Point 1", "Point 2", "Point 3"]
                        },
                        "notes": "Content slide notes"
                    }
                ]
            }
        ]
    }
    path.write_text(json.dumps(presentation, indent=2), encoding='utf-8')


def validate_pptx_output(path: Path) -> bool:
    """Validate that a PPTX file was created and is valid."""
    if not path.exists():
        return False
    if not path.suffix == '.pptx':
        return False
    if path.stat().st_size == 0:
        return False

    # Try to open with python-pptx
    try:
        from pptx import Presentation
        prs = Presentation(str(path))
        return True
    except Exception:
        return False


def validate_manifest(manifest_path: Path) -> bool:
    """Validate that a manifest file exists and is valid JSON."""
    if not manifest_path.exists():
        return False

    try:
        manifest = load_manifest(str(manifest_path))
        return manifest.id is not None
    except Exception:
        return False


# =============================================================================
# TEST CLASS: Full Pipeline Tests
# =============================================================================

class TestFullPipeline:
    """End-to-end pipeline tests"""

    def test_full_pipeline_markdown_input(self, temp_output_dir):
        """Test complete pipeline from Markdown to PPTX"""
        # Create input markdown
        input_path = temp_output_dir / "input.md"
        create_sample_markdown(input_path)

        output_path = temp_output_dir / "output.pptx"

        # Configure pipeline
        config = PipelineConfig(
            input_path=input_path,
            output_path=output_path,
            verbose=True
        )

        # Run pipeline
        pipeline = Pipeline(config)
        result = pipeline.run()

        # Assertions
        assert result.success, f"Pipeline failed: {result.errors}"
        assert result.output_path is not None
        assert result.output_path.exists()
        assert validate_pptx_output(result.output_path)
        assert result.stages_completed == 6
        assert result.manifest is not None
        assert result.manifest_path is not None
        assert validate_manifest(result.manifest_path)

    def test_full_pipeline_json_input(self, temp_output_dir, minimal_presentation_path):
        """Test complete pipeline from JSON presentation structure to PPTX"""
        output_path = temp_output_dir / "json_output.pptx"

        config = PipelineConfig(
            input_path=minimal_presentation_path,
            output_path=output_path,
            verbose=True
        )

        pipeline = Pipeline(config)
        result = pipeline.run()

        assert result.success
        assert result.output_path.exists()
        assert validate_pptx_output(result.output_path)
        assert result.stages_completed == 6

    def test_full_pipeline_with_theme(self, temp_output_dir):
        """Test pipeline with theme selection"""
        input_path = temp_output_dir / "themed_input.md"
        create_sample_markdown(input_path)

        output_path = temp_output_dir / "themed_output.pptx"

        config = PipelineConfig(
            input_path=input_path,
            output_path=output_path,
            theme="corporate",
            verbose=True
        )

        pipeline = Pipeline(config)
        result = pipeline.run()

        assert result.success
        assert result.manifest.template_used is not None

    def test_full_pipeline_with_validation(self, temp_output_dir):
        """Test pipeline with all validation enabled"""
        input_path = temp_output_dir / "validation_input.md"
        create_sample_markdown(input_path)

        output_path = temp_output_dir / "validation_output.pptx"

        config = PipelineConfig(
            input_path=input_path,
            output_path=output_path,
            max_bullets_per_slide=6,
            max_words_per_bullet=12,
            min_quality_score=70.0,
            verbose=True
        )

        pipeline = Pipeline(config)
        result = pipeline.run()

        assert result.success
        assert result.manifest.quality is not None
        assert result.manifest.quality.validation_score >= 0

    def test_validate_only_mode(self, temp_output_dir):
        """Test pipeline in validation-only mode (no PPTX generation)"""
        input_path = temp_output_dir / "validate_only.md"
        create_sample_markdown(input_path)

        output_path = temp_output_dir / "no_output.pptx"

        config = PipelineConfig(
            input_path=input_path,
            output_path=output_path,
            validate_only=True,
            verbose=True
        )

        pipeline = Pipeline(config)
        result = pipeline.run()

        assert result.success
        # Output file should NOT be created in validate-only mode
        assert not output_path.exists()
        # But validation should have run
        assert result.stages_completed == 5  # All stages except generation


# =============================================================================
# TEST CLASS: Stage Isolation Tests
# =============================================================================

class TestStageIsolation:
    """Individual stage tests"""

    def test_ingestion_stage(self, temp_output_dir):
        """Test ingestion stage can load and detect format"""
        input_path = temp_output_dir / "ingestion_test.md"
        create_sample_markdown(input_path)

        config = PipelineConfig(
            input_path=input_path,
            output_path=temp_output_dir / "output.pptx"
        )

        pipeline = Pipeline(config)
        stage_result = pipeline._stage_ingestion()

        assert stage_result.success
        assert stage_result.data is not None
        assert 'format' in stage_result.data
        assert 'hash' in stage_result.data
        assert stage_result.data['format'] in ['markdown', 'json', 'text', 'html']

    def test_extraction_stage(self, temp_output_dir):
        """Test extraction stage can parse content structure"""
        input_path = temp_output_dir / "extraction_test.md"
        create_sample_markdown(input_path)

        config = PipelineConfig(
            input_path=input_path,
            output_path=temp_output_dir / "output.pptx"
        )

        pipeline = Pipeline(config)

        # Run ingestion first to populate stage data
        pipeline._stage_ingestion()

        # Run extraction
        stage_result = pipeline._stage_extraction()

        assert stage_result.success
        assert stage_result.data is not None
        assert 'chapters' in stage_result.metadata or 'concepts' in stage_result.metadata

    def test_transformation_stage(self, temp_output_dir):
        """Test transformation stage converts to presentation schema"""
        input_path = temp_output_dir / "transform_test.md"
        create_sample_markdown(input_path)

        config = PipelineConfig(
            input_path=input_path,
            output_path=temp_output_dir / "output.pptx"
        )

        pipeline = Pipeline(config)

        # Run prerequisite stages
        pipeline._stage_ingestion()
        pipeline._stage_extraction()

        # Run transformation
        stage_result = pipeline._stage_transformation()

        assert stage_result.success
        assert stage_result.data is not None
        assert 'sections' in stage_result.data or isinstance(stage_result.data, dict)
        assert 'slides' in stage_result.metadata or 'sections' in stage_result.metadata

    def test_template_selection_stage(self, temp_output_dir):
        """Test template selection stage chooses appropriate template"""
        input_path = temp_output_dir / "template_test.md"
        create_sample_markdown(input_path)

        config = PipelineConfig(
            input_path=input_path,
            output_path=temp_output_dir / "output.pptx"
        )

        pipeline = Pipeline(config)

        # Run prerequisite stages
        pipeline._stage_ingestion()
        pipeline._stage_extraction()
        pipeline._stage_transformation()

        # Run template selection
        stage_result = pipeline._stage_template_selection()

        assert stage_result.success
        assert stage_result.data is not None
        assert 'template' in stage_result.data

    def test_validation_stage(self, temp_output_dir):
        """Test validation stage performs quality checks"""
        input_path = temp_output_dir / "validation_test.md"
        create_sample_markdown(input_path)

        config = PipelineConfig(
            input_path=input_path,
            output_path=temp_output_dir / "output.pptx",
            min_quality_score=0.0  # Set low threshold for testing
        )

        pipeline = Pipeline(config)

        # Run prerequisite stages
        pipeline._stage_ingestion()
        pipeline._stage_extraction()
        pipeline._stage_transformation()
        pipeline._stage_template_selection()

        # Run validation
        stage_result = pipeline._stage_validation()

        # Validation might succeed or fail, but should not error
        assert stage_result.stage_name == 'validation'
        assert stage_result.data is not None
        assert 'validationScore' in stage_result.data or 'validation_score' in stage_result.data

    def test_generation_stage(self, temp_output_dir):
        """Test generation stage creates PPTX file"""
        input_path = temp_output_dir / "generation_test.md"
        create_sample_markdown(input_path)

        output_path = temp_output_dir / "generated.pptx"

        config = PipelineConfig(
            input_path=input_path,
            output_path=output_path
        )

        pipeline = Pipeline(config)

        # Run all prerequisite stages
        pipeline._stage_ingestion()
        pipeline._stage_extraction()
        pipeline._stage_transformation()
        pipeline._stage_template_selection()

        # Run generation
        stage_result = pipeline._stage_generation()

        assert stage_result.success
        assert output_path.exists()
        assert validate_pptx_output(output_path)


# =============================================================================
# TEST CLASS: Error Handling Tests
# =============================================================================

class TestErrorHandling:
    """Error handling and recovery tests"""

    def test_pipeline_invalid_input(self, temp_output_dir):
        """Test pipeline handles invalid input gracefully"""
        # Create invalid JSON file
        input_path = temp_output_dir / "invalid.json"
        input_path.write_text("{ invalid json content", encoding='utf-8')

        output_path = temp_output_dir / "output.pptx"

        config = PipelineConfig(
            input_path=input_path,
            output_path=output_path
        )

        pipeline = Pipeline(config)
        result = pipeline.run()

        # Should fail gracefully
        assert not result.success
        assert len(result.errors) > 0

    def test_pipeline_missing_file(self, temp_output_dir):
        """Test pipeline handles missing input file gracefully"""
        input_path = temp_output_dir / "nonexistent.md"
        output_path = temp_output_dir / "output.pptx"

        config = PipelineConfig(
            input_path=input_path,
            output_path=output_path
        )

        pipeline = Pipeline(config)
        result = pipeline.run()

        assert not result.success
        assert len(result.errors) > 0
        assert any('not found' in err.lower() for err in result.errors)

    def test_pipeline_validation_failure(self, temp_output_dir):
        """Test pipeline handles validation failure appropriately"""
        input_path = temp_output_dir / "validation_fail.json"

        # Create presentation with many violations
        bad_presentation = {
            "metadata": {"title": "Bad Presentation"},
            "sections": [{
                "title": "Section",
                "slides": [{
                    "type": "content",
                    "title": "Too Many Bullets",
                    "content": {
                        "bullets": [f"Bullet {i}" for i in range(20)]  # Violates 6x6 rule
                    }
                }]
            }]
        }
        input_path.write_text(json.dumps(bad_presentation), encoding='utf-8')

        output_path = temp_output_dir / "output.pptx"

        config = PipelineConfig(
            input_path=input_path,
            output_path=output_path,
            fail_on_warnings=True,
            min_quality_score=95.0  # Set high threshold
        )

        pipeline = Pipeline(config)
        result = pipeline.run()

        # Should complete but may have warnings
        assert result.manifest.quality is not None
        if result.manifest.quality.validation_score < 95.0:
            assert len(result.warnings) > 0 or not result.success

    def test_pipeline_partial_recovery(self, temp_output_dir):
        """Test pipeline can provide partial results on failure"""
        input_path = temp_output_dir / "partial_test.md"
        create_sample_markdown(input_path)

        output_path = temp_output_dir / "output.pptx"

        config = PipelineConfig(
            input_path=input_path,
            output_path=output_path
        )

        pipeline = Pipeline(config)
        result = pipeline.run()

        # Even if pipeline fails, should have manifest with partial data
        if not result.success:
            assert result.manifest is not None
            assert len(result.manifest.processing_steps) > 0


# =============================================================================
# TEST CLASS: Manifest/Provenance Tests
# =============================================================================

class TestManifestIntegration:
    """Manifest and provenance tests"""

    def test_manifest_creation(self, temp_output_dir):
        """Test that manifest is created at pipeline start"""
        input_path = temp_output_dir / "manifest_test.md"
        create_sample_markdown(input_path)

        output_path = temp_output_dir / "output.pptx"

        config = PipelineConfig(
            input_path=input_path,
            output_path=output_path
        )

        pipeline = Pipeline(config)

        # Manifest should be created during init
        assert pipeline.manifest is not None
        assert pipeline.manifest.id is not None
        assert pipeline.manifest.version is not None

    def test_manifest_stage_tracking(self, temp_output_dir):
        """Test that stages are recorded in manifest"""
        input_path = temp_output_dir / "tracking_test.md"
        create_sample_markdown(input_path)

        output_path = temp_output_dir / "output.pptx"

        config = PipelineConfig(
            input_path=input_path,
            output_path=output_path
        )

        pipeline = Pipeline(config)
        result = pipeline.run()

        assert result.success
        assert len(result.manifest.processing_steps) > 0

        # Check that stages were recorded
        stage_names = [step.stage for step in result.manifest.processing_steps]
        assert 'ingestion' in stage_names
        assert 'extraction' in stage_names
        assert 'transformation' in stage_names

    def test_manifest_provenance(self, temp_output_dir):
        """Test that provenance info is captured"""
        input_path = temp_output_dir / "provenance_test.md"
        create_sample_markdown(input_path)

        output_path = temp_output_dir / "output.pptx"

        config = PipelineConfig(
            input_path=input_path,
            output_path=output_path
        )

        pipeline = Pipeline(config)
        result = pipeline.run()

        assert result.success
        assert result.manifest.provenance_info is not None
        assert result.manifest.provenance_info.source_path is not None
        assert result.manifest.provenance_info.source_format is not None
        assert result.manifest.provenance_info.input_hash is not None

    def test_manifest_persistence(self, temp_output_dir):
        """Test that manifest is saved correctly and can be loaded"""
        input_path = temp_output_dir / "persistence_test.md"
        create_sample_markdown(input_path)

        output_path = temp_output_dir / "output.pptx"

        config = PipelineConfig(
            input_path=input_path,
            output_path=output_path
        )

        pipeline = Pipeline(config)
        result = pipeline.run()

        assert result.success
        assert result.manifest_path is not None
        assert result.manifest_path.exists()

        # Load manifest and verify
        loaded_manifest = load_manifest(str(result.manifest_path))
        assert loaded_manifest.id == result.manifest.id
        assert loaded_manifest.version == result.manifest.version
        assert len(loaded_manifest.processing_steps) == len(result.manifest.processing_steps)

    def test_manifest_quality_metadata(self, temp_output_dir):
        """Test that quality metadata is captured in manifest"""
        input_path = temp_output_dir / "quality_test.md"
        create_sample_markdown(input_path)

        output_path = temp_output_dir / "output.pptx"

        config = PipelineConfig(
            input_path=input_path,
            output_path=output_path
        )

        pipeline = Pipeline(config)
        result = pipeline.run()

        assert result.success
        assert result.manifest.quality is not None
        assert result.manifest.quality.total_slides > 0
        assert result.manifest.quality.validation_score >= 0

    def test_manifest_processing_log(self, temp_output_dir):
        """Test that processing log is maintained"""
        input_path = temp_output_dir / "log_test.md"
        create_sample_markdown(input_path)

        output_path = temp_output_dir / "output.pptx"

        config = PipelineConfig(
            input_path=input_path,
            output_path=output_path
        )

        pipeline = Pipeline(config)
        result = pipeline.run()

        assert result.success
        assert result.manifest.processing_log is not None
        assert len(result.manifest.processing_log.stages_completed) > 0
        assert result.manifest.processing_log.duration_seconds > 0


# =============================================================================
# TEST CLASS: Integration Tests with Test Fixtures
# =============================================================================

class TestFixtureIntegration:
    """Tests using the standard test fixtures"""

    def test_integration_minimal_fixture(self, temp_output_dir, minimal_presentation_path):
        """Test pipeline with minimal_5_slides.json fixture"""
        output_path = temp_output_dir / "minimal_output.pptx"

        config = PipelineConfig(
            input_path=minimal_presentation_path,
            output_path=output_path,
            verbose=True
        )

        pipeline = Pipeline(config)
        result = pipeline.run()

        assert result.success
        assert result.output_path.exists()
        assert validate_pptx_output(result.output_path)

        # Should have created expected number of slides
        assert result.manifest.quality is not None
        assert result.manifest.quality.total_slides == 5

    def test_integration_all_types_fixture(self, temp_output_dir, all_slide_types_path):
        """Test pipeline with all_slide_types.json fixture"""
        output_path = temp_output_dir / "all_types_output.pptx"

        config = PipelineConfig(
            input_path=all_slide_types_path,
            output_path=output_path,
            verbose=True
        )

        pipeline = Pipeline(config)
        result = pipeline.run()

        assert result.success
        assert result.output_path.exists()
        assert validate_pptx_output(result.output_path)

        # Should demonstrate variety
        assert result.manifest.quality is not None
        assert result.manifest.quality.slide_type_variety > 3

    def test_integration_complex_fixture(self, temp_output_dir, complex_presentation_path):
        """Test pipeline with complex_50_slides.json fixture"""
        output_path = temp_output_dir / "complex_output.pptx"

        config = PipelineConfig(
            input_path=complex_presentation_path,
            output_path=output_path,
            verbose=True
        )

        pipeline = Pipeline(config)
        result = pipeline.run()

        assert result.success
        assert result.output_path.exists()
        assert validate_pptx_output(result.output_path)

        # Should have 50 slides
        assert result.manifest.quality is not None
        assert result.manifest.quality.total_slides == 50


# =============================================================================
# TEST CLASS: Configuration Integration Tests
# =============================================================================

class TestConfigIntegration:
    """Configuration system integration tests"""

    def test_pipeline_with_config(self, temp_output_dir):
        """Test that pipeline respects configuration"""
        input_path = temp_output_dir / "config_test.md"
        create_sample_markdown(input_path)

        output_path = temp_output_dir / "output.pptx"

        config = PipelineConfig(
            input_path=input_path,
            output_path=output_path,
            max_bullets_per_slide=6,
            max_words_per_bullet=10,
            include_speaker_notes=True,
            verbose=False
        )

        pipeline = Pipeline(config)

        # Verify config is stored in manifest
        assert pipeline.manifest.pipeline_config is not None
        assert pipeline.manifest.pipeline_config['maxBulletsPerSlide'] == 6
        assert pipeline.manifest.pipeline_config['maxWordsPerBullet'] == 10

    def test_pipeline_config_override(self, temp_output_dir):
        """Test that presentation metadata can override config"""
        input_path = temp_output_dir / "override_test.json"

        presentation = {
            "metadata": {
                "title": "Override Test",
                "author": "Test Author",
                "subject": "Testing"
            },
            "sections": [{
                "title": "Section",
                "slides": [{
                    "type": "title",
                    "title": "Override Test"
                }]
            }]
        }
        input_path.write_text(json.dumps(presentation), encoding='utf-8')

        output_path = temp_output_dir / "output.pptx"

        config = PipelineConfig(
            input_path=input_path,
            output_path=output_path
        )

        pipeline = Pipeline(config)
        result = pipeline.run()

        assert result.success
        # Metadata from JSON should be preserved in manifest
        assert result.manifest.source_info is not None

    def test_pipeline_quality_settings(self, temp_output_dir):
        """Test that quality settings are enforced"""
        input_path = temp_output_dir / "quality_settings.md"
        create_sample_markdown(input_path)

        output_path = temp_output_dir / "output.pptx"

        config = PipelineConfig(
            input_path=input_path,
            output_path=output_path,
            min_quality_score=80.0,
            fail_on_warnings=False
        )

        pipeline = Pipeline(config)
        result = pipeline.run()

        # Pipeline should complete
        assert result.manifest is not None
        assert result.manifest.quality is not None

        # Quality score should be calculated
        assert result.manifest.quality.validation_score >= 0


# =============================================================================
# TEST CLASS: Performance and Timing Tests
# =============================================================================

class TestPerformance:
    """Performance and timing tests"""

    def test_pipeline_timing_tracking(self, temp_output_dir):
        """Test that pipeline tracks execution time"""
        input_path = temp_output_dir / "timing_test.md"
        create_sample_markdown(input_path)

        output_path = temp_output_dir / "output.pptx"

        config = PipelineConfig(
            input_path=input_path,
            output_path=output_path
        )

        start_time = time.time()
        pipeline = Pipeline(config)
        result = pipeline.run()
        end_time = time.time()

        assert result.success

        # Total duration should be reasonable
        assert result.total_duration_ms > 0
        assert result.total_duration_ms < (end_time - start_time) * 1000 * 2  # Allow 2x margin

        # Each stage should have duration
        for step in result.manifest.processing_steps:
            assert step.duration_ms > 0

    def test_stage_duration_tracking(self, temp_output_dir):
        """Test that individual stage durations are tracked"""
        input_path = temp_output_dir / "stage_timing.md"
        create_sample_markdown(input_path)

        output_path = temp_output_dir / "output.pptx"

        config = PipelineConfig(
            input_path=input_path,
            output_path=output_path
        )

        pipeline = Pipeline(config)
        result = pipeline.run()

        assert result.success

        # All stages should have timing
        stage_names = [step.stage for step in result.manifest.processing_steps]
        assert 'ingestion' in stage_names

        for step in result.manifest.processing_steps:
            assert step.duration_ms >= 0


# =============================================================================
# RUN TESTS
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
