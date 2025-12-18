"""
Notes Generator for Slideforge

Generates speaker notes from full content that was condensed for slides.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum
import re


class NoteStyle(Enum):
    """Styles for speaker notes."""
    DETAILED = "detailed"      # Full content with context
    SUMMARY = "summary"        # Key points summary
    TALKING_POINTS = "talking_points"  # Bullet points for speaker
    SCRIPT = "script"          # Full presentation script
    MINIMAL = "minimal"        # Just reminders


@dataclass
class SpeakerNote:
    """A speaker note for a slide."""
    slide_id: str
    content: str
    style: NoteStyle
    source_content: str = ""
    key_points: List[str] = field(default_factory=list)
    timing_hint: Optional[str] = None
    transitions: Dict[str, str] = field(default_factory=dict)  # prev/next hints


class NotesGenerator:
    """
    Generates speaker notes from full content.

    When slide content is condensed to meet the 6x6 rule,
    the full content becomes speaker notes.
    """

    # Templates for different note styles
    TEMPLATES = {
        NoteStyle.DETAILED: """
{source_header}

{full_content}

{key_points_section}

{transition_notes}
""",
        NoteStyle.SUMMARY: """
Key Points:
{key_points}

Additional Context:
{context_summary}
""",
        NoteStyle.TALKING_POINTS: """
Talking Points:
{talking_points}

Remember to mention:
{reminders}
""",
        NoteStyle.SCRIPT: """
[INTRODUCTION]
{intro}

[MAIN CONTENT]
{main_content}

[KEY TAKEAWAYS]
{takeaways}

[TRANSITION]
{transition}
""",
        NoteStyle.MINIMAL: """
