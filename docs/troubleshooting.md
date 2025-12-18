# Slideforge Troubleshooting Guide

Common issues and solutions for PPTX presentation generation.

---

## Quick Reference

| Issue | Likely Cause | Solution |
|-------|--------------|----------|
| Module not found | Missing dependencies | Activate venv or install python-pptx |
| Theme not loading | Invalid theme name | Use `--list-templates` to verify |
| Empty slides | Malformed JSON | Validate against schema |
| Layout issues | Wrong slide type | Check slide type documentation |
| Styling not applied | No theme specified | Add `--theme` flag |

---

## Installation Issues

### ModuleNotFoundError: No module named 'pptx'

**Cause**: python-pptx not installed or virtual environment not activated.

**Solution**:
```bash
# Option 1: Activate project virtual environment
source scripts/venv/bin/activate

# Option 2: Install directly
pip install python-pptx Pillow
```

### ImportError: template_loader

**Cause**: Running script from wrong directory.

**Solution**:
```bash
cd scripts/pptx-generator
python pptx_generator.py --help
```

---

## Theme Issues

### Theme Not Found

**Symptom**: Warning "Template 'xxx' not found, using default"

**Cause**: Invalid theme name or missing template file.

**Solution**:
```bash
# List available themes
python pptx_generator.py --list-templates

# Verify template files exist
ls templates/pptx/masters/
```

**Available themes**: `corporate`, `corporate_blue`, `creative`, `dark_mode`, `educational`, `minimal`, `stout`

### Styles Not Applying

**Cause**: Theme colors defined but master template missing.

**Solution**:
1. Ensure `.pptx` master file exists in `templates/pptx/masters/`
2. Verify `registry.json` has correct path
3. Check file permissions

---

## Content Issues

### Empty Slides Generated

**Causes**:
- Missing `content` object in slide definition
- Wrong field names for slide type
- Empty arrays

**Solution**: Verify JSON structure matches slide type:

```json
// Content slide requires "bullets" array
{
  "type": "content",
  "title": "My Slide",
  "content": {
    "bullets": ["Point 1", "Point 2"]
  }
}

// Two-content requires "left" and "right" arrays
{
  "type": "two_content",
  "title": "Comparison",
  "content": {
    "left": ["Left 1"],
    "right": ["Right 1"]
  }
}
```

### Slide Type Not Recognized

**Symptom**: Slide renders as basic content instead of expected layout.

**Cause**: Invalid `type` value.

**Valid types**:
- `title` - Title slide
- `section_header` - Section divider
- `content` - Bullet points
- `two_content` - Two columns
- `comparison` - Labeled columns
- `quote` - Quote display
- `image` - Image slide
- `blank` - Empty slide
- `styled_content` - Content with callouts

### Missing Speaker Notes

**Cause**: Notes field not included or empty.

**Solution**:
```json
{
  "type": "content",
  "title": "Slide Title",
  "content": {"bullets": ["..."]},
  "notes": "Speaker notes appear here in presenter view."
}
```

---

## Layout Issues

### Text Overflowing Slides

**Cause**: Too much content for slide type.

**Solutions**:
1. Follow 6x6 rule: max 6 bullets, 6 words each
2. Split into multiple slides
3. Use two-column layout for comparisons

### Callout Box Not Appearing

**Cause**: Using `content` type instead of `styled_content`.

**Solution**:
```json
{
  "type": "styled_content",
  "title": "Key Info",
  "content": {
    "bullets": ["Point 1", "Point 2"],
    "callout_text": "Important note",
    "callout_type": "tip"
  }
}
```

**Callout types**: `info` (blue), `success` (green), `warning` (yellow), `tip` (purple)

---

## File Issues

### Output File Not Created

**Causes**:
- Invalid output path
- Permission denied
- JSON parsing error

**Solution**:
```bash
# Check for errors in output
python pptx_generator.py -i input.json -o output.pptx 2>&1

# Verify input JSON is valid
python -c "import json; json.load(open('input.json'))"
```

### Overwriting Existing File

**Behavior**: Existing files are overwritten without warning.

**Prevention**: Use timestamped filenames:
```bash
python pptx_generator.py -i input.json -o "presentation_$(date +%Y%m%d_%H%M%S).pptx"
```

---

## JSON Validation

### Schema Validation

Validate your JSON against the presentation schema:

```python
import json
import jsonschema

with open('schemas/presentation/presentation_schema.json') as f:
    schema = json.load(f)

with open('your_presentation.json') as f:
    content = json.load(f)

jsonschema.validate(content, schema)
```

### Common JSON Errors

**Missing commas**:
```json
// Wrong
{
  "title": "Slide 1"
  "content": {}
}

// Correct
{
  "title": "Slide 1",
  "content": {}
}
```

**Trailing commas**:
```json
// Wrong (JSON doesn't allow trailing commas)
{
  "bullets": [
    "Point 1",
    "Point 2",
  ]
}

// Correct
{
  "bullets": [
    "Point 1",
    "Point 2"
  ]
}
```

---

## Performance Issues

### Slow Generation

**Causes**:
- Large number of slides
- High-resolution images
- Complex styled content

**Solutions**:
1. Batch large presentations into sections
2. Optimize images before including
3. Use simpler slide types where possible

### Memory Errors

**Cause**: Very large presentations or memory-intensive operations.

**Solution**:
```bash
# Generate in sections
python pptx_generator.py -i section1.json -o section1.pptx
python pptx_generator.py -i section2.json -o section2.pptx
# Combine in PowerPoint
```

---

## Agent Workflow Issues

### Batch Size Exceeded

**Symptom**: Agents not completing or timing out.

**Cause**: More than 10 simultaneous Task calls.

**Solution**: Limit to 10 agents per batch, wait for completion before next batch.

### Section Not Generated

**Cause**: Agent received multi-section prompt.

**Solution**: One agent = one section. Never ask an agent to create multiple sections.

---

## Validation Checklist

### Before Generation
- [ ] JSON is valid (no syntax errors)
- [ ] All slides have `type` field
- [ ] Content fields match slide type
- [ ] Bullet arrays are not empty

### After Generation
- [ ] PPTX opens in PowerPoint/LibreOffice
- [ ] All slides render correctly
- [ ] Theme colors applied
- [ ] Speaker notes present

---

## Getting Help

If issues persist:

1. **Check examples**: `templates/pptx/examples/beekeeping_example.json`
2. **Review schemas**: `schemas/presentation/`
3. **Test with minimal input**: Create simple 2-slide presentation first
4. **Check logs**: Generator outputs INFO/WARNING messages

---

## Error Messages Reference

| Error | Meaning | Fix |
|-------|---------|-----|
| `Layout index X not found` | Theme missing layouts | Use different theme or check master file |
| `Image not found` | Image path invalid | Use absolute path or verify file exists |
| `No module named 'pptx'` | Dependency missing | `pip install python-pptx` |
| `JSONDecodeError` | Invalid JSON syntax | Validate JSON structure |
| `KeyError: 'content'` | Missing required field | Add `content` object to slide |
