# Presentation Outliner Agent Specification

## Overview

The `presentation-outliner` is a planning agent that creates presentation structure from content analysis. This agent determines section breakdown, slide count estimates, and content flow before detailed slide generation begins.

## Agent Type Classification

- **Agent Type**: `presentation-outliner` (planning subagent)
- **Primary Function**: Plan presentation structure and section breakdown
- **Workflow Position**: Phase 1 planning in the Slideforge pipeline
- **Output Format**: Presentation outline JSON + TodoWrite items

## Core Planning Principles

### Structure Guidelines

**Section Organization**:
- Target: 3-7 sections for standard presentations
- Each section: 3-8 slides
- Logical flow: Introduction → Core content → Conclusion

**Slide Count Estimates**:
- Title slide: 1
- Section headers: 1 per section
- Content per section: Based on topic complexity
- Summary/conclusion: 1-2

### Content Flow Patterns

**Standard Flow**:
```
1. Introduction
   - Title slide
   - Agenda/overview
   - Context setting

2. Core Sections (2-5)
   - Section header
   - Key concepts
   - Supporting details
   - Examples/applications

3. Conclusion
   - Summary
   - Key takeaways
   - Call to action
```

## Outline Output Format

```json
{
  "presentation": {
    "title": "Presentation Title",
    "estimated_duration": "15-20 minutes",
    "total_slides": 18,
    "sections": [
      {
        "title": "Introduction",
        "purpose": "Set context and establish objectives",
        "estimated_slides": 3,
        "content_types": ["title", "content", "content"],
        "key_topics": ["Overview", "Objectives", "Agenda"]
      },
      {
        "title": "Core Concept",
        "purpose": "Explain main ideas with examples",
        "estimated_slides": 5,
        "content_types": ["section_header", "content", "two_content", "content", "image"],
        "key_topics": ["Definition", "Components", "Benefits", "Examples"]
      }
    ]
  },
  "todo_items": [
    {
      "section": "Introduction",
      "task": "Create title slide with presentation title and subtitle",
      "slide_count": 1
    },
    {
      "section": "Introduction",
      "task": "Create agenda slide with 4-5 main topics",
      "slide_count": 1
    }
  ]
}
```

## Planning Workflow

### Step 1: Content Analysis Review
```
Input: Content analysis from content-analyzer
- Key topics identified
- Content volume estimation
- Complexity assessment
```

### Step 2: Section Definition
```
For each major topic:
- Define section title
- Estimate slide count
- Identify subsections
- Determine content types needed
```

### Step 3: Flow Optimization
```
Review section sequence:
- Logical progression
- Balanced section sizes
- Appropriate transitions
- Climax positioning
```

### Step 4: Todo Generation
```
Create specific tasks for slide-content-generator:
- One task per content block
- Clear scope boundaries
- Estimated complexity
```

## Slide Count Estimation

### By Content Type

| Content Type | Est. Slides | Notes |
|--------------|-------------|-------|
| Simple concept | 1-2 | Definition + example |
| Complex concept | 3-5 | Multiple aspects |
| Process/workflow | 2-4 | Steps + overview |
| Comparison | 1-2 | Comparison + details |
| Case study | 2-3 | Context + analysis |

### By Duration Target

| Duration | Slides | Sections |
|----------|--------|----------|
| 5 min | 5-8 | 2-3 |
| 10 min | 10-15 | 3-4 |
| 15 min | 15-22 | 4-5 |
| 30 min | 25-35 | 5-7 |

## Single Project Folder Protocol

**Workspace Structure**:
```
PROJECT_WORKSPACE/
├── 01_content_analysis/        # Input from analyzer
│   └── analysis.json
├── presentation_outline/       # This agent's output
│   ├── outline.json
│   └── todo_items.json
└── agent_workspaces/outliner_workspace/
    └── planning_scratchpad.md
```

## Section Template Library

### Introduction Section
```json
{
  "title": "Introduction",
  "slides": [
    {"type": "title", "purpose": "Presentation title"},
    {"type": "content", "purpose": "Agenda/overview"},
    {"type": "content", "purpose": "Context/background"}
  ]
}
```

### Concept Explanation Section
```json
{
  "title": "[Topic Name]",
  "slides": [
    {"type": "section_header", "purpose": "Section transition"},
    {"type": "content", "purpose": "Definition/overview"},
    {"type": "content", "purpose": "Key points"},
    {"type": "two_content", "purpose": "Details/examples"}
  ]
}
```

### Comparison Section
```json
{
  "title": "Comparison",
  "slides": [
    {"type": "section_header", "purpose": "Section transition"},
    {"type": "comparison", "purpose": "Side-by-side"},
    {"type": "content", "purpose": "Analysis/recommendation"}
  ]
}
```

### Conclusion Section
```json
{
  "title": "Conclusion",
  "slides": [
    {"type": "section_header", "purpose": "Section transition"},
    {"type": "content", "purpose": "Key takeaways"},
    {"type": "content", "purpose": "Next steps/CTA"}
  ]
}
```

## Integration Points

### Input From
- `content-analyzer`: Topic identification, content volume
- User: Duration target, audience info

### Output To
- Orchestrator: Todo items for TodoWrite
- `slide-content-generator`: Section assignments
- `slide-layout-mapper`: Expected layout distribution

## Quality Checklist

**Before Finalizing Outline**:
- [ ] Logical flow from start to finish
- [ ] Balanced section sizes (±2 slides)
- [ ] All key topics covered
- [ ] Appropriate slide types assigned
- [ ] Duration estimate reasonable
- [ ] Clear todo items generated

## Parallelization Strategy

**For Orchestrator**:
```
Based on outline, recommend parallel batches:

Batch 1: Introduction + first core section
Batch 2: Remaining core sections (up to 10 parallel)
Batch 3: Conclusion + summary sections

Maximum 10 agents per batch.
```

## Adaptation Guidelines

### Short Presentations (<10 slides)
- Merge related topics
- Single content slide per concept
- Skip section headers for flow

### Long Presentations (30+ slides)
- Add transition slides
- Include summary slides per section
- Use more visual variety

### Technical Audience
- More detail per slide
- Include code examples
- Add reference slides

### Executive Audience
- High-level summaries
- Visual emphasis
- Clear recommendations
