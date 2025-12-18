# Slide Design Guide

Best practices for creating effective presentations with Slideforge.

## The 6x6 Rule

The most important principle in slide design:

- **Maximum 6 bullet points** per slide
- **Maximum 6 words** per bullet point

This keeps slides scannable and prevents information overload.

### Why It Matters

- Audiences read faster than presenters speak
- Too much text causes split attention
- Key points get lost in dense slides
- Simplicity increases retention

### Applying the Rule

**Before (Too Dense):**
```
- The new marketing strategy will focus on social media engagement across multiple platforms including Instagram, Twitter, and LinkedIn
- Our target audience consists of professionals aged 25-45 who are decision makers in their organizations
- We plan to increase our advertising budget by 30% to support these initiatives
```

**After (6x6 Applied):**
```
- Focus: social media engagement
- Platforms: Instagram, Twitter, LinkedIn
- Audience: professionals aged 25-45
- Budget increase: 30%
```

## One Idea Per Slide

Each slide should communicate a single concept.

### Signs You Need to Split

- Slide has multiple headers
- Bullet points cover different topics
- You can't summarize in one sentence
- Audience needs time to process each point

### When to Use Multiple Slides

| One Slide | Multiple Slides |
|-----------|-----------------|
| Single process with steps | Complex workflow with details |
| Simple list | Items needing explanation |
| One comparison | Multiple comparisons |
| Brief overview | Detailed analysis |

## Visual Hierarchy

Guide the audience's eye through your content.

### Title Hierarchy

```
SLIDE TITLE (32pt, bold)
Supporting subtitle if needed (24pt)

• Main bullet point (24pt)
  - Sub-point if necessary (20pt)
```

### Emphasis Techniques

1. **Size**: Larger = more important
2. **Weight**: Bold for emphasis
3. **Color**: Accent color for key terms
4. **Position**: Top/left gets read first
5. **Space**: Isolation draws attention

## Slide Types and When to Use Them

### Title Slide
**Use for**: Opening, presenter introduction
**Content**: Title, subtitle, date/author

### Agenda Slide
**Use for**: Presentation roadmap, expectation setting
**Content**: 3-5 section names with optional descriptions
*(See detailed guidance below)*

### Section Header
**Use for**: Topic transitions, agenda markers
**Content**: Section name, brief description

### Divider Slide
**Use for**: Major section transitions, visual breaks
**Content**: Section name or number with minimal text
*(See detailed guidance below)*

### Content Slide
**Use for**: Most information
**Content**: Title + 3-6 bullet points

### Two Content
**Use for**: Parallel information, before/after
**Content**: Two columns of related points

### Comparison
**Use for**: Pros/cons, options, alternatives
**Content**: Labeled columns with contrasts

### Image Slide
**Use for**: Visual evidence, diagrams, charts
**Content**: Title + large image

### Image Grid Slide
**Use for**: Visual collections, photo galleries
**Content**: 2-9 images arranged in organized grid
*(See detailed guidance below)*

### Data Visualization Slide
**Use for**: Quantitative evidence, trend analysis
**Content**: Chart/graph with descriptive headline
*(See detailed guidance below)*

### Quote Slide
**Use for**: Key messages, testimonials
**Content**: Quote text + attribution

---

## Detailed Slide Type Guidance

The following sections provide in-depth best practices for specialized slide types.

### Agenda Slide

**When to Use:**
- Opening of presentation to set expectations
- Complex presentations with multiple sections
- Workshops or training sessions
- Return to agenda between sections for progress tracking

**Best Practices:**
- Keep to 3-5 main sections (cognitive load limit)
- Use benefit-oriented section names ("What You'll Gain" vs "Section 3")
- Show progress indicators to maintain engagement
- Consider visual alternatives: journey maps, numbered sections, icons

**Avoid:**
- More than 8 items (overwhelming for audiences)
- Presentations under 15 minutes (unnecessary overhead)
- Redundant items like "Questions?" or "Thank You"
- Overly detailed descriptions (keep agenda high-level)

### Divider Slide

