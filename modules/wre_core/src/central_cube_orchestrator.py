#!/usr/bin/env python3
"""
Central Cube Orchestrator - Modular System Integration Hub

This orchestrator provides:
1. Feature flag management for all system modules
2. Safe module initialization with fallbacks
3. Health monitoring across all components
4. Unified command interface for system control
5. WSP-compliant module coordination

WSP Compliance: This implements WSP 30 (Agentic Module Build Orchestration)
and provides the central coordination point for all FoundUps Agent modules.
"""

import asyncio
import logging
import sys
import json
from datetime import datetime
from typing import Dict, Optional, Any, List
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModuleStatus(Enum):
    """Module operational status"""
    DISABLED = "disabled"
    LOADING = "loading"
    ACTIVE = "active"
    ERROR = "error"
    MAINTENANCE = "maintenance"

@dataclass
class FeatureFlag:
    """Feature flag configuration"""
    name: str
    enabled: bool
    description: str
    dependencies: List[str] = None
    experimental: bool = False
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []

@dataclass
class ModuleConfig:
    """Module configuration structure"""
    name: str
    path: str
    feature_flag: str
    dependencies: List[str]
    status: ModuleStatus
    instance: Optional[Any] = None
    last_health_check: Optional[datetime] = None
    error_message: Optional[str] = None

