#!/usr/bin/env python3
"""
FoundUps Agent - WSP-Compliant Block-Based Main Entry Point
Follows WSP 80 Cube-Level DAE Architecture

Minimal orchestrator that launches existing blocks.
No vibecoding - uses only existing, tested blocks.
Each block is composed of multiple modules per WSP 80.
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


class BlockLauncher:
    """WSP-compliant block launcher using existing blocks only"""
    
    def __init__(self):
        self.blocks = {
            '1': {
                'name': 'YouTube DAE',
                'module': 'modules.communication.livechat.src.auto_moderator_dae',
                'function': 'main',
                'description': '0102 consciousness monitoring YouTube Live Chat (WSP-Compliant)'
            },
            '2': {
                'name': 'LinkedIn DAE [PENDING]',
                'module': 'modules.platform_integration.linkedin_agent.src.linkedin_agent',
                'function': 'main',
                'description': '0102 consciousness for LinkedIn engagement'
            },
            '3': {
                'name': 'X DAE [PENDING]',
                'module': 'modules.platform_integration.x_twitter.src.x_twitter_dae',
                'function': 'main',
                'description': '0102 consciousness for X/Twitter platform'
            },
            '4': {
                'name': 'AMO DAE',
                'module': 'modules.infrastructure.wre_core.run_wre',
                'function': 'main',
                'description': 'Autonomous Management Orchestrator DAE'
            },
            '5': {
                'name': 'Remote DAE [PENDING]',
                'module': 'modules.infrastructure.remote_dae.src.remote_dae',
                'function': 'main',
                'description': 'Remote control and monitoring DAE'
            },
        }
    
    def show_menu(self):
        """Display available blocks"""
        print("\n" + "="*60)
        print("FOUNDUPS AGENT - DAE CUBE LAUNCHER")
        print("="*60)
        for key, block in self.blocks.items():
            print(f"{key}. {block['name']}")
            print(f"   {block['description']}")
        print("9. Exit")
        print("="*60)
    
    def launch_block(self, choice: str) -> bool:
        """Launch selected block"""
        if choice == '9':
            return False
            
        if choice not in self.blocks:
            print("Invalid choice")
            return True
            
        block_info = self.blocks[choice]
        logger.info(f"Launching {block_info['name']}...")
        
        try:
            if 'function' in block_info:
                # Import and call function
                module = __import__(block_info['module'], fromlist=[block_info['function']])
                func = getattr(module, block_info['function'])
                # Check if function is async
                if asyncio.iscoroutinefunction(func):
                    asyncio.run(func())
                else:
                    func()
            elif 'class' in block_info:
                # Import and instantiate class
                module = __import__(block_info['module'], fromlist=[block_info['class']])
                cls = getattr(module, block_info['class'])
                instance = cls()
                if hasattr(instance, 'run'):
                    if asyncio.iscoroutinefunction(instance.run):
                        asyncio.run(instance.run())
                    else:
                        instance.run()
                else:
                    logger.info(f"{block_info['class']} initialized")
            else:
                logger.error("Block configuration error")
                
        except ImportError as e:
            logger.error(f"Block not available: {e}")
            logger.info("Ensure block is installed and follows WSP 80 architecture")
        except Exception as e:
            logger.error(f"Launch error: {e}")
            
        return True
    
    def run(self):
        """Main loop"""
        while True:
            self.show_menu()
            choice = input("\nSelect DAE (1=YouTube, 4=AMO work | others pending | 9 to exit): ").strip()
            
            if not self.launch_block(choice):
                break
        
        print("Exiting...")


def main():
    """Main entry point - minimal block orchestrator"""
    # Check for command line arguments
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if arg in ["--help", "-h"]:
            print("Usage: python main.py [option]")
            print("Options:")
            print("  --youtube    Launch YouTube DAE")
            print("  --linkedin   Launch LinkedIn DAE")
            print("  --x          Launch X DAE")
            print("  --amo        Launch AMO DAE")
            print("  --remote     Launch Remote DAE")
            print("  --help       Show this help")
            print("\nNo arguments: Show interactive menu")
            return
        elif arg == "--youtube":
            launcher = BlockLauncher()
            launcher.launch_block('1')
            return
        elif arg == "--linkedin":
            launcher = BlockLauncher()
            launcher.launch_block('2')
            return
        elif arg == "--x":
            launcher = BlockLauncher()
            launcher.launch_block('3')
            return
        elif arg == "--amo":
            launcher = BlockLauncher()
            launcher.launch_block('4')
            return
        elif arg == "--remote":
            launcher = BlockLauncher()
            launcher.launch_block('5')
            return
    
    # Interactive mode
    launcher = BlockLauncher()
    launcher.run()


if __name__ == "__main__":
    main()