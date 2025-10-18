#!/usr/bin/env python3
"""
WSP 60: Module Memory Architecture - Migration Utility
Safely migrates memory data from legacy paths to module-specific paths.

This utility provides:
1. Safe migration with backup
2. Validation of migrated data  
3. Rollback capability
4. Migration progress tracking
"""

import os
import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple
import logging

from memory_path_resolver import MemoryPathResolver

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WSP60MemoryMigrator:
    """WSP 60 compliant memory migration utility."""
    
    def __init__(self, project_root: Path = None):
        """Initialize migrator."""
        self.project_root = project_root or Path.cwd()
        self.resolver = MemoryPathResolver(self.project_root)
        self.backup_dir = self.project_root / "memory_backup_wsp60" / datetime.now().strftime("%Y%m%d_%H%M%S")
        self.migration_log = []
        
    def create_backup(self) -> bool:
        """Create backup of current memory structure."""
        try:
            legacy_memory = self.project_root / "memory"
            if not legacy_memory.exists():
                logger.info("No legacy memory directory to backup")
                return True
                
            self.backup_dir.mkdir(parents=True, exist_ok=True)
            shutil.copytree(legacy_memory, self.backup_dir / "memory")
            
            # Also backup any existing module memory
            for module_path in ["modules/infrastructure/agent_management/memory",
                               "modules/communication/livechat/memory", 
                               "modules/ai_intelligence/banter_engine/memory",
                               "modules/platform_integration/youtube_proxy/memory"]:
                full_path = self.project_root / module_path
                if full_path.exists():
                    backup_path = self.backup_dir / module_path
                    backup_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copytree(full_path, backup_path)
            
            logger.info(f"Backup created: {self.backup_dir}")
            return True
            
        except Exception as e:
            logger.error(f"Backup creation failed: {e}")
            return False
    
    def migrate_agent_management_data(self) -> bool:
        """Migrate agent management files to WSP 60 module memory."""
        logger.info("Starting agent management data migration...")
        
        files_to_migrate = [
            "agent_registry.json",
            "same_account_conflicts.json", 
            "session_cache.json"
        ]
        
        success_count = 0
        for filename in files_to_migrate:
            if self._migrate_single_file(filename):
                success_count += 1
            
        success = success_count == len(files_to_migrate)
        logger.info(f"Agent management migration: {success_count}/{len(files_to_migrate)} files")
        return success
    
    def migrate_livechat_data(self) -> bool:
        """Migrate livechat data to WSP 60 module memory."""
        logger.info("Starting livechat data migration...")
        
        directories_to_migrate = [
            "conversations",
            "chat_logs", 
            "conversation"  # Legacy naming
        ]
        
        success_count = 0
        for dirname in directories_to_migrate:
            if self._migrate_single_directory(dirname):
                success_count += 1
                
        success = success_count == len(directories_to_migrate)
        logger.info(f"Livechat migration: {success_count}/{len(directories_to_migrate)} directories")
        return success
    
    def _migrate_single_file(self, filename: str) -> bool:
        """Migrate a single file using the resolver."""
        try:
            legacy_path = self.project_root / "memory" / filename
            
            if not legacy_path.exists():
                logger.warning(f"Legacy file does not exist: {filename}")
                return True  # Not an error if file doesn't exist
            
            # Check if we have a module mapping (don't use resolver for this)
            clean_filename = filename.replace("memory/", "").replace("memory\\", "")
            if clean_filename not in self.resolver.MODULE_MEMORY_MAPPING:
                logger.info(f"No module mapping for {filename}, keeping in legacy location")
                return True
            
            # Get the target module path directly from mapping
            module_path_str = self.resolver.MODULE_MEMORY_MAPPING[clean_filename]
            module_path = self.project_root / module_path_str
            
            # Create module directory
            module_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy file
            shutil.copy2(legacy_path, module_path)
            
            # Validate copy
            if self._validate_file_copy(legacy_path, module_path):
                self.migration_log.append({
                    "type": "file",
                    "source": str(legacy_path),
                    "target": str(module_path), 
                    "status": "success",
                    "timestamp": datetime.now().isoformat()
                })
                logger.info(f"Migrated: {filename} → {module_path}")
                return True
            else:
                logger.error(f"Validation failed for {filename}")
                return False
                
        except Exception as e:
            logger.error(f"Migration failed for {filename}: {e}")
            return False
    
    def _migrate_single_directory(self, dirname: str) -> bool:
        """Migrate a single directory using the resolver."""
        try:
            legacy_path = self.project_root / "memory" / dirname
            
            if not legacy_path.exists():
                logger.warning(f"Legacy directory does not exist: {dirname}")
                return True
            
            # Check if we have a module mapping (don't use resolver for this)
            clean_dirname = dirname.replace("memory/", "").replace("memory\\", "")
            if clean_dirname not in self.resolver.MODULE_MEMORY_MAPPING:
                logger.info(f"No module mapping for {dirname}, keeping in legacy location")
                return True
            
            # Get the target module path directly from mapping
            module_path_str = self.resolver.MODULE_MEMORY_MAPPING[clean_dirname]
            module_path = self.project_root / module_path_str
            
            # Create module directory
            module_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy directory
            if module_path.exists():
                shutil.rmtree(module_path)  # Remove existing
            shutil.copytree(legacy_path, module_path)
            
            # Validate copy
            if self._validate_directory_copy(legacy_path, module_path):
                self.migration_log.append({
                    "type": "directory",
                    "source": str(legacy_path),
                    "target": str(module_path),
                    "status": "success", 
                    "timestamp": datetime.now().isoformat()
                })
                logger.info(f"Migrated: {dirname}/ → {module_path}/")
                return True
            else:
                logger.error(f"Validation failed for {dirname}")
                return False
                
        except Exception as e:
            logger.error(f"Migration failed for {dirname}: {e}")
            return False
    
    def _validate_file_copy(self, source: Path, target: Path) -> bool:
        """Validate file was copied correctly."""
        if not target.exists():
            return False
        
        # Check file size
        if source.stat().st_size != target.stat().st_size:
            return False
        
        # For JSON files, validate structure
        if source.suffix == '.json':
            try:
                with open(source, 'r', encoding='utf-8') as f:
                    source_data = json.load(f)
                with open(target, 'r', encoding='utf-8') as f:
                    target_data = json.load(f)
                return source_data == target_data
            except Exception:
                return False
        
        return True
    
    def _validate_directory_copy(self, source: Path, target: Path) -> bool:
        """Validate directory was copied correctly."""
        if not target.exists():
            return False
        
        # Check file count
        source_files = list(source.rglob('*'))
        target_files = list(target.rglob('*'))
        
        if len(source_files) != len(target_files):
            return False
        
        # Validate a few key files
        for source_file in source_files[:5]:  # Check first 5 files
            relative_path = source_file.relative_to(source)
            target_file = target / relative_path
            
            if source_file.is_file() and not self._validate_file_copy(source_file, target_file):
                return False
        
        return True
    
    def get_migration_report(self) -> dict:
        """Get detailed migration report."""
        return {
            "timestamp": datetime.now().isoformat(),
            "backup_location": str(self.backup_dir),
            "total_migrations": len(self.migration_log),
            "successful_migrations": len([m for m in self.migration_log if m["status"] == "success"]),
            "failed_migrations": len([m for m in self.migration_log if m["status"] == "failed"]),
            "migration_details": self.migration_log
        }
    
    def rollback_migration(self) -> bool:
        """Rollback migration using backup."""
        try:
            if not self.backup_dir.exists():
                logger.error("No backup found for rollback")
                return False
            
            # Restore legacy memory
            legacy_memory = self.project_root / "memory"
            if legacy_memory.exists():
                shutil.rmtree(legacy_memory)
            
            backup_memory = self.backup_dir / "memory"
            if backup_memory.exists():
                shutil.copytree(backup_memory, legacy_memory)
            
            # Remove migrated module memory
            for entry in self.migration_log:
                if entry["status"] == "success":
                    target_path = Path(entry["target"])
                    if target_path.exists():
                        if target_path.is_file():
                            target_path.unlink()
                        else:
                            shutil.rmtree(target_path)
            
            logger.info("Migration rolled back successfully")
            return True
            
        except Exception as e:
            logger.error(f"Rollback failed: {e}")
            return False


