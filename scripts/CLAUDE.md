# CLAUDE.md - Scripts Directory Governance

This file provides guidance to Claude Code when creating, managing, and executing scripts in this repository's `/scripts/` directory for IMSCC package generation and instructional design automation.

## Repository Purpose - Scripts Context

The `/scripts/` directory is dedicated to creating reliable, modular, and well-documented automation tools for converting instructional design materials into production-ready Brightspace IMSCC packages. All scripts must prioritize reliability, single execution, and atomic operations to prevent system integrity issues.

## Core Principles for Script Development

### 1. Atomic Operations (MANDATORY)
- **Single Execution Rule**: Every script executes exactly once per invocation
- **No Intermediate States**: All operations must be atomic - either complete success or complete failure
- **Immediate Cleanup**: Any failure triggers immediate cleanup of all temporary files/directories
- **Pre-flight Validation**: Validate all inputs and conditions before making any file system changes

### 2. Reliability Standards (ZERO TOLERANCE)
- **Fail-Fast Design**: Detect and report errors immediately, never attempt recovery
- **Input Validation**: Comprehensive validation of all parameters before execution
- **Output Verification**: Validate all outputs meet specifications before reporting success
- **Error Logging**: Detailed error reporting with specific failure reasons

### 3. File System Integrity (CRITICAL)
- **Single Output Files**: Generate exactly one output file per execution
- **No Duplicate Creation**: Prevent any numbered duplicate files or folders
- **Collision Detection**: Check for existing outputs before creating new ones
- **Cleanup Responsibility**: Clean up all temporary files regardless of success/failure

## Script Architecture Standards

### Directory Structure
```
/scripts/
├── CLAUDE.md                 # This governance file
├── README.md                # Overall scripts directory documentation
├── [script-name]/           # Individual script directories
│   ├── README.md           # Script-specific documentation
│   ├── [script-name].py    # Main script file
│   ├── config/             # Configuration files
│   ├── tests/              # Unit tests
│   └── examples/           # Usage examples
```

### Script Naming Conventions
- **Directory Names**: Use kebab-case (e.g., `imscc-generator`, `content-parser`)
- **Script Files**: Use snake_case matching directory (e.g., `imscc_generator.py`)
- **Configuration**: Store in `config/` subdirectory as JSON or YAML
- **Documentation**: Comprehensive `README.md` in each script directory
- **Version Control**: Semantic versioning (v1.0.0) in documentation

### Required Documentation (MANDATORY)
Each script directory must include:
- **README.md** with description, usage, dependencies, examples, and changelog
- **Function Documentation**: Docstrings for all functions with parameters and return values
- **Error Handling**: Document all possible error conditions and responses
- **Dependencies**: List all required packages and versions
- **Testing**: Include unit tests and validation procedures

## IMSCC Generation Requirements

### Critical Success Factors (Based on Debug Analysis)
1. **Schema Compliance**: IMS Common Cartridge 1.2.0 with proper namespace
2. **Content Accuracy**: Actual course content in HTML, not placeholder text
3. **Assessment Integration**: Native Brightspace tools (assignments, quizzes, discussions)
4. **File Integrity**: All manifest references resolve to existing files
5. **Single Output**: Exactly one .imscc file per execution
6. **Template Resolution**: Zero unresolved template variables

### Modular Script Architecture for IMSCC Generation
Create separate, focused scripts for each major function:

#### 1. Course Content Parser (`course-content-parser/`)
**Purpose**: Extract and structure content from markdown course materials
**Input**: Course folder with week_XX.md files, course_info.md, assessment_guide.md
**Output**: Structured JSON with parsed content, learning objectives, assignments
**Critical Requirements**:
- Extract actual academic content, not just structure
- Parse sub-modules per week (count varies by topic complexity: overview, concept summaries, key concepts, applications, etc.)
- Generate substantial content for each sub-module (minimum word counts)
- Remove hardcoded textbook references
- Validate content quality before output

