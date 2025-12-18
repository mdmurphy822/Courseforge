# Slideforge Examples

Example presentations and JSON content files demonstrating Slideforge capabilities.

## Generated PPTX Examples

Ready-to-use example presentations in `presentations/`:

| File | Template | Description |
|------|----------|-------------|
| `k12_science.pptx` | Educational | High school science introduction |
| `business_food.pptx` | Corporate | Farm-to-table business pitch |
| `driving_guide.pptx` | Minimal | New driver instruction guide |
| `chili_recipes.pptx` | Creative | Chili cooking recipes |

Each demonstrates different slide types and template styling.

---

## JSON Source Files

### Psychology Introduction
**File:** `templates/pptx/examples/psychology_intro.json`

An introductory psychology presentation demonstrating educational content:
- 5 sections with 16 slides
- Multiple slide types (title, content, comparison, two_content, quote, section_header)
- Comprehensive speaker notes for presenters
- 6x6 rule compliance throughout

**To generate PPTX:**
```bash
cd scripts/pptx-generator
python pptx_generator.py -i ../../templates/pptx/examples/psychology_intro.json -o ../../examples/psychology_presentation.pptx -t ../../templates/pptx/masters/educational.pptx
```

---

### Beekeeping Presentation
**File:** `templates/pptx/examples/beekeeping_example.json`

An educational presentation about beekeeping basics demonstrating:
- Multiple section organization
- Various slide types (title, content, comparison)
- Speaker notes for each slide
- 6x6 rule compliance

**To generate PPTX:**
```bash
cd scripts/pptx-generator
python pptx_generator.py -i ../../templates/pptx/examples/beekeeping_example.json -o ../../examples/beekeeping.pptx
```

### Minimal Example
**File:** `templates/pptx/examples/minimal_example.json`

The simplest valid Slideforge presentation showing:
- Required metadata fields
- Basic slide structure
- Minimal content organization

## Using Templates

Apply a template theme when generating:
```bash
# With corporate template
python pptx_generator.py -i content.json -o output.pptx -t ../../templates/pptx/masters/corporate.pptx

# Available templates: corporate, corporate_blue, creative, dark_mode, educational, minimal, stout
```

## JSON Structure

All presentation JSON files follow this structure:
```json
{
  "metadata": {
    "title": "Presentation Title",
    "subtitle": "Optional subtitle",
    "author": "Author Name",
    "date": "2025"
  },
  "sections": [
    {
      "title": "Section Name",
      "slides": [
        {
          "type": "content",
          "title": "Slide Title",
          "content": {
            "bullets": ["Point 1", "Point 2"]
          },
          "notes": "Speaker notes here"
        }
      ]
    }
  ]
}
```

## Slide Types

| Type | Description |
|------|-------------|
| `title` | Title slide with subtitle |
| `content` | Bullet point slide |
| `comparison` | Two-column comparison |
| `two_content` | Two-column content |
| `image` | Image slide |
| `quote` | Quote display |
| `section_header` | Section divider |
| `blank` | Empty slide |
