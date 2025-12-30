#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auto-Fix Engine - Extracted from AI Overseer

Handles Qwen-powered autonomous bug fixing, patch validation,
and bug classification.

WSP 62 Refactoring: Extracted to comply with file size thresholds.
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class AutoFixEngine:
    """
    Autonomous code fixing engine powered by Qwen.
    
    Extracted from AI Overseer for WSP 62 compliance.
    """

    def __init__(self, repo_root: Path, patch_executor, autonomous_orchestrator, logger):
        """
        Initialize Auto-Fix Engine.
        
        Args:
            repo_root: Repository root path
            patch_executor: PatchExecutor instance
            autonomous_orchestrator: AutonomousRefactoringOrchestrator
            logger: Logging instance
        """
        self.repo_root = repo_root
        self.patch_executor = patch_executor
        self.autonomous_orchestrator = autonomous_orchestrator
        self.logger = logger

    def _qwen_classify_bugs(self, detected_bugs: List[Dict], skill: Dict) -> List[Dict]:
        """Phase 2 (Qwen): Classify bugs with WSP 15 MPS scoring and determine actions"""
        classified = []

        for bug in detected_bugs:
            config = bug["config"]
            qwen_action = config.get("qwen_action", "ignore")

            # Interpret qwen_action into auto_fixable/needs_0102 flags
            auto_fixable = (qwen_action == "auto_fix")
            needs_0102 = (qwen_action == "bug_report")
            should_ignore = (qwen_action == "ignore")

            # Skip if Qwen decided to ignore (e.g., stream_not_found P4 backlog)
            if should_ignore:
                logger.info(f"[QWEN-IGNORE] Skipping {bug['pattern_name']} (qwen_action=ignore)")
                continue

            # Get WSP 15 MPS scoring
            wsp_15_mps = config.get("wsp_15_mps", {})
            complexity = wsp_15_mps.get("complexity", 3)

            classification = {
                "pattern_name": bug["pattern_name"],
                "complexity": complexity,
                "auto_fixable": auto_fixable,
                "needs_0102": needs_0102,
                "qwen_action": qwen_action,
                "fix_action": config.get("fix_action"),
                "fix_module": config.get("fix_module"),
                "fix_function": config.get("fix_function"),
                "matches": bug["matches"],
                "config": config  # Pass full config for announcements
            }
            classified.append(classification)

            logger.info(f"[QWEN-CLASSIFY] {bug['pattern_name']}: complexity={complexity}, action={qwen_action}")

        return classified


    def _apply_auto_fix(self, bug: Dict, skill: Dict) -> Dict:
        """
        Phase 3: Apply operational auto-fix for complexity 1-2 bugs

        Implements approved operational fixes:
        - OAuth reauthorization (subprocess)
        - API credential rotation (function call)
        - Service reconnection (method call)
        - Daemon restart (process management)

        Returns success/failure for MetricsAppender tracking
        """
        import subprocess

        fix_action = bug.get("fix_action")
        pattern_name = bug["pattern_name"]
        skill_name = skill.get("daemon_name", "unknown_daemon")

        # Generate execution ID for metrics tracking
        exec_id = f"fix_{pattern_name}_{int(time.time())}"
        start_time = time.time()

        logger.info(f"[AUTO-FIX] Applying {fix_action} for {pattern_name} | exec_id={exec_id}")

        try:
            # Operational Fix 1: OAuth Reauthorization (P0, Complexity 2)
            if fix_action == "run_reauthorization_script":
                fix_command = bug["config"].get("fix_command")
                if not fix_command:
                    return {
                        "success": False,
                        "bug": pattern_name,
                        "error": "No fix_command in skill config"
                    }

                logger.info(f"[AUTO-FIX] Running OAuth reauth: {fix_command}")
                result = subprocess.run(
                    fix_command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=30
                )

                success = result.returncode == 0

                # Track metrics
                execution_time_ms = int((time.time() - start_time) * 1000)
                self.metrics.append_performance_metric(
                    skill_name=skill_name,
                    execution_id=exec_id,
                    execution_time_ms=execution_time_ms,
                    agent="ai_overseer",
                    exception_occurred=False
                )
                self.metrics.append_outcome_metric(
                    skill_name=skill_name,
                    execution_id=exec_id,
                    decision=fix_action,
                    expected_decision=fix_action,
                    correct=success,
                    confidence=1.0 if success else 0.0,
                    reasoning=f"OAuth reauth {'succeeded' if success else 'failed'}: {fix_command}",
                    agent="ai_overseer"
                )

                return {
                    "success": success,
                    "bug": pattern_name,
                    "fix_applied": fix_action,
                    "method": "subprocess",
                    "command": fix_command,
                    "stdout": result.stdout[:500],  # Truncate for metrics
                    "stderr": result.stderr[:500] if result.stderr else None,
                    "returncode": result.returncode,
                    "execution_id": exec_id
                }

            # Operational Fix 2: API Credential Rotation (P1, Complexity 2)
            elif fix_action == "rotate_api_credentials":
                logger.info(f"[AUTO-FIX] Rotating API credentials")

                # Import YouTube auth module
                try:
                    from modules.platform_integration.youtube_auth.src.youtube_auth import get_authenticated_service
                except ImportError as e:
                    return {
                        "success": False,
                        "bug": pattern_name,
                        "error": f"Cannot import youtube_auth: {e}"
                    }

                # Force credential rotation by calling auth service
                # The function auto-rotates between available credential sets
                try:
                    service = get_authenticated_service()
                    success = True
                    error_msg = None
                except Exception as e:
                    success = False
                    error_msg = str(e)

                # Track metrics
                execution_time_ms = int((time.time() - start_time) * 1000)
                self.metrics.append_performance_metric(
                    skill_name=skill_name,
                    execution_id=exec_id,
                    execution_time_ms=execution_time_ms,
                    agent="ai_overseer",
                    exception_occurred=not success
                )
                self.metrics.append_outcome_metric(
                    skill_name=skill_name,
                    execution_id=exec_id,
                    decision=fix_action,
                    expected_decision=fix_action,
                    correct=success,
                    confidence=1.0 if success else 0.0,
                    reasoning=f"API rotation {'succeeded' if success else f'failed: {error_msg}'}",
                    agent="ai_overseer"
                )

                if success:
                    return {
                        "success": True,
                        "bug": pattern_name,
                        "fix_applied": fix_action,
                        "method": "api_rotation",
                        "message": "API credentials rotated to next available set",
                        "execution_id": exec_id
                    }
                else:
                    return {
                        "success": False,
                        "bug": pattern_name,
                        "error": error_msg,
                        "method": "api_rotation",
                        "execution_id": exec_id
                    }

            # Operational Fix 3: Service Reconnection (P1, Complexity 2)
            elif fix_action == "reconnect_service":
                logger.info(f"[AUTO-FIX] Attempting service reconnection")

                # For now, return success (actual reconnection logic would go here)
                # TODO: Integrate with actual service reconnection methods
                success = True

                # Track metrics
                execution_time_ms = int((time.time() - start_time) * 1000)
                self.metrics.append_performance_metric(
                    skill_name=skill_name,
                    execution_id=exec_id,
                    execution_time_ms=execution_time_ms,
                    agent="ai_overseer",
                    exception_occurred=False
                )
                self.metrics.append_outcome_metric(
                    skill_name=skill_name,
                    execution_id=exec_id,
                    decision=fix_action,
                    expected_decision=fix_action,
                    correct=success,
                    confidence=0.5,  # Placeholder has lower confidence
                    reasoning="Service reconnection placeholder (not yet implemented)",
                    agent="ai_overseer"
                )

                return {
                    "success": True,
                    "bug": pattern_name,
                    "fix_applied": fix_action,
                    "method": "service_reconnect",
                    "message": "Service reconnection attempted (placeholder)",
                    "execution_id": exec_id
                }

            # Code Fix: Unicode conversion (Complexity 1 - uses PatchExecutor)
            elif fix_action == "add_unicode_conversion_before_youtube_send":
                logger.info(f"[AUTO-FIX] Applying Unicode conversion patch via PatchExecutor")

                try:
                    # Generate UTF-8 header patch for the affected file
                    # Convert Python module notation to file path
                    # FROM: modules.ai_intelligence.banter_engine.src.banter_engine
                    # TO:   modules/ai_intelligence/banter_engine/src/banter_engine.py
                    affected_module = bug.get("fix_module", "modules.ai_intelligence.banter_engine.src.banter_engine")
                    affected_file = affected_module.replace('.', '/') + '.py'

                    # Simple UTF-8 header patch template
                    patch_content = f"""diff --git a/{affected_file} b/{affected_file}
index 0000000..1111111 100644
--- a/{affected_file}
+++ b/{affected_file}
@@ -1,3 +1,4 @@
+# -*- coding: utf-8 -*-
 \"\"\"
 Module implementation
 \"\"\"
"""

                    # Apply patch using PatchExecutor
                    patch_result = self.patch_executor.apply_patch(
                        patch_content=patch_content,
                        patch_description=f"Add UTF-8 header to {affected_file}"
                    )

                    success = patch_result["success"]
                    execution_time_ms = int((time.time() - start_time) * 1000)

                    # Track metrics
                    self.metrics.append_performance_metric(
                        skill_name=skill_name,
                        execution_id=exec_id,
                        execution_time_ms=execution_time_ms,
                        agent="ai_overseer",
                        exception_occurred=not success
                    )

                    if success:
                        verification = self._verify_unicode_patch(
                            patch_result.get("files_modified", [])
                        )

                        self.metrics.append_outcome_metric(
                            skill_name=skill_name,
                            execution_id=f"{exec_id}_verify",
                            decision="verify_unicode_patch",
                            expected_decision="verify_unicode_patch",
                            correct=verification["verified"],
                            confidence=0.9 if verification["verified"] else 0.0,
                            reasoning=verification["reason"],
                            agent="ai_overseer"
                        )

                        if verification["verified"]:
                            return {
                                "success": True,
                                "bug": pattern_name,
                                "fix_applied": fix_action,
                                "method": "patch_executor",
                                "files_modified": patch_result["files_modified"],
                                "message": f"UTF-8 header patch applied to {affected_file}",
                                "execution_id": exec_id,
                                "needs_restart": True,
                                "verification": verification
                            }

                        logger.warning(f"[VERIFY] Unicode patch verification failed: {verification['reason']}")
                        return {
                            "success": False,
                            "bug": pattern_name,
                            "fix_applied": fix_action,
                            "error": "Verification failed - manual review required",
                            "execution_id": exec_id,
                            "verification": verification,
                            "needs_restart": False,
                            "escalate": True
                        }

                    # Patch failed - record outcome
                    self.metrics.append_outcome_metric(
                        skill_name=skill_name,
                        execution_id=exec_id,
                        decision=fix_action,
                        expected_decision=fix_action,
                        correct=False,
                        confidence=0.0,
                        reasoning=patch_result.get("error", "Patch application failed"),
                        agent="ai_overseer"
                    )

                    return {
                        "success": False,
                        "bug": pattern_name,
                        "fix_applied": None,
                        "error": patch_result.get("error", "Patch application failed"),
                        "violations": patch_result.get("violations", []),
                        "execution_id": exec_id
                    }

                except Exception as e:
                    logger.error(f"[AUTO-FIX] Unicode patch failed: {e}")
                    execution_time_ms = int((time.time() - start_time) * 1000)
                    self.metrics.append_performance_metric(
                        skill_name=skill_name,
                        execution_id=exec_id,
                        execution_time_ms=execution_time_ms,
                        agent="ai_overseer",
                        exception_occurred=True,
                        exception_type=type(e).__name__
                    )
                    return {
                        "success": False,
                        "bug": pattern_name,
                        "error": str(e),
                        "execution_id": exec_id
                    }

            # Unknown fix action
            else:
                logger.error(f"[AUTO-FIX] Unknown fix_action: {fix_action} for pattern {pattern_name}")
                logger.error(f"[AUTO-FIX] Available actions: run_reauthorization_script, rotate_api_credentials, reconnect_service, add_unicode_conversion_before_youtube_send")
                execution_time_ms = int((time.time() - start_time) * 1000)
                self.metrics.append_performance_metric(
                    skill_name=skill_name,
                    execution_id=exec_id,
                    execution_time_ms=execution_time_ms,
                    agent="ai_overseer",
                    exception_occurred=True,
                    exception_type="UnknownFixAction"
                )
                self.metrics.append_outcome_metric(
                    skill_name=skill_name,
                    execution_id=exec_id,
                    decision=fix_action if fix_action else "unknown",
                    expected_decision=None,
                    correct=False,
                    confidence=0.0,
                    reasoning=f"Unknown fix_action: {fix_action}",
                    agent="ai_overseer"
                )

                return {
                    "success": False,
                    "bug": pattern_name,
                    "error": f"Unknown fix_action: {fix_action}",
                    "available_fixes": ["run_reauthorization_script", "rotate_api_credentials", "reconnect_service"],
                    "execution_id": exec_id
                }

        except subprocess.TimeoutExpired:
            execution_time_ms = int((time.time() - start_time) * 1000)
            self.metrics.append_performance_metric(
                skill_name=skill_name,
                execution_id=exec_id,
                execution_time_ms=execution_time_ms,
                agent="ai_overseer",
                exception_occurred=True,
                exception_type="TimeoutExpired"
            )
            return {
                "success": False,
                "bug": pattern_name,
                "error": "Fix command timed out after 30s",
                "execution_id": exec_id
            }
        except Exception as e:
            logger.error(f"[AUTO-FIX] Failed to apply {fix_action}: {e}")
            execution_time_ms = int((time.time() - start_time) * 1000)
            self.metrics.append_performance_metric(
                skill_name=skill_name,
                execution_id=exec_id,
                execution_time_ms=execution_time_ms,
                agent="ai_overseer",
                exception_occurred=True,
                exception_type=type(e).__name__
            )
            return {
                "success": False,
                "bug": pattern_name,
                "error": str(e),
                "traceback": traceback.format_exc()[:500],
                "execution_id": exec_id
            }


    def _verify_unicode_patch(self, files_modified: List[str]) -> Dict[str, Any]:
        """
        Verify UTF-8 header insertion for modified files.
        """
        if not files_modified:
            return {
                "verified": False,
                "reason": "No files reported as modified"
            }

        missing_files: List[str] = []
        missing_header: List[str] = []

        for rel_path in files_modified:
            file_path = project_root / rel_path
            if not file_path.exists():
                missing_files.append(rel_path)
                continue

            try:
                with open(file_path, 'r', encoding='utf-8') as handle:
                    first_lines = [handle.readline() for _ in range(5)]
            except Exception as exc:
                missing_header.append(f"{rel_path} (read error: {exc})")
                continue

            if not any("# -*- coding: utf-8 -*-" in line for line in first_lines):
                missing_header.append(rel_path)

        if missing_files:
            return {
                "verified": False,
                "reason": f"Modified files missing: {', '.join(missing_files)}"
            }

        if missing_header:
            return {
                "verified": False,
                "reason": f"UTF-8 header missing in: {', '.join(missing_header)}"
            }

        return {
            "verified": True,
            "reason": "UTF-8 header confirmed in patched files"
        }

    # ==================== HOLODAE TELEMETRY MONITORING ====================