#### 2. HTML Generator (`html-generator/`)
**Purpose**: Convert structured content JSON into HTML pages with Bootstrap framework
**Input**: Structured content JSON from course-content-parser
**Output**: Individual HTML files for each content object
**Critical Requirements**:
- Bootstrap 4.3.1 framework with CDN fallbacks
- Interactive accordion functionality for key concepts
- WCAG 2.2 AA accessibility compliance
- Responsive design for mobile compatibility
- Professional typography and visual hierarchy
- Consistent styling across all pages

#### 3. Assessment XML Generator (`assessment-xml-generator/`)
**Purpose**: Create native Brightspace assessment objects (QTI, D2L XML)
**Input**: Assessment data from course content parser
**Output**: Properly formatted XML files for assignments, quizzes, discussions
**Critical Requirements**:
- QTI 1.2 compliant quiz XML
- D2L assignment XML with dropbox configuration
- Discussion forum XML with grading parameters
- Gradebook integration metadata
- Proper point values and weighting

#### 4. Manifest Generator (`manifest-generator/`)
**Purpose**: Create IMS Common Cartridge manifest file
**Input**: All HTML files, XML assessments, resource inventory
**Output**: Valid imsmanifest.xml file
**Critical Requirements**:
- IMS Common Cartridge 1.2.0 specification compliance
- Proper namespace: `http://www.imsglobal.org/xsd/imsccv1p2/imscp_v1p1`
- All resource references validate to existing files
- Correct resource types for all content objects
- Hierarchical course structure representation

#### 5. Package Assembler (`package-assembler/`)
**Purpose**: Combine all components into final IMSCC package
**Input**: HTML files, XML files, manifest, CSS/JS dependencies
**Output**: Single .imscc ZIP file
**Critical Requirements**:
- Single execution with atomic operations
- Pre-flight validation of all inputs
- Proper ZIP structure following IMS specifications
- No extracted contents - compressed file only
- Collision detection for output filename
- Post-execution validation of single file output

## Script Execution Protocol

### Pre-Execution Validation (MANDATORY)
```python
def validate_execution_environment():
    """Comprehensive pre-flight checks before any script execution"""
    # Check output directory doesn't exist
    if output_path.exists():
        raise SystemExit(f"COLLISION DETECTED: {output_path} already exists")
    
    # Validate all required inputs
    validate_all_inputs()
    
    # Check dependencies and requirements
    validate_dependencies()
    
    # Create execution lock
    create_execution_lock()

def atomic_execution(operation_func):
    """Wrapper ensuring atomic operations with cleanup"""
    temp_files = []
    try:
        result = operation_func(temp_files)
        finalize_outputs(temp_files)
        return result
    except Exception as e:
        cleanup_all_temps(temp_files)
        raise SystemExit(f"ATOMIC OPERATION FAILED: {e}")
    finally:
        remove_execution_lock()
```

### Post-Execution Validation (MANDATORY)
```python
def validate_outputs():
    """Comprehensive output validation"""
    # Confirm exactly one output file
    output_files = list(output_dir.glob("*"))
    if len(output_files) != 1:
        raise SystemExit(f"OUTPUT VALIDATION FAILED: {len(output_files)} files found, expected 1")
    
    # Validate file format and structure
    validate_file_format(output_files[0])
    
    # Check for any duplicate patterns
    check_no_duplicates()
    
    # Log successful completion
    log_success(output_files[0])
```

## Error Handling Standards

### Failure Classification
- **CRITICAL**: System integrity violations, file system corruption, security issues
- **HIGH**: Functional failures that prevent successful IMSCC generation
- **MEDIUM**: Quality issues that affect user experience but don't prevent import
- **LOW**: Minor formatting or optimization opportunities

### Error Response Protocol
```python
def handle_error(error_type, error_message, context):
    """Standardized error handling across all scripts"""
    # Log detailed error information
    log_error(error_type, error_message, context)
    
    # Clean up any temporary files/directories
    cleanup_temps()
    
    # For CRITICAL and HIGH errors, immediately exit
    if error_type in ['CRITICAL', 'HIGH']:
        raise SystemExit(f"{error_type} ERROR: {error_message}")
    
    # For MEDIUM/LOW errors, warn and continue
    log_warning(error_message)
```

