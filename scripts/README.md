# Scripts Directory

This directory contains all code used in the instructional design project, organized by functionality and purpose.

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

### Example README.md Template
```markdown
# [Script Name]

## Description
Brief description of what this script does.

## Usage
```bash
python script.py [arguments]
```

## Dependencies
- Python 3.8+
- Required packages: numpy, pandas

## Configuration
- Set environment variable X
- Configure file Y

## Changelog
### v1.0.0 - 2025-08-02
- Initial version
- Added feature X
- Fixed bug Y

## Author
Name <email@example.com>
```

## Current Scripts Directory Structure

### `/package-creators/` - IMSCC Generation Tools
Complete collection of tools for creating IMS Common Cartridge (.imscc) packages from course content for Brightspace LMS import. Contains both production-ready generators and emergency solutions for environment-specific ZIP packaging issues.

**Key Scripts:**
- **`production_imscc_generator.py`** - Production-ready generator with zero-tolerance Pattern 7 prevention
- **`imscc-master-generator.py`** - Master orchestration script coordinating all modular components
- **`manual_imscc_creator.py`** - Emergency IMSCC creator for ZIP packaging failures (Pattern 10 solution)
- **`final_imscc_creator.py`** - Production-ready IMSCC package generator with comprehensive validation
- **`simple_imscc_generator.py`** - Simple generator without external dependencies

### `/course-content-parser/` - Content Processing
Extracts and structures content from markdown course materials into JSON format for HTML generation.

### `/html-generator/` - Web Content Creation  
Converts structured content JSON into HTML pages with Bootstrap framework and WCAG 2.2 AA accessibility compliance.

### `/assessment-xml-generator/` - Assessment Tools
Creates native Brightspace assessment objects (QTI, D2L XML) for assignments, quizzes, and discussions.

### `/bulletproof-imscc-generator/` - Specialized Package Creation
Bulletproof IMSCC generation with atomic operations and comprehensive validation protocols.

### `/brightspace-packager/` - Enhanced Package Management
Enhanced Brightspace Package Generator with export directory management - transforms structured markdown course content into production-ready IMS Common Cartridge packages with full Brightspace integration, native assessment tools, and interactive Bootstrap accordion components. Automatically saves all packages to `/exports/YYYYMMDD_HHMMSS/` timestamped directories.

### `/test-utilities/` - Testing and Validation
Collection of test scripts and validation utilities for IMSCC generation and Pattern 7 prevention testing.

**Key Scripts:**
- **`test_compression.py`** - Tests ZIP compression functionality and capabilities
- **`test_master_generator.py`** - Tests master generator orchestration functionality  
- **`test_bulletproof.py`** - Bulletproof generator validation tests
- **`execute_imscc_generation.py`** - IMSCC generation testing

### `/utilities/` - Support Tools
Helper scripts for file management, cleanup operations, and general support functions.

## **CRITICAL: Script Organization Compliance**

### **MANDATORY: All Scripts Must Be in `/scripts/` Directory**

**REQUIRED STRUCTURE:**
- **Location**: `/scripts/[project-name]/` (kebab-case directory names)
- **Documentation**: Every script directory MUST include comprehensive `README.md`
- **Configuration**: Config files in `config/` subdirectory within each script folder
- **Examples**: Usage examples in `examples/` subdirectory where applicable

**PROHIBITED LOCATIONS:**
❌ **Project root directory**: No scripts in project root `/*.py`
❌ **Export directories**: No scripts in `/exports/YYYYMMDD_HHMMSS/*.py`
❌ **Content directories**: No scripts mixed with course materials

### **Pattern 7 Prevention Protocol (ZERO TOLERANCE)**
All IMSCC generation scripts implement bulletproof Pattern 7 prevention:
- **Single Execution Rule**: Every script executes exactly once per invocation
- **Atomic Operations**: Either complete success or complete failure with cleanup
- **Pre-flight Validation**: Validate all inputs before making file system changes
- **Output Verification**: Confirm exactly one output file per execution

### **ZIP Packaging Crisis Resolution**
Due to environment ZIP compression limitations (Pattern 10 - Empty ZIP files):
- **Primary Solution**: `manual_imscc_creator.py` with comprehensive validation
- **Fallback**: Manual packaging instructions provided for user execution
- **Emergency Protocol**: All creators include user-executable packaging commands

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