"""
Pipeline Manifest for Slideforge

Tracks processing history, provenance, and quality metrics
throughout the presentation generation pipeline.

This module provides comprehensive provenance tracking based on LibV2 patterns,
including:
- Source file lineage and transformation history
- Pipeline stage execution details
- Agent invocation tracking
- Quality metrics and validation results
- Complete audit trail from input to output

Key Classes:
    ProvenanceInfo: Source file provenance and lineage tracking
    ProcessingLog: Aggregate statistics for pipeline execution
    ProcessingStep: Individual stage execution records
    ProvenanceEntry: Granular transformation tracking
    QualityMetadata: Quality metrics and validation results
    PipelineManifest: Main manifest container

Usage:
    # Create new manifest at pipeline start
    manifest = create_manifest(
        source_path="/path/to/input.md",
        source_format="markdown",
        pipeline_version="1.0.0"
    )

    # Update during pipeline execution
    manifest.update_processing_log(
        stage_name="extraction",
        slides_created=15,
        warnings=2
    )

    # Track agent work
    manifest.add_agent_log(
        agent_name="slide-content-generator",
        task="Generate introduction slides",
        result={"target_ids": ["slide_001", "slide_002"]}
    )

    # Finalize and save
    manifest.finalize_processing_log(duration_seconds=42.5)
    manifest.save(Path("output/manifest.json"))
"""

import json
import uuid
import hashlib
import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path


@dataclass
class ProvenanceEntry:
    """Tracks source-to-output lineage."""
    source_id: str
    source_type: str  # chapter, section, block
    source_path: str  # JSONPath-like reference
    target_ids: List[str]
    transformation: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "sourceId": self.source_id,
            "sourceType": self.source_type,
            "sourcePath": self.source_path,
            "targetIds": self.target_ids,
            "transformation": self.transformation,
            "timestamp": self.timestamp
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProvenanceEntry':
        """Create from dictionary."""
        return cls(
            source_id=data.get("sourceId", ""),
            source_type=data.get("sourceType", ""),
            source_path=data.get("sourcePath", ""),
            target_ids=data.get("targetIds", []),
            transformation=data.get("transformation", ""),
            timestamp=data.get("timestamp", datetime.now().isoformat())
        )


@dataclass
class ProcessingStep:
    """Single processing step record."""
    stage: str
    timestamp: str
    duration_ms: float
    input_hash: str
    output_hash: str
    success: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "stage": self.stage,
            "timestamp": self.timestamp,
            "durationMs": self.duration_ms,
            "inputHash": self.input_hash,
            "outputHash": self.output_hash,
            "success": self.success,
            "errors": self.errors,
            "warnings": self.warnings,
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProcessingStep':
        """Create from dictionary."""
        return cls(
            stage=data.get("stage", ""),
            timestamp=data.get("timestamp", ""),
            duration_ms=data.get("durationMs", 0.0),
            input_hash=data.get("inputHash", ""),
            output_hash=data.get("outputHash", ""),
            success=data.get("success", False),
            errors=data.get("errors", []),
            warnings=data.get("warnings", []),
            metadata=data.get("metadata", {})
        )


@dataclass
class QualityMetadata:
    """Quality tracking metrics."""
    six_six_violations: int = 0
    notes_coverage: float = 0.0
    slide_type_variety: int = 0
    validation_score: float = 0.0
    total_slides: int = 0
    total_sections: int = 0
    issues: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "sixSixViolations": self.six_six_violations,
            "notesCoverage": round(self.notes_coverage, 3),
            "slideTypeVariety": self.slide_type_variety,
            "validationScore": round(self.validation_score, 2),
            "totalSlides": self.total_slides,
            "totalSections": self.total_sections,
            "issues": self.issues
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'QualityMetadata':
        """Create from dictionary."""
        return cls(
            six_six_violations=data.get("sixSixViolations", 0),
            notes_coverage=data.get("notesCoverage", 0.0),
            slide_type_variety=data.get("slideTypeVariety", 0),
            validation_score=data.get("validationScore", 0.0),
            total_slides=data.get("totalSlides", 0),
            total_sections=data.get("totalSections", 0),
            issues=data.get("issues", [])
        )


