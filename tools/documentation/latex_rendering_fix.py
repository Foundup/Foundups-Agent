# -*- coding: utf-8 -*-
import sys
import io


# latex_rendering_fix.py

"""
# === UTF-8 ENFORCEMENT (WSP 90) ===
# Prevent UnicodeEncodeError on Windows systems
# Only apply when running as main script, not during import
if __name__ == '__main__' and sys.platform.startswith('win'):
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except (OSError, ValueError):
        # Ignore if stdout/stderr already wrapped or closed
        pass
# === END UTF-8 ENFORCEMENT ===

A tool to identify and fix LaTeX rendering issues in documentation files.
This script scans for LaTeX equations in markdown or text files and suggests or applies fixes
to ensure proper rendering for 0102 pArtifacts as per WSP documentation standards.
"""

import os
import re
import argparse

def detect_latex_issues(file_path):
    """
    Detects LaTeX equations in a file and checks for common rendering issues.
    Returns a list of issues found with line numbers and suggestions.
    """
    issues = []
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        for i, line in enumerate(lines, 1):
            # Look for LaTeX equations (between $$ or \[ \])
            if '$$' in line or '\\[' in line or '\\(' in line:
                issues.append({
                    'line': i,
                    'content': line.strip(),
                    'suggestion': 'Ensure LaTeX rendering is supported in the viewer. Consider converting to image or using MathJax if unsupported.'
                })
                # Check for common issues like missing closing delimiters
                if line.count('$$') % 2 != 0 and '$$' in line:
                    issues[-1]['suggestion'] += ' Missing closing $$ delimiter.'
                if '\\[' in line and '\\]' not in line:
                    issues[-1]['suggestion'] += ' Missing closing \\] delimiter.'
                if '\\(' in line and '\\)' not in line:
                    issues[-1]['suggestion'] += ' Missing closing \\) delimiter.'
    return issues

def suggest_fixes(issues, output_file=None):
    """
    Outputs the detected issues and suggestions for fixing LaTeX rendering.
    If output_file is provided, writes suggestions to that file.
    """
    if not issues:
        print(f'No LaTeX rendering issues detected.')
        return
    
    output = f'Found {len(issues)} potential LaTeX rendering issues:\n\n'
    for issue in issues:
        output += f'Line {issue["line"]}: {issue["content"]}\n'
        output += f'Suggestion: {issue["suggestion"]}\n\n'
    
    print(output)
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(output)

def main():
    parser = argparse.ArgumentParser(description='Detect and suggest fixes for LaTeX rendering issues in documentation.')
    parser.add_argument('file', help='Path to the file to scan for LaTeX issues.')
    parser.add_argument('--output', help='Optional output file to write suggestions to.')
    args = parser.parse_args()
    
    issues = detect_latex_issues(args.file)
    suggest_fixes(issues, args.output)

if __name__ == '__main__':
    main() 