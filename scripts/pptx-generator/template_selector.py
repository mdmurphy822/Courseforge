"""
Template Selector for Slideforge

Intelligent template selection based on content analysis.
Uses the master catalog's metadata to recommend the best
template for a given presentation's content.

Implements:
- Domain detection from content keywords
- Content type analysis
- Formality assessment
- Audience inference
- Weighted scoring algorithm
"""

import json
import re
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from collections import defaultdict, Counter
from enum import Enum


class Domain(Enum):
    """Content domain classifications."""
    BUSINESS = "business"
    TECHNOLOGY = "technology"
    CREATIVE = "creative"
    EDUCATION = "education"
    GENERAL = "general"


class Formality(Enum):
    """Presentation formality levels."""
    FORMAL = "formal"
    SEMI_FORMAL = "semi_formal"
    INFORMAL = "informal"


class ContentTypeCategory(Enum):
    """Categories of content types."""
    EXPLANATION = "explanation"
    EXAMPLE = "example"
    DEFINITION = "definition"
    PROCEDURE = "procedure"
    DATA_VISUALIZATION = "data_visualization"
    COMPARISON = "comparison"
    NARRATIVE = "narrative"
    EXERCISE = "exercise"


@dataclass
class ContentAnalysis:
    """Result of content analysis."""
    domain: Domain
    domain_confidence: float
    content_types: Dict[str, float]  # ContentType -> weight
    formality: Formality
    audience_hints: List[str]
    difficulty: str  # beginner, intermediate, advanced
    keywords: List[str]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "domain": self.domain.value,
            "domainConfidence": round(self.domain_confidence, 3),
            "contentTypes": self.content_types,
            "formality": self.formality.value,
            "audienceHints": self.audience_hints,
            "difficulty": self.difficulty,
            "keywords": self.keywords[:20]
        }


@dataclass
class TemplateRecommendation:
    """A template recommendation with reasoning."""
    template_id: str
    score: float
    reasons: List[str]
    breakdown: Dict[str, float]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "templateId": self.template_id,
            "score": round(self.score, 3),
            "reasons": self.reasons,
            "breakdown": {k: round(v, 3) for k, v in self.breakdown.items()}
        }


@dataclass
class LayoutAssignment:
    """Layout assignment for a slide."""
    slide_index: int
    slide_title: str
    assigned_layout: str
    reason: str


