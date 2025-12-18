# Changelog

All notable changes to Slideforge will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-12-17

### Added

#### Core Features
- AI-powered presentation generation from structured content
- Multiple input format support (Markdown, JSON outlines, structured documents)
- Professional PPTX output with speaker notes
- Theme system with 5 built-in templates

#### Theme Templates
- `corporate` - Professional blue theme for business presentations
- `dark_mode` - Dark background with vibrant accents
- `creative` - Bold orange/navy for creative presentations
- `minimal` - Clean charcoal with maximum whitespace
- `educational` - Warm purple/brown for learning content

#### Agent System
- 6 specialized AI agents for presentation creation
- Parallel execution with batch management (up to 10 agents per batch)
- Individual section protocol (one agent = one section)

#### Presentation Agents
- `presentation-outliner` - Structure and section planning
- `slide-content-generator` - Slide content creation
- `slide-layout-mapper` - Optimal layout selection
- `slide-validator` - Quality validation
- `pptx-packager` - Final PPTX assembly

#### Slide Types Supported
- Title slides with subtitles
- Section headers
- Content slides with bullet points
- Two-column layouts
- Comparison slides
- Quote slides
- Image slides
- Styled content with callout boxes

#### Visual Elements
- Callout boxes (info, success, warning, tip)
- Rounded cards for content grouping
- Circle badges for step numbers
- Speech bubbles for quotes
- Consistent color theming throughout

#### Documentation
- Getting started guide
- Workflow reference
- Slide design best practices
- Troubleshooting guide

### Technical Details

#### Supported Output
- Microsoft PowerPoint 2007+ (.pptx)
- Cross-platform compatible (Windows, macOS, Linux)
- LibreOffice Impress compatible

#### Dependencies
- python-pptx >= 0.6.21
- Pillow >= 9.0.0
- jsonschema >= 4.0.0

## [Unreleased]

### Planned
- Additional theme templates
- Image optimization and placement
- Chart and diagram support
- Markdown-to-slides direct conversion
- Presentation templates library expansion
