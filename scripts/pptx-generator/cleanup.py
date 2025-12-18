"""Cleanup utilities for Slideforge presentation generation.

Handles cleanup of intermediate files after PPTX generation,
leaving only the final presentation file in the exports folder.
"""

import shutil
from pathlib import Path
from typing import Optional

# Minimum valid PPTX size (10KB) - smaller likely indicates a problem
MIN_PPTX_SIZE = 10240


class CleanupError(Exception):
    """Raised when cleanup cannot proceed safely."""
    pass


def cleanup_project(
    project_folder: Path,
    keep_json: bool = False
) -> Path:
    """Clean intermediate files from a project folder.

    Moves the final PPTX to the project root and removes all
    intermediate directories and files.

    Args:
        project_folder: Path to the timestamped project folder
        keep_json: If True, preserve the presentation JSON file

    Returns:
        Path to the final PPTX file

    Raises:
        CleanupError: If no valid PPTX found or cleanup cannot proceed
    """
    project_folder = Path(project_folder)

    if not project_folder.exists():
        raise CleanupError(f"Project folder not found: {project_folder}")

    # Find PPTX files - check both 03_final_output and root
    pptx_files = []

    final_output = project_folder / "03_final_output"
    if final_output.exists():
        pptx_files.extend(final_output.glob("*.pptx"))

    # Also check project root for direct output
    pptx_files.extend(project_folder.glob("*.pptx"))

    if not pptx_files:
        raise CleanupError(
            f"No PPTX file found in {project_folder} - cannot cleanup"
        )

    # Use the first PPTX found
    final_pptx = pptx_files[0]

    # Validate PPTX size
    if final_pptx.stat().st_size < MIN_PPTX_SIZE:
        raise CleanupError(
            f"PPTX file too small ({final_pptx.stat().st_size} bytes) - "
            "may be corrupted, skipping cleanup"
        )

    # Move PPTX to project root if in subfolder
    if final_pptx.parent != project_folder:
        dest = project_folder / final_pptx.name
        shutil.move(str(final_pptx), str(dest))
        final_pptx = dest

    # Remove intermediate directories
    intermediate_dirs = [
        "01_content_analysis",
        "02_slide_content",
        "03_final_output",
        "agent_workspaces"
    ]

    for dirname in intermediate_dirs:
        target = project_folder / dirname
        if target.exists() and target.is_dir():
            shutil.rmtree(target)

    # Remove intermediate JSON files
    if not keep_json:
        for json_file in project_folder.glob("*_presentation.json"):
            json_file.unlink()

    # Remove project log
    log_file = project_folder / "project_log.md"
    if log_file.exists():
        log_file.unlink()

    return final_pptx


def cleanup_runtime(runtime_folder: Path) -> int:
    """Clean shared runtime/agent_workspaces directory.

    Removes temporary agent workspace files while preserving
    .gitkeep files and the downloads folder structure.

    Args:
        runtime_folder: Path to the runtime directory

    Returns:
        Number of items cleaned
    """
    runtime_folder = Path(runtime_folder)
    workspaces = runtime_folder / "agent_workspaces"

    if not workspaces.exists():
        return 0

    cleaned = 0
    preserve = {".gitkeep", "downloads"}

    for item in workspaces.iterdir():
        if item.name in preserve:
            # Clean downloads folder contents but keep structure
            if item.name == "downloads" and item.is_dir():
                for download_item in item.iterdir():
                    if download_item.name != ".gitkeep":
                        if download_item.is_dir():
                            shutil.rmtree(download_item)
                        else:
                            download_item.unlink()
                        cleaned += 1
            continue

        # Remove workspace items
        if item.is_dir():
            shutil.rmtree(item)
        else:
            item.unlink()
        cleaned += 1

    return cleaned


def cleanup_all(
    project_folder: Optional[Path] = None,
    runtime_folder: Optional[Path] = None,
    keep_json: bool = False
) -> dict:
    """Perform full cleanup of project and runtime directories.

    Args:
        project_folder: Path to project export folder (optional)
        runtime_folder: Path to runtime directory (optional)
        keep_json: If True, preserve presentation JSON file

    Returns:
        Dictionary with cleanup results
    """
    results = {
        "project_cleaned": False,
        "runtime_cleaned": False,
        "final_pptx": None,
        "runtime_items_removed": 0,
        "errors": []
    }

    # Clean project folder
    if project_folder:
        try:
            final_pptx = cleanup_project(project_folder, keep_json)
            results["project_cleaned"] = True
            results["final_pptx"] = str(final_pptx)
        except CleanupError as e:
            results["errors"].append(str(e))

    # Clean runtime folder
    if runtime_folder:
        try:
            count = cleanup_runtime(runtime_folder)
            results["runtime_cleaned"] = True
            results["runtime_items_removed"] = count
        except Exception as e:
            results["errors"].append(f"Runtime cleanup failed: {e}")

    return results
