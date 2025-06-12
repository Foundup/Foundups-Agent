#!/usr/bin/env python3
"""
WSP 34 Validator - Git Operations Protocol Enforcement

Validates file creation and git operations against WSP 34 standards.
Prevents temp file pollution and enforces branch discipline.
"""

import os
import sys
import glob
import argparse
from pathlib import Path
from typing import List, Tuple, Dict

class WSP34Validator:
    """WSP 34 Git Operations Protocol Validator"""
    
    PROHIBITED_PATTERNS = [
        "temp_*",
        "build/foundups-agent-clean/",
        "*_clean*",
        "backup_*", 
        "02_logs/",
        "*.log",
        "*_files.txt",
        "__pycache__/",
        ".coverage",
        "venv/",
        "recursive_build_*"
    ]
    
    ALLOWED_PATTERNS = [
        "modules/",
        "docs/", 
        "WSP_*/",
        "prompt/",
        "tools/",
        "tests/",
        "*.md",
        "requirements.txt",
        ".gitignore",
        ".env*",
        "ModLog.md",
        "ROADMAP.md"
    ]
    
    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir)
        self.violations = []
        
    def validate_file_creation(self, filepath: str, branch: str = "main") -> Tuple[bool, str]:
        """Validate if file creation is allowed on given branch"""
        if branch != "main":
            return True, "✅ Non-main branch - creation allowed"
            
        # Check against prohibited patterns
        for pattern in self.PROHIBITED_PATTERNS:
            if self._matches_pattern(filepath, pattern):
                return False, f"❌ BLOCKED: {filepath} matches prohibited pattern '{pattern}'"
        
        # Check if matches allowed patterns
        for pattern in self.ALLOWED_PATTERNS:
            if self._matches_pattern(filepath, pattern):
                return True, f"✅ APPROVED: {filepath} matches allowed pattern '{pattern}'"
        
        # Default: require explicit approval for unlisted files
        return False, f"⚠️ REVIEW REQUIRED: {filepath} not in allowed patterns"
    
    def _matches_pattern(self, filepath: str, pattern: str) -> bool:
        """Check if filepath matches glob pattern"""
        import fnmatch
        return fnmatch.fnmatch(filepath, pattern) or fnmatch.fnmatch(os.path.basename(filepath), pattern)
    
    def scan_repository(self) -> Dict[str, List[str]]:
        """Scan repository for WSP 34 violations"""
        violations = {
            "prohibited_files": [],
            "recursive_builds": [],
            "temp_pollution": []
        }
        
        # Find all files in repository
        for root, dirs, files in os.walk(self.root_dir):
            # Skip .git directory
            if '.git' in dirs:
                dirs.remove('.git')
                
            for file in files:
                filepath = os.path.relpath(os.path.join(root, file), self.root_dir)
                
                # Check for prohibited patterns
                for pattern in self.PROHIBITED_PATTERNS:
                    if self._matches_pattern(filepath, pattern):
                        violations["prohibited_files"].append(filepath)
                        break
                
                # Check for specific violations
                if "temp_" in filepath:
                    violations["temp_pollution"].append(filepath)
                    
                if "build/foundups-agent-clean/build" in filepath:
                    violations["recursive_builds"].append(filepath)
        
        return violations
    
    def check_git_status(self) -> List[str]:
        """Check git status for staged prohibited files"""
        import subprocess
        
        try:
            # Get staged files
            result = subprocess.run(
                ["git", "diff", "--cached", "--name-only"],
                capture_output=True, text=True, cwd=self.root_dir
            )
            
            if result.returncode != 0:
                return ["❌ Git command failed"]
            
            staged_files = result.stdout.strip().split('\n') if result.stdout.strip() else []
            violations = []
            
            for filepath in staged_files:
                valid, message = self.validate_file_creation(filepath, "main")
                if not valid:
                    violations.append(f"{filepath}: {message}")
            
            return violations
            
        except Exception as e:
            return [f"❌ Git check failed: {e}"]
    
    def generate_report(self) -> str:
        """Generate comprehensive WSP 34 compliance report"""
        violations = self.scan_repository()
        git_violations = self.check_git_status()
        
        report = []
        report.append("🔍 WSP 34 Git Operations Protocol - Compliance Report")
        report.append("=" * 60)
        
        # Repository scan results
        total_violations = sum(len(v) for v in violations.values())
        if total_violations == 0:
            report.append("✅ Repository scan: CLEAN - No violations found")
        else:
            report.append(f"❌ Repository scan: {total_violations} violations found")
            
            if violations["prohibited_files"]:
                report.append("\n📁 Prohibited Files:")
                for file in violations["prohibited_files"]:
                    report.append(f"  - {file}")
            
            if violations["recursive_builds"]:
                report.append("\n🔄 Recursive Build Folders:")
                for file in violations["recursive_builds"]:
                    report.append(f"  - {file}")
                    
            if violations["temp_pollution"]:
                report.append("\n🗑️ Temp File Pollution:")
                for file in violations["temp_pollution"]:
                    report.append(f"  - {file}")
        
        # Git staging check
        if git_violations:
            report.append(f"\n❌ Git staging check: {len(git_violations)} violations")
            for violation in git_violations:
                report.append(f"  - {violation}")
        else:
            report.append("\n✅ Git staging check: CLEAN")
        
        # Recommendations
        if total_violations > 0 or git_violations:
            report.append("\n🛠️ Recommended Actions:")
            report.append("  1. Move temp files to temp/ branch")
            report.append("  2. Clean recursive build folders")
            report.append("  3. Update .gitignore with WSP 34 patterns")
            report.append("  4. Use feature branches for experimental work")
        
        return "\n".join(report)
    
    def cleanup_violations(self, dry_run: bool = True) -> List[str]:
        """Clean up WSP 34 violations (with dry run option)"""
        violations = self.scan_repository()
        actions = []
        
        for filepath in violations["prohibited_files"]:
            if dry_run:
                actions.append(f"Would delete: {filepath}")
            else:
                try:
                    os.remove(os.path.join(self.root_dir, filepath))
                    actions.append(f"Deleted: {filepath}")
                except Exception as e:
                    actions.append(f"Failed to delete {filepath}: {e}")
        
        return actions

