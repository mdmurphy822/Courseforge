# Slideforge Configuration System

The Slideforge configuration system provides a flexible, layered approach to managing presentation generation settings. Inspired by LibV2 patterns, it allows defaults, project-specific overrides, and presentation-specific customization.

---

## Overview

### Configuration Layers

The system uses three layers of configuration (in order of precedence, lowest to highest):

1. **Global Defaults** (`schemas/presentation/defaults.json`)
   - Base configuration for all presentations
   - Defines quality standards, generation settings, validation rules
   - Maintained in version control

2. **Project Overrides** (`project_folder/config.json`)
   - Project-specific settings
   - Override global defaults for specific projects
   - Optional - if missing, only global defaults are used

3. **Presentation Metadata** (passed at runtime)
   - Presentation-specific overrides
   - Highest precedence - overrides both defaults and project settings
   - Useful for one-off customizations

### Configuration Sections

The configuration is organized into eight sections:

- **quality_settings**: Quality standards (max bullets, words, accessibility)
- **generation_settings**: Default generation options (theme, template, format)
- **validation_settings**: Validation behavior and thresholds
- **transformation_settings**: Content transformation rules
- **content_profiling**: Content analysis settings
- **output_settings**: Output file handling
- **performance_settings**: Performance optimization
- **logging_settings**: Logging configuration

---

## Quick Start

### Basic Usage

```python
from scripts.utilities import ConfigLoader

# Create a config loader
loader = ConfigLoader()

# Get merged configuration with defaults
config = loader.get_config()

# Access settings
max_bullets = config.quality_settings["max_bullets_per_slide"]
default_theme = config.generation_settings["default_theme"]
```

### Get Specific Settings

```python
loader = ConfigLoader()

# Quick access without loading full config
max_bullets = loader.get_quality_setting("max_bullets_per_slide")
default_template = loader.get_generation_setting("default_template")
run_validation = loader.get_validation_setting("run_structure_validation")
```

### Project-Specific Configuration

```python
from pathlib import Path

loader = ConfigLoader()

# Load config for a specific project
project_path = Path("exports/20251217_myproject")
config = loader.get_config(project_path=project_path)
```

### Presentation-Specific Overrides

```python
loader = ConfigLoader()

# Override settings for a specific presentation
presentation_metadata = {
    "theme": "corporate_dark",
    "max_bullets_per_slide": 4
}

config = loader.get_config(presentation_metadata=presentation_metadata)
```

---

## Configuration Reference

### Quality Settings

```json
{
  "quality_settings": {
    "max_bullets_per_slide": 6,
    "max_words_per_bullet": 6,
    "max_chars_per_bullet": 100,
    "require_speaker_notes": true,
    "minimum_speaker_notes_length": 50,
    "accessibility_requirements": {
      "alt_text_required": true,
      "color_contrast_minimum": 4.5,
      "minimum_font_size": 18,
      "require_slide_titles": true
    },
    "content_density": {
      "max_table_rows": 8,
      "max_table_columns": 6,
      "max_process_steps": 6,
      "max_timeline_events": 6,
      "max_cards_per_grid": 6,
      "max_stats_per_grid": 6
    }
  }
}
```

### Generation Settings

```json
{
  "generation_settings": {
    "default_theme": "corporate",
    "default_template": "corporate.pptx",
    "template_directory": "templates/pptx/themes",
    "aspect_ratio": "16:9",
    "note_style": "talking_points",
    "include_slide_numbers": true,
    "include_date": true,
    "generate_toc": false,
    "generate_section_headers": true,
    "generate_transitions": true,
    "default_font": {
      "family": "Arial",
      "heading_size": 32,
      "body_size": 24
    }
  }
}
```

### Validation Settings

```json
{
  "validation_settings": {
    "run_structure_validation": true,
    "run_schema_validation": true,
    "run_semantic_validation": true,
    "run_accessibility_validation": true,
    "fail_on_warnings": false,
    "fail_on_errors": true,
    "minimum_quality_score": 0.7,
    "validation_thresholds": {
      "critical_issues": 0,
      "high_issues": 3,
      "medium_issues": 10
    }
  }
}
```

