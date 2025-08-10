#!/usr/bin/env python3
"""
WSP Violation Checker - Prevents WSP 49 violations
Checks for test files in wrong locations and other WSP violations
"""

import os
import sys
from pathlib import Path
from typing import List, Tuple

class WSPViolationChecker:
    """Check for WSP framework violations"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.violations = []
        
    def check_test_files_in_root(self) -> List[Tuple[str, str]]:
        """Check for test files in root directory (WSP 49 violation)"""
        violations = []
        
        # Patterns that indicate test files
        test_patterns = [
            'test_*.py',
            'debug_*.py',
            '*_test.py',
            'minimal_test.py',
            'test_*.bat',
            '*_test.bat'
        ]
        
        # Check root directory
        for pattern in test_patterns:
            for file in self.project_root.glob(pattern):
                if file.is_file():
                    # Determine proper location
                    proper_location = self._determine_proper_location(file)
                    violations.append((str(file), proper_location))
                    
        return violations
    
    def _determine_proper_location(self, file: Path) -> str:
        """Determine proper location for a test file based on its content"""
        filename = file.name.lower()
        
        # Check filename for hints
        if 'cursor' in filename:
            return 'modules/development/cursor_multi_agent_bridge/tests/'
        elif 'wre' in filename:
            return 'modules/wre_core/tests/'
        elif 'github' in filename:
            return 'modules/platform_integration/github_integration/tests/'
        elif 'compliance' in filename:
            return 'modules/infrastructure/compliance_agent/tests/'
        else:
            # Try to read file to determine module
            try:
                content = file.read_text(encoding='utf-8', errors='ignore')
                if 'cursor' in content.lower():
                    return 'modules/development/cursor_multi_agent_bridge/tests/'
                elif 'websocket' in content.lower() or 'wre' in content.lower():
                    return 'modules/wre_core/tests/'
                elif 'github' in content.lower():
                    return 'modules/platform_integration/github_integration/tests/'
            except:
                pass
                
        return 'modules/[appropriate_domain]/[module]/tests/'
    
    def check_redundant_module_structure(self) -> List[str]:
        """Check for redundant module naming (WSP 49 violation)"""
        violations = []
        
        modules_dir = self.project_root / 'modules'
        if modules_dir.exists():
            for domain_dir in modules_dir.iterdir():
                if domain_dir.is_dir():
                    for module_dir in domain_dir.iterdir():
                        if module_dir.is_dir():
                            # Check if module has redundant subdirectory
                            redundant_path = module_dir / module_dir.name
                            if redundant_path.exists() and redundant_path.is_dir():
                                violations.append(str(redundant_path))
                                
        return violations
    
    def check_missing_test_directories(self) -> List[str]:
        """Check for modules missing test directories"""
        missing = []
        
        modules_dir = self.project_root / 'modules'
        if modules_dir.exists():
            for domain_dir in modules_dir.iterdir():
                if domain_dir.is_dir() and not domain_dir.name.startswith('.'):
                    for module_dir in domain_dir.iterdir():
                        if module_dir.is_dir() and not module_dir.name.startswith('.'):
                            test_dir = module_dir / 'tests'
                            if not test_dir.exists():
                                missing.append(str(module_dir))
                                
        return missing
    
    def run_all_checks(self) -> dict:
        """Run all WSP violation checks"""
        results = {
            'test_files_in_root': self.check_test_files_in_root(),
            'redundant_structure': self.check_redundant_module_structure(),
            'missing_test_dirs': self.check_missing_test_directories()
        }
        
        return results
    
    def print_report(self, results: dict):
        """Print violation report"""
        print("=" * 60)
        print("WSP VIOLATION CHECK REPORT")
        print("=" * 60)
        
        # Test files in root
        if results['test_files_in_root']:
            print("\n❌ WSP 49 VIOLATION: Test files in root directory")
            print("-" * 40)
            for file, proper_location in results['test_files_in_root']:
                print(f"  File: {file}")
                print(f"  Move to: {proper_location}")
                print()
        else:
            print("\n✅ No test files in root directory")
        
        # Redundant structure
        if results['redundant_structure']:
            print("\n❌ WSP 49 VIOLATION: Redundant module structure")
            print("-" * 40)
            for path in results['redundant_structure']:
                print(f"  Redundant: {path}")
        else:
            print("\n✅ No redundant module structures")
        
        # Missing test directories
        if results['missing_test_dirs']:
            print("\n⚠️ WSP 49 WARNING: Modules missing test directories")
            print("-" * 40)
            for path in results['missing_test_dirs']:
                print(f"  Missing tests/: {path}")
        
        # Summary
        total_violations = (
            len(results['test_files_in_root']) +
            len(results['redundant_structure'])
        )
        
        print("\n" + "=" * 60)
        if total_violations == 0:
            print("✅ WSP COMPLIANCE: All checks passed!")
        else:
            print(f"❌ WSP VIOLATIONS: {total_violations} issues found")
            print("Run 'python tools/wsp_violation_fixer.py' to auto-fix")
        print("=" * 60)
        
        return total_violations

def main():
    """Main entry point"""
    project_root = Path(__file__).resolve().parent.parent
    
    checker = WSPViolationChecker(project_root)
    results = checker.run_all_checks()
    violations = checker.print_report(results)
    
    # Exit with error code if violations found
    sys.exit(1 if violations > 0 else 0)

if __name__ == "__main__":
    main()