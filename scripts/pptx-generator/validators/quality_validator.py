"""Quality validation for Slideforge presentations.

Validates presentations against design best practices including:
- 6x6 rule (max 6 bullets, max 6 words per bullet)
- Speaker notes coverage
- Slide type variety
- Section balance
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class QualityViolation:
    """A single quality violation."""
    rule: str
    severity: str  # error, warning, info
    location: str
    message: str
    suggestion: Optional[str] = None


@dataclass
class QualityMetrics:
    """Quality metrics for a presentation."""
    slide_count: int = 0
    section_count: int = 0
    slides_with_notes: int = 0
    notes_coverage: float = 0.0
    six_six_violations: int = 0
    slide_type_variety: float = 0.0
    avg_bullets_per_slide: float = 0.0
    section_balance_score: float = 0.0


@dataclass
class QualityReport:
    """Complete quality validation report."""
    valid: bool
    score: float  # 0-100
    metrics: QualityMetrics = field(default_factory=QualityMetrics)
    violations: List[QualityViolation] = field(default_factory=list)
    summary: str = ""


def validate_quality(data: dict) -> QualityReport:
    """Validate presentation quality against best practices.

    Args:
        data: Presentation data dictionary

    Returns:
        QualityReport with metrics and violations
    """
    report = QualityReport(valid=True, score=100.0)
    metrics = QualityMetrics()
    violations = []

    sections = data.get('sections', [])
    metrics.section_count = len(sections)

    all_slides = []
    slide_types_used = set()
    bullets_per_slide = []
    slides_per_section = []

    for si, section in enumerate(sections):
        slides = section.get('slides', [])
        slides_per_section.append(len(slides))

        for sli, slide in enumerate(slides):
            all_slides.append(slide)
            location = f"Section {si+1} '{section.get('title', 'Untitled')}', Slide {sli+1}"

            slide_type = slide.get('type', 'content')
            slide_types_used.add(slide_type)

            # Check speaker notes
            if slide.get('notes'):
                metrics.slides_with_notes += 1
            elif slide_type in ['content', 'two_content', 'comparison']:
                violations.append(QualityViolation(
                    rule="speaker_notes",
                    severity="warning",
                    location=location,
                    message="Missing speaker notes",
                    suggestion="Add speaker notes to help presenters"
                ))

            # Check 6x6 rule
            content = slide.get('content', {})
            slide_bullets = 0

            for key in ['bullets', 'left', 'right']:
                items = content.get(key, [])
                slide_bullets += len(items)

                # Check bullet count
                if len(items) > 6:
                    metrics.six_six_violations += 1
                    violations.append(QualityViolation(
                        rule="6x6_bullet_count",
                        severity="warning",
                        location=f"{location} ({key})",
                        message=f"{len(items)} bullets exceeds maximum of 6",
                        suggestion="Split into multiple slides or condense content"
                    ))

                # Check word count per bullet
                for bi, bullet in enumerate(items):
                    words = len(bullet.split())
                    if words > 6:
                        metrics.six_six_violations += 1
                        violations.append(QualityViolation(
                            rule="6x6_word_count",
                            severity="info",
                            location=f"{location} ({key}), bullet {bi+1}",
                            message=f"{words} words exceeds recommended 6",
                            suggestion="Shorten to key phrase or split across bullets"
                        ))

            bullets_per_slide.append(slide_bullets)

    # Calculate metrics
    metrics.slide_count = len(all_slides)

    if metrics.slide_count > 0:
        metrics.notes_coverage = round(
            metrics.slides_with_notes / metrics.slide_count * 100, 1
        )
        metrics.avg_bullets_per_slide = round(
            sum(bullets_per_slide) / len(bullets_per_slide), 1
        ) if bullets_per_slide else 0

    # Slide type variety (out of 8 possible types)
    possible_types = {'title', 'section_header', 'content', 'two_content',
                      'comparison', 'image', 'quote', 'blank'}
    metrics.slide_type_variety = round(
        len(slide_types_used & possible_types) / len(possible_types) * 100, 1
    )

    # Section balance score
    if slides_per_section:
        avg = sum(slides_per_section) / len(slides_per_section)
        if avg > 0:
            variance = sum((x - avg) ** 2 for x in slides_per_section) / len(slides_per_section)
            # Lower variance = better balance (100 = perfect, decreases with variance)
            metrics.section_balance_score = round(max(0, 100 - variance * 5), 1)
        else:
            metrics.section_balance_score = 100.0

    # Calculate overall score
    score_deductions = 0

    # Deduct for 6x6 violations (5 points each, max 30)
    score_deductions += min(30, metrics.six_six_violations * 5)

    # Deduct for low notes coverage (up to 20 points)
    if metrics.notes_coverage < 80:
        score_deductions += int((80 - metrics.notes_coverage) / 4)

    # Deduct for low type variety (up to 10 points)
    if metrics.slide_type_variety < 30:
        score_deductions += 10

    report.score = max(0, 100 - score_deductions)
    report.metrics = metrics
    report.violations = violations

    # Determine validity (score >= 70 = valid)
    report.valid = report.score >= 70

    # Generate summary
    error_count = sum(1 for v in violations if v.severity == "error")
    warning_count = sum(1 for v in violations if v.severity == "warning")

    if report.score >= 90:
        report.summary = "Excellent quality presentation"
    elif report.score >= 80:
        report.summary = "Good quality with minor improvements possible"
    elif report.score >= 70:
        report.summary = "Acceptable quality with some issues to address"
    else:
        report.summary = "Quality issues need attention before presentation"

    report.summary += f" ({error_count} errors, {warning_count} warnings)"

    return report


def check_6x6_rule(bullets: List[str]) -> List[QualityViolation]:
    """Check a list of bullets against the 6x6 rule.

    Args:
        bullets: List of bullet point strings

    Returns:
        List of violations found
    """
    violations = []

    if len(bullets) > 6:
        violations.append(QualityViolation(
            rule="6x6_bullet_count",
            severity="warning",
            location="",
            message=f"{len(bullets)} bullets exceeds maximum of 6"
        ))

    for i, bullet in enumerate(bullets):
        words = len(bullet.split())
        if words > 6:
            violations.append(QualityViolation(
                rule="6x6_word_count",
                severity="info",
                location=f"bullet {i+1}",
                message=f"{words} words exceeds recommended 6"
            ))

    return violations
