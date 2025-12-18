"""
Semantic Validator for Slideforge (Level 3)

Validates presentation quality, completeness, and pedagogical effectiveness.
Goes beyond schema compliance to ensure meaningful content.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Set
from enum import Enum
import re


class IssueCategory(Enum):
    """Categories of quality issues."""
    CONTENT = "content"
    DESIGN = "design"
    ACCESSIBILITY = "accessibility"
    PEDAGOGY = "pedagogy"
    CONSISTENCY = "consistency"
    COMPLETENESS = "completeness"


class IssueSeverity(Enum):
    """Severity levels for quality issues."""
    CRITICAL = "critical"
    MAJOR = "major"
    MINOR = "minor"
    SUGGESTION = "suggestion"


@dataclass
class QualityIssue:
    """A quality/semantic issue."""
    category: IssueCategory
    severity: IssueSeverity
    message: str
    location: str
    suggestion: str = ""
    rule_id: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "category": self.category.value,
            "severity": self.severity.value,
            "message": self.message,
            "location": self.location,
            "suggestion": self.suggestion,
            "ruleId": self.rule_id
        }


@dataclass
class QualityMetrics:
    """Quality metrics for a presentation."""
    # Content metrics
    total_slides: int = 0
    total_sections: int = 0
    slides_with_notes: int = 0
    slides_with_titles: int = 0
    empty_slides: int = 0

    # 6x6 compliance
    six_six_violations: int = 0
    max_bullets_per_slide: int = 0
    avg_bullets_per_slide: float = 0.0
    max_words_per_bullet: int = 0
    avg_words_per_bullet: float = 0.0

    # Variety metrics
    slide_type_count: int = 0
    slide_types_used: Set[str] = field(default_factory=set)

    # Calculated scores
    notes_coverage: float = 0.0
    title_coverage: float = 0.0
    six_six_score: float = 0.0
    variety_score: float = 0.0
    overall_score: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "totalSlides": self.total_slides,
            "totalSections": self.total_sections,
            "slidesWithNotes": self.slides_with_notes,
            "slidesWithTitles": self.slides_with_titles,
            "emptySlides": self.empty_slides,
            "sixSixViolations": self.six_six_violations,
            "maxBulletsPerSlide": self.max_bullets_per_slide,
            "avgBulletsPerSlide": round(self.avg_bullets_per_slide, 2),
            "maxWordsPerBullet": self.max_words_per_bullet,
            "avgWordsPerBullet": round(self.avg_words_per_bullet, 2),
            "slideTypeCount": self.slide_type_count,
            "slideTypesUsed": list(self.slide_types_used),
            "notesCoverage": round(self.notes_coverage, 2),
            "titleCoverage": round(self.title_coverage, 2),
            "sixSixScore": round(self.six_six_score, 2),
            "varietyScore": round(self.variety_score, 2),
            "overallScore": round(self.overall_score, 2)
        }


@dataclass
class SemanticValidationResult:
    """Result of semantic validation."""
    valid: bool
    issues: List[QualityIssue] = field(default_factory=list)
    metrics: QualityMetrics = field(default_factory=QualityMetrics)
    recommendations: List[str] = field(default_factory=list)

    @property
    def critical_issues(self) -> List[QualityIssue]:
        """Get critical issues only."""
        return [i for i in self.issues if i.severity == IssueSeverity.CRITICAL]

    @property
    def major_issues(self) -> List[QualityIssue]:
        """Get major issues only."""
        return [i for i in self.issues if i.severity == IssueSeverity.MAJOR]

    @property
    def issue_count(self) -> int:
        """Total issue count."""
        return len(self.issues)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "valid": self.valid,
            "issues": [i.to_dict() for i in self.issues],
            "metrics": self.metrics.to_dict(),
            "recommendations": self.recommendations,
            "summary": {
                "totalIssues": self.issue_count,
                "criticalCount": len(self.critical_issues),
                "majorCount": len(self.major_issues),
                "overallScore": self.metrics.overall_score
            }
        }


class SemanticValidator:
    """
    Level 3 Validator: Quality and Completeness

    Validates:
    - 6x6 rule compliance
    - Speaker notes coverage
    - Slide type variety
    - Content quality
    - Accessibility considerations
    - Pedagogical effectiveness
    """

    # Quality thresholds
    THRESHOLDS = {
        "min_notes_coverage": 0.80,  # 80% of slides should have notes
        "min_title_coverage": 0.95,  # 95% of slides should have titles
        "min_slide_variety": 3,       # At least 3 different slide types
        "min_overall_score": 70,      # Minimum passing score
        "max_bullets": 6,
        "max_words_per_bullet": 6,
        "max_chars_per_bullet": 100,
        "min_slides_per_section": 2,
        "max_slides_per_section": 15,
        "max_consecutive_same_type": 3
    }

    def __init__(self, thresholds: Optional[Dict[str, Any]] = None):
        """
        Initialize validator with optional custom thresholds.

        Args:
            thresholds: Custom threshold values
        """
        self.thresholds = dict(self.THRESHOLDS)
        if thresholds:
            self.thresholds.update(thresholds)

    def validate(
        self,
        presentation: Dict[str, Any],
        strict: bool = False
    ) -> SemanticValidationResult:
        """
        Perform semantic validation on presentation.

        Args:
            presentation: Presentation dictionary
            strict: If True, minor issues also fail validation

        Returns:
            SemanticValidationResult
        """
        issues = []
        recommendations = []

        # Calculate metrics
        metrics = self._calculate_metrics(presentation)

        # Run all quality checks
        issues.extend(self._check_six_six_compliance(presentation))
        issues.extend(self._check_notes_coverage(presentation, metrics))
        issues.extend(self._check_slide_variety(presentation, metrics))
        issues.extend(self._check_content_quality(presentation))
        issues.extend(self._check_accessibility(presentation))
        issues.extend(self._check_consistency(presentation))
        issues.extend(self._check_section_balance(presentation))

        # Generate recommendations
        recommendations = self._generate_recommendations(metrics, issues)

        # Calculate scores
        metrics = self._calculate_scores(metrics, issues)

        # Determine validity
        if strict:
            is_valid = len(issues) == 0
        else:
            critical_or_major = [
                i for i in issues
                if i.severity in [IssueSeverity.CRITICAL, IssueSeverity.MAJOR]
            ]
            is_valid = len(critical_or_major) == 0 and metrics.overall_score >= self.thresholds["min_overall_score"]

        return SemanticValidationResult(
            valid=is_valid,
            issues=issues,
            metrics=metrics,
            recommendations=recommendations
        )

    def _calculate_metrics(self, presentation: Dict[str, Any]) -> QualityMetrics:
        """Calculate quality metrics from presentation."""
        metrics = QualityMetrics()

        sections = presentation.get("sections", [])
        metrics.total_sections = len(sections)

        all_bullets = []
        slide_types = set()

        for section in sections:
            for slide in section.get("slides", []):
                metrics.total_slides += 1

                # Track slide type
                slide_type = slide.get("type", "content")
                slide_types.add(slide_type)

                # Check for notes
                if slide.get("notes"):
                    metrics.slides_with_notes += 1

                # Check for title
                if slide.get("title"):
                    metrics.slides_with_titles += 1

                # Check for empty content
                if self._is_empty_slide(slide):
                    metrics.empty_slides += 1

                # Collect bullets for analysis
                content = slide.get("content", {})
                bullets = content.get("bullets", [])
                if bullets:
                    all_bullets.extend(bullets)
                    if len(bullets) > metrics.max_bullets_per_slide:
                        metrics.max_bullets_per_slide = len(bullets)

        metrics.slide_types_used = slide_types
        metrics.slide_type_count = len(slide_types)

        # Calculate averages
        if metrics.total_slides > 0:
            metrics.notes_coverage = metrics.slides_with_notes / metrics.total_slides
            metrics.title_coverage = metrics.slides_with_titles / metrics.total_slides

        # Bullet analysis
        if all_bullets:
            total_bullets = len(all_bullets)
            metrics.avg_bullets_per_slide = total_bullets / metrics.total_slides if metrics.total_slides > 0 else 0

            word_counts = [len(b.split()) for b in all_bullets]
            metrics.max_words_per_bullet = max(word_counts) if word_counts else 0
            metrics.avg_words_per_bullet = sum(word_counts) / len(word_counts) if word_counts else 0

        return metrics

    def _calculate_scores(
        self,
        metrics: QualityMetrics,
        issues: List[QualityIssue]
    ) -> QualityMetrics:
        """Calculate quality scores."""
        # 6x6 Score (0-100)
        if metrics.total_slides > 0:
            violation_rate = metrics.six_six_violations / metrics.total_slides
            metrics.six_six_score = max(0, 100 - (violation_rate * 100))
        else:
            metrics.six_six_score = 100

        # Notes coverage score (0-100)
        metrics.notes_coverage = metrics.notes_coverage  # Already 0-1

        # Variety score (0-100)
        target_types = 5
        metrics.variety_score = min(100, (metrics.slide_type_count / target_types) * 100)

        # Overall score calculation
        weights = {
            "six_six": 0.30,
            "notes": 0.25,
            "variety": 0.15,
            "titles": 0.15,
            "issues": 0.15
        }

        # Issue penalty
        issue_penalty = 0
        for issue in issues:
            if issue.severity == IssueSeverity.CRITICAL:
                issue_penalty += 20
            elif issue.severity == IssueSeverity.MAJOR:
                issue_penalty += 10
            elif issue.severity == IssueSeverity.MINOR:
                issue_penalty += 3
            else:  # SUGGESTION
                issue_penalty += 1

        issue_score = max(0, 100 - issue_penalty)

        metrics.overall_score = (
            weights["six_six"] * metrics.six_six_score +
            weights["notes"] * (metrics.notes_coverage * 100) +
            weights["variety"] * metrics.variety_score +
            weights["titles"] * (metrics.title_coverage * 100) +
            weights["issues"] * issue_score
        )

        return metrics

    def _check_six_six_compliance(
        self,
        presentation: Dict[str, Any]
    ) -> List[QualityIssue]:
        """Check 6x6 rule compliance."""
        issues = []
        max_bullets = self.thresholds["max_bullets"]
        max_words = self.thresholds["max_words_per_bullet"]
        max_chars = self.thresholds["max_chars_per_bullet"]

        for section_idx, section in enumerate(presentation.get("sections", [])):
            for slide_idx, slide in enumerate(section.get("slides", [])):
                location = f"sections[{section_idx}].slides[{slide_idx}]"
                content = slide.get("content", {})
                bullets = content.get("bullets", [])

                # Check bullet count
                if len(bullets) > max_bullets:
                    issues.append(QualityIssue(
                        category=IssueCategory.DESIGN,
                        severity=IssueSeverity.MAJOR,
                        message=f"Slide has {len(bullets)} bullets (max {max_bullets})",
                        location=location,
                        suggestion=f"Split into {(len(bullets) + max_bullets - 1) // max_bullets} slides",
                        rule_id="SIX_SIX_BULLET_COUNT"
                    ))

                # Check each bullet
                for i, bullet in enumerate(bullets):
                    word_count = len(bullet.split())
                    char_count = len(bullet)

                    if word_count > max_words:
                        issues.append(QualityIssue(
                            category=IssueCategory.DESIGN,
                            severity=IssueSeverity.MINOR,
                            message=f"Bullet {i+1} has {word_count} words (max {max_words})",
                            location=f"{location}.content.bullets[{i}]",
                            suggestion="Shorten to key points only",
                            rule_id="SIX_SIX_WORD_COUNT"
                        ))

                    if char_count > max_chars:
                        issues.append(QualityIssue(
                            category=IssueCategory.DESIGN,
                            severity=IssueSeverity.SUGGESTION,
                            message=f"Bullet {i+1} has {char_count} characters (max {max_chars})",
                            location=f"{location}.content.bullets[{i}]",
                            suggestion="Consider using shorter phrasing",
                            rule_id="SIX_SIX_CHAR_COUNT"
                        ))

        return issues

    def _check_notes_coverage(
        self,
        presentation: Dict[str, Any],
        metrics: QualityMetrics
    ) -> List[QualityIssue]:
        """Check speaker notes coverage."""
        issues = []
        min_coverage = self.thresholds["min_notes_coverage"]

        if metrics.notes_coverage < min_coverage:
            missing = metrics.total_slides - metrics.slides_with_notes
            issues.append(QualityIssue(
                category=IssueCategory.COMPLETENESS,
                severity=IssueSeverity.MAJOR,
                message=f"Only {metrics.notes_coverage:.0%} of slides have notes (target: {min_coverage:.0%})",
                location="presentation",
                suggestion=f"Add speaker notes to {missing} slides",
                rule_id="NOTES_COVERAGE"
            ))

        # Find specific slides without notes
        for section_idx, section in enumerate(presentation.get("sections", [])):
            for slide_idx, slide in enumerate(section.get("slides", [])):
                if not slide.get("notes") and slide.get("type") not in ["blank"]:
                    issues.append(QualityIssue(
                        category=IssueCategory.COMPLETENESS,
                        severity=IssueSeverity.SUGGESTION,
                        message="Slide has no speaker notes",
                        location=f"sections[{section_idx}].slides[{slide_idx}]",
                        suggestion="Add speaker notes to help presenters",
                        rule_id="MISSING_NOTES"
                    ))

        return issues

    def _check_slide_variety(
        self,
        presentation: Dict[str, Any],
        metrics: QualityMetrics
    ) -> List[QualityIssue]:
        """Check slide type variety."""
        issues = []
        min_variety = self.thresholds["min_slide_variety"]
        max_consecutive = self.thresholds["max_consecutive_same_type"]

        if metrics.slide_type_count < min_variety:
            issues.append(QualityIssue(
                category=IssueCategory.DESIGN,
                severity=IssueSeverity.MINOR,
                message=f"Only {metrics.slide_type_count} slide types used (recommend at least {min_variety})",
                location="presentation",
                suggestion="Use comparison, quote, or image slides for visual variety",
                rule_id="SLIDE_VARIETY"
            ))

        # Check for too many consecutive same-type slides
        for section_idx, section in enumerate(presentation.get("sections", [])):
            slides = section.get("slides", [])
            consecutive_count = 1
            last_type = None

            for slide_idx, slide in enumerate(slides):
                current_type = slide.get("type", "content")

                if current_type == last_type:
                    consecutive_count += 1
                    if consecutive_count > max_consecutive:
                        issues.append(QualityIssue(
                            category=IssueCategory.DESIGN,
                            severity=IssueSeverity.SUGGESTION,
                            message=f"{consecutive_count} consecutive '{current_type}' slides",
                            location=f"sections[{section_idx}].slides[{slide_idx}]",
                            suggestion="Consider breaking up with different slide types",
                            rule_id="CONSECUTIVE_SAME_TYPE"
                        ))
                else:
                    consecutive_count = 1

                last_type = current_type

        return issues

    def _check_content_quality(
        self,
        presentation: Dict[str, Any]
    ) -> List[QualityIssue]:
        """Check content quality issues."""
        issues = []

        for section_idx, section in enumerate(presentation.get("sections", [])):
            for slide_idx, slide in enumerate(section.get("slides", [])):
                location = f"sections[{section_idx}].slides[{slide_idx}]"
                title = slide.get("title", "")
                content = slide.get("content", {})

                # Check for vague titles
                vague_patterns = [
                    r'^overview$', r'^introduction$', r'^summary$',
                    r'^continued$', r'^more\s+', r'^misc'
                ]
                if title:
                    for pattern in vague_patterns:
                        if re.match(pattern, title.lower()):
                            issues.append(QualityIssue(
                                category=IssueCategory.CONTENT,
                                severity=IssueSeverity.SUGGESTION,
                                message=f"Title '{title}' is generic",
                                location=location,
                                suggestion="Use a more specific, descriptive title",
                                rule_id="VAGUE_TITLE"
                            ))
                            break

                # Check for bullet redundancy
                bullets = content.get("bullets", [])
                if len(bullets) >= 2:
                    bullet_lower = [b.lower() for b in bullets]
                    for i, b1 in enumerate(bullet_lower):
                        for j, b2 in enumerate(bullet_lower[i+1:], i+1):
                            similarity = self._simple_similarity(b1, b2)
                            if similarity > 0.8:
                                issues.append(QualityIssue(
                                    category=IssueCategory.CONTENT,
                                    severity=IssueSeverity.MINOR,
                                    message=f"Bullets {i+1} and {j+1} appear similar",
                                    location=f"{location}.content.bullets",
                                    suggestion="Combine or differentiate similar points",
                                    rule_id="SIMILAR_BULLETS"
                                ))

        return issues

    def _check_accessibility(
        self,
        presentation: Dict[str, Any]
    ) -> List[QualityIssue]:
        """Check accessibility considerations."""
        issues = []

        for section_idx, section in enumerate(presentation.get("sections", [])):
            for slide_idx, slide in enumerate(section.get("slides", [])):
                location = f"sections[{section_idx}].slides[{slide_idx}]"
                slide_type = slide.get("type", "content")
                content = slide.get("content", {})

                # Check for image alt text
                if slide_type == "image":
                    if not content.get("alt_text"):
                        issues.append(QualityIssue(
                            category=IssueCategory.ACCESSIBILITY,
                            severity=IssueSeverity.MAJOR,
                            message="Image slide missing alt text",
                            location=location,
                            suggestion="Add descriptive alt text for accessibility",
                            rule_id="MISSING_ALT_TEXT"
                        ))

                # Check for title presence (screen reader navigation)
                if slide_type not in ["blank", "title"]:
                    if not slide.get("title"):
                        issues.append(QualityIssue(
                            category=IssueCategory.ACCESSIBILITY,
                            severity=IssueSeverity.MINOR,
                            message="Slide missing title (affects screen reader navigation)",
                            location=location,
                            suggestion="Add a title for accessibility",
                            rule_id="MISSING_TITLE_ACCESSIBILITY"
                        ))

        return issues

    def _check_consistency(
        self,
        presentation: Dict[str, Any]
    ) -> List[QualityIssue]:
        """Check consistency issues."""
        issues = []

        # Check section naming consistency
        sections = presentation.get("sections", [])
        section_titles = [s.get("title", "") for s in sections]

        # Check for numbered vs non-numbered sections
        numbered = [t for t in section_titles if re.match(r'^\d+[\.\):]', t)]
        if 0 < len(numbered) < len(section_titles):
            issues.append(QualityIssue(
                category=IssueCategory.CONSISTENCY,
                severity=IssueSeverity.SUGGESTION,
                message="Inconsistent section numbering",
                location="sections",
                suggestion="Either number all sections or none",
                rule_id="INCONSISTENT_NUMBERING"
            ))

        return issues

    def _check_section_balance(
        self,
        presentation: Dict[str, Any]
    ) -> List[QualityIssue]:
        """Check section balance and size."""
        issues = []
        min_slides = self.thresholds["min_slides_per_section"]
        max_slides = self.thresholds["max_slides_per_section"]

        for section_idx, section in enumerate(presentation.get("sections", [])):
            slides = section.get("slides", [])
            slide_count = len(slides)
            location = f"sections[{section_idx}]"

            if slide_count < min_slides and section.get("title"):
                issues.append(QualityIssue(
                    category=IssueCategory.DESIGN,
                    severity=IssueSeverity.SUGGESTION,
                    message=f"Section has only {slide_count} slide(s)",
                    location=location,
                    suggestion="Consider merging with adjacent section",
                    rule_id="SECTION_TOO_SMALL"
                ))

            if slide_count > max_slides:
                issues.append(QualityIssue(
                    category=IssueCategory.DESIGN,
                    severity=IssueSeverity.MINOR,
                    message=f"Section has {slide_count} slides (recommend max {max_slides})",
                    location=location,
                    suggestion="Consider splitting into subsections",
                    rule_id="SECTION_TOO_LARGE"
                ))

        return issues

    def _generate_recommendations(
        self,
        metrics: QualityMetrics,
        issues: List[QualityIssue]
    ) -> List[str]:
        """Generate improvement recommendations."""
        recommendations = []

        # Notes recommendations
        if metrics.notes_coverage < 0.80:
            recommendations.append(
                f"Add speaker notes to improve presenter experience "
                f"(current coverage: {metrics.notes_coverage:.0%})"
            )

        # Variety recommendations
        if metrics.slide_type_count < 3:
            recommendations.append(
                "Use more diverse slide types (comparison, quote, image) "
                "to maintain audience engagement"
            )

        # 6x6 recommendations
        if metrics.six_six_violations > 0:
            recommendations.append(
                f"Address {metrics.six_six_violations} 6x6 rule violations "
                "to improve readability"
            )

        # Issue-based recommendations
        issue_categories = {}
        for issue in issues:
            cat = issue.category.value
            issue_categories[cat] = issue_categories.get(cat, 0) + 1

        if issue_categories.get("accessibility", 0) > 0:
            recommendations.append(
                "Review accessibility issues to ensure presentation is usable by all"
            )

        if metrics.empty_slides > 0:
            recommendations.append(
                f"Add content to {metrics.empty_slides} empty slide(s)"
            )

        return recommendations

    def _is_empty_slide(self, slide: Dict[str, Any]) -> bool:
        """Check if slide has no meaningful content."""
        slide_type = slide.get("type", "")

        if slide_type == "blank":
            return False

        content = slide.get("content", {})

        if not content:
            return True

        # Check for content based on type
        if slide_type == "content":
            return len(content.get("bullets", [])) == 0

        if slide_type == "table":
            return len(content.get("rows", [])) == 0

        if slide_type in ["two_content", "comparison"]:
            return (len(content.get("left", [])) == 0 and
                    len(content.get("right", [])) == 0)

        return False

    def _simple_similarity(self, s1: str, s2: str) -> float:
        """Calculate simple word overlap similarity."""
        words1 = set(s1.split())
        words2 = set(s2.split())

        if not words1 or not words2:
            return 0.0

        intersection = words1.intersection(words2)
        union = words1.union(words2)

        return len(intersection) / len(union) if union else 0.0
