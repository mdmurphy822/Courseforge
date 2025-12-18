# Slide Layout Mapper Agent Specification

## Overview

The `slide-layout-mapper` is a specialized agent for selecting optimal slide layouts based on content characteristics. This agent analyzes content structure and recommends appropriate slide types for maximum visual impact.

## Agent Type Classification

- **Agent Type**: `slide-layout-mapper` (design decision subagent)
- **Primary Function**: Map content to optimal slide layouts
- **Workflow Position**: Between content analysis and slide generation
- **Output Format**: Layout assignments JSON

## Layout Selection Rules

### Content → Layout Mapping

| Content Pattern | Recommended Layout | Rationale |
|-----------------|-------------------|-----------|
| Title + subtitle only | `title` | Opening/closing slides |
| Section transition | `section_header` | Clear section breaks |
| 1-6 bullet points | `content` | Standard content |
| Two related lists | `two_content` | Side-by-side comparison |
| Pros/cons, before/after | `comparison` | Labeled columns |
| Image with caption | `image` | Visual focus |
| Quotation + attribution | `quote` | Emphasis on message |
| Custom/special content | `blank` | Full control |
| 3+ numeric values with labels | `stats_grid` | Statistics display |
| "Note:", "Tip:", "Warning:" markers | `callout` | Important notice |
| 2-4 parallel concepts | `cards_grid` | Grouped concepts |
| Definition or term explanation | `key_concept` | Terminology |
| Bullets + highlight point | content with `containers` | Mixed layout |
| 2-8 navigation items with progress | `agenda` | Opening/overview slides |
| Section transition text | `divider` | Bold visual breaks between sections |
| Quantitative data with categories | `data_viz` | Charts (bar, line, pie, etc.) |
| 2-9 related images | `image_grid` | Photo galleries, visual comparisons |

### Decision Criteria

**Use `content` when**:
- Single list of related points
- Step-by-step instructions
- Key features or benefits
- Bullet count: 1-6 items

**Use `two_content` when**:
- Two related but distinct lists
- Parallel concepts
- No explicit comparison needed
- Items don't need labels

**Use `comparison` when**:
- Explicit before/after
- Pros and cons
- Option A vs Option B
- Lists need column headers

**Use `image` when**:
- Visual is primary content
- Diagram, chart, screenshot
- Photo with minimal text

**Use `quote` when**:
- Impactful statement
- Expert opinion
- Memorable phrase
- Attribution required

**Use `agenda` when**:
- Opening/overview slides
- List of topics to be covered (2-8 items)
- May include progress indicators or timing
- Setting expectations for presentation flow

**Use `divider` when**:
- Bold visual break between major sections
- Section transition with minimal text
- Single phrase or section title
- Creating clear separation in presentation flow

**Use `data_viz` when**:
- Numeric data with categories
- Data suitable for charting (bar, line, pie)
- Quantitative comparisons or trends
- Performance metrics or statistics visualization

**Use `image_grid` when**:
- Multiple related images (2-9 items)
- Photo galleries or visual collections
- Product showcases or examples
- Visual comparisons requiring grid layout

### Container Detection Rules

**Detect `callout` when content contains:**
- Explicit markers: "Note:", "Tip:", "Warning:", "Important:", "Remember:"
- Imperative guidance: "Always...", "Never...", "Make sure..."
- Safety or critical information

**Detect `stats_grid` when content contains:**
- 3+ numeric values with labels (e.g., "95% satisfaction", "$2.5M revenue")
- Percentages, currency, multipliers, or metric data
- KPIs or performance indicators

**Detect `cards_grid` when content contains:**
- 2-4 parallel concepts of equal importance
- Categories or grouped features
- Items with similar structure (title + description)

**Detect `key_concept` when content contains:**
- "Definition:" or "Term:" markers
- Technical terminology explanations
- Single concept needing visual emphasis

**Detect inline `containers` when content has:**
- Regular bullets plus one highlighted point
- Standard content with a tip or warning at the end

**Detect `agenda` when content contains:**
- List of sections/topics to be covered (2-8 items)
- May include timing or progress indicators
- Overview of presentation structure
- Typically at start of presentation or major sections

**Detect `divider` when content contains:**
- Single phrase or title marking section transition
- Section number or identifier
- Minimal supporting content (1-2 words max)
- Acts as visual break between major sections

**Detect `data_viz` when content contains:**
- Numeric data that can be charted
- Multiple categories with corresponding values
- Comparisons, trends, or distributions
- Data suitable for bar, line, pie, or other chart types

