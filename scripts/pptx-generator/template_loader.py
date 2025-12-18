#!/usr/bin/env python3
"""
Template Loader - Discovers and loads PPTX master templates.

This module handles:
- Loading templates from the masters/ directory
- Discovering custom templates in the custom/ directory
- Parsing registry.json for template metadata
- Validating template structure and layouts
- Providing theme colors and layout mappings

Usage:
    from template_loader import TemplateLoader

    loader = TemplateLoader()
    template_path, config = loader.get_template("corporate")
    # or
    template_path, config = loader.get_template("custom/my_brand.pptx")
"""

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


@dataclass
class TemplateColors:
    """Color configuration from a template."""
    primary: str = "#2c5aa0"
    secondary: str = "#4a4a4a"
    accent: str = "#28a745"
    background: str = "#ffffff"
    surface: str = "#f8f9fa"
    text_primary: str = "#333333"
    text_secondary: str = "#666666"
    success: str = "#28a745"
    warning: str = "#ffc107"
    info: str = "#17a2b8"

    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> "TemplateColors":
        """Create TemplateColors from dictionary."""
        return cls(
            primary=data.get("primary", cls.primary),
            secondary=data.get("secondary", cls.secondary),
            accent=data.get("accent", cls.accent),
            background=data.get("background", cls.background),
            surface=data.get("surface", cls.surface),
            text_primary=data.get("text_primary", cls.text_primary),
            text_secondary=data.get("text_secondary", cls.text_secondary),
            success=data.get("success", cls.success),
            warning=data.get("warning", cls.warning),
            info=data.get("info", cls.info),
        )


@dataclass
class TemplateConfig:
    """Configuration for a single template."""
    id: str
    name: str
    path: Path
    description: str = ""
    category: str = "general"
    colors: TemplateColors = field(default_factory=TemplateColors)
    fonts: Dict[str, str] = field(default_factory=lambda: {"heading": "Arial", "body": "Arial"})
    layouts: Dict[str, int] = field(default_factory=dict)
    is_custom: bool = False

    # Default layout indices (PowerPoint standard)
    DEFAULT_LAYOUTS = {
        "title": 0,
        "content": 1,
        "section_header": 2,
        "two_content": 3,
        "comparison": 4,
        "title_only": 5,
        "blank": 6,
        "image": 1,
        "quote": 5,
    }

    def get_layout_index(self, layout_type: str) -> int:
        """Get the layout index for a given type, with fallback to defaults."""
        if layout_type in self.layouts:
            return self.layouts[layout_type]
        return self.DEFAULT_LAYOUTS.get(layout_type, 1)


