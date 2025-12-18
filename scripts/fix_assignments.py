#!/usr/bin/env python3
"""
Fix Assignment Instructions for Brightspace

Converts assignment XML files from deprecated D2L 2.0 format to correct IMSCC extensions format.
"""

import os
import re
import zipfile
import shutil
from pathlib import Path

# Paths
EXAMPLES_DIR = Path("/home/bacon/Desktop/Courseforge/examples")
IMSCC_FILE = EXAMPLES_DIR / "intro_python.imscc"
TEMP_DIR = EXAMPLES_DIR / "intro_python_temp"

# Correct namespace and schema
CORRECT_NAMESPACE = "http://www.imsglobal.org/xsd/imscc_extensions/assignment"
CORRECT_SCHEMA = "http://www.imsglobal.org/profile/cc/cc_extensions/cc_extresource_assignmentv1p0_v1p0.xsd"


def extract_imscc():
    """Extract IMSCC package to temp directory."""
    print(f"Extracting {IMSCC_FILE} to {TEMP_DIR}...")

    # Remove existing temp dir
    if TEMP_DIR.exists():
        shutil.rmtree(TEMP_DIR)

    TEMP_DIR.mkdir(parents=True)

    with zipfile.ZipFile(IMSCC_FILE, 'r') as zip_ref:
        zip_ref.extractall(TEMP_DIR)

    print(f"Extracted to {TEMP_DIR}")


def convert_assignment_xml(file_path: Path):
    """Convert a single assignment XML file to use instructor_text element."""
    print(f"Converting {file_path.name}...")

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    instructions_html = None

    # Format 1: <text texttype="text/html"><![CDATA[...]]></text>
    instructions_match = re.search(
        r'<text\s+texttype="text/html">\s*<!\[CDATA\[(.*?)\]\]>\s*</text>',
        content,
        re.DOTALL
    )
    if instructions_match:
        instructions_html = instructions_match.group(1).strip()

    # Format 2: <text texttype="text/html">...</text> (no CDATA)
    if not instructions_html:
        instructions_match = re.search(
            r'<text\s+texttype="text/html">(.*?)</text>',
            content,
            re.DOTALL
        )
        if instructions_match:
            instructions_html = instructions_match.group(1).strip()

    # Format 3: <instructions><![CDATA[...]]></instructions>
    if not instructions_html:
        instructions_match = re.search(
            r'<instructions>\s*<!\[CDATA\[(.*?)\]\]>\s*</instructions>',
            content,
            re.DOTALL
        )
        if instructions_match:
            instructions_html = instructions_match.group(1).strip()

    # Format 4: <instructions>...</instructions> (no CDATA)
    if not instructions_html:
        instructions_match = re.search(
            r'<instructions>(.*?)</instructions>',
            content,
            re.DOTALL
        )
        if instructions_match:
            instructions_html = instructions_match.group(1).strip()

    if not instructions_html:
        print(f"  Warning: Could not find instructions in {file_path.name}")
        return False

    # HTML-encode the content (convert < > & to entities)
    import html
    encoded_html = html.escape(instructions_html)

    # Extract points from gradable element
    points_match = re.search(r'points_possible="([^"]+)"', content)
    points = points_match.group(1) if points_match else "100"

    # Get identifier from existing content or filename
    id_match = re.search(r'identifier="([^"]+)"', content)
    identifier = id_match.group(1) if id_match else file_path.stem

    # Build new XML content with instructor_text element
    new_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<assignment xmlns="{CORRECT_NAMESPACE}"
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
            xsi:schemaLocation="{CORRECT_NAMESPACE} {CORRECT_SCHEMA}"
            identifier="{identifier}">
  <title>{extract_title(content)}</title>
  <instructor_text texttype="text/html">{encoded_html}</instructor_text>
  <submission_formats>
    <format type="file"/>
  </submission_formats>
  <gradable points_possible="{points}">true</gradable>
</assignment>
'''

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print(f"  Converted {file_path.name}")
    return True


def extract_title(content: str) -> str:
    """Extract title from assignment XML."""
    match = re.search(r'<title>(.*?)</title>', content)
    return match.group(1) if match else "Assignment"


def update_manifest():
    """Update imsmanifest.xml resource types for assignments."""
    manifest_path = TEMP_DIR / "imsmanifest.xml"
    print(f"Updating {manifest_path}...")

    with open(manifest_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Replace deprecated resource type with correct one
    # Match various forms of the d2l assignment type
    patterns = [
        r'type="imsccv1p1/d2l_2p0/assignment"',
        r'type="d2l_2p0/assignment"',
        r'type="assignment"',  # Generic
    ]

    for pattern in patterns:
        content = re.sub(pattern, 'type="assignment_xmlv1p0"', content)

    with open(manifest_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print("  Updated manifest resource types")


def repackage_imscc():
    """Repackage the temp directory back into IMSCC."""
    print(f"Repackaging to {IMSCC_FILE}...")

    # Remove old IMSCC
    if IMSCC_FILE.exists():
        IMSCC_FILE.unlink()

    # Create new IMSCC
    with zipfile.ZipFile(IMSCC_FILE, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(TEMP_DIR):
            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(TEMP_DIR)
                zipf.write(file_path, arcname)

    print(f"Created {IMSCC_FILE}")


def cleanup():
    """Remove temp directory."""
    print(f"Cleaning up {TEMP_DIR}...")
    if TEMP_DIR.exists():
        shutil.rmtree(TEMP_DIR)
    print("Done!")


def main():
    print("=" * 60)
    print("Fix Assignment Instructions for Brightspace")
    print("=" * 60)

    # Step 1: Extract
    extract_imscc()

    # Step 2: Find and convert assignment files
    assignment_files = list(TEMP_DIR.glob("**/assignment_week_*.xml"))
    print(f"\nFound {len(assignment_files)} assignment files")

    converted = 0
    for assignment_file in sorted(assignment_files):
        if convert_assignment_xml(assignment_file):
            converted += 1

    print(f"\nConverted {converted} assignment files")

    # Step 3: Update manifest
    update_manifest()

    # Step 4: Repackage
    repackage_imscc()

    # Step 5: Cleanup
    cleanup()

    print("\n" + "=" * 60)
    print("COMPLETE! Assignment instructions should now appear in Brightspace.")
    print("=" * 60)


if __name__ == "__main__":
    main()
