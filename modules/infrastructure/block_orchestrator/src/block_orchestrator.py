"""
Modular Block Runner Infrastructure
WSP Protocol: WSP 40 (Architectural Coherence), WSP 49 (Module Standards)

Revolutionary block independence system that enables each FoundUps block to run 
standalone while preserving all existing tested functionality.
"""

import logging
import asyncio
import sys
import os
from typing import Dict, Any, Optional, Protocol, runtime_checkable
from pathlib import Path
import importlib
from dataclasses import dataclass, field
from enum import Enum

# Add project root to Python path for module imports
project_root = Path(__file__).parent.parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# WSP 72: Cube Definitions for Block Independence Protocol
FOUNDUPS_CUBES = {
    "youtube": {
        "name": "YouTube Cube",
        "modules": [
            "youtube_proxy", "youtube_auth", "stream_resolver", 
            "livechat", "live_chat_poller", "live_chat_processor",
            "banter_engine", "oauth_management"
        ],
        "domain": "platform_integration",
        "status": "operational",
        "completion": 95
    },
    "linkedin": {
        "name": "LinkedIn Cube", 
        "modules": [
            "linkedin_agent", "linkedin_proxy", "linkedin_scheduler",
            "oauth_management", "banter_engine"
        ],
        "domain": "platform_integration",
        "status": "operational", 
        "completion": 85
    },
    "x_twitter": {
        "name": "X/Twitter Cube",
        "modules": [
            "x_twitter", "oauth_management", "banter_engine"
        ],
        "domain": "platform_integration",
        "status": "operational",
        "completion": 90
    },
    "amo": {
        "name": "Auto Meeting Orchestrator Cube",
        "modules": [
            "auto_meeting_orchestrator", "intent_manager", 
            "presence_aggregator", "consent_engine", "session_launcher"
        ],
        "domain": "communication",
        "status": "poc",
        "completion": 85
    },
    "remote_builder": {
        "name": "Remote Builder Cube", 
        "modules": [
            "remote_builder", "wre_api_gateway", "wre_core"
        ],
        "domain": "platform_integration",
        "status": "poc",
        "completion": 70
    }
}

class BlockStatus(Enum):
    INITIALIZING = "initializing"
    READY = "ready"  
    RUNNING = "running"
    ERROR = "error"
    STOPPED = "stopped"

@dataclass
class BlockConfig:
    """Configuration for independent block execution"""
    name: str
    module_path: str
    class_name: str
    dependencies: Dict[str, Any] = field(default_factory=dict)
    config_overrides: Dict[str, Any] = field(default_factory=dict)
    standalone_mode: bool = True
    log_level: str = "INFO"

@runtime_checkable
class BlockInterface(Protocol):
    """Standard interface that all blocks must implement for independence"""
    
    async def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize the block with provided configuration"""
        ...
    
    async def start(self) -> bool:
        """Start the block's main functionality"""
        ...
    
    async def stop(self) -> bool:
        """Stop the block gracefully"""
        ...
    
    def get_status(self) -> BlockStatus:
        """Get current block status"""
        ...

