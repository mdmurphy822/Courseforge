# Error Recovery Quick Reference

## Configuration Options

```python
PipelineConfig(
    input_path=Path("input.md"),
    output_path=Path("output.pptx"),
    
    # Error Recovery Options
    enable_checkpoints=True,        # Auto-save state after each stage
    enable_retry=True,              # Auto-retry transient failures
    max_retry_attempts=3,           # Number of retry attempts
    save_partial_results=True,      # Save data on failure
    resume_from_stage=None,         # Resume from specific stage
    resume_from_checkpoint=None     # Resume from checkpoint file
)
```

## Basic Usage

```python
# Standard execution with automatic checkpointing
config = PipelineConfig(
    input_path=Path("input.md"),
    output_path=Path("output.pptx")
)
pipeline = Pipeline(config)
result = pipeline.run()
```

## Resume Operations

```python
# Resume from stage name
config.resume_from_stage = "transformation"
result = pipeline.run()

# Resume from checkpoint file
checkpoint_path = Path(".slideforge_checkpoints/checkpoint_validation_*.json")
result = pipeline.resume_from_checkpoint(checkpoint_path)

# Resume using run_from_stage()
result = pipeline.run_from_stage("validation")
```

## Exception Types

```python
from scripts.pipeline.orchestrator import (
    RecoverableError,      # Can be retried
    CriticalError,         # Stops pipeline
    ValidationError,       # Validation failures
    TransformationError,   # Transformation failures
    GenerationError,       # PPTX generation failures
    CheckpointError        # Checkpoint system errors
)
```

## Checkpoint Management

```python
# Initialize checkpoint manager
from scripts.pipeline.orchestrator import CheckpointManager

manager = CheckpointManager(Path(".slideforge_checkpoints"))

# Save checkpoint
checkpoint_path = manager.save_checkpoint(
    stage="validation",
    state=stage_data,
    stage_results=results,
    config=config_dict,
    stages_completed=["ingestion", "extraction"]
)

# Load checkpoint
checkpoint = manager.load_checkpoint("checkpoint_id")
latest = manager.get_latest_checkpoint()
stage_cp = manager.get_checkpoint_for_stage("transformation")

# Cleanup old checkpoints
manager.cleanup_checkpoints(keep_latest=3)
```

## Retry Decorator

```python
from scripts.pipeline.orchestrator import with_retry, RecoverableError

@with_retry(max_attempts=3, delay_seconds=1.0, backoff_multiplier=2.0)
def risky_operation():
    if transient_condition:
        raise RecoverableError("Temporary failure")
    return result
```

## Error Handling

```python
try:
    result = pipeline.run()
    
    if not result.success:
        print(f"Pipeline failed at: {result.last_successful_stage}")
        print(f"Partial results: {result.partial_results_path}")
        
        # Show structured errors
        for error in result.structured_errors:
            print(error.format_message())
            
    else:
        print(f"Success! Recovered from {result.recovered_from_errors} errors")
        print(f"Checkpoint: {result.checkpoint_path}")
        
except CriticalError as e:
    print(f"Critical error: {e}")
    print(f"Context: {e.context}")
```

## Result Fields

```python
result = pipeline.run()

result.success                  # bool: Overall success
result.output_path              # Path: Generated PPTX file
result.manifest_path            # Path: Pipeline manifest
result.errors                   # List[str]: Error messages
result.warnings                 # List[str]: Warning messages
result.stages_completed         # int: Number of stages completed
result.total_duration_ms        # float: Total execution time
result.partial_results_path     # Path: Partial results directory
result.last_successful_stage    # str: Last completed stage
result.checkpoint_path          # Path: Most recent checkpoint
result.structured_errors        # List[PipelineError]: Detailed errors
result.recovered_from_errors    # int: Number of recovered errors
```

## Directory Locations

```
Project Root/
├── .slideforge_checkpoints/         # Checkpoint storage
│   ├── checkpoints.json
│   └── checkpoint_*.json
├── partial_results_*/               # Failure diagnostics
│   ├── stage_data.json
│   ├── stage_results.json
│   └── recovery_info.json
└── output/
    ├── presentation.pptx
    └── presentation_manifest.json
```

## Pipeline Stages

1. **ingestion** (CRITICAL) - Load and detect input format
2. **extraction** - Parse semantic structure
3. **transformation** - Convert to presentation schema
4. **template_selection** - Choose optimal template (fallback: "minimal")
5. **validation** - Quality checks (can skip)
6. **generation** (CRITICAL) - Create PPTX file

## Graceful Degradation

Non-critical stages with fallbacks:
- **template_selection**: Uses "minimal" template on failure
- **validation**: Skips validation on failure (unless --strict)

Critical stages (must succeed):
- **ingestion**: Cannot continue without input
- **generation**: Cannot complete without PPTX output

## CLI Integration (Recommended)

```bash
# Resume from stage
python -m scripts.pipeline generate input.md output.pptx --resume-from transformation

# Resume from checkpoint
python -m scripts.pipeline generate input.md output.pptx --resume-checkpoint checkpoint_*.json

# Disable checkpoints
python -m scripts.pipeline generate input.md output.pptx --no-checkpoints

# Configure retries
python -m scripts.pipeline generate input.md output.pptx --max-retries 5 --no-retry
```

## Helper Methods (To Be Integrated)

Located in `error_recovery_helpers.py`:
- `_load_checkpoints_until()` - Load checkpoints before stage
- `_load_from_checkpoint()` - Load from checkpoint ID
- `_load_checkpoint_state()` - Restore state
- `_wrap_with_retry()` - Wrap function with retry
- `_handle_stage_failure()` - Graceful degradation
- `_get_failure_suggestions()` - Recovery suggestions
- `_save_partial_results()` - Save intermediate data

## Common Patterns

### Pattern 1: Resilient Execution
```python
config = PipelineConfig(
    input_path=Path("input.md"),
    output_path=Path("output.pptx"),
    enable_checkpoints=True,
    enable_retry=True,
    max_retry_attempts=5
)
```

### Pattern 2: Fast Execution (No Recovery)
```python
config = PipelineConfig(
    input_path=Path("input.md"),
    output_path=Path("output.pptx"),
    enable_checkpoints=False,
    enable_retry=False
)
```

### Pattern 3: Resume After Failure
```python
# Initial run
result1 = pipeline.run()  # Fails at transformation

# Fix issue, then resume
config.resume_from_stage = "transformation"
result2 = pipeline.run()  # Continues from transformation
```

### Pattern 4: Checkpoint-Based Recovery
```python
# Find latest checkpoint
manager = CheckpointManager(Path(".slideforge_checkpoints"))
checkpoint = manager.get_latest_checkpoint()

# Resume from checkpoint
result = pipeline.resume_from_checkpoint(
    Path(f".slideforge_checkpoints/{checkpoint.checkpoint_id}.json")
)
```

## Troubleshooting

### Checkpoint Not Found
- Check `.slideforge_checkpoints/` directory exists
- Verify checkpoint file permissions
- Check `checkpoints.json` index

### Retry Not Working
- Verify `enable_retry=True`
- Check exception type is `RecoverableError`
- Confirm stage is non-critical

### Partial Results Not Saved
- Verify `save_partial_results=True`
- Check output directory is writable
- Review logs for save errors
