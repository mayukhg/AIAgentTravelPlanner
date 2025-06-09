# Enable GitHub Wiki - Step by Step

## Why Wiki Tab Isn't Visible

The wiki feature is disabled by default in GitHub repositories. You need to enable it first.

## Steps to Enable Wiki

### 1. Navigate to Repository Settings
- Go to: https://github.com/mayukhg/AIAgentTravelPlanner
- Click the "Settings" tab (located at the top of the repository page)

### 2. Find Features Section
- Scroll down to the "Features" section (about halfway down the settings page)
- Look for the "Wiki" checkbox

### 3. Enable Wiki
- Check the box next to "Wiki"
- The setting saves automatically

### 4. Verify Wiki Tab Appears
- Go back to your repository main page
- You should now see a "Wiki" tab next to "Code", "Issues", "Pull requests", etc.

## After Enabling Wiki

Once the wiki tab appears, you have two deployment options:

### Option A: Quick Manual Deployment
```bash
# Clone the wiki repository
git clone https://github.com/mayukhg/AIAgentTravelPlanner.wiki.git

# Copy the prepared documentation
cp wiki-deploy/*.md AIAgentTravelPlanner.wiki/

# Deploy to GitHub
cd AIAgentTravelPlanner.wiki
git add .
git commit -m "Deploy comprehensive documentation"
git push origin master
```

### Option B: Enable Auto-Sync (Recommended)
```bash
# Add the GitHub Actions workflow for automatic updates
git add .github/workflows/sync-wiki.yml
git commit -m "Add automated wiki sync"
git push origin main
```

Then manually trigger the workflow or push any change to the docs/ folder.

## Troubleshooting

**If Settings tab is not visible:**
- You need admin or write access to the repository
- Contact the repository owner to enable wiki

**If Wiki checkbox is not in Features:**
- Ensure you're in the correct repository settings
- Some organization repositories may have restrictions

**If Wiki tab still doesn't appear:**
- Refresh the page after enabling
- Check browser cache and refresh again

## Verification

After enabling wiki, you should see:
1. Wiki tab in repository navigation
2. Empty wiki with "Create the first page" button
3. Ability to create and edit wiki pages

Your comprehensive documentation (11 pages) is ready to deploy once the wiki is enabled.