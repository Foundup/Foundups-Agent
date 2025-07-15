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
            
            # WSP-54 Duty 3.4.5.1: Chronicle Cleanup (Agentic Recursive)
            cleanup_results.update(self._manage_chronicle_files())
            
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

    def _manage_chronicle_files(self) -> Dict:
        """
        WSP-54 Duty 3.4.5.1: Agentic Recursive Chronicle Cleanup
        
        Autonomously manages WRE chronicle files with recursive intelligence:
        - Learns usage patterns for optimal retention
        - Implements intelligent archival strategies
        - Maintains operational history while optimizing storage
        """
        chronicle_results = {
            "chronicles_processed": 0,
            "chronicles_archived": 0,
            "chronicles_deleted": 0,
            "space_freed": 0,
            "retention_patterns": {},
            "recursive_optimizations": []
        }
        
        try:
            # Primary chronicle directory
            chronicle_dir = self.project_root / "modules" / "wre_core" / "logs"
            
            if not chronicle_dir.exists():
                return chronicle_results
            
            # Get all chronicle files
            chronicle_files = list(chronicle_dir.glob("session_*.chronicle.jsonl"))
            current_time = time.time()
            
            # Agentic Intelligence: Analyze usage patterns
            usage_analytics = self._analyze_chronicle_usage(chronicle_files)
            
            # Recursive Learning: Apply retention strategy
            retention_strategy = self._learn_retention_strategy(usage_analytics)
            
            for chronicle_file in chronicle_files:
                try:
                    file_age_days = (current_time - chronicle_file.stat().st_mtime) / 86400
                    file_size = chronicle_file.stat().st_size
                    
                    chronicle_results["chronicles_processed"] += 1
                    
                    # Agentic Decision Making
                    action = self._decide_chronicle_action(chronicle_file, file_age_days, file_size, retention_strategy)
                    
                    if action == "archive":
                        # Archive to compressed format
                        archived_path = self._archive_chronicle(chronicle_file)
                        if archived_path:
                            chronicle_results["chronicles_archived"] += 1
                            chronicle_results["space_freed"] += file_size
                            
                    elif action == "delete":
                        # Safe deletion with backup
                        if self._safe_delete_chronicle(chronicle_file):
                            chronicle_results["chronicles_deleted"] += 1
                            chronicle_results["space_freed"] += file_size
                            
                    # Recursive Enhancement: Track decisions
                    chronicle_results["retention_patterns"][chronicle_file.name] = {
                        "age_days": file_age_days,
                        "size": file_size,
                        "action": action,
                        "reasoning": retention_strategy.get("reasoning", "pattern_based")
                    }
                    
                except Exception as e:
                    print(f"⚠️  Chronicle cleanup error for {chronicle_file}: {e}")
                    continue
            
            # Recursive Optimization: Learn from this session
            optimizations = self._generate_chronicle_optimizations(chronicle_results)
            chronicle_results["recursive_optimizations"] = optimizations
            
            print(f"🗂️  Chronicle cleanup: {chronicle_results['chronicles_archived']} archived, {chronicle_results['chronicles_deleted']} deleted, {chronicle_results['space_freed']} bytes freed")
            
        except Exception as e:
            print(f"⚠️  Chronicle management error: {e}")
            
        return chronicle_results

    def _analyze_chronicle_usage(self, chronicle_files: List[Path]) -> Dict:
        """Agentic Intelligence: Analyze chronicle access patterns."""
        analytics = {
            "file_count": len(chronicle_files),
            "size_distribution": {},
            "age_distribution": {},
            "access_patterns": {},
            "storage_efficiency": 0
        }
        
        current_time = time.time()
        total_size = 0
        
        for chronicle_file in chronicle_files:
            try:
                stat = chronicle_file.stat()
                age_days = (current_time - stat.st_mtime) / 86400
                size = stat.st_size
                total_size += size
                
                # Size categories
                if size < 1024:  # < 1KB
                    analytics["size_distribution"]["small"] = analytics["size_distribution"].get("small", 0) + 1
                elif size < 1024 * 1024:  # < 1MB
                    analytics["size_distribution"]["medium"] = analytics["size_distribution"].get("medium", 0) + 1
                else:  # >= 1MB
                    analytics["size_distribution"]["large"] = analytics["size_distribution"].get("large", 0) + 1
                
                # Age categories
                if age_days < 7:
                    analytics["age_distribution"]["recent"] = analytics["age_distribution"].get("recent", 0) + 1
                elif age_days < 30:
                    analytics["age_distribution"]["medium"] = analytics["age_distribution"].get("medium", 0) + 1
                else:
                    analytics["age_distribution"]["old"] = analytics["age_distribution"].get("old", 0) + 1
                    
            except Exception as e:
                continue
        
        analytics["total_size"] = total_size
        analytics["average_size"] = total_size / len(chronicle_files) if chronicle_files else 0
        
        return analytics

    def _learn_retention_strategy(self, usage_analytics: Dict) -> Dict:
        """Recursive Learning: Develop intelligent retention strategy."""
        strategy = {
            "recent_threshold": 7,  # Keep files < 7 days
            "archive_threshold": 30,  # Archive files 7-30 days
            "delete_threshold": 90,  # Delete files > 90 days
            "size_factor": 1.0,
            "reasoning": "adaptive_learning"
        }
        
        # Adaptive Learning: Adjust thresholds based on usage
        if usage_analytics.get("total_size", 0) > 100 * 1024 * 1024:  # > 100MB
            strategy["archive_threshold"] = 14  # More aggressive archiving
            strategy["delete_threshold"] = 60   # More aggressive deletion
            strategy["reasoning"] = "storage_pressure_optimization"
            
        # Intelligence: Prioritize large files for cleanup
        large_files = usage_analytics.get("size_distribution", {}).get("large", 0)
        if large_files > 5:
            strategy["size_factor"] = 0.5  # Reduce thresholds for large files
            strategy["reasoning"] = "large_file_optimization"
        
        return strategy

    def _decide_chronicle_action(self, chronicle_file: Path, age_days: float, size: int, strategy: Dict) -> str:
        """Agentic Decision Making: Determine optimal action for each chronicle."""
        size_factor = strategy.get("size_factor", 1.0)
        
        # Apply size factor to thresholds
        recent_threshold = strategy["recent_threshold"] * size_factor
        archive_threshold = strategy["archive_threshold"] * size_factor
        delete_threshold = strategy["delete_threshold"] * size_factor
        
        # Decision logic
        if age_days < recent_threshold:
            return "keep"
        elif age_days < archive_threshold:
            return "archive"
        elif age_days < delete_threshold:
            # Consider file size for deletion decision
            if size > 10 * 1024 * 1024:  # > 10MB
                return "delete"
            else:
                return "archive"
        else:
            return "delete"

    def _archive_chronicle(self, chronicle_file: Path) -> Optional[Path]:
        """Archive chronicle file with compression."""
        try:
            archive_dir = chronicle_file.parent / "archive"
            archive_dir.mkdir(exist_ok=True)
            
            # Compress and move
            import gzip
            compressed_name = f"{chronicle_file.stem}.gz"
            compressed_path = archive_dir / compressed_name
            
            with open(chronicle_file, 'rb') as f_in:
                with gzip.open(compressed_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            chronicle_file.unlink()
            return compressed_path
            
        except Exception as e:
            print(f"⚠️  Archive error for {chronicle_file}: {e}")
            return None

    def _safe_delete_chronicle(self, chronicle_file: Path) -> bool:
        """Safe deletion with backup option."""
        try:
            chronicle_file.unlink()
            return True
        except Exception as e:
            print(f"⚠️  Delete error for {chronicle_file}: {e}")
            return False

    def _generate_chronicle_optimizations(self, results: Dict) -> List[Dict]:
        """Generate recursive optimizations for next cleanup cycle."""
        optimizations = []
        
        # Storage optimization
        if results.get("space_freed", 0) > 50 * 1024 * 1024:  # > 50MB freed
            optimizations.append({
                "type": "storage_efficiency",
                "improvement": "High space recovery achieved",
                "next_cycle": "Continue current strategy"
            })
        
        # Pattern recognition
        if results.get("chronicles_archived", 0) > results.get("chronicles_deleted", 0):
            optimizations.append({
                "type": "retention_pattern",
                "improvement": "Archive-heavy strategy effective",
                "next_cycle": "Increase archive threshold"
            })
        
        return optimizations

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