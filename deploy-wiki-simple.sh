#!/bin/bash

# Simple GitHub Wiki Deployment Script
# This script prepares everything for manual deployment

set -e

echo "🚀 GitHub Wiki Deployment Preparation"
echo "====================================="

# Check if we're in the right directory
if [ ! -d "docs" ]; then
    echo "❌ Error: docs/ directory not found"
    echo "Please run this script from the project root directory"
    exit 1
fi

# Validate documentation first
echo "📋 Validating documentation..."
if command -v python3 &> /dev/null; then
    python3 scripts/validate-wiki.py
    if [ $? -ne 0 ]; then
        echo "❌ Documentation validation failed"
        exit 1
    fi
else
    echo "⚠️  Python3 not found, skipping validation"
fi

# Prepare deployment directory
echo "📁 Preparing deployment files..."
rm -rf wiki-deploy
mkdir -p wiki-deploy

# Copy all documentation files except README.md
cp docs/*.md wiki-deploy/
rm -f wiki-deploy/README.md

echo "✅ Wiki files prepared in wiki-deploy/ directory"
echo ""
echo "🔧 Manual Deployment Steps:"
echo "=========================="
echo ""
echo "1. Enable Wiki in GitHub:"
echo "   - Go to: https://github.com/mayukhg/AIAgentTravelPlanner/settings"
echo "   - Under 'Features', check 'Wiki'"
echo ""
echo "2. Clone your wiki repository:"
echo "   git clone https://github.com/mayukhg/AIAgentTravelPlanner.wiki.git"
echo ""
echo "3. Copy the prepared files:"
echo "   cp wiki-deploy/*.md AIAgentTravelPlanner.wiki/"
echo ""
echo "4. Deploy to GitHub:"
echo "   cd AIAgentTravelPlanner.wiki"
echo "   git add ."
echo "   git commit -m 'Deploy comprehensive documentation'"
echo "   git push origin master"
echo ""
echo "5. Visit your wiki:"
echo "   https://github.com/mayukhg/AIAgentTravelPlanner/wiki"
echo ""
echo "📊 Documentation Summary:"
echo "- $(ls wiki-deploy/*.md | wc -l) documentation pages ready"
echo "- Home page with complete navigation"
echo "- API reference with examples"
echo "- Installation and user guides"
echo "- Development and security documentation"
echo ""
echo "🔄 For automatic updates in the future:"
echo "- Commit .github/workflows/sync-wiki.yml to enable auto-sync"
echo "- Future changes to docs/ will automatically update the wiki"

# List all files being deployed
echo ""
echo "📄 Files ready for deployment:"
for file in wiki-deploy/*.md; do
    filename=$(basename "$file")
    echo "   ✓ $filename"
done

echo ""
echo "🎯 Ready for deployment! Follow the manual steps above."