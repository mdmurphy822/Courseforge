# Slideforge Schemas

JSON schemas for presentation content validation and structure definition.

## Schema Directory Structure

```
schemas/
├── README.md                    # This file
├── Claude.md                    # Schema development guidelines
├── presentation/                # Core presentation schemas
│   ├── presentation_schema.json # Main presentation structure
│   ├── theme_schema.json        # Theme configuration
│   ├── theme_catalog_schema.json # Theme registry
│   └── defaults.json            # Default configuration settings
└── accessibility/               # Accessibility compliance
    └── wcag22_compliance_schema.json
```

## Core Schemas

### Presentation Schema
**File**: `presentation/presentation_schema.json`

Defines the complete presentation structure:

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

### Defaults Configuration
**File**: `presentation/defaults.json`

Global default configuration settings for presentation generation. See [Configuration System Documentation](../docs/configuration-system.md) for details.

```json
{
  "quality_settings": {
    "max_bullets_per_slide": 6,
    "max_words_per_bullet": 6,
    "accessibility_requirements": {
      "alt_text_required": true,
      "color_contrast_minimum": 4.5
    }
  },
  "generation_settings": {
    "default_theme": "corporate",
    "default_template": "corporate.pptx"
  }
}
```

### Theme Schema
**File**: `presentation/theme_schema.json`

Defines theme configuration:

```json
{
  "name": "Theme Name",
  "description": "Theme description",
  "aspect_ratio": "16:9",
  "colors": {
    "primary": "#2c5aa0",
    "secondary": "#28a745",
    "accent": "#ffc107",
    "background": "#ffffff",
    "text_primary": "#333333",
    "text_secondary": "#666666"
  },
  "fonts": {
    "heading": {"family": "Arial", "weight": "bold"},
    "body": {"family": "Arial", "weight": "normal"}
  },
  "sizes": {
    "title": 44,
    "subtitle": 32,
    "section_header": 40,
    "slide_title": 32,
    "body": 24,
    "caption": 18
  }
}
```

## Slide Type Reference

### Title Slide
```json
{
  "type": "title",
  "title": "Main Title",
  "content": {
    "subtitle": "Subtitle text"
  },
  "notes": "Speaker notes"
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

### Two-Content Slide
```json
{
  "type": "two_content",
  "title": "Two Columns",
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
  "title": "Comparison",
  "content": {
    "left_title": "Option A",
    "left": ["Feature 1", "Feature 2"],
    "right_title": "Option B",
    "right": ["Feature 1", "Feature 2"]
  }
}
```

### Quote Slide
```json
{
  "type": "quote",
  "title": "",
  "content": {
    "text": "The quote text",
    "attribution": "Author Name"
  }
}
```

### Styled Content Slide
```json
{
  "type": "styled_content",
  "title": "Key Points",
  "content": {
    "bullets": ["Point 1", "Point 2"],
    "step_number": 1,
    "callout_text": "Important note",
    "callout_type": "tip"
  }
}
```

**Callout Types:**
- `info` - Blue, informational
- `success` - Green, positive
- `warning` - Yellow, caution
- `tip` - Purple, helpful hint

## Schema Validation

### Python Validation
```python
import json
import jsonschema

# Load schema
with open('schemas/presentation/presentation_schema.json') as f:
    schema = json.load(f)

# Load content
with open('your_presentation.json') as f:
    content = json.load(f)

# Validate
jsonschema.validate(content, schema)
print("Valid!")
```

### CLI Validation
```bash
# Using jsonschema CLI
jsonschema -i presentation.json schemas/presentation/presentation_schema.json
```

## Available Themes

Themes are defined in `templates/pptx/masters/registry.json`:

| Theme | Primary Color | Category |
|-------|---------------|----------|
| `corporate` | #2c5aa0 (Blue) | Business |
| `dark_mode` | #6c63ff (Purple) | Modern |
| `creative` | #ff6b35 (Orange) | Creative |
| `minimal` | #2d3436 (Charcoal) | Minimal |
| `educational` | #5c4d7d (Purple) | Education |

## Best Practices

### Content Guidelines
- Maximum 6 bullets per slide
- Maximum 6 words per bullet
- Always include speaker notes
- Use appropriate slide types for content

### Theme Selection
- `corporate` - Professional business presentations
- `dark_mode` - Tech talks, modern audiences
- `creative` - Pitches, creative content
- `minimal` - Content-focused, distraction-free
- `educational` - Training, learning materials

## Integration

### With PPTX Generator
```bash
python pptx_generator.py \
  --input presentation.json \
  --output output.pptx \
  --theme corporate
```

### Programmatic Usage
```python
from pptx_generator import PPTXGenerator

generator = PPTXGenerator(template_name="corporate")
generator.create_from_structure(content)
generator.save("output.pptx")
```

## Extending Schemas

### Adding Custom Slide Types
1. Add handler in `pptx_generator.py`
2. Update `presentation_schema.json` if needed
3. Document in this README

### Creating Custom Themes
1. Create `.pptx` master in `templates/pptx/custom/`
2. Register in `registry.json`
3. Define color scheme in registration

See `templates/pptx/custom/README.md` for detailed instructions.
