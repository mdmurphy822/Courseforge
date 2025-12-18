"""
Block to Slide Mapper for Slideforge

Maps semantic content blocks to appropriate slide types
based on content characteristics and context.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
import re


class BlockType(Enum):
    """Semantic block types from extraction."""
    PARAGRAPH = "paragraph"
    LIST_ORDERED = "list_ordered"
    LIST_UNORDERED = "list_unordered"
    DEFINITION_LIST = "definition_list"
    TABLE = "table"
    BLOCKQUOTE = "blockquote"
    CODE_BLOCK = "code_block"
    FIGURE = "figure"
    HEADING = "heading"
    CALLOUT_INFO = "callout_info"
    CALLOUT_WARNING = "callout_warning"
    CALLOUT_TIP = "callout_tip"
    CALLOUT_NOTE = "callout_note"
    PROCEDURE = "procedure"
    COMPARISON = "comparison"
    TIMELINE = "timeline"


class SlideType(Enum):
    """Available slide types in presentation schema."""
    TITLE = "title"
    SECTION_HEADER = "section_header"
    CONTENT = "content"
    TWO_CONTENT = "two_content"
    COMPARISON = "comparison"
    IMAGE = "image"
    QUOTE = "quote"
    BLANK = "blank"
    TABLE = "table"
    PROCESS_FLOW = "process_flow"
    COMPARISON_MATRIX = "comparison_matrix"
    TIMELINE = "timeline"
    KEY_VALUE = "key_value"


@dataclass
class SlideTypeMapping:
    """Mapping configuration for a block type."""
    block_type: str
    primary_slide_type: str
    fallback_slide_type: str
    conditions: Dict[str, Any] = field(default_factory=dict)
    priority: int = 5  # 1-10, higher = more specific


@dataclass
class MappingDecision:
    """Result of a mapping decision."""
    slide_type: str
    confidence: float  # 0.0 - 1.0
    reason: str
    alternatives: List[Tuple[str, float]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class BlockToSlideMapper:
    """
    Maps content blocks to slide types using configurable rules.

    Considers:
    - Block type semantics
    - Content characteristics
    - Context (preceding/following blocks)
    - Presentation flow
    """

    # Default mapping rules
    DEFAULT_MAPPINGS: Dict[str, SlideTypeMapping] = {
        "paragraph": SlideTypeMapping(
            block_type="paragraph",
            primary_slide_type="content",
            fallback_slide_type="content"
        ),
        "list_ordered": SlideTypeMapping(
            block_type="list_ordered",
            primary_slide_type="content",
            fallback_slide_type="content",
            conditions={"max_items": 6, "prefer_process_if_sequential": True}
        ),
        "list_unordered": SlideTypeMapping(
            block_type="list_unordered",
            primary_slide_type="content",
            fallback_slide_type="content",
            conditions={"max_items": 6}
        ),
        "definition_list": SlideTypeMapping(
            block_type="definition_list",
            primary_slide_type="two_content",
            fallback_slide_type="content",
            conditions={"prefer_key_value_if_short": True}
        ),
        "table": SlideTypeMapping(
            block_type="table",
            primary_slide_type="table",
            fallback_slide_type="content",
            conditions={"max_columns": 6, "max_rows": 8}
        ),
        "blockquote": SlideTypeMapping(
            block_type="blockquote",
            primary_slide_type="quote",
            fallback_slide_type="content"
        ),
        "code_block": SlideTypeMapping(
            block_type="code_block",
            primary_slide_type="content",
            fallback_slide_type="content",
            conditions={"use_monospace": True}
        ),
        "figure": SlideTypeMapping(
            block_type="figure",
            primary_slide_type="image",
            fallback_slide_type="content"
        ),
        "heading": SlideTypeMapping(
            block_type="heading",
            primary_slide_type="section_header",
            fallback_slide_type="content",
            conditions={"level_threshold": 2}
        ),
        "callout_info": SlideTypeMapping(
            block_type="callout_info",
            primary_slide_type="content",
            fallback_slide_type="content",
            conditions={"style": "info"}
        ),
        "callout_warning": SlideTypeMapping(
            block_type="callout_warning",
            primary_slide_type="content",
            fallback_slide_type="content",
            conditions={"style": "warning"}
        ),
        "procedure": SlideTypeMapping(
            block_type="procedure",
            primary_slide_type="process_flow",
            fallback_slide_type="content",
            conditions={"max_steps": 6}
        ),
        "comparison": SlideTypeMapping(
            block_type="comparison",
            primary_slide_type="comparison",
            fallback_slide_type="two_content"
        ),
        "timeline": SlideTypeMapping(
            block_type="timeline",
            primary_slide_type="timeline",
            fallback_slide_type="content",
            conditions={"max_events": 6}
        )
    }

    # Patterns for detecting special content
    COMPARISON_PATTERNS = [
        r'\bvs\.?\b', r'\bversus\b', r'\bcompared? to\b',
        r'\bpros?\s+(?:and\s+)?cons?\b', r'\badvantages?\s+(?:and\s+)?disadvantages?\b',
        r'\bbefore\s+(?:and\s+)?after\b', r'\bdifferences?\b'
    ]

    PROCESS_PATTERNS = [
        r'\bstep\s+\d+\b', r'\bfirst(?:ly)?\b.*\bthen\b',
        r'\b(?:next|finally|lastly)\b', r'\bprocess\b',
        r'\bworkflow\b', r'\bprocedure\b'
    ]

    TIMELINE_PATTERNS = [
        r'\b\d{4}\b', r'\b(?:january|february|march|april|may|june|july|august|september|october|november|december)\b',
        r'\bhistory\b', r'\bevolution\b', r'\btimeline\b',
        r'\bchronolog(?:y|ical)\b', r'\bmilestone\b'
    ]

    def __init__(self, custom_mappings: Optional[Dict[str, SlideTypeMapping]] = None):
        """Initialize mapper with optional custom mappings."""
        self.mappings = dict(self.DEFAULT_MAPPINGS)
        if custom_mappings:
            self.mappings.update(custom_mappings)

    def map_block(
        self,
        block: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> MappingDecision:
        """
        Map a single block to a slide type.

        Args:
            block: Content block with type and content
            context: Optional context (previous blocks, section info)

        Returns:
            MappingDecision with slide type and reasoning
        """
        block_type = block.get("type", "paragraph").lower()
        content = self._extract_text_content(block)

        # Get base mapping
        mapping = self.mappings.get(block_type, self.DEFAULT_MAPPINGS["paragraph"])

        # Analyze content for special patterns
        detected_patterns = self._detect_content_patterns(content)

        # Determine best slide type
        slide_type, confidence, reason = self._determine_slide_type(
            block, mapping, detected_patterns, context
        )

        # Generate alternatives
        alternatives = self._generate_alternatives(
            block, mapping, detected_patterns, slide_type
        )

        return MappingDecision(
            slide_type=slide_type,
            confidence=confidence,
            reason=reason,
            alternatives=alternatives,
            metadata={
                "block_type": block_type,
                "detected_patterns": detected_patterns,
                "mapping_rule": mapping.block_type
            }
        )

    def map_blocks(
        self,
        blocks: List[Dict[str, Any]],
        section_context: Optional[Dict[str, Any]] = None
    ) -> List[MappingDecision]:
        """
        Map multiple blocks with inter-block context awareness.

        Args:
            blocks: List of content blocks
            section_context: Optional section-level context

        Returns:
            List of MappingDecisions
        """
        decisions = []

        for i, block in enumerate(blocks):
            context = {
                "previous": blocks[i-1] if i > 0 else None,
                "next": blocks[i+1] if i < len(blocks) - 1 else None,
                "position": i,
                "total_blocks": len(blocks),
                "section": section_context
            }

            decision = self.map_block(block, context)

            # Post-process for flow optimization
            if decisions:
                decision = self._optimize_for_flow(decision, decisions[-1], context)

            decisions.append(decision)

        return decisions

    def _extract_text_content(self, block: Dict[str, Any]) -> str:
        """Extract text content from various block structures."""
        content = block.get("content", "")

        if isinstance(content, str):
            return content
        elif isinstance(content, list):
            return " ".join(str(item) for item in content)
        elif isinstance(content, dict):
            text_parts = []
            if "text" in content:
                text_parts.append(content["text"])
            if "items" in content:
                text_parts.extend(str(item) for item in content["items"])
            if "bullets" in content:
                text_parts.extend(str(item) for item in content["bullets"])
            return " ".join(text_parts)

        return str(content) if content else ""

    def _detect_content_patterns(self, content: str) -> Dict[str, bool]:
        """Detect special content patterns."""
        content_lower = content.lower()

        return {
            "comparison": any(
                re.search(p, content_lower, re.IGNORECASE)
                for p in self.COMPARISON_PATTERNS
            ),
            "process": any(
                re.search(p, content_lower, re.IGNORECASE)
                for p in self.PROCESS_PATTERNS
            ),
            "timeline": any(
                re.search(p, content_lower, re.IGNORECASE)
                for p in self.TIMELINE_PATTERNS
            ),
            "has_numbers": bool(re.search(r'\d+', content)),
            "is_question": content.strip().endswith("?"),
            "has_bullets": "•" in content or "-" in content.split("\n")[0] if content else False
        }

    def _determine_slide_type(
        self,
        block: Dict[str, Any],
        mapping: SlideTypeMapping,
        patterns: Dict[str, bool],
        context: Optional[Dict[str, Any]]
    ) -> Tuple[str, float, str]:
        """Determine the best slide type based on analysis."""
        block_type = block.get("type", "paragraph")
        content = block.get("content", {})

        # Check for pattern-based overrides
        if patterns.get("comparison") and block_type in ["list_unordered", "paragraph"]:
            return "comparison", 0.85, "Comparison language detected"

        if patterns.get("process") and block_type == "list_ordered":
            # Check if it fits process flow constraints
            items = self._get_list_items(content)
            if items and len(items) <= 6:
                return "process_flow", 0.90, "Sequential process detected"

        if patterns.get("timeline"):
            events = self._extract_timeline_events(content)
            if events and len(events) <= 6:
                return "timeline", 0.85, "Timeline content detected"

        # Check definition list for key-value
        if block_type == "definition_list":
            pairs = self._extract_definition_pairs(content)
            if pairs and len(pairs) <= 6:
                return "key_value", 0.80, "Key-value pairs detected"

        # Check table constraints
        if block_type == "table":
            if self._table_fits_constraints(content, mapping.conditions):
                return "table", 0.95, "Table within size constraints"
            else:
                return mapping.fallback_slide_type, 0.60, "Table exceeds constraints"

        # Default to primary mapping
        return mapping.primary_slide_type, 0.75, f"Default mapping for {block_type}"

    def _generate_alternatives(
        self,
        block: Dict[str, Any],
        mapping: SlideTypeMapping,
        patterns: Dict[str, bool],
        selected_type: str
    ) -> List[Tuple[str, float]]:
        """Generate alternative slide type recommendations."""
        alternatives = []

        # Always include fallback if different
        if mapping.fallback_slide_type != selected_type:
            alternatives.append((mapping.fallback_slide_type, 0.50))

        # Add pattern-based alternatives
        if patterns.get("comparison") and selected_type != "comparison":
            alternatives.append(("comparison", 0.60))

        if patterns.get("process") and selected_type != "process_flow":
            alternatives.append(("process_flow", 0.55))

        # Content slide is always a fallback
        if selected_type != "content" and ("content", 0.50) not in alternatives:
            alternatives.append(("content", 0.40))

        # Sort by confidence
        alternatives.sort(key=lambda x: x[1], reverse=True)

        return alternatives[:3]  # Return top 3 alternatives

    def _optimize_for_flow(
        self,
        current: MappingDecision,
        previous: MappingDecision,
        context: Dict[str, Any]
    ) -> MappingDecision:
        """Optimize slide type selection for presentation flow."""
        # Avoid too many consecutive same types (except content)
        if (current.slide_type == previous.slide_type and
            current.slide_type not in ["content", "section_header"]):

            # Check if we have good alternatives
            for alt_type, alt_conf in current.alternatives:
                if alt_type != current.slide_type and alt_conf >= 0.45:
                    return MappingDecision(
                        slide_type=alt_type,
                        confidence=alt_conf,
                        reason=f"Flow optimization: varied from consecutive {current.slide_type}",
                        alternatives=current.alternatives,
                        metadata=current.metadata
                    )

        return current

    def _get_list_items(self, content: Any) -> List[str]:
        """Extract list items from content."""
        if isinstance(content, list):
            return content
        elif isinstance(content, dict):
            return content.get("items", content.get("bullets", []))
        return []

    def _extract_timeline_events(self, content: Any) -> List[Dict[str, str]]:
        """Extract timeline events from content."""
        items = self._get_list_items(content)
        events = []

        for item in items:
            item_str = str(item)
            # Look for date patterns
            date_match = re.search(r'(\d{4}|\w+\s+\d{1,2})', item_str)
            if date_match:
                events.append({
                    "date": date_match.group(1),
                    "label": item_str
                })

        return events

    def _extract_definition_pairs(self, content: Any) -> List[Dict[str, str]]:
        """Extract key-value pairs from definition list content."""
        if isinstance(content, dict) and "pairs" in content:
            return content["pairs"]

        if isinstance(content, list):
            pairs = []
            for item in content:
                if isinstance(item, dict) and "term" in item:
                    pairs.append({
                        "key": item["term"],
                        "value": item.get("definition", "")
                    })
            return pairs

        return []

    def _table_fits_constraints(
        self,
        content: Any,
        conditions: Dict[str, Any]
    ) -> bool:
        """Check if table content fits size constraints."""
        max_cols = conditions.get("max_columns", 6)
        max_rows = conditions.get("max_rows", 8)

        if isinstance(content, dict):
            headers = content.get("headers", [])
            rows = content.get("rows", [])

            if len(headers) > max_cols:
                return False
            if len(rows) > max_rows:
                return False

        return True

    def get_mapping_for_type(self, block_type: str) -> SlideTypeMapping:
        """Get the mapping configuration for a block type."""
        return self.mappings.get(block_type, self.DEFAULT_MAPPINGS["paragraph"])

    def add_custom_mapping(self, mapping: SlideTypeMapping) -> None:
        """Add or update a custom mapping rule."""
        self.mappings[mapping.block_type] = mapping
