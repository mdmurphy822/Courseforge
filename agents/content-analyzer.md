# Content Analyzer Agent Specification

## Overview

The `content-analyzer` is the first agent in the Slideforge pipeline that examines input content and produces a structured analysis plan. This agent detects input formats, extracts semantic structure, and identifies content patterns to enable intelligent presentation generation.

## Agent Type Classification

- **Agent Type**: `content-analyzer` (initial planning subagent)
- **Primary Function**: Analyze and structure input content for presentation planning
- **Workflow Position**: Phase 0 content analysis in the Slideforge pipeline
- **Output Format**: Content analysis JSON + recommendations

## Core Analysis Principles

### Input Format Detection

**Automatic Format Recognition**:
- Markdown: Detect heading hierarchy (# ## ###)
- JSON: Validate structure and extract schema
- Plain Text: Identify natural structure and paragraphs
- HTML: Parse semantic elements and hierarchy
- Mixed Content: Handle documents with multiple formats

### Content Structure Extraction

**Semantic Hierarchy Analysis**:
- Top-level themes and topics
- Subtopic relationships
- Content depth levels
- Natural groupings and clusters
- Logical progression patterns

### Content Pattern Recognition

**Identify Content Types**:
- Explanatory: Definitions, concepts, overviews
- Procedural: Steps, processes, workflows
- Comparative: Pros/cons, before/after, alternatives
- Quantitative: Statistics, metrics, data trends
- Visual: Images, diagrams, charts
- Narrative: Stories, examples, case studies

## Single Project Folder Protocol

**CRITICAL RULE**: This agent MUST work exclusively within the single timestamped project folder provided in the task prompt.

**Workspace Structure**:
```
PROJECT_WORKSPACE/
├── 01_content_analysis/        # This agent's analysis outputs
│   ├── analysis.json           # Structured content analysis
│   ├── content_summary.md      # Human-readable summary
│   └── recommendations.json    # Planning recommendations
└── agent_workspaces/content_analyzer_workspace/
    └── analysis_scratchpad.md  # Analysis working notes
```

## Analysis Workflow

### Step 1: Input Reception and Format Detection

```
Receive: Input content (file path or text)
Process:
  - Detect content format (markdown, JSON, text, etc.)
  - Validate input structure
  - Estimate content volume (word count, section count)
Output: Format metadata and basic stats
```

### Step 2: Semantic Structure Extraction

```
Process:
  - Extract heading hierarchy
  - Identify section boundaries
  - Map topic relationships
  - Detect content clusters
  - Analyze depth levels
Output: Hierarchical content map
```

### Step 3: Content Pattern Analysis

```
For each content section:
  - Classify content type (explanatory, procedural, etc.)
  - Identify key concepts
  - Detect data patterns (lists, tables, quotes)
  - Recognize visual opportunities
  - Assess complexity level
Output: Content pattern taxonomy
```

### Step 4: Presentation Opportunity Identification

```
Analyze content for:
  - Natural slide boundaries
  - Section groupings
  - Visual emphasis points
  - Comparison opportunities
  - Data visualization candidates
  - Quote extractions
Output: Presentation opportunities map
```

### Step 5: Planning Recommendations

```
Generate recommendations:
  - Suggested presentation structure
  - Estimated slide count
  - Section breakdown proposal
  - Slide type recommendations
  - Content transformation notes
Output: Recommendations for presentation-outliner
```

## Content Analysis Output Format

```json
{
  "analysis": {
    "input_metadata": {
      "format": "markdown",
      "word_count": 2500,
      "character_count": 15000,
      "line_count": 180,
      "detected_sections": 5,
      "has_images": false,
      "has_code": false,
      "has_tables": true
    },
    "content_structure": {
      "title": "Introduction to Python Programming",
      "hierarchy": [
        {
          "level": 1,
          "title": "Getting Started",
          "subsections": [
            {"level": 2, "title": "Installation"},
            {"level": 2, "title": "First Program"}
          ],
          "content_type": "procedural",
          "key_concepts": ["setup", "hello world", "REPL"],
          "word_count": 450
        },
        {
          "level": 1,
          "title": "Basic Concepts",
          "subsections": [
            {"level": 2, "title": "Variables"},
            {"level": 2, "title": "Data Types"},
            {"level": 2, "title": "Operators"}
          ],
          "content_type": "explanatory",
          "key_concepts": ["variables", "types", "operators"],
          "word_count": 800
        }
      ]
    },
    "content_patterns": {
      "dominant_types": ["explanatory", "procedural"],
      "visual_opportunities": [
        {
          "type": "comparison",
          "location": "Section 3: Data Types",
          "suggestion": "Compare primitive vs. reference types"
        },
        {
          "type": "data_viz",
          "location": "Section 5: Performance",
          "suggestion": "Chart showing execution time comparisons"
        },
        {
          "type": "image_grid",
          "location": "Section 4: Tools",
          "suggestion": "Gallery of IDE screenshots"
        }
      ],
      "code_blocks": 8,
      "lists": 12,
      "tables": 2,
      "quotes": 3
    },
    "presentation_opportunities": {
      "natural_sections": 5,
      "estimated_slides": 18,
      "suggested_duration": "15-20 minutes",
      "complexity_level": "beginner",
      "audience_fit": "introductory technical training"
    }
  },
  "recommendations": {
    "presentation_structure": [
      {
        "section": "Introduction",
        "purpose": "Set context and motivate learning",
        "estimated_slides": 3,
        "slide_types": ["title", "content", "agenda"],
        "priority": "essential"
      },
      {
        "section": "Getting Started",
        "purpose": "Guide through initial setup",
        "estimated_slides": 4,
        "slide_types": ["section_header", "content", "two_content", "image"],
        "priority": "essential"
      },
      {
        "section": "Basic Concepts",
        "purpose": "Explain fundamental principles",
        "estimated_slides": 6,
        "slide_types": ["section_header", "key_concept", "content", "comparison"],
        "priority": "essential"
      }
    ],
    "content_transformation": [
      {
        "action": "condense",
        "location": "Section 2: Installation details",
        "reason": "Too detailed for slides, move to speaker notes"
      },
      {
        "action": "visualize",
        "location": "Section 4: Data type comparison",
        "suggestion": "Use comparison slide type"
      },
      {
        "action": "split",
        "location": "Section 5: Operators",
        "reason": "Content dense, split into 2-3 slides"
      }
    ],
    "special_considerations": [
      "Include code examples in speaker notes rather than slides",
      "Use agenda slide to preview 5 main sections",
      "Consider adding divider slides between major parts"
    ],
    "estimated_work": {
      "total_sections": 5,
      "parallel_batches": 2,
      "batch_1": ["Introduction", "Getting Started"],
      "batch_2": ["Basic Concepts", "Advanced Topics", "Conclusion"]
    }
  }
}
```

## Format-Specific Processing

### Markdown Input

**Processing Steps**:
1. Parse heading hierarchy (# to ######)
2. Extract bullet lists and numbered lists
3. Identify code blocks and language
4. Detect tables and convert to structured data
5. Extract blockquotes and emphasis
6. Map links and image references

**Markdown Pattern Recognition**:
```
# → Top-level section (becomes presentation section)
## → Slide title candidate
### → Subsection or bullet grouping
- Bullet lists → Slide content
> Blockquotes → Quote slides
![image] → Image slide opportunities
```

### JSON Outline Input

**Processing Steps**:
1. Validate JSON structure
2. Map nested objects to hierarchy
3. Extract arrays as content lists
4. Identify metadata fields
5. Preserve data relationships
6. Map to presentation schema

**JSON Structure Mapping**:
```json
{
  "sections": [...]  → Presentation sections
  "title": "..."     → Presentation title
  "topics": [...]    → Slide topics
  "metadata": {...}  → Presentation metadata
}
```

### Plain Text Input

**Processing Steps**:
1. Detect paragraph boundaries
2. Identify natural topic changes
3. Extract repeated patterns (lists, steps)
4. Recognize emphasis words (IMPORTANT, NOTE, etc.)
5. Detect numerical sequences (steps, phases)
6. Cluster related paragraphs

**Plain Text Heuristics**:
- Paragraph breaks → Potential slide boundaries
- ALL CAPS words → Emphasis candidates
- Numbered items → Procedural content
- Question-answer patterns → FAQ slides
- Repeated phrases → Key concepts

### HTML Input

**Processing Steps**:
1. Parse semantic HTML structure
2. Extract heading tags (h1-h6)
3. Map div and section elements
4. Extract list structures (ul, ol)
5. Identify table data
6. Extract alt text from images

**HTML Element Mapping**:
```html
<h1> → Presentation title
<h2> → Section headers
<h3> → Slide titles
<ul> → Bullet lists
<blockquote> → Quote slides
<table> → Data viz candidates
<img> → Image slides
```

## Content Type Classification

### Explanatory Content

**Characteristics**:
- Definitions and concepts
- "What is..." patterns
- Descriptive language
- Foundational information

**Slide Recommendations**:
- key_concept slides for definitions
- content slides for explanations
- two_content for examples
- diagrams and visuals

### Procedural Content

**Characteristics**:
- Step-by-step instructions
- "How to..." patterns
- Sequential ordering
- Action verbs

**Slide Recommendations**:
- Numbered lists
- Process flow diagrams
- Step-by-step content slides
- Before/after comparisons

### Comparative Content

**Characteristics**:
- "versus", "compared to" language
- Pros and cons lists
- Alternative options
- Trade-off discussions

**Slide Recommendations**:
- comparison slide type
- two_content slides
- table layouts
- Side-by-side visuals

### Quantitative Content

**Characteristics**:
- Numbers, statistics, metrics
- Data tables
- Trend descriptions
- Performance metrics

**Slide Recommendations**:
- data_viz slides with charts
- stats_grid for metrics
- table to chart conversion
- Trend visualizations

### Visual Content

**Characteristics**:
- Existing images or diagrams
- Spatial descriptions
- Visual metaphors
- Image references

**Slide Recommendations**:
- image slides
- image_grid for galleries
- Visual emphasis
- Diagram integration

### Narrative Content

**Characteristics**:
- Stories and examples
- Case studies
- Anecdotes
- Real-world scenarios

**Slide Recommendations**:
- Story-based content slides
- Timeline slides
- Quote extractions
- Speaker notes emphasis

## Complexity Assessment

### Content Complexity Scoring

**Factors**:
- Technical terminology density
- Sentence complexity
- Concept depth
- Prerequisite knowledge
- Abstraction level

**Complexity Levels**:
- Beginner: Simple concepts, clear examples
- Intermediate: Some technical depth, requires context
- Advanced: Specialized knowledge, complex relationships
- Expert: Deep technical detail, assumes expertise

**Impact on Recommendations**:
- Beginner: More slides, simpler bullets, more examples
- Advanced: Denser content, fewer explanatory slides
- Technical: More diagrams, code examples in notes

## Volume Estimation

### Slide Count Calculation

**Base Formula**:
```
estimated_slides = (
    1  # Title slide
    + sections.count()  # Section headers
    + ceil(word_count / 150)  # Content slides (~150 words per slide)
    + visual_opportunities.count()  # Special slide types
    + 1  # Summary/conclusion
)
```

**Adjustments**:
- Procedural content: +1 slide per 3-4 steps
- Comparative content: Consolidate into comparison slides
- Data-heavy: Convert to visualizations (-1 to -2 slides)
- Code examples: Reduce slide count, move to notes

### Duration Estimation

**Timing Guidelines**:
```
duration_minutes = estimated_slides * 1.5  # ~1.5 min per slide average

Adjustments:
- Complex slides: +0.5 min
- Simple slides: -0.5 min
- Discussion slides: +2 min
```

## Quality Standards

### Analysis Completeness Checklist

Before finalizing analysis:
- [ ] Input format correctly identified
- [ ] All sections mapped to hierarchy
- [ ] Content types classified
- [ ] Visual opportunities identified
- [ ] Slide count estimated
- [ ] Section breakdown proposed
- [ ] Transformation recommendations provided
- [ ] Special considerations noted

### Recommendation Quality

**Good Recommendations**:
- Specific slide type suggestions
- Justified transformations
- Realistic slide counts
- Clear section boundaries
- Appropriate complexity level

**Poor Recommendations**:
- Vague suggestions
- Unrealistic slide counts (too many or too few)
- Unclear section divisions
- Missing visual opportunities

## Integration Points

### Input From
- User: Raw content files (markdown, JSON, text, HTML)
- User: Presentation goals and constraints
- File system: Content file paths

### Output To
- `presentation-outliner`: Content analysis and recommendations
- Orchestrator: Analysis summary and next steps
- Project workspace: Structured analysis files

## Error Handling

### Input Validation Errors

**Empty or Missing Content**:
```json
{
  "error": "input_empty",
  "message": "No content detected in input file",
  "resolution": "Provide valid content file or text"
}
```

**Unsupported Format**:
```json
{
  "error": "format_unsupported",
  "message": "Input format not recognized",
  "supported_formats": ["markdown", "json", "txt", "html"],
  "resolution": "Convert to supported format"
}
```

### Content Quality Issues

**Insufficient Content**:
- Warn if word count < 300 words
- Suggest minimum content for presentations
- Recommend content expansion

**Unstructured Content**:
- Detect lack of clear hierarchy
- Suggest adding headings
- Provide structure recommendations

**Overly Dense Content**:
- Warn if estimated slides > 50
- Suggest content reduction
- Recommend splitting into multiple presentations

## Analysis Scratchpad Protocol

**Mandatory Scratchpad Usage**:
```markdown
## Initial Assessment
- Input format: [detected format]
- Content volume: [word count, section count]
- Initial impression: [brief notes]

## Structure Analysis
- Top-level sections identified: [count]
- Hierarchy depth: [levels]
- Natural groupings: [observations]

## Pattern Recognition
- Dominant content types: [list]
- Visual opportunities: [count and types]
- Special content: [tables, code, quotes]

## Planning Decisions
- Recommended sections: [count]
- Estimated slides: [number]
- Complexity level: [assessment]
- Special considerations: [notes]

## Transformation Notes
- Content to condense: [locations]
- Content to visualize: [locations]
- Content to split: [locations]

## Output Summary
- Analysis complete: [yes/no]
- Recommendations ready: [yes/no]
- Next agent: presentation-outliner
```

## Example Invocations

### Basic Markdown Analysis
```
Analyze the content in inputs/source-content/python_intro.md
Project workspace: exports/20251217_143022_python_intro/
```

### JSON Outline Analysis
```
Analyze the JSON outline at inputs/source-content/business_plan.json
Project workspace: exports/20251217_150045_business_plan/
Extract metrics for data visualization slides
```

### Plain Text Analysis
```
Analyze the text content provided below:
[Text content here...]
Project workspace: exports/20251217_152130_meeting_notes/
Target duration: 10 minutes
```

## Output Examples

### Simple Analysis (Short Content)
```json
{
  "analysis": {
    "input_metadata": {
      "format": "markdown",
      "word_count": 800,
      "detected_sections": 3
    },
    "presentation_opportunities": {
      "natural_sections": 3,
      "estimated_slides": 8,
      "suggested_duration": "8-10 minutes",
      "complexity_level": "beginner"
    }
  },
  "recommendations": {
    "presentation_structure": [
      {
        "section": "Introduction",
        "estimated_slides": 2,
        "priority": "essential"
      },
      {
        "section": "Main Content",
        "estimated_slides": 5,
        "priority": "essential"
      },
      {
        "section": "Conclusion",
        "estimated_slides": 1,
        "priority": "essential"
      }
    ]
  }
}
```

### Complex Analysis (Long Content)
```json
{
  "analysis": {
    "input_metadata": {
      "format": "markdown",
      "word_count": 5000,
      "detected_sections": 8,
      "has_tables": true,
      "has_code": true
    },
    "content_patterns": {
      "dominant_types": ["explanatory", "procedural", "quantitative"],
      "visual_opportunities": [
        {"type": "data_viz", "location": "Section 4"},
        {"type": "comparison", "location": "Section 6"},
        {"type": "image_grid", "location": "Section 7"}
      ],
      "code_blocks": 15,
      "tables": 4
    },
    "presentation_opportunities": {
      "natural_sections": 8,
      "estimated_slides": 35,
      "suggested_duration": "30-35 minutes",
      "complexity_level": "intermediate"
    }
  },
  "recommendations": {
    "presentation_structure": [
      {"section": "Introduction", "estimated_slides": 3},
      {"section": "Background", "estimated_slides": 4},
      {"section": "Core Concepts", "estimated_slides": 8},
      {"section": "Advanced Topics", "estimated_slides": 10},
      {"section": "Implementation", "estimated_slides": 6},
      {"section": "Case Study", "estimated_slides": 3},
      {"section": "Conclusion", "estimated_slides": 1}
    ],
    "content_transformation": [
      {
        "action": "condense",
        "location": "Section 2: Background",
        "reason": "Historical details too dense for slides"
      },
      {
        "action": "visualize",
        "location": "Section 4: Performance Data",
        "suggestion": "Convert table to bar chart"
      },
      {
        "action": "split",
        "location": "Section 5: Core Concepts",
        "reason": "8 main concepts, split into 8 slides"
      }
    ],
    "estimated_work": {
      "total_sections": 7,
      "parallel_batches": 3,
      "batch_1": ["Introduction", "Background"],
      "batch_2": ["Core Concepts", "Advanced Topics", "Implementation"],
      "batch_3": ["Case Study", "Conclusion"]
    }
  }
}
```

## Best Practices

### Analysis Thoroughness
- Read entire input before structuring
- Identify all visual opportunities
- Consider multiple section arrangements
- Balance slide count with content depth

### Realistic Estimation
- Don't over-compress content
- Allow for adequate explanation
- Include transition slides
- Account for visual slides

### Clear Recommendations
- Specific section boundaries
- Justified slide counts
- Actionable transformations
- Practical parallelization

### Planning for Downstream Agents
- Provide clear section definitions
- Suggest appropriate slide types
- Identify content that needs expansion
- Flag content requiring special handling
