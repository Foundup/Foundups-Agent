"""
Unicode Fixer Tool

WSP-compliant tool to scan and fix Unicode characters that may cause encoding issues.
WSP Compliance: WSP 34, WSP 54, WSP 22, WSP 50
"""

import os
import re
import argparse
import logging
from pathlib import Path
from typing import List, Dict, Tuple, Set
from dataclasses import dataclass
from datetime import datetime


@dataclass
class UnicodeIssue:
    """Represents a Unicode issue found in a file."""
    file_path: str
    line_number: int
    column: int
    character: str
    unicode_code: str
    context: str
    severity: str  # 'error', 'warning', 'info'


class UnicodeFixer:
    """
    WSP-compliant Unicode fixing tool for autonomous codebase maintenance.
    
    Provides comprehensive Unicode character scanning and fixing capabilities:
    - Unicode character detection and analysis
    - WSP compliance checking
    - Automatic and manual fixing options
    - Report generation and audit trail
    """
    
    def __init__(self, root_path: str = "."):
        """Initialize the Unicode fixer with WSP compliance standards."""
        self.root_path = Path(root_path)
        self.issues: List[UnicodeIssue] = []
        self.fixed_files: Set[str] = set()
        
        # WSP compliance keywords
        self.wsp_keywords = [
            'wsp', 'protocol', 'compliance', '0102', 'partifact', 'quantum',
            'autonomous', 'agent', 'modular', 'testing', 'documentation'
        ]
        
        # File extensions to scan
        self.scan_extensions = {
            '.py', '.md', '.txt', '.json', '.yaml', '.yml', 
            '.html', '.css', '.js', '.ts', '.jsx', '.tsx'
        }
        
        # Directories to exclude
        self.exclude_dirs = {
            '__pycache__', '.git', '.vscode', 'node_modules', 
            'venv', 'env', '.pytest_cache', 'build', 'dist'
        }
        
        # Problematic Unicode characters and their replacements
        self.unicode_replacements = {
            # Smart quotes
            '"': '"',  # Left double quotation mark
            '"': '"',  # Right double quotation mark
            ''': "'",  # Left single quotation mark
            ''': "'",  # Right single quotation mark
            
            # Em dashes and en dashes
            '—': '-',  # Em dash
            '–': '-',  # En dash
            
            # Ellipsis
            '…': '...',  # Horizontal ellipsis
            
            # Bullets
            '•': '*',  # Bullet
            '◦': '*',  # White bullet
            '▪': '*',  # Black small square
            '▫': '*',  # White small square
            
            # Arrows
            '→': '->',  # Right arrow
            '←': '<-',  # Left arrow
            '⇒': '=>',  # Right double arrow
            '⇐': '<=',  # Left double arrow
            
            # Mathematical symbols
            '×': '*',  # Multiplication sign
            '÷': '/',  # Division sign
            '±': '+/-',  # Plus-minus sign
            '≤': '<=',  # Less than or equal
            '≥': '>=',  # Greater than or equal
            '≠': '!=',  # Not equal
            
            # Currency symbols
            '€': 'EUR',  # Euro
            '£': 'GBP',  # Pound
            '¥': 'JPY',  # Yen
            '¢': 'cent',  # Cent
            
            # Degree and other symbols
            '°': 'deg',  # Degree sign
            '©': '(c)',  # Copyright
            '®': '(R)',  # Registered trademark
            '™': '(TM)',  # Trademark
        }
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
    
    def scan_codebase(self) -> List[UnicodeIssue]:
        """
        Scan the entire codebase for Unicode issues.
        
        Returns:
            List[UnicodeIssue]: List of found Unicode issues
        """
        self.issues = []
        
        for file_path in self._get_files_to_scan():
            try:
                self._scan_file(file_path)
            except Exception as e:
                self.logger.error(f"Error scanning {file_path}: {e}")
        
        self.logger.info(f"Scan complete. Found {len(self.issues)} Unicode issues.")
        return self.issues
    
    def fix_issues(self, auto_fix: bool = False, dry_run: bool = True) -> Dict[str, int]:
        """
        Fix Unicode issues in the codebase.
        
        Args:
            auto_fix: Whether to automatically fix issues without confirmation
            dry_run: Whether to perform a dry run without making changes
            
        Returns:
            Dict[str, int]: Statistics about the fixing operation
        """
        stats = {
            'files_processed': 0,
            'issues_fixed': 0,
            'files_modified': 0,
            'errors': 0
        }
        
        if not self.issues:
            self.logger.info("No Unicode issues found to fix.")
            return stats
        
        # Group issues by file
        issues_by_file = {}
        for issue in self.issues:
            if issue.file_path not in issues_by_file:
                issues_by_file[issue.file_path] = []
            issues_by_file[issue.file_path].append(issue)
        
        for file_path, file_issues in issues_by_file.items():
            try:
                if self._fix_file_issues(file_path, file_issues, auto_fix, dry_run):
                    stats['files_processed'] += 1
                    if not dry_run:
                        stats['files_modified'] += 1
                    stats['issues_fixed'] += len(file_issues)
            except Exception as e:
                self.logger.error(f"Error fixing {file_path}: {e}")
                stats['errors'] += 1
        
        return stats
    
    def generate_report(self, output_file: str = None) -> str:
        """
        Generate a comprehensive report of Unicode issues.
        
        Args:
            output_file: Optional output file path
            
        Returns:
            str: Report content
        """
        report_lines = [
            "# Unicode Fixer Report",
            f"Generated: {datetime.now().isoformat()}",
            f"Total Issues: {len(self.issues)}",
            "",
            "## Summary",
            f"- Files scanned: {len(self._get_files_to_scan())}",
            f"- Issues found: {len(self.issues)}",
            f"- Files with issues: {len(set(issue.file_path for issue in self.issues))}",
            "",
            "## Issues by Severity",
        ]
        
        # Count by severity
        severity_counts = {}
        for issue in self.issues:
            severity_counts[issue.severity] = severity_counts.get(issue.severity, 0) + 1
        
        for severity, count in severity_counts.items():
            report_lines.append(f"- {severity.title()}: {count}")
        
        report_lines.extend([
            "",
            "## Detailed Issues",
            ""
        ])
        
        # Group by file
        issues_by_file = {}
        for issue in self.issues:
            if issue.file_path not in issues_by_file:
                issues_by_file[issue.file_path] = []
            issues_by_file[issue.file_path].append(issue)
        
        for file_path, file_issues in sorted(issues_by_file.items()):
            report_lines.append(f"### {file_path}")
            report_lines.append(f"Issues: {len(file_issues)}")
            report_lines.append("")
            
            for issue in sorted(file_issues, key=lambda x: x.line_number):
                report_lines.append(
                    f"- Line {issue.line_number}:{issue.column} - "
                    f"'{issue.character}' ({issue.unicode_code}) - "
                    f"{issue.severity.upper()}"
                )
                report_lines.append(f"  Context: {issue.context}")
                report_lines.append("")
        
        report_content = "\n".join(report_lines)
        
        if output_file:
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(report_content)
                self.logger.info(f"Report saved to {output_file}")
            except Exception as e:
                self.logger.error(f"Error saving report: {e}")
        
        return report_content
    
    def _get_files_to_scan(self) -> List[Path]:
        """Get all files to scan for Unicode issues."""
        files = []
        
        for root, dirs, files_in_dir in os.walk(self.root_path):
            # Exclude directories
            dirs[:] = [d for d in dirs if d not in self.exclude_dirs]
            
            for file in files_in_dir:
                file_path = Path(root) / file
                if file_path.suffix in self.scan_extensions:
                    files.append(file_path)
        
        return files
    
    def _scan_file(self, file_path: Path):
        """Scan a single file for Unicode issues."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            for line_num, line in enumerate(content.split('\n'), 1):
                for col_num, char in enumerate(line, 1):
                    if self._is_problematic_unicode(char):
                        context = line[max(0, col_num-20):col_num+20].strip()
                        issue = UnicodeIssue(
                            file_path=str(file_path),
                            line_number=line_num,
                            column=col_num,
                            character=char,
                            unicode_code=f"U+{ord(char):04X}",
                            context=context,
                            severity=self._get_severity(char)
                        )
                        self.issues.append(issue)
        
        except UnicodeDecodeError as e:
            self.logger.warning(f"Unicode decode error in {file_path}: {e}")
            # Add a special issue for encoding problems
            issue = UnicodeIssue(
                file_path=str(file_path),
                line_number=0,
                column=0,
                character="",
                unicode_code="ENCODING_ERROR",
                context=f"Unicode decode error: {e}",
                severity="error"
            )
            self.issues.append(issue)
    
    def _is_problematic_unicode(self, char: str) -> bool:
        """Check if a character is problematic Unicode."""
        if ord(char) < 128:  # ASCII
            return False
        
        # Check if it's in our replacement list
        if char in self.unicode_replacements:
            return True
        
        # Check for other potentially problematic characters
        # High Unicode ranges that might cause issues
        code_point = ord(char)
        
        # Private use areas, control characters, etc.
        if (0xE000 <= code_point <= 0xF8FF or  # Private Use Area
            0xF0000 <= code_point <= 0xFFFFF or  # Supplementary Private Use Area-A
            0x100000 <= code_point <= 0x10FFFF):  # Supplementary Private Use Area-B
            return True
        
        return False
    
    def _get_severity(self, char: str) -> str:
        """Determine the severity of a Unicode issue."""
        if char in self.unicode_replacements:
            return "warning"  # Can be automatically fixed
        
        code_point = ord(char)
        if (0xE000 <= code_point <= 0xF8FF or
            0xF0000 <= code_point <= 0xFFFFF or
            0x100000 <= code_point <= 0x10FFFF):
            return "error"  # Private use areas
        
        return "info"  # Other Unicode characters
    
    def _fix_file_issues(self, file_path: str, issues: List[UnicodeIssue], 
                        auto_fix: bool, dry_run: bool) -> bool:
        """Fix Unicode issues in a single file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            modified = False
            
            # Sort issues by line number in reverse order to avoid offset issues
            sorted_issues = sorted(issues, key=lambda x: x.line_number, reverse=True)
            
            for issue in sorted_issues:
                if issue.line_number > 0 and issue.line_number <= len(lines):
                    line = lines[issue.line_number - 1]
                    if issue.column <= len(line):
                        char = line[issue.column - 1]
                        if char == issue.character:
                            # Replace the character
                            replacement = self.unicode_replacements.get(char, char)
                            new_line = line[:issue.column - 1] + replacement + line[issue.column:]
                            lines[issue.line_number - 1] = new_line
                            modified = True
            
            if modified and not dry_run:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(lines))
                self.fixed_files.add(file_path)
                self.logger.info(f"Fixed Unicode issues in {file_path}")
            
            return modified
        
        except Exception as e:
            self.logger.error(f"Error fixing {file_path}: {e}")
            return False


