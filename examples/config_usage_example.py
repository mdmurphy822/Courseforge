#!/usr/bin/env python3
"""
Configuration System Usage Examples

This example demonstrates how to use the Slideforge configuration layering system.
"""

import sys
from pathlib import Path

# Add scripts directory to path
repo_root = Path(__file__).parent.parent
sys.path.insert(0, str(repo_root))

from scripts.utilities import ConfigLoader, SlideforgeConfig


def example_1_basic_usage():
    """Example 1: Basic configuration loading."""
    print("=" * 60)
    print("Example 1: Basic Configuration Loading")
    print("=" * 60)

    # Create a config loader
    loader = ConfigLoader()

    # Get merged configuration with defaults
    config = loader.get_config()

    # Access settings
    max_bullets = config.quality_settings["max_bullets_per_slide"]
    print(f"Max bullets per slide: {max_bullets}")

    default_theme = config.generation_settings["default_theme"]
    print(f"Default theme: {default_theme}")

    run_validation = config.validation_settings["run_structure_validation"]
    print(f"Run structure validation: {run_validation}")

    print()


def example_2_specific_settings():
    """Example 2: Get specific settings quickly."""
    print("=" * 60)
    print("Example 2: Get Specific Settings")
    print("=" * 60)

    loader = ConfigLoader()

    # Quick access to specific settings without loading full config
    max_bullets = loader.get_quality_setting("max_bullets_per_slide")
    print(f"Max bullets per slide: {max_bullets}")

    min_notes_length = loader.get_quality_setting("minimum_speaker_notes_length")
    print(f"Minimum speaker notes length: {min_notes_length}")

    default_template = loader.get_generation_setting("default_template")
    print(f"Default template: {default_template}")

    print()


def example_3_project_overrides():
    """Example 3: Project-specific configuration."""
    print("=" * 60)
    print("Example 3: Project-Specific Configuration")
    print("=" * 60)

    # In a real scenario, you would have a project directory with config.json
    # For demonstration, we'll show how it would work

    loader = ConfigLoader()

    # Example project config override (would be in project_folder/config.json)
    project_overrides = {
        "quality_settings": {
            "max_bullets_per_slide": 5,  # Stricter than default
            "require_speaker_notes": True
        },
        "generation_settings": {
            "default_theme": "minimal",
            "include_slide_numbers": False
        }
    }

    print("Project overrides:")
    print(f"  - Max bullets: {project_overrides['quality_settings']['max_bullets_per_slide']}")
    print(f"  - Theme: {project_overrides['generation_settings']['default_theme']}")
    print()


def example_4_presentation_metadata():
    """Example 4: Presentation-specific overrides."""
    print("=" * 60)
    print("Example 4: Presentation-Specific Overrides")
    print("=" * 60)

    loader = ConfigLoader()

    # Presentation metadata can override settings
    presentation_metadata = {
        "theme": "corporate_dark",
        "template_path": "templates/pptx/themes/dark.pptx",
        "max_bullets_per_slide": 4
    }

    # Get config with metadata overrides
    config = loader.get_config(presentation_metadata=presentation_metadata)

    print(f"Effective theme: {config.generation_settings['default_theme']}")
    print(f"Max bullets: {config.quality_settings['max_bullets_per_slide']}")

    print()


def example_5_validation():
    """Example 5: Configuration validation."""
    print("=" * 60)
    print("Example 5: Configuration Validation")
    print("=" * 60)

    loader = ConfigLoader()

    # Create a config with some problematic values
    config = SlideforgeConfig(
        quality_settings={
            "max_bullets_per_slide": 12,  # Too high
            "max_words_per_bullet": 20,    # Too high
            "accessibility_requirements": {
                "color_contrast_minimum": 3.0  # Below WCAG AA
            }
        }
    )

    # Validate the configuration
    warnings = loader.validate_config(config)

    if warnings:
        print(f"Configuration has {len(warnings)} warnings:")
        for i, warning in enumerate(warnings, 1):
            print(f"  {i}. {warning}")
    else:
        print("Configuration is valid!")

    print()


