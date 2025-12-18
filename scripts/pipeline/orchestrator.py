"""
Pipeline Orchestrator for Slideforge

Main orchestration module that coordinates the presentation
generation pipeline from input to final PPTX output.

Pipeline Stages:
1. Content Ingestion - Load and detect format
2. Semantic Extraction - Parse content structure
3. Content Transformation - Convert to presentation schema
4. Template Selection - Choose optimal template
5. Validation - Quality checks
6. PPTX Generation - Create final output
"""

import json
import time
import logging
import hashlib
import traceback
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List, Callable
from functools import wraps
from enum import Enum
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from .manifest import (
    PipelineManifest,
    ProcessingStep,
    QualityMetadata,
    ProvenanceEntry,
    ProvenanceInfo,
    ProcessingLog,
    PresentationProfile,
    extract_presentation_profile,
    create_manifest
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s - %(message)s'
)
logger = logging.getLogger('slideforge.pipeline')


# ============================================================================
# Error Classification System
# ============================================================================

class ErrorSeverity(Enum):
    """Error severity levels."""
    CRITICAL = "critical"  # Pipeline must stop
    HIGH = "high"          # Stage fails, pipeline may stop
    MEDIUM = "medium"      # Degraded operation, can continue
    LOW = "low"            # Warning only, no impact


class RecoverableError(Exception):
    """Errors that can be retried or worked around."""
    def __init__(self, message: str, severity: ErrorSeverity = ErrorSeverity.MEDIUM):
        super().__init__(message)
        self.severity = severity


class CriticalError(Exception):
    """Errors that stop the pipeline immediately."""
    def __init__(self, message: str, context: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.context = context or {}


class ValidationError(RecoverableError):
    """Validation failures."""
    pass


class TransformationError(RecoverableError):
    """Transformation failures."""
    pass


class GenerationError(CriticalError):
    """PPTX generation failures."""
    pass


class CheckpointError(Exception):
    """Checkpoint system errors."""
    pass


@dataclass
class PipelineError:
    """Structured error information for reporting."""
    stage: str
    error_type: str
    message: str
    context: Dict[str, Any] = field(default_factory=dict)
    recoverable: bool = True
    suggestions: List[str] = field(default_factory=list)
    traceback: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "stage": self.stage,
            "errorType": self.error_type,
            "message": self.message,
            "context": self.context,
            "recoverable": self.recoverable,
            "suggestions": self.suggestions,
            "traceback": self.traceback,
            "timestamp": self.timestamp
        }

    def format_message(self) -> str:
        """Format error for user display."""
        lines = [
            f"\n{'='*70}",
            f"ERROR in stage: {self.stage}",
            f"Type: {self.error_type}",
            f"{'='*70}",
            f"\n{self.message}\n"
        ]

        if self.context:
            lines.append("\nContext:")
            for key, value in self.context.items():
                lines.append(f"  {key}: {value}")

        if self.suggestions:
            lines.append("\nSuggestions:")
            for i, suggestion in enumerate(self.suggestions, 1):
                lines.append(f"  {i}. {suggestion}")

        lines.append(f"\nRecoverable: {'Yes' if self.recoverable else 'No'}")
        lines.append(f"{'='*70}\n")

        return "\n".join(lines)


# ============================================================================
# Checkpoint System
# ============================================================================

@dataclass
class PipelineCheckpoint:
    """Checkpoint data for pipeline state."""
    checkpoint_id: str
    stage: str
    timestamp: str
    state_snapshot: Dict[str, Any]
    stage_results: Dict[str, Dict[str, Any]]
    config_snapshot: Dict[str, Any]
    stages_completed: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "checkpointId": self.checkpoint_id,
            "stage": self.stage,
            "timestamp": self.timestamp,
            "stateSnapshot": self.state_snapshot,
            "stageResults": self.stage_results,
            "configSnapshot": self.config_snapshot,
            "stagesCompleted": self.stages_completed
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PipelineCheckpoint':
        """Create from dictionary."""
        return cls(
            checkpoint_id=data.get("checkpointId", ""),
            stage=data.get("stage", ""),
            timestamp=data.get("timestamp", ""),
            state_snapshot=data.get("stateSnapshot", {}),
            stage_results=data.get("stageResults", {}),
            config_snapshot=data.get("configSnapshot", {}),
            stages_completed=data.get("stagesCompleted", [])
        )


