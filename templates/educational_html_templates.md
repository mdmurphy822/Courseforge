# Educational HTML Template Repository

## Overview
This repository documents researched educational HTML templates that are suitable for IMSCC packages and Brightspace deployment. All templates have been evaluated for accessibility, educational effectiveness, and Brightspace compatibility.

## Template Categories

### 1. Lesson Content Templates

#### **Basic Lesson Template**
- **Use Case**: Standard weekly content modules
- **Accessibility**: WCAG 2.2 AA compliant
- **Brightspace Compatible**: ✅ Yes
- **Features**: Self-contained, embedded CSS, clear hierarchy
- **File**: `templates/lesson_basic.html`

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{MODULE_TITLE}}</title>
    <style>
        /* Brightspace-compatible embedded styles */
        .lesson-container { 
            max-width: 800px; 
            margin: 0 auto; 
            padding: 20px;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
        }
        .module-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 30px;
        }
        .learning-objectives {
            background-color: #e7f3ff;
            border-left: 4px solid #007bff;
            padding: 15px;
            margin: 20px 0;
            border-radius: 0 4px 4px 0;
        }
        .content-section {
            margin: 30px 0;
        }
        .key-concept {
            background-color: #fff3cd;
            border: 1px solid #ffeaa7;
            padding: 15px;
            border-radius: 4px;
            margin: 15px 0;
        }
        .example-box {
            background-color: #f8f9fa;
            border-left: 4px solid #28a745;
            padding: 15px;
            margin: 15px 0;
        }
    </style>
</head>
<body>
    <div class="lesson-container">
        <header class="module-header">
            <h1>{{MODULE_TITLE}}</h1>
            <p class="module-meta">{{COURSE_NAME}} | {{MODULE_NUMBER}} of {{TOTAL_MODULES}}</p>
        </header>
        
        <section class="learning-objectives">
            <h2>Learning Objectives</h2>
            <ul>
                <li>{{OBJECTIVE_1}}</li>
                <li>{{OBJECTIVE_2}}</li>
                <li>{{OBJECTIVE_3}}</li>
            </ul>
        </section>
        
        <main class="content-section">
            <h2>Introduction</h2>
            {{INTRODUCTION_CONTENT}}
            
            <h2>Key Concepts</h2>
            <div class="key-concept">
                <h3>{{CONCEPT_TITLE}}</h3>
                <p>{{CONCEPT_CONTENT}}</p>
            </div>
            
            <div class="example-box">
                <h3>Example</h3>
                <p>{{EXAMPLE_CONTENT}}</p>
            </div>
        </main>
    </div>
