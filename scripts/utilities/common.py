"""
Common Utility Functions for Slideforge

Provides shared utility functions used across Slideforge scripts including:
- Slug generation for file naming
- Repository root detection
- File validation helpers
- Path manipulation utilities
"""

import re
from pathlib import Path
from typing import Optional, List
from .validation_result import ValidationResult


def generate_slug(title: str, max_length: int = 50) -> str:
    """
    Convert a title to a URL-safe slug.

    Args:
        title: Input title string
        max_length: Maximum length of the slug (default: 50)

    Returns:
        URL-safe slug string

    Example:
        >>> generate_slug("Introduction to Python Programming")
        'introduction-to-python-programming'
        >>> generate_slug("Module 1: Getting Started!", max_length=20)
        'module-1-getting'
    """
    # Convert to lowercase
    slug = title.lower()

    # Replace special characters and spaces with hyphens
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[-\s]+', '-', slug)

    # Remove leading/trailing hyphens
    slug = slug.strip('-')

    # Truncate to max_length
    if len(slug) > max_length:
        # Try to break at a hyphen near the limit
        truncated = slug[:max_length]
        last_hyphen = truncated.rfind('-')
        if last_hyphen > max_length * 0.7:  # Only break if hyphen is reasonably close
            slug = truncated[:last_hyphen]
        else:
            slug = truncated

    # Ensure it's not empty
    if not slug:
        slug = 'untitled'

    return slug


def ensure_unique_slug(slug: str, directory: Path, extension: str = "") -> str:
    """
    Ensure slug is unique by appending a number if necessary.

    Args:
        slug: Base slug string
        directory: Directory to check for existing files
        extension: File extension to check (e.g., ".json", ".pptx")

    Returns:
        Unique slug (may have number appended)

    Example:
        >>> ensure_unique_slug("presentation", Path("/exports"), ".pptx")
        'presentation-2'  # if presentation.pptx already exists
    """
    if not directory.exists():
        return slug

    # Check if base slug exists
    test_path = directory / f"{slug}{extension}"
    if not test_path.exists():
        return slug

    # Try numbered variants
    counter = 2
    while True:
        numbered_slug = f"{slug}-{counter}"
        test_path = directory / f"{numbered_slug}{extension}"
        if not test_path.exists():
            return numbered_slug
        counter += 1

        # Prevent infinite loops
        if counter > 9999:
            raise RuntimeError(f"Could not generate unique slug for '{slug}' after 9999 attempts")


def get_repo_root(start_path: Optional[Path] = None) -> Optional[Path]:
    """
    Find the repository root by looking for CLAUDE.md.

    Args:
        start_path: Starting path for search (default: current directory)

    Returns:
        Path to repository root, or None if not found

    Example:
        >>> root = get_repo_root()
        >>> if root:
        ...     print(f"Repository root: {root}")
    """
    current = start_path or Path.cwd()

    # Walk up the directory tree
    for parent in [current] + list(current.parents):
        claude_file = parent / "CLAUDE.md"
        if claude_file.exists():
            return parent

    return None


def get_slideforge_root() -> Path:
    """
    Get the Slideforge repository root.

    Returns:
        Path to Slideforge root

    Raises:
        RuntimeError: If repository root cannot be found
    """
    root = get_repo_root()
    if root is None:
        raise RuntimeError(
            "Could not find Slideforge repository root. "
            "Make sure CLAUDE.md exists in the repository root."
        )
    return root


def validate_file_exists(path: Path, file_type: str = "") -> ValidationResult:
    """
    Validate that a file exists and is readable.

    Args:
        path: Path to file
        file_type: Optional description of file type (e.g., "schema", "template")

    Returns:
        ValidationResult with appropriate errors or info

    Example:
        >>> result = validate_file_exists(Path("/path/to/schema.json"), "schema")
        >>> if not result.valid:
        ...     print(f"Schema validation failed: {result.errors}")
    """
    result = ValidationResult()
    result.context['file_path'] = str(path)
    result.context['file_type'] = file_type

    if not path.exists():
        file_desc = f"{file_type} file" if file_type else "File"
        result.add_error(
            f"{file_desc} not found: {path}",
            context={'path': str(path), 'exists': False}
        )
        return result

    if not path.is_file():
        result.add_error(
            f"Path is not a file: {path}",
            context={'path': str(path), 'is_file': False}
        )
        return result

    # Check if readable
    try:
        with open(path, 'r') as f:
            f.read(1)  # Try to read one byte
        result.add_info(f"File exists and is readable: {path}")
    except (PermissionError, IOError) as e:
        result.add_error(
            f"File is not readable: {path}",
            context={'path': str(path), 'error': str(e)}
        )

    return result


def validate_directory_exists(path: Path, create: bool = False) -> ValidationResult:
    """
    Validate that a directory exists, optionally creating it.

    Args:
        path: Path to directory
        create: If True, create directory if it doesn't exist

    Returns:
        ValidationResult
    """
    result = ValidationResult()
    result.context['directory_path'] = str(path)

    if not path.exists():
        if create:
            try:
                path.mkdir(parents=True, exist_ok=True)
                result.add_info(f"Created directory: {path}")
            except (PermissionError, OSError) as e:
                result.add_error(
                    f"Failed to create directory: {path}",
                    context={'path': str(path), 'error': str(e)}
                )
        else:
            result.add_error(
                f"Directory not found: {path}",
                context={'path': str(path), 'exists': False}
            )
    elif not path.is_dir():
        result.add_error(
            f"Path exists but is not a directory: {path}",
            context={'path': str(path), 'is_dir': False}
        )
    else:
        result.add_info(f"Directory exists: {path}")

    return result


