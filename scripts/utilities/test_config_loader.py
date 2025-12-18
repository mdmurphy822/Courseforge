#!/usr/bin/env python3
"""
Test script for ConfigLoader to validate functionality.
"""

import json
import sys
from pathlib import Path

# Change to repo root before importing
repo_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(repo_root))

# Change working directory to repo root
import os
os.chdir(repo_root)

from scripts.utilities import ConfigLoader, SlideforgeConfig


def test_load_defaults():
    """Test loading default configuration."""
    print("Test 1: Load defaults")
    print("-" * 60)

    loader = ConfigLoader()
    defaults = loader.load_defaults()

    print(f"✓ Loaded {len(defaults)} configuration sections")
    print(f"  - Quality settings: {len(defaults.get('quality_settings', {}))} keys")
    print(f"  - Generation settings: {len(defaults.get('generation_settings', {}))} keys")
    print(f"  - Validation settings: {len(defaults.get('validation_settings', {}))} keys")
    print()

    return True


def test_get_specific_settings():
    """Test getting specific settings."""
    print("Test 2: Get specific settings")
    print("-" * 60)

    loader = ConfigLoader()

    max_bullets = loader.get_quality_setting("max_bullets_per_slide")
    print(f"✓ max_bullets_per_slide: {max_bullets}")

    default_theme = loader.get_generation_setting("default_theme")
    print(f"✓ default_theme: {default_theme}")

    run_validation = loader.get_validation_setting("run_structure_validation")
    print(f"✓ run_structure_validation: {run_validation}")
    print()

    return True


def test_config_merge():
    """Test configuration merging."""
    print("Test 3: Configuration merging")
    print("-" * 60)

    loader = ConfigLoader()

    base = {
        "quality_settings": {
            "max_bullets_per_slide": 6,
            "max_words_per_bullet": 6
        },
        "generation_settings": {
            "default_theme": "corporate"
        }
    }

    override = {
        "quality_settings": {
            "max_bullets_per_slide": 5  # Override this
            # max_words_per_bullet should remain 6
        },
        "generation_settings": {
            "include_date": False  # Add new key
        }
    }

    merged = loader.merge_configs(base, override)

    assert merged["quality_settings"]["max_bullets_per_slide"] == 5, "Should use override value"
    assert merged["quality_settings"]["max_words_per_bullet"] == 6, "Should preserve base value"
    assert merged["generation_settings"]["default_theme"] == "corporate", "Should preserve base value"
    assert merged["generation_settings"]["include_date"] == False, "Should add new key"

    print("✓ Deep merge works correctly")
    print(f"  - Overridden: max_bullets_per_slide = {merged['quality_settings']['max_bullets_per_slide']}")
    print(f"  - Preserved: max_words_per_bullet = {merged['quality_settings']['max_words_per_bullet']}")
    print(f"  - Added: include_date = {merged['generation_settings']['include_date']}")
    print()

    return True


def test_get_config():
    """Test getting full merged config."""
    print("Test 4: Get full merged configuration")
    print("-" * 60)

    loader = ConfigLoader()
    config = loader.get_config()

    assert isinstance(config, SlideforgeConfig), "Should return SlideforgeConfig instance"
    assert len(config.quality_settings) > 0, "Should have quality settings"
    assert len(config.generation_settings) > 0, "Should have generation settings"

    print(f"✓ Created SlideforgeConfig instance")
    print(f"  - Type: {type(config).__name__}")
    print(f"  - Quality settings: {len(config.quality_settings)} keys")
    print(f"  - Generation settings: {len(config.generation_settings)} keys")
    print()

    return True


def test_metadata_override():
    """Test presentation metadata overrides."""
    print("Test 5: Presentation metadata overrides")
    print("-" * 60)

    loader = ConfigLoader()

    # Test with metadata override
    metadata = {
        "theme": "dark_mode",
        "max_bullets_per_slide": 5
    }

    config = loader.get_config(presentation_metadata=metadata)

    assert config.generation_settings["default_theme"] == "dark_mode", "Should override theme"
    assert config.quality_settings["max_bullets_per_slide"] == 5, "Should override max bullets"

    print(f"✓ Metadata overrides applied correctly")
    print(f"  - Theme: {config.generation_settings['default_theme']}")
    print(f"  - Max bullets: {config.quality_settings['max_bullets_per_slide']}")
    print()

    return True


def test_config_validation():
    """Test configuration validation."""
    print("Test 6: Configuration validation")
    print("-" * 60)

    loader = ConfigLoader()

    # Create config with problematic values
    config = SlideforgeConfig(
        quality_settings={
            "max_bullets_per_slide": 10,  # Too high
            "max_words_per_bullet": 15,    # Too high
            "accessibility_requirements": {
                "color_contrast_minimum": 3.0  # Too low
            }
        },
        validation_settings={
            "run_structure_validation": False  # Disabled
        }
    )

    warnings = loader.validate_config(config)

    print(f"✓ Found {len(warnings)} validation warnings:")
    for i, warning in enumerate(warnings, 1):
        print(f"  {i}. {warning}")
    print()

    assert len(warnings) > 0, "Should find warnings for problematic values"

    return True


def test_config_dict_conversion():
    """Test config to dict conversion."""
    print("Test 7: Config to dict conversion")
    print("-" * 60)

    loader = ConfigLoader()
    config = loader.get_config()

    config_dict = config.to_dict()

    assert isinstance(config_dict, dict), "Should return dictionary"
    assert "quality_settings" in config_dict, "Should have quality_settings"
    assert "generation_settings" in config_dict, "Should have generation_settings"

    print(f"✓ Converted config to dictionary")
    print(f"  - Keys: {list(config_dict.keys())}")
    print()

    return True


def main():
    """Run all tests."""
    print("=" * 60)
    print("ConfigLoader Test Suite")
    print("=" * 60)
    print()

    tests = [
        test_load_defaults,
        test_get_specific_settings,
        test_config_merge,
        test_get_config,
        test_metadata_override,
        test_config_validation,
        test_config_dict_conversion
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
                print(f"✗ {test.__name__} failed")
        except Exception as e:
            failed += 1
            print(f"✗ {test.__name__} raised exception: {e}")
            import traceback
            traceback.print_exc()
        print()

    print("=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
