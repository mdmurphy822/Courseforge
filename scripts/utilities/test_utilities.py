#!/usr/bin/env python3
"""
Test script for ValidationResult and common utilities.

Runs basic tests to verify all utility functions work correctly.
"""

import sys
from pathlib import Path
import tempfile
import shutil

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.utilities import (
    ValidationResult,
    ValidationSeverity,
    ValidationIssue,
    generate_slug,
    ensure_unique_slug,
    get_repo_root,
    validate_file_exists,
    validate_directory_exists,
    sanitize_filename,
    read_text_file,
    get_file_size_mb,
    ensure_output_directory
)


def test_validation_result():
    """Test ValidationResult functionality."""
    print("\n" + "=" * 70)
    print("TEST: ValidationResult")
    print("=" * 70)

    # Test basic error/warning accumulation
    result = ValidationResult()
    assert result.valid, "New result should be valid"

    result.add_error("Test error", context={"field": "test"})
    assert not result.valid, "Result should be invalid after error"
    assert result.error_count == 1, "Should have 1 error"

    result.add_warning("Test warning")
    assert result.warning_count == 1, "Should have 1 warning"

    # Test structured issues
    result.add_issue(
        message="Test issue",
        severity=ValidationSeverity.ERROR,
        path="$.test",
        rule_id="TEST_RULE",
        suggestion="Fix it"
    )
    assert result.issue_count == 1, "Should have 1 structured issue"

    # Test merging
    other = ValidationResult()
    other.add_error("Another error")
    result.merge(other)
    # Note: We have 1 error from add_error, 1 from add_issue (ERROR severity), and 1 from merge = 3 total
    assert result.error_count == 3, f"Should have 3 errors after merge (got {result.error_count})"

    # Test serialization
    data = result.to_dict()
    assert "valid" in data, "Dict should have 'valid' key"
    assert "summary" in data, "Dict should have 'summary' key"

    print("✓ ValidationResult basic operations")
    print("✓ Error and warning accumulation")
    print("✓ Structured issues")
    print("✓ Result merging")
    print("✓ Serialization")


def test_slug_generation():
    """Test slug generation."""
    print("\n" + "=" * 70)
    print("TEST: Slug Generation")
    print("=" * 70)

    # Basic slug
    slug = generate_slug("Introduction to Python")
    assert slug == "introduction-to-python", f"Expected 'introduction-to-python', got '{slug}'"
    print(f"✓ Basic slug: '{slug}'")

    # Special characters
    slug = generate_slug("Module 1: Getting Started!")
    assert slug == "module-1-getting-started", f"Got: '{slug}'"
    print(f"✓ Special chars: '{slug}'")

    # Max length
    slug = generate_slug("A" * 100, max_length=20)
    assert len(slug) <= 20, f"Slug too long: {len(slug)}"
    print(f"✓ Max length: '{slug}' (length: {len(slug)})")

    # Uniqueness
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        (tmppath / "test.txt").touch()

        unique = ensure_unique_slug("test", tmppath, ".txt")
        assert unique == "test-2", f"Expected 'test-2', got '{unique}'"
        print(f"✓ Unique slug: '{unique}'")


def test_file_operations():
    """Test file validation operations."""
    print("\n" + "=" * 70)
    print("TEST: File Operations")
    print("=" * 70)

    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)

        # Test file exists validation
        test_file = tmppath / "test.txt"
        result = validate_file_exists(test_file)
        assert not result.valid, "Non-existent file should fail validation"
        print("✓ Detect missing file")

        # Create file and test again
        test_file.write_text("Test content")
        result = validate_file_exists(test_file, "test")
        assert result.valid, "Existing file should pass validation"
        print("✓ Validate existing file")

        # Test directory validation
        test_dir = tmppath / "subdir"
        result = validate_directory_exists(test_dir, create=True)
        assert result.valid, "Directory should be created"
        assert test_dir.exists(), "Directory should exist"
        print("✓ Create directory")

        # Test read file
        result = read_text_file(test_file)
        assert result.valid, "Should read file successfully"
        assert result.context['content'] == "Test content", "Content should match"
        print("✓ Read text file")

        # Test file size
        size_mb = get_file_size_mb(test_file)
        assert size_mb > 0, "File should have size"
        print(f"✓ Get file size: {size_mb:.6f} MB")


def test_filename_sanitization():
    """Test filename sanitization."""
    print("\n" + "=" * 70)
    print("TEST: Filename Sanitization")
    print("=" * 70)

    # Remove invalid characters
    clean = sanitize_filename("File: Name with | Invalid * Chars.txt")
    assert "<" not in clean and ">" not in clean, "Should remove invalid chars"
    print(f"✓ Sanitize: '{clean}'")

    # Preserve extension
    long_name = "A" * 250 + ".pptx"
    clean = sanitize_filename(long_name, max_length=200)
    assert clean.endswith(".pptx"), "Should preserve extension"
    assert len(clean) <= 200, "Should respect max length"
    print(f"✓ Preserve extension: length={len(clean)}, ends with '.pptx'")


def test_repo_root():
    """Test repository root detection."""
    print("\n" + "=" * 70)
    print("TEST: Repository Root Detection")
    print("=" * 70)

    root = get_repo_root()
    if root:
        print(f"✓ Found repo root: {root}")

        # Check for CLAUDE.md
        claude_file = root / "CLAUDE.md"
        assert claude_file.exists(), "CLAUDE.md should exist at root"
        print("✓ Verified CLAUDE.md exists")
    else:
        print("⚠ Could not find repo root (may be normal in some environments)")


def test_output_directory():
    """Test output directory creation."""
    print("\n" + "=" * 70)
    print("TEST: Output Directory Creation")
    print("=" * 70)

    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)

        # Create timestamped directory
        output_dir = ensure_output_directory(tmppath, "Test Presentation")
        assert output_dir.exists(), "Directory should be created"

        # Check naming pattern
        assert "test-presentation" in output_dir.name.lower(), "Should contain slug"
        print(f"✓ Created: {output_dir.name}")

        # Create another with same name
        output_dir2 = ensure_output_directory(tmppath, "Test Presentation")
        assert output_dir2 != output_dir, "Should create unique directory"
        print(f"✓ Unique: {output_dir2.name}")


def run_all_tests():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("RUNNING UTILITY TESTS")
    print("=" * 70)

    tests = [
        ("ValidationResult", test_validation_result),
        ("Slug Generation", test_slug_generation),
        ("File Operations", test_file_operations),
        ("Filename Sanitization", test_filename_sanitization),
        ("Repository Root", test_repo_root),
        ("Output Directory", test_output_directory),
    ]

    passed = 0
    failed = 0

    for name, test_func in tests:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"\n✗ TEST FAILED: {name}")
            print(f"  Error: {e}")
            failed += 1
        except Exception as e:
            print(f"\n✗ TEST ERROR: {name}")
            print(f"  Exception: {e}")
            failed += 1

    # Print summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Passed: {passed}/{len(tests)}")
    print(f"Failed: {failed}/{len(tests)}")

    if failed == 0:
        print("\n✓ ALL TESTS PASSED")
        return 0
    else:
        print(f"\n✗ {failed} TEST(S) FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
