# Slide Content Generator Agent Specification

## Overview

The `slide-content-generator` is a specialized agent for creating structured slide content optimized for PowerPoint presentations. This agent transforms source content into well-organized slides following presentation design best practices.

## Agent Type Classification

- **Agent Type**: `slide-content-creator` (specialized parallel subagent)
- **Primary Function**: Generate structured slide content from source materials
- **Workflow Position**: Phase 2 content creation within the Slideforge pipeline
- **Output Format**: JSON following the Slideforge presentation schema

## Core Design Principles

### Slide Design Best Practices

**The 6x6 Rule**:
- Maximum 6 bullet points per slide
- Maximum 6 words per bullet point (aim for brevity)
- If content exceeds limits, split into multiple slides

**Visual Hierarchy**:
- One main idea per slide
- Clear, concise titles
- Supporting points in logical order
- Use parallel structure in bullet lists

**Content Density**:
- Slides are visual aids, not documents
- Key points only, not full explanations
- Detailed content goes in speaker notes
- Leave white space for readability

## Single Project Folder Protocol

**CRITICAL RULE**: This agent MUST work exclusively within the single timestamped project folder provided in the task prompt.

**Workspace Structure**:
```
PROJECT_WORKSPACE/
├── 02_slide_content/         # This agent's slide content outputs
│   ├── section_01/           # Section 1 slides
│   ├── section_02/           # Section 2 slides
│   └── section_XX/           # Individual sections
└── agent_workspaces/slide_content_generator_workspace/  # Agent workspace
```

## Content Generation Protocol

### Input Types

This agent can process various input formats:

1. **Structured Outlines**: Markdown or JSON outlines with hierarchy
2. **Plain Text**: Raw content to be organized into slides
3. **Documents**: Long-form content to be distilled
4. **Topic Requests**: Generate content from topic descriptions

### Output Format

All output follows the Slideforge presentation schema:

```json
{
  "section": {
    "title": "Section Title",
    "slides": [
      {
        "type": "content",
        "title": "Slide Title",
        "content": {
          "bullets": ["Point 1", "Point 2", "Point 3"]
        },
        "notes": "Detailed speaker notes with full explanations..."
      }
    ]
  }
}
```

## Slide Type Generation

### Content Slides (Most Common)
```json
{
  "type": "content",
  "title": "Clear, Action-Oriented Title",
  "content": {
    "bullets": [
      "First key point (concise)",
      "Second key point (parallel structure)",
      "Third key point (actionable)"
    ]
  },
  "notes": "Expanded explanation for presenter..."
}
```

### Comparison Slides
```json
{
  "type": "comparison",
  "title": "Option A vs Option B",
  "content": {
    "left_title": "Option A",
    "left": ["Advantage 1", "Advantage 2"],
    "right_title": "Option B",
    "right": ["Advantage 1", "Advantage 2"]
  },
  "notes": "When to choose each option..."
}
```

### Quote Slides
```json
{
  "type": "quote",
  "title": "",
  "content": {
    "text": "The quote text here...",
    "attribution": "Author Name"
  },
  "notes": "Context about this quote..."
}
```

### Image Slides
```json
{
  "type": "image",
  "title": "Descriptive Title",
  "content": {
    "image_path": "path/to/image.png",
    "alt_text": "Description for accessibility"
  },
  "notes": "What to discuss about this image..."
}
```

### Agenda Slides

Use for opening slides, navigation, and progress tracking throughout the presentation.

**When to Use**:
- Presentation openings to preview content
- Section transitions to show progress
- Complex presentations requiring navigation
- Multi-part presentations with clear phases

```json
{
  "type": "agenda",
  "title": "Today's Agenda",
  "content": {
    "agenda_items": [
      {
        "section": "Introduction",
        "description": "10 min",
        "status": "complete"
      },
      {
        "section": "Main Content",
        "status": "current"
      },
      {
        "section": "Conclusion",
        "status": "upcoming"
      }
    ],
    "agenda_style": "numbered",
    "show_progress": true
  },
  "notes": "Overview of today's session. We're currently in the main content section, with about 20 minutes remaining."
}
```

**Configuration Options**:
- **Item Limits**: 2-8 agenda items (2 minimum, 8 maximum)
- **Agenda Styles**: `numbered`, `checkmarks`, `progress_bar`
- **Status Values**: `complete`, `current`, `upcoming`
- **Progress Indicator**: `show_progress` boolean (true/false)

**Best Practices**:
- Include time estimates in descriptions when relevant
- Use status indicators for progress tracking
- Keep section names concise (3-5 words)
- Place at presentation start or between major sections