• {key_point_1}
• {key_point_2}
• {key_point_3}
"""
    }

    def __init__(self, default_style: NoteStyle = NoteStyle.TALKING_POINTS):
        """Initialize with default note style."""
        self.default_style = default_style

    def generate_notes(
        self,
        slide_content: Dict[str, Any],
        original_content: Any,
        style: Optional[NoteStyle] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> SpeakerNote:
        """
        Generate speaker notes for a slide.

        Args:
            slide_content: The condensed slide content
            original_content: The full original content
            style: Note style to use
            context: Optional context (prev/next slides)

        Returns:
            SpeakerNote with generated content
        """
        style = style or self.default_style

        # Extract source text
        source_text = self._extract_source_text(original_content)

        # Extract key points
        key_points = self._extract_key_points(original_content, slide_content)

        # Generate notes based on style
        if style == NoteStyle.DETAILED:
            notes_content = self._generate_detailed(
                slide_content, source_text, key_points, context
            )
        elif style == NoteStyle.SUMMARY:
            notes_content = self._generate_summary(
                slide_content, source_text, key_points
            )
        elif style == NoteStyle.TALKING_POINTS:
            notes_content = self._generate_talking_points(
                slide_content, source_text, key_points
            )
        elif style == NoteStyle.SCRIPT:
            notes_content = self._generate_script(
                slide_content, source_text, key_points, context
            )
        else:  # MINIMAL
            notes_content = self._generate_minimal(key_points)

        # Generate transitions
        transitions = self._generate_transitions(slide_content, context)

        return SpeakerNote(
            slide_id=slide_content.get("id", ""),
            content=notes_content.strip(),
            style=style,
            source_content=source_text,
            key_points=key_points,
            timing_hint=self._estimate_timing(notes_content),
            transitions=transitions
        )

    def generate_notes_batch(
        self,
        slides: List[Dict[str, Any]],
        original_contents: List[Any],
        style: Optional[NoteStyle] = None
    ) -> List[SpeakerNote]:
        """
        Generate notes for multiple slides with context awareness.

        Args:
            slides: List of slide content dictionaries
            original_contents: List of original content for each slide
            style: Note style to use

        Returns:
            List of SpeakerNotes
        """
        notes = []

        for i, (slide, original) in enumerate(zip(slides, original_contents)):
            context = {
                "previous": slides[i-1] if i > 0 else None,
                "next": slides[i+1] if i < len(slides) - 1 else None,
                "position": i,
                "total_slides": len(slides),
                "is_first": i == 0,
                "is_last": i == len(slides) - 1
            }

            note = self.generate_notes(slide, original, style, context)
            notes.append(note)

        return notes

    def _extract_source_text(self, original: Any) -> str:
        """Extract text from original content."""
        if isinstance(original, str):
            return original

        if isinstance(original, dict):
            parts = []

            if "text" in original:
                parts.append(original["text"])
            if "content" in original:
                parts.append(self._extract_source_text(original["content"]))
            if "bullets" in original:
                parts.extend(original["bullets"])
            if "items" in original:
                parts.extend(str(item) for item in original["items"])
            if "paragraphs" in original:
                parts.extend(original["paragraphs"])

            return "\n".join(str(p) for p in parts if p)

        if isinstance(original, list):
            return "\n".join(
                self._extract_source_text(item) for item in original
            )

        return str(original) if original else ""

    def _extract_key_points(
        self,
        original: Any,
        slide_content: Dict[str, Any]
    ) -> List[str]:
        """Extract key points from content."""
        key_points = []

        # Get slide bullets as starting point
        slide_bullets = slide_content.get("content", {}).get("bullets", [])

        # These are the key points shown on slide
        key_points.extend(slide_bullets)

        # Find additional points from original that weren't included
        original_text = self._extract_source_text(original)

        # Look for important patterns
        important_patterns = [
            r'(?:important|key|note|remember|critical):\s*([^.!?]+[.!?])',
            r'(?:in summary|to summarize|in conclusion):\s*([^.!?]+[.!?])',
            r'(?:the main|the key|the important)\s+(?:point|idea|concept)\s+is\s+([^.!?]+[.!?])'
        ]

        for pattern in important_patterns:
            matches = re.findall(pattern, original_text, re.IGNORECASE)
            for match in matches:
                if match not in key_points:
                    key_points.append(match.strip())

        return key_points[:10]  # Limit to 10 key points

    def _generate_detailed(
        self,
        slide_content: Dict[str, Any],
        source_text: str,
        key_points: List[str],
        context: Optional[Dict[str, Any]]
    ) -> str:
        """Generate detailed speaker notes."""
        parts = []

        # Source header
        title = slide_content.get("title", "Slide")
        parts.append(f"=== {title} ===\n")

        # Full content
        if source_text:
            parts.append("Full Content:")
            parts.append(source_text)
            parts.append("")

        # Key points section
        if key_points:
            parts.append("Key Points to Emphasize:")
            for i, point in enumerate(key_points, 1):
                parts.append(f"  {i}. {point}")
            parts.append("")

        # Transition notes
        if context:
            transition = self._generate_transition_text(context)
            if transition:
                parts.append(f"Transition: {transition}")

        return "\n".join(parts)

    def _generate_summary(
        self,
        slide_content: Dict[str, Any],
        source_text: str,
        key_points: List[str]
    ) -> str:
        """Generate summary speaker notes."""
        parts = []

        # Key points
        if key_points:
            parts.append("Key Points:")
            for point in key_points[:5]:
                parts.append(f"• {point}")
            parts.append("")

        # Context summary (condensed source)
        if source_text:
            summary = self._summarize_text(source_text, max_sentences=3)
            if summary:
                parts.append("Additional Context:")
                parts.append(summary)

        return "\n".join(parts)

    def _generate_talking_points(
        self,
        slide_content: Dict[str, Any],
        source_text: str,
        key_points: List[str]
    ) -> str:
        """Generate talking points for speaker."""
        parts = []

        # Main talking points
        parts.append("Talking Points:")
        for point in key_points[:5]:
            parts.append(f"→ {point}")
        parts.append("")

        # Reminders from original content
        reminders = self._extract_reminders(source_text, key_points)
        if reminders:
            parts.append("Remember to mention:")
            for reminder in reminders[:3]:
                parts.append(f"• {reminder}")

        return "\n".join(parts)

    def _generate_script(
        self,
        slide_content: Dict[str, Any],
        source_text: str,
        key_points: List[str],
        context: Optional[Dict[str, Any]]
    ) -> str:
        """Generate full presentation script."""
        parts = []
        title = slide_content.get("title", "")

        # Introduction
        parts.append("[INTRODUCTION]")
        if context and context.get("is_first"):
            parts.append(f"Welcome. Let's begin with {title}.")
        else:
            parts.append(f"Now let's discuss {title}.")
        parts.append("")

        # Main content
        parts.append("[MAIN CONTENT]")
        if source_text:
            parts.append(source_text[:500])  # First 500 chars
        parts.append("")

        # Key takeaways
        parts.append("[KEY TAKEAWAYS]")
        for point in key_points[:3]:
            parts.append(f"• {point}")
        parts.append("")

        # Transition
        parts.append("[TRANSITION]")
        if context:
            transition = self._generate_transition_text(context)
            parts.append(transition or "Let's move on to the next topic.")

        return "\n".join(parts)

    def _generate_minimal(self, key_points: List[str]) -> str:
        """Generate minimal reminder notes."""
        points = key_points[:3] if key_points else ["Main point", "Supporting point", "Conclusion"]
        return "\n".join(f"• {point}" for point in points)

    def _generate_transitions(
        self,
        slide_content: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, str]:
        """Generate transition hints."""
        transitions = {}

        if not context:
            return transitions

        prev_slide = context.get("previous")
        next_slide = context.get("next")

        if prev_slide:
            prev_title = prev_slide.get("title", "previous topic")
            transitions["from_previous"] = f"Building on {prev_title}..."

        if next_slide:
            next_title = next_slide.get("title", "next topic")
            transitions["to_next"] = f"This leads us to {next_title}..."

        return transitions

    def _generate_transition_text(self, context: Dict[str, Any]) -> str:
        """Generate transition text based on context."""
        if context.get("is_last"):
            return "This concludes our presentation."

        next_slide = context.get("next")
        if next_slide:
            next_title = next_slide.get("title", "the next topic")
            return f"Next, we'll explore {next_title}."

        return ""

    def _summarize_text(self, text: str, max_sentences: int = 3) -> str:
        """Create a brief summary of text."""
        # Split into sentences
        sentences = re.split(r'(?<=[.!?])\s+', text)

        if len(sentences) <= max_sentences:
            return text

        # Take first and last sentences, plus middle if room
        summary_sentences = [sentences[0]]

        if max_sentences >= 3 and len(sentences) >= 3:
            mid = len(sentences) // 2
            summary_sentences.append(sentences[mid])

        if max_sentences >= 2:
            summary_sentences.append(sentences[-1])

        return " ".join(summary_sentences)

    def _extract_reminders(
        self,
        source_text: str,
        already_included: List[str]
    ) -> List[str]:
        """Extract additional reminders not in key points."""
        reminders = []

        # Look for examples
        example_pattern = r'(?:for example|such as|e\.g\.|i\.e\.)[,:]?\s*([^.!?]+[.!?]?)'
        examples = re.findall(example_pattern, source_text, re.IGNORECASE)

        for example in examples[:2]:
            clean = example.strip()
            if clean and clean not in already_included:
                reminders.append(f"Example: {clean}")

        # Look for statistics/numbers
        stat_pattern = r'(\d+(?:\.\d+)?%?\s+(?:of|percent|people|users|companies)[^.!?]*[.!?])'
        stats = re.findall(stat_pattern, source_text, re.IGNORECASE)

        for stat in stats[:2]:
            if stat not in already_included:
                reminders.append(stat.strip())

        return reminders

    def _estimate_timing(self, notes_content: str) -> str:
        """Estimate speaking time for notes."""
        # Average speaking rate: 150 words per minute
        word_count = len(notes_content.split())
        minutes = word_count / 150

        if minutes < 1:
            return "< 1 minute"
        elif minutes < 2:
            return "1-2 minutes"
        elif minutes < 3:
            return "2-3 minutes"
        else:
            return f"~{int(minutes)} minutes"

    def combine_notes(self, notes: List[SpeakerNote]) -> str:
        """Combine multiple notes into a single document."""
        parts = []

        for i, note in enumerate(notes, 1):
            parts.append(f"--- Slide {i} ---")
            parts.append(note.content)
            if note.timing_hint:
                parts.append(f"[Timing: {note.timing_hint}]")
            parts.append("")

        return "\n".join(parts)