**When to Use:**
- Major section transitions between topics
- Presentations over 20 minutes requiring mental breaks
- After complex content requiring audience processing time
- When topic shifts significantly from previous section

**Best Practices:**
- Maintain consistent style throughout presentation
- Use bold colors that contrast with content slides
- Include numbered style for long presentations ("Part 2 of 4")
- Keep text minimal - these are visual pauses, not content

**Avoid:**
- Using at every slide transition (overuse diminishes impact)
- Short presentations (under 10 slides)
- Design similarity to content slides (should be visually distinct)
- Adding unnecessary content or graphics

### Data Visualization Slide

**Chart Selection Guide:**
| Data Type | Recommended Chart |
|-----------|------------------|
| Categories comparison | Column/Bar chart |
| Trend over time | Line chart |
| Parts of whole | Pie chart (max 5 slices) |
| Continuous data distribution | Area chart |

**When to Use:**
- Presenting quantitative evidence or metrics
- Showing trends over time periods
- Comparing values between categories
- Displaying key performance indicators (KPIs)

**Best Practices:**
- Headline states the insight, not just chart description
- Annotate key findings directly on the chart
- Limit to maximum 6 data series for readability
- Include alt text descriptions for accessibility
- Use consistent color coding across related charts

**Avoid:**
- Pie charts with more than 5 slices (use bar chart instead)
- 3D effects that distort data perception
- Excessive data labels cluttering the visualization
- Dual-axis charts unless absolutely necessary

### Image Grid Slide

**Layout Selection:**
| Image Count | Recommended Layout |
|------------|-------------------|
| 2 | 2x1 (side by side) |
| 3 | 3x1 (horizontal row) |
| 4 | 2x2 (square grid) |
| 5-6 | 3x2 (rectangular grid) |
| 7-9 | 3x3 (large grid) |

**When to Use:**
- Product galleries and portfolios
- Team member or people photos
- Before/after visual comparisons
- Visual evidence or example collections
- Location or facility showcases

**Best Practices:**
- Maintain consistent image quality and style throughout
- Provide meaningful captions, not just labels
- Include descriptive alt text for accessibility
- Use medium gap spacing for visual separation
- Ensure all images have similar aspect ratios

**Avoid:**
- Mixing portrait and landscape orientations in same grid
- More than 9 images per slide (use multiple slides instead)
- Low resolution or pixelated images
- Inconsistent visual styles (photos mixed with illustrations)

## Container Slide Types

Slideforge provides specialized container types for enhanced visual presentation.

### Callout Slides
**Use for**: Important notices, tips, warnings, best practices
**Content**: 1-4 colored callout boxes

| Callout Type | Color | Use For |
|--------------|-------|---------|
| `info` | Blue | General information, notes |
| `tip` | Purple | Best practices, shortcuts |
| `warning` | Yellow | Cautions, limitations |
| `success` | Green | Achievements, confirmations |

**When to Use:**
- Highlighting critical information
- Safety or compliance reminders
- Best practices and recommendations
- Key takeaways that need emphasis

**Example:**
```json
{
  "type": "callout",
  "title": "Before You Begin",
  "content": {
    "callouts": [
      {"callout_type": "warning", "text": "Save your work before proceeding"},
      {"callout_type": "tip", "text": "Use keyboard shortcuts for efficiency"}
    ]
  }
}
```

### Stats Grid Slides
**Use for**: Statistics, KPIs, metrics, numeric highlights
**Content**: 2-6 stat cards with value + label

**Layout Options:**
- `auto` - Automatically arranges based on count
- `2x1`, `3x1` - Single row layouts
- `2x2`, `3x2` - Multi-row layouts

**When to Use:**
- Dashboard-style metric displays
- Quarterly results and KPIs
- Survey results and percentages
- Before/after comparisons with numbers

**Example:**
```json
{
  "type": "stats_grid",
  "title": "Q4 Results",
  "content": {
    "stats": [
      {"value": "95%", "label": "Satisfaction", "trend": "up", "highlight": true},
      {"value": "$2.5M", "label": "Revenue", "trend": "up"},
      {"value": "45", "label": "New Clients"}
    ]
  }
}
```