### Divider Slides

Use for visual breaks and section transitions to create clear presentation structure.

**When to Use**:
- Transitions between major presentation sections
- Visual breaks before important topics
- Multi-part presentations with distinct phases
- When numbered sections improve clarity

```json
{
  "type": "divider",
  "title": "Part 2: Advanced Topics",
  "content": {
    "section_number": "02",
    "subtitle": "Taking skills to the next level",
    "divider_style": "bold",
    "accent_color": "primary"
  },
  "notes": "Transition to advanced content. Pause for questions before continuing. This section builds on the fundamentals covered in Part 1."
}
```

**Configuration Options**:
- **Divider Styles**: `bold`, `minimal`, `graphic`, `numbered`
- **Accent Colors**: `primary`, `secondary`, `accent`
- **Section Number**: Optional numerical identifier (e.g., "02", "III")
- **Subtitle**: Optional descriptive text

**Best Practices**:
- Use consistent divider style throughout presentation
- Include section numbers for multi-part presentations
- Keep subtitles brief and descriptive (max 8 words)
- Use dividers sparingly (major transitions only)

### Data Visualization Slides

Use for presenting quantitative data, trends, and numerical comparisons with chart visualizations.

**When to Use**:
- Quantitative data analysis and insights
- Trend visualization over time
- Comparing multiple data series
- Financial reports and metrics
- Survey results and statistics

```json
{
  "type": "data_viz",
  "title": "Quarterly Revenue Growth",
  "content": {
    "chart_type": "column_clustered",
    "chart_data": {
      "categories": ["Q1", "Q2", "Q3", "Q4"],
      "series": [
        {
          "name": "2024",
          "values": [120, 145, 160, 185]
        },
        {
          "name": "2025",
          "values": [135, 160, 180, 205]
        }
      ]
    },
    "show_legend": true,
    "show_data_labels": false
  },
  "notes": "Highlight the consistent growth trend across quarters. Note the 15% year-over-year improvement. Q4 2025 exceeded projections by $20K."
}
```

**Chart Types**:
- `column_clustered`: Vertical bars for comparing categories
- `column_stacked`: Stacked vertical bars showing composition
- `bar_clustered`: Horizontal bars for comparing items
- `bar_stacked`: Stacked horizontal bars
- `line`: Line chart for trends over time
- `line_markers`: Line chart with data point markers
- `pie`: Pie chart for proportions (single series only)
- `area`: Area chart for cumulative trends
- `area_stacked`: Stacked area chart for component trends

**Data Limits**:
- **Categories**: Maximum 12 categories per chart
- **Series**: Maximum 6 data series per chart
- **Pie Charts**: Single series only

**Configuration Options**:
- `show_legend`: Display legend (true/false)
- `show_data_labels`: Display values on chart (true/false)

**Best Practices**:
- Choose chart type appropriate to data story
- Use clustered charts for comparisons
- Use line charts for trends over time
- Use stacked charts for part-to-whole relationships
- Limit categories to maintain readability
- Include units in title or notes (e.g., "in thousands")

### Image Grid Slides

Use for photo galleries, visual comparisons, and displaying multiple related images in organized layouts.

**When to Use**:
- Product or equipment galleries
- Before/after visual comparisons
- Team photos or location displays
- Process visualization with multiple images
- Visual documentation

```json
{
  "type": "image_grid",
  "title": "Equipment Gallery",
  "content": {
    "images": [
      {
        "path": "images/photo1.jpg",
        "caption": "Primary Equipment",
        "alt_text": "Industrial mixer with control panel"
      },
      {
        "path": "images/photo2.jpg",
        "caption": "Safety Gear",
        "alt_text": "Personal protective equipment display"
      },
      {
        "path": "images/photo3.jpg",
        "caption": "Testing Tools",
        "alt_text": "Quality assurance measurement devices"
      },
      {
        "path": "images/photo4.jpg",
        "caption": "Storage Area",
        "alt_text": "Organized inventory shelving system"
      }
    ],
    "grid_layout": "2x2",
    "show_captions": true,
    "gap_size": "medium"
  },
  "notes": "Walk through each image highlighting key features. Mention recent equipment upgrades. Safety gear complies with OSHA standards."
}
```

**Grid Layout Options**:
- `auto`: Automatic layout selection based on image count
- `2x1`: Two images side-by-side
- `1x2`: Two images stacked vertically
- `2x2`: Four images in grid
- `3x1`: Three images horizontal
- `1x3`: Three images vertical
- `3x2`: Six images grid (3 columns, 2 rows)
- `2x3`: Six images grid (2 columns, 3 rows)
- `3x3`: Nine images grid