**Detect `image_grid` when content contains:**
- 2-9 related images to display together
- Photo galleries or visual collections
- Product showcases or example sets
- Visual comparisons requiring multiple images

## Layout Assignment Output

```json
{
  "assignments": [
    {
      "section": 0,
      "slide": 0,
      "current_type": "content",
      "recommended_type": "two_content",
      "confidence": 0.85,
      "rationale": "Content has two parallel lists that would display better side-by-side"
    }
  ],
  "summary": {
    "total_slides": 15,
    "changes_recommended": 3,
    "layout_distribution": {
      "title": 1,
      "section_header": 3,
      "content": 8,
      "two_content": 2,
      "comparison": 1,
      "stats_grid": 2,
      "callout": 1,
      "cards_grid": 1,
      "key_concept": 1,
      "agenda": 1,
      "divider": 2,
      "data_viz": 1,
      "image_grid": 1
    }
  }
}
```

## Analysis Patterns

### Content Structure Detection

**Single List Detection**:
```python
if 'bullets' in content and not ('left' in content or 'right' in content):
    return 'content'
```

**Dual List Detection**:
```python
if 'left' in content and 'right' in content:
    if 'left_title' in content and 'right_title' in content:
        return 'comparison'
    return 'two_content'
```

**Quote Detection**:
```python
if 'text' in content and 'attribution' in content:
    return 'quote'
```

### Content Splitting Recommendations

**When to Split**:
- More than 6 bullets → Split into multiple content slides
- Complex comparison → Multiple comparison slides
- Long quotes → Quote + content follow-up

**Split Output Format**:
```json
{
  "action": "split",
  "original_slide": {"section": 1, "slide": 3},
  "suggested_splits": [
    {
      "type": "content",
      "bullets": ["Point 1", "Point 2", "Point 3"]
    },
    {
      "type": "content",
      "bullets": ["Point 4", "Point 5", "Point 6"]
    }
  ]
}
```

## Single Project Folder Protocol

**Workspace Structure**:
```
PROJECT_WORKSPACE/
├── 01_content_analysis/        # Input analysis
├── 02_slide_content/           # Content to map
├── layout_assignments/         # This agent's output
│   └── layout_recommendations.json
└── agent_workspaces/layout_mapper_workspace/
```

## Layout Optimization Goals

### Visual Balance
- Avoid 5+ consecutive content slides
- Insert visual variety (image, quote) when possible
- Balance text-heavy and visual slides

### Cognitive Load
- One idea per slide
- Use comparison for explicit contrasts
- Use two_content for related parallels

### Presentation Flow
- Title → Section headers → Content → Summary
- Build complexity gradually
- Use section_header for clear transitions

## Integration Points

### Input From
- `content-analyzer`: Content structure analysis
- `presentation-outliner`: Section breakdown

### Output To
- `slide-content-generator`: Layout recommendations
- `slide-validator`: Expected layout distribution

## Confidence Scoring

| Confidence | Meaning |
|------------|---------|
| 0.95+ | Clear match, high certainty |
| 0.80-0.94 | Good match, minor alternatives |
| 0.60-0.79 | Reasonable match, review recommended |
| <0.60 | Uncertain, manual review needed |

## Quick Reference

### Layout Selection Flowchart

```
START
  │
  ├─ Is it a title/opening? → title
  │
  ├─ Is it an agenda/overview list? → agenda
  │
  ├─ Is it a section transition? → section_header or divider
  │
  ├─ Does it have a quote? → quote
  │
  ├─ Does it have multiple images (2-9)? → image_grid
  │
  ├─ Does it have a single image? → image
  │
  ├─ Does it have quantitative data? → data_viz
  │
  ├─ Does it have two labeled lists? → comparison
  │
  ├─ Does it have two parallel lists? → two_content
  │
  ├─ Does it have one list? → content
  │
  └─ Custom/special? → blank
```

### Container Selection Flowchart

```
START with content
  │
  ├─ Has 3+ numeric values? → stats_grid
  │
  ├─ Has "Note:/Tip:/Warning:" marker? → callout
  │
  ├─ Is a definition/term explanation? → key_concept
  │
  ├─ Has 2-4 parallel concepts? → cards_grid
  │
  ├─ Has bullets + one highlight? → content with containers
  │
  └─ Standard content? → content
```

## CLI Integration

```bash
# Analyze and suggest layouts for a presentation
slideforge inspect presentation content.json --suggest-layouts

# Apply layout recommendations
slideforge generate -i content.json -o output.pptx --optimize-layouts
```
