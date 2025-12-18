#!/usr/bin/env python3
"""
Test script for enhanced provenance tracking in manifest.py

Tests the new ProvenanceInfo and ProcessingLog functionality.
"""

import json
import tempfile
from pathlib import Path

from manifest import (
    PipelineManifest,
    ProvenanceInfo,
    ProcessingLog,
    QualityMetadata,
    create_manifest,
    save_manifest,
    load_manifest
)


def test_provenance_info_creation():
    """Test ProvenanceInfo creation and serialization."""
    print("\n=== Testing ProvenanceInfo ===")

    provenance = ProvenanceInfo(
        source_path="/path/to/source.md",
        source_format="markdown",
        pipeline_version="1.0.0",
        processing_timestamp="2025-12-17T12:00:00",
        input_hash="abc123def456",
        original_filename="source.md",
        file_size_bytes=1024,
        source_type="document",
        original_provider="Test Author"
    )

    # Test to_dict
    data = provenance.to_dict()
    print(f"ProvenanceInfo dict: {json.dumps(data, indent=2)}")

    # Test from_dict
    restored = ProvenanceInfo.from_dict(data)
    assert restored.source_path == provenance.source_path
    assert restored.input_hash == provenance.input_hash
    print("✓ ProvenanceInfo serialization works")


def test_processing_log():
    """Test ProcessingLog functionality."""
    print("\n=== Testing ProcessingLog ===")

    log = ProcessingLog(
        stages_completed=["ingestion", "extraction", "transformation"],
        agents_used=["content-analyzer", "slide-generator"],
        slides_created=25,
        warnings_generated=3,
        errors_generated=0,
        duration_seconds=42.5
    )

    # Test to_dict
    data = log.to_dict()
    print(f"ProcessingLog dict: {json.dumps(data, indent=2)}")

    # Test from_dict
    restored = ProcessingLog.from_dict(data)
    assert restored.slides_created == log.slides_created
    assert restored.duration_seconds == log.duration_seconds
    print("✓ ProcessingLog serialization works")


def test_manifest_with_provenance():
    """Test PipelineManifest with enhanced provenance."""
    print("\n=== Testing PipelineManifest with Provenance ===")

    manifest = PipelineManifest()

    # Initialize processing log
    manifest.initialize_processing_log()

    # Create provenance info
    manifest.create_provenance_info(
        source_path="/test/input.md",
        source_format="markdown",
        pipeline_version="1.0.0",
        input_hash="test_hash_123",
        source_type="document",
        original_provider="Test Suite"
    )

    # Update processing log
    manifest.update_processing_log(
        stage_name="ingestion",
        slides_created=0,
        warnings=0,
        errors=0
    )

    manifest.update_processing_log(
        stage_name="transformation",
        slides_created=15,
        warnings=2,
        errors=0
    )

    # Add agent log
    manifest.add_agent_log(
        agent_name="slide-content-generator",
        task="Generate introduction slides",
        result={"target_ids": ["slide_001", "slide_002"]}
    )

    # Finalize
    manifest.finalize_processing_log(duration_seconds=30.5)

    # Add quality metadata
    quality = QualityMetadata(
        six_six_violations=2,
        notes_coverage=0.85,
        slide_type_variety=4,
        validation_score=92.5,
        total_slides=15,
        total_sections=3
    )
    manifest.set_quality(quality)

    # Test serialization
    data = manifest.to_dict()
    print(f"Manifest keys: {list(data.keys())}")

    # Check enhanced fields are present
    assert "provenanceInfo" in data
    assert "processingLog" in data
    print("✓ Enhanced fields present in manifest")

    # Test summary
    summary = manifest.get_summary()
    print(f"\nManifest summary: {json.dumps(summary, indent=2)}")

    assert "provenance" in summary
    assert "processing" in summary
    print("✓ Enhanced summary includes provenance and processing info")

    return manifest


def test_manifest_save_load():
    """Test saving and loading manifest with provenance."""
    print("\n=== Testing Manifest Save/Load ===")

    # Create test manifest
    manifest = test_manifest_with_provenance()

    # Save to temp file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        temp_path = Path(f.name)

    try:
        save_manifest(manifest, str(temp_path))
        print(f"✓ Manifest saved to {temp_path}")

        # Load back
        loaded = load_manifest(str(temp_path))
        print("✓ Manifest loaded successfully")

        # Verify provenance info
        assert loaded.provenance_info is not None
        assert loaded.provenance_info.source_format == "markdown"
        assert loaded.provenance_info.input_hash == "test_hash_123"
        print("✓ ProvenanceInfo preserved")

        # Verify processing log
        assert loaded.processing_log is not None
        assert loaded.processing_log.slides_created == 15
        assert loaded.processing_log.duration_seconds == 30.5
        print("✓ ProcessingLog preserved")

        # Verify quality
        assert loaded.quality is not None
        assert loaded.quality.validation_score == 92.5
        print("✓ Quality metadata preserved")

    finally:
        # Cleanup
        if temp_path.exists():
            temp_path.unlink()
        print(f"✓ Cleaned up {temp_path}")


def test_create_manifest_function():
    """Test the convenience create_manifest function."""
    print("\n=== Testing create_manifest() Function ===")

    # Create temp test file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write("# Test Content\n\nTest presentation content.")
        temp_path = Path(f.name)

    try:
        manifest = create_manifest(
            source_path=str(temp_path),
            source_format="markdown",
            pipeline_version="1.0.0",
            pipeline_config={"test": True},
            source_type="document",
            original_provider="Test Suite"
        )

        # Verify manifest is properly initialized
        assert manifest.provenance_info is not None
        assert manifest.provenance_info.source_format == "markdown"
        assert manifest.provenance_info.input_hash is not None
        assert len(manifest.provenance_info.input_hash) == 64  # SHA256 hex
        print(f"✓ Manifest created with hash: {manifest.provenance_info.input_hash[:16]}...")

        assert manifest.processing_log is not None
        print("✓ Processing log initialized")

        # Verify backward compatibility (legacy source_info)
        assert manifest.source_info.get("path") == str(temp_path)
        assert manifest.source_info.get("format") == "markdown"
        print("✓ Legacy source_info maintained for backward compatibility")

    finally:
        if temp_path.exists():
            temp_path.unlink()


def main():
    """Run all tests."""
    print("=" * 60)
    print("TESTING ENHANCED PROVENANCE TRACKING")
    print("=" * 60)

    try:
        test_provenance_info_creation()
        test_processing_log()
        test_manifest_with_provenance()
        test_manifest_save_load()
        test_create_manifest_function()

        print("\n" + "=" * 60)
        print("ALL TESTS PASSED ✓")
        print("=" * 60)

    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