def sanitize_filename(filename: str, max_length: int = 200) -> str:
    """
    Sanitize a filename by removing invalid characters.

    Args:
        filename: Input filename
        max_length: Maximum length for filename (default: 200)

    Returns:
        Sanitized filename

    Example:
        >>> sanitize_filename("My Presentation: Part 1.pptx")
        'My Presentation Part 1.pptx'
    """
    # Remove characters that are invalid in filenames
    # Keep alphanumeric, spaces, hyphens, underscores, periods
    sanitized = re.sub(r'[<>:"/\\|?*]', '', filename)

    # Remove control characters
    sanitized = re.sub(r'[\x00-\x1f\x7f]', '', sanitized)

    # Collapse multiple spaces
    sanitized = re.sub(r'\s+', ' ', sanitized)

    # Truncate to max_length
    if len(sanitized) > max_length:
        # Try to preserve extension
        parts = sanitized.rsplit('.', 1)
        if len(parts) == 2:
            name, ext = parts
            name = name[:max_length - len(ext) - 1]
            sanitized = f"{name}.{ext}"
        else:
            sanitized = sanitized[:max_length]

    return sanitized.strip()


def find_files_by_pattern(
    directory: Path,
    pattern: str,
    recursive: bool = False
) -> List[Path]:
    """
    Find files matching a glob pattern.

    Args:
        directory: Directory to search
        pattern: Glob pattern (e.g., "*.json", "**/*.pptx")
        recursive: If True, search recursively

    Returns:
        List of matching file paths

    Example:
        >>> files = find_files_by_pattern(Path("/exports"), "*.pptx")
        >>> for file in files:
        ...     print(f"Found: {file}")
    """
    if not directory.exists():
        return []

    if recursive:
        return sorted(directory.rglob(pattern))
    else:
        return sorted(directory.glob(pattern))


def get_relative_path(path: Path, base: Optional[Path] = None) -> Path:
    """
    Get relative path from base directory.

    Args:
        path: Path to make relative
        base: Base directory (default: repository root)

    Returns:
        Relative path

    Example:
        >>> rel = get_relative_path(Path("/repo/exports/proj1/output.pptx"))
        >>> print(rel)
        exports/proj1/output.pptx
    """
    if base is None:
        base = get_repo_root() or Path.cwd()

    try:
        return path.relative_to(base)
    except ValueError:
        # If path is not relative to base, return as-is
        return path


def ensure_output_directory(base_dir: Path, project_name: str) -> Path:
    """
    Create and return a unique project directory.

    Args:
        base_dir: Base exports directory
        project_name: Name of the project

    Returns:
        Path to created project directory

    Raises:
        RuntimeError: If directory cannot be created
    """
    from datetime import datetime

    # Generate timestamped directory name
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    slug = generate_slug(project_name, max_length=30)
    dir_name = f"{timestamp}_{slug}"

    output_dir = base_dir / dir_name

    # Ensure unique
    counter = 1
    while output_dir.exists():
        dir_name = f"{timestamp}_{slug}_{counter}"
        output_dir = base_dir / dir_name
        counter += 1

        if counter > 99:
            raise RuntimeError(f"Could not create unique directory for '{project_name}'")

    # Create directory
    result = validate_directory_exists(output_dir, create=True)
    if not result.valid:
        raise RuntimeError(f"Failed to create output directory: {result.errors[0]}")

    return output_dir


def read_text_file(path: Path, encoding: str = 'utf-8') -> ValidationResult:
    """
    Read a text file and return ValidationResult with contents.

    Args:
        path: Path to file
        encoding: Text encoding (default: utf-8)

    Returns:
        ValidationResult with 'content' in context if successful
    """
    result = validate_file_exists(path)
    if not result.valid:
        return result

    try:
        content = path.read_text(encoding=encoding)
        result.context['content'] = content
        result.context['line_count'] = len(content.splitlines())
        result.context['char_count'] = len(content)
        result.add_info(f"Successfully read file: {path}")
    except (IOError, UnicodeDecodeError) as e:
        result.add_error(
            f"Failed to read file: {path}",
            context={'path': str(path), 'error': str(e)}
        )

    return result


def get_file_size_mb(path: Path) -> float:
    """
    Get file size in megabytes.

    Args:
        path: Path to file

    Returns:
        File size in MB, or 0 if file doesn't exist
    """
    if not path.exists():
        return 0.0

    size_bytes = path.stat().st_size
    return size_bytes / (1024 * 1024)


def validate_project_structure(project_dir: Path) -> ValidationResult:
    """
    Validate the structure of a Slideforge project directory.

    Args:
        project_dir: Path to project directory

    Returns:
        ValidationResult with details about project structure
    """
    result = ValidationResult()
    result.context['project_dir'] = str(project_dir)

    if not project_dir.exists():
        result.add_error(f"Project directory not found: {project_dir}")
        return result

    # Check for expected subdirectories
    expected_dirs = [
        "01_content_analysis",
        "02_slide_content",
        "03_final_output"
    ]

    for dir_name in expected_dirs:
        dir_path = project_dir / dir_name
        if not dir_path.exists():
            result.add_warning(f"Missing expected directory: {dir_name}")
        else:
            result.add_info(f"Found directory: {dir_name}")

    # Check for final output
    output_dir = project_dir / "03_final_output"
    if output_dir.exists():
        pptx_files = list(output_dir.glob("*.pptx"))
        if not pptx_files:
            result.add_warning("No PPTX files found in final output directory")
        else:
            result.add_info(f"Found {len(pptx_files)} PPTX file(s)")
            result.context['pptx_files'] = [str(f) for f in pptx_files]

    return result
