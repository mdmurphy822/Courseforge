#!/usr/bin/env python3
"""
Basic Pipeline Test Runner (No pytest required)

This script runs a subset of pipeline integration tests without requiring pytest.
Useful for quick validation or environments where pytest is not available.

Note: For full test suite, use pytest (see PIPELINE_TESTS_README.md)
"""

import sys
import tempfile
from pathlib import Path

# Add paths for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "pipeline"))
sys.path.insert(0, str(Path(__file__).parent.parent / "semantic-structure-extractor"))
sys.path.insert(0, str(Path(__file__).parent.parent / "pptx-generator"))

# Import test utilities
from test_pipeline_integration import (
    create_sample_markdown,
    create_sample_json,
    validate_pptx_output,
    validate_manifest
)

from orchestrator import Pipeline, PipelineConfig


class SimpleTestRunner:
    """Simple test runner without pytest dependency"""

    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []

    def run_test(self, test_name, test_func):
        """Run a single test function"""
        print(f"\nRunning: {test_name}...", end=" ")
        try:
            test_func()
            print("✓ PASSED")
            self.passed += 1
            return True
        except AssertionError as e:
            print(f"✗ FAILED: {e}")
            self.failed += 1
            self.errors.append((test_name, str(e)))
            return False
        except Exception as e:
            print(f"✗ ERROR: {e}")
            self.failed += 1
            self.errors.append((test_name, f"Error: {e}"))
            return False

    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 70)
        print(f"Test Results: {self.passed} passed, {self.failed} failed")
        print("=" * 70)

        if self.errors:
            print("\nFailures and Errors:")
            for test_name, error in self.errors:
                print(f"  ✗ {test_name}")
                print(f"    {error}")

        return self.failed == 0


def test_basic_pipeline():
    """Basic pipeline test - Markdown to PPTX"""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        # Create input
        input_path = tmpdir / "input.md"
        create_sample_markdown(input_path)

        output_path = tmpdir / "output.pptx"

        # Configure and run pipeline
        config = PipelineConfig(
            input_path=input_path,
            output_path=output_path,
            verbose=False
        )

        pipeline = Pipeline(config)
        result = pipeline.run()

        # Assertions
        assert result.success, f"Pipeline failed: {result.errors}"
        assert output_path.exists(), "Output file not created"
        assert validate_pptx_output(output_path), "Invalid PPTX output"


def test_manifest_creation():
    """Test manifest creation and persistence"""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        input_path = tmpdir / "input.md"
        create_sample_markdown(input_path)

        output_path = tmpdir / "output.pptx"

        config = PipelineConfig(
            input_path=input_path,
            output_path=output_path,
            verbose=False
        )

        pipeline = Pipeline(config)
        result = pipeline.run()

        assert result.success, "Pipeline failed"
        assert result.manifest is not None, "Manifest not created"
        assert result.manifest_path is not None, "Manifest path not set"
        assert validate_manifest(result.manifest_path), "Invalid manifest"


def test_stage_ingestion():
    """Test ingestion stage isolation"""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        input_path = tmpdir / "input.md"
        create_sample_markdown(input_path)

        config = PipelineConfig(
            input_path=input_path,
            output_path=tmpdir / "output.pptx"
        )

        pipeline = Pipeline(config)
        stage_result = pipeline._stage_ingestion()

        assert stage_result.success, "Ingestion stage failed"
        assert 'format' in stage_result.data, "Format not detected"
        assert 'hash' in stage_result.data, "Hash not computed"


def test_error_handling():
    """Test pipeline error handling"""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        # Non-existent input file
        input_path = tmpdir / "nonexistent.md"
        output_path = tmpdir / "output.pptx"

        config = PipelineConfig(
            input_path=input_path,
            output_path=output_path
        )

        pipeline = Pipeline(config)
        result = pipeline.run()

        assert not result.success, "Pipeline should fail for missing file"
        assert len(result.errors) > 0, "Errors should be recorded"


def test_json_input():
    """Test JSON input handling"""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        input_path = tmpdir / "input.json"
        create_sample_json(input_path)

        output_path = tmpdir / "output.pptx"

        config = PipelineConfig(
            input_path=input_path,
            output_path=output_path,
            verbose=False
        )

        pipeline = Pipeline(config)
        result = pipeline.run()

        assert result.success, "Pipeline failed for JSON input"
        assert output_path.exists(), "Output not created for JSON input"


def main():
    """Main test runner"""
    print("=" * 70)
    print("Pipeline Integration Tests (Basic Runner)")
    print("=" * 70)
    print("\nRunning subset of tests without pytest...")
    print("For full test suite, install pytest and run:")
    print("  pytest tests/test_pipeline_integration.py -v")

    runner = SimpleTestRunner()

    # Run basic tests
    runner.run_test("test_basic_pipeline", test_basic_pipeline)
    runner.run_test("test_manifest_creation", test_manifest_creation)
    runner.run_test("test_stage_ingestion", test_stage_ingestion)
    runner.run_test("test_error_handling", test_error_handling)
    runner.run_test("test_json_input", test_json_input)

    # Print summary
    success = runner.print_summary()

    if success:
        print("\n✅ All basic tests passed!")
        print("\nNote: This is a subset of the full test suite.")
        print("Run the full suite with pytest for complete coverage.")
        return 0
    else:
        print("\n❌ Some tests failed. See details above.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
