# Slideforge

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

**Transform structured content into professional PowerPoint presentations.**

AI-powered presentation generator that converts markdown outlines, JSON structures, and documents into well-designed PPTX files.

## Overview

Slideforge uses intelligent content transformation to create high-quality presentations from various input formats. Built for educators, business professionals, and anyone who needs to create presentations efficiently.

### Key Features

- **Multiple Input Formats**: Markdown, JSON outlines, plain text documents
- **Smart Content Transformation**: Automatically structures content for slides
- **Template Support**: Apply custom themes and corporate branding
- **Speaker Notes**: Detailed presenter notes generated automatically
- **Best Practices Built-in**: 6x6 rule, visual hierarchy, consistent styling
- **Slide Type Variety**: Title, content, comparison, image, quote slides

## Quick Start

### Installation

```bash
cd scripts
pip install -r requirements.txt
```

### Basic Usage

**From JSON:**
```bash
cd scripts/pptx-generator
python pptx_generator.py --input content.json --output presentation.pptx
```

**With Theme:**
```bash
python pptx_generator.py -i content.json -o output.pptx -t themes/corporate.pptx
```

### Python API

```python
from pptx_generator import PPTXGenerator

# Create presentation
generator = PPTXGenerator()
generator.add_title_slide("My Presentation", "Subtitle here")
generator.add_content_slide("Key Points", [
    "First important point",
    "Second important point",
    "Third important point"
])
generator.save("output.pptx")
```

## Input Formats

### Markdown

```markdown
# Presentation Title

## Introduction

### Overview
- First key point
- Second key point
- Third key point

## Main Content

### Details
- Supporting information
- Additional context
```

### JSON

```json
{
  "metadata": {
    "title": "Presentation Title",
    "author": "Your Name",
    "date": "2024-01-01"
  },
  "sections": [
    {
      "title": "Introduction",
      "slides": [
        {
          "type": "content",
          "title": "Overview",
          "content": {
            "bullets": ["Point 1", "Point 2", "Point 3"]
          },
          "notes": "Speaker notes here..."
        }
      ]
    }
  ]
}
```

## Slide Types

| Type | Description |
|------|-------------|
| `title` | Opening slide with title and subtitle |
| `section_header` | Section transition slide |
| `content` | Standard bullet point slide |
| `two_content` | Two-column layout |
| `comparison` | Side-by-side comparison with headers |
| `image` | Image-focused slide |
| `quote` | Quote with attribution |
| `blank` | Empty slide for custom content |

## Project Structure

```
/Slideforge/
├── CLAUDE.md           # AI orchestration guide
├── README.md           # This file
├── agents/             # AI agent specifications
├── scripts/
│   └── pptx-generator/ # Core generation module
├── schemas/
│   └── presentation/   # JSON schemas
├── templates/
│   └── pptx/          # Theme templates
├── inputs/            # Source content
└── exports/           # Generated presentations
```

## Design Principles

Slideforge follows presentation best practices:

- **6x6 Rule**: Maximum 6 bullet points per slide, 6 words per bullet
- **One Idea Per Slide**: Focus on a single concept
- **Visual Hierarchy**: Clear titles and logical flow
- **Speaker Notes**: Detailed notes for presenters
- **Consistent Styling**: Uniform layouts throughout

## Documentation

- [Getting Started](docs/getting-started.md) - Quick start guide
- [Workflow Reference](docs/workflow-reference.md) - Detailed protocols
- [Slide Design Guide](docs/slide-design-guide.md) - Design best practices

## Dependencies

```
python-pptx>=0.6.21
Pillow>=9.0.0
beautifulsoup4>=4.9.0
jsonschema>=4.0.0
```

## License

MIT License - See LICENSE file for details.

## Contributing

Contributions welcome! Please read our contributing guidelines before submitting PRs.