### Transformation Settings

```json
{
  "transformation_settings": {
    "split_strategy": "semantic",
    "enable_content_splitting": true,
    "split_threshold_words": 60,
    "merge_short_sections": true,
    "min_section_size": 2,
    "generate_section_dividers": true,
    "importance_threshold": 0.3,
    "auto_layout_detection": true,
    "preserve_source_structure": true
  }
}
```

---

## Advanced Usage

### Configuration Merging

The system deep merges configurations, allowing fine-grained overrides:

```python
loader = ConfigLoader()

# Defaults set max_bullets to 6
# Project config overrides to 5
# Presentation metadata overrides to 4

config = loader.get_config(
    project_path=Path("exports/project"),
    presentation_metadata={"max_bullets_per_slide": 4}
)

# Result: 4 (presentation metadata takes precedence)
```

### Configuration Validation

Validate configurations to catch common issues:

```python
loader = ConfigLoader()
config = loader.get_config()

# Validate the configuration
warnings = loader.validate_config(config)

if warnings:
    print(f"Configuration has {len(warnings)} warnings:")
    for warning in warnings:
        print(f"  - {warning}")
```

### Custom Configuration

Create custom configurations programmatically:

```python
from scripts.utilities import SlideforgeConfig

config = SlideforgeConfig(
    quality_settings={
        "max_bullets_per_slide": 5,
        "max_words_per_bullet": 8
    },
    generation_settings={
        "default_theme": "academic",
        "include_slide_numbers": True
    }
)

# Use the custom config
max_bullets = config.quality_settings["max_bullets_per_slide"]

# Convert to dict for saving
config_dict = config.to_dict()
```

### Saving Project Configuration

Save configuration to a project directory:

```python
loader = ConfigLoader()
config = loader.get_config(presentation_metadata={"theme": "dark_mode"})

# Save to project
project_path = Path("exports/20251217_project")
loader.save_project_config(project_path, config)
# Creates: exports/20251217_project/config.json
```

---

## Project Configuration File

To create a project-specific configuration, create `config.json` in your project directory:

```json
{
  "quality_settings": {
    "max_bullets_per_slide": 5,
    "require_speaker_notes": true
  },
  "generation_settings": {
    "default_theme": "minimal",
    "include_slide_numbers": false
  },
  "validation_settings": {
    "minimum_quality_score": 0.8
  }
}
```

The system will automatically load and merge this with global defaults.

---

## Common Patterns

### Pattern 1: Strict Quality Standards

```python
# For presentations requiring high quality standards
strict_metadata = {
    "max_bullets_per_slide": 4,
    "max_words_per_bullet": 5,
    "require_speaker_notes": True,
    "minimum_speaker_notes_length": 100
}

config = loader.get_config(presentation_metadata=strict_metadata)
```

### Pattern 2: Minimal Validation

```python
# For quick prototypes or drafts
minimal_validation = {
    "run_semantic_validation": False,
    "fail_on_warnings": False,
    "minimum_quality_score": 0.5
}

config = loader.get_config(presentation_metadata=minimal_validation)
```

### Pattern 3: Custom Theme

```python
# Apply a custom theme
custom_theme = {
    "theme": "corporate_dark",
    "template_path": "templates/pptx/themes/dark.pptx",
    "default_font": {
        "family": "Calibri",
        "heading_size": 36,
        "body_size": 22
    }
}

config = loader.get_config(presentation_metadata=custom_theme)
```

---

## Integration with Scripts

### In Generation Scripts

```python
from pathlib import Path
from scripts.utilities import ConfigLoader

def generate_presentation(input_file: Path, output_dir: Path):
    """Generate presentation with configuration."""

    # Load configuration
    loader = ConfigLoader()
    config = loader.get_config(project_path=output_dir)

    # Use config values
    max_bullets = config.quality_settings["max_bullets_per_slide"]
    default_theme = config.generation_settings["default_theme"]

    # Generate presentation with these settings
    # ...

    # Validate configuration
    warnings = loader.validate_config(config)
    if warnings:
        print("Configuration warnings:")
        for warning in warnings:
            print(f"  - {warning}")
```

