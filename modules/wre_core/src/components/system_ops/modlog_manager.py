"""
ModLog Manager Component

Handles all ModLog operations and management.
Extracted from system_manager.py per WSP 62 refactoring requirements.

WSP Compliance:
- WSP 62: Large File and Refactoring Enforcement Protocol (refactoring)
- WSP 1: Single responsibility principle (ModLog operations only)
- WSP 22: Traceable Narrative compliance
"""

from pathlib import Path
from typing import Dict, Any, List
from modules.wre_core.src.utils.logging_utils import wre_log


class ModLogManager:
    """
    ModLog Manager - Handles ModLog operations and management
    
    Responsibilities:
    - ModLog file updates
    - ModLog validation and compliance
    - ModLog content management
    - Cross-module ModLog coordination
    """
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        
    def update_modlog(self, session_manager):
        """Update ModLog files for all modules."""
        wre_log("📝 Updating ModLog files...", "INFO")
        session_manager.log_operation("modlog_update", {"action": "start"})
        
        try:
            # Find all ModLog files
            modlog_files = list(self.project_root.rglob("ModLog.md"))
            
            if not modlog_files:
                wre_log("⚠️ No ModLog files found", "WARNING")
                return False
                
            wre_log(f"📋 Found {len(modlog_files)} ModLog files", "INFO")
            
            # Update each ModLog file
            updated_count = 0
            for modlog_path in modlog_files:
                if self._update_single_modlog(modlog_path, session_manager):
                    updated_count += 1
                    
            wre_log(f"✅ Updated {updated_count}/{len(modlog_files)} ModLog files", "SUCCESS")
            session_manager.log_achievement("modlog_update", f"Updated {updated_count} ModLog files")
            return True
            
        except Exception as e:
            wre_log(f"❌ ModLog update failed: {e}", "ERROR")
            session_manager.log_operation("modlog_update", {"error": str(e)})
            return False
            
    def _update_single_modlog(self, modlog_path: Path, session_manager) -> bool:
        """Update a single ModLog file."""
        try:
            # Read current ModLog content
            with open(modlog_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Add timestamp and session info
            timestamp = session_manager.get_current_timestamp()
            session_id = session_manager.get_current_session_id()
            
            # Create update entry
            update_entry = f"""
## {timestamp} - WRE Session Update

**Session ID**: {session_id}
**Action**: Automated ModLog update via ModLogManager
**Component**: {modlog_path.parent.name if modlog_path.parent.name != 'Foundups-Agent' else 'root'}
**Status**: ✅ Updated
**WSP 22**: Traceable narrative maintained

---
"""
            
            # Append to ModLog
            with open(modlog_path, 'a', encoding='utf-8') as f:
                f.write(update_entry)
                
            wre_log(f"✅ Updated ModLog: {modlog_path.relative_to(self.project_root)}", "SUCCESS")
            return True
            
        except Exception as e:
            wre_log(f"❌ Failed to update {modlog_path}: {e}", "ERROR")
            return False
            
    def validate_modlog_compliance(self) -> Dict[str, Any]:
        """Validate ModLog compliance across all modules."""
        wre_log("🔍 Validating ModLog compliance...", "INFO")
        
        validation_result = {
            'total_modules': 0,
            'compliant_modules': 0,
            'non_compliant_modules': [],
            'missing_modlogs': [],
            'issues': []
        }
        
        try:
            # Check modules directory
            modules_path = self.project_root / "modules"
            if not modules_path.exists():
                validation_result['issues'].append("Modules directory not found")
                return validation_result
                
            # Check each module for ModLog compliance
            for module_dir in modules_path.iterdir():
                if module_dir.is_dir() and not module_dir.name.startswith('.'):
                    validation_result['total_modules'] += 1
                    
                    modlog_path = module_dir / "ModLog.md"
                    if not modlog_path.exists():
                        validation_result['missing_modlogs'].append(str(module_dir.name))
                    else:
                        # Check ModLog content compliance
                        if self._check_modlog_compliance(modlog_path):
                            validation_result['compliant_modules'] += 1
                        else:
                            validation_result['non_compliant_modules'].append(str(module_dir.name))
                            
            wre_log(f"📊 ModLog compliance: {validation_result['compliant_modules']}/{validation_result['total_modules']} modules compliant", "INFO")
            
            if validation_result['missing_modlogs']:
                wre_log(f"⚠️ Missing ModLogs: {', '.join(validation_result['missing_modlogs'])}", "WARNING")
                
            if validation_result['non_compliant_modules']:
                wre_log(f"⚠️ Non-compliant ModLogs: {', '.join(validation_result['non_compliant_modules'])}", "WARNING")
                
        except Exception as e:
            validation_result['issues'].append(f"Validation error: {str(e)}")
            wre_log(f"❌ ModLog validation failed: {e}", "ERROR")
            
        return validation_result
        
    def _check_modlog_compliance(self, modlog_path: Path) -> bool:
        """Check if a ModLog file meets WSP 22 compliance requirements."""
        try:
            with open(modlog_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Basic compliance checks per WSP 22
            has_version_header = '# ModLog' in content or '## ModLog' in content
            has_timestamp_entries = any(line.strip().startswith('##') and ('202' in line) for line in content.split('\n'))
            has_wsp_references = 'WSP' in content
            has_traceable_narrative = len(content) > 100  # Basic content length check
            
            return has_version_header and has_timestamp_entries and has_wsp_references and has_traceable_narrative
            
        except Exception:
            return False
            
    def create_modlog_for_module(self, module_path: Path, module_name: str) -> bool:
        """Create a new ModLog file for a module."""
        try:
            modlog_path = module_path / "ModLog.md"
            
            if modlog_path.exists():
                wre_log(f"⚠️ ModLog already exists for {module_name}", "WARNING")
                return False
                
            # Create initial ModLog content
            initial_content = f"""# ModLog - {module_name}

**Module**: {module_name}
**Created**: {self._get_current_timestamp()}
**WSP Compliance**: WSP 22 - Traceable Narrative

## Purpose
This ModLog tracks all changes, enhancements, and compliance activities for the {module_name} module per WSP 22 protocols.

## Change History

### {self._get_current_timestamp()} - Initial Creation

**Action**: ModLog creation via ModLogManager
**WSP 22**: Traceable narrative initialized
**Status**: ✅ Created
**Next Actions**: Module development per WSP protocols

---
"""
            
            # Write initial content
            with open(modlog_path, 'w', encoding='utf-8') as f:
                f.write(initial_content)
                
            wre_log(f"✅ Created ModLog for {module_name}", "SUCCESS")
            return True
            
        except Exception as e:
            wre_log(f"❌ Failed to create ModLog for {module_name}: {e}", "ERROR")
            return False
            
    def update_modlog_with_entry(self, module_path: Path, entry_data: Dict[str, str]) -> bool:
        """Update a specific ModLog with a custom entry."""
        try:
            modlog_path = module_path / "ModLog.md"
            
            if not modlog_path.exists():
                wre_log(f"⚠️ ModLog not found at {modlog_path}", "WARNING")
                return False
                
            # Create entry from data
            timestamp = entry_data.get('timestamp', self._get_current_timestamp())
            action = entry_data.get('action', 'Update')
            details = entry_data.get('details', 'ModLog entry')
            wsp_reference = entry_data.get('wsp_reference', 'WSP 22')
            status = entry_data.get('status', '✅ Updated')
            
            entry = f"""
### {timestamp} - {action}

**Action**: {details}
**WSP Reference**: {wsp_reference}
**Status**: {status}
**Component**: ModLogManager

---
"""
            
            # Append entry
            with open(modlog_path, 'a', encoding='utf-8') as f:
                f.write(entry)
                
            wre_log(f"✅ Updated ModLog with custom entry: {action}", "SUCCESS")
            return True
            
        except Exception as e:
            wre_log(f"❌ Failed to update ModLog with entry: {e}", "ERROR")
            return False
            
    def get_modlog_summary(self) -> Dict[str, Any]:
        """Get a summary of all ModLog files in the project."""
        summary = {
            'total_modlogs': 0,
            'recent_updates': [],
            'compliance_status': 'UNKNOWN',
            'oldest_update': None,
            'newest_update': None
        }
        
        try:
            modlog_files = list(self.project_root.rglob("ModLog.md"))
            summary['total_modlogs'] = len(modlog_files)
            
            if modlog_files:
                # Analyze ModLog files
                update_dates = []
                for modlog_path in modlog_files:
                    try:
                        with open(modlog_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            
                        # Extract recent updates (simplified)
                        lines = content.split('\n')
                        for line in lines:
                            if line.strip().startswith('##') and '202' in line:
                                summary['recent_updates'].append({
                                    'file': str(modlog_path.relative_to(self.project_root)),
                                    'update': line.strip()
                                })
                                # Keep only last 10 updates
                                if len(summary['recent_updates']) > 10:
                                    summary['recent_updates'] = summary['recent_updates'][-10:]
                                    
                    except Exception:
                        continue
                        
                # Set compliance status based on count
                if summary['total_modlogs'] >= 5:
                    summary['compliance_status'] = 'GOOD'
                elif summary['total_modlogs'] >= 3:
                    summary['compliance_status'] = 'MODERATE'
                else:
                    summary['compliance_status'] = 'NEEDS_IMPROVEMENT'
                    
        except Exception as e:
            summary['error'] = str(e)
            
        return summary
        
    def _get_current_timestamp(self) -> str:
        """Get current timestamp in standard format."""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
    def list_all_modlogs(self) -> List[Dict[str, str]]:
        """List all ModLog files with their basic information."""
        modlogs = []
        
        try:
            modlog_files = list(self.project_root.rglob("ModLog.md"))
            
            for modlog_path in modlog_files:
                try:
                    # Get basic file info
                    relative_path = modlog_path.relative_to(self.project_root)
                    
                    # Get file size
                    file_size = modlog_path.stat().st_size
                    
                    # Get module name
                    if modlog_path.parent.name == 'Foundups-Agent':
                        module_name = 'root'
                    else:
                        module_name = modlog_path.parent.name
                        
                    modlogs.append({
                        'path': str(relative_path),
                        'module': module_name,
                        'size_bytes': file_size,
                        'size_readable': self._format_file_size(file_size)
                    })
                    
                except Exception:
                    continue
                    
        except Exception as e:
            wre_log(f"❌ Failed to list ModLogs: {e}", "ERROR")
            
        return modlogs
        
    def _format_file_size(self, size_bytes: int) -> str:
        """Format file size in human-readable format."""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.1f} MB" 