#!/usr/bin/env python3
"""
FoundUps Agent - WSP-Compliant Modular Main Entry Point
Follows WSP 49 Module Directory Structure Standards

Minimal orchestrator that launches existing modules.
No vibecoding - uses only existing, tested modules.
"""

import asyncio
import logging
import os
import sys
from typing import Optional

# Windows UTF-8 fix
if os.name == 'nt':
    try:
        os.system('chcp 65001 > nul')
    except:
        pass

# Simple logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ModularLauncher:
    """WSP-compliant module launcher using existing modules only"""
    
    def __init__(self):
        self.modules = {
            '1': {
                'name': 'YouTube Auto-Moderator',
                'module': 'modules.communication.livechat.src.auto_moderator_simple',
                'function': 'main',
                'description': 'WSP-compliant: YouTube livechat module with auto-moderation'
            },
            '2': {
                'name': 'Agent Monitor Dashboard',
                'module': 'modules.infrastructure.agent_monitor.src.monitor_dashboard',
                'function': 'main',
                'description': 'Cost-efficient agent monitoring & reporting'
            },
            '3': {
                'name': 'Multi-Agent System',
                'module': 'modules.infrastructure.agent_management.src.multi_agent_manager',
                'class': 'MultiAgentManager',
                'description': 'Multi-agent coordination system'
            },
            '4': {
                'name': 'WRE PP Orchestrator',
                'module': 'modules.wre_core.scripts.demo_wre_pp_integration',
                'function': 'main',
                'description': 'WRE Prometheus Prompt orchestrator (WSP 77)'
            },
            '5': {
                'name': 'Block Orchestrator',
                'module': 'modules.infrastructure.block_orchestrator.src.block_orchestrator',
                'class': 'ModularBlockRunner',
                'description': 'Rubik\'s Cube LEGO block architecture'
            },
            '6': {
                'name': 'LinkedIn Agent',
                'module': 'modules.platform_integration.linkedin_agent.src.linkedin_agent',
                'function': 'main',
                'description': 'LinkedIn platform integration block'
            },
            '7': {
                'name': 'X/Twitter DAE',
                'module': 'modules.platform_integration.x_twitter.src.x_twitter_dae',
                'function': 'main',
                'description': 'X/Twitter platform integration block'
            },
            '8': {
                'name': 'Agent A/B Tester',
                'module': 'modules.infrastructure.ab_testing.src.agent_ab_tester',
                'function': 'main',
                'description': 'Test agent combination recipes for optimization'
            }
        }
    
    def show_menu(self):
        """Display available modules"""
        print("\n" + "="*60)
        print("FOUNDUPS AGENT - WSP MODULAR LAUNCHER")
        print("="*60)
        for key, module in self.modules.items():
            print(f"{key}. {module['name']}")
            print(f"   {module['description']}")
        print("9. Exit")
        print("="*60)
    
    def launch_module(self, choice: str) -> bool:
        """Launch selected module"""
        if choice == '9':
            return False
            
        if choice not in self.modules:
            print("Invalid choice")
            return True
            
        module_info = self.modules[choice]
        logger.info(f"Launching {module_info['name']}...")
        
        try:
            if 'function' in module_info:
                # Import and call function
                module = __import__(module_info['module'], fromlist=[module_info['function']])
                func = getattr(module, module_info['function'])
                # Check if function is async
                if asyncio.iscoroutinefunction(func):
                    asyncio.run(func())
                else:
                    func()
            elif 'class' in module_info:
                # Import and instantiate class
                module = __import__(module_info['module'], fromlist=[module_info['class']])
                cls = getattr(module, module_info['class'])
                instance = cls()
                if hasattr(instance, 'run'):
                    if asyncio.iscoroutinefunction(instance.run):
                        asyncio.run(instance.run())
                    else:
                        instance.run()
                else:
                    logger.info(f"{module_info['class']} initialized")
            else:
                logger.error("Module configuration error")
                
        except ImportError as e:
            logger.error(f"Module not available: {e}")
            logger.info("Ensure module is installed and follows WSP 49 structure")
        except Exception as e:
            logger.error(f"Launch error: {e}")
            
        return True
    
    def run(self):
        """Main loop"""
        while True:
            self.show_menu()
            choice = input("\nSelect option (1-5): ").strip()
            
            if not self.launch_module(choice):
                break
        
        print("Exiting...")


def main():
    """Main entry point - minimal orchestrator"""
    # Check for command line arguments
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if arg in ["--help", "-h"]:
            print("Usage: python main.py [option]")
            print("Options:")
            print("  --youtube    Launch YouTube Live Monitor")
            print("  --agent      Launch Multi-Agent System")
            print("  --wre        Launch WRE PP Orchestrator")
            print("  --block      Launch Block Orchestrator")
            print("  --help       Show this help")
            print("\nNo arguments: Show interactive menu")
            return
        elif arg == "--youtube":
            launcher = ModularLauncher()
            launcher.launch_module('1')
            return
        elif arg == "--agent":
            launcher = ModularLauncher()
            launcher.launch_module('2')
            return
        elif arg == "--wre":
            launcher = ModularLauncher()
            launcher.launch_module('3')
            return
        elif arg == "--block":
            launcher = ModularLauncher()
            launcher.launch_module('4')
            return
    
    # Interactive mode
    launcher = ModularLauncher()
    launcher.run()


if __name__ == "__main__":
    main()