class TemplateSelector:
    """
    Intelligent template selection based on content analysis.

    Uses keyword matching, content type detection, and formality
    assessment to recommend the best-fit template.
    """

    # Domain keyword patterns
    DOMAIN_KEYWORDS: Dict[Domain, List[str]] = {
        Domain.BUSINESS: [
            "revenue", "profit", "strategy", "market", "growth", "sales",
            "roi", "kpi", "stakeholder", "budget", "forecast", "quarterly",
            "fiscal", "investment", "portfolio", "enterprise", "corporate"
        ],
        Domain.TECHNOLOGY: [
            "software", "code", "api", "system", "architecture", "database",
            "algorithm", "framework", "deploy", "cloud", "server", "data",
            "machine learning", "ai", "automation", "development", "agile"
        ],
        Domain.CREATIVE: [
            "design", "brand", "creative", "visual", "concept", "campaign",
            "marketing", "content", "story", "experience", "aesthetic",
            "color", "typography", "layout", "portfolio", "artistic"
        ],
        Domain.EDUCATION: [
            "learning", "objective", "student", "lesson", "course", "module",
            "training", "skill", "knowledge", "assessment", "quiz", "tutorial",
            "exercise", "practice", "understand", "explain", "teach"
        ]
    }

    # Content type indicator patterns
    CONTENT_TYPE_PATTERNS: Dict[ContentTypeCategory, List[str]] = {
        ContentTypeCategory.EXPLANATION: [
            r"\b(explain|understand|concept|theory|principle|overview)\b",
            r"\b(what is|how does|why|because|therefore)\b"
        ],
        ContentTypeCategory.EXAMPLE: [
            r"\b(example|instance|case study|scenario|illustration)\b",
            r"\b(for example|such as|e\.g\.|demonstrates)\b"
        ],
        ContentTypeCategory.DEFINITION: [
            r"\b(definition|means|refers to|is defined as)\b",
            r"\b(term|glossary|vocabulary|meaning)\b"
        ],
        ContentTypeCategory.PROCEDURE: [
            r"\b(step|procedure|process|method|how to)\b",
            r"\b(first|then|next|finally|instructions)\b"
        ],
        ContentTypeCategory.DATA_VISUALIZATION: [
            r"\b(data|chart|graph|statistics|percent|metric)\b",
            r"\b(increase|decrease|growth|trend|compare)\b"
        ],
        ContentTypeCategory.COMPARISON: [
            r"\b(compare|contrast|versus|vs|difference)\b",
            r"\b(pros|cons|advantages|disadvantages|better|worse)\b"
        ],
        ContentTypeCategory.NARRATIVE: [
            r"\b(story|journey|experience|case|history)\b",
            r"\b(beginning|ending|challenge|success)\b"
        ],
        ContentTypeCategory.EXERCISE: [
            r"\b(exercise|practice|activity|try|apply)\b",
            r"\b(quiz|test|assessment|check your)\b"
        ]
    }

    # Formality indicators
    FORMALITY_INDICATORS = {
        Formality.FORMAL: [
            "executive", "board", "stakeholder", "corporate", "official",
            "professional", "strategic", "compliance", "governance"
        ],
        Formality.INFORMAL: [
            "fun", "creative", "brainstorm", "workshop", "hands-on",
            "interactive", "playful", "engaging", "casual"
        ]
    }

    def __init__(self, catalog_path: Optional[str] = None):
        """
        Initialize the selector.

        Args:
            catalog_path: Path to master_catalog.json
        """
        self.catalog = self._load_catalog(catalog_path)
        self.weights = self.catalog.get("selection_weights", {
            "domain_match": 0.40,
            "content_fit": 0.35,
            "formality_match": 0.15,
            "audience_alignment": 0.10
        })

    def _load_catalog(self, catalog_path: Optional[str]) -> Dict[str, Any]:
        """Load the master catalog."""
        if catalog_path:
            path = Path(catalog_path)
        else:
            # Default path
            path = Path(__file__).parent.parent.parent / "templates" / "pptx" / "master_catalog.json"

        if path.exists():
            with open(path, 'r') as f:
                return json.load(f)

        # Fallback to minimal catalog
        return {
            "templates": {},
            "indexes": {},
            "selection_weights": {}
        }

    def analyze_content(self, presentation: Dict[str, Any]) -> ContentAnalysis:
        """
        Analyze presentation content for template matching.

        Args:
            presentation: Presentation JSON (semantic or presentation schema format)

        Returns:
            ContentAnalysis with detected characteristics
        """
        # Extract all text content
        all_text = self._extract_all_text(presentation)
        all_text_lower = all_text.lower()

        # Detect domain
        domain, domain_confidence = self._detect_domain(all_text_lower)

        # Detect content types
        content_types = self._detect_content_types(all_text_lower)

        # Assess formality
        formality = self._assess_formality(all_text_lower)

        # Infer audience
        audience_hints = self._infer_audience(all_text_lower, domain)

        # Get difficulty from profile if available
        difficulty = self._get_difficulty(presentation)

        # Extract keywords
        keywords = self._extract_keywords(all_text)

        return ContentAnalysis(
            domain=domain,
            domain_confidence=domain_confidence,
            content_types=content_types,
            formality=formality,
            audience_hints=audience_hints,
            difficulty=difficulty,
            keywords=keywords
        )

    def recommend_templates(
        self,
        presentation: Dict[str, Any],
        top_n: int = 3
    ) -> List[TemplateRecommendation]:
        """
        Return ranked template recommendations.

        Args:
            presentation: Presentation content
            top_n: Number of recommendations to return

        Returns:
            List of TemplateRecommendation objects, sorted by score
        """
        analysis = self.analyze_content(presentation)
        recommendations = []

        for template_id, template in self.catalog.get("templates", {}).items():
            score, breakdown, reasons = self._score_template(template, analysis)
            recommendations.append(TemplateRecommendation(
                template_id=template_id,
                score=score,
                reasons=reasons,
                breakdown=breakdown
            ))

        # Sort by score descending
        recommendations.sort(key=lambda r: r.score, reverse=True)

        return recommendations[:top_n]

    def select_best_template(self, presentation: Dict[str, Any]) -> str:
        """
        Select the best template for the presentation.

        Args:
            presentation: Presentation content

        Returns:
            Template ID of the best match
        """
        recommendations = self.recommend_templates(presentation, top_n=1)
        if recommendations:
            return recommendations[0].template_id
        return "minimal"  # Safe default

    def select_layouts(
        self,
        slides: List[Dict[str, Any]],
        template_id: str
    ) -> List[LayoutAssignment]:
        """
        Select optimal layouts for each slide.

        Args:
            slides: List of slide dictionaries
            template_id: Selected template ID

        Returns:
            List of LayoutAssignment objects
        """
        template = self.catalog.get("templates", {}).get(template_id, {})
        layouts = template.get("layouts", {})
        layout_types = self.catalog.get("layout_types", {})

        assignments = []

        for idx, slide in enumerate(slides):
            slide_type = slide.get("type", "content")
            title = slide.get("title", f"Slide {idx + 1}")

            # Map slide type to layout
            if slide_type in layouts:
                assigned = slide_type
                reason = f"Direct mapping for {slide_type} slide"
            else:
                # Infer best layout from content
                assigned, reason = self._infer_layout(slide, layout_types)

            assignments.append(LayoutAssignment(
                slide_index=idx,
                slide_title=title,
                assigned_layout=assigned,
                reason=reason
            ))

        return assignments

    def _extract_all_text(self, presentation: Dict[str, Any]) -> str:
        """Extract all text content from presentation."""
        texts = []

        # From metadata
        metadata = presentation.get("metadata", {})
        texts.append(metadata.get("title", ""))
        texts.append(metadata.get("subtitle", ""))
        texts.append(metadata.get("subject", ""))

        # From sections/slides
        for section in presentation.get("sections", []):
            texts.append(section.get("title", ""))
            for slide in section.get("slides", []):
                texts.append(slide.get("title", ""))
                content = slide.get("content", {})
                if isinstance(content, dict):
                    texts.extend(content.get("bullets", []))
                    texts.extend(content.get("left", []))
                    texts.extend(content.get("right", []))
                    texts.append(content.get("text", ""))
                texts.append(slide.get("notes", ""))

        # From chapters (semantic format)
        for chapter in presentation.get("chapters", []):
            texts.append(chapter.get("headingText", ""))
            for block in chapter.get("contentBlocks", []):
                if isinstance(block, dict):
                    texts.append(block.get("content", ""))
                    texts.extend(block.get("items", []))

        return " ".join(str(t) for t in texts if t)

    def _detect_domain(self, text: str) -> Tuple[Domain, float]:
        """Detect the content domain."""
        scores = defaultdict(float)

        for domain, keywords in self.DOMAIN_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text:
                    scores[domain] += 1

        if not scores:
            return Domain.GENERAL, 0.5

        best_domain = max(scores.keys(), key=lambda d: scores[d])
        total_matches = sum(scores.values())
        confidence = scores[best_domain] / total_matches if total_matches > 0 else 0.5

        return best_domain, min(1.0, confidence)

    def _detect_content_types(self, text: str) -> Dict[str, float]:
        """Detect content type distribution."""
        type_counts = defaultdict(int)
        total = 0

        for content_type, patterns in self.CONTENT_TYPE_PATTERNS.items():
            for pattern in patterns:
                matches = len(re.findall(pattern, text, re.IGNORECASE))
                type_counts[content_type.value] += matches
                total += matches

        # Normalize to weights
        if total == 0:
            return {"explanation": 1.0}  # Default

        return {
            ct: count / total
            for ct, count in type_counts.items()
            if count > 0
        }

    def _assess_formality(self, text: str) -> Formality:
        """Assess the formality level."""
        formal_score = 0
        informal_score = 0

        for indicator in self.FORMALITY_INDICATORS[Formality.FORMAL]:
            if indicator in text:
                formal_score += 1

        for indicator in self.FORMALITY_INDICATORS[Formality.INFORMAL]:
            if indicator in text:
                informal_score += 1

        if formal_score > informal_score + 2:
            return Formality.FORMAL
        elif informal_score > formal_score + 2:
            return Formality.INFORMAL
        else:
            return Formality.SEMI_FORMAL

    def _infer_audience(self, text: str, domain: Domain) -> List[str]:
        """Infer likely audience from content."""
        audiences = []

        # Domain-based inference
        domain_audiences = {
            Domain.BUSINESS: ["executives", "stakeholders"],
            Domain.TECHNOLOGY: ["developers", "engineers"],
            Domain.CREATIVE: ["creative_teams", "designers"],
            Domain.EDUCATION: ["students", "learners"],
            Domain.GENERAL: ["general"]
        }

        audiences.extend(domain_audiences.get(domain, ["general"]))

        # Keyword-based inference
        if any(word in text for word in ["executive", "board", "ceo", "leadership"]):
            if "executives" not in audiences:
                audiences.append("executives")
        if any(word in text for word in ["student", "learner", "beginner"]):
            if "students" not in audiences:
                audiences.append("students")

        return audiences

    def _get_difficulty(self, presentation: Dict[str, Any]) -> str:
        """Get difficulty level from presentation data."""
        # Check content profiles
        profiles = presentation.get("contentProfiles", {})
        aggregate = profiles.get("aggregate", {})

        if aggregate:
            return aggregate.get("difficultyLevel", "intermediate")

        # Default
        return "intermediate"

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract significant keywords from text."""
        # Simple keyword extraction
        words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())

        # Filter common words
        stopwords = {
            'that', 'this', 'with', 'from', 'have', 'will', 'your',
            'about', 'which', 'when', 'where', 'what', 'they', 'been',
            'their', 'more', 'some', 'these', 'other', 'into', 'also'
        }

        filtered = [w for w in words if w not in stopwords]

        # Get most common
        counter = Counter(filtered)
        return [word for word, _ in counter.most_common(30)]

    def _score_template(
        self,
        template: Dict[str, Any],
        analysis: ContentAnalysis
    ) -> Tuple[float, Dict[str, float], List[str]]:
        """
        Score a template against content analysis.

        Returns:
            Tuple of (total_score, breakdown, reasons)
        """
        breakdown = {}
        reasons = []

        # Domain match
        template_domain = template.get("classification", {}).get("domain", "general")
        if template_domain == analysis.domain.value:
            breakdown["domain"] = 1.0
            reasons.append(f"Excellent domain match: {template_domain}")
        elif template_domain == "general":
            breakdown["domain"] = 0.7
            reasons.append("General-purpose template suitable for any domain")
        else:
            breakdown["domain"] = 0.3
            reasons.append(f"Domain mismatch: template is for {template_domain}")

        # Content fit
        content_fit = template.get("content_fit", {})
        fit_score = 0.0
        total_weight = 0.0

        for content_type, weight in analysis.content_types.items():
            type_fit = content_fit.get(content_type, 0.5)
            fit_score += type_fit * weight
            total_weight += weight

        breakdown["content_fit"] = fit_score / total_weight if total_weight > 0 else 0.5

        if breakdown["content_fit"] >= 0.8:
            reasons.append("Strong content type fit")
        elif breakdown["content_fit"] >= 0.6:
            reasons.append("Good content type compatibility")

        # Formality match
        template_formality = template.get("classification", {}).get("formality", "semi_formal")
        if template_formality == analysis.formality.value:
            breakdown["formality"] = 1.0
            reasons.append(f"Formality match: {template_formality}")
        elif (template_formality == "semi_formal" or
              analysis.formality == Formality.SEMI_FORMAL):
            breakdown["formality"] = 0.7
        else:
            breakdown["formality"] = 0.4

        # Audience alignment
        template_audience = set(template.get("classification", {}).get("audience", []))
        analysis_audience = set(analysis.audience_hints)
        overlap = len(template_audience & analysis_audience)

        if overlap > 0:
            breakdown["audience"] = min(1.0, overlap / len(analysis_audience))
            reasons.append(f"Audience alignment: {overlap} matches")
        else:
            breakdown["audience"] = 0.3

        # Calculate weighted total
        total_score = (
            self.weights.get("domain_match", 0.4) * breakdown["domain"] +
            self.weights.get("content_fit", 0.35) * breakdown["content_fit"] +
            self.weights.get("formality_match", 0.15) * breakdown["formality"] +
            self.weights.get("audience_alignment", 0.1) * breakdown["audience"]
        )

        return total_score, breakdown, reasons

    def _infer_layout(
        self,
        slide: Dict[str, Any],
        layout_types: Dict[str, Any]
    ) -> Tuple[str, str]:
        """Infer the best layout for a slide."""
        content = slide.get("content", {})

        # Check for two-column indicators
        if content.get("left") and content.get("right"):
            if content.get("left_title") or content.get("right_title"):
                return "comparison", "Has comparison columns with headers"
            return "two_content", "Has two-column content"

        # Check for quote
        if content.get("text") and content.get("attribution"):
            return "quote", "Has quote text with attribution"

        # Check for image
        if content.get("image_path"):
            return "image", "Has image content"

        # Check bullet count for content
        bullets = content.get("bullets", [])
        if bullets:
            return "content", f"Has {len(bullets)} bullet points"

        # Default
        return "content", "Default content layout"


# Convenience function
def select_template(
    presentation: Dict[str, Any],
    catalog_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Select the best template for a presentation.

    Args:
        presentation: Presentation content
        catalog_path: Path to master_catalog.json

    Returns:
        Dictionary with template_id, analysis, and recommendations
    """
    selector = TemplateSelector(catalog_path)
    analysis = selector.analyze_content(presentation)
    recommendations = selector.recommend_templates(presentation)

    return {
        "selected_template": recommendations[0].template_id if recommendations else "minimal",
        "analysis": analysis.to_dict(),
        "recommendations": [r.to_dict() for r in recommendations]
    }