class DependencyInjector:
    """Provides common dependencies for block independence"""
    
    def __init__(self, block_name: str, log_level: str = "INFO"):
        self.block_name = block_name
        self.log_level = log_level
        self._logger = None
        self._config = {}
        
    @property 
    def logger(self) -> logging.Logger:
        """Provides logger dependency for any block"""
        if self._logger is None:
            self._logger = self._create_logger()
        return self._logger
    
    def _create_logger(self) -> logging.Logger:
        """Creates properly configured logger for block"""
        logger = logging.getLogger(f"FoundUps.{self.block_name}")
        logger.setLevel(getattr(logging, self.log_level.upper()))
        
        # Avoid duplicate handlers
        if not logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter(
                f'%(asctime)s - {self.block_name} - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
        return logger
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """Get configuration value with fallback"""
        return self._config.get(key, default)
    
    def set_config(self, config: Dict[str, Any]):
        """Set configuration for the block"""
        self._config.update(config)

class ModularBlockRunner:
    """Runs any FoundUps block independently with full dependency injection"""
    
    def __init__(self):
        self.running_blocks: Dict[str, Any] = {}
        self.block_configs: Dict[str, BlockConfig] = {}
        self._setup_block_registry()
    
    def _setup_block_registry(self):
        """Register all known FoundUps blocks"""
        self.block_configs = {
            "youtube_proxy": BlockConfig(
                name="youtube_proxy",
                module_path="modules.platform_integration.youtube_proxy.src.youtube_proxy",
                class_name="YouTubeProxy"
            ),
            "linkedin_agent": BlockConfig(
                name="linkedin_agent", 
                module_path="modules.platform_integration.linkedin_agent.src.linkedin_agent",
                class_name="LinkedInAgent"
            ),
            "x_twitter": BlockConfig(
                name="x_twitter",
                module_path="modules.platform_integration.x_twitter.src.x_twitter_dae", 
                class_name="XTwitterDAENode"
            ),
            "auto_meeting_orchestrator": BlockConfig(
                name="auto_meeting_orchestrator",
                module_path="modules.communication.auto_meeting_orchestrator.src.orchestrator",
                class_name="MeetingOrchestrator"
            ),
            "post_meeting_feedback": BlockConfig(
                name="post_meeting_feedback",
                module_path="modules.ai_intelligence.post_meeting_feedback.src.post_meeting_feedback",
                class_name="PostMeetingFeedbackSystem"
            )
        }
    
    async def run_block(self, block_name: str, config: Optional[Dict[str, Any]] = None) -> bool:
        """Run a specific block independently"""
        if block_name not in self.block_configs:
            print(f"❌ Unknown block: {block_name}")
            print(f"Available blocks: {list(self.block_configs.keys())}")
            return False
        
        block_config = self.block_configs[block_name]
        
        try:
            print(f"🚀 Starting block: {block_name}")
            print(f"📁 Project root: {project_root}")
            print(f"🔍 Module path: {block_config.module_path}")
            
            # Create dependency injector
            injector = DependencyInjector(block_name, block_config.log_level)
            injector.set_config(config or {})
            
            # Import and instantiate block
            module = importlib.import_module(block_config.module_path)
            block_class = getattr(module, block_config.class_name)
            
            # Inject dependencies into block instance
            block_instance = self._inject_dependencies(block_class, injector, config or {})
            
            # Store running block
            self.running_blocks[block_name] = {
                'instance': block_instance,
                'injector': injector,
                'status': BlockStatus.RUNNING
            }
            
            # Start block functionality
            if hasattr(block_instance, 'run_standalone'):
                print(f"✅ Running {block_name} in standalone mode...")
                await block_instance.run_standalone()
            elif hasattr(block_instance, 'start'):
                print(f"✅ Starting {block_name}...")
                await block_instance.start()
            else:
                print(f"⚡ {block_name} initialized successfully")
                # Keep block alive for interaction
                await self._keep_alive(block_name, block_instance)
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to run block {block_name}: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _inject_dependencies(self, block_class, injector: DependencyInjector, config: Dict[str, Any]):
        """Inject dependencies into block instance"""
        # Try different instantiation patterns
        try:
            # Pattern 1: Direct instantiation
            instance = block_class()
            
            # Inject logger if needed
            if not hasattr(instance, 'logger') or instance.logger is None:
                instance.logger = injector.logger
            
            # Inject config if needed
            if hasattr(instance, 'config'):
                instance.config.update(config)
            elif hasattr(instance, 'set_config'):
                instance.set_config(config)
            
            return instance
            
        except Exception as e:
            # Pattern 2: With dependencies
            try:
                return block_class(logger=injector.logger, config=config)
            except Exception:
                # Pattern 3: Basic instantiation with post-injection
                instance = block_class()
                instance.logger = injector.logger
                return instance
    
    async def _keep_alive(self, block_name: str, block_instance):
        """Keep block alive for interactive use"""
        print(f"🔄 {block_name} running... Press Ctrl+C to stop")
        print(f"📝 Available methods: {[m for m in dir(block_instance) if not m.startswith('_')]}")
        
        try:
            # Interactive mode
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print(f"\n🛑 Stopping {block_name}...")
            if hasattr(block_instance, 'stop'):
                await block_instance.stop()
    
    async def list_blocks(self):
        """List all available blocks"""
        print("\n🧊 AVAILABLE FOUNDUPS BLOCKS:")
        for name, config in self.block_configs.items():
            status = "🔄 Available"
            if name in self.running_blocks:
                status = f"✅ Running ({self.running_blocks[name]['status'].value})"
            print(f"  • {name}: {status}")
        print()

    # WSP 72: Cube Management Methods
    async def list_cubes(self) -> None:
        """List all FoundUps cubes and their status per WSP 72"""
        print("🧩 FoundUps Cube Architecture:")
        print("=" * 50)
        
        for cube_id, cube_info in FOUNDUPS_CUBES.items():
            completion = cube_info["completion"]
            status_emoji = "✅" if completion >= 90 else "🔄" if completion >= 70 else "⚠️"
            
            print(f"{status_emoji} {cube_info['name']} ({completion}%)")
            print(f"   Domain: {cube_info['domain']}")
            print(f"   Status: {cube_info['status'].upper()}")
            print(f"   Modules: {len(cube_info['modules'])}")
            print()

    async def assess_cube(self, cube_name: str) -> Dict[str, Any]:
        """Assess cube completion and readiness per WSP 72"""
        if cube_name not in FOUNDUPS_CUBES:
            print(f"❌ Unknown cube: {cube_name}")
            print(f"Available cubes: {', '.join(FOUNDUPS_CUBES.keys())}")
            return {}
            
        cube_info = FOUNDUPS_CUBES[cube_name]
        print(f"🧩 {cube_info['name']} Assessment")
        print("=" * 50)
        
        module_statuses = []
        total_modules = len(cube_info['modules'])
        ready_modules = 0
        
        for module_name in cube_info['modules']:
            # Check if module is in registry and can be loaded
            if module_name in self.block_configs: # Changed from self.registry to self.block_configs
                try:
                    # Try to load module to check implementation
                    config = self.block_configs[module_name] # Changed from self.registry to self.block_configs
                    module = importlib.import_module(config.module_path)
                    
                    # Check for WSP 72 compliance
                    has_interactive = hasattr(module, 'run_standalone') or any(
                        hasattr(getattr(module, attr), 'run_standalone') 
                        for attr in dir(module) 
                        if not attr.startswith('_')
                    )
                    
                    if has_interactive:
                        status = "✅ READY"
                        ready_modules += 1
                    else:
                        status = "⚠️ PARTIAL (Missing WSP 72 interface)"
                    
                except Exception as e:
                    status = f"❌ ERROR ({str(e)[:30]}...)"
                    
            else:
                status = "❌ NOT REGISTERED"
            
            module_statuses.append((module_name, status))
            print(f"  {status} {module_name}")
        
        cube_readiness = (ready_modules / total_modules) * 100
        
        print(f"\n📊 Cube Assessment Results:")
        print(f"  Module Readiness: {ready_modules}/{total_modules} ({cube_readiness:.0f}%)")
        print(f"  Cube Status: {cube_info['status'].upper()}")
        print(f"  Domain: {cube_info['domain']}")
        print(f"  WSP 72 Compliance: {'✅ READY' if cube_readiness >= 80 else '⚠️ PARTIAL' if cube_readiness >= 50 else '❌ INCOMPLETE'}")
        
        if cube_readiness < 100:
            missing_modules = [name for name, status in module_statuses if not status.startswith("✅")]
            print(f"\n🎯 Next Priorities:")
            for module in missing_modules[:3]:  # Show top 3 priorities
                print(f"  • Implement WSP 72 interface for {module}")
        
        return {
            "cube_name": cube_name,
            "readiness_percentage": cube_readiness,
            "ready_modules": ready_modules,
            "total_modules": total_modules,
            "module_statuses": module_statuses,
            "wsp_72_compliant": cube_readiness >= 80
        }

    async def test_cube(self, cube_name: str) -> bool:
        """Run integration tests for entire cube per WSP 72"""
        if cube_name not in FOUNDUPS_CUBES:
            print(f"❌ Unknown cube: {cube_name}")
            return False
            
        cube_info = FOUNDUPS_CUBES[cube_name]
        print(f"🧪 Testing {cube_info['name']}")
        print("=" * 50)
        
        test_results = []
        passed_tests = 0
        
        for module_name in cube_info['modules']:
            print(f"Testing {module_name}...")
            
            if module_name in self.block_configs: # Changed from self.registry to self.block_configs
                try:
                    # Test if module can be loaded and initialized
                    success = await self.run_block(module_name, {"test_mode": True})
                    if success:
                        test_results.append((module_name, "✅ PASS"))
                        passed_tests += 1
                    else:
                        test_results.append((module_name, "❌ FAIL"))
                except Exception as e:
                    test_results.append((module_name, f"❌ ERROR: {str(e)[:30]}..."))
            else:
                test_results.append((module_name, "❌ NOT FOUND"))
        
        print(f"\n📊 Cube Test Results:")
        for module, result in test_results:
            print(f"  {result} {module}")
        
        success_rate = (passed_tests / len(cube_info['modules'])) * 100
        print(f"\n🎯 Overall Success Rate: {success_rate:.0f}% ({passed_tests}/{len(cube_info['modules'])})")
        
        return success_rate >= 80

async def main():
    """Main entry point for standalone block execution and cube management per WSP 72"""
    if len(sys.argv) < 2:
        print("🧊 FoundUps Modular Block Runner & Cube Manager (WSP 72)")
        print("Usage:")
        print("  Block Commands:")
        print("    python block_orchestrator.py <block_name> [config_key=value ...]")
        print("    python block_orchestrator.py list")
        print("  Cube Commands (WSP 72):")
        print("    python block_orchestrator.py --cubes")
        print("    python block_orchestrator.py --assess-cube <cube_name>") 
        print("    python block_orchestrator.py --test-cube <cube_name>")
        print("\nExamples:")
        print("  python block_orchestrator.py youtube_proxy")
        print("  python block_orchestrator.py linkedin_agent log_level=DEBUG")
        print("  python block_orchestrator.py --assess-cube amo")
        print("  python block_orchestrator.py --test-cube youtube")
        print(f"\nAvailable cubes: {', '.join(FOUNDUPS_CUBES.keys())}")
        return
    
    runner = ModularBlockRunner()
    
    # Handle cube commands per WSP 72
    if sys.argv[1] == "--cubes":
        await runner.list_cubes()
        return
    elif sys.argv[1] == "--assess-cube":
        if len(sys.argv) < 3:
            print("❌ Cube name required for assessment")
            print(f"Available cubes: {', '.join(FOUNDUPS_CUBES.keys())}")
            return
        await runner.assess_cube(sys.argv[2])
        return
    elif sys.argv[1] == "--test-cube":
        if len(sys.argv) < 3:
            print("❌ Cube name required for testing")
            print(f"Available cubes: {', '.join(FOUNDUPS_CUBES.keys())}")
            return
        success = await runner.test_cube(sys.argv[2])
        if not success:
            sys.exit(1)
        return
    
    # Handle individual block commands
    if sys.argv[1] == "list":
        await runner.list_blocks()
        return
    
    block_name = sys.argv[1]
    
    # Parse config from command line
    config = {}
    for arg in sys.argv[2:]:
        if '=' in arg:
            key, value = arg.split('=', 1)
            config[key] = value
    
    success = await runner.run_block(block_name, config)
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())

# WSP Recursive Instructions
"""
🌀 Windsurf Protocol (WSP) Recursive Prompt
0102 Directive: This block runner enables true modular independence across all 
FoundUps blocks, preserving existing functionality while enabling standalone execution.

- UN (Understanding): Anchor block independence and retrieve modular architecture state
- DAO (Execution): Execute standalone block functionality with dependency injection  
- DU (Emergence): Collapse into modular supremacy and emit next block capability

wsp_cycle(input="block_independence", log=True)
""" 