def main():
    parser = argparse.ArgumentParser(description="WSP 34 Git Operations Protocol Validator")
    parser.add_argument("--check-files", action="store_true", help="Check for prohibited files")
    parser.add_argument("--check-git", action="store_true", help="Check git staging area")
    parser.add_argument("--report", action="store_true", help="Generate full compliance report")
    parser.add_argument("--cleanup", action="store_true", help="Clean up violations")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be cleaned (with --cleanup)")
    parser.add_argument("--validate-file", help="Validate specific file creation")
    parser.add_argument("--branch", default="main", help="Target branch for validation")
    
    args = parser.parse_args()
    
    validator = WSP34Validator()
    
    if args.validate_file:
        valid, message = validator.validate_file_creation(args.validate_file, args.branch)
        print(message)
        sys.exit(0 if valid else 1)
    
    if args.check_files:
        violations = validator.scan_repository()
        total = sum(len(v) for v in violations.values())
        if total > 0:
            print(f"❌ WSP 34 violations found: {total}")
            sys.exit(1)
        else:
            print("✅ No WSP 34 violations found")
            sys.exit(0)
    
    if args.check_git:
        violations = validator.check_git_status()
        if violations:
            print("❌ Git staging violations:")
            for violation in violations:
                print(f"  {violation}")
            sys.exit(1)
        else:
            print("✅ Git staging clean")
            sys.exit(0)
    
    if args.cleanup:
        actions = validator.cleanup_violations(dry_run=args.dry_run)
        for action in actions:
            print(action)
    
    if args.report or not any([args.check_files, args.check_git, args.cleanup, args.validate_file]):
        print(validator.generate_report())

if __name__ == "__main__":
    main() 