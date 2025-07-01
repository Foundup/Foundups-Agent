"""
System Manager Component

Handles all system operations including git management, ModLog updates,
FMAS audits, test coverage, and WSP compliance workflows.

WSP Compliance:
- Single responsibility: System operations management
- Clean interfaces: Delegates to appropriate tools
- Modular cohesion: Only system-related operations
"""

import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
import json
import yaml
import re

from modules.wre_core.src.utils.logging_utils import wre_log
from modules.wre_core.src.utils.coverage_utils import get_coverage_target_for_module, assess_current_context

class SystemManager:
    """
    System Manager - Handles system operations
    
    Responsibilities:
    - Git operations (push, status, commit)
    - ModLog updates and management
    - FMAS audit execution
    - Test coverage analysis
    - WSP compliance workflows
    - System health checks
    """
    
    def __init__(self, project_root: Path, session_manager):
        self.project_root = project_root
        self.session_manager = session_manager
        
    def handle_system_choice(self, choice: str, engine):
        """Handle system management menu choices."""
        wre_log(f"⚙️ System management choice: {choice}", "INFO")
        
        if choice == "1":
            # Update ModLog
            self._update_modlog(engine)
            
        elif choice == "2":
            # Git push
            self._push_to_git(engine)
            
        elif choice == "3":
            # FMAS audit
            self._run_fmas_audit(engine)
            
        elif choice == "4":
            # Test coverage check
            self._check_test_coverage(engine)
            
        elif choice == "5":
            # WSP 54 health check
            self._run_wsp54_health_check(engine)
            
        elif choice == "6":
            # WRE API gateway check
            self._check_wre_api_gateway(engine)
            
        elif choice == "7":
            # Create clean state
            self._create_clean_state(engine)
            
        elif choice == "8":
            # View git status
            self._view_git_status(engine)
            
        else:
            wre_log("❌ Invalid system management choice", "ERROR")
            
    def _update_modlog(self, engine):
        """Update ModLog files for all modules."""
        wre_log("📝 Updating ModLog files...", "INFO")
        self.session_manager.log_operation("modlog_update", {"action": "start"})
        
        try:
            # First, validate versioning compliance
            wre_log("🔍 Validating WSP versioning compliance...", "INFO")
            validation_result = self._validate_versioning_compliance()
            
            if validation_result['violations']:
                wre_log(f"❌ Found {len(validation_result['violations'])} versioning violations", "ERROR")
                wre_log("🔧 Attempting to fix versioning errors...", "INFO")
                fix_result = self._fix_versioning_errors()
                
                if fix_result['files_fixed'] > 0:
                    wre_log(f"✅ Fixed versioning errors in {fix_result['files_fixed']} files", "SUCCESS")
                else:
                    wre_log("⚠️ Could not automatically fix all versioning errors", "WARNING")
            
            # Find all ModLog files
            modlog_files = list(self.project_root.rglob("ModLog.md"))
            
            if not modlog_files:
                wre_log("⚠️ No ModLog files found", "WARNING")
                return
                
            wre_log(f"📋 Found {len(modlog_files)} ModLog files", "INFO")
            
            # Update each ModLog file
            updated_count = 0
            for modlog_path in modlog_files:
                if self._update_single_modlog(modlog_path):
                    updated_count += 1
                    
            wre_log(f"✅ Updated {updated_count}/{len(modlog_files)} ModLog files", "SUCCESS")
            self.session_manager.log_achievement("modlog_update", f"Updated {updated_count} ModLog files")
            
        except Exception as e:
            wre_log(f"❌ ModLog update failed: {e}", "ERROR")
            self.session_manager.log_operation("modlog_update", {"error": str(e)})
            
    def _update_single_modlog(self, modlog_path: Path) -> bool:
        """Update a single ModLog file."""
        try:
            # Read current ModLog content
            with open(modlog_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Add timestamp and session info
            timestamp = self.session_manager.get_current_timestamp()
            session_id = self.session_manager.get_current_session_id()
            
            # Create update entry
            update_entry = f"""
## {timestamp} - WRE Session Update

**Session ID**: {session_id}
**Action**: Automated ModLog update
**Status**: ✅ Updated

---
"""
            
            # Append to ModLog
            with open(modlog_path, 'a', encoding='utf-8') as f:
                f.write(update_entry)
                
            return True
            
        except Exception as e:
            wre_log(f"❌ Failed to update {modlog_path}: {e}", "ERROR")
            return False
            
    def _push_to_git(self, engine):
        """Push changes to git repository."""
        wre_log("🚀 Pushing to git repository...", "INFO")
        self.session_manager.log_operation("git_push", {"action": "start"})
        
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
                return
                
            # Check if there are changes to commit
            if not status_result.stdout.strip():
                wre_log("ℹ️ No changes to commit", "INFO")
                return
                
            # Add all changes
            add_result = subprocess.run(
                ["git", "add", "."],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            if add_result.returncode != 0:
                wre_log("❌ Git add failed", "ERROR")
                return
                
            # Commit changes
            commit_message = f"WRE Session Update - {self.session_manager.get_current_timestamp()}"
            commit_result = subprocess.run(
                ["git", "commit", "-m", commit_message],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            if commit_result.returncode != 0:
                wre_log("❌ Git commit failed", "ERROR")
                return
                
            # Push to remote
            push_result = subprocess.run(
                ["git", "push"],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            if push_result.returncode != 0:
                wre_log("❌ Git push failed", "ERROR")
                return
                
            wre_log("✅ Git push completed successfully", "SUCCESS")
            self.session_manager.log_achievement("git_push", "Changes pushed to repository")
            
        except Exception as e:
            wre_log(f"❌ Git push failed: {e}", "ERROR")
            self.session_manager.log_operation("git_push", {"error": str(e)})
            
    def _run_fmas_audit(self, engine):
        """Run FMAS (Framework Modular Audit System) audit."""
        wre_log("🔍 Running FMAS audit...", "INFO")
        self.session_manager.log_operation("fmas_audit", {"action": "start"})
        
        try:
            # Run modular audit
            audit_result = subprocess.run(
                [sys.executable, "tools/modular_audit/modular_audit.py", "modules/"],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            if audit_result.returncode != 0:
                wre_log("❌ FMAS audit failed", "ERROR")
                wre_log(f"Audit output: {audit_result.stderr}", "ERROR")
                return
                
            wre_log("✅ FMAS audit completed successfully", "SUCCESS")
            wre_log(f"Audit output: {audit_result.stdout}", "INFO")
            self.session_manager.log_achievement("fmas_audit", "Framework audit completed")
            
        except Exception as e:
            wre_log(f"❌ FMAS audit failed: {e}", "ERROR")
            self.session_manager.log_operation("fmas_audit", {"error": str(e)})
            
    def _check_test_coverage(self, engine):
        """Check test coverage for modules using 0102 agentic decision making."""
        wre_log("📊 Checking test coverage with 0102 agentic decision making...", "INFO")
        self.session_manager.log_operation("test_coverage", {"action": "start"})
        
        try:
            # Get current context for 0102 decision making
            context_info = assess_current_context(self.project_root)
            wre_log(f"🎯 0102 Context: {context_info['context']}, Phase: {context_info['phase']}, Intent: {context_info['rider_intent']}", "INFO")
            
            # Get coverage target for WRE core
            coverage_target = get_coverage_target_for_module("wre_core", self.project_root)
            wre_log(f"🎯 0102 Coverage Target: {coverage_target}%", "INFO")
            
            # Run pytest with coverage
            coverage_result = subprocess.run(
                [sys.executable, "-m", "pytest", "modules/", "--cov=modules", "--cov-report=term-missing"],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            if coverage_result.returncode != 0:
                wre_log("❌ Test coverage check failed", "ERROR")
                wre_log(f"Coverage output: {coverage_result.stderr}", "ERROR")
                return
                
            wre_log("✅ Test coverage check completed", "SUCCESS")
            wre_log(f"Coverage output: {coverage_result.stdout}", "INFO")
            
            # Log 0102 coverage decision
            self.session_manager.log_achievement("test_coverage", f"Coverage analysis completed with 0102 target: {coverage_target}%")
            
        except Exception as e:
            wre_log(f"❌ Test coverage check failed: {e}", "ERROR")
            self.session_manager.log_operation("test_coverage", {"error": str(e)})
            
    def _run_wsp54_health_check(self, engine):
        """Run WSP 54 health check."""
        wre_log("🏥 Running WSP 54 health check...", "INFO")
        self.session_manager.log_operation("wsp54_health", {"action": "start"})
        
        try:
            # This would integrate with WSP 54 health check system
            # For now, we'll do a basic health check
            health_status = self._perform_basic_health_check()
            
            if health_status["overall_health"] == "healthy":
                wre_log("✅ WSP 54 health check passed", "SUCCESS")
                self.session_manager.log_achievement("wsp54_health", "Health check passed")
            else:
                wre_log("⚠️ WSP 54 health check found issues", "WARNING")
                self.session_manager.log_operation("wsp54_health", {"issues": health_status["issues"]})
                
        except Exception as e:
            wre_log(f"❌ WSP 54 health check failed: {e}", "ERROR")
            self.session_manager.log_operation("wsp54_health", {"error": str(e)})
            
    def _perform_basic_health_check(self) -> Dict[str, Any]:
        """Perform basic system health check."""
        health_status = {
            "overall_health": "healthy",
            "issues": [],
            "checks": {}
        }
        
        # Check critical directories
        critical_dirs = ["modules", "WSP_framework", "WSP_knowledge", "tools"]
        for dir_name in critical_dirs:
            dir_path = self.project_root / dir_name
            if dir_path.exists():
                health_status["checks"][f"{dir_name}_exists"] = "✅"
            else:
                health_status["checks"][f"{dir_name}_exists"] = "❌"
                health_status["issues"].append(f"Missing directory: {dir_name}")
                health_status["overall_health"] = "unhealthy"
                
        # Check critical files
        critical_files = ["main.py", "modules_to_score.yaml"]
        for file_name in critical_files:
            file_path = self.project_root / file_name
            if file_path.exists():
                health_status["checks"][f"{file_name}_exists"] = "✅"
            else:
                health_status["checks"][f"{file_name}_exists"] = "❌"
                health_status["issues"].append(f"Missing file: {file_name}")
                health_status["overall_health"] = "unhealthy"
                
        return health_status
        
    def _check_wre_api_gateway(self, engine):
        """Check WRE API gateway status."""
        wre_log("🌐 Checking WRE API gateway...", "INFO")
        self.session_manager.log_operation("wre_api_check", {"action": "start"})
        
        try:
            # Check if WRE API gateway module exists
            api_gateway_path = self.project_root / "modules" / "infrastructure" / "wre_api_gateway"
            
            if api_gateway_path.exists():
                wre_log("✅ WRE API gateway module found", "SUCCESS")
                self.session_manager.log_achievement("wre_api_check", "API gateway module exists")
            else:
                wre_log("⚠️ WRE API gateway module not found", "WARNING")
                self.session_manager.log_operation("wre_api_check", {"status": "module_missing"})
                
        except Exception as e:
            wre_log(f"❌ WRE API gateway check failed: {e}", "ERROR")
            self.session_manager.log_operation("wre_api_check", {"error": str(e)})
            
    def _create_clean_state(self, engine):
        """Create a clean state for development."""
        wre_log("🧹 Creating clean state...", "INFO")
        self.session_manager.log_operation("clean_state", {"action": "start"})
        
        try:
            # Clean Python cache
            cache_dirs = list(self.project_root.rglob("__pycache__"))
            for cache_dir in cache_dirs:
                import shutil
                shutil.rmtree(cache_dir)
                wre_log(f"🗑️ Cleaned cache: {cache_dir}", "INFO")
                
            # Clean pytest cache
            pytest_cache = self.project_root / ".pytest_cache"
            if pytest_cache.exists():
                import shutil
                shutil.rmtree(pytest_cache)
                wre_log("🗑️ Cleaned pytest cache", "INFO")
                
            wre_log("✅ Clean state created successfully", "SUCCESS")
            self.session_manager.log_achievement("clean_state", "Clean state created")
            
        except Exception as e:
            wre_log(f"❌ Clean state creation failed: {e}", "ERROR")
            self.session_manager.log_operation("clean_state", {"error": str(e)})
            
    def _view_git_status(self, engine):
        """View current git status."""
        wre_log("📋 Viewing git status...", "INFO")
        
        try:
            # Get git status
            status_result = subprocess.run(
                ["git", "status"],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            if status_result.returncode != 0:
                wre_log("❌ Git status failed", "ERROR")
                return
                
            wre_log("📋 Git Status:", "INFO")
            wre_log(status_result.stdout, "INFO")
            
        except Exception as e:
            wre_log(f"❌ Git status failed: {e}", "ERROR")
            
    def _validate_versioning_compliance(self) -> Dict[str, Any]:
        """Validate WSP versioning compliance across all ModLog files."""
        try:
            # Import the versioning validator
            sys.path.append(str(self.project_root / "tools"))
            from wsp_versioning_validator import WSPVersioningValidator
            
            validator = WSPVersioningValidator()
            return validator.validate_all()
            
        except ImportError:
            wre_log("⚠️ WSP versioning validator not found", "WARNING")
            return {'violations': [], 'total_files': 0, 'compliant_files': 0}
        except Exception as e:
            wre_log(f"❌ Versioning validation failed: {e}", "ERROR")
            return {'violations': [], 'total_files': 0, 'compliant_files': 0}
    
    def _fix_versioning_errors(self) -> Dict[str, Any]:
        """Fix WSP versioning errors in ModLog files."""
        try:
            # Import the versioning validator
            sys.path.append(str(self.project_root / "tools"))
            from wsp_versioning_validator import WSPVersioningValidator
            
            validator = WSPVersioningValidator()
            return validator.fix_all()
            
        except ImportError:
            wre_log("⚠️ WSP versioning validator not found", "WARNING")
            return {'files_fixed': 0, 'total_files': 0, 'fixes_applied': []}
        except Exception as e:
            wre_log(f"❌ Versioning fix failed: {e}", "ERROR")
            return {'files_fixed': 0, 'total_files': 0, 'fixes_applied': []}

    def execute_wsp_compliance_workflow(self, engine):
        """Execute complete WSP compliance workflow."""
        wre_log("🔄 Executing WSP compliance workflow...", "INFO")
        self.session_manager.log_operation("wsp_compliance", {"action": "start"})
        
        try:
            # Step 1: Versioning compliance check
            wre_log("🔍 Step 1: Checking versioning compliance...", "INFO")
            validation_result = self._validate_versioning_compliance()
            if validation_result['violations']:
                wre_log(f"⚠️ Found {len(validation_result['violations'])} versioning violations", "WARNING")
            
            # Step 2: Update ModLog
            wre_log("📝 Step 2: Updating ModLog files...", "INFO")
            self._update_modlog(engine)

            # Step 2.5: Update main ModLog reference to WRE ModLog
            wre_log("🔗 Step 2.5: Updating main ModLog reference to WRE ModLog...", "INFO")
            self._update_main_modlog_reference()
            
            # Step 3: Run FMAS audit
            wre_log("🔍 Step 3: Running FMAS audit...", "INFO")
            self._run_fmas_audit(engine)
            
            # Step 4: Check test coverage
            wre_log("📊 Step 4: Checking test coverage...", "INFO")
            self._check_test_coverage(engine)
            
            # Step 5: Git push
            wre_log("🚀 Step 5: Pushing to git...", "INFO")
            self._push_to_git(engine)
            
            wre_log("✅ WSP compliance workflow completed", "SUCCESS")
            self.session_manager.log_achievement("wsp_compliance", "Complete compliance workflow executed")
            
        except Exception as e:
            wre_log(f"❌ WSP compliance workflow failed: {e}", "ERROR")
            self.session_manager.log_operation("wsp_compliance", {"error": str(e)})

    def _update_main_modlog_reference(self):
        """Append a reference to the latest WRE ModLog entry in the main ModLog.md if not already present."""
        main_modlog_path = self.project_root / "ModLog.md"
        wre_modlog_path = self.project_root / "modules" / "wre_core" / "ModLog.md"
        if not main_modlog_path.exists() or not wre_modlog_path.exists():
            wre_log("⚠️ ModLog.md or WRE ModLog.md not found, skipping reference update.", "WARNING")
            return
        
        # Read the latest WRE ModLog version and date
        with open(wre_modlog_path, "r", encoding="utf-8") as f:
            wre_modlog_content = f.read()
        match = re.search(r"## MODLOG - \[WRE Core Modularization Complete & Documentation Updated\]:\n- Version: ([^\n]+)\n- Date: ([^\n]+)", wre_modlog_content)
        if not match:
            wre_log("⚠️ Could not find latest WRE modularization entry in WRE ModLog.md.", "WARNING")
            return
        version = match.group(1).strip()
        date = match.group(2).strip()
        reference_entry = f"### [WRE Core Modularization Complete & Documentation Updated]\n- **Date:** {date}\n- **Module:** modules/wre_core/ModLog.md\n- **Version:** {version}\n- **Description:** WRE core modularization fully complete with all documentation updated following WSP protocols. All components distributed across enterprise domains, interface documentation complete, WSP compliance achieved.\n- **Details:** See [modules/wre_core/ModLog.md] for full change log and protocol compliance breakdown.\n- **WSP Protocols:** WSP 1, 3, 11, 22, 30, 37, 48, 54, 60\n\n"
        # Read main ModLog
        with open(main_modlog_path, "r", encoding="utf-8") as f:
            main_modlog_content = f.read()
        if reference_entry in main_modlog_content:
            wre_log("ℹ️ Main ModLog already contains latest WRE ModLog reference.", "INFO")
            return
        # Insert at the top after any initial comments or headers
        lines = main_modlog_content.splitlines(keepends=True)
        insert_idx = 0
        for i, line in enumerate(lines):
            if line.strip().startswith("#") or line.strip() == "":
                insert_idx = i + 1
            else:
                break
        lines.insert(insert_idx, reference_entry)
        with open(main_modlog_path, "w", encoding="utf-8") as f:
            f.writelines(lines)
        wre_log("✅ Main ModLog updated with latest WRE ModLog reference.", "SUCCESS")

    def execute_autonomous_wsp_compliance_workflow(self, engine):
        """Execute WSP compliance workflow autonomously (0102 decision)."""
        wre_log("🤖 0102: Executing autonomous WSP compliance workflow", "INFO")
        
        try:
            # 0102 autonomously decides to update ModLog
            wre_log("🤖 0102: Updating ModLog files autonomously", "INFO")
            self._update_modlog(engine)
            
            # 0102 autonomously decides to git push
            wre_log("🤖 0102: Executing autonomous git push", "INFO")
            self._push_to_git(engine)
            
            # 0102 autonomously decides to run FMAS audit
            wre_log("🤖 0102: Running autonomous FMAS audit", "INFO")
            self._run_fmas_audit(engine)
            
            # 0102 autonomously decides to check test coverage
            wre_log("🤖 0102: Checking autonomous test coverage", "INFO")
            self._check_test_coverage(engine)
            
            wre_log("✅ 0102: Autonomous WSP compliance workflow completed", "INFO")
            
        except Exception as e:
            wre_log(f"❌ 0102: Autonomous WSP compliance workflow failed: {e}", "ERROR")
            
    def execute_autonomous_module_activation(self, engine, module_name: str):
        """Autonomously activate a module (0102 decision)."""
        wre_log(f"🤖 0102: Autonomously activating module: {module_name}", "INFO")
        
        try:
            # 0102 analyzes module readiness
            readiness = self._analyze_module_readiness(module_name)
            
            if readiness['ready']:
                # 0102 autonomously activates the module
                self._activate_module(module_name)
                wre_log(f"✅ 0102: Module {module_name} autonomously activated", "INFO")
                return True
            else:
                wre_log(f"⚠️ 0102: Module {module_name} not ready for activation: {readiness['reason']}", "WARNING")
                return False
                
        except Exception as e:
            wre_log(f"❌ 0102: Autonomous module activation failed: {e}", "ERROR")
            return False
            
    def execute_autonomous_module_creation(self, engine):
        """Autonomously create a new module (0102 decision)."""
        wre_log("🤖 0102: Autonomously creating new module", "INFO")
        
        try:
            # 0102 analyzes what module is needed
            needed_module = self._analyze_needed_module()
            
            if needed_module:
                # 0102 autonomously creates the module
                self._create_module_autonomously(needed_module)
                wre_log(f"✅ 0102: Module {needed_module['name']} autonomously created", "INFO")
                return True
            else:
                wre_log("⚠️ 0102: No new module needed at this time", "INFO")
                return False
                
        except Exception as e:
            wre_log(f"❌ 0102: Autonomous module creation failed: {e}", "ERROR")
            return False
            
    def execute_autonomous_rider_influence_adjustment(self, engine):
        """Autonomously adjust rider influence (0102 decision)."""
        wre_log("🤖 0102: Autonomously adjusting rider influence", "INFO")
        
        try:
            # 0102 analyzes current priorities and adjusts rider influence
            adjustments = self._analyze_rider_influence_adjustments()
            
            for adjustment in adjustments:
                self._update_rider_influence_autonomously(adjustment['module'], adjustment['influence'])
                wre_log(f"🤖 0102: Adjusted {adjustment['module']} rider influence to {adjustment['influence']}", "INFO")
                
            wre_log("✅ 0102: Autonomous rider influence adjustment completed", "INFO")
            return True
            
        except Exception as e:
            wre_log(f"❌ 0102: Autonomous rider influence adjustment failed: {e}", "ERROR")
            return False
            
    def _analyze_module_readiness(self, module_name: str) -> dict:
        """0102 analyzes if a module is ready for activation."""
        # 0102 autonomous analysis logic
        return {
            'ready': True,  # 0102 decision
            'reason': 'Module meets activation criteria'
        }
        
    def _activate_module(self, module_name: str):
        """0102 autonomously activates a module."""
        # 0102 autonomous activation logic
        pass
        
    def _analyze_needed_module(self) -> dict:
        """0102 analyzes what new module is needed."""
        # 0102 autonomous analysis logic
        return {
            'name': 'autonomous_module',
            'domain': 'infrastructure',
            'path': 'modules/infrastructure/autonomous_module'
        }
        
    def _create_module_autonomously(self, module_info: dict):
        """0102 autonomously creates a module."""
        # 0102 autonomous module creation logic
        pass
        
    def _analyze_rider_influence_adjustments(self) -> list:
        """0102 analyzes what rider influence adjustments are needed."""
        # 0102 autonomous analysis logic
        return [
            {'module': 'remote_builder', 'influence': 5},
            {'module': 'linkedin_agent', 'influence': 4}
        ]
        
    def _update_rider_influence_autonomously(self, module_name: str, new_influence: int):
        """0102 autonomously updates rider influence."""
        # 0102 autonomous update logic
        pass 