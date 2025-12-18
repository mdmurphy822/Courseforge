"""
Content Splitter for Slideforge

Enforces the 6x6 rule and splits content appropriately
for optimal slide presentation.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple
import re
from enum import Enum


class SplitStrategy(Enum):
    """Strategies for splitting content."""
    EQUAL = "equal"           # Split into roughly equal parts
    SEMANTIC = "semantic"     # Split at semantic boundaries
    THRESHOLD = "threshold"   # Split when exceeding threshold
    PRIORITY = "priority"     # Keep high-priority items together


@dataclass
class SplitResult:
    """Result of a content split operation."""
    original_content: Any
    split_parts: List[Any]
    strategy_used: str
    split_points: List[int]
    overflow_notes: str = ""  # Content that went to notes
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SixSixRule:
    """Configuration for 6x6 rule enforcement."""
    max_bullets: int = 6
    max_words_per_bullet: int = 6
    max_characters_per_bullet: int = 100
    strict_mode: bool = False  # If True, never exceed limits
    overflow_to_notes: bool = True


class SixSixRuleEnforcer:
    """
    Enforces the 6x6 rule for presentation content.

    The 6x6 rule states:
    - Maximum 6 bullet points per slide
    - Maximum 6 words per bullet point
    """

    def __init__(self, config: Optional[SixSixRule] = None):
        """Initialize with optional custom configuration."""
        self.config = config or SixSixRule()

    def check_compliance(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check content for 6x6 rule compliance.

        Returns:
            Compliance report with violations and recommendations
        """
        violations = []
        recommendations = []

        bullets = content.get("bullets", [])

        # Check bullet count
        if len(bullets) > self.config.max_bullets:
            violations.append({
                "type": "too_many_bullets",
                "actual": len(bullets),
                "max": self.config.max_bullets,
                "severity": "high"
            })
            recommendations.append(
                f"Split into {self._calculate_slide_count(len(bullets))} slides"
            )

        # Check each bullet
        for i, bullet in enumerate(bullets):
            word_count = len(bullet.split())
            char_count = len(bullet)

            if word_count > self.config.max_words_per_bullet:
                violations.append({
                    "type": "bullet_too_long",
                    "bullet_index": i,
                    "word_count": word_count,
                    "max_words": self.config.max_words_per_bullet,
                    "severity": "medium"
                })
                recommendations.append(
                    f"Bullet {i+1}: Shorten to {self.config.max_words_per_bullet} words or less"
                )

            if char_count > self.config.max_characters_per_bullet:
                violations.append({
                    "type": "bullet_too_many_chars",
                    "bullet_index": i,
                    "char_count": char_count,
                    "max_chars": self.config.max_characters_per_bullet,
                    "severity": "low"
                })

        return {
            "compliant": len(violations) == 0,
            "violations": violations,
            "recommendations": recommendations,
            "bullet_count": len(bullets),
            "average_words": self._average_words(bullets),
            "score": self._calculate_compliance_score(violations, len(bullets))
        }

    def enforce(
        self,
        content: Dict[str, Any],
        strategy: SplitStrategy = SplitStrategy.SEMANTIC
    ) -> List[Dict[str, Any]]:
        """
        Enforce 6x6 rule on content, splitting if necessary.

        Args:
            content: Content dictionary with bullets
            strategy: Strategy for splitting content

        Returns:
            List of compliant content dictionaries
        """
        compliance = self.check_compliance(content)

        if compliance["compliant"]:
            return [content]

        bullets = content.get("bullets", [])
        title = content.get("title", "")

        # First, condense individual bullets if needed
        condensed_bullets = [
            self._condense_bullet(b) for b in bullets
        ]

        # Then split into multiple slides if too many bullets
        if len(condensed_bullets) > self.config.max_bullets:
            return self._split_bullets(
                condensed_bullets, title, strategy, content
            )

        return [{**content, "bullets": condensed_bullets}]

    def _condense_bullet(self, bullet: str) -> str:
        """Condense a bullet to meet word limit."""
        words = bullet.split()

        if len(words) <= self.config.max_words_per_bullet:
            return bullet

        # Try to find a natural break point
        condensed = self._find_natural_break(words)

        if condensed:
            return condensed

        # Fall back to truncation
        return " ".join(words[:self.config.max_words_per_bullet])

    def _find_natural_break(self, words: List[str]) -> Optional[str]:
        """Find a natural breaking point in text."""
        max_words = self.config.max_words_per_bullet

        # Look for conjunctions or punctuation within limit
        for i in range(min(len(words), max_words), 0, -1):
            word = words[i-1].lower()
            if word in ["and", "or", "but", ",", "-", ":"]:
                return " ".join(words[:i-1])

        return None

    def _split_bullets(
        self,
        bullets: List[str],
        title: str,
        strategy: SplitStrategy,
        original: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Split bullets into multiple slide contents."""
        max_per_slide = self.config.max_bullets

        if strategy == SplitStrategy.EQUAL:
            return self._split_equal(bullets, title, max_per_slide, original)
        elif strategy == SplitStrategy.SEMANTIC:
            return self._split_semantic(bullets, title, max_per_slide, original)
        elif strategy == SplitStrategy.PRIORITY:
            return self._split_priority(bullets, title, max_per_slide, original)
        else:
            return self._split_threshold(bullets, title, max_per_slide, original)

    def _split_equal(
        self,
        bullets: List[str],
        title: str,
        max_per_slide: int,
        original: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Split bullets into equal-sized groups."""
        slides = []
        num_slides = self._calculate_slide_count(len(bullets))
        items_per_slide = len(bullets) // num_slides

        for i in range(num_slides):
            start = i * items_per_slide
            if i == num_slides - 1:
                # Last slide gets remaining items
                end = len(bullets)
            else:
                end = start + items_per_slide

            slide_bullets = bullets[start:end]
            slide_title = self._generate_continuation_title(title, i, num_slides)

            slides.append({
                **original,
                "title": slide_title,
                "bullets": slide_bullets,
                "_split_index": i,
                "_split_total": num_slides
            })

        return slides

    def _split_semantic(
        self,
        bullets: List[str],
        title: str,
        max_per_slide: int,
        original: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Split at semantic boundaries."""
        groups = self._find_semantic_groups(bullets)
        slides = []
        current_group = []
        slide_num = 0
        total_slides = self._estimate_slides_for_groups(groups, max_per_slide)

        for group in groups:
            if len(current_group) + len(group) <= max_per_slide:
                current_group.extend(group)
            else:
                if current_group:
                    slides.append({
                        **original,
                        "title": self._generate_continuation_title(title, slide_num, total_slides),
                        "bullets": current_group,
                        "_split_index": slide_num,
                        "_split_total": total_slides
                    })
                    slide_num += 1

                # Handle large groups
                if len(group) > max_per_slide:
                    sub_slides = self._split_equal(group, title, max_per_slide, original)
                    for sub in sub_slides:
                        sub["_split_index"] = slide_num
                        slide_num += 1
                        slides.append(sub)
                    current_group = []
                else:
                    current_group = group

        if current_group:
            slides.append({
                **original,
                "title": self._generate_continuation_title(title, slide_num, total_slides),
                "bullets": current_group,
                "_split_index": slide_num,
                "_split_total": total_slides
            })

        # Recalculate totals
        for i, slide in enumerate(slides):
            slide["_split_total"] = len(slides)

        return slides

    def _split_priority(
        self,
        bullets: List[str],
        title: str,
        max_per_slide: int,
        original: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Split keeping high-priority items on first slide."""
        # First slide gets the first max_per_slide items (assumed high priority)
        slides = []
        num_slides = self._calculate_slide_count(len(bullets))

        first_slide = {
            **original,
            "title": title,
            "bullets": bullets[:max_per_slide],
            "_split_index": 0,
            "_split_total": num_slides
        }
        slides.append(first_slide)

        # Remaining items go to continuation slides
        remaining = bullets[max_per_slide:]
        if remaining:
            continuation = self._split_equal(
                remaining,
                f"{title} (Continued)",
                max_per_slide,
                original
            )
            for i, slide in enumerate(continuation, 1):
                slide["_split_index"] = i
                slide["_split_total"] = num_slides
            slides.extend(continuation)

        return slides

    def _split_threshold(
        self,
        bullets: List[str],
        title: str,
        max_per_slide: int,
        original: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Simple threshold-based splitting."""
        slides = []
        num_slides = self._calculate_slide_count(len(bullets))

        for i in range(0, len(bullets), max_per_slide):
            slide_bullets = bullets[i:i + max_per_slide]
            slide_num = i // max_per_slide

            slides.append({
                **original,
                "title": self._generate_continuation_title(title, slide_num, num_slides),
                "bullets": slide_bullets,
                "_split_index": slide_num,
                "_split_total": num_slides
            })

        return slides

    def _find_semantic_groups(self, bullets: List[str]) -> List[List[str]]:
        """Group bullets by semantic similarity."""
        groups = []
        current_group = []

        for bullet in bullets:
            if not current_group:
                current_group.append(bullet)
                continue

            # Check for semantic continuity
            if self._is_continuation(current_group[-1], bullet):
                current_group.append(bullet)
            else:
                groups.append(current_group)
                current_group = [bullet]

        if current_group:
            groups.append(current_group)

        return groups

    def _is_continuation(self, prev: str, curr: str) -> bool:
        """Check if current bullet continues from previous."""
        # Look for continuation markers
        continuation_markers = [
            r'^also\b', r'^additionally\b', r'^furthermore\b',
            r'^moreover\b', r'^similarly\b', r'^likewise\b'
        ]

        curr_lower = curr.lower()
        for pattern in continuation_markers:
            if re.match(pattern, curr_lower):
                return True

        # Check for topic continuity (shared first word)
        prev_first = prev.split()[0].lower() if prev.split() else ""
        curr_first = curr.split()[0].lower() if curr.split() else ""

        if prev_first == curr_first and prev_first not in ["the", "a", "an"]:
            return True

        return False

    def _estimate_slides_for_groups(
        self,
        groups: List[List[str]],
        max_per_slide: int
    ) -> int:
        """Estimate total slides needed for groups."""
        total = 0
        current_count = 0

        for group in groups:
            if current_count + len(group) <= max_per_slide:
                current_count += len(group)
            else:
                total += 1
                if len(group) > max_per_slide:
                    total += (len(group) - 1) // max_per_slide
                current_count = len(group) % max_per_slide

        if current_count > 0:
            total += 1

        return max(total, 1)

    def _generate_continuation_title(
        self,
        title: str,
        index: int,
        total: int
    ) -> str:
        """Generate title for continuation slides."""
        if index == 0:
            return title
        elif total <= 2:
            return f"{title} (Continued)"
        else:
            return f"{title} ({index + 1}/{total})"

    def _calculate_slide_count(self, bullet_count: int) -> int:
        """Calculate how many slides are needed."""
        if bullet_count <= self.config.max_bullets:
            return 1
        return (bullet_count + self.config.max_bullets - 1) // self.config.max_bullets

    def _average_words(self, bullets: List[str]) -> float:
        """Calculate average words per bullet."""
        if not bullets:
            return 0.0

        total_words = sum(len(b.split()) for b in bullets)
        return total_words / len(bullets)

    def _calculate_compliance_score(
        self,
        violations: List[Dict],
        bullet_count: int
    ) -> float:
        """Calculate a compliance score (0-100)."""
        if not violations:
            return 100.0

        penalty = 0
        for v in violations:
            if v["severity"] == "high":
                penalty += 30
            elif v["severity"] == "medium":
                penalty += 15
            else:
                penalty += 5

        return max(0, 100 - penalty)


class ContentSplitter:
    """
    High-level content splitter for various content types.

    Handles splitting of different content structures while
    maintaining semantic coherence.
    """

    def __init__(self, six_six_config: Optional[SixSixRule] = None):
        """Initialize with optional 6x6 rule configuration."""
        self.six_six_enforcer = SixSixRuleEnforcer(six_six_config)

    def split_content(
        self,
        content: Dict[str, Any],
        content_type: str,
        strategy: SplitStrategy = SplitStrategy.SEMANTIC
    ) -> SplitResult:
        """
        Split content based on type and strategy.

        Args:
            content: Content to split
            content_type: Type of content (bullets, table, process, etc.)
            strategy: Splitting strategy

        Returns:
            SplitResult with split parts
        """
        if content_type in ["content", "bullets"]:
            return self._split_bullet_content(content, strategy)
        elif content_type == "table":
            return self._split_table(content)
        elif content_type in ["process_flow", "steps"]:
            return self._split_process(content, strategy)
        elif content_type == "comparison":
            return self._split_comparison(content)
        else:
            # Default: treat as bullet content
            return self._split_bullet_content(content, strategy)

    def _split_bullet_content(
        self,
        content: Dict[str, Any],
        strategy: SplitStrategy
    ) -> SplitResult:
        """Split bullet-based content."""
        parts = self.six_six_enforcer.enforce(content, strategy)

        return SplitResult(
            original_content=content,
            split_parts=parts,
            strategy_used=strategy.value,
            split_points=[i * 6 for i in range(1, len(parts))],
            metadata={
                "original_bullet_count": len(content.get("bullets", [])),
                "resulting_slides": len(parts)
            }
        )

    def _split_table(self, content: Dict[str, Any]) -> SplitResult:
        """Split table content if too large."""
        headers = content.get("headers", [])
        rows = content.get("rows", [])

        max_rows = 8
        max_cols = 6

        parts = []
        overflow = []

        # Handle too many columns
        if len(headers) > max_cols:
            # Split vertically (multiple tables side by side concept)
            overflow.append(f"Table has {len(headers)} columns, exceeds {max_cols} max")
            headers = headers[:max_cols]
            rows = [row[:max_cols] for row in rows]

        # Handle too many rows
        if len(rows) <= max_rows:
            parts.append({
                **content,
                "headers": headers,
                "rows": rows
            })
        else:
            # Split horizontally
            for i in range(0, len(rows), max_rows):
                chunk_rows = rows[i:i + max_rows]
                title = content.get("title", "Table")

                if i > 0:
                    title = f"{title} (Continued)"

                parts.append({
                    **content,
                    "title": title,
                    "headers": headers,
                    "rows": chunk_rows
                })

        return SplitResult(
            original_content=content,
            split_parts=parts,
            strategy_used="table_split",
            split_points=[i * max_rows for i in range(1, len(parts))],
            overflow_notes="; ".join(overflow) if overflow else "",
            metadata={
                "original_rows": len(content.get("rows", [])),
                "original_columns": len(content.get("headers", [])),
                "resulting_tables": len(parts)
            }
        )

    def _split_process(
        self,
        content: Dict[str, Any],
        strategy: SplitStrategy
    ) -> SplitResult:
        """Split process flow content."""
        steps = content.get("steps", [])
        max_steps = 6

        if len(steps) <= max_steps:
            return SplitResult(
                original_content=content,
                split_parts=[content],
                strategy_used="no_split_needed",
                split_points=[]
            )

        parts = []
        title = content.get("title", "Process")

        for i in range(0, len(steps), max_steps):
            chunk_steps = steps[i:i + max_steps]
            part_title = title

            if i > 0:
                part_title = f"{title} (Continued)"

            parts.append({
                **content,
                "title": part_title,
                "steps": chunk_steps,
                "_step_offset": i
            })

        return SplitResult(
            original_content=content,
            split_parts=parts,
            strategy_used=strategy.value,
            split_points=[i * max_steps for i in range(1, len(parts))],
            metadata={
                "original_steps": len(steps),
                "resulting_slides": len(parts)
            }
        )

    def _split_comparison(self, content: Dict[str, Any]) -> SplitResult:
        """Split comparison content if needed."""
        left = content.get("left", [])
        right = content.get("right", [])
        max_items = 6

        # If both sides fit, no split needed
        if len(left) <= max_items and len(right) <= max_items:
            return SplitResult(
                original_content=content,
                split_parts=[content],
                strategy_used="no_split_needed",
                split_points=[]
            )

        # Balance and split
        parts = []
        title = content.get("title", "Comparison")

        max_len = max(len(left), len(right))
        num_slides = (max_len + max_items - 1) // max_items

        for i in range(num_slides):
            start = i * max_items
            end = start + max_items

            part_title = title if i == 0 else f"{title} (Continued)"

            parts.append({
                **content,
                "title": part_title,
                "left": left[start:end],
                "right": right[start:end]
            })

        return SplitResult(
            original_content=content,
            split_parts=parts,
            strategy_used="comparison_split",
            split_points=[i * max_items for i in range(1, len(parts))],
            metadata={
                "left_items": len(left),
                "right_items": len(right),
                "resulting_slides": len(parts)
            }
        )
