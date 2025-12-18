# Provenance Tracking in Slideforge Pipeline

## Overview

The Slideforge pipeline implements comprehensive provenance tracking based on LibV2 patterns. This ensures complete auditability and traceability from source content to final PPTX output.

## Architecture

### Core Components

1. **ProvenanceInfo** - Source file lineage and metadata
2. **ProcessingLog** - Aggregate pipeline execution statistics
3. **ProcessingStep** - Detailed stage-by-stage execution records
4. **ProvenanceEntry** - Granular transformation tracking (source-to-target mapping)
5. **QualityMetadata** - Quality metrics and validation results

### Data Flow

```
Input File
    ↓
[ProvenanceInfo Created]
    ↓ (compute SHA256 hash)
    ↓
[Pipeline Stages Execute]
    ↓ (each stage tracked in ProcessingStep)
    ↓ (agent invocations logged)
    ↓
[ProcessingLog Updated]
    ↓ (aggregate statistics)
    ↓
[Quality Validation]
    ↓
[Manifest Finalized & Saved]
    ↓
Output PPTX + Manifest JSON
```

## ProvenanceInfo Structure

Tracks comprehensive source file metadata:

```python
{
  "sourcePath": "/path/to/input.md",
  "sourceFormat": "markdown",           # markdown, json, text, html
  "pipelineVersion": "1.0.0",
  "processingTimestamp": "2025-12-17T12:00:00Z",
  "inputHash": "abc123...",             # SHA256 hash
  "originalFilename": "input.md",
  "fileSizeBytes": 10240,
  "sourceType": "document",             # document, outline, notes
  "originalProvider": "Author Name",
  "parentVersion": null                 # If derived from another presentation
}
```

### Use Cases

- **Reproducibility**: Input hash ensures exact source can be identified
- **Lineage Tracking**: Know which file version produced which output
- **Audit Trail**: Complete history of content origins

## ProcessingLog Structure

Aggregates pipeline execution statistics:

```python
{
  "stagesCompleted": [
    "ingestion",
    "extraction",
    "transformation",
    "template_selection",
    "validation",
    "generation"
  ],
  "agentsUsed": [
    "content-analyzer",
    "slide-content-generator",
    "slide-layout-mapper"
  ],
  "slidesCreated": 25,
  "warningsGenerated": 3,
  "errorsGenerated": 0,
  "durationSeconds": 42.5
}
```

### Use Cases

- **Performance Monitoring**: Track pipeline execution time
- **Quality Tracking**: Monitor warning/error rates
- **Agent Accountability**: Know which agents participated
- **Output Metrics**: Count slides and sections generated

## ProcessingStep Structure

Records detailed stage execution:

```python
{
  "stage": "transformation",
  "timestamp": "2025-12-17T12:00:30Z",
  "durationMs": 1250.5,
  "inputHash": "abc123...",             # Hash of stage input
  "outputHash": "def456...",            # Hash of stage output
  "success": true,
  "errors": [],
  "warnings": ["Warning message"],
  "metadata": {
    "sections": 5,
    "slides": 25
  }
}
```

### Use Cases

- **Debug Failed Stages**: Identify exactly where pipeline failed
- **Performance Analysis**: Find bottleneck stages
- **Reproducibility**: Input/output hashes track data flow
- **Error Investigation**: Detailed error and warning tracking

## ProvenanceEntry Structure

Tracks granular source-to-output transformations:

```python
{
  "sourceId": "chapter_01",
  "sourceType": "chapter",               # chapter, section, block
  "sourcePath": "$.chapters[0]",        # JSONPath-like reference
  "targetIds": ["slide_001", "slide_002"],
  "transformation": "chapter-to-slides",
  "timestamp": "2025-12-17T12:00:35Z"
}
```

### Use Cases

- **Content Attribution**: Map output slides back to source content
- **Transformation Tracking**: Know how content was transformed
- **Agent Work Tracking**: Log what each agent produced
- **Citation Generation**: Generate source citations for slides

## QualityMetadata Structure

Tracks validation and quality metrics:

```python
{
  "sixSixViolations": 2,                # Slides violating 6x6 rule
  "notesCoverage": 0.85,                # Percentage with speaker notes
  "slideTypeVariety": 4,                # Number of unique slide types
  "validationScore": 92.5,              # Overall quality score (0-100)
  "totalSlides": 25,
  "totalSections": 5,
  "issues": [
    {
      "type": "six_six_violation",
      "slide": "Introduction Overview",
      "bulletCount": 8
    }
  ]
}
```