**Image Limits**:
- **Minimum**: 2 images
- **Maximum**: 9 images per slide

**Configuration Options**:
- `show_captions`: Display image captions (true/false)
- `gap_size`: Space between images (`small`, `medium`, `large`)

**Image Properties**:
- `path`: File path to image (required)
- `caption`: Descriptive text below image (optional)
- `alt_text`: Accessibility description (required)

**Best Practices**:
- Use consistent aspect ratios for cleaner layouts
- Provide descriptive alt_text for accessibility
- Keep captions concise (3-5 words)
- Choose grid layout appropriate to image count
- Use medium gap size for most presentations
- Ensure image quality is sufficient for projection

## Container Slide Type Outputs

Container slide types provide enhanced visual presentation for specialized content. These types use structured layouts to improve information hierarchy and visual appeal.

### Callout Slides

Use for important notices, warnings, tips, or highlighted information that requires special attention.

**When to Use**:
- Safety warnings or critical cautions
- Best practices and tips
- Important reminders
- Key takeaways that need emphasis

```json
{
  "type": "callout",
  "title": "Important Notice",
  "content": {
    "callouts": [
      {
        "callout_type": "warning",
        "heading": "Caution",
        "text": "Save your work frequently to avoid data loss"
      },
      {
        "callout_type": "tip",
        "heading": "Pro Tip",
        "text": "Use keyboard shortcuts for efficiency"
      },
      {
        "callout_type": "info",
        "text": "Additional documentation available online"
      }
    ]
  },
  "notes": "Emphasize these points during presentation. The warning is critical for new users."
}
```

**Callout Types**:
- `warning`: Red/yellow styling for cautions and alerts
- `tip`: Green/blue styling for helpful suggestions
- `info`: Blue styling for informational notes
- `note`: Neutral styling for general remarks

### Stats Grid Slides

Use for presenting quantitative data, metrics, KPIs, or numerical highlights in a scannable format.

**When to Use**:
- Dashboard-style metric displays
- Quarterly results or performance indicators
- Survey results and statistics
- Growth metrics and trends

```json
{
  "type": "stats_grid",
  "title": "Q4 Performance Metrics",
  "content": {
    "stats": [
      {
        "value": "95%",
        "label": "Customer Satisfaction",
        "trend": "up",
        "highlight": true
      },
      {
        "value": "$2.5M",
        "label": "Quarterly Revenue",
        "trend": "up"
      },
      {
        "value": "45",
        "label": "New Clients",
        "trend": "neutral"
      },
      {
        "value": "12%",
        "label": "Market Share",
        "trend": "up"
      }
    ],
    "stats_layout": "2x2"
  },
  "notes": "Highlight the satisfaction score improvement from 89% last quarter. Revenue exceeded projections by 15%."
}
```

**Layout Options**:
- `3x1`: Three stats in a horizontal row (ideal for 3 key metrics)
- `2x2`: Four stats in a grid (balanced dashboard view)
- `4x1`: Four stats in a row (comparison emphasis)

**Trend Indicators**:
- `up`: Positive trend indicator (green arrow)
- `down`: Negative trend indicator (red arrow)
- `neutral`: No change indicator (gray dash)

### Cards Grid Slides

Use for organizing related information into distinct, scannable cards.

**When to Use**:
- Service or product offerings
- Team member profiles
- Feature comparisons
- Process steps or phases

```json
{
  "type": "cards_grid",
  "title": "Our Core Services",
  "content": {
    "cards": [
      {
        "title": "Consulting",
        "items": [
          "Strategic Planning",
          "Process Assessment",
          "Risk Analysis"
        ],
        "color": "primary"
      },
      {
        "title": "Development",
        "items": [
          "Custom Solutions",
          "System Integration",
          "Quality Assurance"
        ],
        "color": "secondary"
      },
      {
        "title": "Support",
        "items": [
          "Training Programs",
          "24/7 Helpdesk",
          "Maintenance"
        ],
        "color": "accent"
      }
    ],
    "cards_columns": 3
  },
  "notes": "Walk through each service area. Mention recent client success stories for consulting and development."
}
```

**Column Options**:
- `2`: Two cards side-by-side (detailed content)
- `3`: Three cards across (balanced layout)
- `4`: Four cards across (compact overview)

**Color Themes**:
- `primary`: Main brand color
- `secondary`: Secondary brand color
- `accent`: Accent/highlight color
- `neutral`: Gray/neutral styling

