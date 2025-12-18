"""
Slideforge Test Fixtures
Shared pytest fixtures for all test modules
"""

import pytest
import sys
import tempfile
import shutil
from pathlib import Path

# Add scripts directory to path for imports
SCRIPTS_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(SCRIPTS_DIR))

# Fixture directories
FIXTURES_DIR = Path(__file__).parent / 'fixtures'
SAMPLE_HTML_DIR = FIXTURES_DIR / 'sample_html'


# =============================================================================
# HTML FIXTURE PATHS
# =============================================================================

@pytest.fixture
def accessible_html_path():
    """Path to fully WCAG AA compliant HTML file"""
    return SAMPLE_HTML_DIR / 'accessible.html'


@pytest.fixture
def missing_alt_html_path():
    """Path to HTML with missing alt attributes on images"""
    return SAMPLE_HTML_DIR / 'missing_alt.html'


@pytest.fixture
def broken_headings_html_path():
    """Path to HTML with improper heading hierarchy"""
    return SAMPLE_HTML_DIR / 'broken_headings.html'


@pytest.fixture
def forms_no_labels_html_path():
    """Path to HTML with forms lacking proper labels"""
    return SAMPLE_HTML_DIR / 'forms_no_labels.html'


# =============================================================================
# HTML CONTENT FIXTURES (in-memory)
# =============================================================================

@pytest.fixture
def accessible_html_content():
    """Returns WCAG AA compliant HTML content"""
    return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Accessible Test Page</title>
</head>
<body>
    <a href="#main-content" class="skip-link">Skip to main content</a>
    <header role="banner">
        <nav aria-label="Main navigation">
            <ul>
                <li><a href="index.html">Home</a></li>
                <li><a href="about.html">About Us</a></li>
            </ul>
        </nav>
    </header>
    <main id="main-content" role="main">
        <h1>Welcome to the Course</h1>
        <section aria-labelledby="intro-heading">
            <h2 id="intro-heading">Introduction</h2>
            <p>This is an introduction paragraph with sufficient content.</p>
            <img src="diagram.png" alt="Network topology diagram showing three connected servers">
            <h3>Key Concepts</h3>
            <ul>
                <li>First concept explanation</li>
                <li>Second concept explanation</li>
            </ul>
        </section>
    </main>
    <footer role="contentinfo">
        <p>&copy; 2025 Slideforge</p>
    </footer>
</body>
</html>'''


@pytest.fixture
def missing_alt_html_content():
    """Returns HTML with images missing alt attributes"""
    return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Missing Alt Text Test</title>
</head>
<body>
    <main>
        <h1>Page with Missing Alt Text</h1>
        <img src="image1.png">
        <img src="image2.jpg" alt="">
        <img src="image3.gif">
        <p>Some content here.</p>
    </main>
</body>
</html>'''


@pytest.fixture
def broken_headings_html_content():
    """Returns HTML with improper heading hierarchy (skips levels)"""
    return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Broken Headings Test</title>
</head>
<body>
    <main>
        <h1>Main Title</h1>
        <h3>Skipped to H3</h3>
        <p>Content under H3</p>
        <h5>Skipped to H5</h5>
        <p>Content under H5</p>
        <h2>Back to H2</h2>
        <h4>Skipped to H4</h4>
    </main>
</body>
</html>'''


@pytest.fixture
def forms_no_labels_html_content():
    """Returns HTML with form inputs lacking proper labels"""
    return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Forms Without Labels Test</title>
</head>
<body>
    <main>
        <h1>Form Without Labels</h1>
        <form action="/submit" method="post">
            <input type="text" name="username" placeholder="Username">
            <input type="password" name="password" placeholder="Password">
            <select name="country">
                <option value="">Select Country</option>
                <option value="us">United States</option>
            </select>
            <textarea name="comments" placeholder="Comments"></textarea>
            <input type="checkbox" name="agree" value="yes"> I agree
            <button type="submit">Submit</button>
        </form>
    </main>
</body>
</html>'''


# =============================================================================
# PRESENTATION FIXTURES
# =============================================================================

