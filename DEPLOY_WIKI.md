# GitHub Wiki Deployment Instructions

## Pre-Deployment Checklist

Your documentation is ready for deployment with:
- ✅ 12 comprehensive documentation pages
- ✅ All internal links validated and working
- ✅ Professional structure and navigation
- ✅ Automated sync workflow configured

## Deployment Options

### Option 1: Automated GitHub Actions Deployment (Recommended)

This method automatically deploys your wiki whenever you push changes to the docs folder.

1. **Enable Wiki in GitHub Repository**:
   - Go to: `https://github.com/mayukhg/AIAgentTravelPlanner/settings`
   - Scroll to "Features" section
   - Check "Wiki" to enable it

2. **Commit the GitHub Actions Workflow**:
   ```bash
   git add .github/workflows/sync-wiki.yml
   git commit -m "Add automated wiki sync workflow"
   git push origin main
   ```

3. **Trigger Initial Deployment**:
   ```bash
   git add docs/
   git commit -m "Add comprehensive documentation for wiki"
   git push origin main
   ```

4. **Monitor Deployment**:
   - Go to: `https://github.com/mayukhg/AIAgentTravelPlanner/actions`
   - Watch the "Sync Documentation to Wiki" workflow execute

### Option 2: Manual Wiki Deployment

If you prefer manual control over the deployment:

1. **Enable Wiki** (same as Option 1, step 1)

2. **Clone Wiki Repository**:
   ```bash
   git clone https://github.com/mayukhg/AIAgentTravelPlanner.wiki.git
   cd AIAgentTravelPlanner.wiki
   ```

3. **Copy Documentation Files**:
   ```bash
   cp ../docs/*.md .
   rm README.md  # Remove docs README (not needed in wiki)
   ```

4. **Deploy to Wiki**:
   ```bash
   git add .
   git commit -m "Deploy comprehensive Multi-Agent Assistant documentation"
   git push origin master
   ```

### Option 3: Using the Automated Setup Script

Run the provided setup script for guided deployment:

```bash
chmod +x setup-wiki.sh
./setup-wiki.sh
```

Choose option 1 (Manual setup) or 3 (Both manual and automation).

## Verification Steps

After deployment, verify your wiki:

1. **Visit Your Wiki**: `https://github.com/mayukhg/AIAgentTravelPlanner/wiki`

2. **Check Navigation**: 
   - Home page should display complete navigation
   - All internal links should work correctly
   - Each page should be accessible

3. **Test Key Pages**:
   - Installation guide has complete setup instructions
   - API Reference includes all endpoints with examples
   - User Guide provides comprehensive usage instructions

## Expected Wiki Structure

Your deployed wiki will include:

```
Home - Main navigation and system overview
├── Getting Started
│   ├── Installation - Complete setup guide
│   ├── Configuration - Environment setup
│   └── User Guide - How to use the system
├── Architecture & Design
│   ├── System Architecture - Design patterns
│   ├── Agent Framework - Multi-agent details
│   └── Database Schema - Data models
├── API Documentation
│   └── API Reference - REST API with examples
├── Development
│   ├── Development Guide - For contributors
│   └── Troubleshooting - Common issues
└── Security & Operations
    └── Security Guidelines - Best practices
```

## Post-Deployment Configuration

### Customize Home Page
Edit `docs/Home.md` to add project-specific information:
- Update repository links
- Add specific installation requirements
- Include project status or roadmap

### Set Up Monitoring
- Enable GitHub repository insights to track wiki usage
- Monitor the GitHub Actions workflow for sync issues
- Set up notifications for wiki edits (if needed)

### Team Access
Configure wiki permissions in repository settings:
- Public repositories: Wiki is publicly readable
- Private repositories: Inherits repository permissions
- Organization repositories: Configure team access

## Troubleshooting Deployment

### Common Issues

**Wiki not appearing after enabling**:
- Ensure at least one page exists (Home.md)
- Check that wiki is enabled in repository settings
- Verify you have push permissions to the repository

**GitHub Actions workflow failing**:
- Check Actions tab for specific error messages
- Ensure GITHUB_TOKEN has sufficient permissions
- Verify workflow file syntax in `.github/workflows/sync-wiki.yml`

**Links not working in wiki**:
- Internal links should not include `.md` extension
- Use relative links: `[Page Name](Page-Name)`
- Ensure target pages exist

### Recovery Steps

If deployment fails:

1. **Check Wiki Status**:
   ```bash
   curl -I https://github.com/mayukhg/AIAgentTravelPlanner/wiki
   ```

2. **Validate Documentation**:
   ```bash
   python3 scripts/validate-wiki.py
   ```

3. **Re-run Setup**:
   ```bash
   ./setup-wiki.sh
   ```

## Maintenance

### Updating Documentation
1. Edit files in `docs/` folder
2. Commit and push changes
3. GitHub Actions automatically syncs to wiki (if enabled)

### Manual Sync
If using manual deployment, repeat Option 2 steps to update wiki.

## Success Indicators

Your wiki deployment is successful when:
- ✅ Wiki is accessible at the GitHub URL
- ✅ All navigation links work correctly
- ✅ Pages display properly formatted content
- ✅ Search functionality works across all pages
- ✅ Mobile display is responsive

## Next Steps

After successful deployment:
1. Share wiki URL with team members
2. Add wiki link to repository README
3. Set up documentation update procedures
4. Consider adding wiki link to project website

Your comprehensive documentation is now live and accessible to users and contributors.