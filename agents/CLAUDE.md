# Agent Protocols and Coordination

This file contains protocols for Slideforge agent behavior, workspace usage, and coordination strategies.

## Agent Scratchpad Protocol

**All agents MUST use dedicated scratchpads for design decisions.**

### Scratchpad Usage Requirements
```
WHEN AGENTS SHOULD CREATE SCRATCHPADS:
1. **Presentation Architecture** - section structure, slide count, content flow
2. **Layout Selection** - choosing appropriate slide types
3. **Content Transformation** - converting input to slide format
4. **Quality Decisions** - splitting content, organizing sections

SCRATCHPAD ORGANIZATION:
- ONE scratchpad per agent: `agent_workspaces/{agent_type}_scratchpad.md`
- All agent work in single file: analysis, decisions, todos, rationale
- Structured sections: ## Analysis, ## Decisions, ## Updated Todos, ## Rationale
```

## Agent Autonomy and Responsibilities

### Agent-to-Orchestrator Todo Integration
```
AGENT TODO LIST PROTOCOL:
  → Planning agents provide detailed todo lists
  → Todo items must be specific, actionable tasks
  → Orchestrator loads agent todo lists into TodoWrite
  → Orchestrator executes via appropriate agents
```

### Agent Responsibilities
```
AGENTS ARE RESPONSIBLE FOR:
  ✅ Analyzing content and determining optimal structure
  ✅ Creating comprehensive todo lists
  ✅ Determining slide layouts and content organization
  ✅ Recommending parallel batching strategies
  ✅ Providing specific, actionable tasks
```

## Agent Coordination Strategies

### Large Presentations (20+ slides)
```
  → ORCHESTRATOR uses individual section agents
  → PARALLEL execution of multiple agents
  → Each agent handles ONE section
  → Progress tracking via TodoWrite
```

### Medium Presentations (10-20 slides)
```
  → ORCHESTRATOR uses section-based agents
  → Mixed sequential/parallel execution
  → Section-level quality gates
```

### Small Presentations (<10 slides)
```
  → Single agent can handle entire presentation
  → Sequential execution
  → End-to-end quality assurance
```

## Individual Section Protocol

### CRITICAL EXECUTION RULES

**BATCH SIZE LIMITATIONS:**
- Maximum 10 simultaneous Task calls per batch
- Wait for batch completion before starting next batch

**PARALLEL EXECUTION PATTERN:**
```
# BATCH 1 (up to 10 agents):
Task(slide-content-generator, "Section 1", "Create introduction slides")
Task(slide-content-generator, "Section 2", "Create main content slides")
# ... up to 10 total

# WAIT for completion
# Update TodoWrite
# THEN execute BATCH 2
```

### ANTI-PATTERNS TO AVOID
```
❌ NEVER assign multiple sections to one agent
❌ NEVER use prompts like "create all sections"
✅ ALWAYS use individual section assignments
✅ ALWAYS verify each Task specifies ONE section
```

## Agent Workspace Containment

**MANDATORY for ALL agents:**

1. **Single Project Folder**: All agents receive project folder path
2. **Agent Subdirectories**: Each agent creates subdirectory within project folder
3. **No Scattered Files**: Outputs ONLY within assigned project folder
4. **Folder Inheritance**: All workspaces contained within timestamped project folder

## Available Agents

| Agent | Purpose | Output |
|-------|---------|--------|
| `content-analyzer` | Analyze input content | Structure plan |
| `presentation-outliner` | Plan presentation | Section breakdown |
| `slide-content-generator` | Create slide content | Section JSON |
| `slide-layout-mapper` | Select layouts | Layout assignments |
| `slide-validator` | Quality validation | Validation report |
| `pptx-packager` | Final assembly | PPTX file |

## Quality Standards

### Slide Content Validation
```
EVERY SLIDE MUST:
  ✅ Have a clear, descriptive title
  ✅ Follow 6x6 rule (max 6 bullets, 6 words each)
  ✅ Focus on one main idea
  ✅ Include speaker notes
  ✅ Use appropriate slide type
```

### Section Validation
```
EVERY SECTION MUST:
  ✅ Have logical flow from first to last slide
  ✅ Include section header slide
  ✅ Progress from introduction to conclusion
  ✅ Use consistent styling
```

## Handoff Protocol

### Content Analyzer → Presentation Outliner
```
Pass: Content analysis, key topics, suggested structure
Receive: Section breakdown, slide count estimates
```

### Presentation Outliner → Slide Content Generator
```
Pass: Section outline, content requirements
Receive: Slide JSON per section
```

### Slide Content Generator → PPTX Packager
```
Pass: Combined slide JSON, metadata, theme selection
Receive: Final PPTX file
```
