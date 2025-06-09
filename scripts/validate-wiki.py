#!/usr/bin/env python3
"""
Wiki Documentation Validator
Validates the integrity and completeness of wiki documentation files.
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Dict, Set

class WikiValidator:
    def __init__(self, docs_dir: str = "docs"):
        self.docs_dir = Path(docs_dir)
        self.errors = []
        self.warnings = []
        
        # Required files for complete documentation
        self.required_files = {
            "Home.md": "Main wiki homepage",
            "Installation.md": "Installation and setup guide",
            "User-Guide.md": "User documentation",
            "API-Reference.md": "API documentation",
            "System-Architecture.md": "System design documentation",
            "Agent-Framework.md": "Agent system documentation",
            "Configuration.md": "Configuration reference",
            "Development-Guide.md": "Developer documentation",
            "Database-Schema.md": "Database documentation",
            "Security-Guidelines.md": "Security documentation",
            "Troubleshooting.md": "Troubleshooting guide"
        }
    
    def validate_file_existence(self) -> None:
        """Check that all required documentation files exist."""
        print("Validating file existence...")
        
        missing_files = []
        for filename, description in self.required_files.items():
            file_path = self.docs_dir / filename
            if not file_path.exists():
                missing_files.append(f"{filename} - {description}")
        
        if missing_files:
            self.errors.append("Missing required files:")
            for file in missing_files:
                self.errors.append(f"  - {file}")
        else:
            print("✓ All required files present")
    
    def validate_internal_links(self) -> None:
        """Check for broken internal links between documentation pages."""
        print("Validating internal links...")
        
        # Get all existing markdown files
        existing_files = {f.stem for f in self.docs_dir.glob("*.md")}
        broken_links = []
        
        for md_file in self.docs_dir.glob("*.md"):
            content = md_file.read_text(encoding='utf-8')
            
            # Find markdown links [text](target)
            link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
            links = re.findall(link_pattern, content)
            
            for link_text, link_target in links:
                # Skip external links (http/https)
                if link_target.startswith(('http://', 'https://')):
                    continue
                
                # Skip anchor links
                if link_target.startswith('#'):
                    continue
                
                # Check if target file exists (remove .md extension if present)
                target_file = link_target.replace('.md', '')
                if target_file not in existing_files:
                    broken_links.append(f"{md_file.name}: [{link_text}]({link_target})")
        
        if broken_links:
            self.errors.append("Broken internal links found:")
            for link in broken_links:
                self.errors.append(f"  - {link}")
        else:
            print("✓ All internal links valid")
    
    def validate_content_structure(self) -> None:
        """Validate that files have proper structure and content."""
        print("Validating content structure...")
        
        structure_issues = []
        
        for md_file in self.docs_dir.glob("*.md"):
            content = md_file.read_text(encoding='utf-8')
            lines = content.split('\n')
            
            # Check for title (H1 header)
            has_title = any(line.startswith('# ') for line in lines[:10])
            if not has_title:
                structure_issues.append(f"{md_file.name}: Missing H1 title")
            
            # Check minimum content length
            if len(content.strip()) < 500:
                self.warnings.append(f"{md_file.name}: Very short content ({len(content)} chars)")
            
            # Check for code blocks without language specification
            code_blocks = re.findall(r'```(\w*)', content)
            unnamed_blocks = [block for block in code_blocks if not block]
            if unnamed_blocks:
                self.warnings.append(f"{md_file.name}: {len(unnamed_blocks)} code blocks without language specification")
        
        if structure_issues:
            self.errors.append("Content structure issues:")
            for issue in structure_issues:
                self.errors.append(f"  - {issue}")
        else:
            print("✓ Content structure valid")
    
    def validate_cross_references(self) -> None:
        """Check that important topics are cross-referenced appropriately."""
        print("Validating cross-references...")
        
        # Key topics that should be mentioned across files
        cross_ref_checks = {
            "Installation": ["Home.md", "User-Guide.md", "Development-Guide.md"],
            "Configuration": ["Installation.md", "Development-Guide.md", "Security-Guidelines.md"],
            "API": ["Home.md", "User-Guide.md", "Development-Guide.md"],
            "Security": ["Configuration.md", "Development-Guide.md", "Troubleshooting.md"]
        }
        
        missing_refs = []
        
        for topic, should_mention_in in cross_ref_checks.items():
            for filename in should_mention_in:
                file_path = self.docs_dir / filename
                if file_path.exists():
                    content = file_path.read_text(encoding='utf-8').lower()
                    if topic.lower() not in content:
                        missing_refs.append(f"{filename}: Should reference '{topic}'")
        
        if missing_refs:
            self.warnings.append("Missing cross-references:")
            for ref in missing_refs:
                self.warnings.append(f"  - {ref}")
        else:
            print("✓ Cross-references look good")
    
    def validate_home_page(self) -> None:
        """Validate that the Home page has proper navigation structure."""
        print("Validating Home page navigation...")
        
        home_file = self.docs_dir / "Home.md"
        if not home_file.exists():
            self.errors.append("Home.md is missing")
            return
        
        content = home_file.read_text(encoding='utf-8')
        
        # Check for navigation links to major sections
        required_nav_links = [
            "Installation", "User-Guide", "API-Reference", 
            "System-Architecture", "Development-Guide"
        ]
        
        missing_nav = []
        for nav_item in required_nav_links:
            if nav_item not in content:
                missing_nav.append(nav_item)
        
        if missing_nav:
            self.warnings.append("Home page missing navigation links:")
            for item in missing_nav:
                self.warnings.append(f"  - {item}")
        else:
            print("✓ Home page navigation complete")
    
    def generate_report(self) -> None:
        """Generate validation report."""
        print("\n" + "="*60)
        print("WIKI DOCUMENTATION VALIDATION REPORT")
        print("="*60)
        
        if not self.errors and not self.warnings:
            print("✅ All validation checks passed!")
            print("Your documentation is ready for GitHub wiki.")
            return
        
        if self.errors:
            print("\n🚨 ERRORS (must be fixed):")
            for error in self.errors:
                print(f"   {error}")
        
        if self.warnings:
            print("\n⚠️  WARNINGS (recommended to fix):")
            for warning in self.warnings:
                print(f"   {warning}")
        
        print(f"\nSummary: {len(self.errors)} errors, {len(self.warnings)} warnings")
        
        if self.errors:
            print("\nPlease fix all errors before setting up the wiki.")
            sys.exit(1)
        else:
            print("\nDocumentation is ready! Warnings are optional improvements.")
    
    def run_validation(self) -> None:
        """Run all validation checks."""
        if not self.docs_dir.exists():
            print(f"❌ Documentation directory '{self.docs_dir}' not found!")
            sys.exit(1)
        
        print(f"Validating documentation in '{self.docs_dir}'...")
        print("-" * 50)
        
        self.validate_file_existence()
        self.validate_internal_links()
        self.validate_content_structure()
        self.validate_cross_references()
        self.validate_home_page()
        
        self.generate_report()

def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Validate wiki documentation")
    parser.add_argument("--docs-dir", default="docs", 
                       help="Documentation directory (default: docs)")
    parser.add_argument("--verbose", action="store_true",
                       help="Show detailed validation output")
    
    args = parser.parse_args()
    
    validator = WikiValidator(args.docs_dir)
    validator.run_validation()

if __name__ == "__main__":
    main()