class CheckpointManager:
    """Manages pipeline checkpoints for recovery."""

    def __init__(self, checkpoint_dir: Path):
        """
        Initialize checkpoint manager.

        Args:
            checkpoint_dir: Directory to store checkpoints
        """
        self.checkpoint_dir = checkpoint_dir
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        self._checkpoint_file = self.checkpoint_dir / "checkpoints.json"
        self._checkpoints: Dict[str, PipelineCheckpoint] = {}
        self._load_checkpoints()

    def save_checkpoint(
        self,
        stage: str,
        state: Dict[str, Any],
        stage_results: Dict[str, Dict[str, Any]],
        config: Dict[str, Any],
        stages_completed: List[str]
    ) -> Path:
        """
        Save checkpoint after successful stage.

        Args:
            stage: Stage name
            state: Current pipeline state
            stage_results: Results from all stages
            config: Pipeline configuration
            stages_completed: List of completed stage names

        Returns:
            Path to checkpoint file
        """
        checkpoint_id = self._generate_checkpoint_id(stage)
        timestamp = datetime.now().isoformat()

        checkpoint = PipelineCheckpoint(
            checkpoint_id=checkpoint_id,
            stage=stage,
            timestamp=timestamp,
            state_snapshot=state.copy(),
            stage_results=stage_results.copy(),
            config_snapshot=config,
            stages_completed=stages_completed.copy()
        )

        # Save to memory
        self._checkpoints[checkpoint_id] = checkpoint

        # Save to disk
        self._persist_checkpoints()

        # Also save individual checkpoint file
        checkpoint_path = self.checkpoint_dir / f"{checkpoint_id}.json"
        with open(checkpoint_path, 'w', encoding='utf-8') as f:
            json.dump(checkpoint.to_dict(), f, indent=2)

        logger.info(f"Checkpoint saved: {checkpoint_id} (stage: {stage})")
        return checkpoint_path

    def load_checkpoint(self, checkpoint_id: str) -> Optional[PipelineCheckpoint]:
        """
        Load checkpoint by ID.

        Args:
            checkpoint_id: Checkpoint identifier

        Returns:
            PipelineCheckpoint or None if not found
        """
        if checkpoint_id in self._checkpoints:
            return self._checkpoints[checkpoint_id]

        # Try loading from disk
        checkpoint_path = self.checkpoint_dir / f"{checkpoint_id}.json"
        if checkpoint_path.exists():
            with open(checkpoint_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                checkpoint = PipelineCheckpoint.from_dict(data)
                self._checkpoints[checkpoint_id] = checkpoint
                return checkpoint

        return None

    def get_latest_checkpoint(self) -> Optional[PipelineCheckpoint]:
        """
        Get most recent checkpoint.

        Returns:
            Latest PipelineCheckpoint or None
        """
        if not self._checkpoints:
            return None

        latest = max(
            self._checkpoints.values(),
            key=lambda cp: cp.timestamp
        )
        return latest

    def get_checkpoint_for_stage(self, stage: str) -> Optional[PipelineCheckpoint]:
        """
        Get checkpoint for a specific stage.

        Args:
            stage: Stage name

        Returns:
            PipelineCheckpoint or None
        """
        for checkpoint in self._checkpoints.values():
            if checkpoint.stage == stage:
                return checkpoint
        return None

    def cleanup_checkpoints(self, keep_latest: int = 3) -> None:
        """
        Remove old checkpoints, keeping only recent ones.

        Args:
            keep_latest: Number of recent checkpoints to keep
        """
        if len(self._checkpoints) <= keep_latest:
            return

        # Sort by timestamp
        sorted_checkpoints = sorted(
            self._checkpoints.values(),
            key=lambda cp: cp.timestamp,
            reverse=True
        )

        # Remove old ones
        for checkpoint in sorted_checkpoints[keep_latest:]:
            checkpoint_path = self.checkpoint_dir / f"{checkpoint.checkpoint_id}.json"
            if checkpoint_path.exists():
                checkpoint_path.unlink()
            del self._checkpoints[checkpoint.checkpoint_id]

        self._persist_checkpoints()
        logger.info(f"Cleaned up old checkpoints, kept {keep_latest} most recent")

    def _generate_checkpoint_id(self, stage: str) -> str:
        """Generate unique checkpoint ID."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"checkpoint_{stage}_{timestamp}"

    def _load_checkpoints(self) -> None:
        """Load checkpoints from disk."""
        if not self._checkpoint_file.exists():
            return

        try:
            with open(self._checkpoint_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for checkpoint_data in data.get("checkpoints", []):
                    checkpoint = PipelineCheckpoint.from_dict(checkpoint_data)
                    self._checkpoints[checkpoint.checkpoint_id] = checkpoint
        except Exception as e:
            logger.warning(f"Failed to load checkpoints: {e}")

    def _persist_checkpoints(self) -> None:
        """Persist checkpoints to disk."""
        data = {
            "checkpoints": [cp.to_dict() for cp in self._checkpoints.values()],
            "lastUpdated": datetime.now().isoformat()
        }

        with open(self._checkpoint_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)


# ============================================================================
# Retry Logic
# ============================================================================

def with_retry(
    max_attempts: int = 3,
    delay_seconds: float = 1.0,
    backoff_multiplier: float = 2.0,
    retriable_exceptions: tuple = (RecoverableError, ConnectionError, TimeoutError)
):
    """
    Decorator for retrying failed operations.

    Args:
        max_attempts: Maximum retry attempts
        delay_seconds: Initial delay between retries
        backoff_multiplier: Delay multiplier for exponential backoff
        retriable_exceptions: Exception types to retry

    Usage:
        @with_retry(max_attempts=3, delay_seconds=1.0)
        def risky_operation():
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            delay = delay_seconds

            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except retriable_exceptions as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        logger.warning(
                            f"Attempt {attempt + 1}/{max_attempts} failed: {e}. "
                            f"Retrying in {delay:.1f}s..."
                        )
                        time.sleep(delay)
                        delay *= backoff_multiplier
                    else:
                        logger.error(f"All {max_attempts} attempts failed")
                        raise
                except Exception as e:
                    # Non-retriable exception
                    logger.error(f"Non-retriable exception: {e}")
                    raise

            # Should not reach here, but just in case
            if last_exception:
                raise last_exception

        return wrapper
    return decorator


@dataclass
class PipelineConfig:
    """Pipeline configuration."""
    input_path: Path
    output_path: Path
    theme: Optional[str] = None
    template: Optional[str] = None
    validate_only: bool = False
    verbose: bool = False
    checkpoint_dir: Optional[Path] = None
    fail_on_warnings: bool = False

    # Error recovery config
    enable_checkpoints: bool = True
    enable_retry: bool = True
    max_retry_attempts: int = 3
    save_partial_results: bool = True
    resume_from_stage: Optional[str] = None
    resume_from_checkpoint: Optional[str] = None

    # Stage-specific config
    max_bullets_per_slide: int = 6
    max_words_per_bullet: int = 12
    include_speaker_notes: bool = True
    min_quality_score: float = 70.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "inputPath": str(self.input_path),
            "outputPath": str(self.output_path),
            "theme": self.theme,
            "template": self.template,
            "validateOnly": self.validate_only,
            "verbose": self.verbose,
            "checkpointDir": str(self.checkpoint_dir) if self.checkpoint_dir else None,
            "enableCheckpoints": self.enable_checkpoints,
            "enableRetry": self.enable_retry,
            "maxRetryAttempts": self.max_retry_attempts,
            "savePartialResults": self.save_partial_results,
            "maxBulletsPerSlide": self.max_bullets_per_slide,
            "maxWordsPerBullet": self.max_words_per_bullet,
            "includeSpeakerNotes": self.include_speaker_notes,
            "minQualityScore": self.min_quality_score
        }


