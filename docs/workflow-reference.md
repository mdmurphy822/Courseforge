# Slideforge Workflow Reference

Complete workflow phases, execution protocols, and best practices for presentation generation.

---

## Simplified Pipeline

```
INPUT                         PROCESSING                              OUTPUT
─────                         ──────────                              ──────
Structured Content    content-to-slide    presentation    slide-content    slide-layout    pptx
(Markdown/JSON/   ──►    analyzer     ──►   outliner   ──►  generator  ──►   mapper    ──►  packager  ──►  .PPTX
 Outline/Text)
```

---

## Phase 1: Input Analysis & Planning

**Orchestrator Actions:**
1. Create timestamped project folder: `exports/YYYYMMDD_HHMMSS_presentationname/`
2. Invoke planning agent to analyze content structure
3. Planning agent returns structured todo list (NO EXECUTION)
4. Orchestrator loads todo list into TodoWrite

**Key Principle:** Planning agents provide structured todo lists. They do NOT execute tasks.

---

## Phase 2: Presentation Structure

**Orchestrator Actions:**
1. Invoke `presentation-outliner` agent
2. Agent determines optimal slide progression based on:
   - Content logical flow
   - Audience engagement patterns
   - Visual variety requirements
3. Agent creates presentation structure
4. Validation triggers automatically after outline completion

**Structure Guidelines:**
- Title slide first
- Section headers for major topics
- Content slides grouped by theme
- Quote or summary slides for emphasis

---

## Phase 3: Slide Content Generation

**Execution Protocol:**
1. Review content generation tasks from todo list
2. Execute slide-content-generator agents in parallel batches

**Critical Batch Constraints:**
- Maximum: 10 agents per batch
- Each agent creates exactly ONE section
- Wait for batch completion before next batch
- Update TodoWrite after each batch

**Anti-Patterns (NEVER DO):**
- Assign multiple sections to one agent
- Use prompts like "create all slides"
- Exceed 10 simultaneous Task calls

**Correct Pattern:**
```python
# BATCH 1 (10 agents max)
Task(slide-content-generator, "Create introduction section")
Task(slide-content-generator, "Create background section")
Task(slide-content-generator, "Create main content section")
# ... up to 10 total

# WAIT for completion, update todos, then BATCH 2
```

---

## Phase 4: Layout Mapping

**Orchestrator Actions:**
1. Invoke `slide-layout-mapper` agent
2. Agent assigns optimal layouts based on content type:
   - Bullet lists → Content layout
   - Comparisons → Two-column or comparison layout
   - Key quotes → Quote layout
   - Transitions → Section header layout

**Layout Selection Guide:**

| Content Type | Recommended Layout |
|--------------|-------------------|
| Opening | Title slide |
| Topic transition | Section header |
| Key points | Content |
| Side-by-side info | Two content |
| Pros/cons | Comparison |
| Key message | Quote |
| Visual focus | Image |

---

## Phase 5: Validation & Packaging

**Orchestrator Actions:**
1. Invoke `slide-validator` agent:
   - Check content completeness
   - Verify slide type appropriateness
   - Validate speaker notes presence
2. If issues found: reinvoke agents to fix
3. When validation complete: invoke `pptx-packager`
4. Output: Single PPTX file

---

## Orchestrator Protocol Summary

| Step | Actor | Action |
|------|-------|--------|
| 1 | Planning Agent | Analyzes input, returns todo list (NO execution) |
| 2 | Orchestrator | Loads todo list into TodoWrite |
| 3 | Orchestrator | Executes todos via appropriate agents |
| 4 | Execution Agents | Work from todo specs (NO todo modifications) |
| 5 | Orchestrator | Manages all todo state changes |

**Critical Rule:** Only orchestrator modifies TodoWrite. No agent-to-agent todo feedback loops.

---

## Agent Reference

| Agent | Purpose | Input | Output |
|-------|---------|-------|--------|
| `presentation-outliner` | Structure planning | Source content | Section outline |
| `slide-content-generator` | Content creation | Section spec | Slide content JSON |
| `slide-layout-mapper` | Layout selection | Content analysis | Layout assignments |
| `slide-validator` | Quality validation | Full presentation | Validation report |
| `pptx-packager` | PPTX assembly | Validated content | .pptx file |

---

## File Naming Convention

Presentation files:
```
YYYYMMDD_HHMMSS_presentationname.pptx
```

Content files:
```
section_XX_description.json
```

Examples:
- `section_01_introduction.json`
- `section_02_main_content.json`
- `section_03_conclusion.json`

---

## Project Folder Structure

```
exports/YYYYMMDD_HHMMSS_presentationname/
├── 01_content_analysis/
├── 02_slide_content/
│   ├── section_01/
│   ├── section_02/
│   └── section_XX/
├── 03_final_output/
│   └── presentation.pptx
├── agent_workspaces/
└── project_log.md
```

---

## Quality Standards

### Slide Design Rules
- **6x6 Rule**: Maximum 6 bullets, 6 words per bullet
- **One Idea Per Slide**: Focus on single concept
- **Visual Hierarchy**: Clear title, supporting points
- **Consistent Styling**: Same layouts for similar content

### Validation Checklist

**Before Content Generation:**
- [ ] Planning agent has provided todo list
- [ ] Orchestrator has loaded todos into TodoWrite
- [ ] Individual section assignments prepared
- [ ] Batch size ≤10 confirmed

**Before Packaging:**
- [ ] All slides created
- [ ] Quality validation passed
- [ ] Speaker notes included
- [ ] No placeholder content

**After Packaging:**
- [ ] Single PPTX file generated
- [ ] File opens correctly
- [ ] Theme applied consistently
- [ ] All sections present

---

## Execution Commands

### Generate from JSON
```bash
cd scripts/pptx-generator
python pptx_generator.py -i content.json -o presentation.pptx
```

### With Theme
```bash
python pptx_generator.py -i content.json -o presentation.pptx --theme corporate
```

### List Available Themes
```bash
python pptx_generator.py --list-templates
```

---

## Troubleshooting Quick Reference

| Issue | Solution |
|-------|----------|
| Empty slides | Check JSON content structure |
| Theme not applied | Verify theme name with --list-templates |
| Layout wrong | Use correct slide type |
| Missing notes | Add "notes" field to slides |
| Generation fails | Validate JSON syntax |

For detailed troubleshooting, see [troubleshooting.md](troubleshooting.md).
