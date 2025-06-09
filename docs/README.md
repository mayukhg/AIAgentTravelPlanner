# GitHub Wiki Documentation

This `docs/` folder contains the complete source documentation for the Multi-Agent Assistant System, designed to be used as a GitHub wiki.

## Wiki Structure

The documentation is organized into comprehensive sections covering all aspects of the system:

### Core Documentation
- **[Home](Home.md)** - Main wiki homepage with overview and navigation
- **[Installation](Installation.md)** - Complete setup and installation guide
- **[User Guide](User-Guide.md)** - How to use the assistant effectively
- **[API Reference](API-Reference.md)** - Complete REST API documentation

### Architecture & Design
- **[System Architecture](System-Architecture.md)** - High-level system design and patterns
- **[Agent Framework](Agent-Framework.md)** - Multi-agent system detailed documentation
- **[Database Schema](Database-Schema.md)** - Complete database structure and relationships

### Configuration & Development
- **[Configuration](Configuration.md)** - Environment setup and configuration options
- **[Development Guide](Development-Guide.md)** - For contributors and developers
- **[Security Guidelines](Security-Guidelines.md)** - Comprehensive security best practices
- **[Troubleshooting](Troubleshooting.md)** - Common issues and solutions

## Setting Up GitHub Wiki

### Option 1: Manual Wiki Setup

1. **Enable Wiki** in your GitHub repository:
   - Go to repository Settings → Features → Wiki → Enable

2. **Create Wiki Pages**:
   - Navigate to the Wiki tab in your repository
   - Click "Create the first page"
   - Copy content from each `.md` file in this folder
   - Create pages with the same names (remove `.md` extension)

3. **Set Home Page**:
   - Copy content from `Home.md` to the default Home page
   - This becomes your wiki's main navigation

### Option 2: Automated Wiki Sync

Use GitHub Actions to automatically sync this docs folder to your wiki:

```yaml
# .github/workflows/sync-wiki.yml
name: Sync Wiki

on:
  push:
    paths:
      - 'docs/**'
    branches:
      - main

jobs:
  sync-wiki:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v3
        
      - name: Sync to Wiki
        uses: newrelic/wiki-sync-action@main
        with:
          source: docs/
          destination: wiki/
          token: ${{ secrets.GITHUB_TOKEN }}
```

### Option 3: Git Submodule Approach

1. **Clone Wiki Repository**:
```bash
git clone https://github.com/username/repository.wiki.git
cd repository.wiki
```

2. **Copy Documentation**:
```bash
cp ../repository/docs/*.md .
git add .
git commit -m "Initial wiki documentation"
git push origin master
```

## Navigation Structure

The wiki uses internal linking for easy navigation:

```markdown
- [Installation Guide](Installation)
- [User Guide](User-Guide)
- [API Reference](API-Reference)
```

Links automatically resolve to wiki pages (GitHub removes `.md` extensions).

## Content Organization

### Hierarchical Structure
- Main topics as separate pages
- Sub-topics as sections within pages
- Cross-references between related topics

### Formatting Standards
- Consistent heading structure (H1 for page title, H2-H4 for sections)
- Code blocks with language specification
- Tables for structured information
- Diagrams using ASCII art or mermaid syntax

### Update Workflow

1. **Edit Documentation**: Modify files in the `docs/` folder
2. **Test Locally**: Preview changes using any Markdown viewer
3. **Commit Changes**: Push to main repository
4. **Sync to Wiki**: Manual copy or automated sync

## Advanced Features

### Search Functionality
GitHub wiki includes built-in search that indexes:
- Page titles and content
- Code blocks and comments
- Headers and links

### Version Control
- Full Git history for all wiki changes
- Ability to view diffs and revert changes
- Branch protection for wiki repository

### Access Control
- Same permissions as main repository
- Can be configured separately if needed
- Supports private wikis for private repositories

## Customization Options

### Styling
- GitHub wiki uses GitHub Flavored Markdown
- Supports syntax highlighting for 100+ languages
- Custom CSS through organization settings (if available)

### Templates
Create page templates for consistency:

```markdown
# Page Title

Brief description of the page content.

## Overview
[High-level summary]

## Detailed Information
[Main content sections]

## Examples
[Code examples and usage]

## Related Pages
- [Link to related page](Related-Page)
```

### Interactive Elements
- Collapsible sections using `<details>` tags
- Tables with sorting capabilities
- Embedded diagrams with mermaid syntax

## Maintenance

### Regular Updates
- Keep documentation in sync with code changes
- Update version numbers and dates
- Refresh screenshots and examples

### Quality Assurance
- Review links for accuracy
- Test code examples
- Verify installation instructions

### Community Contributions
- Enable wiki editing for contributors
- Set up review process for major changes
- Maintain style guide for consistency

## Integration with Development

### Documentation as Code
- Store documentation alongside source code
- Include documentation updates in pull requests
- Use documentation reviews as part of code review process

### Automated Checks
```yaml
# Check for broken links
- name: Check markdown links
  uses: gaurav-nelson/github-action-markdown-link-check@v1
  with:
    use-quiet-mode: 'yes'
```

### Release Notes Integration
- Link wiki pages to specific releases
- Maintain changelog in wiki format
- Cross-reference features with documentation

This documentation structure provides comprehensive coverage of the Multi-Agent Assistant System while being easily maintainable and navigable as a GitHub wiki.