@dataclass
class StageResult:
    """Result from a pipeline stage."""
    stage_name: str
    success: bool
    data: Any = None
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    duration_ms: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PipelineResult:
    """Final result of pipeline execution."""
    success: bool
    output_path: Optional[Path] = None
    manifest_path: Optional[Path] = None
    manifest: Optional[PipelineManifest] = None
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    stages_completed: int = 0
    total_duration_ms: float = 0.0
    partial_results_path: Optional[Path] = None
    last_successful_stage: Optional[str] = None
    checkpoint_path: Optional[Path] = None
    structured_errors: List[PipelineError] = field(default_factory=list)
    recovered_from_errors: int = 0


class Pipeline:
    """
    Main orchestration pipeline for presentation generation.

    Coordinates all stages from input to PPTX output with
    validation and error recovery.
    """

    STAGES = [
        'ingestion',
        'extraction',
        'transformation',
        'template_selection',
        'validation',
        'generation'
    ]

    def __init__(self, config: PipelineConfig):
        """
        Initialize the pipeline.

        Args:
            config: Pipeline configuration
        """
        self.config = config

        # Initialize manifest with enhanced provenance tracking
        # Note: Full provenance will be set during ingestion stage
        self.manifest = PipelineManifest()
        self.manifest.pipeline_config = config.to_dict()
        self.manifest.initialize_processing_log()

        self._stage_data: Dict[str, Any] = {}
        self._stage_results: Dict[str, Dict[str, Any]] = {}
        self._stages_completed: List[str] = []
        self._pipeline_start_time = time.time()
        self._recovered_errors: int = 0

        # Initialize checkpoint manager
        if config.enable_checkpoints:
            checkpoint_dir = config.checkpoint_dir or (
                config.output_path.parent / ".slideforge_checkpoints"
            )
            self.checkpoint_manager = CheckpointManager(checkpoint_dir)
        else:
            self.checkpoint_manager = None

        # Critical stages that cannot be skipped
        self._critical_stages = ['ingestion', 'generation']

        if config.verbose:
            logging.getLogger('slideforge').setLevel(logging.DEBUG)

    def run(self) -> PipelineResult:
        """
        Execute the full pipeline with error recovery.

        Returns:
            PipelineResult with success status and output info
        """
        start_time = time.time()
        result = PipelineResult(success=True)

        # Check if resuming from checkpoint or stage
        start_stage_idx = 0
        if self.config.resume_from_checkpoint:
            start_stage_idx = self._load_from_checkpoint(self.config.resume_from_checkpoint)
        elif self.config.resume_from_stage:
            if self.config.resume_from_stage in self.STAGES:
                start_stage_idx = self.STAGES.index(self.config.resume_from_stage)
                logger.info(f"Resuming from stage: {self.config.resume_from_stage}")
            else:
                raise ValueError(f"Invalid stage: {self.config.resume_from_stage}")

        try:
            # Execute pipeline stages
            for idx, stage_name in enumerate(self.STAGES[start_stage_idx:], start=start_stage_idx):
                # Get stage function
                stage_func = getattr(self, f'_stage_{stage_name}')

                # Run stage with retry if enabled
                if self.config.enable_retry and stage_name not in self._critical_stages:
                    stage_func_wrapped = self._wrap_with_retry(stage_func)
                else:
                    stage_func_wrapped = stage_func

                stage_result = self._run_stage(stage_name, stage_func_wrapped)

                # Handle stage result
                if not stage_result.success:
                    # Check if failure can be handled gracefully
                    if self._handle_stage_failure(stage_name, stage_result, result):
                        # Continue with degraded operation
                        logger.warning(f"Continuing with fallback for stage: {stage_name}")
                        result.warnings.extend(stage_result.warnings)
                        result.warnings.append(f"Stage {stage_name} failed but continuing with defaults")
                    else:
                        # Critical failure - save partial results and exit
                        result.last_successful_stage = self._stages_completed[-1] if self._stages_completed else None
                        if self.config.save_partial_results:
                            result.partial_results_path = self._save_partial_results(stage_name)
                        return self._finalize_result(result, stage_result)

                # Stage succeeded - save checkpoint
                self._stages_completed.append(stage_name)
                result.stages_completed += 1
                result.last_successful_stage = stage_name

                if self.checkpoint_manager:
                    checkpoint_path = self.checkpoint_manager.save_checkpoint(
                        stage=stage_name,
                        state=self._stage_data,
                        stage_results=self._stage_results,
                        config=self.config.to_dict(),
                        stages_completed=self._stages_completed
                    )
                    result.checkpoint_path = checkpoint_path

                # Handle validate_only mode
                if self.config.validate_only and stage_name == 'validation':
                    logger.info("Validation only mode - skipping generation")
                    break

                # Store output path for generation stage
                if stage_name == 'generation' and stage_result.data:
                    result.output_path = Path(stage_result.data.get('output_path', ''))

            result.success = True
            result.recovered_from_errors = self._recovered_errors

        except CriticalError as e:
            logger.error(f"Critical error: {e}")
            result.success = False
            pipeline_error = PipelineError(
                stage=result.last_successful_stage or "unknown",
                error_type="CriticalError",
                message=str(e),
                context=e.context,
                recoverable=False,
                traceback=traceback.format_exc()
            )
            result.structured_errors.append(pipeline_error)
            result.errors.append(pipeline_error.format_message())

            if self.config.save_partial_results:
                result.partial_results_path = self._save_partial_results("critical_error")

        except Exception as e:
            logger.exception(f"Pipeline failed: {e}")
            result.success = False
            pipeline_error = PipelineError(
                stage=result.last_successful_stage or "unknown",
                error_type=type(e).__name__,
                message=str(e),
                recoverable=False,
                traceback=traceback.format_exc()
            )
            result.structured_errors.append(pipeline_error)
            result.errors.append(pipeline_error.format_message())

            if self.config.save_partial_results:
                result.partial_results_path = self._save_partial_results("exception")

        # Finalize
        result.total_duration_ms = (time.time() - start_time) * 1000
        result.manifest = self.manifest

        # Finalize processing log with total duration
        self.manifest.finalize_processing_log(result.total_duration_ms / 1000)

        # Save manifest
        manifest_path = self._get_manifest_path()
        self.manifest.save(manifest_path)
        result.manifest_path = manifest_path

        # Cleanup old checkpoints
        if self.checkpoint_manager and result.success:
            self.checkpoint_manager.cleanup_checkpoints()

        logger.info(f"Pipeline completed. Manifest saved to: {manifest_path}")
        if result.recovered_from_errors > 0:
            logger.info(f"Recovered from {result.recovered_from_errors} errors during execution")

        return result

    def run_from_stage(self, stage_name: str) -> PipelineResult:
        """
        Resume pipeline from a specific stage.

        Args:
            stage_name: Name of stage to resume from

        Returns:
            PipelineResult
        """
        if stage_name not in self.STAGES:
            raise ValueError(f"Unknown stage: {stage_name}")

        # Update config to resume from this stage
        self.config.resume_from_stage = stage_name

        # Load checkpoint data for previous stages
        if self.checkpoint_manager:
            checkpoint = self.checkpoint_manager.get_checkpoint_for_stage(stage_name)
            if checkpoint:
                self._load_checkpoint_state(checkpoint)
            else:
                logger.warning(f"No checkpoint found for stage {stage_name}, starting fresh")

        return self.run()

    def resume_from_checkpoint(self, checkpoint_path: Path) -> PipelineResult:
        """
        Resume pipeline from a specific checkpoint file.

        Args:
            checkpoint_path: Path to checkpoint file

        Returns:
            PipelineResult
        """
        with open(checkpoint_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            checkpoint = PipelineCheckpoint.from_dict(data)

        self._load_checkpoint_state(checkpoint)

        # Resume from next stage after checkpoint
        stage_idx = self.STAGES.index(checkpoint.stage)
        if stage_idx < len(self.STAGES) - 1:
            next_stage = self.STAGES[stage_idx + 1]
            self.config.resume_from_stage = next_stage
            logger.info(f"Resuming from checkpoint, starting at stage: {next_stage}")
        else:
            logger.info("Checkpoint is at final stage, re-running final stage")
            self.config.resume_from_stage = checkpoint.stage

        return self.run()

    def _run_stage(
        self,
        stage_name: str,
        stage_func: Callable[[], StageResult]
    ) -> StageResult:
        """Run a single pipeline stage with error tracking."""
        logger.info(f"Starting stage: {stage_name}")
        start_time = time.time()

        try:
            result = stage_func()
            result.duration_ms = (time.time() - start_time) * 1000

            # Store stage result
            self._stage_results[stage_name] = {
                'success': result.success,
                'data': result.data,
                'errors': result.errors,
                'warnings': result.warnings,
                'duration_ms': result.duration_ms,
                'metadata': result.metadata
            }

            # Record in manifest
            self.manifest.record_step(
                stage=stage_name,
                input_data=self._stage_data.get(f'{stage_name}_input'),
                output_data=result.data,
                duration_ms=result.duration_ms,
                success=result.success,
                errors=result.errors,
                warnings=result.warnings,
                metadata=result.metadata
            )

            # Update processing log
            self.manifest.update_processing_log(
                stage_name=stage_name,
                warnings=len(result.warnings),
                errors=len(result.errors)
            )

            if result.success:
                logger.info(f"Stage {stage_name} completed in {result.duration_ms:.1f}ms")
            else:
                logger.error(f"Stage {stage_name} failed: {result.errors}")

            return result

        except Exception as e:
            logger.exception(f"Stage {stage_name} raised exception")
            error_result = StageResult(
                stage_name=stage_name,
                success=False,
                errors=[str(e)],
                duration_ms=(time.time() - start_time) * 1000
            )

            # Store failed stage result
            self._stage_results[stage_name] = {
                'success': False,
                'data': None,
                'errors': [str(e)],
                'warnings': [],
                'duration_ms': error_result.duration_ms,
                'metadata': {'exception_type': type(e).__name__}
            }

            return error_result

    def _stage_ingestion(self) -> StageResult:
        """Stage 1: Load and analyze input content with enhanced provenance tracking."""
        input_path = self.config.input_path

        if not input_path.exists():
            return StageResult(
                stage_name='ingestion',
                success=False,
                errors=[f"Input file not found: {input_path}"]
            )

        # Read content
        content = input_path.read_text(encoding='utf-8')
        file_size = input_path.stat().st_size

        # Detect format
        from semantic_structure_extractor import detect_format
        detected_format = detect_format(content)

        # Compute input hash for provenance
        input_hash = PipelineManifest.compute_file_hash(str(input_path))

        # Create comprehensive provenance info
        self.manifest.create_provenance_info(
            source_path=str(input_path),
            source_format=detected_format,
            pipeline_version=self.manifest.version,
            input_hash=input_hash,
            source_type="document"  # Could be made configurable
        )

        logger.info(f"Source provenance: {detected_format} file, hash: {input_hash[:16]}...")

        # Store for next stage
        self._stage_data['ingestion_input'] = str(input_path)
        self._stage_data['raw_content'] = content
        self._stage_data['input_format'] = detected_format

        return StageResult(
            stage_name='ingestion',
            success=True,
            data={
                'path': str(input_path),
                'format': detected_format,
                'size': file_size,
                'hash': input_hash
            },
            metadata={
                'format': detected_format,
                'size_bytes': file_size,
                'input_hash': input_hash
            }
        )

    def _stage_extraction(self) -> StageResult:
        """Stage 2: Extract semantic structure."""
        from semantic_structure_extractor import SemanticStructureExtractor

        content = self._stage_data.get('raw_content', '')
        input_format = self._stage_data.get('input_format', 'auto')

        extractor = SemanticStructureExtractor()
        self._stage_data['extraction_input'] = content[:1000]  # Sample for hash

        try:
            # Use profiled extraction for full analysis
            structure = extractor.extract_with_profiling(
                content,
                str(self.config.input_path),
                input_format
            )

            self._stage_data['semantic_structure'] = structure

            chapter_count = len(structure.get('chapters', []))
            concept_count = len(structure.get('conceptGraph', {}).get('nodes', {}))

            return StageResult(
                stage_name='extraction',
                success=True,
                data=structure,
                metadata={
                    'chapters': chapter_count,
                    'concepts': concept_count
                }
            )

        except Exception as e:
            return StageResult(
                stage_name='extraction',
                success=False,
                errors=[f"Extraction failed: {e}"]
            )

    def _stage_transformation(self) -> StageResult:
        """Stage 3: Transform to presentation schema."""
        from semantic_structure_extractor import PresentationTransformer

        structure = self._stage_data.get('semantic_structure', {})
        concept_graph = structure.get('conceptGraph', {})

        self._stage_data['transformation_input'] = {
            'chapters': len(structure.get('chapters', []))
        }

        try:
            transformer = PresentationTransformer()
            presentation = transformer.transform(structure, concept_graph)

            self._stage_data['presentation'] = presentation

            slide_count = sum(
                len(section.get('slides', []))
                for section in presentation.get('sections', [])
            )

            # Update processing log with slide count
            self.manifest.update_processing_log(slides_created=slide_count)

            # Generate presentation profile (LibV2 pattern)
            try:
                profile = extract_presentation_profile(presentation)
                self.manifest.set_presentation_profile(profile)
                logger.info(f"Content profile: {slide_count} slides, "
                           f"{profile.total_words} words, "
                           f"{profile.six_by_six_compliance*100:.1f}% 6x6 compliance, "
                           f"{profile.speaker_notes_coverage*100:.1f}% notes coverage")
            except Exception as e:
                logger.warning(f"Failed to generate presentation profile: {e}")

            logger.info(f"Transformed content into {slide_count} slides across {len(presentation.get('sections', []))} sections")

            return StageResult(
                stage_name='transformation',
                success=True,
                data=presentation,
                metadata={
                    'sections': len(presentation.get('sections', [])),
                    'slides': slide_count
                }
            )

        except Exception as e:
            return StageResult(
                stage_name='transformation',
                success=False,
                errors=[f"Transformation failed: {e}"]
            )

    def _stage_template_selection(self) -> StageResult:
        """Stage 4: Select optimal template."""
        from pptx_generator.template_selector import TemplateSelector

        presentation = self._stage_data.get('presentation', {})
        self._stage_data['template_selection_input'] = 'presentation'

        try:
            # Use specified template or auto-select
            if self.config.template:
                selected_template = self.config.template
                reasons = ["User-specified template"]
            else:
                selector = TemplateSelector()
                recommendations = selector.recommend_templates(presentation)

                if recommendations:
                    selected_template = recommendations[0].template_id
                    reasons = recommendations[0].reasons
                else:
                    selected_template = "minimal"
                    reasons = ["Default fallback"]

            self._stage_data['selected_template'] = selected_template
            self.manifest.template_used = selected_template

            return StageResult(
                stage_name='template_selection',
                success=True,
                data={
                    'template': selected_template,
                    'reasons': reasons
                },
                metadata={
                    'template': selected_template
                }
            )

        except Exception as e:
            # Fall back to default template
            self._stage_data['selected_template'] = "minimal"
            self.manifest.template_used = "minimal"

            return StageResult(
                stage_name='template_selection',
                success=True,
                data={'template': 'minimal'},
                warnings=[f"Template selection failed, using default: {e}"]
            )

    def _stage_validation(self) -> StageResult:
        """Stage 5: Validate presentation quality."""
        presentation = self._stage_data.get('presentation', {})
        self._stage_data['validation_input'] = 'presentation'

        warnings = []
        issues = []

        # Calculate quality metrics
        total_slides = 0
        slides_with_notes = 0
        slide_types = set()
        six_six_violations = 0

        for section in presentation.get('sections', []):
            for slide in section.get('slides', []):
                total_slides += 1
                slide_types.add(slide.get('type', 'content'))

                if slide.get('notes'):
                    slides_with_notes += 1

                # Check 6x6 rule
                content = slide.get('content', {})
                bullets = content.get('bullets', [])
                if len(bullets) > 6:
                    six_six_violations += 1
                    issues.append({
                        'type': 'six_six_violation',
                        'slide': slide.get('title', 'Unknown'),
                        'bullet_count': len(bullets)
                    })

        notes_coverage = slides_with_notes / total_slides if total_slides > 0 else 0

        # Calculate score
        score = 100.0
        score -= six_six_violations * 5
        score -= max(0, (0.8 - notes_coverage) * 20)
        score -= max(0, (3 - len(slide_types)) * 10)
        score = max(0, min(100, score))

        quality = QualityMetadata(
            six_six_violations=six_six_violations,
            notes_coverage=notes_coverage,
            slide_type_variety=len(slide_types),
            validation_score=score,
            total_slides=total_slides,
            total_sections=len(presentation.get('sections', [])),
            issues=issues
        )

        self.manifest.set_quality(quality)

        if six_six_violations > 0:
            warnings.append(f"Found {six_six_violations} slides violating 6x6 rule")
        if notes_coverage < 0.8:
            warnings.append(f"Speaker notes coverage is {notes_coverage*100:.1f}% (target: 80%)")
        if len(slide_types) < 3:
            warnings.append(f"Limited slide type variety: {len(slide_types)} types used")

        success = score >= self.config.min_quality_score

        return StageResult(
            stage_name='validation',
            success=success,
            data=quality.to_dict(),
            warnings=warnings,
            metadata={
                'score': score,
                'total_slides': total_slides
            }
        )

    def _stage_generation(self) -> StageResult:
        """Stage 6: Generate PPTX file."""
        presentation = self._stage_data.get('presentation', {})
        template = self._stage_data.get('selected_template', 'minimal')

        self._stage_data['generation_input'] = {
            'sections': len(presentation.get('sections', []))
        }

        try:
            from pptx_generator import PPTXGenerator

            # Prepare output path
            output_path = self.config.output_path
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Generate PPTX
            generator = PPTXGenerator(template_name=template)
            generator.create_from_structure(presentation)
            generator.save(str(output_path))

            # Update manifest
            self.manifest.set_output_info(
                path=str(output_path),
                format='pptx',
                size=output_path.stat().st_size if output_path.exists() else 0
            )

            return StageResult(
                stage_name='generation',
                success=True,
                data={
                    'output_path': str(output_path)
                },
                metadata={
                    'template': template,
                    'file_size': output_path.stat().st_size if output_path.exists() else 0
                }
            )

        except Exception as e:
            return StageResult(
                stage_name='generation',
                success=False,
                errors=[f"PPTX generation failed: {e}"]
            )

    def _finalize_result(
        self,
        result: PipelineResult,
        failed_stage: StageResult
    ) -> PipelineResult:
        """Finalize result after a failed stage."""
        result.success = False
        result.errors.extend(failed_stage.errors)
        result.warnings.extend(failed_stage.warnings)
        return result

    def _get_manifest_path(self) -> Path:
        """Get path for manifest file."""
        output_path = self.config.output_path
        return output_path.parent / f"{output_path.stem}_manifest.json"

    def _load_checkpoints_until(self, stage_name: str) -> None:
        """Load checkpoint data for stages before the specified stage."""
        if not self.config.checkpoint_dir:
            return

        stage_idx = self.STAGES.index(stage_name)

        for stage in self.STAGES[:stage_idx]:
            checkpoint_path = self.config.checkpoint_dir / f"checkpoint_{stage}.json"
            if checkpoint_path.exists():
                with open(checkpoint_path, 'r') as f:
                    data = json.load(f)
                    self._stage_data.update(data.get('stage_data', {}))


def run_pipeline(
    input_path: str,
    output_path: str,
    template: Optional[str] = None,
    verbose: bool = False
) -> PipelineResult:
    """
    Convenience function to run the pipeline.

    Args:
        input_path: Path to input file (Markdown or HTML)
        output_path: Path for output PPTX file
        template: Optional template name
        verbose: Enable verbose logging

    Returns:
        PipelineResult with success status and output info
    """
    config = PipelineConfig(
        input_path=Path(input_path),
        output_path=Path(output_path),
        template=template,
        verbose=verbose
    )

    pipeline = Pipeline(config)
    return pipeline.run()
