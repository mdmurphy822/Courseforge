"""
Semantic Structure Extractor Package

Extracts semantic structure from DART-processed HTML documents
for learning objective generation.
"""

from .heading_parser import (
    HeadingParser,
    HeadingHierarchy,
    HeadingNode,
    extract_heading_hierarchy
)

from .content_block_classifier import (
    ContentBlockClassifier,
    ContentBlock,
    BlockType,
    Definition,
    KeyTerm,
    TableData,
    FigureData,
    classify_html_content
)

from .semantic_structure_extractor import (
    SemanticStructureExtractor,
    ChapterStructure,
    SectionStructure,
    extract_textbook_structure
)

__version__ = "1.0.0"

__all__ = [
    # Heading Parser
    "HeadingParser",
    "HeadingHierarchy",
    "HeadingNode",
    "extract_heading_hierarchy",
    # Content Block Classifier
    "ContentBlockClassifier",
    "ContentBlock",
    "BlockType",
    "Definition",
    "KeyTerm",
    "TableData",
    "FigureData",
    "classify_html_content",
    # Semantic Structure Extractor
    "SemanticStructureExtractor",
    "ChapterStructure",
    "SectionStructure",
    "extract_textbook_structure",
]
