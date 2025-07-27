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

async def main():
    """Main entry point for standalone block execution"""
    if len(sys.argv) < 2:
        print("🧊 FoundUps Modular Block Runner")
        print("Usage: python block_runner.py <block_name> [config_key=value ...]")
        print("\nExamples:")
        print("  python block_runner.py youtube_proxy")
        print("  python block_runner.py linkedin_agent log_level=DEBUG")
        print("  python block_runner.py list  # Show available blocks")
        return
    
    runner = ModularBlockRunner()
    
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