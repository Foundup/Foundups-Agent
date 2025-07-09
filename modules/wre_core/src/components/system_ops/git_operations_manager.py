"""
Git Operations Manager Component

Handles all git version control operations.
Extracted from system_manager.py per WSP 62 refactoring requirements.

WSP Compliance:
- WSP 62: Large File and Refactoring Enforcement Protocol (refactoring)
- WSP 1: Single responsibility principle (git operations only)
- WSP 34: Git Operations Protocol compliance
"""

import subprocess
from pathlib import Path
from modules.wre_core.src.utils.logging_utils import wre_log


class GitOperationsManager:
    """
    Git Operations Manager - Handles git version control operations
    
    Responsibilities:
    - Git push operations
    - Git status checking and display
    - Git add and commit operations
    - Repository state validation
    """
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        
    def push_to_git(self, session_manager):
        """Push changes to git repository."""
        wre_log("🚀 Pushing to git repository...", "INFO")
        session_manager.log_operation("git_push", {"action": "start"})
        
        try:
            # Check git status
            status_result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            if status_result.returncode != 0:
                wre_log("❌ Git status check failed", "ERROR")
                session_manager.log_operation("git_push", {"error": "status_check_failed"})
                return False
                
            # Check if there are changes to commit
            if not status_result.stdout.strip():
                wre_log("ℹ️ No changes to commit", "INFO")
                session_manager.log_operation("git_push", {"result": "no_changes"})
                return True
                
            # Add all changes
            add_result = subprocess.run(
                ["git", "add", "."],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            if add_result.returncode != 0:
                wre_log("❌ Git add failed", "ERROR")
                session_manager.log_operation("git_push", {"error": "add_failed"})
                return False
                
            # Commit changes
            commit_message = f"WRE Session Update - {session_manager.get_current_timestamp()}"
            commit_result = subprocess.run(
                ["git", "commit", "-m", commit_message],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            if commit_result.returncode != 0:
                wre_log("❌ Git commit failed", "ERROR")
                session_manager.log_operation("git_push", {"error": "commit_failed"})
                return False
                
            # Push to remote
            push_result = subprocess.run(
                ["git", "push"],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            if push_result.returncode == 0:
                wre_log("✅ Successfully pushed to git", "SUCCESS")
                session_manager.log_achievement("git_push", "Successfully pushed changes")
                return True
            else:
                wre_log("❌ Git push failed", "ERROR")
                session_manager.log_operation("git_push", {"error": "push_failed"})
                return False
                
        except Exception as e:
            wre_log(f"❌ Git operation failed: {e}", "ERROR")
            session_manager.log_operation("git_push", {"error": str(e)})
            return False
            
    def view_git_status(self, session_manager):
        """View current git repository status."""
        wre_log("📊 Checking git repository status...", "INFO")
        session_manager.log_operation("git_status", {"action": "check"})
        
        try:
            # Get git status
            status_result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            if status_result.returncode != 0:
                wre_log("❌ Git status check failed", "ERROR")
                return False
                
            # Display status
            if status_result.stdout.strip():
                wre_log("📋 Git Repository Status:", "INFO")
                for line in status_result.stdout.strip().split('\n'):
                    if line:
                        status_code = line[:2]
                        filename = line[3:]
                        status_desc = self._get_status_description(status_code)
                        wre_log(f"  {status_desc}: {filename}", "INFO")
            else:
                wre_log("✅ Working directory clean", "SUCCESS")
                
            # Get branch info
            branch_result = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            if branch_result.returncode == 0:
                current_branch = branch_result.stdout.strip()
                wre_log(f"🌿 Current branch: {current_branch}", "INFO")
                
            session_manager.log_achievement("git_status", "Git status displayed successfully")
            return True
            
        except Exception as e:
            wre_log(f"❌ Git status check failed: {e}", "ERROR")
            session_manager.log_operation("git_status", {"error": str(e)})
            return False
            
    def _get_status_description(self, status_code: str) -> str:
        """Get human-readable description for git status code."""
        status_map = {
            'M ': 'Modified',
            ' M': 'Modified (working tree)',
            'A ': 'Added',
            'D ': 'Deleted',
            'R ': 'Renamed',
            'C ': 'Copied',
            'U ': 'Unmerged',
            '??': 'Untracked',
            '!!': 'Ignored'
        }
        return status_map.get(status_code, f'Unknown ({status_code})')
        
    def validate_git_repository(self) -> bool:
        """Validate that the current directory is a git repository."""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--git-dir"],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except Exception:
            return False
            
    def get_current_branch(self) -> str:
        """Get the current git branch name."""
        try:
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                return result.stdout.strip()
            return "unknown"
        except Exception:
            return "unknown"
            
    def get_commit_count(self) -> int:
        """Get the total number of commits in the repository."""
        try:
            result = subprocess.run(
                ["git", "rev-list", "--count", "HEAD"],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                return int(result.stdout.strip())
            return 0
        except Exception:
            return 0 