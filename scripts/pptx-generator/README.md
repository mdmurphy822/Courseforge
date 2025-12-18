# PPTX Generator

Core PowerPoint generation module for Slideforge.

## Overview

This module provides the functionality to create PPTX files from structured content using the python-pptx library.

## Features

- **Template Support**: Use existing PPTX files as themes
- **Multiple Slide Types**: Title, content, comparison, image, quote, and more
- **Speaker Notes**: Full support for presenter notes
- **Structured Input**: Create from JSON or markdown
- **Accessibility**: Alt text support for images

## Usage

### Python API

```python
from pptx_generator import PPTXGenerator

# Create generator (optionally with template)
generator = PPTXGenerator(template_path="theme.pptx")

# Add slides
generator.add_title_slide("Presentation Title", "Subtitle")
generator.add_content_slide("Topic", ["Point 1", "Point 2", "Point 3"])
generator.add_comparison_slide(
    "Comparison",
    "Option A", ["Pro 1", "Pro 2"],
    "Option B", ["Pro 1", "Pro 2"]
)

# Save
generator.save("output.pptx")
```

### From JSON

```python
from pptx_generator import create_presentation_from_json

create_presentation_from_json(
    json_path="content.json",
    output_path="output.pptx",
    template_path="theme.pptx"  # optional
)
```

### From Markdown

```python
from pptx_generator import create_presentation_from_markdown

markdown = """
# My Presentation

## Introduction

### Overview
- First point
- Second point
- Third point

## Main Content

### Key Concepts
- Concept A
- Concept B
"""

create_presentation_from_markdown(markdown, "output.pptx")
```

### CLI

```bash
python pptx_generator.py --input content.json --output presentation.pptx
python pptx_generator.py -i content.json -o presentation.pptx -t theme.pptx
```

## JSON Schema

```json
{
  "metadata": {
    "title": "Presentation Title",
    "subtitle": "Optional subtitle",
    "author": "Author Name",
    "date": "2024-01-01"
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

| Type | Description | Content Fields |
|------|-------------|----------------|
| `title` | Title slide | `subtitle` |
| `section_header` | Section divider | `subtitle` |
| `content` | Bullet points | `bullets` |
| `two_content` | Two columns | `left`, `right` |
| `comparison` | Labeled columns | `left_title`, `left`, `right_title`, `right` |
| `image` | Image slide | `image_path`, `alt_text` |
| `quote` | Quote slide | `text`, `attribution` |
| `blank` | Empty slide | - |

## Dependencies

- python-pptx >= 0.6.21
- Pillow >= 9.0.0 (for image handling)
