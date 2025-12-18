# Test Fixtures Package
# Contains sample files for testing

"""
Fixture directories:
- sample_html/: HTML files for accessibility and content testing
- sample_presentations/: JSON presentation fixtures for PPTX generation
- expected_outputs/: Expected output files for validation testing
"""

from pathlib import Path

FIXTURES_DIR = Path(__file__).parent
SAMPLE_HTML_DIR = FIXTURES_DIR / 'sample_html'
SAMPLE_PRESENTATIONS_DIR = FIXTURES_DIR / 'sample_presentations'
EXPECTED_OUTPUTS_DIR = FIXTURES_DIR / 'expected_outputs'