def main():
    """Main migration function."""
    migrator = WSP60MemoryMigrator()
    
    print("🚀 WSP 60 Memory Migration Starting...")
    print("=" * 50)
    
    # Create backup
    if not migrator.create_backup():
        print("❌ Backup creation failed - aborting migration")
        return False
    
    print("✅ Backup created successfully")
    
    # Phase 1: Agent Management Data
    print("\n📁 Phase 1: Agent Management Data")
    if migrator.migrate_agent_management_data():
        print("✅ Agent management data migrated")
    else:
        print("⚠️  Agent management migration had issues")
    
    # Phase 2: LiveChat Data  
    print("\n💬 Phase 2: LiveChat Data")
    if migrator.migrate_livechat_data():
        print("✅ LiveChat data migrated")
    else:
        print("⚠️  LiveChat migration had issues")
    
    # Generate report
    report = migrator.get_migration_report()
    print(f"\n📊 Migration Report:")
    print(f"   Total: {report['total_migrations']}")
    print(f"   Success: {report['successful_migrations']}")
    print(f"   Failed: {report['failed_migrations']}")
    print(f"   Backup: {report['backup_location']}")
    
    # Save report
    report_path = migrator.project_root / "WSP_agentic" / "migration_report_wsp60.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"📝 Report saved: {report_path}")
    
    return report['failed_migrations'] == 0

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 