@dataclass
class PresentationProfile:
    """
    Profile of a generated presentation based on LibV2 content profiling patterns.

    Provides comprehensive analytics about presentation structure, content quality,
    and compliance with design guidelines.
    """
    # Slide Statistics
    total_slides: int = 0
    total_sections: int = 0
    total_words: int = 0
    total_characters: int = 0

    # Slide Type Distribution
    slide_type_distribution: Dict[str, int] = field(default_factory=dict)

    # Section Analysis
    section_sizes: Dict[str, int] = field(default_factory=dict)  # section_name -> slide_count

    # Content Quality Metrics
    speaker_notes_coverage: float = 0.0  # 0.0 to 1.0
    average_bullets_per_slide: float = 0.0
    average_words_per_bullet: float = 0.0
    six_by_six_compliance: float = 0.0  # Percentage of slides compliant (0.0 to 1.0)

    # Content Complexity
    vocabulary_richness: float = 0.0  # Type-token ratio
    average_sentence_length: float = 0.0

    # Visual Elements
    images_count: int = 0
    tables_count: int = 0
    charts_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "totalSlides": self.total_slides,
            "totalSections": self.total_sections,
            "totalWords": self.total_words,
            "totalCharacters": self.total_characters,
            "slideTypeDistribution": self.slide_type_distribution,
            "sectionSizes": self.section_sizes,
            "speakerNotesCoverage": round(self.speaker_notes_coverage, 3),
            "averageBulletsPerSlide": round(self.average_bullets_per_slide, 2),
            "averageWordsPerBullet": round(self.average_words_per_bullet, 2),
            "sixBySixCompliance": round(self.six_by_six_compliance, 3),
            "vocabularyRichness": round(self.vocabulary_richness, 3),
            "averageSentenceLength": round(self.average_sentence_length, 2),
            "imagesCount": self.images_count,
            "tablesCount": self.tables_count,
            "chartsCount": self.charts_count
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PresentationProfile':
        """Create from dictionary."""
        return cls(
            total_slides=data.get("totalSlides", 0),
            total_sections=data.get("totalSections", 0),
            total_words=data.get("totalWords", 0),
            total_characters=data.get("totalCharacters", 0),
            slide_type_distribution=data.get("slideTypeDistribution", {}),
            section_sizes=data.get("sectionSizes", {}),
            speaker_notes_coverage=data.get("speakerNotesCoverage", 0.0),
            average_bullets_per_slide=data.get("averageBulletsPerSlide", 0.0),
            average_words_per_bullet=data.get("averageWordsPerBullet", 0.0),
            six_by_six_compliance=data.get("sixBySixCompliance", 0.0),
            vocabulary_richness=data.get("vocabularyRichness", 0.0),
            average_sentence_length=data.get("averageSentenceLength", 0.0),
            images_count=data.get("imagesCount", 0),
            tables_count=data.get("tablesCount", 0),
            charts_count=data.get("chartsCount", 0)
        )


@dataclass
class ProvenanceInfo:
    """
    Comprehensive provenance tracking for input sources.
    Based on LibV2 patterns for source lineage tracking.
    """
    source_path: str
    source_format: str  # "markdown", "json", "text", "html"
    pipeline_version: str
    processing_timestamp: str  # ISO format
    input_hash: Optional[str] = None  # SHA256 of input content
    original_filename: Optional[str] = None
    file_size_bytes: int = 0

    # Extended provenance (LibV2-inspired)
    source_type: Optional[str] = None  # "document", "outline", "notes"
    original_provider: Optional[str] = None  # Content author/organization
    parent_version: Optional[str] = None  # If derived from another presentation

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "sourcePath": self.source_path,
            "sourceFormat": self.source_format,
            "pipelineVersion": self.pipeline_version,
            "processingTimestamp": self.processing_timestamp,
            "inputHash": self.input_hash,
            "originalFilename": self.original_filename,
            "fileSizeBytes": self.file_size_bytes,
            "sourceType": self.source_type,
            "originalProvider": self.original_provider,
            "parentVersion": self.parent_version
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProvenanceInfo':
        """Create from dictionary."""
        return cls(
            source_path=data.get("sourcePath", ""),
            source_format=data.get("sourceFormat", ""),
            pipeline_version=data.get("pipelineVersion", ""),
            processing_timestamp=data.get("processingTimestamp", ""),
            input_hash=data.get("inputHash"),
            original_filename=data.get("originalFilename"),
            file_size_bytes=data.get("fileSizeBytes", 0),
            source_type=data.get("sourceType"),
            original_provider=data.get("originalProvider"),
            parent_version=data.get("parentVersion")
        )


