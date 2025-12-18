"""
Semantic to Presentation Transformer for Slideforge

Core transformation module that converts semantic structure
output to presentation schema format.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import json
import uuid
from datetime import datetime

from .block_to_slide_mapper import BlockToSlideMapper, MappingDecision
from .content_splitter import ContentSplitter, SixSixRule, SplitStrategy
from .notes_generator import NotesGenerator, NoteStyle


@dataclass
class TransformationConfig:
    """Configuration for semantic to presentation transformation."""
    # 6x6 Rule settings
    max_bullets: int = 6
    max_words_per_bullet: int = 6
    strict_six_six: bool = False

    # Notes settings
    generate_notes: bool = True
    notes_style: NoteStyle = NoteStyle.TALKING_POINTS

    # Split settings
    split_strategy: SplitStrategy = SplitStrategy.SEMANTIC

    # Section settings
    create_section_headers: bool = True
    section_header_style: str = "section_header"

    # Title slide settings
    create_title_slide: bool = True

    # Quality settings
    min_slides_per_section: int = 1
    max_slides_per_section: int = 20

    # Metadata
    include_provenance: bool = True


@dataclass
class TransformationResult:
    """Result of a transformation operation."""
    presentation: Dict[str, Any]
    metadata: Dict[str, Any]
    provenance: List[Dict[str, Any]]
    quality_metrics: Dict[str, Any]
    warnings: List[str]

    def to_json(self, indent: int = 2) -> str:
        """Export result as JSON."""
        return json.dumps({
            "presentation": self.presentation,
            "metadata": self.metadata,
            "provenance": self.provenance,
            "qualityMetrics": self.quality_metrics,
            "warnings": self.warnings
        }, indent=indent, ensure_ascii=False)

    def save(self, path: Path) -> None:
        """Save result to file."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(self.to_json())