### Key Concept Slides

Use for defining important terms, principles, or foundational concepts that require emphasis.

**When to Use**:
- Defining key terminology
- Explaining core principles
- Highlighting critical concepts
- Educational content

```json
{
  "type": "key_concept",
  "title": "Understanding Machine Learning",
  "content": {
    "concept_title": "Machine Learning",
    "definition": "A subset of artificial intelligence that enables systems to learn and improve from experience without being explicitly programmed",
    "details": [
      "Requires training data to identify patterns",
      "Improves accuracy over time with more data",
      "Powers recommendation systems and predictions",
      "Different from traditional rule-based programming"
    ],
    "concept_style": "boxed"
  },
  "notes": "Elaborate on real-world applications like Netflix recommendations and spam filters. Mention the difference between supervised and unsupervised learning if questions arise."
}
```

**Style Options**:
- `boxed`: Prominent box around definition
- `highlighted`: Colored background emphasis
- `simple`: Clean, minimal styling

### Content Slides with Inline Containers

Standard content slides can include inline containers for mixed content presentation.

**When to Use**:
- Adding callouts to bullet lists
- Highlighting specific points within content
- Combining regular content with emphasized information

```json
{
  "type": "content",
  "title": "Implementation Steps",
  "content": {
    "bullets": [
      "Step 1: Setup development environment",
      "Step 2: Configure system parameters",
      "Step 3: Deploy to production"
    ],
    "containers": [
      {
        "container_type": "callout",
        "callout": {
          "type": "warning",
          "heading": "Critical",
          "text": "Always backup your database before deployment"
        }
      },
      {
        "container_type": "callout",
        "callout": {
          "type": "tip",
          "text": "Use staging environment for testing first"
        }
      }
    ]
  },
  "notes": "Emphasize the backup warning - mention the incident from Q2 as a cautionary tale. Staging tests should run for at least 24 hours."
}
```

### Two Content Slides with Containers

Two-column layouts can also incorporate containers for structured visual organization.

```json
{
  "type": "two_content",
  "title": "Development Phases",
  "content": {
    "left_title": "Planning Phase",
    "left": [
      "Requirements gathering",
      "Architecture design",
      "Resource allocation"
    ],
    "right_title": "Execution Phase",
    "right": [
      "Development sprints",
      "Quality assurance",
      "Deployment"
    ],
    "containers": [
      {
        "container_type": "stats",
        "stats": {
          "stats": [
            {"value": "2-4", "label": "Planning Weeks"},
            {"value": "8-12", "label": "Execution Weeks"}
          ],
          "layout": "2x1"
        }
      }
    ]
  },
  "notes": "Highlight the importance of thorough planning. Execution timeline varies based on project complexity."
}
```

## Container Selection Guidelines

### Content Pattern Recognition

When analyzing source content, identify these patterns for container selection:

| Content Pattern | Recommended Slide Type | Reason |
|-----------------|----------------------|---------|
| Numerical data, metrics, KPIs | `stats_grid` | Visual impact and scannability |
| Warnings, cautions, alerts | `callout` (warning) | Visual emphasis and attention |
| Tips, best practices | `callout` (tip) | Helpful distinction from main content |
| Key terminology definitions | `key_concept` | Educational clarity |
| Grouped services/features | `cards_grid` | Organized comparison |
| Mixed content with highlights | `content` + inline containers | Flexible emphasis |
| Presentation outline, session overview | `agenda` | Navigation and progress tracking |
| Section transitions, major breaks | `divider` | Visual structure and pacing |
| Quantitative data, trends, comparisons | `data_viz` | Chart-based data visualization |
| Photo galleries, visual arrays | `image_grid` | Organized multi-image display |

### Visual Hierarchy Considerations

**Use containers when**:
- Content requires special visual emphasis
- Information needs to stand out from main flow
- Metrics or data need dashboard-style presentation
- Definitions require focused attention

**Avoid containers when**:
- Content is already brief (3-4 bullets)
- Standard bullet format provides sufficient clarity
- Visual clutter would reduce readability
- Presentation theme doesn't support enhanced layouts

### Combining Multiple Container Types

For complex slides, combine container types strategically:

```json
{
  "type": "content",
  "title": "Project Overview",
  "content": {
    "bullets": ["Key milestone 1", "Key milestone 2"],
    "containers": [
      {
        "container_type": "stats",
        "stats": {
          "stats": [
            {"value": "$500K", "label": "Budget"},
            {"value": "6 mo", "label": "Timeline"}
          ],
          "layout": "2x1"
        }
      },
      {
        "container_type": "callout",
        "callout": {
          "type": "warning",
          "text": "Resource constraints require careful planning"
        }
      }
    ]
  },
  "notes": "Present overview first, then dive into metrics and constraints."
}
```