### Use Cases

- **Quality Gates**: Enforce minimum quality thresholds
- **Content Improvement**: Identify specific quality issues
- **Template Selection**: Choose templates based on content complexity
- **Reporting**: Generate quality reports for stakeholders

## Usage Examples

### Creating a Manifest

```python
from manifest import create_manifest

# Option 1: Using convenience function
manifest = create_manifest(
    source_path="/path/to/input.md",
    source_format="markdown",
    pipeline_version="1.0.0",
    source_type="document",
    original_provider="Content Team"
)

# Option 2: Manual creation
from manifest import PipelineManifest

manifest = PipelineManifest()
manifest.create_provenance_info(
    source_path="/path/to/input.md",
    source_format="markdown",
    pipeline_version="1.0.0",
    input_hash="abc123...",
    source_type="document"
)
manifest.initialize_processing_log()
```

### Updating During Pipeline Execution

```python
# Stage completion
manifest.update_processing_log(
    stage_name="extraction",
    warnings=2,
    errors=0
)

# Track slides created
manifest.update_processing_log(
    slides_created=15
)

# Log agent work
manifest.add_agent_log(
    agent_name="slide-content-generator",
    task="Generate introduction slides",
    result={
        "target_ids": ["slide_001", "slide_002", "slide_003"],
        "success": True
    }
)

# Add detailed provenance entry
from manifest import ProvenanceEntry

entry = ProvenanceEntry(
    source_id="chapter_01",
    source_type="chapter",
    source_path="$.chapters[0]",
    target_ids=["slide_001", "slide_002"],
    transformation="chapter-to-slides"
)
manifest.add_provenance(entry)
```

### Adding Quality Metadata

```python
from manifest import QualityMetadata

quality = QualityMetadata(
    six_six_violations=2,
    notes_coverage=0.85,
    slide_type_variety=4,
    validation_score=92.5,
    total_slides=25,
    total_sections=5,
    issues=[
        {
            "type": "six_six_violation",
            "slide": "Introduction Overview",
            "bullet_count": 8
        }
    ]
)
manifest.set_quality(quality)
```

### Finalizing and Saving

```python
# Finalize with total duration
manifest.finalize_processing_log(duration_seconds=42.5)

# Set output information
manifest.set_output_info(
    path="/output/presentation.pptx",
    format="pptx",
    size=2048576
)

# Save manifest
from pathlib import Path
manifest.save(Path("/output/manifest.json"))

# Or use convenience function
from manifest import save_manifest
save_manifest(manifest, "/output/manifest.json")
```

### Loading Existing Manifest

```python
from manifest import load_manifest

manifest = load_manifest("/output/manifest.json")

# Access provenance info
print(f"Source: {manifest.provenance_info.source_path}")
print(f"Format: {manifest.provenance_info.source_format}")
print(f"Hash: {manifest.provenance_info.input_hash}")

# Access processing log
print(f"Stages: {manifest.processing_log.stages_completed}")
print(f"Agents: {manifest.processing_log.agents_used}")
print(f"Slides: {manifest.processing_log.slides_created}")
print(f"Duration: {manifest.processing_log.duration_seconds}s")

# Get summary
summary = manifest.get_summary()
print(json.dumps(summary, indent=2))
```

## Integration with Pipeline

The orchestrator (`orchestrator.py`) automatically tracks provenance at each stage:

### Stage 1: Ingestion
- Computes input file hash
- Creates ProvenanceInfo
- Initializes ProcessingLog

### Stage 2-5: Processing Stages
- Records ProcessingStep for each stage
- Updates ProcessingLog with warnings/errors
- Tracks stage completion

### Stage 3: Transformation
- Updates ProcessingLog with slide count
- Can add ProvenanceEntry for source-to-slide mapping

### Stage 5: Validation
- Creates QualityMetadata
- Records quality issues

### Stage 6: Generation
- Sets output information
- Finalizes ProcessingLog with duration
- Saves complete manifest

