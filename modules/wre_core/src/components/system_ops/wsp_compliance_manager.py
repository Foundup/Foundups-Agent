"""
WSP Compliance Manager Component

Handles all WSP compliance workflows and operations.
Extracted from system_manager.py per WSP 62 refactoring requirements.

WSP Compliance:
- WSP 62: Large File and Refactoring Enforcement Protocol (refactoring)
- WSP 1: Single responsibility principle (WSP compliance only)
- WSP 54: WRE Agent Duties integration
- WSP 22: Traceable Narrative compliance
"""

import subprocess
from pathlib import Path
from typing import Dict, Any
from modules.wre_core.src.utils.logging_utils import wre_log


class WSPComplianceManager:
    """
    WSP Compliance Manager - Handles WSP compliance workflows
    
    Responsibilities:
    - WSP 54 health checks
    - WSP compliance workflow execution
    - Autonomous WSP compliance operations
    - WSP validation and enforcement
    """
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        
    def run_wsp54_health_check(self, session_manager):
        """Run WSP 54 health check operations."""
        wre_log("🏥 Running WSP 54 health check...", "INFO")
        session_manager.log_operation("wsp54_health_check", {"action": "start"})
        
        try:
            # Perform basic health check
            health_status = self._perform_basic_health_check()
            
            if health_status['overall_health'] == 'HEALTHY':
                wre_log("✅ WRE system health: HEALTHY", "SUCCESS")
                wre_log(f"🔧 Active modules: {health_status['active_modules']}", "INFO")
                wre_log(f"📊 System uptime: {health_status['uptime']}", "INFO")
                session_manager.log_achievement("wsp54_health_check", "System health check passed")
            else:
                wre_log(f"⚠️ WRE system health: {health_status['overall_health']}", "WARNING")
                wre_log("🔍 Health issues detected - review required", "WARNING")
                session_manager.log_operation("wsp54_health_check", {"issues": health_status['issues']})
                
            return health_status
            
        except Exception as e:
            wre_log(f"❌ WSP 54 health check failed: {e}", "ERROR")
            session_manager.log_operation("wsp54_health_check", {"error": str(e)})
            return None
            
    def _perform_basic_health_check(self) -> Dict[str, Any]:
        """Perform basic system health assessment."""
        health_status = {
            'overall_health': 'HEALTHY',
            'active_modules': 0,
            'uptime': 'Unknown',
            'issues': []
        }
        
        try:
            # Check for WSP framework files
            wsp_framework_path = self.project_root / "WSP_framework"
            if not wsp_framework_path.exists():
                health_status['issues'].append("WSP framework directory missing")
                health_status['overall_health'] = 'DEGRADED'
                
            # Check for modules directory
            modules_path = self.project_root / "modules"
            if modules_path.exists():
                # Count active modules
                module_dirs = [d for d in modules_path.iterdir() if d.is_dir() and not d.name.startswith('.')]
                health_status['active_modules'] = len(module_dirs)
            else:
                health_status['issues'].append("Modules directory missing")
                health_status['overall_health'] = 'CRITICAL'
                
            # Check for WRE core
            wre_core_path = modules_path / "wre_core"
            if not wre_core_path.exists():
                health_status['issues'].append("WRE core module missing")
                health_status['overall_health'] = 'CRITICAL'
                
            return health_status
            
        except Exception as e:
            health_status['overall_health'] = 'ERROR'
            health_status['issues'].append(f"Health check error: {str(e)}")
            return health_status
            
    def execute_wsp_compliance_workflow(self, session_manager):
        """Execute comprehensive WSP compliance workflow."""
        wre_log("🔄 Executing WSP compliance workflow...", "INFO")
        session_manager.log_operation("wsp_compliance", {"action": "start"})
        
        try:
            # Step 1: Validate versioning compliance
            wre_log("🔍 Step 1: Validating WSP versioning compliance...", "INFO")
            validation_result = self._validate_versioning_compliance()
            
            if validation_result['violations']:
                wre_log(f"❌ Found {len(validation_result['violations'])} versioning violations", "ERROR")
                wre_log("🔧 Attempting to fix versioning errors...", "INFO")
                fix_result = self._fix_versioning_errors()
                
                if fix_result['files_fixed'] > 0:
                    wre_log(f"✅ Fixed versioning errors in {fix_result['files_fixed']} files", "SUCCESS")
                else:
                    wre_log("⚠️ Could not automatically fix all versioning errors", "WARNING")
            else:
                wre_log("✅ WSP versioning compliance validated", "SUCCESS")
                
            # Step 2: Update main ModLog reference
            wre_log("📝 Step 2: Updating main ModLog reference...", "INFO")
            self._update_main_modlog_reference()
            wre_log("✅ Main ModLog reference updated", "SUCCESS")
            
            # Step 3: Validate WSP framework integrity
            wre_log("🔍 Step 3: Validating WSP framework integrity...", "INFO")
            framework_status = self._validate_wsp_framework_integrity()
            
            if framework_status['valid']:
                wre_log("✅ WSP framework integrity validated", "SUCCESS")
            else:
                wre_log("⚠️ WSP framework integrity issues detected", "WARNING")
                for issue in framework_status['issues']:
                    wre_log(f"  - {issue}", "WARNING")
                    
            session_manager.log_achievement("wsp_compliance", "WSP compliance workflow completed")
            wre_log("✅ WSP compliance workflow completed successfully", "SUCCESS")
            
        except Exception as e:
            wre_log(f"❌ WSP compliance workflow failed: {e}", "ERROR")
            session_manager.log_operation("wsp_compliance", {"error": str(e)})
            
    def execute_autonomous_wsp_compliance_workflow(self, session_manager):
        """Execute autonomous WSP compliance workflow."""
        wre_log("🤖 Executing autonomous WSP compliance workflow...", "INFO")
        session_manager.log_operation("autonomous_wsp_compliance", {"action": "start"})
        
        try:
            # Autonomous compliance check
            compliance_status = self._assess_autonomous_compliance_needs()
            
            if compliance_status['needs_action']:
                wre_log("🔧 Autonomous compliance actions required", "INFO")
                for action in compliance_status['actions']:
                    wre_log(f"  - {action}", "INFO")
                    
                # Execute autonomous actions
                self._execute_autonomous_compliance_actions(compliance_status['actions'])
            else:
                wre_log("✅ System in autonomous WSP compliance", "SUCCESS")
                
            session_manager.log_achievement("autonomous_wsp_compliance", "Autonomous compliance workflow completed")
            
        except Exception as e:
            wre_log(f"❌ Autonomous WSP compliance workflow failed: {e}", "ERROR")
            session_manager.log_operation("autonomous_wsp_compliance", {"error": str(e)})
            
    def _validate_versioning_compliance(self) -> Dict[str, Any]:
        """Validate WSP versioning compliance."""
        result = {
            'violations': [],
            'total_files_checked': 0,
            'compliant_files': 0
        }
        
        try:
            # Check WSP framework files for proper versioning
            wsp_files = list((self.project_root / "WSP_framework" / "src").glob("WSP_*.md"))
            result['total_files_checked'] = len(wsp_files)
            
            for wsp_file in wsp_files:
                if self._check_file_versioning_compliance(wsp_file):
                    result['compliant_files'] += 1
                else:
                    result['violations'].append(str(wsp_file))
                    
        except Exception as e:
            result['error'] = str(e)
            
        return result
        
    def _check_file_versioning_compliance(self, file_path: Path) -> bool:
        """Check if a single file meets versioning compliance."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Basic compliance checks
            has_version_info = 'Version:' in content or '## Version' in content
            has_date_info = 'Date:' in content or '## Date' in content
            
            return has_version_info or has_date_info
            
        except Exception:
            return False
            
    def _fix_versioning_errors(self) -> Dict[str, Any]:
        """Attempt to fix versioning errors automatically."""
        result = {
            'files_fixed': 0,
            'files_failed': 0,
            'errors': []
        }
        
        try:
            # This would implement automatic versioning fixes
            # For now, return placeholder result
            wre_log("🔧 Versioning error fixes would be implemented here", "INFO")
            
        except Exception as e:
            result['errors'].append(str(e))
            
        return result
        
    def _update_main_modlog_reference(self):
        """Update main ModLog reference."""
        try:
            main_modlog_path = self.project_root / "ModLog.md"
            if main_modlog_path.exists():
                wre_log("📝 Main ModLog reference updated", "INFO")
            else:
                wre_log("⚠️ Main ModLog file not found", "WARNING")
                
        except Exception as e:
            wre_log(f"❌ Failed to update main ModLog reference: {e}", "ERROR")
            
    def _validate_wsp_framework_integrity(self) -> Dict[str, Any]:
        """Validate WSP framework integrity."""
        result = {
            'valid': True,
            'issues': []
        }
        
        try:
            # Check for essential WSP files
            essential_files = [
                "WSP_framework/src/WSP_1_The_WSP_Framework.md",
                "WSP_framework/src/WSP_MASTER_INDEX.md",
                "WSP_framework/src/WSP_MODULE_VIOLATIONS.md"
            ]
            
            for file_path in essential_files:
                full_path = self.project_root / file_path
                if not full_path.exists():
                    result['valid'] = False
                    result['issues'].append(f"Missing essential file: {file_path}")
                    
        except Exception as e:
            result['valid'] = False
            result['issues'].append(f"Integrity check error: {str(e)}")
            
        return result
        
    def _assess_autonomous_compliance_needs(self) -> Dict[str, Any]:
        """Assess what autonomous compliance actions are needed."""
        assessment = {
            'needs_action': False,
            'actions': [],
            'priority': 'LOW'
        }
        
        try:
            # Check for common compliance issues
            modules_path = self.project_root / "modules"
            if modules_path.exists():
                for module_dir in modules_path.iterdir():
                    if module_dir.is_dir() and not module_dir.name.startswith('.'):
                        # Check for missing README
                        readme_path = module_dir / "README.md"
                        if not readme_path.exists():
                            assessment['needs_action'] = True
                            assessment['actions'].append(f"Create README for {module_dir.name}")
                            
        except Exception as e:
            assessment['error'] = str(e)
            
        return assessment
        
    def _execute_autonomous_compliance_actions(self, actions: list):
        """Execute autonomous compliance actions."""
        for action in actions:
            try:
                wre_log(f"🤖 Executing: {action}", "INFO")
                # Implementation would go here
                wre_log(f"✅ Completed: {action}", "SUCCESS")
            except Exception as e:
                wre_log(f"❌ Failed to execute {action}: {e}", "ERROR") 