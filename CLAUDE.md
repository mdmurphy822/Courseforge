# Courseforge

AI-powered instructional design system that creates and remediates accessible, LMS-ready IMSCC course packages.

---

## Quick Start

### Course Creation Mode
**Input**: Exam objectives (PDF/text) + optional DART-processed textbooks (HTML)
**Output**: Single IMSCC file ready for Brightspace import

### Course Intake/Remediation Mode (NEW)
**Input**: Any IMSCC package (Canvas, Blackboard, Moodle, Brightspace, etc.)
**Output**: Fully accessible, enhanced IMSCC with 100% WCAG 2.2 AA compliance

---

## Workflow Pipelines

### Pipeline 1: Course Creation
```
INPUT                         PROCESSING                              OUTPUT
─────                         ──────────                              ──────
Exam Objectives ──┐
(PDF/text)        │
                  ├──► exam-research ──► course-outliner ──► content-generator ──► brightspace-packager ──► IMSCC
Textbooks ────────┘         │                │                    │
(DART HTML)           requirements-      oscqr-            quality-assurance
                      collector          evaluator              (per batch)
```

### Pipeline 2: Intake & Remediation (NEW)
```
INPUT                         PROCESSING                                    OUTPUT
─────                         ──────────                                    ──────
Any IMSCC Package ──► imscc-intake-parser ──► content-analyzer ──┬──► dart-automation-coordinator
(Canvas, Blackboard,          │                   │               │           (PDF/Office → HTML)
 Moodle, Brightspace)         │                   │               │
                              │                   │               ├──► accessibility-remediation
                              ▼                   │               │           (WCAG fixes)
                     LMS Detection                │               │
                     Version Detection            │               ├──► content-quality-remediation
                     Content Inventory            │               │           (Educational depth)
                                                  │               │
                                                  │               ├──► intelligent-design-mapper
                                                  │               │           (Component styling)
                                                  │               │
                                                  │               └──► remediation-validator ──► brightspace-packager ──► Improved IMSCC
                                                  │                           (Final QA)
                                                  ▼
                                         Remediation Queue
```

---

## Orchestrator Protocol

**The orchestrator is a lightweight task manager. Specialized agents determine frameworks and content structure.**

### Orchestrator Responsibilities
1. Create timestamped project folder in `exports/`
2. Invoke planning agent → receive todo list (NO EXECUTION)
3. Load todo list into TodoWrite (single source of truth)
4. Execute todos via specialized agents in parallel batches
5. Coordinate quality validation
6. Invoke final packaging

### Workflow Steps
```
USER REQUEST →
  STEP 1: Planning agent analyzes request, returns todo list (NO execution) →
  STEP 2: Orchestrator loads todo list into TodoWrite →
  STEP 3: Orchestrator executes todos via agents (agents do NOT modify TodoWrite) →
  STEP 4: Quality validation (oscqr-course-evaluator + quality-assurance) →
  STEP 5: Package generation (brightspace-packager) →
  OUTPUT: Single IMSCC file
```

---

## Available Agents

### Course Creation Agents
| Agent | Purpose | When to Use |
|-------|---------|-------------|
| `exam-research` | Certification objective analysis | Analyzing exam/certification objectives |
| `requirements-collector` | Course specification gathering | New course projects |
| `course-outliner` | Course structure and learning objectives | Creating course framework |
| `content-generator` | Educational content creation | Content development (1 file per agent) |
| `educational-standards` | Pedagogical framework compliance | UDL, ADDIE, Bloom's alignment |
| `quality-assurance` | Pattern prevention and validation | Quality gates |
| `oscqr-course-evaluator` | Educational quality assessment | OSCQR evaluation |
| `brightspace-packager` | IMSCC package generation | Final deployment |
| `html-design-research` | HTML/CSS design pattern research | Template and design validation |
| `objective-synthesizer` | Learning objective synthesis | Combining objectives from textbooks |
| `textbook-ingestor` | Textbook content processing | Entry point for textbook materials |

### Intake & Remediation Agents (NEW)
| Agent | Purpose | When to Use |
|-------|---------|-------------|
| `imscc-intake-parser` | Universal IMSCC package parsing | Importing existing courses |
| `content-analyzer` | Accessibility/quality gap detection | Analyzing imported content |
| `dart-automation-coordinator` | Automated DART conversion orchestration | Converting PDFs/Office docs to accessible HTML |
| `accessibility-remediation` | Automatic WCAG fixes | Fixing accessibility issues |
| `content-quality-remediation` | Educational depth enhancement | Improving thin content |
| `intelligent-design-mapper` | AI-driven component selection | Applying interactive styling |

---

## Critical Execution Protocols

### Individual File Protocol (MANDATORY)
- ONE agent = ONE file (never multiple files per agent)
- Maximum 10 simultaneous Task calls per batch
- Wait for batch completion before next batch

**Correct:**
```python
Task(content-generator, "Create week_01_module_01_introduction.html")
Task(content-generator, "Create week_01_module_02_concepts.html")
# ... up to 10 per batch
```

**Wrong:**
```python
Task(content-generator, "Create all Week 1 content")  # NEVER DO THIS
```

---

## Project Structure

