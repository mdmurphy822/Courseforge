#!/usr/bin/env python3
"""
PPTX Repair Utility

Fixes PowerPoint files with Windows compatibility issues:
- Missing ppt/presProps.xml (Presentation Properties)
- Missing ppt/viewProps.xml (View Properties)
- Missing ppt/tableStyles.xml (Table Styles)
- Missing <p:clrMap> in slide masters (causes invisible content)
- Missing <a:prstGeom> on shapes (causes rendering failures)

These issues cause Windows PowerPoint to show empty/blank slides even though
content exists. This script performs surgical XML repairs.

Reference: LibV2 course "Accessible PowerPoint: OOXML Structure and WCAG 2.2 Compliance"
"""

import argparse
import re
import shutil
import tempfile
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path


# OOXML Namespace definitions
NAMESPACES = {
    'r': 'http://schemas.openxmlformats.org/package/2006/relationships',
    'ct': 'http://schemas.openxmlformats.org/package/2006/content-types',
    'p': 'http://schemas.openxmlformats.org/presentationml/2006/main',
    'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
}

# Relationship type URIs (from LibV2 OOXML course)
REL_TYPES = {
    'presProps': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/presProps',
    'viewProps': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/viewProps',
    'tableStyles': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/tableStyles',
}

# Content types for missing parts
CONTENT_TYPES = {
    '/ppt/presProps.xml': 'application/vnd.openxmlformats-officedocument.presentationml.presProps+xml',
    '/ppt/viewProps.xml': 'application/vnd.openxmlformats-officedocument.presentationml.viewProps+xml',
    '/ppt/tableStyles.xml': 'application/vnd.openxmlformats-officedocument.presentationml.tableStyles+xml',
}

# Default XML content for missing files
PRES_PROPS_XML = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:presentationPr xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"/>
'''

VIEW_PROPS_XML = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:viewPr xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:normalViewPr><p:restoredLeft sz="15620"/><p:restoredTop sz="94660"/></p:normalViewPr>
  <p:slideViewPr><p:cSldViewPr><p:cViewPr varScale="1"><p:scale><a:sx n="100" d="100"/><a:sy n="100" d="100"/></p:scale><p:origin x="0" y="0"/></p:cViewPr></p:cSldViewPr></p:slideViewPr>
  <p:gridSpacing cx="76200" cy="76200"/>
</p:viewPr>
'''

