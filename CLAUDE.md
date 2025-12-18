# Slideforge

AI-powered presentation generator that transforms structured content into professional PowerPoint presentations.

---

## Quick Start

**Input**: Structured content (Markdown, JSON outline, documents)
**Output**: Single PPTX file ready for presentation

---

## Workflow Pipeline

```
INPUT                         PROCESSING                              OUTPUT
─────                         ──────────                              ──────
Structured Content    content-to-slide    presentation    slide-content    slide-layout    pptx
(Markdown/JSON/   ──►    analyzer     ──►   outliner   ──►  generator  ──►   mapper    ──►  packager  ──►  .PPTX
 Outline/Text)
```

---

## Orchestrator Protocol

**The orchestrator is a lightweight task manager. Specialized agents handle content transformation and slide generation.**

### Orchestrator Responsibilities
1. Create timestamped project folder in `exports/`
2. Invoke planning agent to analyze content and create structure
3. Load todo list into TodoWrite (single source of truth)
4. Execute todos via specialized agents in parallel batches
5. Coordinate slide quality validation
6. Invoke final PPTX packaging

### Workflow Steps
```
USER REQUEST →
  STEP 1: Content analyzer examines input, returns structure plan (NO execution) →
  STEP 2: Orchestrator loads plan into TodoWrite →
  STEP 3: Orchestrator executes via slide agents (agents do NOT modify TodoWrite) →
  STEP 4: Quality validation (slide-validator) →
  STEP 5: Package generation (pptx-packager) →
  OUTPUT: Single PPTX file
```

---

## Available Agents

| Agent | Purpose | When to Use |
|-------|---------|-------------|
| `content-analyzer` | Analyze input and plan structure | Initial content processing |
| `presentation-outliner` | Plan presentation structure | Creating slide framework |
| `slide-content-generator` | Create slide content | Content development (JSON output) |
| `slide-layout-mapper` | Select optimal layouts | Layout assignment |
| `slide-validator` | Quality validation | Before packaging |
| `pptx-packager` | PPTX file generation | Final assembly |

---

## Critical Execution Protocols

### Individual Section Protocol (MANDATORY)
- ONE agent = ONE section (never multiple sections per agent)
- Maximum 10 simultaneous Task calls per batch
- Wait for batch completion before next batch

**Correct:**
```python
Task(slide-content-generator, "Create introduction section slides")
Task(slide-content-generator, "Create main content section slides")
# ... up to 10 per batch
```

**Wrong:**
```python
Task(slide-content-generator, "Create all presentation slides")  # NEVER DO THIS
```

---

## Project Structure

```
/Slideforge/
├── CLAUDE.md                    # This file
├── README.md                    # Project overview
├── docs/                        # Documentation
│   ├── getting-started.md       # Quick start guide
│   ├── workflow-reference.md    # Detailed workflow protocols
│   └── slide-design-guide.md    # Slide design best practices
├── agents/                      # Agent specifications
├── inputs/                      # Input files
│   └── source-content/          # Markdown, outlines, documents
├── templates/                   # PPTX templates and themes
│   └── pptx/
│       ├── themes/              # Theme PPTX files
│       └── examples/            # Example presentations
├── schemas/                     # JSON schemas
│   └── presentation/            # Presentation and slide schemas
├── scripts/                     # Automation scripts
│   ├── pptx-generator/          # Core PPTX generation
│   ├── semantic-structure-extractor/  # Content parsing
│   └── utilities/               # Helper utilities
├── exports/                     # Generated presentations
│   └── YYYYMMDD_HHMMSS_name/    # Timestamped project folders
└── runtime/                     # Agent workspaces
```

### Export Project Structure
```
exports/YYYYMMDD_HHMMSS_presentationname/
├── 01_content_analysis/
├── 02_slide_content/
│   ├── section_01/
│   └── section_XX/
├── 03_final_output/
│   └── presentation.pptx         # Final deliverable
├── agent_workspaces/
└── project_log.md
```

---

## Input Formats

### Markdown
```markdown
# Presentation Title

## Section 1: Introduction

### Overview
- First key point
- Second key point

### Details
- Supporting information
```

### JSON Outline
```json
{
  "metadata": {
    "title": "Presentation Title",
    "author": "Author Name"
  },
  "sections": [
    {
      "title": "Introduction",
      "slides": [...]
    }
  ]
}
```

---

## Quality Standards

### Slide Design Rules
- **6x6 Rule**: Maximum 6 bullets, 6 words per bullet
- **One Idea Per Slide**: Focus on single concept
- **Visual Hierarchy**: Clear title, supporting points
- **Consistent Styling**: Same layouts for similar content

### Validation Checklist
- [ ] All slides have descriptive titles
- [ ] No bullet lists exceed 6 items
- [ ] Content is concise and scannable
- [ ] Sections flow logically
- [ ] Speaker notes provide context

---

## Documentation

| Document | Location | Purpose |
|----------|----------|---------|
| Getting Started | `docs/getting-started.md` | Quick start guide |
| Workflow Reference | `docs/workflow-reference.md` | Detailed protocols |
| Slide Design Guide | `docs/slide-design-guide.md` | Design best practices |
| Agent Specs | `agents/*.md` | Individual agent protocols |

---

## Color Palettes (WCAG 2.2 AA Compliant)

### Corporate Template
*Trust + Stability + Success*
```css
Primary Navy: #1B4F72
Steel Gray: #5D6D7E
Emerald Accent: #1E8449
Text Primary: #1C2833
```

### Educational Template
*Trust + Growth + Optimism*
```css
Deep Blue: #1A5276
Teal-Green: #148F77
Gold Accent: #D4AC0D
Background: #FEF9E7
Text Primary: #1C2833
```

### Creative Template
*Creativity + Sophistication + Passion*
```css
Rich Purple: #6C3483
Teal: #17A2B8
Coral Accent: #E74C3C
Background: #F4ECF7
Text Primary: #2C2C54
```

### Minimal Template
*Clarity + Action*
```css
Charcoal: #212529
Cool Gray: #6C757D
Electric Blue: #007BFF
Background: #FFFFFF
```

### Color Psychology Reference
| Color | Association | Best For |
|-------|-------------|----------|
| Blue | Trust, stability | Corporate, educational |
| Green | Growth, success | Finance, health |
| Purple | Creativity, luxury | Creative, premium |
| Teal | Sophistication | Modern, tech |

---

## Slide Types

Content generators should use these slide types appropriately:

| Type | Use Case | Content |
|------|----------|---------|
| Title | Opening slide | Title + subtitle |
| Section Header | Section transitions | Section name |
| Content | Main slides | Title + bullets |
| Two Content | Side-by-side | Two columns |
| Comparison | Pros/cons, before/after | Labeled columns |
| Image | Visual focus | Title + image |
| Quote | Key messages | Quote + attribution |
| Blank | Custom content | Empty canvas |

---

## Script Usage

### Generate from JSON
```bash
cd scripts/pptx-generator
python pptx_generator.py --input content.json --output presentation.pptx
```

### With Theme Template
```bash
python pptx_generator.py -i content.json -o output.pptx -t themes/corporate.pptx
```

---

## Dependencies

```
python-pptx>=0.6.21
Pillow>=9.0.0
beautifulsoup4>=4.9.0
jsonschema>=4.0.0
```