```
/Courseforge/
├── CLAUDE.md                    # This file
├── README.md                    # Project overview
├── docs/                        # Documentation
│   ├── troubleshooting.md       # Error patterns and solutions
│   ├── workflow-reference.md    # Detailed workflow protocols
│   └── getting-started.md       # Quick start guide
├── agents/                      # Agent specifications
├── inputs/                      # Input files
│   ├── exam-objectives/         # Certification exam PDFs/docs
│   ├── textbooks/               # DART-processed HTML textbooks
│   ├── existing-packages/       # IMSCC packages for intake (NEW)
│   └── design-books/            # Design reference materials
├── templates/                   # HTML templates and components
├── schemas/                     # IMSCC and content schemas
├── imscc-standards/             # Brightspace/IMSCC technical specs
├── scripts/                     # Automation scripts
│   ├── imscc-extractor/         # Universal IMSCC extraction (NEW)
│   ├── dart-batch-processor/    # Automated DART conversion (NEW)
│   ├── component-applier/       # Interactive component application (NEW)
│   └── remediation-validator/   # Final quality validation (NEW)
├── exports/                     # Generated course packages
│   └── YYYYMMDD_HHMMSS_name/    # Timestamped project folders
└── runtime/                     # Agent workspaces
```

### Export Project Structure
```
exports/YYYYMMDD_HHMMSS_coursename/
├── 00_template_analysis/
├── 01_learning_objectives/
├── 02_course_planning/
├── 03_content_development/
│   ├── week_01/
│   └── week_XX/
├── 04_quality_validation/
├── 05_final_package/
├── agent_workspaces/
├── project_log.md
└── coursename.imscc              # Final deliverable
```

---

## Textbook Integration

Textbooks must be pre-processed through DART before use:

1. Run textbook PDF through DART (set `DART_PATH` environment variable):
   ```bash
   cd $DART_PATH
   python convert.py textbook.pdf -o /path/to/courseforge/inputs/textbooks/
   ```
2. DART produces WCAG 2.2 AA accessible HTML
3. Place output in `inputs/textbooks/`
4. Reference in course generation

---

## Quality Standards

### Pattern Prevention
See `docs/troubleshooting.md` for complete pattern list. Critical patterns:
- Schema/namespace consistency (IMS CC 1.1)
- Assessment XML format (QTI 1.2)
- Content completeness (all weeks substantive)
- Organization hierarchy (no empty structures)

### OSCQR Evaluation
Automatic quality assessment after course outline completion:
- 70% threshold for pre-development
- 90% threshold for pre-production
- 100% accessibility compliance required

---

## Documentation

| Document | Location | Purpose |
|----------|----------|---------|
| Troubleshooting | `docs/troubleshooting.md` | Error patterns and solutions |
| Workflow Reference | `docs/workflow-reference.md` | Detailed execution protocols |
| Getting Started | `docs/getting-started.md` | Quick start guide |
| Pattern Prevention | `docs/PATTERN_PREVENTION_GUIDE.md` | Comprehensive pattern catalog |
| Agent Specs | `agents/*.md` | Individual agent protocols |

---

## CSS Color Palette (for content generation)

```css
Primary Blue: #2c5aa0
Success Green: #28a745
Warning Yellow: #ffc107
Danger Red: #dc3545
Light Gray: #f8f9fa
Border Gray: #e0e0e0
```

---

## Template Components

Content generators should incorporate these Bootstrap 4.3.1 components:
- Flip Cards (concept reveals)
- Knowledge Checks (self-assessment)
- Accordions (progressive disclosure)
- Call-out Boxes (info, warning, success, danger)
- Tabbed Content (section organization)
- Activity Cards (learning activities)

Templates located in: `templates/`

---

## Intake & Remediation Workflow (NEW)

### Supported IMSCC Sources
Courseforge can import and remediate IMSCC packages from:
- **Brightspace/D2L** - Detected via `d2l_2p0` namespace
- **Canvas** - Detected via `canvas.instructure` namespace
- **Blackboard** - Detected via `blackboard.com` namespace
- **Moodle** - Detected via `moodle.org` namespace
- **Sakai** - Detected via `sakaiproject.org` namespace
- **Generic IMSCC** - Standard IMS CC 1.1/1.2/1.3

### Intake Workflow Steps
```
1. Place IMSCC package in: inputs/existing-packages/
2. Invoke imscc-intake-parser agent
3. Agent extracts, detects source LMS, inventories content
4. content-analyzer identifies remediation needs
5. Parallel remediation:
   - dart-automation-coordinator: PDFs/Office → accessible HTML
   - accessibility-remediation: WCAG 2.2 AA fixes
   - content-quality-remediation: Educational enhancements
   - intelligent-design-mapper: Interactive component styling
6. remediation-validator: Final quality validation
7. brightspace-packager: Generate improved IMSCC
```

### Remediation Capabilities
| Capability | Target |
|------------|--------|
| PDF Conversion | 100% to accessible HTML via DART |
| Office Documents | 100% to accessible HTML via DART |
| Alt Text | AI-generated for all images |
| Heading Structure | Automatic hierarchy correction |
| Color Contrast | WCAG AA (4.5:1 minimum) |
| Keyboard Navigation | Full accessibility |
| Component Styling | AI-selected interactive elements |
| Quality Enhancement | Learning objectives, summaries, checks |

### Scripts for Intake
| Script | Location | Purpose |
|--------|----------|---------|
| `imscc_extractor.py` | `scripts/imscc-extractor/` | Universal IMSCC parsing |
| `dart_batch_processor.py` | `scripts/dart-batch-processor/` | Parallel DART conversion |
| `component_applier.py` | `scripts/component-applier/` | Interactive component application |
| `remediation_validator.py` | `scripts/remediation-validator/` | Final quality validation |

### Success Metrics
| Metric | Target |
|--------|--------|
| IMSCC import success | 95%+ (any source LMS) |
| WCAG compliance | 100% Level AA |
| DART conversion | 98%+ for PDFs |
| Component accuracy | 90%+ appropriate selections |
