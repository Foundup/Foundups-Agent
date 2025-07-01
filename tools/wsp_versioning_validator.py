#!/usr/bin/env python3
"""
WSP Versioning Validator
Automated tool to validate WSP semantic versioning compliance across all ModLog files.
Prevents versioning errors like 2.6.0 instead of 0.2.6.

Usage:
    python tools/wsp_versioning_validator.py --check-modlog
    python tools/wsp_versioning_validator.py --fix-modlog
    python tools/wsp_versioning_validator.py --validate-all
"""

import re
import os
import sys
import argparse
from pathlib import Path
from typing import List, Dict, Tuple, Optional

class WSPVersioningValidator:
    """WSP Versioning Compliance Validator"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.violations = []
        self.fixes_applied = []
        
        # WSP Versioning Patterns
        self.correct_patterns = [
            r'Version: 0\.\d+\.\d+',  # 0.x.x format
            r'Git Tag: v0\.\d+\.\d+',  # v0.x.x format
        ]
        
        self.forbidden_patterns = [
            r'Version: [2-9]\.\d+\.\d+',  # 2.x.x, 3.x.x, etc.
            r'Version: 1\.\d+\.\d+',      # 1.x.x (until MVP)
            r'Git Tag: v[2-9]\.\d+\.\d+', # v2.x.x, v3.x.x, etc.
            r'Git Tag: v1\.\d+\.\d+',     # v1.x.x (until MVP)
        ]
    
    def scan_modlog_files(self) -> List[Path]:
        """Find all ModLog files in the project"""
        modlog_files = []
        
        # Search patterns for ModLog files
        search_patterns = [
            "**/ModLog.md",
            "**/docs/ModLog.md",
            "**/WSP_*/ModLog.md"
        ]
        
        for pattern in search_patterns:
            modlog_files.extend(self.project_root.glob(pattern))
        
        return list(set(modlog_files))  # Remove duplicates
    
    def validate_file(self, file_path: Path) -> List[Dict]:
        """Validate a single ModLog file for versioning compliance"""
        violations = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
            
            for line_num, line in enumerate(lines, 1):
                for pattern in self.forbidden_patterns:
                    if re.search(pattern, line):
                        violations.append({
                            'file': str(file_path),
                            'line': line_num,
                            'content': line.strip(),
                            'pattern': pattern,
                            'type': 'forbidden_version'
                        })
            
            # Check for missing correct patterns
            has_version = any(re.search(r'Version:', line) for line in lines)
            has_git_tag = any(re.search(r'Git Tag:', line) for line in lines)
            
            if has_version and not any(re.search(r'Version: 0\.\d+\.\d+', line) for line in lines):
                violations.append({
                    'file': str(file_path),
                    'line': 0,
                    'content': 'No correct version pattern found',
                    'pattern': 'Version: 0.x.x',
                    'type': 'missing_correct_version'
                })
            
            if has_git_tag and not any(re.search(r'Git Tag: v0\.\d+\.\d+', line) for line in lines):
                violations.append({
                    'file': str(file_path),
                    'line': 0,
                    'content': 'No correct git tag pattern found',
                    'pattern': 'Git Tag: v0.x.x',
                    'type': 'missing_correct_git_tag'
                })
                
        except Exception as e:
            violations.append({
                'file': str(file_path),
                'line': 0,
                'content': f'Error reading file: {e}',
                'pattern': 'file_error',
                'type': 'file_error'
            })
        
        return violations
    
    def fix_versioning_errors(self, file_path: Path) -> List[Dict]:
        """Fix versioning errors in a ModLog file"""
        fixes = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Fix version patterns
            content = re.sub(r'Version: ([2-9])\.(\d+)\.(\d+)', r'Version: 0.\2.\3', content)
            content = re.sub(r'Version: 1\.(\d+)\.(\d+)', r'Version: 0.\1.\2', content)
            
            # Fix git tag patterns
            content = re.sub(r'Git Tag: v([2-9])\.(\d+)\.(\d+)', r'Git Tag: v0.\2.\3', content)
            content = re.sub(r'Git Tag: v1\.(\d+)\.(\d+)', r'Git Tag: v0.\1.\2', content)
            
            # Apply fixes if content changed
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                fixes.append({
                    'file': str(file_path),
                    'changes': 'Versioning patterns corrected to WSP format',
                    'original': original_content[:200] + '...' if len(original_content) > 200 else original_content,
                    'fixed': content[:200] + '...' if len(content) > 200 else content
                })
        
        except Exception as e:
            fixes.append({
                'file': str(file_path),
                'changes': f'Error fixing file: {e}',
                'original': '',
                'fixed': ''
            })
        
        return fixes
    
    def validate_all(self) -> Dict:
        """Validate all ModLog files in the project"""
        modlog_files = self.scan_modlog_files()
        all_violations = []
        
        print(f"🔍 Scanning {len(modlog_files)} ModLog files for versioning compliance...")
        
        for file_path in modlog_files:
            violations = self.validate_file(file_path)
            all_violations.extend(violations)
            
            if violations:
                print(f"❌ {file_path}: {len(violations)} violations found")
            else:
                print(f"✅ {file_path}: Compliant")
        
        return {
            'total_files': len(modlog_files),
            'violations': all_violations,
            'compliant_files': len(modlog_files) - len([v for v in all_violations if v['type'] != 'file_error']),
            'files_with_violations': len(set(v['file'] for v in all_violations))
        }
    
    def fix_all(self) -> Dict:
        """Fix all versioning errors in ModLog files"""
        modlog_files = self.scan_modlog_files()
        all_fixes = []
        
        print(f"🔧 Fixing versioning errors in {len(modlog_files)} ModLog files...")
        
        for file_path in modlog_files:
            fixes = self.fix_versioning_errors(file_path)
            all_fixes.extend(fixes)
            
            if fixes:
                print(f"✅ {file_path}: Fixed")
            else:
                print(f"✅ {file_path}: No fixes needed")
        
        return {
            'total_files': len(modlog_files),
            'fixes_applied': all_fixes,
            'files_fixed': len([f for f in all_fixes if 'Error' not in f['changes']])
        }
    
    def generate_report(self, validation_result: Dict) -> str:
        """Generate a detailed validation report"""
        report = []
        report.append("# WSP Versioning Compliance Report")
        report.append("")
        
        # Summary
        report.append("## 📊 Summary")
        report.append(f"- **Total Files Scanned**: {validation_result['total_files']}")
        report.append(f"- **Compliant Files**: {validation_result['compliant_files']}")
        report.append(f"- **Files with Violations**: {validation_result['files_with_violations']}")
        report.append(f"- **Total Violations**: {len(validation_result['violations'])}")
        report.append("")
        
        # Violations Details
        if validation_result['violations']:
            report.append("## ❌ Violations Found")
            report.append("")
            
            for violation in validation_result['violations']:
                report.append(f"### {violation['file']}")
                report.append(f"- **Line**: {violation['line']}")
                report.append(f"- **Type**: {violation['type']}")
                report.append(f"- **Content**: `{violation['content']}`")
                report.append(f"- **Pattern**: `{violation['pattern']}`")
                report.append("")
        else:
            report.append("## ✅ All Files Compliant")
            report.append("No versioning violations found!")
            report.append("")
        
        # Recommendations
        report.append("## 🛡️ WSP Versioning Requirements")
        report.append("")
        report.append("### ✅ Correct Patterns:")
        report.append("- `Version: 0.2.6`")
        report.append("- `Git Tag: v0.2.6-feature-name`")
        report.append("")
        report.append("### ❌ Forbidden Patterns:")
        report.append("- `Version: 2.6.0` (Major version 2+ forbidden)")
        report.append("- `Version: 1.5.0` (Major version 1+ until MVP)")
        report.append("- `Git Tag: v2.6.0-feature-name`")
        report.append("")
        
        return "\n".join(report)

def main():
    parser = argparse.ArgumentParser(description='WSP Versioning Validator')
    parser.add_argument('--check-modlog', action='store_true', 
                       help='Check ModLog files for versioning compliance')
    parser.add_argument('--fix-modlog', action='store_true',
                       help='Fix versioning errors in ModLog files')
    parser.add_argument('--validate-all', action='store_true',
                       help='Validate all files and generate report')
    parser.add_argument('--output-report', type=str,
                       help='Output report to file')
    
    args = parser.parse_args()
    
    validator = WSPVersioningValidator()
    
    if args.check_modlog or args.validate_all:
        print("🔍 WSP Versioning Compliance Check")
        print("=" * 50)
        
        result = validator.validate_all()
        report = validator.generate_report(result)
        
        if args.output_report:
            with open(args.output_report, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"📄 Report saved to: {args.output_report}")
        else:
            print(report)
        
        if result['violations']:
            print("\n❌ Versioning violations found!")
            sys.exit(1)
        else:
            print("\n✅ All files compliant with WSP versioning!")
    
    elif args.fix_modlog:
        print("🔧 WSP Versioning Error Fix")
        print("=" * 50)
        
        result = validator.fix_all()
        
        print(f"\n📊 Fix Summary:")
        print(f"- Files processed: {result['total_files']}")
        print(f"- Files fixed: {result['files_fixed']}")
        print(f"- Total fixes applied: {len(result['fixes_applied'])}")
        
        if result['fixes_applied']:
            print("\n🔧 Fixes Applied:")
            for fix in result['fixes_applied']:
                print(f"- {fix['file']}: {fix['changes']}")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main() 