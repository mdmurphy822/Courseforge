"""
Configuration Loader for Slideforge

Implements a layered configuration system inspired by LibV2 patterns:
1. Global defaults (schemas/presentation/defaults.json)
2. Project overrides (project_folder/config.json)
3. Presentation overrides (presentation metadata)

Usage:
    from utilities import ConfigLoader

    config = ConfigLoader()
    project_config = config.get_config(
        project_path=Path("exports/20251217_project"),
        presentation_metadata={"theme": "dark_mode"}
    )

    max_bullets = config.get_quality_setting("max_bullets_per_slide")
"""

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Any, Optional, List
from copy import deepcopy


@dataclass
class SlideforgeConfig:
    """
    Slideforge configuration container.

    Attributes:
        quality_settings: Quality standards and constraints
        generation_settings: Default generation options
        validation_settings: Validation behavior and thresholds
        transformation_settings: Content transformation rules
        content_profiling: Content analysis settings
        output_settings: Output file handling
        performance_settings: Performance optimization
        logging_settings: Logging configuration
    """
    quality_settings: Dict[str, Any] = field(default_factory=dict)
    generation_settings: Dict[str, Any] = field(default_factory=dict)
    validation_settings: Dict[str, Any] = field(default_factory=dict)
    transformation_settings: Dict[str, Any] = field(default_factory=dict)
    content_profiling: Dict[str, Any] = field(default_factory=dict)
    output_settings: Dict[str, Any] = field(default_factory=dict)
    performance_settings: Dict[str, Any] = field(default_factory=dict)
    logging_settings: Dict[str, Any] = field(default_factory=dict)

    def get(self, section: str, key: str, default: Any = None) -> Any:
        """
        Get a specific configuration value.

        Args:
            section: Configuration section name
            key: Setting key within section
            default: Default value if not found

        Returns:
            Configuration value or default

        Example:
            >>> config.get("quality_settings", "max_bullets_per_slide", 6)
            6
        """
        section_dict = getattr(self, section, {})
        return section_dict.get(key, default)

    def set(self, section: str, key: str, value: Any) -> None:
        """
        Set a specific configuration value.

        Args:
            section: Configuration section name
            key: Setting key within section
            value: Value to set
        """
        section_dict = getattr(self, section, {})
        section_dict[key] = value

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert configuration to dictionary.

        Returns:
            Dictionary representation of config
        """
        return {
            'quality_settings': self.quality_settings,
            'generation_settings': self.generation_settings,
            'validation_settings': self.validation_settings,
            'transformation_settings': self.transformation_settings,
            'content_profiling': self.content_profiling,
            'output_settings': self.output_settings,
            'performance_settings': self.performance_settings,
            'logging_settings': self.logging_settings
        }


class ConfigLoader:
    """
    Load and merge Slideforge configurations with layering support.

    Configuration layers (in order of precedence, lowest to highest):
    1. Global defaults (schemas/presentation/defaults.json)
    2. Project overrides (project_folder/config.json)
    3. Presentation metadata overrides

    Attributes:
        repo_root: Path to repository root
        defaults_path: Path to global defaults file
        _defaults_cache: Cached defaults to avoid repeated file reads
    """

    def __init__(self, repo_root: Optional[Path] = None):
        """
        Initialize configuration loader.

        Args:
            repo_root: Path to repository root (auto-detected if None)
        """
        from .common import get_slideforge_root

        self.repo_root = repo_root or get_slideforge_root()
        self.defaults_path = self.repo_root / "schemas" / "presentation" / "defaults.json"
        self._defaults_cache: Optional[Dict[str, Any]] = None

    def load_defaults(self) -> Dict[str, Any]:
        """
        Load global default configuration.

        Returns:
            Dictionary of default settings

        Raises:
            FileNotFoundError: If defaults.json not found
            json.JSONDecodeError: If defaults.json is invalid JSON
        """
        # Return cached defaults if available
        if self._defaults_cache is not None:
            return deepcopy(self._defaults_cache)

        if not self.defaults_path.exists():
            raise FileNotFoundError(
                f"Global defaults not found: {self.defaults_path}\n"
                "Expected location: schemas/presentation/defaults.json"
            )

        try:
            with open(self.defaults_path, 'r', encoding='utf-8') as f:
                defaults = json.load(f)

            # Cache the defaults
            self._defaults_cache = deepcopy(defaults)
            return defaults

        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(
                f"Invalid JSON in defaults file: {self.defaults_path}",
                e.doc,
                e.pos
            )

    def load_project_config(self, project_path: Path) -> Dict[str, Any]:
        """
        Load project-specific configuration overrides.

        Args:
            project_path: Path to project directory

        Returns:
            Dictionary of project settings (empty if no config file)
        """
        config_path = project_path / "config.json"

        if not config_path.exists():
            return {}

        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            # Log warning but don't fail - just use defaults
            print(f"Warning: Could not load project config from {config_path}: {e}")
            return {}

    def merge_configs(self, *configs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deep merge multiple configuration dictionaries.

        Later configurations override earlier ones. Nested dictionaries
        are merged recursively.

        Args:
            *configs: Variable number of config dictionaries to merge

        Returns:
            Merged configuration dictionary

        Example:
            >>> base = {"quality_settings": {"max_bullets": 6}}
            >>> override = {"quality_settings": {"max_bullets": 5}}
            >>> merged = loader.merge_configs(base, override)
            >>> merged["quality_settings"]["max_bullets"]
            5
        """
        result = {}

        for config in configs:
            if not config:
                continue

            result = self._deep_merge(result, config)

        return result

    def _deep_merge(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """
        Recursively merge two dictionaries.

        Args:
            base: Base dictionary
            override: Override dictionary

        Returns:
            Merged dictionary
        """
        result = deepcopy(base)

        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                # Recursively merge nested dictionaries
                result[key] = self._deep_merge(result[key], value)
            else:
                # Override the value
                result[key] = deepcopy(value)

        return result

    def get_config(
        self,
        project_path: Optional[Path] = None,
        presentation_metadata: Optional[Dict] = None
    ) -> SlideforgeConfig:
        """
        Get merged configuration with all layers applied.

        Args:
            project_path: Optional path to project directory
            presentation_metadata: Optional presentation-specific overrides

        Returns:
            SlideforgeConfig with merged settings

        Example:
            >>> config = loader.get_config(
            ...     project_path=Path("exports/20251217_project"),
            ...     presentation_metadata={"theme": "dark_mode"}
            ... )
        """
        # Start with defaults
        configs_to_merge = [self.load_defaults()]

        # Add project config if provided
        if project_path is not None and project_path.exists():
            project_config = self.load_project_config(project_path)
            if project_config:
                configs_to_merge.append(project_config)

        # Add presentation metadata overrides if provided
        if presentation_metadata:
            # Convert presentation metadata to config format
            metadata_config = self._metadata_to_config(presentation_metadata)
            if metadata_config:
                configs_to_merge.append(metadata_config)

        # Merge all configs
        merged = self.merge_configs(*configs_to_merge)

        # Create SlideforgeConfig from merged dict
        return SlideforgeConfig(
            quality_settings=merged.get('quality_settings', {}),
            generation_settings=merged.get('generation_settings', {}),
            validation_settings=merged.get('validation_settings', {}),
            transformation_settings=merged.get('transformation_settings', {}),
            content_profiling=merged.get('content_profiling', {}),
            output_settings=merged.get('output_settings', {}),
            performance_settings=merged.get('performance_settings', {}),
            logging_settings=merged.get('logging_settings', {})
        )

    def _metadata_to_config(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert presentation metadata to configuration overrides.

        Maps common metadata fields to configuration settings.

        Args:
            metadata: Presentation metadata dictionary

        Returns:
            Configuration dictionary
        """
        config = {}

        # Map theme to generation settings
        if 'theme' in metadata:
            config.setdefault('generation_settings', {})
            config['generation_settings']['default_theme'] = metadata['theme']

        # Map template_path to generation settings
        if 'template_path' in metadata:
            config.setdefault('generation_settings', {})
            config['generation_settings']['default_template'] = metadata['template_path']

        # Map quality overrides
        quality_keys = ['max_bullets_per_slide', 'max_words_per_bullet', 'require_speaker_notes']
        for key in quality_keys:
            if key in metadata:
                config.setdefault('quality_settings', {})
                config['quality_settings'][key] = metadata[key]

        return config

    def get_quality_setting(self, key: str, default: Any = None) -> Any:
        """
        Get a specific quality setting from defaults.

        Args:
            key: Setting key
            default: Default value if not found

        Returns:
            Setting value or default

        Example:
            >>> max_bullets = loader.get_quality_setting("max_bullets_per_slide", 6)
        """
        defaults = self.load_defaults()
        return defaults.get('quality_settings', {}).get(key, default)

    def get_generation_setting(self, key: str, default: Any = None) -> Any:
        """
        Get a specific generation setting from defaults.

        Args:
            key: Setting key
            default: Default value if not found

        Returns:
            Setting value or default
        """
        defaults = self.load_defaults()
        return defaults.get('generation_settings', {}).get(key, default)

    def get_validation_setting(self, key: str, default: Any = None) -> Any:
        """
        Get a specific validation setting from defaults.

        Args:
            key: Setting key
            default: Default value if not found

        Returns:
            Setting value or default
        """
        defaults = self.load_defaults()
        return defaults.get('validation_settings', {}).get(key, default)

    def save_project_config(self, project_path: Path, config: SlideforgeConfig) -> None:
        """
        Save configuration to project directory.

        Args:
            project_path: Path to project directory
            config: Configuration to save

        Raises:
            IOError: If config cannot be saved
        """
        config_path = project_path / "config.json"

        # Ensure project directory exists
        project_path.mkdir(parents=True, exist_ok=True)

        # Save config as JSON
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config.to_dict(), f, indent=2)
        except IOError as e:
            raise IOError(f"Failed to save config to {config_path}: {e}")

    def validate_config(self, config: SlideforgeConfig) -> List[str]:
        """
        Validate configuration for common issues.

        Args:
            config: Configuration to validate

        Returns:
            List of validation warnings (empty if valid)
        """
        warnings = []

        # Check quality settings
        max_bullets = config.quality_settings.get('max_bullets_per_slide', 6)
        if max_bullets > 8:
            warnings.append(
                f"max_bullets_per_slide is {max_bullets}, "
                "which exceeds recommended maximum of 8"
            )

        max_words = config.quality_settings.get('max_words_per_bullet', 6)
        if max_words > 10:
            warnings.append(
                f"max_words_per_bullet is {max_words}, "
                "which exceeds recommended maximum of 10"
            )

        # Check accessibility requirements
        contrast = config.quality_settings.get('accessibility_requirements', {}).get(
            'color_contrast_minimum', 4.5
        )
        if contrast < 4.5:
            warnings.append(
                f"color_contrast_minimum is {contrast}, "
                "which is below WCAG AA standard of 4.5"
            )

        # Check validation settings
        if not config.validation_settings.get('run_structure_validation', True):
            warnings.append("Structure validation is disabled - may produce invalid presentations")

        return warnings


def create_default_project_config(project_path: Path) -> None:
    """
    Create a default project configuration file.

    Args:
        project_path: Path to project directory
    """
    loader = ConfigLoader()
    config = loader.get_config()
    loader.save_project_config(project_path, config)