@dataclass
class ProcessingLog:
    """
    Aggregate processing statistics for the pipeline run.
    Provides high-level summary of pipeline execution.
    """
    stages_completed: List[str] = field(default_factory=list)
    agents_used: List[str] = field(default_factory=list)
    slides_created: int = 0
    warnings_generated: int = 0
    errors_generated: int = 0
    duration_seconds: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "stagesCompleted": self.stages_completed,
            "agentsUsed": self.agents_used,
            "slidesCreated": self.slides_created,
            "warningsGenerated": self.warnings_generated,
            "errorsGenerated": self.errors_generated,
            "durationSeconds": round(self.duration_seconds, 2)
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProcessingLog':
        """Create from dictionary."""
        return cls(
            stages_completed=data.get("stagesCompleted", []),
            agents_used=data.get("agentsUsed", []),
            slides_created=data.get("slidesCreated", 0),
            warnings_generated=data.get("warningsGenerated", 0),
            errors_generated=data.get("errorsGenerated", 0),
            duration_seconds=data.get("durationSeconds", 0.0)
        )


@dataclass
class PipelineManifest:
    """Rich manifest for tracking processing history."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    version: str = "1.0.0"
    created: str = field(default_factory=lambda: datetime.now().isoformat())
    updated: str = field(default_factory=lambda: datetime.now().isoformat())

    # Enhanced provenance tracking
    provenance_info: Optional[ProvenanceInfo] = None
    processing_log: Optional[ProcessingLog] = None

    # Content profiling (LibV2 pattern)
    presentation_profile: Optional[PresentationProfile] = None

    # Legacy fields (maintained for backward compatibility)
    source_info: Dict[str, Any] = field(default_factory=dict)
    processing_steps: List[ProcessingStep] = field(default_factory=list)
    provenance: List[ProvenanceEntry] = field(default_factory=list)
    quality: Optional[QualityMetadata] = None
    output_info: Dict[str, Any] = field(default_factory=dict)

    template_used: str = ""
    pipeline_config: Dict[str, Any] = field(default_factory=dict)

    def record_step(
        self,
        stage: str,
        input_data: Any,
        output_data: Any,
        duration_ms: float,
        success: bool = True,
        errors: Optional[List[str]] = None,
        warnings: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Record a processing step."""
        step = ProcessingStep(
            stage=stage,
            timestamp=datetime.now().isoformat(),
            duration_ms=duration_ms,
            input_hash=self._compute_hash(input_data),
            output_hash=self._compute_hash(output_data),
            success=success,
            errors=errors or [],
            warnings=warnings or [],
            metadata=metadata or {}
        )
        self.processing_steps.append(step)
        self.updated = datetime.now().isoformat()

    def add_provenance(self, entry: ProvenanceEntry) -> None:
        """Add provenance tracking entry."""
        self.provenance.append(entry)

    def create_provenance_info(
        self,
        source_path: str,
        source_format: str,
        pipeline_version: str,
        input_hash: Optional[str] = None,
        source_type: Optional[str] = None,
        original_provider: Optional[str] = None,
        parent_version: Optional[str] = None
    ) -> ProvenanceInfo:
        """
        Create and set comprehensive provenance information.

        Args:
            source_path: Full path to source file
            source_format: Format of source ("markdown", "json", "text", "html")
            pipeline_version: Version of Slideforge pipeline
            input_hash: SHA256 hash of input content
            source_type: Type of source content ("document", "outline", "notes")
            original_provider: Content author or organization
            parent_version: If derived from another presentation

        Returns:
            ProvenanceInfo instance
        """
        from pathlib import Path

        source_file = Path(source_path)
        file_size = source_file.stat().st_size if source_file.exists() else 0

        self.provenance_info = ProvenanceInfo(
            source_path=str(source_path),
            source_format=source_format,
            pipeline_version=pipeline_version,
            processing_timestamp=datetime.now().isoformat(),
            input_hash=input_hash,
            original_filename=source_file.name,
            file_size_bytes=file_size,
            source_type=source_type,
            original_provider=original_provider,
            parent_version=parent_version
        )

        # Also update legacy source_info for backward compatibility
        self.set_source_info(
            path=str(source_path),
            format=source_format,
            size=file_size,
            content_hash=input_hash or ""
        )

        return self.provenance_info

    def set_source_info(
        self,
        path: str,
        format: str,
        size: int = 0,
        content_hash: str = ""
    ) -> None:
        """Set source file information (legacy method)."""
        self.source_info = {
            "path": path,
            "format": format,
            "size": size,
            "hash": content_hash,
            "timestamp": datetime.now().isoformat()
        }

    def set_output_info(
        self,
        path: str,
        format: str = "pptx",
        size: int = 0
    ) -> None:
        """Set output file information."""
        self.output_info = {
            "path": path,
            "format": format,
            "size": size,
            "timestamp": datetime.now().isoformat()
        }

    def set_quality(self, quality: QualityMetadata) -> None:
        """Set quality metadata."""
        self.quality = quality

    def set_presentation_profile(self, profile: PresentationProfile) -> None:
        """Set presentation profile."""
        self.presentation_profile = profile

    def initialize_processing_log(self) -> ProcessingLog:
        """
        Initialize processing log at pipeline start.

        Returns:
            ProcessingLog instance
        """
        self.processing_log = ProcessingLog()
        return self.processing_log

    def update_processing_log(
        self,
        stage_name: Optional[str] = None,
        agent_name: Optional[str] = None,
        slides_created: int = 0,
        warnings: int = 0,
        errors: int = 0
    ) -> None:
        """
        Update processing log during pipeline execution.

        Args:
            stage_name: Name of completed stage
            agent_name: Name of agent used
            slides_created: Number of slides created
            warnings: Number of warnings generated
            errors: Number of errors generated
        """
        if not self.processing_log:
            self.initialize_processing_log()

        if stage_name and stage_name not in self.processing_log.stages_completed:
            self.processing_log.stages_completed.append(stage_name)

        if agent_name and agent_name not in self.processing_log.agents_used:
            self.processing_log.agents_used.append(agent_name)

        self.processing_log.slides_created += slides_created
        self.processing_log.warnings_generated += warnings
        self.processing_log.errors_generated += errors

        self.updated = datetime.now().isoformat()

    def finalize_processing_log(self, duration_seconds: float) -> None:
        """
        Finalize processing log with total duration.

        Args:
            duration_seconds: Total pipeline execution time in seconds
        """
        if not self.processing_log:
            self.initialize_processing_log()

        self.processing_log.duration_seconds = duration_seconds
        self.updated = datetime.now().isoformat()

    def add_agent_log(self, agent_name: str, task: str, result: Dict[str, Any]) -> None:
        """
        Track agent invocation for processing log.

        Args:
            agent_name: Name of the agent
            task: Description of the task
            result: Result data from agent execution
        """
        self.update_processing_log(agent_name=agent_name)

        # Add detailed provenance entry for agent work
        entry = ProvenanceEntry(
            source_id=f"agent_{agent_name}",
            source_type="agent_task",
            source_path=task,
            target_ids=result.get("target_ids", []),
            transformation=f"Agent: {agent_name}",
            timestamp=datetime.now().isoformat()
        )
        self.add_provenance(entry)

    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the manifest with enhanced provenance."""
        summary = {
            "id": self.id,
            "created": self.created,
            "source": self.source_info.get("path", ""),
            "output": self.output_info.get("path", ""),
            "template": self.template_used,
            "stages_completed": len(self.processing_steps),
            "success": all(s.success for s in self.processing_steps),
            "quality_score": self.quality.validation_score if self.quality else None,
            "total_slides": self.quality.total_slides if self.quality else 0
        }

        # Add enhanced provenance info if available
        if self.provenance_info:
            summary["provenance"] = {
                "source_format": self.provenance_info.source_format,
                "pipeline_version": self.provenance_info.pipeline_version,
                "input_hash": self.provenance_info.input_hash
            }

        # Add processing log summary if available
        if self.processing_log:
            summary["processing"] = {
                "agents_used": len(self.processing_log.agents_used),
                "slides_created": self.processing_log.slides_created,
                "duration_seconds": self.processing_log.duration_seconds,
                "warnings": self.processing_log.warnings_generated,
                "errors": self.processing_log.errors_generated
            }

        return summary

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with enhanced provenance tracking."""
        result = {
            "id": self.id,
            "version": self.version,
            "created": self.created,
            "updated": self.updated,
            "sourceInfo": self.source_info,
            "processingSteps": [s.to_dict() for s in self.processing_steps],
            "provenance": [p.to_dict() for p in self.provenance],
            "quality": self.quality.to_dict() if self.quality else None,
            "outputInfo": self.output_info,
            "templateUsed": self.template_used,
            "pipelineConfig": self.pipeline_config
        }

        # Add enhanced provenance fields
        if self.provenance_info:
            result["provenanceInfo"] = self.provenance_info.to_dict()

        if self.processing_log:
            result["processingLog"] = self.processing_log.to_dict()

        # Add presentation profile
        if self.presentation_profile:
            result["presentationProfile"] = self.presentation_profile.to_dict()

        return result

    def to_json(self, indent: int = 2) -> str:
        """Export manifest as JSON string."""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)

    def save(self, path: Path) -> None:
        """Save manifest to file."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(self.to_json())

    @classmethod
    def load(cls, path: Path) -> 'PipelineManifest':
        """Load manifest from file."""
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return cls.from_dict(data)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PipelineManifest':
        """Create from dictionary with enhanced provenance support."""
        manifest = cls(
            id=data.get("id", str(uuid.uuid4())),
            version=data.get("version", "1.0.0"),
            created=data.get("created", datetime.now().isoformat()),
            updated=data.get("updated", datetime.now().isoformat())
        )
        manifest.source_info = data.get("sourceInfo", {})
        manifest.processing_steps = [
            ProcessingStep.from_dict(s) for s in data.get("processingSteps", [])
        ]
        manifest.provenance = [
            ProvenanceEntry.from_dict(p) for p in data.get("provenance", [])
        ]
        if data.get("quality"):
            manifest.quality = QualityMetadata.from_dict(data["quality"])
        manifest.output_info = data.get("outputInfo", {})
        manifest.template_used = data.get("templateUsed", "")
        manifest.pipeline_config = data.get("pipelineConfig", {})

        # Load enhanced provenance fields
        if data.get("provenanceInfo"):
            manifest.provenance_info = ProvenanceInfo.from_dict(data["provenanceInfo"])

        if data.get("processingLog"):
            manifest.processing_log = ProcessingLog.from_dict(data["processingLog"])

        # Load presentation profile
        if data.get("presentationProfile"):
            manifest.presentation_profile = PresentationProfile.from_dict(data["presentationProfile"])

        return manifest

    def _compute_hash(self, data: Any) -> str:
        """Compute a hash for data."""
        if data is None:
            return ""
        try:
            json_str = json.dumps(data, sort_keys=True, default=str)
            return hashlib.sha256(json_str.encode()).hexdigest()[:16]
        except (TypeError, ValueError):
            return hashlib.sha256(str(data).encode()).hexdigest()[:16]

    @staticmethod
    def compute_file_hash(file_path: str) -> str:
        """
        Compute SHA256 hash of a file.

        Args:
            file_path: Path to file

        Returns:
            SHA256 hash as hex string
        """
        sha256_hash = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except (IOError, OSError):
            return ""


# Content Profiling Functions (LibV2 Pattern)

def extract_presentation_profile(presentation: Dict[str, Any]) -> PresentationProfile:
    """
    Extract comprehensive profile from presentation schema JSON.

    Analyzes presentation structure, content quality, and visual elements
    to provide detailed metrics and compliance assessments.

    Args:
        presentation: Presentation data following presentation_schema.json

    Returns:
        PresentationProfile with comprehensive analytics
    """
    profile = PresentationProfile()

    sections = presentation.get('sections', [])
    profile.total_sections = len(sections)

    # Counters
    total_bullets = 0
    bullet_word_counts = []
    slides_with_notes = 0
    compliant_slides = 0
    all_text_content = []
    all_sentences = []

    # Process each section
    for section in sections:
        section_title = section.get('title', 'Untitled Section')
        section_slide_count = 0

        for slide in section.get('slides', []):
            profile.total_slides += 1
            section_slide_count += 1

            # Track slide type
            slide_type = slide.get('type', 'content')
            profile.slide_type_distribution[slide_type] = \
                profile.slide_type_distribution.get(slide_type, 0) + 1

            # Track speaker notes
            if slide.get('notes'):
                slides_with_notes += 1

            # Extract content for analysis
            content = slide.get('content', {})
            slide_texts = []

            # Title
            if slide.get('title'):
                slide_texts.append(slide['title'])

            # Bullets (main content)
            bullets = content.get('bullets', [])
            if bullets:
                total_bullets += len(bullets)
                for bullet in bullets:
                    slide_texts.append(bullet)
                    words = bullet.split()
                    bullet_word_counts.append(len(words))

                # Check 6x6 compliance
                if len(bullets) <= 6:
                    # Check word count per bullet
                    if all(len(b.split()) <= 12 for b in bullets):
                        compliant_slides += 1
                else:
                    # More than 6 bullets = non-compliant
                    pass
            else:
                # Slides without bullets are considered compliant
                compliant_slides += 1

            # Two-column content
            for col in ['left', 'right']:
                col_bullets = content.get(col, [])
                if col_bullets:
                    total_bullets += len(col_bullets)
                    for bullet in col_bullets:
                        slide_texts.append(bullet)
                        bullet_word_counts.append(len(bullet.split()))

            # Other text content
            for key in ['subtitle', 'text', 'definition', 'attribution', 'chart_title']:
                if content.get(key):
                    slide_texts.append(content[key])

            # Tables
            if content.get('headers') or content.get('rows'):
                profile.tables_count += 1
                if content.get('headers'):
                    slide_texts.extend(content['headers'])
                if content.get('rows'):
                    for row in content['rows']:
                        slide_texts.extend(row)

            # Charts
            if content.get('chart_type') or content.get('chart_data'):
                profile.charts_count += 1

            # Images
            if content.get('image_path'):
                profile.images_count += 1
            if content.get('images'):
                profile.images_count += len(content['images'])

            # Complex structures
            if content.get('steps'):
                for step in content['steps']:
                    if step.get('label'):
                        slide_texts.append(step['label'])
                    if step.get('description'):
                        slide_texts.append(step['description'])

            if content.get('events'):
                for event in content['events']:
                    if event.get('label'):
                        slide_texts.append(event['label'])
                    if event.get('description'):
                        slide_texts.append(event['description'])

            if content.get('pairs'):
                for pair in content['pairs']:
                    if pair.get('key'):
                        slide_texts.append(pair['key'])
                    if pair.get('value'):
                        slide_texts.append(pair['value'])

            if content.get('stats'):
                for stat in content['stats']:
                    if stat.get('value'):
                        slide_texts.append(stat['value'])
                    if stat.get('label'):
                        slide_texts.append(stat['label'])

            if content.get('cards'):
                for card in content['cards']:
                    if card.get('title'):
                        slide_texts.append(card['title'])
                    if card.get('items'):
                        slide_texts.extend(card['items'])

            if content.get('callouts'):
                for callout in content['callouts']:
                    if callout.get('heading'):
                        slide_texts.append(callout['heading'])
                    if callout.get('text'):
                        slide_texts.append(callout['text'])

            if content.get('details'):
                slide_texts.extend(content['details'])

            if content.get('agenda_items'):
                for item in content['agenda_items']:
                    if item.get('section'):
                        slide_texts.append(item['section'])
                    if item.get('description'):
                        slide_texts.append(item['description'])

            # Speaker notes
            if slide.get('notes'):
                slide_texts.append(slide['notes'])

            # Aggregate text content
            all_text_content.extend(slide_texts)

            # Extract sentences for complexity analysis
            for text in slide_texts:
                sentences = re.split(r'[.!?]+', text)
                all_sentences.extend([s.strip() for s in sentences if s.strip()])

        # Track section sizes
        if section_slide_count > 0:
            profile.section_sizes[section_title] = section_slide_count

    # Calculate metrics
    if profile.total_slides > 0:
        profile.speaker_notes_coverage = slides_with_notes / profile.total_slides
        profile.six_by_six_compliance = compliant_slides / profile.total_slides

    if total_bullets > 0:
        profile.average_bullets_per_slide = total_bullets / profile.total_slides

    if bullet_word_counts:
        profile.average_words_per_bullet = sum(bullet_word_counts) / len(bullet_word_counts)

    # Word and character counts
    all_text = ' '.join(all_text_content)
    profile.total_characters = len(all_text)
    words = all_text.split()
    profile.total_words = len(words)

    # Vocabulary richness (type-token ratio)
    profile.vocabulary_richness = calculate_vocabulary_richness(all_text_content)

    # Average sentence length
    if all_sentences:
        sentence_lengths = [len(s.split()) for s in all_sentences]
        profile.average_sentence_length = sum(sentence_lengths) / len(sentence_lengths)

    return profile


def calculate_vocabulary_richness(texts: List[str]) -> float:
    """
    Calculate type-token ratio for content quality assessment.

    Type-token ratio is the ratio of unique words (types) to total words (tokens).
    Higher values indicate more diverse vocabulary.

    Args:
        texts: List of text strings to analyze

    Returns:
        Type-token ratio (0.0 to 1.0)
    """
    if not texts:
        return 0.0

    # Combine all texts
    combined = ' '.join(texts).lower()

    # Extract words (alphanumeric only)
    words = re.findall(r'\b[a-z0-9]+\b', combined)

    if not words:
        return 0.0

    # Calculate ratio
    unique_words = set(words)
    return len(unique_words) / len(words)


def calculate_content_complexity(presentation: Dict[str, Any]) -> Dict[str, Any]:
    """
    Assess complexity metrics for presentation content.

    Args:
        presentation: Presentation data following presentation_schema.json

    Returns:
        Dictionary with complexity metrics:
        - average_sentence_length: Average words per sentence
        - vocabulary_diversity: Type-token ratio
        - reading_level: Estimated reading level (basic/intermediate/advanced)
    """
    all_text_content = []
    all_sentences = []

    # Extract all text from presentation
    for section in presentation.get('sections', []):
        for slide in section.get('slides', []):
            content = slide.get('content', {})

            # Collect all text fields
            text_fields = []

            if slide.get('title'):
                text_fields.append(slide['title'])

            for key in ['subtitle', 'text', 'bullets', 'left', 'right', 'definition']:
                value = content.get(key)
                if isinstance(value, list):
                    text_fields.extend(value)
                elif value:
                    text_fields.append(value)

            if slide.get('notes'):
                text_fields.append(slide['notes'])

            all_text_content.extend(text_fields)

            # Extract sentences
            for text in text_fields:
                sentences = re.split(r'[.!?]+', text)
                all_sentences.extend([s.strip() for s in sentences if s.strip()])

    # Calculate metrics
    avg_sentence_length = 0.0
    if all_sentences:
        sentence_lengths = [len(s.split()) for s in all_sentences]
        avg_sentence_length = sum(sentence_lengths) / len(sentence_lengths)

    vocabulary_diversity = calculate_vocabulary_richness(all_text_content)

    # Estimate reading level based on sentence length
    if avg_sentence_length < 10:
        reading_level = "basic"
    elif avg_sentence_length < 20:
        reading_level = "intermediate"
    else:
        reading_level = "advanced"

    return {
        "average_sentence_length": round(avg_sentence_length, 2),
        "vocabulary_diversity": round(vocabulary_diversity, 3),
        "reading_level": reading_level
    }


# Convenience functions for creating manifests

def create_manifest(
    source_path: str,
    source_format: str,
    pipeline_version: str = "1.0.0",
    pipeline_config: Optional[Dict[str, Any]] = None,
    source_type: Optional[str] = None,
    original_provider: Optional[str] = None
) -> PipelineManifest:
    """
    Create a new manifest with provenance tracking.

    Args:
        source_path: Path to source file
        source_format: Format of source ("markdown", "json", "text", "html")
        pipeline_version: Version of Slideforge pipeline
        pipeline_config: Pipeline configuration dictionary
        source_type: Type of source content ("document", "outline", "notes")
        original_provider: Content author or organization

    Returns:
        PipelineManifest instance
    """
    manifest = PipelineManifest()
    manifest.version = pipeline_version
    manifest.pipeline_config = pipeline_config or {}

    # Compute input hash
    input_hash = PipelineManifest.compute_file_hash(source_path)

    # Create provenance info
    manifest.create_provenance_info(
        source_path=source_path,
        source_format=source_format,
        pipeline_version=pipeline_version,
        input_hash=input_hash,
        source_type=source_type,
        original_provider=original_provider
    )

    # Initialize processing log
    manifest.initialize_processing_log()

    return manifest


def load_manifest(manifest_path: str) -> PipelineManifest:
    """
    Load existing manifest from file.

    Args:
        manifest_path: Path to manifest JSON file

    Returns:
        PipelineManifest instance
    """
    from pathlib import Path
    return PipelineManifest.load(Path(manifest_path))


def save_manifest(manifest: PipelineManifest, manifest_path: str) -> None:
    """
    Save manifest to file.

    Args:
        manifest: PipelineManifest instance
        manifest_path: Path for output JSON file
    """
    from pathlib import Path
    manifest.save(Path(manifest_path))