@pytest.fixture
def sample_presentation_json():
    """Returns a sample presentation JSON structure"""
    return {
        "metadata": {
            "title": "Test Presentation",
            "subtitle": "A Test Subtitle",
            "author": "Test Author",
            "date": "2025-12-17"
        },
        "sections": [
            {
                "title": "Introduction",
                "slides": [
                    {
                        "type": "title",
                        "title": "Test Presentation",
                        "content": {"subtitle": "A Test Subtitle"}
                    }
                ]
            },
            {
                "title": "Main Content",
                "slides": [
                    {
                        "type": "content",
                        "title": "Key Points",
                        "content": {
                            "bullets": ["Point 1", "Point 2", "Point 3"]
                        },
                        "notes": "Speaker notes here"
                    }
                ]
            }
        ]
    }


# =============================================================================
# TEMPORARY DIRECTORY FIXTURES
# =============================================================================

@pytest.fixture
def temp_output_dir(tmp_path):
    """Creates a temporary output directory that is cleaned up after test"""
    output_dir = tmp_path / 'output'
    output_dir.mkdir(parents=True, exist_ok=True)
    yield output_dir
    # Cleanup happens automatically with tmp_path


@pytest.fixture
def temp_presentation_dir(tmp_path):
    """Creates a mock presentation directory structure"""
    pres_dir = tmp_path / 'test_presentation'
    pres_dir.mkdir(parents=True, exist_ok=True)

    # Create section directories
    for section in range(1, 4):
        section_dir = pres_dir / f'section_{section:02d}'
        section_dir.mkdir(parents=True, exist_ok=True)

    yield pres_dir


# =============================================================================
# HELPER FIXTURES
# =============================================================================

@pytest.fixture
def write_temp_html(tmp_path):
    """Factory fixture for writing temporary HTML files"""
    def _write_html(content, filename='test.html'):
        file_path = tmp_path / filename
        file_path.write_text(content)
        return file_path
    return _write_html


@pytest.fixture
def slideforge_path():
    """Returns the path to the Slideforge project root"""
    return Path(__file__).parent.parent.parent


@pytest.fixture
def scripts_path():
    """Returns the path to the scripts directory"""
    return Path(__file__).parent.parent


# =============================================================================
# PRESENTATION JSON FIXTURES
# =============================================================================

@pytest.fixture
def minimal_presentation():
    """Returns a minimal valid presentation with 5 slides"""
    import json
    fixture_path = FIXTURES_DIR / 'sample_presentations' / 'minimal_5_slides.json'
    with open(fixture_path, 'r') as f:
        return json.load(f)


@pytest.fixture
def all_slide_types_presentation():
    """Returns a presentation demonstrating all 21+ slide types"""
    import json
    fixture_path = FIXTURES_DIR / 'sample_presentations' / 'all_slide_types.json'
    with open(fixture_path, 'r') as f:
        return json.load(f)


@pytest.fixture
def complex_presentation():
    """Returns a large presentation with 50 slides across 5 sections"""
    import json
    fixture_path = FIXTURES_DIR / 'sample_presentations' / 'complex_50_slides.json'
    with open(fixture_path, 'r') as f:
        return json.load(f)


@pytest.fixture
def presentation_schema():
    """Returns the presentation JSON schema for validation"""
    import json
    schema_path = Path(__file__).parent.parent.parent / 'schemas' / 'presentation' / 'presentation_schema.json'
    with open(schema_path, 'r') as f:
        return json.load(f)


@pytest.fixture
def minimal_presentation_path():
    """Returns the path to the minimal presentation fixture file"""
    return FIXTURES_DIR / 'sample_presentations' / 'minimal_5_slides.json'


@pytest.fixture
def all_slide_types_path():
    """Returns the path to the all slide types fixture file"""
    return FIXTURES_DIR / 'sample_presentations' / 'all_slide_types.json'


@pytest.fixture
def complex_presentation_path():
    """Returns the path to the complex presentation fixture file"""
    return FIXTURES_DIR / 'sample_presentations' / 'complex_50_slides.json'