## Manifest Output Example

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "version": "1.0.0",
  "created": "2025-12-17T12:00:00Z",
  "updated": "2025-12-17T12:00:45Z",

  "provenanceInfo": {
    "sourcePath": "/inputs/presentation.md",
    "sourceFormat": "markdown",
    "pipelineVersion": "1.0.0",
    "processingTimestamp": "2025-12-17T12:00:00Z",
    "inputHash": "abc123def456...",
    "originalFilename": "presentation.md",
    "fileSizeBytes": 10240,
    "sourceType": "document",
    "originalProvider": "Content Team",
    "parentVersion": null
  },

  "processingLog": {
    "stagesCompleted": [
      "ingestion",
      "extraction",
      "transformation",
      "template_selection",
      "validation",
      "generation"
    ],
    "agentsUsed": ["content-analyzer", "slide-generator"],
    "slidesCreated": 25,
    "warningsGenerated": 3,
    "errorsGenerated": 0,
    "durationSeconds": 42.5
  },

  "processingSteps": [
    {
      "stage": "ingestion",
      "timestamp": "2025-12-17T12:00:01Z",
      "durationMs": 250.5,
      "inputHash": "...",
      "outputHash": "...",
      "success": true,
      "errors": [],
      "warnings": [],
      "metadata": {
        "format": "markdown",
        "size_bytes": 10240
      }
    }
    // ... more stages
  ],

  "provenance": [
    {
      "sourceId": "chapter_01",
      "sourceType": "chapter",
      "sourcePath": "$.chapters[0]",
      "targetIds": ["slide_001", "slide_002"],
      "transformation": "chapter-to-slides",
      "timestamp": "2025-12-17T12:00:35Z"
    }
    // ... more entries
  ],

  "quality": {
    "sixSixViolations": 2,
    "notesCoverage": 0.85,
    "slideTypeVariety": 4,
    "validationScore": 92.5,
    "totalSlides": 25,
    "totalSections": 5,
    "issues": [...]
  },

  "outputInfo": {
    "path": "/output/presentation.pptx",
    "format": "pptx",
    "size": 2048576,
    "timestamp": "2025-12-17T12:00:45Z"
  },

  "templateUsed": "professional",
  "pipelineConfig": {...}
}
```

## Backward Compatibility

The enhanced manifest maintains full backward compatibility:

- **Legacy fields preserved**: `source_info`, `processing_steps`, `provenance`, `quality`, `output_info`
- **New fields added**: `provenance_info`, `processing_log`
- **Dual tracking**: Both old and new fields are populated
- **Graceful loading**: Old manifests load without the new fields

This ensures existing tools and scripts continue to work while new tools can leverage enhanced tracking.

## LibV2 Pattern Alignment

The provenance tracking follows LibV2 patterns from `/home/bacon/Desktop/1KSUNNY/LibV2`:

- **Source tracking**: Similar to LibV2's `sourceforge_manifest`
- **Content profiling**: Similar to LibV2's `content_profile`
- **Quality metadata**: Similar to LibV2's `quality_metadata`
- **Provenance structure**: Similar to LibV2's `provenance` field
- **Hash-based integrity**: SHA256 hashing for reproducibility

## Testing

Run the test suite to verify provenance tracking:

```bash
cd /home/bacon/Desktop/Slideforge/scripts/pipeline
python3 test_manifest_provenance.py
```

Tests cover:
- ProvenanceInfo creation and serialization
- ProcessingLog functionality
- Manifest creation with enhanced fields
- Save/load round-trip
- Backward compatibility
- Convenience functions

## Future Enhancements

Potential improvements for provenance tracking:

1. **Slide-level provenance**: Track which source paragraphs map to which bullets
2. **Transformation DAG**: Build directed acyclic graph of transformations
3. **Version tracking**: Track presentation version history
4. **Diff generation**: Compare manifests to see what changed
5. **Visualization**: Generate provenance flow diagrams
6. **Export formats**: Export provenance to RDF, GraphML, or other formats

## References

- LibV2 manifest schema: `/home/bacon/Desktop/1KSUNNY/LibV2/schema/course_manifest.schema.json`
- LibV2 course model: `/home/bacon/Desktop/1KSUNNY/LibV2/tools/libv2/models/course.py`
- Slideforge manifest: `/home/bacon/Desktop/Slideforge/scripts/pipeline/manifest.py`
- Slideforge orchestrator: `/home/bacon/Desktop/Slideforge/scripts/pipeline/orchestrator.py`