TABLE_STYLES_XML = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<a:tblStyleLst xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" def="{5C22544A-7EE6-4342-B048-85BDC9FD1C3A}"/>
'''

# Color map element for slide masters (maps theme colors)
CLRMAP_XML = '<p:clrMap bg1="lt1" tx1="dk1" bg2="lt2" tx2="dk2" accent1="accent1" accent2="accent2" accent3="accent3" accent4="accent4" accent5="accent5" accent6="accent6" hlink="hlink" folHlink="folHlink"/>'

# Geometry element for shapes
PRSTGEOM_XML = '<a:prstGeom prst="rect"><a:avLst/></a:prstGeom>'

# Color map override for slide layouts and slides
CLRMAPOVR_XML = '<p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr>'

# Default text style for presentation.xml (9 levels required by Windows PowerPoint)
DEFAULT_TEXT_STYLE_XML = '''<p:defaultTextStyle><a:defPPr><a:defRPr lang="en-US"/></a:defPPr><a:lvl1pPr marL="0" algn="l" defTabSz="457200" rtl="0" eaLnBrk="1" latinLnBrk="0" hangingPunct="1"><a:defRPr sz="1800" kern="1200"><a:solidFill><a:schemeClr val="tx1"/></a:solidFill><a:latin typeface="+mn-lt"/><a:ea typeface="+mn-ea"/><a:cs typeface="+mn-cs"/></a:defRPr></a:lvl1pPr><a:lvl2pPr marL="457200" algn="l" defTabSz="457200" rtl="0" eaLnBrk="1" latinLnBrk="0" hangingPunct="1"><a:defRPr sz="1800" kern="1200"><a:solidFill><a:schemeClr val="tx1"/></a:solidFill><a:latin typeface="+mn-lt"/><a:ea typeface="+mn-ea"/><a:cs typeface="+mn-cs"/></a:defRPr></a:lvl2pPr><a:lvl3pPr marL="914400" algn="l" defTabSz="457200" rtl="0" eaLnBrk="1" latinLnBrk="0" hangingPunct="1"><a:defRPr sz="1800" kern="1200"><a:solidFill><a:schemeClr val="tx1"/></a:solidFill><a:latin typeface="+mn-lt"/><a:ea typeface="+mn-ea"/><a:cs typeface="+mn-cs"/></a:defRPr></a:lvl3pPr><a:lvl4pPr marL="1371600" algn="l" defTabSz="457200" rtl="0" eaLnBrk="1" latinLnBrk="0" hangingPunct="1"><a:defRPr sz="1800" kern="1200"><a:solidFill><a:schemeClr val="tx1"/></a:solidFill><a:latin typeface="+mn-lt"/><a:ea typeface="+mn-ea"/><a:cs typeface="+mn-cs"/></a:defRPr></a:lvl4pPr><a:lvl5pPr marL="1828800" algn="l" defTabSz="457200" rtl="0" eaLnBrk="1" latinLnBrk="0" hangingPunct="1"><a:defRPr sz="1800" kern="1200"><a:solidFill><a:schemeClr val="tx1"/></a:solidFill><a:latin typeface="+mn-lt"/><a:ea typeface="+mn-ea"/><a:cs typeface="+mn-cs"/></a:defRPr></a:lvl5pPr><a:lvl6pPr marL="2286000" algn="l" defTabSz="457200" rtl="0" eaLnBrk="1" latinLnBrk="0" hangingPunct="1"><a:defRPr sz="1800" kern="1200"><a:solidFill><a:schemeClr val="tx1"/></a:solidFill><a:latin typeface="+mn-lt"/><a:ea typeface="+mn-ea"/><a:cs typeface="+mn-cs"/></a:defRPr></a:lvl6pPr><a:lvl7pPr marL="2743200" algn="l" defTabSz="457200" rtl="0" eaLnBrk="1" latinLnBrk="0" hangingPunct="1"><a:defRPr sz="1800" kern="1200"><a:solidFill><a:schemeClr val="tx1"/></a:solidFill><a:latin typeface="+mn-lt"/><a:ea typeface="+mn-ea"/><a:cs typeface="+mn-cs"/></a:defRPr></a:lvl7pPr><a:lvl8pPr marL="3200400" algn="l" defTabSz="457200" rtl="0" eaLnBrk="1" latinLnBrk="0" hangingPunct="1"><a:defRPr sz="1800" kern="1200"><a:solidFill><a:schemeClr val="tx1"/></a:solidFill><a:latin typeface="+mn-lt"/><a:ea typeface="+mn-ea"/><a:cs typeface="+mn-cs"/></a:defRPr></a:lvl8pPr><a:lvl9pPr marL="3657600" algn="l" defTabSz="457200" rtl="0" eaLnBrk="1" latinLnBrk="0" hangingPunct="1"><a:defRPr sz="1800" kern="1200"><a:solidFill><a:schemeClr val="tx1"/></a:solidFill><a:latin typeface="+mn-lt"/><a:ea typeface="+mn-ea"/><a:cs typeface="+mn-cs"/></a:defRPr></a:lvl9pPr></p:defaultTextStyle>'''


def get_next_rid(rels_root: ET.Element) -> str:
    """Find the next available relationship ID."""
    max_id = 0
    for rel in rels_root.findall('.//{http://schemas.openxmlformats.org/package/2006/relationships}Relationship'):
        rid = rel.get('Id', '')
        if rid.startswith('rId'):
            try:
                num = int(rid[3:])
                max_id = max(max_id, num)
            except ValueError:
                pass
    return f'rId{max_id + 1}'


def check_missing_parts(extract_dir: Path) -> dict:
    """Check which required parts are missing."""
    missing = {}

    parts_to_check = {
        'presProps': extract_dir / 'ppt' / 'presProps.xml',
        'viewProps': extract_dir / 'ppt' / 'viewProps.xml',
        'tableStyles': extract_dir / 'ppt' / 'tableStyles.xml',
    }

    for name, path in parts_to_check.items():
        if not path.exists():
            missing[name] = path

    return missing


def inject_missing_parts(extract_dir: Path, missing: dict) -> None:
    """Create the missing XML files."""
    content_map = {
        'presProps': PRES_PROPS_XML,
        'viewProps': VIEW_PROPS_XML,
        'tableStyles': TABLE_STYLES_XML,
    }

    for name, path in missing.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content_map[name], encoding='utf-8')
        print(f"  Created: {path.relative_to(extract_dir)}")


def update_relationships(extract_dir: Path, missing: dict) -> None:
    """Add relationships for the new parts."""
    rels_path = extract_dir / 'ppt' / '_rels' / 'presentation.xml.rels'

    if not rels_path.exists():
        print(f"  Warning: {rels_path} not found, skipping relationship update")
        return

    # Parse existing relationships
    ET.register_namespace('', 'http://schemas.openxmlformats.org/package/2006/relationships')
    tree = ET.parse(rels_path)
    root = tree.getroot()

    # Check existing relationships
    existing_types = set()
    for rel in root.findall('.//{http://schemas.openxmlformats.org/package/2006/relationships}Relationship'):
        existing_types.add(rel.get('Type', ''))

    # Add missing relationships
    next_id = int(get_next_rid(root)[3:])  # Extract number from rIdXX
    for name in missing:
        rel_type = REL_TYPES[name]
        if rel_type not in existing_types:
            rid = f'rId{next_id}'
            next_id += 1
            new_rel = ET.SubElement(root, 'Relationship')
            new_rel.set('Id', rid)
            new_rel.set('Type', rel_type)
            new_rel.set('Target', f'{name}.xml')
            print(f"  Added relationship: {rid} -> {name}.xml")

    # Write back
    tree.write(rels_path, encoding='UTF-8', xml_declaration=True)


def update_content_types(extract_dir: Path, missing: dict) -> None:
    """Add content type declarations for the new parts."""
    ct_path = extract_dir / '[Content_Types].xml'

    if not ct_path.exists():
        print(f"  Warning: {ct_path} not found, skipping content type update")
        return

    # Parse existing content types
    ET.register_namespace('', 'http://schemas.openxmlformats.org/package/2006/content-types')
    tree = ET.parse(ct_path)
    root = tree.getroot()

    # Check existing overrides
    existing_parts = set()
    for override in root.findall('.//{http://schemas.openxmlformats.org/package/2006/content-types}Override'):
        existing_parts.add(override.get('PartName', ''))

    # Add missing overrides
    for name in missing:
        part_name = f'/ppt/{name}.xml'
        if part_name not in existing_parts:
            new_override = ET.SubElement(root, 'Override')
            new_override.set('PartName', part_name)
            new_override.set('ContentType', CONTENT_TYPES[part_name])
            print(f"  Added content type: {part_name}")

    # Write back
    tree.write(ct_path, encoding='UTF-8', xml_declaration=True)


def inject_clrmap(extract_dir: Path) -> int:
    """
    Add missing <p:clrMap> to slide masters.

    Without clrMap, Windows PowerPoint cannot resolve theme colors,
    causing all content to become invisible.

    Returns:
        Number of slide masters fixed
    """
    fixes = 0
    masters_dir = extract_dir / 'ppt' / 'slideMasters'

    if not masters_dir.exists():
        return 0

    for master_file in masters_dir.glob('slideMaster*.xml'):
        content = master_file.read_text(encoding='utf-8')

        # Check if clrMap already exists
        if '<p:clrMap' in content or 'clrMap' in content:
            continue

        # Insert clrMap after </p:cSld> and before <p:sldLayoutIdLst>
        # The element order in slide master must be: cSld, clrMap, sldLayoutIdLst, txStyles
        if '</p:cSld>' in content:
            content = content.replace('</p:cSld>', f'</p:cSld>{CLRMAP_XML}')
            master_file.write_text(content, encoding='utf-8')
            print(f"  Injected clrMap into: {master_file.name}")
            fixes += 1

    return fixes


def inject_geometry(extract_dir: Path) -> int:
    """
    Add missing <a:prstGeom> to shapes that have <a:xfrm> but no geometry.

    Windows PowerPoint requires explicit geometry definitions for all shapes.
    Without it, shapes may not render.

    Returns:
        Number of shapes fixed
    """
    fixes = 0

    # Directories to scan for shapes
    dirs_to_scan = [
        extract_dir / 'ppt' / 'slides',
        extract_dir / 'ppt' / 'slideLayouts',
        extract_dir / 'ppt' / 'slideMasters',
    ]

    for scan_dir in dirs_to_scan:
        if not scan_dir.exists():
            continue

        for xml_file in scan_dir.glob('*.xml'):
            content = xml_file.read_text(encoding='utf-8')
            original_content = content

            # Find <p:spPr> or <p:spPr ...> blocks that contain <a:xfrm> but no <a:prstGeom>
            # Pattern: <p:spPr> ... </a:xfrm> ... </p:spPr> without prstGeom

            # Use regex to find spPr blocks
            sppr_pattern = r'(<p:spPr[^>]*>)(.*?)(</p:spPr>)'

            def add_geometry(match):
                nonlocal fixes
                open_tag = match.group(1)
                inner = match.group(2)
                close_tag = match.group(3)

                # Check if this block has xfrm but no prstGeom
                has_xfrm = '</a:xfrm>' in inner or '<a:xfrm' in inner
                has_geom = '<a:prstGeom' in inner or '<a:custGeom' in inner

                if has_xfrm and not has_geom:
                    # Insert prstGeom after </a:xfrm>
                    inner = inner.replace('</a:xfrm>', f'</a:xfrm>{PRSTGEOM_XML}')
                    fixes += 1

                return open_tag + inner + close_tag

            content = re.sub(sppr_pattern, add_geometry, content, flags=re.DOTALL)

            if content != original_content:
                xml_file.write_text(content, encoding='utf-8')

    if fixes > 0:
        print(f"  Injected geometry into {fixes} shape(s)")

    return fixes


def inject_clrmap_override(extract_dir: Path) -> int:
    """
    Add missing <p:clrMapOvr> to slide layouts and slides.

    Every slide layout and slide MUST have a color map override element,
    even if it just inherits from the master. Without this, Windows
    PowerPoint cannot resolve theme colors on individual slides.

    Returns:
        Number of files fixed
    """
    fixes = 0

    # Fix slide layouts
    layouts_dir = extract_dir / 'ppt' / 'slideLayouts'
    if layouts_dir.exists():
        for layout_file in layouts_dir.glob('*.xml'):
            content = layout_file.read_text(encoding='utf-8')
            if '<p:clrMapOvr' not in content and '</p:sldLayout>' in content:
                content = content.replace('</p:sldLayout>', f'{CLRMAPOVR_XML}</p:sldLayout>')
                layout_file.write_text(content, encoding='utf-8')
                print(f"  Injected clrMapOvr into: {layout_file.name}")
                fixes += 1

    # Fix slides
    slides_dir = extract_dir / 'ppt' / 'slides'
    if slides_dir.exists():
        for slide_file in slides_dir.glob('slide*.xml'):
            content = slide_file.read_text(encoding='utf-8')
            if '<p:clrMapOvr' not in content and '</p:sld>' in content:
                content = content.replace('</p:sld>', f'{CLRMAPOVR_XML}</p:sld>')
                slide_file.write_text(content, encoding='utf-8')
                print(f"  Injected clrMapOvr into: {slide_file.name}")
                fixes += 1

    return fixes


def inject_default_text_style(extract_dir: Path) -> bool:
    """
    Add missing <p:defaultTextStyle> to presentation.xml.

    Windows PowerPoint requires default text styles (9 levels) for proper
    text rendering fallback. Without this, text may not display correctly.

    Returns:
        True if fix was applied, False otherwise
    """
    pres_path = extract_dir / 'ppt' / 'presentation.xml'
    if not pres_path.exists():
        return False

    content = pres_path.read_text(encoding='utf-8')
    if '<p:defaultTextStyle' in content:
        return False

    # Insert before </p:presentation>
    content = content.replace('</p:presentation>', f'{DEFAULT_TEXT_STYLE_XML}</p:presentation>')
    pres_path.write_text(content, encoding='utf-8')
    print("  Injected defaultTextStyle into: presentation.xml")
    return True


def reorder_presentation_elements(extract_dir: Path) -> bool:
    """
    Reorder elements in presentation.xml to match OOXML schema requirements.

    The PresentationML schema requires elements in strict order:
    1. sldMasterIdLst
    2. notesMasterIdLst (optional)
    3. handoutMasterIdLst (optional)
    4. sldIdLst
    5. sldSz
    6. notesSz
    7. ... other optional elements ...
    8. defaultTextStyle

    Returns:
        True if reordering was performed, False otherwise
    """
    pres_path = extract_dir / 'ppt' / 'presentation.xml'
    if not pres_path.exists():
        return False

    # Register namespaces to preserve them
    for prefix, uri in NAMESPACES.items():
        ET.register_namespace(prefix, uri)
    ET.register_namespace('', 'http://schemas.openxmlformats.org/presentationml/2006/main')

    tree = ET.parse(pres_path)
    root = tree.getroot()

    # Define element order per schema
    element_order = [
        '{http://schemas.openxmlformats.org/presentationml/2006/main}sldMasterIdLst',
        '{http://schemas.openxmlformats.org/presentationml/2006/main}notesMasterIdLst',
        '{http://schemas.openxmlformats.org/presentationml/2006/main}handoutMasterIdLst',
        '{http://schemas.openxmlformats.org/presentationml/2006/main}sldIdLst',
        '{http://schemas.openxmlformats.org/presentationml/2006/main}sldSz',
        '{http://schemas.openxmlformats.org/presentationml/2006/main}notesSz',
        '{http://schemas.openxmlformats.org/presentationml/2006/main}embeddedFontLst',
        '{http://schemas.openxmlformats.org/presentationml/2006/main}custShowLst',
        '{http://schemas.openxmlformats.org/presentationml/2006/main}photoAlbum',
        '{http://schemas.openxmlformats.org/presentationml/2006/main}custDataLst',
        '{http://schemas.openxmlformats.org/presentationml/2006/main}kinsoku',
        '{http://schemas.openxmlformats.org/presentationml/2006/main}defaultTextStyle',
        '{http://schemas.openxmlformats.org/presentationml/2006/main}extLst',
    ]

    # Extract all children
    children = list(root)
    for child in children:
        root.remove(child)

    # Sort children by schema order
    def get_order(elem):
        try:
            return element_order.index(elem.tag)
        except ValueError:
            return len(element_order)  # Unknown elements go at end

    children.sort(key=get_order)

    # Re-add in correct order
    for child in children:
        root.append(child)

    # Write back
    tree.write(pres_path, encoding='UTF-8', xml_declaration=True)
    print("  Reordered elements in: presentation.xml")
    return True


def repair_pptx(input_path: Path, output_path: Path) -> bool:
    """
    Repair a PPTX file by injecting missing Windows-required parts.

    Fixes:
    - Missing presProps.xml, viewProps.xml, tableStyles.xml
    - Missing <p:clrMap> in slide masters
    - Missing <p:clrMapOvr> in slide layouts and slides
    - Missing <a:prstGeom> on shapes
    - Missing <p:defaultTextStyle> in presentation.xml
    - Incorrect element ordering in presentation.xml

    Args:
        input_path: Path to the broken PPTX file
        output_path: Path for the repaired PPTX file

    Returns:
        True if repairs were made, False if file was already valid
    """
    print(f"Analyzing: {input_path}")
    repairs_made = False

    # Create temp directory for extraction
    with tempfile.TemporaryDirectory() as temp_dir:
        extract_dir = Path(temp_dir) / 'pptx_content'

        # Extract PPTX (it's a ZIP file)
        with zipfile.ZipFile(input_path, 'r') as zf:
            zf.extractall(extract_dir)

        # Fix 1: Check for missing presentation property files
        missing = check_missing_parts(extract_dir)
        if missing:
            print(f"  Found {len(missing)} missing file(s): {', '.join(missing.keys())}")
            print("Injecting missing files...")
            inject_missing_parts(extract_dir, missing)
            print("Updating relationships...")
            update_relationships(extract_dir, missing)
            print("Updating content types...")
            update_content_types(extract_dir, missing)
            repairs_made = True

        # Fix 2: Inject clrMap into slide masters if missing
        print("Checking slide masters for clrMap...")
        clrmap_fixes = inject_clrmap(extract_dir)
        if clrmap_fixes > 0:
            repairs_made = True

        # Fix 3: Inject clrMapOvr into slide layouts and slides if missing
        print("Checking layouts and slides for clrMapOvr...")
        clrmapovr_fixes = inject_clrmap_override(extract_dir)
        if clrmapovr_fixes > 0:
            repairs_made = True

        # Fix 4: Inject geometry into shapes if missing
        print("Checking shapes for geometry...")
        geom_fixes = inject_geometry(extract_dir)
        if geom_fixes > 0:
            repairs_made = True

        # Fix 5: Inject defaultTextStyle into presentation.xml if missing
        print("Checking presentation.xml for defaultTextStyle...")
        if inject_default_text_style(extract_dir):
            repairs_made = True

        # Fix 6: Reorder elements in presentation.xml to match schema
        print("Reordering presentation.xml elements...")
        reorder_presentation_elements(extract_dir)
        # Always count this as a repair since we always reorder

        if not repairs_made:
            print("  No repairs needed - file appears valid")
            shutil.copy2(input_path, output_path)
            return False

        # Repackage as PPTX
        print(f"Creating: {output_path}")
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for file_path in extract_dir.rglob('*'):
                if file_path.is_file():
                    arcname = file_path.relative_to(extract_dir)
                    zf.write(file_path, arcname)

        print("Repair complete!")
        return True


def main():
    parser = argparse.ArgumentParser(
        description='Repair PPTX files for Windows PowerPoint compatibility',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  %(prog)s presentation.pptx
  %(prog)s input.pptx -o output.pptx

Fixes applied if needed:
  - Missing ppt/presProps.xml (Presentation Properties)
  - Missing ppt/viewProps.xml (View Properties)
  - Missing ppt/tableStyles.xml (Table Styles)
  - Missing <p:clrMap> in slide masters (causes invisible content)
  - Missing <p:clrMapOvr> in slide layouts/slides (causes color issues)
  - Missing <a:prstGeom> on shapes (causes rendering failures)
  - Missing <p:defaultTextStyle> in presentation.xml (text fallback)
  - Incorrect element ordering in presentation.xml (schema compliance)

Reference: LibV2 "Accessible PowerPoint: OOXML Structure and WCAG 2.2 Compliance"
'''
    )
    parser.add_argument('input', type=Path, help='Input PPTX file to repair')
    parser.add_argument('-o', '--output', type=Path, help='Output path (default: input_fixed.pptx)')

    args = parser.parse_args()

    if not args.input.exists():
        print(f"Error: Input file not found: {args.input}")
        return 1

    if not args.input.suffix.lower() == '.pptx':
        print(f"Error: Input must be a .pptx file: {args.input}")
        return 1

    # Default output path
    if args.output:
        output_path = args.output
    else:
        output_path = args.input.with_stem(args.input.stem + '_fixed')

    try:
        repair_pptx(args.input, output_path)
        return 0
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == '__main__':
    exit(main())
