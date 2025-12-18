"""
Pipeline Module for Slideforge

End-to-end pipeline for transforming content into presentations.
Connects semantic extraction, template selection, and PPTX generation
with validation at each stage.

CLI Usage:
    python -m scripts.pipeline generate input.md output.pptx --theme corporate
    python -m scripts.pipeline validate presentation.json
    python -m scripts.pipeline templates
"""

from .orchestrator import (
    Pipeline,
    PipelineConfig,
    PipelineResult,
    StageResult,
    run_pipeline
)

from .manifest import (
    PipelineManifest,
    ProcessingStep,
    ProvenanceEntry,
    QualityMetadata
)

from .cli import main as cli_main

__all__ = [
    "Pipeline",
    "PipelineConfig",
    "PipelineResult",
    "StageResult",
    "run_pipeline",
    "PipelineManifest",
    "ProcessingStep",
    "ProvenanceEntry",
    "QualityMetadata",
    "cli_main"
]

__version__ = "1.0.0"
