#!/usr/bin/env python3
"""
Fix Quiz QTI Metadata Script

Adds missing IMS Common Cartridge metadata to quiz XML files in IMSCC packages.
This fixes the issue where quizzes import but questions don't load in Brightspace.

Missing metadata that this script adds:
1. xmlns:xsi and xsi:schemaLocation on root element
2. cc_profile and qmd_assessmenttype at assessment level
3. itemmetadata with cc_profile on each question item

Usage:
    python3 fix_quiz_metadata.py -i examples/intro_python.imscc -o examples/intro_python_fixed.imscc
"""

import argparse
import zipfile
import tempfile
import shutil
import re
import os
from pathlib import Path


# QTI namespace and schema
QTI_NAMESPACE = "http://www.imsglobal.org/xsd/ims_qtiasiv1p2"
QTI_SCHEMA_LOCATION = "http://www.imsglobal.org/profile/cc/ccv1p3/ccv1p3_qtiasiv1p2p1_v1p0.xsd"


def detect_question_type(item_xml: str) -> str:
    """Detect question type from item XML structure."""
    # Check for response_lid (multiple choice/true-false)
    if 'response_lid' in item_xml:
        # Count response_labels to differentiate MC from TF
        label_count = item_xml.count('<response_label')
        if label_count == 2:
            # Check if it's true/false
            if re.search(r'>True<|>False<', item_xml, re.IGNORECASE):
                return "cc.true_false.v0p1"
        return "cc.multiple_choice.v0p1"

    # Check for response_str (essay/fill-in-blank)
    if 'response_str' in item_xml:
        if 'render_fib' in item_xml:
            # Could be essay or fill-in-blank
            return "cc.essay.v0p1"

    # Default to multiple choice
    return "cc.multiple_choice.v0p1"


def extract_points_from_item(item_xml: str) -> str:
    """Extract point value from item's resprocessing."""
    # Look for maxvalue in decvar
    match = re.search(r'maxvalue="(\d+)"', item_xml)
    if match:
        return match.group(1)
    return "1"


# Mapping from Canvas/non-standard question types to CC profile values
QUESTION_TYPE_MAP = {
    'multiple_choice_question': 'cc.multiple_choice.v0p1',
    'multiple_choice': 'cc.multiple_choice.v0p1',
    'true_false_question': 'cc.true_false.v0p1',
    'true_false': 'cc.true_false.v0p1',
    'essay_question': 'cc.essay.v0p1',
    'essay': 'cc.essay.v0p1',
    'fill_in_blank_question': 'cc.fib.v0p1',
    'fill_in_blank': 'cc.fib.v0p1',
    'short_answer_question': 'cc.fib.v0p1',
    'multiple_answers_question': 'cc.multiple_response.v0p1',
    'multiple_response': 'cc.multiple_response.v0p1',
}


def fix_itemmetadata(item_xml: str) -> str:
    """Fix itemmetadata with wrong field names (question_type -> cc_profile)."""

    # Check if itemmetadata exists but has wrong field names
    if '<itemmetadata>' in item_xml:
        # Fix question_type -> cc_profile
        if '<fieldlabel>question_type</fieldlabel>' in item_xml:
            # Extract the current question type value
            type_match = re.search(
                r'<fieldlabel>question_type</fieldlabel>\s*<fieldentry>([^<]+)</fieldentry>',
                item_xml
            )
            if type_match:
                old_type = type_match.group(1).strip()
                new_type = QUESTION_TYPE_MAP.get(old_type, detect_question_type(item_xml))

                # Replace the fieldlabel and fieldentry
                item_xml = re.sub(
                    r'<fieldlabel>question_type</fieldlabel>(\s*)<fieldentry>[^<]+</fieldentry>',
                    f'<fieldlabel>cc_profile</fieldlabel>\\1<fieldentry>{new_type}</fieldentry>',
                    item_xml
                )

        # Fix points_possible -> cc_weighting
        if '<fieldlabel>points_possible</fieldlabel>' in item_xml:
            item_xml = item_xml.replace(
                '<fieldlabel>points_possible</fieldlabel>',
                '<fieldlabel>cc_weighting</fieldlabel>'
            )

        # If cc_profile still missing after fixes, add it
        if '<fieldlabel>cc_profile</fieldlabel>' not in item_xml:
            question_type = detect_question_type(item_xml)
            points = extract_points_from_item(item_xml)

            # Find qtimetadata in itemmetadata and add cc_profile
            itemmetadata_match = re.search(r'(<itemmetadata>\s*<qtimetadata>\s*\n)', item_xml)
            if itemmetadata_match:
                insert_pos = itemmetadata_match.end()
                cc_fields = f'''            <qtimetadatafield>
              <fieldlabel>cc_profile</fieldlabel>
              <fieldentry>{question_type}</fieldentry>
            </qtimetadatafield>
            <qtimetadatafield>
              <fieldlabel>cc_weighting</fieldlabel>
              <fieldentry>{points}</fieldentry>
            </qtimetadatafield>
'''
                item_xml = item_xml[:insert_pos] + cc_fields + item_xml[insert_pos:]

        return item_xml

    # No itemmetadata exists - add it
    question_type = detect_question_type(item_xml)
    points = extract_points_from_item(item_xml)

    # Create itemmetadata block
    itemmetadata = f'''        <itemmetadata>
          <qtimetadata>
            <qtimetadatafield>
              <fieldlabel>cc_profile</fieldlabel>
              <fieldentry>{question_type}</fieldentry>
            </qtimetadatafield>
            <qtimetadatafield>
              <fieldlabel>cc_weighting</fieldlabel>
              <fieldentry>{points}</fieldentry>
            </qtimetadatafield>
          </qtimetadata>
        </itemmetadata>
'''

    # Insert after <item ...> opening tag
    item_pattern = r'(<item[^>]*>)\s*\n'
    match = re.search(item_pattern, item_xml)
    if match:
        insert_pos = match.end()
        return item_xml[:insert_pos] + itemmetadata + item_xml[insert_pos:]

    return item_xml


