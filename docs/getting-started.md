# Getting Started Guide

## Welcome to Slideforge

This guide walks you through creating your first professional PowerPoint presentation using Slideforge's AI-powered multi-agent system.

## Prerequisites

### Technical Requirements
- **Python 3.8+**: Required for running the PPTX generator
- **Claude Code Access**: For AI-powered content generation
- **Virtual Environment**: Recommended for dependency management

### Dependencies
```bash
# Activate the project virtual environment
source scripts/venv/bin/activate

# Or install dependencies manually
pip install python-pptx Pillow jsonschema
```

## Quick Start (5 minutes)

### Step 1: Prepare Your Content

Create a JSON file with your presentation structure:

```json
{
  "metadata": {
    "title": "My Presentation",
    "subtitle": "A Brief Overview",
    "author": "Your Name",
    "date": "2025-12-17"
  },
  "sections": [
    {
      "title": "Introduction",
      "slides": [
        {
          "type": "title",
          "title": "My Presentation",
          "content": {"subtitle": "A Brief Overview"}
        }
      ]
    },
    {
      "title": "Main Content",
      "slides": [
        {
          "type": "content",
          "title": "Key Points",
          "content": {
            "bullets": [
              "First important point",
              "Second important point",
              "Third important point"
            ]
          },
          "notes": "Speaker notes go here"
        }
      ]
    }
  ]
}
```

### Step 2: Generate Your Presentation

```bash
cd scripts/pptx-generator

# Basic generation
python pptx_generator.py \
  --input your_content.json \
  --output presentation.pptx

# With a theme
python pptx_generator.py \
  --input your_content.json \
  --output presentation.pptx \
  --theme corporate
```

### Step 3: Open and Review

Open `presentation.pptx` in PowerPoint, LibreOffice Impress, or Google Slides.

## Available Themes

List available themes:
```bash
python pptx_generator.py --list-templates
```

| Theme | Description | Best For |
|-------|-------------|----------|
| `corporate` | Professional blue (#2c5aa0) | Business presentations |
| `dark_mode` | Dark with vibrant accents | Tech, modern audiences |
| `creative` | Bold orange/navy | Creative pitches |
| `minimal` | Clean charcoal | Content-focused |
| `educational` | Warm purple/brown | Training, learning |

## Input Formats

### JSON Structure
The recommended format for full control:

```json
{
  "metadata": {
    "title": "Presentation Title",
    "subtitle": "Optional Subtitle",
    "author": "Author Name",
    "date": "2025-12-17",
    "subject": "Topic description"
  },
  "sections": [
    {
      "title": "Section Name",
      "slides": [...]
    }
  ]
}
```

### Markdown (Simple)
For quick presentations:

```markdown
# Presentation Title

## Section 1: Introduction

### First Slide
- Bullet point one
- Bullet point two

### Second Slide
- More content
- Additional points
```

## Slide Types

### Title Slide
```json
{
  "type": "title",
  "title": "Main Title",
  "content": {"subtitle": "Subtitle text"}
}
```

### Content Slide
```json
{
  "type": "content",
  "title": "Slide Title",
  "content": {
    "bullets": ["Point 1", "Point 2", "Point 3"]
  },
  "notes": "Speaker notes"
}
```

### Two-Column Layout
```json
{
  "type": "two_content",
  "title": "Comparison",
  "content": {
    "left": ["Left item 1", "Left item 2"],
    "right": ["Right item 1", "Right item 2"]
  }
}
```

### Comparison Slide
```json
{
  "type": "comparison",
  "title": "Before vs After",
  "content": {
    "left_title": "Before",
    "left": ["Old way 1", "Old way 2"],
    "right_title": "After",
    "right": ["New way 1", "New way 2"]
  }
}
```

### Quote Slide
```json
{
  "type": "quote",
  "title": "",
  "content": {
    "text": "The quote text goes here.",
    "attribution": "Author Name"
  }
}
```

### Styled Content (with callouts)
```json
{
  "type": "styled_content",
  "title": "Key Information",
  "content": {
    "bullets": ["Point 1", "Point 2"],
    "step_number": 1,
    "callout_text": "Important tip here",
    "callout_type": "tip"
  }
}
```

Callout types: `info`, `success`, `warning`, `tip`

## Using AI Agents

For complex presentations, use the orchestrated agent workflow:

### 1. Content Analysis
The system analyzes your source content and creates a structured outline.

### 2. Slide Generation
Individual agents generate content for each section in parallel batches.

### 3. Layout Mapping
Optimal slide layouts are selected based on content type.

### 4. Validation
Quality checks ensure consistency and completeness.

### 5. Packaging
Final PPTX is assembled with your chosen theme.

## Best Practices

### Content Guidelines
- **6x6 Rule**: Maximum 6 bullets, 6 words per bullet
- **One Idea Per Slide**: Focus each slide on a single concept
- **Visual Hierarchy**: Use clear titles and supporting points

### Speaker Notes
Always include speaker notes for context:
```json
{
  "type": "content",
  "title": "Slide Title",
  "content": {"bullets": [...]},
  "notes": "Key talking points and additional context for the presenter."
}
```

## Project Structure

```
Slideforge/
├── scripts/pptx-generator/     # Core generation scripts
│   ├── pptx_generator.py       # Main generator
│   └── template_loader.py      # Theme management
├── templates/pptx/             # PPTX templates
│   ├── masters/                # Theme master files
│   ├── themes/                 # Theme configurations
│   └── examples/               # Example presentations
├── schemas/presentation/       # JSON schemas
├── exports/                    # Generated output
└── examples/                   # Example files
```

## Troubleshooting

### Common Issues

**Module not found: pptx**
```bash
source scripts/venv/bin/activate
# or
pip install python-pptx
```

**Theme not loading**
- Verify theme name with `--list-templates`
- Check that master PPTX files exist in `templates/pptx/masters/`

**Empty slides**
- Ensure JSON structure follows the schema
- Verify `content` object contains appropriate fields for slide type

## Next Steps

1. **Explore Examples**: Check `examples/` for sample presentations
2. **Customize Themes**: Create custom themes in `templates/pptx/custom/`
3. **Read Design Guide**: See `docs/slide-design-guide.md` for best practices
4. **Check Schemas**: Review `schemas/presentation/` for full JSON structure

## Getting Help

- **Documentation**: `docs/` directory
- **Troubleshooting**: `docs/troubleshooting.md`
- **Examples**: `examples/` and `templates/pptx/examples/`
