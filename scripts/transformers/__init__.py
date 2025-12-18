"""
Transformers Module for Slideforge

Content transformation layer that bridges semantic extraction
and presentation generation.
"""

from .semantic_to_presentation import (
    SemanticToPresentationTransformer,
    TransformationConfig,
    TransformationResult
)

from .block_to_slide_mapper import (
    BlockToSlideMapper,
    SlideTypeMapping,
    MappingDecision
)

from .content_splitter import (
    ContentSplitter,
    SplitResult,
    SixSixRuleEnforcer
)

from .notes_generator import (
    NotesGenerator,
    SpeakerNote,
    NoteStyle
)

__all__ = [
    "SemanticToPresentationTransformer",
    "TransformationConfig",
    "TransformationResult",
    "BlockToSlideMapper",
    "SlideTypeMapping",
    "MappingDecision",
    "ContentSplitter",
    "SplitResult",
    "SixSixRuleEnforcer",
    "NotesGenerator",
    "SpeakerNote",
    "NoteStyle"
]

__version__ = "1.0.0"
