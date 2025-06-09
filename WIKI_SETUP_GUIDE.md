# GitHub Wiki Setup Guide

Complete guide for setting up the GitHub wiki with the comprehensive documentation created for the Multi-Agent Assistant System.

## Quick Start Options

### Option 1: Automated Setup (Recommended)

Run the provided setup script:

```bash
./setup-wiki.sh
```

This script will:
- Validate your documentation files
- Clone or initialize the wiki repository
- Copy all documentation to the wiki
- Set up automated syncing via GitHub Actions

### Option 2: Manual Setup

1. **Enable Wiki in GitHub**:
   - Go to your repository on GitHub
   - Click Settings → Features → Wiki → Enable

2. **Clone Wiki Repository**:
   ```bash
   git clone https://github.com/your-username/your-repo.wiki.git
   cd your-repo.wiki
   ```

3. **Copy Documentation**:
   ```bash
   cp ../docs/*.md .
   rm README.md  # Remove docs README as it's not needed in wiki
   ```

4. **Push to Wiki**:
   ```bash
   git add .
   git commit -m "Add comprehensive documentation"
   git push origin master
   ```

## GitHub Actions Automation

The provided workflow (`.github/workflows/sync-wiki.yml`) automatically syncs the `docs/` folder to your wiki whenever you push changes.

### Features:
- Triggers on changes to `docs/` folder
- Handles wiki initialization if it doesn't exist
- Removes old files and replaces with updated documentation
- Can be triggered manually from GitHub Actions tab

### Setup Requirements:
1. GitHub Actions must be enabled in your repository
2. Wiki must be enabled in repository settings
3. Default permissions for GITHUB_TOKEN are sufficient

## Documentation Structure

The wiki includes these comprehensive pages:

### Core Pages
- **Home** - Main navigation and system overview
- **Installation** - Complete setup instructions
- **User Guide** - How to use the assistant effectively
- **API Reference** - REST API documentation with examples

### Technical Documentation
- **System Architecture** - Design patterns and component interactions
- **Agent Framework** - Multi-agent system details
- **Database Schema** - Complete data model documentation
- **Configuration** - Environment and service configuration

### Operations
- **Security Guidelines** - Comprehensive security best practices
- **Troubleshooting** - Common issues and solutions
- **Development Guide** - For contributors and developers

## Navigation Features

### Internal Linking
All pages are cross-referenced with internal links:
```markdown
See the [Installation Guide](Installation) for setup instructions.
```

### Search Integration
GitHub wiki includes full-text search across:
- Page content and titles
- Code blocks and examples
- Headers and documentation

### Mobile Responsive
All documentation is formatted for optimal viewing on desktop and mobile devices.

## Maintenance

### Keeping Documentation Updated

1. **Edit files in `docs/` folder** in your main repository
2. **Commit and push changes** to trigger automatic sync
3. **Manual sync**: Run `./setup-wiki.sh` if needed

### Content Standards
- Use consistent heading structure (H1 for page titles)
- Include code examples with language specification
- Cross-reference related topics
- Keep installation instructions current

## Advanced Configuration

### Custom Workflows

Modify `.github/workflows/sync-wiki.yml` to:
- Change trigger conditions
- Add content validation
- Include additional processing steps

### Wiki Templates

Create consistent page templates:
```markdown
# Page Title

Brief description of the content.

## Overview
High-level summary of the topic.

## Detailed Information
Main content sections with examples.

## Related Pages
- [Related Topic 1](Related-Topic-1)
- [Related Topic 2](Related-Topic-2)
```

### Access Control

Wiki permissions follow your repository settings:
- **Public repos**: Wiki is publicly readable
- **Private repos**: Wiki inherits repository permissions
- **Organization repos**: Can configure team access

## Troubleshooting Setup

### Common Issues

**Wiki not appearing after setup**:
- Ensure wiki is enabled in repository settings
- Check that at least one page exists (Home.md)
- Verify push was successful

**GitHub Actions failing**:
- Check Actions tab for error details
- Ensure GITHUB_TOKEN has sufficient permissions
- Verify workflow file syntax

**Links not working**:
- Use relative links without `.md` extension
- Check that target pages exist
- Ensure consistent file naming

### Validation Commands

Check documentation integrity:
```bash
# Validate all required files exist
ls docs/Home.md docs/Installation.md docs/User-Guide.md

# Check for broken internal links
grep -r "\]\(" docs/ | grep "\.md"

# Verify GitHub Actions workflow
cat .github/workflows/sync-wiki.yml
```

## Next Steps

After setup:

1. **Test the wiki** by visiting `https://github.com/your-username/your-repo/wiki`
2. **Customize the Home page** with your project-specific information
3. **Set up monitoring** for documentation updates
4. **Train contributors** on the documentation update process

The wiki provides comprehensive documentation that grows with your project while maintaining professional presentation and easy navigation.