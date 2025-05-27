#!/usr/bin/env python3
"""
SQL Query Checker for Email Fields

This script scans all Python files to find SQL queries that directly use email fields,
which won't work with encrypted data.
"""

import os
import re
import glob

def scan_file_for_email_queries(filepath):
    """Scan a file for problematic SQL queries using email fields."""
    issues = []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
        
        # Patterns to look for
        patterns = [
            # Direct email field comparisons
            (r'\.filter.*Email\s*==', 'Direct email field comparison in filter'),
            (r'WHERE.*Email\s*=', 'Direct email field comparison in WHERE clause'),
            (r'JOIN.*Email\s*=', 'Direct email field comparison in JOIN'),
            # SQL queries with email fields
            (r'SELECT.*FROM.*WHERE.*Email', 'SELECT with email field in WHERE'),
            (r'UPDATE.*SET.*Email', 'UPDATE with email field'),
            (r'INSERT.*Email', 'INSERT with email field'),
        ]
        
        for i, line in enumerate(lines, 1):
            for pattern, description in patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    # Skip comments and documentation
                    stripped = line.strip()
                    if not stripped.startswith('#') and not stripped.startswith('"""') and not stripped.startswith("'''"):
                        issues.append({
                            'file': filepath,
                            'line': i,
                            'content': line.strip(),
                            'issue': description
                        })
    
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
    
    return issues

def main():
    """Scan all Python files for email-related SQL issues."""
    print("🔍 SCANNING FOR SQL QUERIES WITH DIRECT EMAIL FIELD USAGE")
    print("=" * 60)
    
    # Get all Python files
    python_files = []
    for root, dirs, files in os.walk('.'):
        # Skip virtual environments and cache directories
        dirs[:] = [d for d in dirs if d not in ['venv', '__pycache__', '.git', 'node_modules']]
        
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    all_issues = []
    
    for filepath in python_files:
        issues = scan_file_for_email_queries(filepath)
        all_issues.extend(issues)
    
    if not all_issues:
        print("✅ No problematic SQL queries found!")
        print("All email field usage appears to be properly handled with encryption.")
        return True
    
    print(f"❌ Found {len(all_issues)} potential issues:")
    print()
    
    # Group by file
    files_with_issues = {}
    for issue in all_issues:
        filepath = issue['file']
        if filepath not in files_with_issues:
            files_with_issues[filepath] = []
        files_with_issues[filepath].append(issue)
    
    for filepath, issues in files_with_issues.items():
        print(f"📄 {filepath}")
        for issue in issues:
            print(f"  Line {issue['line']}: {issue['issue']}")
            print(f"    {issue['content']}")
        print()
    
    print("🔧 RECOMMENDATIONS:")
    print("- Replace direct email field comparisons with encrypted email search")
    print("- Use service layer functions that handle encryption/decryption")
    print("- For queries, get all records and filter by decrypted emails")
    
    return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 