class SemanticToPresentationTransformer:
    """
    Transforms semantic structure to presentation schema format.

    Handles:
    - Chapter/section to presentation section mapping
    - Content block to slide type mapping
    - 6x6 rule enforcement with content splitting
    - Speaker notes generation
    - Provenance tracking
    """

    def __init__(self, config: Optional[TransformationConfig] = None):
        """Initialize transformer with configuration."""
        self.config = config or TransformationConfig()

        # Initialize sub-components
        six_six_config = SixSixRule(
            max_bullets=self.config.max_bullets,
            max_words_per_bullet=self.config.max_words_per_bullet,
            strict_mode=self.config.strict_six_six
        )

        self.block_mapper = BlockToSlideMapper()
        self.content_splitter = ContentSplitter(six_six_config)
        self.notes_generator = NotesGenerator(self.config.notes_style)

        self.provenance_log: List[Dict[str, Any]] = []
        self.warnings: List[str] = []

    def transform(
        self,
        semantic_structure: Dict[str, Any],
        source_path: Optional[str] = None
    ) -> TransformationResult:
        """
        Transform semantic structure to presentation format.

        Args:
            semantic_structure: Output from semantic structure extractor
            source_path: Optional path to original source file

        Returns:
            TransformationResult with presentation and metadata
        """
        self.provenance_log = []
        self.warnings = []

        # Extract metadata
        metadata = self._extract_metadata(semantic_structure, source_path)

        # Transform sections
        sections = self._transform_sections(semantic_structure)

        # Build presentation
        presentation = {
            "metadata": metadata,
            "sections": sections
        }

        # Add title slide if configured
        if self.config.create_title_slide:
            presentation = self._add_title_slide(presentation, metadata)

        # Calculate quality metrics
        quality_metrics = self._calculate_quality_metrics(presentation)

        return TransformationResult(
            presentation=presentation,
            metadata={
                "transformedAt": datetime.now().isoformat(),
                "config": self._config_to_dict(),
                "sourcePath": source_path
            },
            provenance=self.provenance_log,
            quality_metrics=quality_metrics,
            warnings=self.warnings
        )

    def _extract_metadata(
        self,
        structure: Dict[str, Any],
        source_path: Optional[str]
    ) -> Dict[str, Any]:
        """Extract presentation metadata from semantic structure."""
        semantic_meta = structure.get("metadata", {})

        metadata = {
            "title": semantic_meta.get("title", "Untitled Presentation"),
            "subtitle": semantic_meta.get("subtitle", ""),
            "author": semantic_meta.get("author", ""),
            "date": semantic_meta.get("date", datetime.now().strftime("%Y-%m-%d")),
            "subject": semantic_meta.get("subject", ""),
            "keywords": semantic_meta.get("keywords", [])
        }

        # Try to extract from document info if not in metadata
        if not metadata["title"] and "document" in structure:
            doc = structure["document"]
            metadata["title"] = doc.get("title", "Untitled Presentation")

        return metadata

    def _transform_sections(
        self,
        structure: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Transform semantic chapters/sections to presentation sections."""
        sections = []

        # Handle different structure formats
        chapters = structure.get("chapters", [])
        if not chapters:
            chapters = structure.get("sections", [])
        if not chapters:
            # Try to create sections from top-level content
            chapters = self._infer_chapters(structure)

        for chapter in chapters:
            section = self._transform_chapter(chapter)
            if section:
                sections.append(section)

        return sections

    def _transform_chapter(
        self,
        chapter: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Transform a semantic chapter to a presentation section."""
        title = chapter.get("title", "")
        chapter_id = chapter.get("id", str(uuid.uuid4())[:8])

        slides = []

        # Add section header if configured
        if self.config.create_section_headers and title:
            header_slide = {
                "type": self.config.section_header_style,
                "title": title,
                "content": {
                    "subtitle": chapter.get("summary", "")
                },
                "notes": f"Section: {title}"
            }
            slides.append(header_slide)

            self._log_provenance(
                source_id=chapter_id,
                source_type="chapter",
                target_type="section_header",
                transformation="create_section_header"
            )

        # Transform content blocks
        blocks = chapter.get("content", [])
        if not blocks:
            blocks = chapter.get("blocks", [])

        # Also check for nested sections
        subsections = chapter.get("sections", [])
        for subsection in subsections:
            subsection_slides = self._transform_subsection(subsection, chapter_id)
            slides.extend(subsection_slides)

        # Transform blocks to slides
        block_slides = self._transform_blocks(blocks, chapter_id)
        slides.extend(block_slides)

        if not slides:
            self.warnings.append(f"Section '{title}' has no slides")
            return None

        return {
            "title": title,
            "slides": slides
        }

    def _transform_subsection(
        self,
        subsection: Dict[str, Any],
        parent_id: str
    ) -> List[Dict[str, Any]]:
        """Transform a subsection to slides."""
        slides = []
        title = subsection.get("title", "")
        subsection_id = subsection.get("id", str(uuid.uuid4())[:8])

        # Add subsection header
        if title:
            slides.append({
                "type": "content",
                "title": title,
                "content": {
                    "subtitle": subsection.get("summary", "")
                }
            })

        # Transform blocks
        blocks = subsection.get("content", [])
        if not blocks:
            blocks = subsection.get("blocks", [])

        block_slides = self._transform_blocks(blocks, f"{parent_id}.{subsection_id}")
        slides.extend(block_slides)

        return slides

    def _transform_blocks(
        self,
        blocks: List[Dict[str, Any]],
        source_id: str
    ) -> List[Dict[str, Any]]:
        """Transform content blocks to slides."""
        slides = []

        # Map blocks to slide types
        mapping_decisions = self.block_mapper.map_blocks(blocks)

        for block, decision in zip(blocks, mapping_decisions):
            block_slides = self._transform_block(block, decision, source_id)
            slides.extend(block_slides)

        return slides

    def _transform_block(
        self,
        block: Dict[str, Any],
        decision: MappingDecision,
        source_id: str
    ) -> List[Dict[str, Any]]:
        """Transform a single block to one or more slides."""
        slides = []
        block_id = block.get("id", str(uuid.uuid4())[:8])

        # Extract content based on block type
        content = self._extract_block_content(block, decision.slide_type)

        # Split if needed (6x6 rule)
        split_result = self.content_splitter.split_content(
            content,
            decision.slide_type,
            self.config.split_strategy
        )

        # Generate slides from split parts
        for i, part in enumerate(split_result.split_parts):
            slide = self._create_slide(
                slide_type=decision.slide_type,
                content=part,
                original_block=block
            )

            # Generate speaker notes
            if self.config.generate_notes:
                notes = self.notes_generator.generate_notes(
                    slide,
                    block,
                    self.config.notes_style
                )
                slide["notes"] = notes.content

            slides.append(slide)

            # Log provenance
            self._log_provenance(
                source_id=f"{source_id}.{block_id}",
                source_type=block.get("type", "unknown"),
                target_type=decision.slide_type,
                transformation="block_to_slide",
                metadata={
                    "split_part": i,
                    "total_parts": len(split_result.split_parts),
                    "confidence": decision.confidence
                }
            )

        return slides

    def _extract_block_content(
        self,
        block: Dict[str, Any],
        slide_type: str
    ) -> Dict[str, Any]:
        """Extract and format content for a slide type."""
        block_type = block.get("type", "paragraph")
        raw_content = block.get("content", "")
        title = block.get("title", "")

        content = {"title": title}

        if slide_type == "content":
            content["bullets"] = self._to_bullets(raw_content)

        elif slide_type == "two_content":
            left, right = self._split_two_columns(raw_content)
            content["left"] = left
            content["right"] = right

        elif slide_type == "comparison":
            left, right = self._split_two_columns(raw_content)
            content["left"] = left
            content["right"] = right
            content["left_title"] = block.get("left_title", "Option A")
            content["right_title"] = block.get("right_title", "Option B")

        elif slide_type == "quote":
            content["text"] = self._extract_quote_text(raw_content)
            content["attribution"] = block.get("attribution", "")

        elif slide_type == "table":
            content["headers"] = block.get("headers", [])
            content["rows"] = block.get("rows", [])

        elif slide_type == "process_flow":
            content["steps"] = self._to_steps(raw_content)
            content["flow_style"] = block.get("flow_style", "horizontal")

        elif slide_type == "timeline":
            content["events"] = self._to_events(raw_content)

        elif slide_type == "key_value":
            content["pairs"] = self._to_pairs(raw_content)

        elif slide_type == "image":
            content["image_path"] = block.get("image_path", "")
            content["alt_text"] = block.get("alt_text", title)

        return content

    def _to_bullets(self, content: Any) -> List[str]:
        """Convert content to bullet list."""
        if isinstance(content, list):
            return [str(item) for item in content]

        if isinstance(content, dict):
            if "bullets" in content:
                return content["bullets"]
            if "items" in content:
                return [str(item) for item in content["items"]]

        if isinstance(content, str):
            # Split by lines or sentences
            lines = content.split("\n")
            if len(lines) > 1:
                return [line.strip() for line in lines if line.strip()]

            # Split by sentences
            import re
            sentences = re.split(r'(?<=[.!?])\s+', content)
            return [s.strip() for s in sentences if s.strip()]

        return [str(content)] if content else []

    def _split_two_columns(self, content: Any) -> Tuple[List[str], List[str]]:
        """Split content into two columns."""
        bullets = self._to_bullets(content)

        if not bullets:
            return [], []

        mid = len(bullets) // 2
        return bullets[:mid], bullets[mid:]

    def _extract_quote_text(self, content: Any) -> str:
        """Extract quote text from content."""
        if isinstance(content, str):
            return content.strip('"\'')

        if isinstance(content, dict):
            return content.get("text", content.get("quote", ""))

        return str(content) if content else ""

    def _to_steps(self, content: Any) -> List[Dict[str, str]]:
        """Convert content to process steps."""
        bullets = self._to_bullets(content)

        return [
            {"label": f"Step {i+1}", "description": bullet}
            for i, bullet in enumerate(bullets)
        ]

    def _to_events(self, content: Any) -> List[Dict[str, str]]:
        """Convert content to timeline events."""
        bullets = self._to_bullets(content)

        return [
            {"label": bullet, "date": "", "description": ""}
            for bullet in bullets
        ]

    def _to_pairs(self, content: Any) -> List[Dict[str, str]]:
        """Convert content to key-value pairs."""
        if isinstance(content, dict) and "pairs" in content:
            return content["pairs"]

        bullets = self._to_bullets(content)
        pairs = []

        for bullet in bullets:
            if ":" in bullet:
                key, value = bullet.split(":", 1)
                pairs.append({"key": key.strip(), "value": value.strip()})
            else:
                pairs.append({"key": bullet, "value": ""})

        return pairs

    def _create_slide(
        self,
        slide_type: str,
        content: Dict[str, Any],
        original_block: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a slide dictionary."""
        title = content.get("title", original_block.get("title", ""))

        slide = {
            "type": slide_type,
            "title": title,
            "content": {k: v for k, v in content.items() if k != "title"}
        }

        return slide

    def _add_title_slide(
        self,
        presentation: Dict[str, Any],
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Add title slide to presentation."""
        title_slide = {
            "type": "title",
            "title": metadata.get("title", ""),
            "content": {
                "subtitle": metadata.get("subtitle", "")
            },
            "notes": f"Welcome to {metadata.get('title', 'this presentation')}"
        }

        # Insert as first section
        title_section = {
            "title": "",
            "slides": [title_slide]
        }

        presentation["sections"].insert(0, title_section)

        return presentation

    def _infer_chapters(
        self,
        structure: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Infer chapters from flat structure."""
        # Try to find content blocks at top level
        content = structure.get("content", [])

        if content:
            return [{
                "title": structure.get("title", "Main Content"),
                "content": content
            }]

        # Return empty if no content found
        return []

    def _log_provenance(
        self,
        source_id: str,
        source_type: str,
        target_type: str,
        transformation: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log a provenance entry."""
        if self.config.include_provenance:
            self.provenance_log.append({
                "sourceId": source_id,
                "sourceType": source_type,
                "targetType": target_type,
                "transformation": transformation,
                "timestamp": datetime.now().isoformat(),
                "metadata": metadata or {}
            })

    def _calculate_quality_metrics(
        self,
        presentation: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate quality metrics for the presentation."""
        total_slides = 0
        slides_with_notes = 0
        six_six_violations = 0
        slide_types = set()

        for section in presentation.get("sections", []):
            for slide in section.get("slides", []):
                total_slides += 1
                slide_types.add(slide.get("type", "content"))

                if slide.get("notes"):
                    slides_with_notes += 1

                # Check 6x6 compliance
                content = slide.get("content", {})
                bullets = content.get("bullets", [])

                if len(bullets) > self.config.max_bullets:
                    six_six_violations += 1

                for bullet in bullets:
                    if len(bullet.split()) > self.config.max_words_per_bullet:
                        six_six_violations += 1

        notes_coverage = slides_with_notes / total_slides if total_slides > 0 else 0

        return {
            "totalSlides": total_slides,
            "totalSections": len(presentation.get("sections", [])),
            "slideTypeVariety": len(slide_types),
            "slideTypes": list(slide_types),
            "notesCoverage": round(notes_coverage, 2),
            "sixSixViolations": six_six_violations,
            "validationScore": self._calculate_validation_score(
                total_slides, notes_coverage, six_six_violations, len(slide_types)
            )
        }

    def _calculate_validation_score(
        self,
        total_slides: int,
        notes_coverage: float,
        violations: int,
        type_variety: int
    ) -> float:
        """Calculate overall validation score (0-100)."""
        score = 100.0

        # Penalize for violations
        score -= violations * 5

        # Reward notes coverage (up to 20 points)
        score += notes_coverage * 20 - 10  # 80% coverage = +6 points

        # Reward type variety (up to 10 points)
        score += min(type_variety * 2, 10)

        # Penalize if too few or too many slides
        if total_slides < 5:
            score -= 10
        elif total_slides > 50:
            score -= 5

        return max(0, min(100, score))

    def _config_to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return {
            "maxBullets": self.config.max_bullets,
            "maxWordsPerBullet": self.config.max_words_per_bullet,
            "strictSixSix": self.config.strict_six_six,
            "generateNotes": self.config.generate_notes,
            "notesStyle": self.config.notes_style.value,
            "splitStrategy": self.config.split_strategy.value,
            "createSectionHeaders": self.config.create_section_headers,
            "createTitleSlide": self.config.create_title_slide
        }
