# Schemas Directory

This directory contains JSON schemas for presentation content validation and theme configuration.

## Directory Structure

### `/presentation/`
Core presentation schemas:
- `presentation_schema.json` - Main presentation structure
- `theme_schema.json` - Theme configuration
- `theme_catalog_schema.json` - Theme registry
- `defaults.json` - Default configuration settings

### `/accessibility/`
WCAG 2.2 AA compliance schemas:
- Accessibility markup requirements
- Screen reader compatibility specifications
- Color contrast validation

## Usage Guidelines

1. **Schema Validation**: All presentation content must validate against appropriate schemas
2. **Version Control**: Maintain schema versions with backward compatibility
3. **Documentation**: Each schema file includes comprehensive comments and examples
4. **Testing**: Schema compliance validated during generation

## Key Schemas

### Presentation Schema
Defines complete presentation structure:
- Metadata (title, author, date)
- Sections array with slides
- Theme configuration

### Slide Schema
Defines supported slide types:
- `title` - Title slide
- `section_header` - Section divider
- `content` - Bullet points
- `two_content` - Two columns
- `comparison` - Labeled columns
- `quote` - Quote display
- `image` - Image slide
- `styled_content` - Content with callouts

### Theme Schema
Defines theme configuration:
- Color palette (primary, secondary, accent)
- Font families and sizes
- Spacing and margins

## Validation

```python
import json
import jsonschema

with open('schemas/presentation/presentation_schema.json') as f:
    schema = json.load(f)

jsonschema.validate(content, schema)
```
