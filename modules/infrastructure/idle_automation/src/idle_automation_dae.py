"""
Idle Automation DAE - Autonomous Background Tasks
WSP-Compliant: WSP 27 (DAE Architecture), WSP 35 (Module Execution Automation)
Integrates with YouTube DAE idle loops for automatic Git + Social Media operations
"""

import asyncio
import json
import logging
import os
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class IdleAutomationDAE:
    """
    WSP 27 DAE: Idle Automation for autonomous background operations.

    Phases per WSP 27:
    -1: Signal - Idle state detection from YouTube DAE
     0: Knowledge - Git status, network connectivity, system state
     1: Protocol - Task execution with safety checks
     2: Agentic - Autonomous decision making and optimization
    """

    def __init__(self):
        """Initialize Idle Automation DAE with WSP 60 memory architecture."""
        logger.info("🚀 Initializing Idle Automation DAE (WSP 27/35 compliant)")

        self.module_path = Path(__file__).parent.parent
        self.memory_path = self.module_path / "memory"
        self.memory_path.mkdir(exist_ok=True)

        # WSP 60: Load persistent state
        self.idle_state = self._load_idle_state()
        self.execution_history = self._load_execution_history()

        # Configuration from environment (WSP 70)
        self.config = {
            "auto_git_push": os.getenv("AUTO_GIT_PUSH", "false").lower() == "true",
            "auto_linkedin_post": os.getenv("AUTO_LINKEDIN_POST", "false").lower() == "true",
            "idle_task_timeout": int(os.getenv("IDLE_TASK_TIMEOUT", "300")),
            "max_daily_executions": int(os.getenv("MAX_DAILY_EXECUTIONS", "3")),
        }

        # WSP 48: WRE integration for recursive improvement
        self._setup_wre_integration()

        logger.info("✅ Idle Automation DAE initialized")
        logger.info(f"   Auto Git Push: {self.config['auto_git_push']}")
        logger.info(f"   Auto LinkedIn: {self.config['auto_linkedin_post']}")

    def _load_idle_state(self) -> Dict[str, Any]:
        """Load persistent idle state (WSP 60)."""
        state_file = self.memory_path / "idle_state.json"

        if state_file.exists():
            try:
                with open(state_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load idle state: {e}")

        # Default state
        return {
            "last_idle_execution": None,
            "last_git_push": None,
            "last_linkedin_post": None,
            "execution_count_today": 0,
            "last_reset_date": datetime.now().date().isoformat(),
            "idle_session_count": 0,
        }

    def _save_idle_state(self):
        """Save idle state persistently (WSP 60)."""
        state_file = self.memory_path / "idle_state.json"

        try:
            with open(state_file, 'w') as f:
                json.dump(self.idle_state, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to save idle state: {e}")

    def _load_execution_history(self) -> list:
        """Load execution history for telemetry (WSP 60)."""
        history_file = self.memory_path / "execution_history.jsonl"

        if history_file.exists():
            try:
                with open(history_file, 'r') as f:
                    return [json.loads(line) for line in f if line.strip()]
            except Exception as e:
                logger.warning(f"Failed to load execution history: {e}")

        return []

    def _log_execution(self, task_type: str, success: bool, details: Dict[str, Any]):
        """Log execution for telemetry and WRE learning (WSP 48)."""
        execution_record = {
            "timestamp": datetime.now().isoformat(),
            "task_type": task_type,
            "success": success,
            "details": details,
            "idle_session": self.idle_state.get("idle_session_count", 0),
        }

        # Add to memory
        self.execution_history.append(execution_record)

        # Keep only last 1000 records
        if len(self.execution_history) > 1000:
            self.execution_history = self.execution_history[-1000:]

        # Save to disk
        history_file = self.memory_path / "execution_history.jsonl"
        try:
            with open(history_file, 'a') as f:
                f.write(json.dumps(execution_record) + "\n")
        except Exception as e:
            logger.error(f"Failed to log execution: {e}")

        # WSP 48: Report to WRE for learning
        if hasattr(self, 'wre_integration') and self.wre_integration:
            try:
                if success:
                    self.wre_integration.record_success(task_type, details)
                else:
                    self.wre_integration.record_error(task_type, details)
            except Exception as e:
                logger.debug(f"WRE integration failed: {e}")

    def _setup_wre_integration(self):
        """Setup WSP 48 WRE integration for recursive improvement."""
        try:
            from modules.infrastructure.wre_core.recursive_improvement.src.wre_integration import (
                record_error, record_success, get_optimized_approach
            )
            self.wre_integration = type('WREIntegration', (), {
                'record_error': record_error,
                'record_success': record_success,
                'get_optimized': get_optimized_approach,
            })()
            logger.info("[0102] WRE recursive improvement connected")
        except Exception as e:
            logger.debug(f"WRE integration not available: {e}")
            self.wre_integration = None

    def _check_daily_limits(self) -> bool:
        """Check if we've exceeded daily execution limits."""
        today = datetime.now().date().isoformat()

        # Reset counter if it's a new day
        if self.idle_state.get("last_reset_date") != today:
            self.idle_state["execution_count_today"] = 0
            self.idle_state["last_reset_date"] = today

        return self.idle_state["execution_count_today"] < self.config["max_daily_executions"]

    def _check_network_connectivity(self) -> bool:
        """Check network connectivity for Git and social media operations."""
        try:
            # Quick connectivity test
            result = subprocess.run(
                ['ping', '-n', '1', '-w', '1000', 'github.com'],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False

    def _check_git_status(self) -> Dict[str, Any]:
        """Check Git working tree status."""
        try:
            # Check for uncommitted changes
            status = subprocess.run(
                ['git', 'status', '--porcelain'],
                capture_output=True, text=True, check=True,
                cwd=self.module_path.parent.parent.parent  # Project root
            )

            changes = status.stdout.strip().split('\n') if status.stdout.strip() else []

            return {
                "has_changes": len(changes) > 0,
                "change_count": len(changes),
                "changes": changes[:10],  # First 10 changes
            }
        except subprocess.CalledProcessError as e:
            logger.warning(f"Git status check failed: {e}")
            return {"has_changes": False, "error": str(e)}

    async def _execute_git_push(self) -> Dict[str, Any]:
        """Execute Git commit and push operations."""
        result = {
            "task": "git_push",
            "success": False,
            "commit_hash": None,
            "files_committed": 0,
            "duration": 0,
        }

        start_time = datetime.now()

        try:
            # Pre-conditions check
            if not self.config["auto_git_push"]:
                result["error"] = "Auto Git push disabled"
                return result

            if not self._check_network_connectivity():
                result["error"] = "No network connectivity"
                return result

            git_status = self._check_git_status()
            if not git_status.get("has_changes"):
                result["error"] = "No changes to commit"
                return result

            # Generate commit message
            commit_message = self._generate_commit_message(git_status)

            # Add all changes
            subprocess.run(['git', 'add', '.'], check=True,
                         cwd=self.module_path.parent.parent.parent)

            # Commit
            subprocess.run(['git', 'commit', '-m', commit_message], check=True,
                         cwd=self.module_path.parent.parent.parent)

            # Push
            subprocess.run(['git', 'push'], check=True,
                         cwd=self.module_path.parent.parent.parent)

            # Get commit hash
            commit_result = subprocess.run(
                ['git', 'rev-parse', 'HEAD'],
                capture_output=True, text=True, check=True,
                cwd=self.module_path.parent.parent.parent
            )

            result["success"] = True
            result["commit_hash"] = commit_result.stdout.strip()
            result["files_committed"] = git_status["change_count"]
            result["commit_message"] = commit_message

            # Update state
            self.idle_state["last_git_push"] = datetime.now().isoformat()

        except subprocess.CalledProcessError as e:
            result["error"] = f"Git operation failed: {e}"
        except Exception as e:
            result["error"] = f"Unexpected error: {e}"
        finally:
            result["duration"] = (datetime.now() - start_time).total_seconds()

        return result

    async def _execute_linkedin_post(self, git_result: Dict[str, Any]) -> Dict[str, Any]:
        """Execute LinkedIn posting using GitLinkedInBridge."""
        result = {
            "task": "linkedin_post",
            "success": False,
            "post_content": None,
            "duration": 0,
        }

        start_time = datetime.now()

        try:
            # Pre-conditions check
            if not self.config["auto_linkedin_post"]:
                result["error"] = "Auto LinkedIn posting disabled"
                return result

            if not git_result.get("success"):
                result["error"] = "Skipping LinkedIn post - Git push failed"
                return result

            # Import and use GitLinkedInBridge
            from modules.platform_integration.linkedin_agent.src.git_linkedin_bridge import GitLinkedInBridge

            bridge = GitLinkedInBridge(company_id="foundups")

            # Get recent commits (should include our new commit)
            commits = bridge.get_recent_commits(1)
            if not commits:
                result["error"] = "No recent commits found"
                return result

            # Generate LinkedIn content
            content = bridge.generate_linkedin_content(commits)

            # Post to LinkedIn (currently commented out for safety)
            # bridge.post_to_linkedin(content)

            result["success"] = True
            result["post_content"] = content
            result["commit_info"] = commits[0] if commits else None

            # Update state
            self.idle_state["last_linkedin_post"] = datetime.now().isoformat()

        except Exception as e:
            result["error"] = f"LinkedIn posting failed: {e}"
        finally:
            result["duration"] = (datetime.now() - start_time).total_seconds()

        return result

    def _generate_commit_message(self, git_status: Dict[str, Any]) -> str:
        """Generate contextual commit message."""
        change_count = git_status["change_count"]

        if change_count == 1:
            return "Auto-commit: 1 file updated during idle automation"
        elif change_count < 5:
            return f"Auto-commit: {change_count} files updated during idle automation"
        else:
            return f"Auto-commit: {change_count} files updated - batch changes during idle automation"

    async def run_idle_tasks(self) -> Dict[str, Any]:
        """
        Main entry point - execute idle automation tasks.
        Called by YouTube DAE when entering idle state.
        """
        logger.info("🤖 Idle Automation DAE: Executing background tasks")

        # Update idle session tracking
        self.idle_state["idle_session_count"] += 1
        self.idle_state["last_idle_execution"] = datetime.now().isoformat()

        execution_result = {
            "session_id": self.idle_state["idle_session_count"],
            "timestamp": datetime.now().isoformat(),
            "tasks_executed": [],
            "overall_success": True,
            "duration": 0,
        }

        start_time = datetime.now()

        try:
            # Phase 0: Knowledge gathering (network, git status, limits)
            if not self._check_daily_limits():
                logger.info("⏰ Daily execution limit reached - skipping idle tasks")
                execution_result["skipped_reason"] = "daily_limit_reached"
                return execution_result

            if not self._check_network_connectivity():
                logger.info("🌐 No network connectivity - skipping idle tasks")
                execution_result["skipped_reason"] = "no_network"
                return execution_result

            # Phase 1: Protocol execution (git push)
            git_result = await self._execute_git_push()
            execution_result["tasks_executed"].append(git_result)

            if git_result["success"]:
                logger.info(f"✅ Git push successful: {git_result['commit_hash'][:8]}")
            else:
                logger.warning(f"⚠️ Git push failed: {git_result.get('error', 'Unknown error')}")
                execution_result["overall_success"] = False

            # Phase 2: Social media posting (if git succeeded)
            linkedin_result = await self._execute_linkedin_post(git_result)
            execution_result["tasks_executed"].append(linkedin_result)

            if linkedin_result["success"]:
                logger.info("✅ LinkedIn post prepared (posting disabled for safety)")
            else:
                logger.info(f"ℹ️ LinkedIn posting skipped: {linkedin_result.get('error', 'N/A')}")

            # Update execution counter
            self.idle_state["execution_count_today"] += 1

            # Log execution
            self._log_execution(
                task_type="idle_automation_cycle",
                success=execution_result["overall_success"],
                details={
                    "git_success": git_result["success"],
                    "linkedin_success": linkedin_result["success"],
                    "session_id": execution_result["session_id"],
                }
            )

        except Exception as e:
            logger.error(f"❌ Idle automation failed: {e}")
            execution_result["overall_success"] = False
            execution_result["error"] = str(e)

            self._log_execution(
                task_type="idle_automation_cycle",
                success=False,
                details={"error": str(e)}
            )
        finally:
            execution_result["duration"] = (datetime.now() - start_time).total_seconds()
            self._save_idle_state()

        logger.info(f"🏁 Idle automation cycle completed in {execution_result['duration']:.1f}s")
        return execution_result

    def get_idle_status(self) -> Dict[str, Any]:
        """Get current idle automation status (WSP 70)."""
        return {
            "last_idle_execution": self.idle_state.get("last_idle_execution"),
            "last_git_push": self.idle_state.get("last_git_push"),
            "last_linkedin_post": self.idle_state.get("last_linkedin_post"),
            "execution_count_today": self.idle_state.get("execution_count_today", 0),
            "idle_session_count": self.idle_state.get("idle_session_count", 0),
            "auto_git_enabled": self.config["auto_git_push"],
            "auto_linkedin_enabled": self.config["auto_linkedin_post"],
            "recent_executions": self.execution_history[-5:] if self.execution_history else [],
        }

    def reset_daily_counter(self):
        """Reset daily execution counter (for testing)."""
        self.idle_state["execution_count_today"] = 0
        self.idle_state["last_reset_date"] = datetime.now().date().isoformat()
        self._save_idle_state()


# Convenience function for YouTube DAE integration
async def run_idle_automation() -> Dict[str, Any]:
    """
    Convenience function for YouTube DAE integration.
    Call this from AutoModeratorDAE when entering idle state.
    """
    dae = IdleAutomationDAE()
    return await dae.run_idle_tasks()