def example_6_layered_config():
    """Example 6: Full layered configuration."""
    print("=" * 60)
    print("Example 6: Full Layered Configuration")
    print("=" * 60)

    loader = ConfigLoader()

    # Layer 1: Global defaults (automatically loaded)
    defaults = loader.load_defaults()
    print(f"Layer 1 (Defaults): max_bullets = {defaults['quality_settings']['max_bullets_per_slide']}")

    # Layer 2: Project overrides (simulated)
    project_overrides = {
        "quality_settings": {
            "max_bullets_per_slide": 5
        }
    }
    print(f"Layer 2 (Project): max_bullets = {project_overrides['quality_settings']['max_bullets_per_slide']}")

    # Layer 3: Presentation metadata overrides
    presentation_metadata = {
        "max_bullets_per_slide": 4
    }
    print(f"Layer 3 (Presentation): max_bullets = {presentation_metadata['max_bullets_per_slide']}")

    # Get final merged config
    config = loader.get_config(presentation_metadata=presentation_metadata)
    print(f"\nFinal merged: max_bullets = {config.quality_settings['max_bullets_per_slide']}")
    print("(Presentation metadata takes precedence)")

    print()


def example_7_custom_config():
    """Example 7: Creating and using custom configuration."""
    print("=" * 60)
    print("Example 7: Custom Configuration")
    print("=" * 60)

    # Create a custom configuration
    config = SlideforgeConfig(
        quality_settings={
            "max_bullets_per_slide": 5,
            "max_words_per_bullet": 8,
            "require_speaker_notes": True,
            "minimum_speaker_notes_length": 100
        },
        generation_settings={
            "default_theme": "academic",
            "include_slide_numbers": True,
            "generate_section_headers": True
        },
        validation_settings={
            "run_structure_validation": True,
            "fail_on_warnings": False,
            "minimum_quality_score": 0.8
        }
    )

    # Use the custom config
    print(f"Max bullets: {config.quality_settings['max_bullets_per_slide']}")
    print(f"Theme: {config.generation_settings['default_theme']}")
    print(f"Quality score threshold: {config.validation_settings['minimum_quality_score']}")

    # Convert to dict for saving
    config_dict = config.to_dict()
    print(f"\nConfig sections: {list(config_dict.keys())}")

    print()


def example_8_practical_usage():
    """Example 8: Practical usage in a script."""
    print("=" * 60)
    print("Example 8: Practical Script Usage")
    print("=" * 60)

    # This is how you would use the config loader in an actual script

    loader = ConfigLoader()

    # Load config for a specific project
    # project_path = Path("exports/20251217_myproject")
    # config = loader.get_config(project_path=project_path)

    # Or with presentation metadata
    presentation_data = {
        "metadata": {
            "title": "My Presentation",
            "author": "Author Name"
        },
        "theme": {
            "template_path": "templates/pptx/themes/corporate.pptx"
        }
    }

    config = loader.get_config(
        presentation_metadata=presentation_data.get("theme", {})
    )

    # Use config values in your script
    print("Script configuration:")
    print(f"  - Max bullets: {config.quality_settings['max_bullets_per_slide']}")
    print(f"  - Max words per bullet: {config.quality_settings['max_words_per_bullet']}")
    print(f"  - Default theme: {config.generation_settings['default_theme']}")
    print(f"  - Validate structure: {config.validation_settings['run_structure_validation']}")

    # Validation
    warnings = loader.validate_config(config)
    if warnings:
        print(f"\nConfiguration warnings: {len(warnings)}")
        for warning in warnings:
            print(f"  - {warning}")
    else:
        print("\n✓ Configuration is valid")

    print()


def main():
    """Run all examples."""
    print()
    print("*" * 60)
    print("Slideforge Configuration System - Usage Examples")
    print("*" * 60)
    print()

    example_1_basic_usage()
    example_2_specific_settings()
    example_3_project_overrides()
    example_4_presentation_metadata()
    example_5_validation()
    example_6_layered_config()
    example_7_custom_config()
    example_8_practical_usage()

    print("*" * 60)
    print("Examples complete!")
    print("*" * 60)


if __name__ == "__main__":
    main()