### In Validation Scripts

```python
from scripts.utilities import ConfigLoader

def validate_presentation(presentation_path: Path):
    """Validate presentation against quality standards."""

    loader = ConfigLoader()
    config = loader.get_config()

    # Get quality thresholds
    max_bullets = config.quality_settings["max_bullets_per_slide"]
    max_words = config.quality_settings["max_words_per_bullet"]

    # Perform validation
    issues = []

    # Check each slide against thresholds
    # ...

    return issues
```

---

## Best Practices

1. **Keep Defaults Generic**: Global defaults should work for most presentations
2. **Use Project Configs for Consistency**: When multiple presentations share settings, use project configs
3. **Use Metadata for One-Offs**: For single presentation customizations, use metadata overrides
4. **Validate Before Use**: Always validate configurations to catch issues early
5. **Document Custom Settings**: If overriding defaults, document why in project README
6. **Test Configuration Changes**: When modifying defaults, test with existing projects

---

## API Reference

### ConfigLoader Class

#### `__init__(repo_root: Optional[Path] = None)`

Initialize configuration loader.

**Parameters:**
- `repo_root`: Path to repository root (auto-detected if None)

#### `load_defaults() -> Dict[str, Any]`

Load global default configuration from `schemas/presentation/defaults.json`.

**Returns:** Dictionary of default settings

**Raises:**
- `FileNotFoundError`: If defaults.json not found
- `json.JSONDecodeError`: If defaults.json is invalid

#### `get_config(project_path: Optional[Path] = None, presentation_metadata: Optional[Dict] = None) -> SlideforgeConfig`

Get merged configuration with all layers applied.

**Parameters:**
- `project_path`: Optional path to project directory
- `presentation_metadata`: Optional presentation-specific overrides

**Returns:** SlideforgeConfig with merged settings

#### `get_quality_setting(key: str, default: Any = None) -> Any`

Get a specific quality setting from defaults.

**Parameters:**
- `key`: Setting key
- `default`: Default value if not found

**Returns:** Setting value or default

#### `validate_config(config: SlideforgeConfig) -> List[str]`

Validate configuration for common issues.

**Parameters:**
- `config`: Configuration to validate

**Returns:** List of validation warnings (empty if valid)

### SlideforgeConfig Class

#### Attributes

- `quality_settings`: Dict[str, Any]
- `generation_settings`: Dict[str, Any]
- `validation_settings`: Dict[str, Any]
- `transformation_settings`: Dict[str, Any]
- `content_profiling`: Dict[str, Any]
- `output_settings`: Dict[str, Any]
- `performance_settings`: Dict[str, Any]
- `logging_settings`: Dict[str, Any]

#### `get(section: str, key: str, default: Any = None) -> Any`

Get a specific configuration value.

#### `set(section: str, key: str, value: Any) -> None`

Set a specific configuration value.

#### `to_dict() -> Dict[str, Any]`

Convert configuration to dictionary.

---

## Examples

Complete usage examples are available in:
- `/home/bacon/Desktop/Slideforge/examples/config_usage_example.py`

Run examples:
```bash
python3 examples/config_usage_example.py
```

---

## Troubleshooting

### Config File Not Found

**Error:** `FileNotFoundError: Global defaults not found`

**Solution:** Ensure `schemas/presentation/defaults.json` exists in repository root.

### Invalid JSON

**Error:** `json.JSONDecodeError: Invalid JSON in defaults file`

**Solution:** Validate JSON syntax using `python3 -m json.tool < schemas/presentation/defaults.json`

### Settings Not Applied

**Issue:** Overrides not taking effect

**Solution:** Check layer precedence - presentation metadata > project config > defaults

### Validation Warnings

**Issue:** Getting unexpected validation warnings

**Solution:** Review `validate_config()` output and adjust settings or thresholds accordingly

---

## Version History

- **v1.0.0** (2025-12-17): Initial release
  - Three-layer configuration system
  - Eight configuration sections
  - Validation support
  - Deep merge capabilities