## Testing and Validation Framework

### Unit Testing Requirements
- **Test Coverage**: Minimum 80% code coverage for all functions
- **Edge Cases**: Test boundary conditions and error scenarios
- **Mock Dependencies**: Use mocks for external dependencies
- **Automated Testing**: Run tests automatically before any deployment

### Integration Testing
- **End-to-End Validation**: Test complete IMSCC generation pipeline
- **Brightspace Import Testing**: Validate packages import successfully
- **Content Verification**: Confirm actual course content appears correctly
- **Assessment Functionality**: Verify all native tools work properly

### Quality Assurance Checklist
- [ ] All inputs validated before processing
- [ ] Single execution behavior confirmed
- [ ] No temporary files left after completion
- [ ] Output file format matches specifications
- [ ] No duplicate files or directories created
- [ ] Error handling tested and functional
- [ ] Documentation complete and accurate

## Security and Safety Standards

### Input Sanitization
- Validate all file paths and prevent directory traversal
- Sanitize all user inputs to prevent injection attacks
- Check file types and sizes for reasonable limits
- Validate XML content against known schemas

### Output Security
- Ensure generated content doesn't contain sensitive information
- Validate all URLs and external references
- Check for malicious code in any generated scripts
- Sanitize all user-provided content in HTML output

## Deployment and Maintenance

### Version Control
- Use semantic versioning for all scripts
- Maintain changelog in README.md files
- Tag stable releases in version control
- Document all breaking changes

### Performance Optimization  
- Profile script execution times and memory usage
- Optimize file I/O operations for large course packages
- Implement caching for repeated operations
- Monitor resource usage during execution

### Monitoring and Logging
- Comprehensive logging for all script operations
- Error tracking and alerting for failed executions
- Performance metrics collection
- User activity monitoring for debugging

## Implementation Success Criteria

### Functional Requirements
- [ ] Generate valid IMSCC packages that import successfully to Brightspace
- [ ] Create native assessment tools (assignments, quizzes, discussions)
- [ ] Ensure all content displays correctly with professional formatting
- [ ] Maintain WCAG 2.2 AA accessibility compliance
- [ ] Support responsive design across all devices

### Technical Requirements
- [ ] Single execution behavior with atomic operations
- [ ] Zero duplicate file/directory creation
- [ ] Comprehensive error handling and logging
- [ ] Complete test coverage with automated validation
- [ ] Performance benchmarks meeting reasonable standards

### Quality Requirements  
- [ ] Professional documentation for all scripts
- [ ] Clear usage examples and troubleshooting guides
- [ ] Maintainable code with proper commenting
- [ ] Scalable architecture supporting future enhancements
- [ ] Reliable deployment process with rollback capability

## Script Development Workflow

### Phase 1: Requirements Analysis
1. Analyze specific functionality needed
2. Define clear inputs, outputs, and success criteria
3. Identify dependencies and constraints
4. Create detailed specification document

### Phase 2: Development
1. Create script directory structure
2. Implement core functionality with error handling
3. Add comprehensive logging and validation
4. Write unit tests and documentation

### Phase 3: Testing
1. Unit test all functions with edge cases
2. Integration testing with real course data
3. Brightspace import validation
4. Performance and security testing

### Phase 4: Deployment
1. Final code review and documentation check
2. Version tagging and release notes
3. Deployment to production environment
4. Monitoring and issue tracking setup

## Emergency Protocols

### Script Failure Response
1. **Immediate Assessment**: Determine failure scope and impact
2. **Containment**: Stop any running processes and prevent further damage
3. **Investigation**: Analyze logs and identify root cause
4. **Communication**: Document issue and notify relevant stakeholders
5. **Resolution**: Implement fix and validate solution
6. **Prevention**: Update scripts and testing to prevent recurrence

### Rollback Procedures
- Maintain previous working versions of all scripts
- Document rollback procedures for each script
- Test rollback processes regularly
- Automate rollback where possible

---

*This CLAUDE.md file governs all script development in the `/scripts/` directory and must be followed exactly to ensure reliable, secure, and maintainable automation tools for IMSCC package generation.*