def fix_quiz_xml(xml_content: str) -> str:
    """Fix quiz XML by adding missing CC metadata."""

    # Step 1: Fix root element - add xsi namespace and schemaLocation
    root_pattern = r'<questestinterop\s+xmlns="([^"]+)">'
    root_match = re.search(root_pattern, xml_content)

    if root_match and 'xmlns:xsi' not in xml_content[:500]:
        old_root = root_match.group(0)
        new_root = f'''<questestinterop xmlns="{QTI_NAMESPACE}"
                 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                 xsi:schemaLocation="{QTI_NAMESPACE} {QTI_SCHEMA_LOCATION}">'''
        xml_content = xml_content.replace(old_root, new_root, 1)

    # Step 2: Add assessment-level cc_profile if missing
    if '<fieldlabel>cc_profile</fieldlabel>' not in xml_content:
        # Find the qtimetadata section in assessment
        qtimetadata_pattern = r'(<qtimetadata>\s*\n)'
        match = re.search(qtimetadata_pattern, xml_content)
        if match:
            insert_pos = match.end()
            cc_profile_fields = '''      <qtimetadatafield>
        <fieldlabel>cc_profile</fieldlabel>
        <fieldentry>cc.exam.v0p1</fieldentry>
      </qtimetadatafield>
      <qtimetadatafield>
        <fieldlabel>qmd_assessmenttype</fieldlabel>
        <fieldentry>Examination</fieldentry>
      </qtimetadatafield>
'''
            xml_content = xml_content[:insert_pos] + cc_profile_fields + xml_content[insert_pos:]

    # Step 3: Fix/add itemmetadata to each question item
    # Find all item elements and process them
    item_pattern = r'<item\s+ident="[^"]*"[^>]*>.*?</item>'

    def fix_metadata_in_item(match):
        item_xml = match.group(0)
        return fix_itemmetadata(item_xml)

    xml_content = re.sub(item_pattern, fix_metadata_in_item, xml_content, flags=re.DOTALL)

    return xml_content


def process_imscc(input_path: str, output_path: str) -> dict:
    """Process IMSCC package and fix all quiz XML files."""
    stats = {
        'quizzes_found': 0,
        'quizzes_fixed': 0,
        'files_copied': 0
    }

    # Create temp directory for extraction
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Extract IMSCC
        print(f"Extracting {input_path}...")
        with zipfile.ZipFile(input_path, 'r') as zf:
            zf.extractall(temp_path)

        # Find and fix all quiz XML files
        for root, dirs, files in os.walk(temp_path):
            for file in files:
                if file.startswith('quiz_') and file.endswith('.xml'):
                    stats['quizzes_found'] += 1
                    file_path = Path(root) / file

                    print(f"Processing {file}...")

                    # Read and fix XML
                    with open(file_path, 'r', encoding='utf-8') as f:
                        original_xml = f.read()

                    fixed_xml = fix_quiz_xml(original_xml)

                    # Write fixed XML
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(fixed_xml)

                    if fixed_xml != original_xml:
                        stats['quizzes_fixed'] += 1
                        print(f"  Fixed: {file}")
                    else:
                        print(f"  No changes needed: {file}")

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
        description='Fix quiz QTI metadata in IMSCC packages for Brightspace compatibility'
    )
    parser.add_argument(
        '-i', '--input',
        required=True,
        help='Input IMSCC file path'
    )
    parser.add_argument(
        '-o', '--output',
        help='Output IMSCC file path (default: input_fixed.imscc)'
    )

    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}")
        return 1

    if args.output:
        output_path = Path(args.output)
    else:
        output_path = input_path.with_stem(input_path.stem + '_fixed')

    print("=" * 60)
    print("Quiz QTI Metadata Fix Script")
    print("=" * 60)
    print(f"Input:  {input_path}")
    print(f"Output: {output_path}")
    print()

    stats = process_imscc(str(input_path), str(output_path))

    print()
    print("=" * 60)
    print("Summary:")
    print(f"  Quizzes found: {stats['quizzes_found']}")
    print(f"  Quizzes fixed: {stats['quizzes_fixed']}")
    print(f"  Files in package: {stats['files_copied']}")
    print("=" * 60)

    if output_path.exists():
        print(f"\nFixed package created: {output_path}")
        print("Please test this package in Brightspace to verify quiz questions load correctly.")

    return 0


if __name__ == "__main__":
    exit(main())