class CentralCubeOrchestrator:
    """
    Central Cube Orchestrator - System Integration Hub
    
    Coordinates all FoundUps Agent modules with feature flags,
    health monitoring, and graceful degradation.
    """
    
    def __init__(self):
        self.feature_flags = {}
        self.modules = {}
        self.running = False
        self.start_time = None
        
        # Initialize feature flags
        self._setup_feature_flags()
        
        # Initialize module configurations
        self._setup_module_configs()
        
        logger.info("Central Cube Orchestrator initialized")
    
    def _setup_feature_flags(self):
        """Initialize feature flags for all system components"""
        flags = [
            # Core Infrastructure
            FeatureFlag(
                name="wre_core",
                enabled=True,
                description="Windsurf Recursive Engine core functionality",
                dependencies=[]
            ),
            FeatureFlag(
                name="oauth_management", 
                enabled=True,
                description="OAuth authentication and credential management",
                dependencies=[]
            ),
            
            # Platform Integrations
            FeatureFlag(
                name="youtube_integration",
                enabled=True,
                description="YouTube API integration and live chat",
                dependencies=["oauth_management"]
            ),
            FeatureFlag(
                name="linkedin_integration",
                enabled=False,  # Mock only for now
                description="LinkedIn integration (mock service)",
                dependencies=["oauth_management"],
                experimental=True
            ),
            FeatureFlag(
                name="twitter_integration",
                enabled=False,  # Mock only for now
                description="X/Twitter integration (mock service)", 
                dependencies=["oauth_management"],
                experimental=True
            ),
            
            # AI Intelligence
            FeatureFlag(
                name="banter_engine",
                enabled=True,
                description="AI banter response engine",
                dependencies=["youtube_integration"]
            ),
            FeatureFlag(
                name="0102_orchestrator",
                enabled=True,
                description="0102 Agentic orchestration system",
                dependencies=["wre_core"]
            ),
            
            # Communication
            FeatureFlag(
                name="auto_meeting_orchestrator",
                enabled=True,
                description="Autonomous meeting orchestration (AMO)",
                dependencies=[]
            ),
            FeatureFlag(
                name="livechat_listener",
                enabled=True,
                description="YouTube live chat monitoring",
                dependencies=["youtube_integration"]
            ),
            
            # Development Tools
            FeatureFlag(
                name="cursor_bridge",
                enabled=False,  # Disabled by default for safety
                description="Cursor IDE integration bridge",
                dependencies=["wre_core"],
                experimental=True
            ),
            FeatureFlag(
                name="module_scaffolding",
                enabled=True,
                description="Automatic module scaffolding",
                dependencies=["wre_core"]
            ),
        ]
        
        for flag in flags:
            self.feature_flags[flag.name] = flag
    
    def _setup_module_configs(self):
        """Initialize module configurations"""
        configs = [
            # Core Infrastructure
            ModuleConfig(
                name="WRE Core",
                path="modules.wre_core.src.main",
                feature_flag="wre_core",
                dependencies=[],
                status=ModuleStatus.DISABLED
            ),
            ModuleConfig(
                name="OAuth Manager", 
                path="modules.infrastructure.oauth_management.src.oauth_manager",
                feature_flag="oauth_management",
                dependencies=[],
                status=ModuleStatus.DISABLED
            ),
            
            # Platform Integrations
            ModuleConfig(
                name="YouTube Proxy",
                path="modules.platform_integration.youtube_proxy.src.youtube_proxy",
                feature_flag="youtube_integration", 
                dependencies=["oauth_management"],
                status=ModuleStatus.DISABLED
            ),
            
            # Communication
            ModuleConfig(
                name="Auto Meeting Orchestrator",
                path="modules.communication.auto_meeting_orchestrator.src.orchestrator",
                feature_flag="auto_meeting_orchestrator",
                dependencies=[],
                status=ModuleStatus.DISABLED
            ),
            ModuleConfig(
                name="LiveChat Listener",
                path="modules.communication.livechat.src.livechat",
                feature_flag="livechat_listener",
                dependencies=["youtube_integration"],
                status=ModuleStatus.DISABLED
            ),
            
            # AI Intelligence
            ModuleConfig(
                name="Banter Engine",
                path="modules.ai_intelligence.banter_engine.src.banter_engine",
                feature_flag="banter_engine",
                dependencies=["youtube_integration"],
                status=ModuleStatus.DISABLED
            ),
        ]
        
        for config in configs:
            self.modules[config.name] = config
    
    async def start_orchestrator(self):
        """Start the central orchestrator and initialize enabled modules"""
        logger.info("🚀 Starting Central Cube Orchestrator")
        self.running = True
        self.start_time = datetime.now()
        
        # Initialize modules based on feature flags
        await self._initialize_enabled_modules()
        
        # Start health monitoring
        asyncio.create_task(self._health_monitor_loop())
        
        logger.info("✅ Central Cube Orchestrator started successfully")
    
    async def _initialize_enabled_modules(self):
        """Initialize all enabled modules in dependency order"""
        # Get enabled modules sorted by dependency order
        enabled_modules = self._get_enabled_modules_by_dependency_order()
        
        for module_name in enabled_modules:
            await self._initialize_module(module_name)
    
    def _get_enabled_modules_by_dependency_order(self) -> List[str]:
        """Get enabled modules sorted by their dependencies"""
        enabled_modules = []
        
        for name, config in self.modules.items():
            flag = self.feature_flags.get(config.feature_flag)
            if flag and flag.enabled:
                enabled_modules.append(name)
        
        # Simple dependency sorting (can be enhanced with topological sort)
        # For now, sort by number of dependencies (least dependencies first)
        enabled_modules.sort(key=lambda name: len(self.modules[name].dependencies))
        
        return enabled_modules
    
    async def _initialize_module(self, module_name: str):
        """Initialize a specific module with error handling"""
        config = self.modules[module_name]
        
        logger.info(f"🔄 Initializing {module_name}...")
        config.status = ModuleStatus.LOADING
        
        try:
            # Check dependencies
            for dep in config.dependencies:
                dep_config = None
                for name, cfg in self.modules.items():
                    if cfg.feature_flag == dep:
                        dep_config = cfg
                        break
                
                if not dep_config or dep_config.status != ModuleStatus.ACTIVE:
                    raise Exception(f"Dependency '{dep}' not available")
            
            # Attempt to import and initialize the module
            if module_name == "OAuth Manager":
                from modules.infrastructure.oauth_management.src.oauth_manager import OAuthManager
                config.instance = OAuthManager(platform="system", logger=logger)
                
            elif module_name == "Auto Meeting Orchestrator":
                from modules.communication.auto_meeting_orchestrator.src.orchestrator import MeetingOrchestrator
                from modules.communication.auto_meeting_orchestrator.src.heartbeat_service import AMOHeartbeatService
                
                amo = MeetingOrchestrator()
                heartbeat = AMOHeartbeatService(amo, heartbeat_interval=60)  # 1 minute intervals
                
                # Start heartbeat in background
                asyncio.create_task(heartbeat.start_heartbeat())
                
                config.instance = {"orchestrator": amo, "heartbeat": heartbeat}
                
            elif module_name == "YouTube Proxy":
                from modules.platform_integration.youtube_proxy.src.youtube_proxy import YouTubeProxy
                config.instance = YouTubeProxy(logger=logger)
                
            elif module_name == "LiveChat Listener":
                from modules.communication.livechat.src.livechat import LiveChatListener
                # Create a placeholder instance (needs YouTube service to be functional)
                config.instance = {"class": LiveChatListener, "status": "ready"}
                
            elif module_name == "Banter Engine":
                from modules.ai_intelligence.banter_engine.src.banter_engine import BanterEngine
                config.instance = BanterEngine()
                
            else:
                # Generic module initialization
                logger.warning(f"⚠️ Generic initialization for {module_name} - may need specific handling")
                config.instance = {"status": "generic_init", "name": module_name}
            
            config.status = ModuleStatus.ACTIVE
            config.last_health_check = datetime.now()
            config.error_message = None
            
            logger.info(f"✅ {module_name} initialized successfully")
            
        except ImportError as e:
            logger.error(f"❌ {module_name} import failed: {e}")
            config.status = ModuleStatus.ERROR
            config.error_message = f"Import error: {e}"
            
        except Exception as e:
            logger.error(f"❌ {module_name} initialization failed: {e}")
            config.status = ModuleStatus.ERROR
            config.error_message = str(e)
    
    async def _health_monitor_loop(self):
        """Background health monitoring for all active modules"""
        while self.running:
            try:
                await self._perform_health_checks()
                await asyncio.sleep(60)  # Check every minute
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Health monitor error: {e}")
                await asyncio.sleep(30)  # Shorter interval on error
    
    async def _perform_health_checks(self):
        """Perform health checks on all active modules"""
        for name, config in self.modules.items():
            if config.status == ModuleStatus.ACTIVE:
                try:
                    # Basic health check - verify instance exists and is responsive
                    if config.instance is None:
                        config.status = ModuleStatus.ERROR
                        config.error_message = "Instance is None"
                        continue
                    
                    # Module-specific health checks
                    if name == "Auto Meeting Orchestrator":
                        # Check AMO heartbeat service
                        heartbeat = config.instance.get("heartbeat")
                        if heartbeat and hasattr(heartbeat, 'get_health_status'):
                            health = heartbeat.get_health_status()
                            if health.get("status") == "offline":
                                logger.warning(f"⚠️ {name} heartbeat offline")
                    
                    config.last_health_check = datetime.now()
                    
                except Exception as e:
                    logger.error(f"❌ Health check failed for {name}: {e}")
                    config.status = ModuleStatus.ERROR
                    config.error_message = f"Health check failed: {e}"
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        uptime = (datetime.now() - self.start_time).total_seconds() if self.start_time else 0
        
        module_stats = {}
        for name, config in self.modules.items():
            module_stats[name] = {
                "status": config.status.value,
                "feature_flag": self.feature_flags.get(config.feature_flag, {}).enabled,
                "last_health_check": config.last_health_check.isoformat() if config.last_health_check else None,
                "error_message": config.error_message
            }
        
        return {
            "orchestrator_status": "running" if self.running else "stopped",
            "uptime_seconds": uptime,
            "modules": module_stats,
            "feature_flags": {name: flag.enabled for name, flag in self.feature_flags.items()},
            "timestamp": datetime.now().isoformat()
        }
    
    def set_feature_flag(self, flag_name: str, enabled: bool) -> bool:
        """Enable or disable a feature flag"""
        if flag_name not in self.feature_flags:
            return False
        
        self.feature_flags[flag_name].enabled = enabled
        logger.info(f"🚩 Feature flag '{flag_name}' set to: {enabled}")
        return True
    
    def get_feature_flags(self) -> Dict[str, bool]:
        """Get all feature flag states"""
        return {name: flag.enabled for name, flag in self.feature_flags.items()}
    
    async def stop_orchestrator(self):
        """Stop the orchestrator and clean up resources"""
        logger.info("🛑 Stopping Central Cube Orchestrator...")
        self.running = False
        
        # Stop all modules
        for name, config in self.modules.items():
            if config.status == ModuleStatus.ACTIVE and config.instance:
                try:
                    # Module-specific cleanup
                    if name == "Auto Meeting Orchestrator":
                        heartbeat = config.instance.get("heartbeat")
                        if heartbeat and hasattr(heartbeat, 'stop_heartbeat'):
                            heartbeat.stop_heartbeat()
                    
                    config.status = ModuleStatus.DISABLED
                    config.instance = None
                    
                except Exception as e:
                    logger.error(f"❌ Error stopping {name}: {e}")
        
        logger.info("✅ Central Cube Orchestrator stopped")

