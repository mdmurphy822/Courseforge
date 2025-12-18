"""Presentation quality checker for Slideforge.

Comprehensive quality analysis for presentations.
Checks presentations against design best practices and generates detailed reports.
"""

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple


@dataclass
class QualityIssue:
    """A quality issue found in the presentation."""
    category: str  # 6x6_rule, speaker_notes, structure, accessibility
    severity: str  # error, warning, info
    location: str
    message: str
    suggestion: Optional[str] = None


@dataclass
class QualityScore:
    """Quality score breakdown."""
    overall: float = 100.0
    content: float = 100.0  # 6x6 rule compliance
    notes: float = 100.0    # Speaker notes coverage
    structure: float = 100.0  # Section balance, flow
    variety: float = 100.0  # Slide type variety


@dataclass
class QualityReport:
    """Complete quality analysis report."""
    presentation_title: str
    score: QualityScore
    metrics: Dict
    issues: List[QualityIssue]
    summary: str
    passed: bool


class PresentationQualityChecker:
    """Quality checker for Slideforge presentations.

    Analyzes presentations against best practices:
    - 6x6 rule (max 6 bullets, ~6 words per bullet)
    - Speaker notes coverage
    - Slide type variety
    - Section balance

    Usage:
        checker = PresentationQualityChecker()
        report = checker.check(presentation_data)
        print(f"Score: {report.score.overall}")
    """

    # Weights for score calculation
    WEIGHT_CONTENT = 0.35
    WEIGHT_NOTES = 0.25
    WEIGHT_STRUCTURE = 0.20
    WEIGHT_VARIETY = 0.20

    # Thresholds
    PASS_THRESHOLD = 70.0
    MAX_BULLETS = 6
    MAX_WORDS_PER_BULLET = 6
    NOTES_TARGET_COVERAGE = 0.80

    def __init__(self):
        self.issues: List[QualityIssue] = []
        self.metrics: Dict = {}

    def check(self, data: dict) -> QualityReport:
        """Run complete quality check on presentation data.

        Args:
            data: Presentation JSON data

        Returns:
            QualityReport with scores, metrics, and issues
        """
        self.issues = []
        self.metrics = {}

        title = data.get('metadata', {}).get('title', 'Untitled')

        # Run all checks
        content_score = self._check_6x6_rule(data)
        notes_score = self._check_speaker_notes(data)
        structure_score = self._check_structure(data)
        variety_score = self._check_slide_variety(data)

        # Calculate overall score
        overall = (
            content_score * self.WEIGHT_CONTENT +
            notes_score * self.WEIGHT_NOTES +
            structure_score * self.WEIGHT_STRUCTURE +
            variety_score * self.WEIGHT_VARIETY
        )

        score = QualityScore(
            overall=round(overall, 1),
            content=round(content_score, 1),
            notes=round(notes_score, 1),
            structure=round(structure_score, 1),
            variety=round(variety_score, 1)
        )

        passed = overall >= self.PASS_THRESHOLD
        summary = self._generate_summary(score, passed)

        return QualityReport(
            presentation_title=title,
            score=score,
            metrics=self.metrics,
            issues=self.issues,
            summary=summary,
            passed=passed
        )

    def _check_6x6_rule(self, data: dict) -> float:
        """Check 6x6 rule compliance.

        Returns score from 0-100 based on violations.
        """
        violations = 0
        total_bullet_lists = 0

        sections = data.get('sections', [])
        for si, section in enumerate(sections):
            for sli, slide in enumerate(section.get('slides', [])):
                location = f"Section {si+1}, Slide {sli+1}"
                content = slide.get('content', {})

                for key in ['bullets', 'left', 'right']:
                    items = content.get(key, [])
                    if not items:
                        continue

                    total_bullet_lists += 1

                    # Check bullet count
                    if len(items) > self.MAX_BULLETS:
                        violations += 1
                        self.issues.append(QualityIssue(
                            category="6x6_rule",
                            severity="warning",
                            location=f"{location} ({key})",
                            message=f"{len(items)} bullets exceeds maximum of {self.MAX_BULLETS}",
                            suggestion="Split content across multiple slides"
                        ))

                    # Check word count
                    for bi, bullet in enumerate(items):
                        words = len(bullet.split())
                        if words > self.MAX_WORDS_PER_BULLET:
                            violations += 1
                            self.issues.append(QualityIssue(
                                category="6x6_rule",
                                severity="info",
                                location=f"{location} ({key}), bullet {bi+1}",
                                message=f"{words} words exceeds target of {self.MAX_WORDS_PER_BULLET}",
                                suggestion="Condense to key phrase"
                            ))

        self.metrics['6x6_violations'] = violations
        self.metrics['bullet_lists_checked'] = total_bullet_lists

        # Score: lose 10 points per violation, min 0
        if total_bullet_lists == 0:
            return 100.0
        return max(0, 100 - (violations * 10))

    def _check_speaker_notes(self, data: dict) -> float:
        """Check speaker notes coverage.

        Returns score based on percentage of slides with notes.
        """
        total_slides = 0
        slides_with_notes = 0
        content_slides_without_notes = []

        sections = data.get('sections', [])
        for si, section in enumerate(sections):
            for sli, slide in enumerate(section.get('slides', [])):
                total_slides += 1
                slide_type = slide.get('type', 'content')

                if slide.get('notes', '').strip():
                    slides_with_notes += 1
                elif slide_type in ['content', 'two_content', 'comparison']:
                    content_slides_without_notes.append(f"Section {si+1}, Slide {sli+1}")

        # Add issues for content slides without notes
        for location in content_slides_without_notes[:5]:  # Limit to 5 warnings
            self.issues.append(QualityIssue(
                category="speaker_notes",
                severity="warning",
                location=location,
                message="Content slide missing speaker notes",
                suggestion="Add notes to help presenters"
            ))

        if len(content_slides_without_notes) > 5:
            self.issues.append(QualityIssue(
                category="speaker_notes",
                severity="info",
                location="Multiple slides",
                message=f"{len(content_slides_without_notes) - 5} more slides missing notes",
                suggestion=None
            ))

        coverage = slides_with_notes / total_slides if total_slides > 0 else 0
        self.metrics['slides_with_notes'] = slides_with_notes
        self.metrics['total_slides'] = total_slides
        self.metrics['notes_coverage'] = round(coverage * 100, 1)

        # Score based on coverage vs target
        if coverage >= self.NOTES_TARGET_COVERAGE:
            return 100.0
        return (coverage / self.NOTES_TARGET_COVERAGE) * 100

    def _check_structure(self, data: dict) -> float:
        """Check presentation structure and balance.

        Returns score based on section balance and logical flow.
        """
        sections = data.get('sections', [])
        if not sections:
            self.issues.append(QualityIssue(
                category="structure",
                severity="error",
                location="Presentation",
                message="No sections found",
                suggestion="Add at least one section"
            ))
            return 0.0

        slides_per_section = []
        for si, section in enumerate(sections):
            slides = section.get('slides', [])
            slides_per_section.append(len(slides))

            # Check section has title
            if not section.get('title'):
                self.issues.append(QualityIssue(
                    category="structure",
                    severity="info",
                    location=f"Section {si+1}",
                    message="Section missing title",
                    suggestion="Add section title for navigation"
                ))

            # Check section not empty
            if len(slides) == 0:
                self.issues.append(QualityIssue(
                    category="structure",
                    severity="warning",
                    location=f"Section {si+1}",
                    message="Empty section",
                    suggestion="Add slides or remove section"
                ))

        self.metrics['section_count'] = len(sections)
        self.metrics['slides_per_section'] = slides_per_section

        # Calculate balance score (lower variance = better)
        if len(slides_per_section) > 1:
            avg = sum(slides_per_section) / len(slides_per_section)
            variance = sum((x - avg) ** 2 for x in slides_per_section) / len(slides_per_section)
            balance_score = max(0, 100 - variance * 5)
        else:
            balance_score = 100.0

        self.metrics['section_balance_score'] = round(balance_score, 1)
        return balance_score

    def _check_slide_variety(self, data: dict) -> float:
        """Check slide type variety.

        Returns score based on variety of slide types used.
        """
        possible_types = {'title', 'section_header', 'content', 'two_content',
                         'comparison', 'image', 'quote', 'blank'}
        used_types = set()

        sections = data.get('sections', [])
        for section in sections:
            for slide in section.get('slides', []):
                slide_type = slide.get('type', 'content')
                used_types.add(slide_type)

        self.metrics['slide_types_used'] = list(used_types)
        self.metrics['slide_type_count'] = len(used_types)

        # Score based on variety (using 4+ types = 100%)
        variety_ratio = min(1.0, len(used_types) / 4)
        score = variety_ratio * 100

        if len(used_types) < 2:
            self.issues.append(QualityIssue(
                category="variety",
                severity="info",
                location="Presentation",
                message="Limited slide type variety",
                suggestion="Consider using different layouts for visual interest"
            ))

        return score

    def _generate_summary(self, score: QualityScore, passed: bool) -> str:
        """Generate human-readable summary."""
        if score.overall >= 90:
            quality = "Excellent"
        elif score.overall >= 80:
            quality = "Good"
        elif score.overall >= 70:
            quality = "Acceptable"
        elif score.overall >= 50:
            quality = "Needs improvement"
        else:
            quality = "Poor"

        errors = sum(1 for i in self.issues if i.severity == "error")
        warnings = sum(1 for i in self.issues if i.severity == "warning")

        status = "PASSED" if passed else "NEEDS ATTENTION"
        return f"{quality} quality ({score.overall}/100) - {status}. {errors} errors, {warnings} warnings."

    def check_file(self, file_path: Path) -> QualityReport:
        """Check a presentation JSON file.

        Args:
            file_path: Path to presentation JSON

        Returns:
            QualityReport
        """
        with open(file_path) as f:
            data = json.load(f)
        return self.check(data)

    def to_dict(self, report: QualityReport) -> dict:
        """Convert report to dictionary for JSON serialization."""
        return {
            'presentation_title': report.presentation_title,
            'passed': report.passed,
            'summary': report.summary,
            'score': {
                'overall': report.score.overall,
                'content': report.score.content,
                'notes': report.score.notes,
                'structure': report.score.structure,
                'variety': report.score.variety
            },
            'metrics': report.metrics,
            'issues': [
                {
                    'category': i.category,
                    'severity': i.severity,
                    'location': i.location,
                    'message': i.message,
                    'suggestion': i.suggestion
                }
                for i in report.issues
            ]
        }