class TemplateLoader:
    """
    Loads and manages PPTX templates.

    Handles both built-in templates (from masters/) and custom templates
    (from custom/ directory or user-specified paths).
    """

    def __init__(self, base_path: Optional[Path] = None):
        """
        Initialize the template loader.

        Args:
            base_path: Base path to templates directory. If None, uses default location.
        """
        if base_path is None:
            # Default: relative to this script
            script_dir = Path(__file__).parent
            self.base_path = script_dir.parent.parent / "templates" / "pptx"
        else:
            self.base_path = Path(base_path)

        self.masters_path = self.base_path / "masters"
        self.custom_path = self.base_path / "custom"
        self.registry_path = self.masters_path / "registry.json"

        self._registry: Dict[str, Any] = {}
        self._templates: Dict[str, TemplateConfig] = {}

        self._load_registry()
        self._discover_custom_templates()

    def _load_registry(self) -> None:
        """Load the template registry from registry.json."""
        if not self.registry_path.exists():
            logger.warning(f"Registry not found: {self.registry_path}")
            return

        try:
            with open(self.registry_path, "r", encoding="utf-8") as f:
                self._registry = json.load(f)

            # Parse templates from registry
            for template_id, config in self._registry.get("templates", {}).items():
                template_path = self.masters_path / config.get("path", f"{template_id}.pptx")

                colors = TemplateColors.from_dict(config.get("colors", {}))

                self._templates[template_id] = TemplateConfig(
                    id=template_id,
                    name=config.get("name", template_id.replace("_", " ").title()),
                    path=template_path,
                    description=config.get("description", ""),
                    category=config.get("category", "general"),
                    colors=colors,
                    fonts=config.get("fonts", {"heading": "Arial", "body": "Arial"}),
                    layouts=config.get("layouts", {}),
                    is_custom=False,
                )

            logger.info(f"Loaded {len(self._templates)} templates from registry")

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse registry: {e}")
        except Exception as e:
            logger.error(f"Error loading registry: {e}")

    def _discover_custom_templates(self) -> None:
        """Discover custom templates in the custom/ directory."""
        if not self.custom_path.exists():
            return

        for pptx_file in self.custom_path.glob("*.pptx"):
            template_id = f"custom/{pptx_file.stem}"

            # Skip if already in registry
            if template_id in self._templates:
                continue

            self._templates[template_id] = TemplateConfig(
                id=template_id,
                name=pptx_file.stem.replace("_", " ").title(),
                path=pptx_file,
                description=f"Custom template: {pptx_file.name}",
                category="custom",
                is_custom=True,
            )

        custom_count = sum(1 for t in self._templates.values() if t.is_custom)
        if custom_count > 0:
            logger.info(f"Discovered {custom_count} custom templates")

    def list_templates(self) -> List[TemplateConfig]:
        """Get a list of all available templates."""
        return list(self._templates.values())

    def list_template_names(self) -> List[str]:
        """Get a list of all template IDs."""
        return list(self._templates.keys())

    def get_default_template(self) -> str:
        """Get the default template ID."""
        return self._registry.get("default_template", "corporate")

    def has_template(self, template_id: str) -> bool:
        """Check if a template exists."""
        # Check direct ID match
        if template_id in self._templates:
            return True

        # Check if it's a path to a file
        template_path = Path(template_id)
        if template_path.exists() and template_path.suffix == ".pptx":
            return True

        # Check relative to base path
        full_path = self.base_path / template_id
        if full_path.exists() and full_path.suffix == ".pptx":
            return True

        return False

    def get_template(self, template_id: str) -> Tuple[Optional[Path], TemplateConfig]:
        """
        Get a template by ID or path.

        Args:
            template_id: Template ID (e.g., "corporate") or path (e.g., "custom/my_brand.pptx")

        Returns:
            Tuple of (template_path, config). Path may be None if template file doesn't exist.
        """
        # Direct ID match
        if template_id in self._templates:
            config = self._templates[template_id]
            path = config.path if config.path.exists() else None
            return path, config

        # Path to file
        template_path = Path(template_id)
        if template_path.exists() and template_path.suffix == ".pptx":
            return template_path, TemplateConfig(
                id=template_path.stem,
                name=template_path.stem.replace("_", " ").title(),
                path=template_path,
                is_custom=True,
            )

        # Relative to base path
        full_path = self.base_path / template_id
        if full_path.exists() and full_path.suffix == ".pptx":
            return full_path, TemplateConfig(
                id=full_path.stem,
                name=full_path.stem.replace("_", " ").title(),
                path=full_path,
                is_custom=True,
            )

        # Not found - return config with no path
        logger.warning(f"Template not found: {template_id}")
        return None, TemplateConfig(
            id=template_id,
            name=template_id,
            path=Path(template_id),
        )

    def get_template_colors(self, template_id: str) -> TemplateColors:
        """Get colors for a template."""
        _, config = self.get_template(template_id)
        return config.colors

    def get_layout_index(self, template_id: str, layout_type: str) -> int:
        """Get the layout index for a template and layout type."""
        _, config = self.get_template(template_id)
        return config.get_layout_index(layout_type)

    def validate_template(self, template_path: Path) -> Tuple[bool, List[str]]:
        """
        Validate a template file.

        Args:
            template_path: Path to PPTX file

        Returns:
            Tuple of (is_valid, list of issues)
        """
        issues = []

        if not template_path.exists():
            issues.append(f"Template file not found: {template_path}")
            return False, issues

        if template_path.suffix != ".pptx":
            issues.append(f"Invalid file type: {template_path.suffix}")
            return False, issues

        try:
            from pptx import Presentation
            prs = Presentation(str(template_path))

            # Check layout count
            layout_count = len(prs.slide_layouts)
            if layout_count < 7:
                issues.append(f"Template has only {layout_count} layouts (need at least 7)")

            # Check for required layouts by testing indices
            required_indices = [0, 1, 2, 3, 4, 5, 6]
            for idx in required_indices:
                if idx >= layout_count:
                    issues.append(f"Missing layout at index {idx}")

        except Exception as e:
            issues.append(f"Error loading template: {e}")
            return False, issues

        return len(issues) == 0, issues


def get_template_catalog() -> Dict[str, Dict[str, Any]]:
    """
    Get a catalog of all available templates.

    Returns dictionary suitable for display or API response.
    """
    loader = TemplateLoader()
    catalog = {}

    for template in loader.list_templates():
        catalog[template.id] = {
            "name": template.name,
            "description": template.description,
            "category": template.category,
            "is_custom": template.is_custom,
            "colors": {
                "primary": template.colors.primary,
                "secondary": template.colors.secondary,
                "accent": template.colors.accent,
                "background": template.colors.background,
            },
            "fonts": template.fonts,
            "available": template.path.exists() if template.path else False,
        }

    return catalog


if __name__ == "__main__":
    # Test the loader
    logging.basicConfig(level=logging.INFO)

    loader = TemplateLoader()

    print("\n=== Available Templates ===")
    for template in loader.list_templates():
        status = "OK" if template.path.exists() else "MISSING"
        print(f"  [{status}] {template.id}: {template.name}")
        print(f"         Category: {template.category}")
        print(f"         Primary color: {template.colors.primary}")

    print(f"\nDefault template: {loader.get_default_template()}")