### Cards Grid Slides
**Use for**: Grouped concepts, features, categories
**Content**: 2-6 content cards arranged in columns

**Color Options:**
- `default` - Light gray background
- `primary` - Blue accent
- `secondary` - Green accent
- `accent` - Yellow accent

**When to Use:**
- Presenting parallel concepts
- Feature comparisons
- Team or role introductions
- Service or product categories

**Example:**
```json
{
  "type": "cards_grid",
  "title": "Our Services",
  "content": {
    "cards": [
      {"title": "Consulting", "items": ["Strategy", "Assessment"], "color": "primary"},
      {"title": "Development", "items": ["Design", "Build"], "color": "secondary"}
    ],
    "cards_columns": 2
  }
}
```

### Key Concept Slides
**Use for**: Definitions, terminology, important concepts
**Content**: Term + definition with optional supporting details

**Style Options:**
- `boxed` - Colored box with white text (default)
- `highlighted` - Light background with colored border
- `minimal` - Simple text treatment

**When to Use:**
- Technical term definitions
- Core concept explanations
- Key takeaways requiring emphasis
- Vocabulary or glossary items

**Example:**
```json
{
  "type": "key_concept",
  "title": "Key Definition",
  "content": {
    "concept_title": "Machine Learning",
    "definition": "A subset of AI enabling systems to learn from data",
    "details": ["Requires training data", "Improves over time"],
    "concept_style": "boxed"
  }
}
```

### Inline Containers (within Content Slides)
**Use for**: Mixing regular bullets with highlighted elements
**Content**: Standard bullets + container elements

Use the `containers` array to add visual elements alongside regular content:

```json
{
  "type": "content",
  "title": "Implementation Steps",
  "content": {
    "bullets": ["Step 1: Setup", "Step 2: Configure", "Step 3: Deploy"],
    "containers": [
      {"container_type": "callout", "callout": {"type": "warning", "text": "Backup first"}}
    ]
  }
}
```

**Container Types for Inline Use:**
- `callout` - Colored alert box
- `stat_box` - Single value + label
- `card` - Small content card
- `concept_block` - Term + definition

## Container Usage Guidelines

### When to Use Containers

| Content Pattern | Recommended Container |
|-----------------|----------------------|
| 3+ statistics or metrics | `stats_grid` |
| "Note:", "Warning:", "Tip:" | `callout` |
| Definition or term explanation | `key_concept` |
| 2-4 parallel concepts | `cards_grid` |
| Bullets + one key highlight | Inline `containers` |

### Container Best Practices

1. **Don't overuse** - Maximum 3 callout slides per presentation
2. **Balance variety** - Avoid consecutive container slides of same type
3. **Keep content concise** - Stat values under 10 characters
4. **Maintain hierarchy** - Containers highlight, not replace main content
5. **Use appropriate colors** - Match callout type to content meaning

### Container Limits

| Container Type | Maximum per Slide |
|----------------|-------------------|
| Callouts | 4 |
| Stats | 6 |
| Cards | 6 |
| Inline containers | 4 |
| Details (key concept) | 4 |

## Speaker Notes Best Practices

Speaker notes are your friend. Use them for:

1. **Expanded explanations** that don't fit on slides
2. **Transition phrases** between topics
3. **Data sources** and citations
4. **Anticipated questions** and answers
5. **Timing cues** for pacing

### Notes Structure

```
[TALKING POINTS]
- Expand first bullet: full explanation
- Key statistic to mention
- Story or example to share

[BACKGROUND]
Additional context if asked

[TIMING]
~2-3 minutes for this slide
```

## Color Usage

### Template Color Palettes (WCAG 2.2 AA Compliant)

**Corporate** - Trust + Stability + Success
| Role | Color | Hex |
|------|-------|-----|
| Primary | Navy Blue | #1B4F72 |
| Secondary | Steel Gray | #5D6D7E |
| Accent | Emerald | #1E8449 |
| Text | Charcoal | #1C2833 |

