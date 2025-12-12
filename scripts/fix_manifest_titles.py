#!/usr/bin/env python3
"""
Fix Manifest Titles Script

Updates manifest titles to match actual content in assessment XML files.
This fixes the issue where manifest shows generic titles like "Week 2 Discussion"
instead of the actual title from the XML file like "Discussion 2: Real-World Variable Uses".

Usage:
    python3 fix_manifest_titles.py -i examples/intro_python_fixed.imscc -o examples/intro_python_final.imscc
"""

import argparse
import zipfile
import tempfile
import re
import os
from pathlib import Path
import xml.etree.ElementTree as ET


def extract_title_from_xml(xml_content: str) -> str:
    """Extract title from XML content."""
    match = re.search(r'<title>([^<]+)</title>', xml_content)
    if match:
        return match.group(1)
    return None


def fix_manifest_titles(temp_path: Path) -> dict:
    """Fix titles in manifest by extracting from actual XML files."""
    stats = {
        'titles_found': 0,
        'titles_updated': 0
    }

    manifest_path = temp_path / 'imsmanifest.xml'
    if not manifest_path.exists():
        print("Error: imsmanifest.xml not found")
        return stats

    # Build a map of resource files to their actual titles
    title_map = {}

    # Find all assessment XML files and extract titles
    for root, dirs, files in os.walk(temp_path):
        for file in files:
            if file.endswith('.xml') and file != 'imsmanifest.xml':
                file_path = Path(root) / file
                rel_path = file_path.relative_to(temp_path)

                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                title = extract_title_from_xml(content)
                if title:
                    # Map by filename (without path) for matching
                    title_map[str(rel_path)] = title
                    title_map[file] = title
                    stats['titles_found'] += 1

    # Read and parse manifest
    with open(manifest_path, 'r', encoding='utf-8') as f:
        manifest_content = f.read()

    # Find all item elements with identifierref pointing to resources
    # Pattern: <item identifier="..." identifierref="...">....<title>OLD_TITLE</title>
    item_pattern = r'(<item[^>]*identifierref="([^"]*)"[^>]*>\s*<title>)([^<]+)(</title>)'

    def update_title(match):
        prefix = match.group(1)
        identifierref = match.group(2)
        old_title = match.group(3)
        suffix = match.group(4)

        # Try to find the actual title from our map
        # The identifierref might be like "RES_W01_DISC_R" which maps to "week_01/discussion_week_01.xml"
        new_title = None

        # Search through title_map for a match
        for path, title in title_map.items():
            # Check if identifierref contains patterns that match the file
            path_lower = path.lower()
            ref_lower = identifierref.lower()

            # Match patterns like W01_DISC -> discussion_week_01
            # or quiz_week_01 -> quiz
            if 'disc' in ref_lower and 'discussion' in path_lower:
                # Extract week number from identifierref
                week_match = re.search(r'w(\d+)', ref_lower)
                if week_match:
                    week_num = week_match.group(1)
                    if f'week_{week_num}' in path_lower or f'week_{int(week_num):02d}' in path_lower:
                        new_title = title
                        break

            elif 'quiz' in ref_lower and 'quiz' in path_lower:
                week_match = re.search(r'w(\d+)', ref_lower)
                if week_match:
                    week_num = week_match.group(1)
                    if f'week_{week_num}' in path_lower or f'week_{int(week_num):02d}' in path_lower:
                        new_title = title
                        break

            elif 'assign' in ref_lower and 'assignment' in path_lower:
                week_match = re.search(r'w(\d+)', ref_lower)
                if week_match:
                    week_num = week_match.group(1)
                    if f'week_{week_num}' in path_lower or f'week_{int(week_num):02d}' in path_lower:
                        new_title = title
                        break

        if new_title and new_title != old_title:
            stats['titles_updated'] += 1
            print(f"  Updated: '{old_title}' -> '{new_title}'")
            return prefix + new_title + suffix

        return match.group(0)

    # Update manifest with correct titles
    updated_manifest = re.sub(item_pattern, update_title, manifest_content)

    # Write updated manifest
    with open(manifest_path, 'w', encoding='utf-8') as f:
        f.write(updated_manifest)

    return stats


def process_imscc(input_path: str, output_path: str) -> dict:
    """Process IMSCC package and fix manifest titles."""
    stats = {
        'titles_found': 0,
        'titles_updated': 0,
        'files_copied': 0
    }

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Extract IMSCC
        print(f"Extracting {input_path}...")
        with zipfile.ZipFile(input_path, 'r') as zf:
            zf.extractall(temp_path)

        # Fix manifest titles
        print("Fixing manifest titles...")
        title_stats = fix_manifest_titles(temp_path)
        stats.update(title_stats)

        # Repackage IMSCC
        print(f"\nCreating fixed package: {output_path}")
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for root, dirs, files in os.walk(temp_path):
                for file in files:
                    file_path = Path(root) / file
                    arc_name = file_path.relative_to(temp_path)
                    zf.write(file_path, arc_name)
                    stats['files_copied'] += 1

    return stats


def main():
    parser = argparse.ArgumentParser(
        description='Fix manifest titles to match actual assessment XML content'
    )
    parser.add_argument(
        '-i', '--input',
        required=True,
        help='Input IMSCC file path'
    )
    parser.add_argument(
        '-o', '--output',
        help='Output IMSCC file path (default: input_titled.imscc)'
    )

    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}")
        return 1

    if args.output:
        output_path = Path(args.output)
    else:
        output_path = input_path.with_stem(input_path.stem + '_titled')

    print("=" * 60)
    print("Manifest Title Fix Script")
    print("=" * 60)
    print(f"Input:  {input_path}")
    print(f"Output: {output_path}")
    print()

    stats = process_imscc(str(input_path), str(output_path))

    print()
    print("=" * 60)
    print("Summary:")
    print(f"  Titles found in XMLs: {stats['titles_found']}")
    print(f"  Manifest titles updated: {stats['titles_updated']}")
    print(f"  Files in package: {stats['files_copied']}")
    print("=" * 60)

    if Path(output_path).exists():
        print(f"\nFixed package created: {output_path}")

    return 0


if __name__ == "__main__":
    exit(main())
