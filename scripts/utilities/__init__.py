# Utilities Module
# Shared utilities for Slideforge scripts

"""
This module provides shared utility functions used across Slideforge
scripts including file handling, logging configuration, and common
validation helpers.
"""

from pathlib import Path

# Import ValidationResult and related classes
from .validation_result import (
    ValidationResult,
    ValidationIssue,
    ValidationSeverity,
    create_file_validation_result,
    create_schema_validation_result
)

# Import common utility functions
from .common import (
    generate_slug,
    ensure_unique_slug,
    get_repo_root,
    get_slideforge_root,
    validate_file_exists,
    validate_directory_exists,
    sanitize_filename,
    find_files_by_pattern,
    get_relative_path,
    ensure_output_directory,
    read_text_file,
    get_file_size_mb,
    validate_project_structure
)

# Import configuration loader
from .config_loader import (
    ConfigLoader,
    SlideforgeConfig,
    create_default_project_config
)

__version__ = "1.0.0"

__all__ = [
    # ValidationResult classes and functions
    "ValidationResult",
    "ValidationIssue",
    "ValidationSeverity",
    "create_file_validation_result",
    "create_schema_validation_result",
    # Common utility functions
    "generate_slug",
    "ensure_unique_slug",
    "get_repo_root",
    "get_slideforge_root",
    "validate_file_exists",
    "validate_directory_exists",
    "sanitize_filename",
    "find_files_by_pattern",
    "get_relative_path",
    "ensure_output_directory",
    "read_text_file",
    "get_file_size_mb",
    "validate_project_structure",
    # Configuration loader
    "ConfigLoader",
    "SlideforgeConfig",
    "create_default_project_config",
]
