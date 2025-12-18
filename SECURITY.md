# Security Policy

## Reporting a Vulnerability

We take security vulnerabilities seriously. If you discover a security issue, please report it responsibly.

### How to Report

1. **GitHub Security Advisories (Preferred)**: Use GitHub's private vulnerability reporting to submit a report directly.

2. **Email**: If you prefer email, contact the maintainers directly (see repository for contact information).

### What to Include

- Description of the vulnerability
- Steps to reproduce the issue
- Potential impact assessment
- Any suggested fixes (optional)

### Response Timeline

- **Acknowledgment**: Within 48 hours
- **Initial Assessment**: Within 7 days
- **Resolution Target**: Depends on severity, typically within 30 days for critical issues

## Supported Versions

| Version | Supported |
|---------|-----------|
| Latest  | Yes       |

## Security Considerations

When using Slideforge, be aware of the following security considerations:

### File Processing

- **Input Files**: Slideforge processes JSON and markdown files. Always validate input from untrusted sources.
- **Output Files**: Generated PPTX files are standard Office Open XML format.
- **File Paths**: Ensure output directories have appropriate access controls.

### Environment Configuration

- **Output Directories**: The `exports/` directory contains generated presentations. Ensure appropriate access controls in production environments.
- **Virtual Environment**: Use the project's virtual environment to isolate dependencies.

### Dependencies

- All dependencies are regularly monitored for security updates.
- Run `pip install --upgrade -r scripts/requirements.txt` periodically to get security patches.

## Disclosure Policy

We follow responsible disclosure practices:

1. Security issues are addressed before public disclosure
2. Credit is given to reporters (unless anonymity is requested)
3. A security advisory is published after the fix is released
