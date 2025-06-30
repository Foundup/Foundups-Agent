# WSP 54 JanitorAgent - The Cleaner
# Core Mandate: Maintain workspace hygiene and module memory organization following WSP 60 three-state architecture

import os
import shutil
import json
import time
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime, timedelta

class JanitorAgent:
    def __init__(self):
        """Initializes the Janitor Agent (WSP-54 Duty 3.4)."""
        self.project_root = Path(__file__).resolve().parent.parent.parent.parent.parent
        self.wsp_knowledge = self.project_root / "WSP_knowledge"
        self.wsp_agentic = self.project_root / "WSP_agentic"
        self.modules_root = self.project_root / "modules"
        self.memory_backup_root = self.wsp_knowledge / "memory_backup_wsp60"
        print("JanitorAgent initialized for WSP 60 memory hygiene management.")

    def clean_workspace(self) -> Dict:
        """
        WSP-54 Duty 3.4.1: Scan workspace for temporary files and cleanup operations.
        
        Returns:
            Dict with cleanup results and WSP_48 enhancement opportunities
        """
        print("🧹 Starting comprehensive workspace cleanup...")
        
        cleanup_results = {
            "temp_files_removed": 0,
            "cache_files_cleaned": 0,
            "memory_operations": 0,
            "logs_rotated": 0,
            "total_space_freed": 0,
            "wsp48_enhancements": []
        }
        
        try:
            # WSP-54 Duty 3.4.1: Scan for temporary files
            cleanup_results.update(self._cleanup_temporary_files())
            
            # WSP-54 Duty 3.4.3: WSP 60 Module Memory Cleanup
            cleanup_results.update(self._cleanup_module_memory())
            
            # WSP-54 Duty 3.4.4: Cache Management
            cleanup_results.update(self._manage_cache_files())
            
            # WSP-54 Duty 3.4.5: Log Rotation
            cleanup_results.update(self._rotate_logs())
            
            # WSP-54 Duty 3.4.6: State 0 Archive Management
            cleanup_results.update(self._manage_state0_archives())
            
            # WSP-54 Duty 3.4.7: Memory Usage Analytics
            analytics = self._generate_memory_analytics()
            cleanup_results["memory_analytics"] = analytics
            
            print(f"✅ Workspace cleanup completed: {cleanup_results['temp_files_removed']} temp files, {cleanup_results['total_space_freed']} bytes freed")
            
            return {
                "status": "success",
                "operation": "workspace_cleanup",
                **cleanup_results
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "wsp48_enhancement": "janitor_infrastructure_failure",
                "enhancement_trigger": f"JanitorAgent needs robustness improvement: {e}"
            }

    def _cleanup_temporary_files(self) -> Dict:
        """Remove temporary files and directories."""
        temp_patterns = [
            "*.tmp", "*.temp", "*~", ".DS_Store",
            "__pycache__", "*.pyc", "*.pyo",
            "test_wre_temp", "temp_*", ".pytest_cache"
        ]
        
        removed_count = 0
        space_freed = 0
        
        for pattern in temp_patterns:
            for temp_file in self.project_root.rglob(pattern):
                try:
                    if temp_file.is_file():
                        space_freed += temp_file.stat().st_size
                        temp_file.unlink()
                        removed_count += 1
                    elif temp_file.is_dir():
                        space_freed += sum(f.stat().st_size for f in temp_file.rglob('*') if f.is_file())
                        shutil.rmtree(temp_file)
                        removed_count += 1
                except Exception as e:
                    print(f"⚠️  Could not remove {temp_file}: {e}")
        
        return {
            "temp_files_removed": removed_count,
            "temp_space_freed": space_freed
        }

    def _cleanup_module_memory(self) -> Dict:
        """WSP-54 Duty 3.4.3: Clean temporary files across module memory directories."""
        memory_operations = 0
        
        for domain_dir in self.modules_root.iterdir():
            if domain_dir.is_dir():
                for module_dir in domain_dir.iterdir():
                    if module_dir.is_dir():
                        memory_dir = module_dir / "memory"
                        if memory_dir.exists():
                            # Clean expired session data
                            self._clean_expired_sessions(memory_dir)
                            
                            # Validate memory structure
                            self._validate_memory_structure(memory_dir)
                            
                            memory_operations += 1
        
        return {"memory_operations": memory_operations}

    def _manage_cache_files(self) -> Dict:
        """WSP-54 Duty 3.4.4: Remove expired session data and cache files."""
        cache_cleaned = 0
        
        # Clean module session caches
        for domain_dir in self.modules_root.iterdir():
            if domain_dir.is_dir():
                for module_dir in domain_dir.iterdir():
                    if module_dir.is_dir():
                        cache_file = module_dir / "memory" / "session_cache.json"
                        if cache_file.exists():
                            # Check if cache is older than 24 hours
                            if time.time() - cache_file.stat().st_mtime > 86400:
                                cache_file.unlink()
                                cache_cleaned += 1
        
        return {"cache_files_cleaned": cache_cleaned}

    def _rotate_logs(self) -> Dict:
        """WSP-54 Duty 3.4.5: Archive old conversation logs per module retention policies."""
        logs_rotated = 0
        
        # Rotate conversation logs older than 7 days
        cutoff_time = time.time() - (7 * 86400)  # 7 days
        
        for domain_dir in self.modules_root.iterdir():
            if domain_dir.is_dir():
                for module_dir in domain_dir.iterdir():
                    if module_dir.is_dir():
                        memory_dir = module_dir / "memory"
                        if memory_dir.exists():
                            for log_file in memory_dir.glob("conversation_*.json"):
                                if log_file.stat().st_mtime < cutoff_time:
                                    # Archive to State 0
                                    archive_path = self._archive_to_state0(log_file, module_dir.name)
                                    if archive_path:
                                        log_file.unlink()
                                        logs_rotated += 1
        
        return {"logs_rotated": logs_rotated}

    def _manage_state0_archives(self) -> Dict:
        """WSP-54 Duty 3.4.6: Coordinate archival of old memory states to WSP_knowledge."""
        if not self.memory_backup_root.exists():
            self.memory_backup_root.mkdir(parents=True)
        
        # Clean archives older than 30 days
        cutoff_time = time.time() - (30 * 86400)  # 30 days
        old_archives = 0
        
        for archive_dir in self.memory_backup_root.iterdir():
            if archive_dir.is_dir() and archive_dir.stat().st_mtime < cutoff_time:
                shutil.rmtree(archive_dir)
                old_archives += 1
        
        return {"old_archives_cleaned": old_archives}

    def _generate_memory_analytics(self) -> Dict:
        """WSP-54 Duty 3.4.7: Track and report memory usage patterns across modules."""
        analytics = {
            "total_modules_with_memory": 0,
            "total_memory_size": 0,
            "memory_per_domain": {},
            "largest_memory_modules": []
        }
        
        module_sizes = []
        
        for domain_dir in self.modules_root.iterdir():
            if domain_dir.is_dir():
                domain_memory = 0
                
                for module_dir in domain_dir.iterdir():
                    if module_dir.is_dir():
                        memory_dir = module_dir / "memory"
                        if memory_dir.exists():
                            analytics["total_modules_with_memory"] += 1
                            
                            # Calculate memory usage
                            module_memory = sum(f.stat().st_size for f in memory_dir.rglob('*') if f.is_file())
                            domain_memory += module_memory
                            analytics["total_memory_size"] += module_memory
                            
                            module_sizes.append({
                                "module": f"{domain_dir.name}/{module_dir.name}",
                                "size": module_memory
                            })
                
                analytics["memory_per_domain"][domain_dir.name] = domain_memory
        
        # Find largest memory modules
        module_sizes.sort(key=lambda x: x["size"], reverse=True)
        analytics["largest_memory_modules"] = module_sizes[:5]
        
        return analytics

    def _clean_expired_sessions(self, memory_dir: Path):
        """Clean expired session data from module memory."""
        session_files = memory_dir.glob("session_*.json")
        cutoff_time = time.time() - 3600  # 1 hour
        
        for session_file in session_files:
            if session_file.stat().st_mtime < cutoff_time:
                try:
                    session_file.unlink()
                except Exception as e:
                    print(f"⚠️  Could not remove expired session {session_file}: {e}")

    def _validate_memory_structure(self, memory_dir: Path):
        """WSP-54 Duty 3.4.9: Ensure module memory maintains proper structure."""
        required_files = ["memory_index.json"]
        
        for required_file in required_files:
            file_path = memory_dir / required_file
            if not file_path.exists():
                # Create missing memory index
                self._create_memory_index(file_path)

    def _create_memory_index(self, index_path: Path):
        """Create missing memory index for module coordination."""
        memory_index = {
            "created": datetime.now().isoformat(),
            "version": "1.0",
            "memory_type": "module_memory",
            "wsp_compliance": "WSP_60",
            "retention_policy": "7_days_active",
            "files": []
        }
        
        with open(index_path, 'w') as f:
            json.dump(memory_index, f, indent=2)

    def _archive_to_state0(self, log_file: Path, module_name: str) -> Optional[Path]:
        """Archive log file to State 0 (WSP_knowledge) following WSP 60."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            archive_dir = self.memory_backup_root / timestamp / module_name
            archive_dir.mkdir(parents=True, exist_ok=True)
            
            archive_path = archive_dir / log_file.name
            shutil.copy2(log_file, archive_path)
            
            return archive_path
        except Exception as e:
            print(f"⚠️  Could not archive {log_file}: {e}")
            return None

    def coordinate_with_agents(self) -> Dict:
        """WSP-54 Duty 3.4.8: Cross-Module Coordination with other WSP 54 agents."""
        coordination_results = {
            "compliance_validations": 0,
            "chronicler_logs": 0,
            "documentation_updates": 0
        }
        
        # This would integrate with ComplianceAgent, ChroniclerAgent, etc.
        # For now, return coordination readiness
        
        return {
            "status": "coordination_ready",
            "results": coordination_results,
            "agents_available": ["ComplianceAgent", "ChroniclerAgent", "DocumentationAgent"]
        } 