**Best Practices**:
- Limit to 2-3 containers per slide for clarity
- Place containers logically (stats before callouts typically)
- Ensure containers enhance rather than overwhelm content

## Content Transformation Rules

### From Long-Form Content

When converting long-form content to slides:

1. **Extract Main Points**: Identify 3-6 key takeaways
2. **Create Headlines**: Transform paragraphs into concise titles
3. **Distill Bullets**: One idea per bullet, 6 words max
4. **Preserve Detail**: Full explanations go in speaker notes
5. **Add Structure**: Group related points into sections

### From Outlines

When converting outlines to slides:

1. **H1 Headers**: Become section titles
2. **H2 Headers**: Become slide titles
3. **H3 Headers**: Become sub-section slides
4. **Bullet Lists**: Become slide content
5. **Paragraphs**: Become speaker notes

### Content Splitting Rules

When content is too dense for a single slide:

```
IF bullets > 6:
  → Split into multiple slides with related groupings
  → Use "Part 1 of 2" or numbered titles
  → Ensure logical flow between slides

IF bullet text > 6 words:
  → Shorten to key phrase
  → Move full text to speaker notes
  → Use active voice and strong verbs
```

## Quality Standards

### Slide Content Validation

Every generated slide must pass these checks:

- [ ] Title is clear and descriptive (max 10 words)
- [ ] Maximum 6 bullet points
- [ ] Bullet text is concise (target 6 words)
- [ ] Parallel grammatical structure in lists
- [ ] One main idea per slide
- [ ] Speaker notes provide context

### Section Structure Validation

Each section must:

- [ ] Have a clear section header slide
- [ ] Progress logically from introduction to conclusion
- [ ] Include variety of slide types (not all bullets)
- [ ] End with summary or call-to-action when appropriate

## Parallel Execution Protocol

### Batch Processing

For presentations with multiple sections:

```python
# Execute content generation in parallel batches (max 10 per batch)
for batch in section_batches:
    tasks = [
        Task(
            subagent_type="slide-content-generator",
            description=f"Generate {section.title} slides",
            prompt=f"Create slides for section: {section.title}..."
        )
        for section in batch
    ]
    await asyncio.gather(*tasks)
```

### Individual Section Focus

Each agent instance handles ONE section:
- Receives section outline and source content
- Generates all slides for that section
- Outputs structured JSON for that section only
- Never crosses section boundaries

## Speaker Notes Best Practices

### Purpose of Speaker Notes

Speaker notes serve as:
- Expanded explanations of bullet points
- Presenter talking points and transitions
- Background information and context
- Answers to anticipated questions
- Timing guidance

### Notes Structure

```
[TALKING POINTS]
- Expand on first bullet: full explanation here
- Key statistic or example to mention
- Transition phrase to next slide

[BACKGROUND]
Additional context the presenter may need

[TIMING]
Approximately 2-3 minutes for this slide
```

## Output Example

Complete section output:

```json
{
  "section": {
    "title": "Getting Started",
    "slides": [
      {
        "type": "section_header",
        "title": "Getting Started",
        "content": {
          "subtitle": "Your first steps to success"
        },
        "notes": "This section covers the basics..."
      },
      {
        "type": "content",
        "title": "Three Steps to Begin",
        "content": {
          "bullets": [
            "Define your goal clearly",
            "Gather necessary resources",
            "Create an action plan"
          ]
        },
        "notes": "Walk through each step with examples..."
      },
      {
        "type": "content",
        "title": "Common Pitfalls to Avoid",
        "content": {
          "bullets": [
            "Starting without clear objectives",
            "Underestimating time requirements",
            "Skipping the planning phase"
          ]
        },
        "notes": "Share a brief story about each pitfall..."
      }
    ]
  }
}
```

## Integration Points

### Upstream: Content Analyzer
Receives structured content analysis with:
- Main topics identified
- Suggested section breakdown
- Key points extracted
- Source material references

### Downstream: PPTX Packager
Outputs slide JSON for:
- Layout selection and application
- Theme integration
- Final PPTX assembly

## Error Handling

### Content Too Sparse
If source content is insufficient:
- Flag section for review
- Suggest topics to expand
- Provide placeholder structure

### Content Too Dense
If content cannot fit presentation format:
- Split into multiple presentations
- Recommend appendix slides
- Prioritize most important points