**Educational** - Trust + Growth + Optimism
| Role | Color | Hex |
|------|-------|-----|
| Primary | Deep Blue | #1A5276 |
| Secondary | Teal-Green | #148F77 |
| Accent | Gold | #D4AC0D |
| Background | Warm Cream | #FEF9E7 |

**Creative** - Creativity + Sophistication + Passion
| Role | Color | Hex |
|------|-------|-----|
| Primary | Rich Purple | #6C3483 |
| Secondary | Teal | #17A2B8 |
| Accent | Coral | #E74C3C |
| Background | Lavender | #F4ECF7 |

**Minimal** - Clarity + Action
| Role | Color | Hex |
|------|-------|-----|
| Primary | Charcoal | #212529 |
| Secondary | Cool Gray | #6C757D |
| Accent | Electric Blue | #007BFF |

### Accessible Color Combinations

| Background | Text | Contrast | WCAG |
|------------|------|----------|------|
| White (#FFFFFF) | Charcoal (#1C2833) | 15.5:1 | AAA |
| Cream (#FEF9E7) | Charcoal (#1C2833) | 14.2:1 | AAA |
| Lavender (#F4ECF7) | Purple (#2C2C54) | 10.8:1 | AAA |
| Navy (#1B4F72) | White (#FFFFFF) | 10.4:1 | AAA |

### Color Psychology (Based on Research)

| Color | Psychological Association | Best Use |
|-------|--------------------------|----------|
| **Blue** | Trust, stability, professionalism, calm | Corporate, educational, healthcare |
| **Green/Teal** | Growth, nature, success, prosperity | Finance, health, success indicators |
| **Purple** | Creativity, luxury, mystery, spirituality | Creative, premium brands |
| **Gold/Amber** | Optimism, attention, warmth | Highlights, accents (use darker tones) |
| **Coral/Red** | Passion, energy, urgency | CTAs, alerts (avoid for colorblind users) |

### When to Use Color

- Highlight key terms with accent color
- Differentiate categories with primary/secondary
- Show status (success/warning/error)
- Maintain brand consistency across slides

### Accessibility Requirements

- **WCAG AA minimum**: 4.5:1 contrast for normal text
- **WCAG AAA target**: 7:1 contrast for enhanced accessibility
- **Never rely on color alone**: Use icons, patterns, or text labels
- **Red-green colorblindness**: Affects 8% of men - use blue/orange instead

## Layout Principles

### Alignment

- Align all elements to a grid
- Consistent margins throughout
- Left-align text (easier to read)
- Center only titles and quotes

### White Space

- Don't fill every pixel
- Space between sections
- Breathing room around images
- Margins from edges

### Balance

- Visual weight distribution
- Don't crowd one side
- Images balanced with text
- Consistent element sizes

## Content Organization

### The Pyramid Principle

Start with the conclusion, then provide support.

```
SLIDE: Our Recommendation

• Choose Option B
  - 40% cost savings
  - Faster implementation
  - Better scalability
```

### Logical Flow

1. **Chronological**: Timeline, process steps
2. **Priority**: Most to least important
3. **Problem-Solution**: Issue then answer
4. **Comparison**: Side-by-side analysis

## Common Mistakes to Avoid

### Content Mistakes

- [ ] Full sentences instead of phrases
- [ ] Reading slides word-for-word
- [ ] Too many slides for time allotted
- [ ] Inconsistent terminology
- [ ] Missing conclusions/takeaways

### Design Mistakes

- [ ] Multiple fonts
- [ ] Inconsistent colors
- [ ] Tiny text
- [ ] Cluttered layouts
- [ ] Low-contrast combinations

### Structural Mistakes

- [ ] No clear sections
- [ ] Missing agenda
- [ ] Abrupt ending
- [ ] No summary slide
- [ ] Illogical ordering

## Quick Reference Checklist

Before finalizing any presentation:

- [ ] Each slide passes 6x6 rule
- [ ] One main idea per slide
- [ ] Consistent styling throughout
- [ ] Speaker notes for all slides
- [ ] Logical section flow
- [ ] Clear titles on every slide
- [ ] Accessible color contrast
- [ ] Summary/conclusion slide
