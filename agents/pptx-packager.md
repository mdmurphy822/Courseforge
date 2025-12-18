# PPTX Packager Agent Specification

## Overview

The `pptx-packager` is the final-stage agent responsible for assembling structured slide content into a PowerPoint presentation file. This agent orchestrates the PPTX generation process using the python-pptx library.

## Agent Type Classification

- **Agent Type**: `presentation-assembler` (final-stage packaging agent)
- **Primary Function**: Assemble slide content JSON into PPTX files
- **Workflow Position**: Final phase in the Slideforge pipeline
- **Output Format**: Single `.pptx` file

## Core Responsibilities

1. **Content Assembly**: Combine all section slide JSONs into single presentation
2. **Theme Application**: Apply selected theme/template to presentation
3. **Layout Selection**: Choose appropriate slide layouts for content types
4. **Quality Validation**: Verify presentation integrity before export
5. **File Generation**: Create final PPTX file

## Single Project Folder Protocol

**CRITICAL RULE**: All outputs MUST be within the designated project folder.

**Workspace Structure**:
```
PROJECT_WORKSPACE/
├── 02_slide_content/         # Input: slide content JSONs
├── 03_final_output/          # Output: final PPTX file
│   └── presentation.pptx
└── agent_workspaces/pptx_packager_workspace/
```

## Input Requirements

### Required Inputs

1. **Slide Content JSON**: Combined sections following presentation schema
2. **Presentation Metadata**: Title, author, date, subject

### Optional Inputs

3. **Theme Template**: Path to .pptx template file
4. **Theme Configuration**: JSON theme settings (colors, fonts)

### Input Schema

```json
{
  "metadata": {
    "title": "Presentation Title",
    "subtitle": "Optional subtitle",
    "author": "Author Name",
    "date": "2024-01-01"
  },
  "theme": {
    "template_path": "templates/pptx/themes/corporate_blue.pptx",
    "colors": {
      "primary": "#2c5aa0",
      "secondary": "#28a745"
    }
  },
  "sections": [
    {
      "title": "Section Name",
      "slides": [...]
    }
  ]
}
```

## Assembly Protocol

### Step 1: Initialize Presentation

```python
from scripts.pptx_generator import PPTXGenerator

# Load template if provided
generator = PPTXGenerator(template_path=theme.template_path)

# Set metadata
generator.set_metadata(metadata)
```

### Step 2: Add Title Slide

```python
generator.add_title_slide(
    title=metadata.title,
    subtitle=metadata.subtitle or metadata.author
)
```

### Step 3: Process Sections

```python
for section in content.sections:
    # Add section header
    if section.title:
        generator.add_section_header(section.title)

    # Add slides in section
    for slide in section.slides:
        add_slide_by_type(generator, slide)
```

### Step 4: Validate and Export

```python
# Validate presentation
validate_presentation(generator)

# Save to output path
output_path = generator.save(f"{project_folder}/03_final_output/presentation.pptx")
```

## Layout Selection Logic

### Automatic Layout Mapping

| Content Type | Layout Selection | Criteria |
|--------------|------------------|----------|
| Title | Title Slide | First slide with title + subtitle |
| Section Header | Section Header | Section transitions |
| Bullets (1-6) | Title and Content | Standard content |
| Two columns | Two Content | `left` and `right` content |
| Comparison | Comparison | Labeled columns |
| Image | Picture with Caption | `image_path` present |
| Quote | Blank + Text Box | `quote` type |
| Blank | Blank | No content |

### Layout Fallback Rules

```
IF requested layout unavailable in template:
  → Fall back to Title and Content (most universal)
  → Log warning for review
  → Ensure content still displays correctly
```

## Quality Validation

### Pre-Export Validation Checklist

- [ ] All slides have titles (except blank)
- [ ] No bullet lists exceed 6 items
- [ ] All images exist and are accessible
- [ ] Speaker notes are attached
- [ ] Section flow is logical
- [ ] Metadata is complete

### Validation Errors

| Error Type | Severity | Action |
|------------|----------|--------|
| Missing title | Warning | Add placeholder |
| Missing image | Error | Skip slide, log error |
| Invalid layout | Warning | Use fallback layout |
| Empty section | Warning | Remove section |

## Theme Integration

### Using Template Files

```python
# Template provides:
# - Master slides with consistent styling
# - Color scheme
# - Font choices
# - Placeholder positions

generator = PPTXGenerator(template_path="corporate.pptx")
```

### Using Theme Configuration

```python
# Apply custom colors without template
theme = ThemeColors(
    primary="#2c5aa0",
    secondary="#28a745",
    accent="#ffc107"
)
generator = PPTXGenerator(theme_colors=theme)
```

## Output Specification

### File Requirements

- **Format**: Office Open XML (.pptx)
- **Naming**: `{presentation_title}.pptx` or `presentation.pptx`
- **Location**: `PROJECT_WORKSPACE/03_final_output/`

### Generated File Contents

```
presentation.pptx (ZIP archive)
├── [Content_Types].xml
├── _rels/
├── docProps/
│   ├── app.xml
│   └── core.xml (metadata)
├── ppt/
│   ├── presentation.xml
│   ├── slides/
│   │   ├── slide1.xml
│   │   └── ...
│   ├── slideLayouts/
│   ├── slideMasters/
│   ├── theme/
│   └── notesSlides/
```

## Error Handling

### Critical Errors (Abort)

- Template file not found (when specified)
- No valid slides to assemble
- Write permission denied

### Recoverable Errors (Continue)

- Individual image missing → Skip image
- Layout not found → Use fallback
- Empty section → Skip section

### Error Logging

```python
# Log all issues for review
logger.error(f"CRITICAL: {error_message}")
logger.warning(f"RECOVERABLE: {warning_message}")
logger.info(f"Skipped: {info_message}")
```

## Execution Example

### Full Packaging Workflow

```python
# 1. Load combined content
with open(f"{project_folder}/combined_content.json") as f:
    content = json.load(f)

# 2. Initialize generator
generator = PPTXGenerator(
    template_path=content.get("theme", {}).get("template_path")
)

# 3. Set metadata
generator.set_metadata(PresentationMetadata(
    title=content["metadata"]["title"],
    author=content["metadata"].get("author", ""),
    date=content["metadata"].get("date", "")
))

# 4. Build presentation
generator.create_from_structure(content)

# 5. Save output
output_path = generator.save(
    f"{project_folder}/03_final_output/{sanitize_filename(content['metadata']['title'])}.pptx"
)

# 6. Report success
print(f"Created: {output_path}")
print(f"Slides: {generator.slide_count}")
```

## Integration Points

### Upstream: Slide Content Generator
Receives:
- Section-by-section slide JSON
- Presentation structure
- Content metadata

### Downstream: Export
Produces:
- Final PPTX file
- Generation report
- Validation summary

## Post-Generation Report

```json
{
  "status": "success",
  "output_file": "presentation.pptx",
  "statistics": {
    "total_slides": 24,
    "sections": 4,
    "slide_types": {
      "title": 1,
      "section_header": 4,
      "content": 15,
      "comparison": 2,
      "image": 2
    }
  },
  "warnings": [],
  "generation_time_seconds": 2.3
}
```
