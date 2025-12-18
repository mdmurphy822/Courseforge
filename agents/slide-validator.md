# Slide Validator Agent Specification

## Overview

The `slide-validator` is a quality assurance agent that validates presentation content against design best practices, schema requirements, and accessibility standards. This agent ensures presentations meet quality thresholds before final packaging.

## Agent Type Classification

- **Agent Type**: `slide-validator` (quality assurance subagent)
- **Primary Function**: Validate presentation content and report issues
- **Workflow Position**: Phase 4 quality validation in the Slideforge pipeline
- **Output Format**: Validation report JSON

## Core Validation Rules

### 6x6 Rule Compliance

**Bullet Count Check**:
- Maximum 6 bullet points per slide
- Applies to: `bullets`, `left`, `right` arrays
- Severity: Warning (allows override)

**Word Count Check**:
- Target: ~6 words per bullet (flexible guideline)
- Maximum: 12 words per bullet (hard limit)
- Severity: Info for 7-12 words, Warning for 12+

### Speaker Notes Validation

**Coverage Requirements**:
- Target: 80% of content slides have notes
- Required for: `content`, `two_content`, `comparison` slide types
- Severity: Warning when below target

**Notes Quality**:
- Minimum 20 words for substantive notes
- Should expand on bullet points
- Should provide presenter context

### Structural Validation

**Section Requirements**:
- Each section should have a title
- Sections should have 3-10 slides (warning outside range)
- Empty sections are errors

**Slide Type Distribution**:
- Presentations should use 2+ slide types
- Overreliance on single type triggers warning

## Container Validation Rules

### Callout Slides
- [ ] callout_type must be one of: info, tip, warning, success
- [ ] text is required and max 200 characters
- [ ] heading is optional
- [ ] Maximum 4 callouts per slide
- [ ] Avoid more than 3 callout slides in a presentation

### Stats Grid Slides
- [ ] Minimum 2, maximum 6 stats per slide
- [ ] Each stat must have value and label
- [ ] value should be concise (max 10 characters recommended)
- [ ] trend must be one of: up, down, neutral, none
- [ ] Avoid more than 2 consecutive stats_grid slides

### Cards Grid Slides
- [ ] Minimum 2, maximum 6 cards per slide
- [ ] Each card must have a title
- [ ] items array max 4 bullets per card
- [ ] color must be one of: default, primary, secondary, accent
- [ ] Bullet counts should be balanced across cards

### Key Concept Slides
- [ ] concept_title is required (max 50 characters)
- [ ] definition is required (max 200 characters)
- [ ] details array max 4 items
- [ ] concept_style must be one of: boxed, highlighted, minimal
- [ ] Limit to 2 key_concept slides per section

### Inline Containers
- [ ] Maximum 4 containers per content slide
- [ ] container_type is required
- [ ] Container-specific validation applies based on type
- [ ] Containers should complement, not replace, main content

### Agenda Slides
- [ ] agenda_items is required array with 2-8 items
- [ ] Each item must have section (string, max 60 characters)
- [ ] description is optional (string, max 100 characters)
- [ ] status must be one of: complete, current, upcoming
- [ ] agenda_style must be one of: numbered, checkmarks, progress_bar
- [ ] Only one item should have status="current"
- [ ] Agenda slide should appear near beginning of presentation

### Divider Slides
- [ ] title is required (string)
- [ ] section_number is optional (max 3 characters, e.g., "01", "A")
- [ ] subtitle is optional (max 80 characters)
- [ ] divider_style must be one of: bold, minimal, graphic, numbered
- [ ] accent_color must be one of: primary, secondary, accent
- [ ] Divider slides should mark major section transitions

### Data Viz Slides
- [ ] chart_type is required, must be one of: bar, column, line, pie, doughnut, area, scatter, radar, combo
- [ ] chart_data.categories is required array (max 12 items)
- [ ] chart_data.series is required array (1-6 series)
- [ ] Each series must have name (string) and values (array)
- [ ] values array length must match categories array length
- [ ] For pie/doughnut charts, only first series is used (warn if multiple)
- [ ] Chart should have descriptive title
- [ ] Include data source in speaker notes

### Image Grid Slides
- [ ] images is required array (2-9 items)
- [ ] Each image must have path (string)
- [ ] caption is optional (max 50 characters per image)
- [ ] alt_text is recommended for accessibility
- [ ] grid_layout must be valid: auto, 2x1, 1x2, 2x2, 3x1, 1x3, 2x3, 3x2, 3x3
- [ ] gap_size must be one of: small, medium, large
- [ ] Verify image paths exist (warning if not found)
- [ ] Maximum 9 images to maintain visual clarity

## Container Usage Guidelines (Quality Warnings)

