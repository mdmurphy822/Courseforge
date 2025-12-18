"""
Semantic Structure Extractor Package

Extracts semantic structure from HTML or Markdown documents
for presentation generation. Includes:
- Heading hierarchy parsing
- Content block classification
- Markdown parsing with YAML front matter
- Content profiling (difficulty, readability, concepts)
- Concept graph building with centrality calculation
- Presentation schema transformation
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
    extract_textbook_structure,
    extract_for_presentation
)

from .markdown_parser import (
    MarkdownParser,
    MarkdownDocument,
    MarkdownSection,
    MarkdownBlock,
    MarkdownBlockType,
    detect_format,
    parse_markdown
)

from .content_profiler import (
    ContentProfiler,
    ContentProfile,
    ConceptReference,
    SectionProfile,
    ContentType,
    DifficultyLevel,
    PedagogicalPattern,
    profile_content
)

from .concept_graph import (
    ConceptGraphBuilder,
    ConceptGraph,
    ConceptNode,
    ConceptEdge,
    CentralityAlgorithm,
    build_concept_graph
)

from .presentation_transformer import (
    PresentationTransformer,
    SlideCandidate,
    SlideType,
    ProvenanceEntry,
    transform_to_presentation
)

__version__ = "2.0.0"

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
    "extract_for_presentation",
    # Markdown Parser
    "MarkdownParser",
    "MarkdownDocument",
    "MarkdownSection",
    "MarkdownBlock",
    "MarkdownBlockType",
    "detect_format",
    "parse_markdown",
    # Content Profiler
    "ContentProfiler",
    "ContentProfile",
    "ConceptReference",
    "SectionProfile",
    "ContentType",
    "DifficultyLevel",
    "PedagogicalPattern",
    "profile_content",
    # Concept Graph
    "ConceptGraphBuilder",
    "ConceptGraph",
    "ConceptNode",
    "ConceptEdge",
    "CentralityAlgorithm",
    "build_concept_graph",
    # Presentation Transformer
    "PresentationTransformer",
    "SlideCandidate",
    "SlideType",
    "ProvenanceEntry",
    "transform_to_presentation",
]
