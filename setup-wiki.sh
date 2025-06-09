#!/bin/bash

# GitHub Wiki Setup Script for Multi-Agent Assistant System
# This script helps set up the GitHub wiki with comprehensive documentation

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    print_error "This script must be run from the root of a git repository."
    exit 1
fi

# Get repository information
REPO_URL=$(git config --get remote.origin.url)
if [[ $REPO_URL == *"github.com"* ]]; then
    # Extract owner/repo from URL
    if [[ $REPO_URL == *".git" ]]; then
        REPO_PATH=$(echo $REPO_URL | sed 's/.*github\.com[:/]\(.*\)\.git/\1/')
    else
        REPO_PATH=$(echo $REPO_URL | sed 's/.*github\.com[:/]\(.*\)/\1/')
    fi
    WIKI_URL="https://github.com/${REPO_PATH}.wiki.git"
else
    print_error "This repository is not hosted on GitHub."
    exit 1
fi

print_status "Repository: $REPO_PATH"
print_status "Wiki URL: $WIKI_URL"

# Check if docs directory exists
if [ ! -d "docs" ]; then
    print_error "docs/ directory not found. Please ensure documentation files are in the docs/ folder."
    exit 1
fi

print_status "Found docs/ directory with $(ls docs/*.md 2>/dev/null | wc -l) documentation files"

# Function to setup wiki manually
setup_manual() {
    print_status "Setting up wiki manually..."
    
    # Check if wiki directory already exists
    if [ -d "wiki" ]; then
        print_warning "wiki/ directory already exists. Removing it..."
        rm -rf wiki
    fi
    
    # Clone or initialize wiki
    print_status "Cloning wiki repository..."
    if git clone "$WIKI_URL" wiki 2>/dev/null; then
        print_success "Wiki repository cloned successfully"
    else
        print_warning "Wiki doesn't exist yet. Creating new wiki..."
        mkdir wiki
        cd wiki
        git init
        git remote add origin "$WIKI_URL"
        
        # Create initial Home page
        echo "# Multi-Agent Assistant System Wiki" > Home.md
        echo "" >> Home.md
        echo "Welcome to the documentation wiki. This will be updated with comprehensive documentation." >> Home.md
        
        git add Home.md
        git commit -m "Initialize wiki"
        
        # Try to push (this will create the wiki)
        if git push -u origin master 2>/dev/null || git push -u origin main 2>/dev/null; then
            print_success "Wiki initialized successfully"
        else
            print_error "Failed to initialize wiki. Please enable wiki in repository settings first."
            cd ..
            rm -rf wiki
            exit 1
        fi
        cd ..
    fi
    
    # Copy documentation files
    print_status "Copying documentation files..."
    cd wiki
    
    # Remove existing markdown files (except .git)
    find . -name "*.md" -not -path "./.git/*" -delete 2>/dev/null || true
    
    # Copy all documentation
    cp ../docs/*.md .
    
    # Remove the docs README.md as it's not needed in wiki
    rm -f README.md
    
    # Add and commit changes
    git add .
    
    if git diff --staged --quiet; then
        print_warning "No changes to commit"
    else
        git commit -m "Add comprehensive documentation from docs/ folder"
        if git push; then
            print_success "Documentation pushed to wiki successfully"
        else
            print_error "Failed to push documentation to wiki"
            exit 1
        fi
    fi
    
    cd ..
    
    print_success "Wiki setup completed!"
    print_status "You can view your wiki at: https://github.com/${REPO_PATH}/wiki"
}

# Function to setup GitHub Actions workflow
setup_automation() {
    print_status "Setting up automated wiki sync..."
    
    if [ ! -f ".github/workflows/sync-wiki.yml" ]; then
        print_error "GitHub Actions workflow file not found. Please ensure .github/workflows/sync-wiki.yml exists."
        exit 1
    fi
    
    print_success "GitHub Actions workflow is already configured"
    print_status "The workflow will automatically sync docs/ to wiki on every push to main/master"
    print_status "You can also trigger it manually from the Actions tab in GitHub"
}

# Function to validate documentation
validate_docs() {
    print_status "Validating documentation files..."
    
    required_files=(
        "Home.md"
        "Installation.md"
        "User-Guide.md"
        "API-Reference.md"
        "System-Architecture.md"
        "Agent-Framework.md"
        "Configuration.md"
        "Development-Guide.md"
        "Database-Schema.md"
        "Security-Guidelines.md"
        "Troubleshooting.md"
    )
    
    missing_files=()
    
    for file in "${required_files[@]}"; do
        if [ ! -f "docs/$file" ]; then
            missing_files+=("$file")
        fi
    done
    
    if [ ${#missing_files[@]} -eq 0 ]; then
        print_success "All required documentation files are present"
    else
        print_warning "Missing documentation files:"
        for file in "${missing_files[@]}"; do
            echo "  - $file"
        done
    fi
    
    # Check for broken internal links (basic check)
    print_status "Checking for potential internal link issues..."
    cd docs
    for file in *.md; do
        # Look for markdown links that might be broken
        grep -n '\[.*\](.*\.md)' "$file" 2>/dev/null | while read -r line; do
            link=$(echo "$line" | sed 's/.*\[.*\](\(.*\.md\)).*/\1/')
            if [ ! -f "$link" ]; then
                print_warning "Potential broken link in $file: $link"
            fi
        done
    done
    cd ..
}

# Main execution
print_status "GitHub Wiki Setup for Multi-Agent Assistant System"
print_status "=================================================="

# Validate documentation first
validate_docs

echo ""
print_status "Choose setup method:"
echo "1) Manual setup (clone wiki and copy files)"
echo "2) Setup GitHub Actions automation only"
echo "3) Both manual setup and automation"
echo "4) Just validate documentation"

read -p "Enter your choice (1-4): " choice

case $choice in
    1)
        setup_manual
        ;;
    2)
        setup_automation
        ;;
    3)
        setup_manual
        setup_automation
        ;;
    4)
        print_success "Documentation validation completed"
        ;;
    *)
        print_error "Invalid choice"
        exit 1
        ;;
esac

echo ""
print_success "Setup completed!"
print_status "Next steps:"
echo "  1. Enable wiki in your GitHub repository settings (if not already enabled)"
echo "  2. Visit your wiki at: https://github.com/${REPO_PATH}/wiki"
echo "  3. If using automation, push changes to trigger wiki sync"
echo "  4. Customize the Home page as needed"

# Clean up wiki directory if it exists
if [ -d "wiki" ]; then
    read -p "Remove local wiki directory? (y/n): " cleanup
    if [[ $cleanup == "y" || $cleanup == "Y" ]]; then
        rm -rf wiki
        print_status "Local wiki directory removed"
    fi
fi