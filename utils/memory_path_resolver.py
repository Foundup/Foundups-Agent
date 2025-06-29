#!/usr/bin/env python3
"""
WSP 60: Module Memory Architecture - Path Resolver
Provides backwards-compatible path resolution during memory migration.

This utility enables gradual migration from legacy memory/ folder to 
WSP 60 compliant module-specific memory directories without breaking 
existing functionality.
"""

import os
from pathlib import Path
from typing import Union
import logging

logger = logging.getLogger(__name__)

class MemoryPathResolver:
    """
    WSP 60 compliant memory path resolver with backwards compatibility.
    
    During migration period:
    1. Check if new module memory path exists and has data
    2. If not, fall back to legacy memory/ path  
    3. Log usage for migration tracking
    """
    
    # WSP 60 Module Memory Mapping
    MODULE_MEMORY_MAPPING = {
        # Agent Management Data
        "agent_registry.json": "modules/infrastructure/agent_management/memory/agent_registry.json",
        "same_account_conflicts.json": "modules/infrastructure/agent_management/memory/same_account_conflicts.json", 
        "session_cache.json": "modules/infrastructure/agent_management/memory/session_cache.json",
        
        # LiveChat Data
        "chat_logs": "modules/communication/livechat/memory/chat_logs",
        "conversations": "modules/communication/livechat/memory/conversations",
        "conversation": "modules/communication/livechat/memory/conversation",  # Legacy naming
        
        # Banter Engine Data
        "banter": "modules/ai_intelligence/banter_engine/memory/banter",
        "banter/banter_data.json": "modules/ai_intelligence/banter_engine/memory/banter_data.json",
        
        # Platform Integration Data  
        "stream_cache.json": "modules/platform_integration/youtube_proxy/memory/stream_cache.json",
        "api_rate_limits.json": "modules/platform_integration/youtube_proxy/memory/api_rate_limits.json",
    }
    
    def __init__(self, project_root: Union[str, Path] = None):
        """
        Initialize path resolver.
        
        Args:
            project_root: Project root directory (defaults to current working directory)
        """
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.legacy_memory = self.project_root / "memory"
        self.migration_log = []
        
    def resolve_path(self, memory_path: str) -> Path:
        """
        Resolve memory path with WSP 60 compliance and backwards compatibility.
        
        Args:
            memory_path: Legacy memory path (e.g., "memory/agent_registry.json")
            
        Returns:
            Path: Resolved path (module-specific if migrated, legacy if not)
        """
        # Remove "memory/" prefix if present
        clean_path = memory_path.replace("memory/", "").replace("memory\\", "")
        
        # Check if we have a WSP 60 module mapping
        if clean_path in self.MODULE_MEMORY_MAPPING:
            module_path = self.project_root / self.MODULE_MEMORY_MAPPING[clean_path]
            legacy_path = self.legacy_memory / clean_path
            
            # Migration logic: Use module path if it exists and has data, otherwise use legacy
            if module_path.exists() and self._has_meaningful_data(module_path):
                self._log_usage("module", clean_path, module_path)
                return module_path
            elif legacy_path.exists():
                self._log_usage("legacy", clean_path, legacy_path)
                return legacy_path
            else:
                # Neither exists - create in module location (WSP 60 compliant)
                self._log_usage("new_module", clean_path, module_path)
                module_path.parent.mkdir(parents=True, exist_ok=True)
                return module_path
        
        # No module mapping - use legacy path
        legacy_path = self.legacy_memory / clean_path
        self._log_usage("unmapped_legacy", clean_path, legacy_path)
        return legacy_path
    
    def _has_meaningful_data(self, path: Path) -> bool:
        """Check if path has meaningful data (not empty file/directory)."""
        if not path.exists():
            return False
        
        if path.is_file():
            return path.stat().st_size > 0
        elif path.is_dir():
            return any(path.iterdir())
        
        return False
    
    def _log_usage(self, path_type: str, original_path: str, resolved_path: Path):
        """Log path usage for migration tracking."""
        log_entry = {
            "type": path_type,
            "original": original_path, 
            "resolved": str(resolved_path),
            "exists": resolved_path.exists()
        }
        self.migration_log.append(log_entry)
        
        # Log to console for debugging
        logger.debug(f"WSP 60 Memory Path: {path_type} | {original_path} → {resolved_path}")
    
    def get_migration_status(self) -> dict:
        """Get migration status summary."""
        status = {
            "total_requests": len(self.migration_log),
            "module_paths": len([l for l in self.migration_log if l["type"] == "module"]),
            "legacy_paths": len([l for l in self.migration_log if l["type"] == "legacy"]),
            "new_module_paths": len([l for l in self.migration_log if l["type"] == "new_module"]),
            "unmapped_paths": len([l for l in self.migration_log if l["type"] == "unmapped_legacy"]),
            "log": self.migration_log
        }
        return status
    
    def migrate_file(self, memory_path: str) -> bool:
        """
        Migrate a specific file from legacy to module memory.
        
        Args:
            memory_path: Legacy memory path to migrate
            
        Returns:
            bool: True if migration successful, False otherwise
        """
        clean_path = memory_path.replace("memory/", "").replace("memory\\", "")
        
        if clean_path not in self.MODULE_MEMORY_MAPPING:
            logger.warning(f"No module mapping for {clean_path}")
            return False
        
        legacy_path = self.legacy_memory / clean_path
        module_path = self.project_root / self.MODULE_MEMORY_MAPPING[clean_path]
        
        if not legacy_path.exists():
            logger.warning(f"Legacy path does not exist: {legacy_path}")
            return False
        
        if module_path.exists():
            logger.info(f"Module path already exists: {module_path}")
            return True
        
        try:
            # Create module directory if needed
            module_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy file/directory
            if legacy_path.is_file():
                import shutil
                shutil.copy2(legacy_path, module_path)
            elif legacy_path.is_dir():
                import shutil
                shutil.copytree(legacy_path, module_path)
            
            logger.info(f"Migrated {legacy_path} → {module_path}")
            return True
            
        except Exception as e:
            logger.error(f"Migration failed for {legacy_path}: {e}")
            return False


# Global resolver instance for easy access
_resolver = None

def get_memory_path(memory_path: str) -> Path:
    """
    Global function for WSP 60 compliant memory path resolution.
    
    Usage:
        from utils.memory_path_resolver import get_memory_path
        
        # Instead of: "memory/agent_registry.json"
        path = get_memory_path("memory/agent_registry.json")
        # Returns: modules/infrastructure/agent_management/memory/agent_registry.json
    """
    global _resolver
    if _resolver is None:
        _resolver = MemoryPathResolver()
    
    return _resolver.resolve_path(memory_path)

def get_migration_status() -> dict:
    """Get global migration status."""
    global _resolver
    if _resolver is None:
        return {"status": "No paths resolved yet"}
    
    return _resolver.get_migration_status()

if __name__ == "__main__":
    # Test the resolver
    resolver = MemoryPathResolver()
    
    test_paths = [
        "memory/agent_registry.json",
        "memory/session_cache.json", 
        "memory/chat_logs",
        "memory/banter/banter_data.json"
    ]
    
    print("WSP 60 Memory Path Resolution Test:")
    print("=" * 50)
    
    for path in test_paths:
        resolved = resolver.resolve_path(path)
        print(f"{path} → {resolved}")
    
    print("\nMigration Status:")
    print("=" * 20)
    status = resolver.get_migration_status()
    for key, value in status.items():
        if key != "log":
            print(f"{key}: {value}") 