# CLI Interface
async def main():
    """Interactive CLI for the Central Cube Orchestrator"""
    print("=== Central Cube Orchestrator ===")
    print("Initializing system...")
    
    orchestrator = CentralCubeOrchestrator()
    
    try:
        await orchestrator.start_orchestrator()
        
        print("\nSystem initialized. Available commands:")
        print("  status  - Show system status")
        print("  flags   - Show feature flags")
        print("  flag <name> <on|off> - Toggle feature flag")
        print("  quit    - Exit orchestrator")
        
        while True:
            try:
                command = input("\nOrchestrator> ").strip().lower()
                
                if command == "quit" or command == "exit":
                    break
                    
                elif command == "status":
                    status = orchestrator.get_system_status()
                    print(json.dumps(status, indent=2))
                    
                elif command == "flags":
                    flags = orchestrator.get_feature_flags()
                    print("\nFeature Flags:")
                    for name, enabled in flags.items():
                        status_icon = "✅" if enabled else "❌"
                        print(f"  {status_icon} {name}: {enabled}")
                        
                elif command.startswith("flag "):
                    parts = command.split()
                    if len(parts) == 3:
                        flag_name, state = parts[1], parts[2]
                        enabled = state.lower() in ["on", "true", "1", "yes"]
                        if orchestrator.set_feature_flag(flag_name, enabled):
                            print(f"✅ Flag '{flag_name}' set to {enabled}")
                        else:
                            print(f"❌ Unknown flag: {flag_name}")
                    else:
                        print("Usage: flag <name> <on|off>")
                        
                elif command == "":
                    continue
                    
                else:
                    print(f"Unknown command: {command}")
                    
            except KeyboardInterrupt:
                break
            except EOFError:
                break
    
    finally:
        await orchestrator.stop_orchestrator()
        print("\nOrchestrator shutdown complete.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nInterrupted by user")