| Condition | Severity | Message |
|-----------|----------|---------|
| >3 callout slides in presentation | Warning | Overuse reduces impact |
| >2 stats_grid slides in sequence | Warning | Consider varying visuals |
| cards_grid with only 1 card | Error | Use content slide instead |
| key_concept without definition | Error | Definition required |
| stats_grid with >6 items | Error | Split into multiple slides |
| Empty containers array | Warning | Remove if not used |
| >1 agenda slide in presentation | Warning | Multiple agendas confuse flow |
| agenda_items with <2 items | Error | Use content slide instead |
| Multiple agenda items with status="current" | Error | Only one item can be current |
| data_viz with >12 categories | Warning | Chart becomes unreadable |
| data_viz series values mismatch categories | Error | Array lengths must match |
| Pie chart with >1 series | Warning | Only first series will be used |
| image_grid with only 1 image | Error | Use image slide instead |
| image_grid with >9 images | Error | Reduces visual impact |
| image_grid with missing image paths | Warning | Verify all paths exist |
| divider slide not at section boundary | Warning | Should mark section transitions |

### Schema Compliance

**Required Fields**:
- `metadata.title` - Presentation must have title
- `sections` - At least one section required
- `slides[].type` - Every slide needs a type

**Type-Specific Requirements**:
- `title` slides: require `content.subtitle`
- `comparison` slides: require `left_title`, `right_title`
- `image` slides: require `image_path`, `alt_text`
- `quote` slides: require `content.text`
- `callout` slides: require `callouts` array with valid callout_type
- `stats_grid` slides: require `stats` array with value, label, trend
- `cards_grid` slides: require `cards` array with title
- `key_concept` slides: require `concept_title`, `definition`
- `agenda` slides: require `agenda_items` array with section, status
- `divider` slides: require `title` and valid divider_style, accent_color
- `data_viz` slides: require `chart_type`, `chart_data` with categories and series
- `image_grid` slides: require `images` array with path for each image

## Validation Report Format

```json
{
  "valid": true,
  "score": 85.5,
  "summary": "Good quality with minor improvements possible",
  "metrics": {
    "slide_count": 15,
    "section_count": 4,
    "notes_coverage": 80.0,
    "six_six_violations": 3,
    "slide_type_variety": 4
  },
  "issues": [
    {
      "severity": "warning",
      "category": "6x6_rule",
      "location": "Section 2, Slide 3",
      "message": "7 bullets exceeds maximum of 6",
      "suggestion": "Split content across multiple slides"
    }
  ],
  "scores": {
    "content": 90.0,
    "notes": 80.0,
    "structure": 85.0,
    "variety": 75.0
  }
}
```

## Severity Levels

| Level | Description | Impact on Score |
|-------|-------------|-----------------|
| `error` | Blocks generation, must fix | -20 points |
| `warning` | Should fix, affects quality | -5 points |
| `info` | Suggestion for improvement | -1 point |

## Score Calculation

**Component Weights**:
- Content (6x6 compliance): 35%
- Speaker Notes: 25%
- Structure: 20%
- Variety: 20%

**Pass Threshold**: 70/100

**Grade Mapping**:
- 90+: Excellent
- 80-89: Good
- 70-79: Acceptable
- 50-69: Needs Improvement
- <50: Poor

## Single Project Folder Protocol

**Workspace Structure**:
```
PROJECT_WORKSPACE/
├── 02_slide_content/           # Content to validate
├── 04_validation/              # Validation outputs
│   ├── validation_report.json
│   └── issues_summary.md
└── agent_workspaces/slide_validator_workspace/
```

## Validation Workflow

### Step 1: Load Content
```python
# Load all section JSON files from 02_slide_content/
# Merge into complete presentation structure
```

### Step 2: Schema Validation
```python
# Validate against presentation_schema.json
# Check required fields and type constraints
```

### Step 3: Quality Checks
```python
# Run 6x6 rule checks
# Check speaker notes coverage
# Analyze structure and balance
# Calculate slide type variety
```

### Step 4: Generate Report
```python
# Compile all issues
# Calculate scores
# Generate summary and recommendations
```

## Integration Points

### Input From
- `slide-content-generator`: Section JSON files
- `presentation-outliner`: Expected structure

### Output To
- `pptx-packager`: Validation status
- Orchestrator: Go/no-go decision

## Quick Validation Checklist

**Before Passing to Packager**:
- [ ] Schema validates successfully
- [ ] Score >= 70 (pass threshold)
- [ ] No error-severity issues
- [ ] All required metadata present
- [ ] Image paths exist (if used)

## CLI Integration

```bash
# Validate a presentation JSON
slideforge validate presentation content.json

# Validate with verbose output
slideforge validate presentation content.json --verbose

# Output as JSON report
slideforge validate presentation content.json --json-output
```

## Error Recovery

**When Validation Fails**:
1. Log all issues to `04_validation/issues_summary.md`
2. Return detailed report to orchestrator
3. Orchestrator decides: fix issues or abort
4. Re-run validation after fixes
