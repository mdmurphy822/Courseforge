# Custom Branding Templates

Place your custom PowerPoint template files (`.pptx`) in this directory to use them with the Slideforge presentation generator.

## How to Use Custom Templates

1. **Create or obtain a PPTX template** with your branding (logos, colors, fonts)
2. **Copy the file** to this `custom/` directory
3. **Use the template** via CLI:
   ```bash
   python pptx_generator.py -i content.json -o output.pptx -t custom/my_brand.pptx
   ```

## Template Requirements

For best results, your custom template should include:

### Standard Slide Layouts (Required)
Your template should have these layouts at the specified indices:

| Index | Layout Type | Description |
|-------|-------------|-------------|
| 0 | Title Slide | Main title + subtitle |
| 1 | Title and Content | Title + bullet points |
| 2 | Section Header | Section divider |
| 3 | Two Content | Two columns |
| 4 | Comparison | Two columns with headers |
| 5 | Title Only | Title with empty area |
| 6 | Blank | Completely empty |

### Cross-Platform Compatibility

**Use these fonts** (available on Windows, macOS, and Linux):
- Arial (recommended)
- Calibri
- Times New Roman
- Georgia

**Avoid these fonts** (may not render correctly):
- Ubuntu
- Liberation Sans
- DejaVu Sans
- Any custom/purchased fonts

### Color Guidelines

- Use RGB hex colors (e.g., `#2c5aa0`)
- Ensure text contrast meets WCAG 2.1 AA standards (4.5:1 ratio)
- Test your template in both PowerPoint and LibreOffice Impress

## Creating a Template

### Option 1: PowerPoint (Windows/macOS)
1. Open PowerPoint
2. View > Slide Master
3. Customize colors, fonts, and layouts
4. Save as `.pptx` file

### Option 2: LibreOffice Impress (Linux)
1. Open LibreOffice Impress
2. View > Master Slide
3. Customize styling
4. File > Save As > ODP format, then export to PPTX

### Option 3: Modify Existing Template
1. Copy a template from `../masters/`
2. Open in your presentation software
3. Modify colors, add logo, etc.
4. Save to this `custom/` directory

## Template Metadata (Optional)

To register your custom template with full metadata, add an entry to `../masters/registry.json`:

```json
{
  "my_brand": {
    "path": "../custom/my_brand.pptx",
    "name": "My Company Brand",
    "description": "Official company branding template",
    "category": "custom",
    "colors": {
      "primary": "#your_color",
      "secondary": "#your_color",
      "accent": "#your_color"
    },
    "layouts": {
      "title": 0,
      "content": 1,
      "section_header": 2
    }
  }
}
```

## Troubleshooting

### Fonts not rendering correctly
- Stick to system fonts (Arial, Calibri)
- Embed fonts if using PowerPoint

### Layout mismatch errors
- Ensure your template has at least 7 slide layouts
- Check layout indices match the expected order

### Colors look different
- Use RGB hex values, not theme colors
- Test in both PowerPoint and LibreOffice

## Need Help?

Check the main documentation at `docs/` or the generator README at `scripts/pptx-generator/README.md`.