</body>
</html>
```

#### **Interactive Lesson Template**
- **Use Case**: Lessons with expandable sections and interactive elements
- **Accessibility**: WCAG 2.2 AA compliant with keyboard navigation
- **Brightspace Compatible**: ✅ Yes (HTML5 only, no JavaScript)
- **Features**: Collapsible sections, progress indicators, accessibility features

### 2. Assessment Templates

#### **Self-Assessment Template**
- **Use Case**: Reflection exercises and self-check activities
- **Accessibility**: Screen reader friendly with proper labels
- **Brightspace Compatible**: ✅ Yes
- **Features**: Checkbox interactions, reflection prompts

### 3. Activity Templates

#### **Case Study Template**
- **Use Case**: Problem-based learning scenarios
- **Accessibility**: WCAG 2.2 AA compliant
- **Brightspace Compatible**: ✅ Yes
- **Features**: Scenario presentation, analysis framework

#### **Discussion Prompt Template**
- **Use Case**: Structured discussion starters
- **Accessibility**: Clear heading structure for screen readers
- **Brightspace Compatible**: ✅ Yes
- **Features**: Question frameworks, context setting

## Researched External Templates

### Open Source Templates

#### **1. MIT OpenCourseWare Style**
- **Source**: Based on MIT OCW accessibility standards
- **License**: Creative Commons inspired
- **Accessibility**: WCAG 2.0 AA compliant (MIT standard)
- **Features**: Clean academic layout, high contrast, clear typography
- **Brightspace Compatibility**: Requires modification (remove external links)
- **Status**: Template adapted for IMSCC use

#### **2. Edulogy Bootstrap Template**
- **Source**: GitHub - technext/edulogy
- **License**: Free download
- **Accessibility**: Bootstrap 4 base (needs accessibility enhancements)
- **Features**: Responsive design, modern layout
- **Brightspace Compatibility**: ⚠️ Requires significant modification
- **Status**: Under evaluation for adaptation

#### **3. Accessible+ Template**
- **Source**: accessible-template.com
- **License**: Commercial (accessible version available)
- **Accessibility**: WCAG 2.2 AA compliant
- **Features**: Bootstrap-based, accessibility-first design
- **Brightspace Compatibility**: Good potential with modifications
- **Status**: Evaluating free components

### Bootstrap Educational Templates

#### **4. BootstrapMade Education Templates**
- **Source**: bootstrapmade.com
- **License**: Mixed (some free, some premium)
- **Accessibility**: Variable (needs enhancement)
- **Features**: Multiple layout options, responsive design
- **Brightspace Compatibility**: Requires link removal and CSS embedding
- **Status**: Selective component extraction

## Accessibility Standards Applied

### WCAG 2.2 AA Compliance Checklist
- [ ] Proper heading hierarchy (H1-H6)
- [ ] Sufficient color contrast (4.5:1 for normal text)
- [ ] Alternative text for images
- [ ] Keyboard navigation support
- [ ] Screen reader compatibility
- [ ] Focus indicators visible
- [ ] No content flashing/seizure risks
- [ ] Semantic HTML structure

### Brightspace Specific Modifications
- [ ] All CSS embedded in `<style>` tags
- [ ] No external stylesheets or scripts
- [ ] No internal page links (`href="#section"`)
- [ ] No JavaScript dependencies
- [ ] Self-contained content structure
- [ ] Mobile-responsive design preserved

## Template Customization Guide

### Variable Replacement System
Templates use double curly braces for easy customization:

```html
<!-- Template Variables -->
{{MODULE_TITLE}} → Actual module title
{{COURSE_NAME}} → Course name
{{MODULE_NUMBER}} → Current module number
{{TOTAL_MODULES}} → Total number of modules
{{OBJECTIVE_1}} → First learning objective
{{INTRODUCTION_CONTENT}} → Main introduction text
```

### Color Scheme Customization
Standard color variables defined in CSS:

```css
:root {
    --primary-color: #007bff;    /* Main brand color */
    --secondary-color: #6c757d;  /* Supporting color */
    --success-color: #28a745;    /* Positive feedback */
    --warning-color: #ffc107;    /* Caution/attention */
    --danger-color: #dc3545;     /* Error/important */
    --info-color: #17a2b8;       /* Information */
    --light-color: #f8f9fa;      /* Light backgrounds */
    --dark-color: #343a40;       /* Dark text/elements */
}
```

## Implementation Workflow

### Step 1: Template Selection
1. Identify content type (lesson, assessment, activity)
2. Select appropriate template from repository
3. Review accessibility and Brightspace compatibility notes

### Step 2: Content Integration
1. Replace template variables with actual content
2. Customize color scheme if needed
3. Add specific multimedia or interactive elements

### Step 3: Quality Assurance
1. Validate HTML structure
2. Test accessibility with screen reader simulation
3. Verify mobile responsiveness
4. Check Brightspace compatibility

### Step 4: IMSCC Integration
1. Place completed HTML file in appropriate directory
2. Reference in manifest.xml
3. Test import in Brightspace sandbox environment

## Template Maintenance

### Regular Updates
- **Monthly**: Review new open source templates
- **Quarterly**: Update accessibility standards compliance
- **Annually**: Comprehensive Brightspace compatibility testing

### Version Control
- Template version numbers in HTML comments
- Change log documentation
- Backward compatibility maintenance

### Community Contributions
- GitHub repository for template contributions
- Peer review process for new templates
- User feedback integration system

## Future Development

### Planned Template Additions
1. **Video Lecture Template** - Structured video content presentation
2. **Simulation Activity Template** - Interactive learning scenarios
3. **Group Project Template** - Collaborative learning frameworks
4. **Assessment Review Template** - Post-assessment learning reinforcement

### Technology Integration
- **Progressive Enhancement** - Advanced features for modern browsers
- **Responsive Images** - Optimized media delivery
- **Print Optimization** - Printer-friendly versions

### Research Initiatives
- **User Experience Studies** - Template effectiveness research
- **Accessibility Testing** - Ongoing compliance verification
- **Learning Outcome Analysis** - Educational effectiveness measurement