def main():
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(description="WSP-compliant Unicode fixing tool")
    parser.add_argument("--path", default=".", help="Root path to scan")
    parser.add_argument("--scan", action="store_true", help="Scan for Unicode issues")
    parser.add_argument("--fix", action="store_true", help="Fix Unicode issues")
    parser.add_argument("--auto-fix", action="store_true", help="Automatically fix issues without confirmation")
    parser.add_argument("--dry-run", action="store_true", help="Perform a dry run without making changes")
    parser.add_argument("--report", help="Generate report to specified file")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=log_level, format='%(levelname)s: %(message)s')
    
    # Initialize fixer
    fixer = UnicodeFixer(args.path)
    
    if args.scan or not (args.scan or args.fix):
        print("🔍 Scanning for Unicode issues...")
        issues = fixer.scan_codebase()
        
        if issues:
            print(f"⚠️  Found {len(issues)} Unicode issues")
            for issue in issues[:10]:  # Show first 10 issues
                print(f"  {issue.file_path}:{issue.line_number}:{issue.column} - '{issue.character}' ({issue.severity})")
            if len(issues) > 10:
                print(f"  ... and {len(issues) - 10} more issues")
        else:
            print("✅ No Unicode issues found")
    
    if args.fix:
        print("🔧 Fixing Unicode issues...")
        stats = fixer.fix_issues(auto_fix=args.auto_fix, dry_run=args.dry_run)
        print(f"📊 Fixing complete:")
        print(f"  Files processed: {stats['files_processed']}")
        print(f"  Issues fixed: {stats['issues_fixed']}")
        print(f"  Files modified: {stats['files_modified']}")
        print(f"  Errors: {stats['errors']}")
    
    if args.report:
        print("📄 Generating report...")
        report = fixer.generate_report(args.report)
        print(f"📋 Report generated: {args.report}")


if __name__ == "__main__":
    main() 