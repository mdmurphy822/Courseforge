# Scripts Directory

This directory contains automation tools for converting structured content into PowerPoint presentations.

## Organization Guidelines

### Folder Structure
Each script or code project should be placed in its own subdirectory within `/scripts/` with the following structure:
```
/scripts/
├── [script-name]/
│   ├── README.md           # Script documentation and changelog
│   ├── [main-script-file]  # Primary script file
│   ├── config/             # Configuration files (if needed)
│   └── examples/           # Usage examples (if applicable)
```

### Naming Conventions
- **Folder Names**: Use kebab-case (lowercase with hyphens) for folder names
- **Script Names**: Use descriptive names that clearly indicate functionality
- **File Extensions**: Use appropriate extensions (.py, .js, .sh, .json, etc.)

### Documentation Requirements
Each script folder MUST include a `README.md` file containing:

1. **Script Description**: What the script does and its purpose
2. **Usage Instructions**: How to run the script with examples
3. **Dependencies**: Required packages, libraries, or tools
4. **Configuration**: Any setup or configuration requirements
5. **Changelog**: Version history with dates and changes made
6. **Author/Maintainer**: Contact information for questions

## Current Scripts Directory Structure

### `/pptx-generator/` - Core PPTX Generation
Main PowerPoint generation engine that converts structured JSON content into professional PPTX presentations.

**Key Scripts:**
- **`pptx_generator.py`** - Main generator with theme support and multiple slide types
- **`template_loader.py`** - Theme template discovery and loading

**Usage:**
```bash
python pptx_generator.py -i content.json -o presentation.pptx --theme corporate
python pptx_generator.py --list-templates
```

### `/semantic-structure-extractor/` - Content Parsing
Extracts semantic structure from HTML documents for content analysis.

**Key Scripts:**
- **`semantic_structure_extractor.py`** - Main extraction module
- **`heading_parser.py`** - Heading hierarchy parsing
- **`content_block_classifier.py`** - Content classification

### `/utilities/` - Support Tools
Helper scripts for file management and general support functions.

### `/tests/` - Testing Infrastructure
Test suite for presentation generation components.

**Run tests:**
```bash
pytest scripts/tests/ -v
```

## Best Practices

1. **Version Control**: Each script should track version changes in its README.md
2. **Error Handling**: Include comprehensive error handling and logging
3. **Testing**: Provide test cases and validation examples
4. **Documentation**: Keep documentation current with code changes
5. **Security**: Never include sensitive information in scripts or documentation
6. **Modularity**: Write reusable code with clear interfaces
7. **Performance**: Optimize for the expected workload and use cases
8. **Atomic Operations**: All scripts must implement single execution with fail-fast error handling
9. **Comprehensive Validation**: Pre-flight and post-execution validation required

## Dependencies

See `requirements.txt` for Python dependencies:
```
python-pptx>=0.6.21
Pillow>=9.0.0
beautifulsoup4>=4.9.0
jsonschema>=4.0.0
```

## Virtual Environment

Activate the project virtual environment:
```bash
source scripts/venv/bin/activate
```
