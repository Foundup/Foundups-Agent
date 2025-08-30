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
import subprocess
from typing import Optional, Dict, List
from datetime import datetime

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
            '0': {
                'name': 'Git Push & Post',
                'module': 'main',
                'function': 'git_push_and_post',
                'description': 'Push to Git and post development updates to LinkedIn'
            },
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
            choice = input("\nSelect option (0=Git Push, 1=YouTube, 4=AMO | others pending | 9=exit): ").strip()
            
            if not self.launch_block(choice):
                break
        
        print("Exiting...")


def generate_smart_commit_message(files):
    """
    Generate intelligent commit message based on changed files.
    Analyzes file patterns to create meaningful messages.
    """
    # Parse file status
    modified_files = []
    new_files = []
    deleted_files = []
    
    for file_line in files:
        if not file_line.strip():
            continue
        
        # Git status format: XY filename
        if len(file_line) >= 3:
            status = file_line[:2]
            filename = file_line[3:].strip()
            
            if 'M' in status:
                modified_files.append(filename)
            elif 'A' in status or '?' in status:
                new_files.append(filename)
            elif 'D' in status:
                deleted_files.append(filename)
    
    # Analyze patterns in changed files
    modules_changed = set()
    features = []
    
    for f in modified_files + new_files:
        # Check for module changes
        if 'modules/' in f:
            parts = f.split('/')
            if len(parts) >= 3:
                module_type = parts[1]  # e.g., 'platform_integration'
                module_name = parts[2]  # e.g., 'social_media_orchestrator'
                modules_changed.add(f"{module_type}/{module_name}")
        
        # Detect specific features
        if 'social_media' in f.lower() or 'orchestrator' in f.lower():
            features.append("social media")
        elif 'linkedin' in f.lower():
            features.append("LinkedIn")
        elif 'x_twitter' in f.lower() or 'twitter' in f.lower():
            features.append("X/Twitter")
        elif 'git' in f.lower() and 'push' in f.lower():
            features.append("Git integration")
        elif 'multi_account' in f.lower():
            features.append("multi-account")
        elif 'main.py' in f:
            features.append("main menu")
        elif 'test' in f.lower():
            features.append("tests")
        elif 'architecture' in f.lower():
            features.append("architecture")
        elif 'config' in f.lower():
            features.append("configuration")
    
    # Generate message based on analysis
    if features:
        unique_features = list(set(features))[:3]  # Top 3 features
        
        # Determine action verb
        if new_files and not modified_files:
            action = "Add"
        elif modified_files and not new_files:
            action = "Update"
        elif deleted_files and not (new_files or modified_files):
            action = "Remove"
        else:
            action = "Implement"
        
        # Build message
        feature_str = ", ".join(unique_features)
        
        # Add WSP reference if detected
        wsp_modules = ["orchestrator", "multi_account", "dae", "architecture"]
        has_wsp = any(w in str(files).lower() for w in wsp_modules)
        
        if has_wsp:
            message = f"{action} {feature_str} (WSP-compliant)"
        else:
            message = f"{action} {feature_str}"
        
        # Add module context if significant
        if len(modules_changed) == 1:
            module = list(modules_changed)[0]
            message += f" in {module}"
        elif len(modules_changed) > 1:
            message += f" across {len(modules_changed)} modules"
    
    else:
        # Fallback to generic but informative message
        total_changes = len(modified_files) + len(new_files) + len(deleted_files)
        
        if len(modules_changed) > 0:
            module_str = ", ".join(list(modules_changed)[:2])
            message = f"Update {module_str} ({total_changes} files)"
        else:
            message = f"Update codebase ({total_changes} files)"
    
    return message


def git_push_and_post():
    """
    Git push with automatic social media posting.
    Pushes code changes and posts updates to LinkedIn development page.
    """
    print("\n" + "="*60)
    print("GIT PUSH & SOCIAL MEDIA UPDATE")
    print("="*60)
    
    # Check git status first
    try:
        status = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True, check=True)
        
        if not status.stdout.strip():
            print("No changes to commit")
            input("\nPress Enter to continue...")
            return
        
        print("\nChanges to be committed:")
        print("-" * 40)
        # Show files that will be committed
        files = status.stdout.strip().split('\n')
        for file in files[:10]:  # Show first 10 files
            print(f"  {file}")
        if len(files) > 10:
            print(f"  ... and {len(files) - 10} more files")
        print("-" * 40)
        
        # Auto-generate commit message based on changed files
        print("\nGenerating commit message...")
        
        # Analyze changes to create meaningful commit message
        commit_message = generate_smart_commit_message(files)
        
        print(f"Commit message: {commit_message}")
        print("\nProceed? (y/n/edit): ", end="")
        response = input().strip().lower()
        
        if response == 'n':
            print("Cancelled")
            return
        elif response == 'edit':
            print("Enter new commit message:")
            custom_message = input("> ").strip()
            if custom_message:
                commit_message = custom_message
            else:
                print("Using auto-generated message")
        
        # Execute git commands
        print("\n[1/4] Adding files...")
        subprocess.run(['git', 'add', '.'], check=True)
        
        print("[2/4] Committing...")
        subprocess.run(['git', 'commit', '-m', commit_message], check=True)
        
        print("[3/4] Pushing to remote...")
        result = subprocess.run(['git', 'push'], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("[OK] Successfully pushed to Git!")
            
            # Trigger social media posting
            print("\n[4/4] Posting to social media...")
            try:
                # Import the multi-account manager
                from modules.platform_integration.social_media_orchestrator.src.multi_account_manager import SocialMediaEventRouter
                
                # Get recent commits for the post
                commits_result = subprocess.run(
                    ['git', 'log', '-3', '--pretty=format:%s'],
                    capture_output=True, text=True, check=True
                )
                
                commit_subjects = commits_result.stdout.strip().split('\n')
                commits_data = [{'subject': subject} for subject in commit_subjects if subject]
                
                # Extract WSP references if any
                import re
                wsp_refs = []
                for commit in commits_data:
                    matches = re.findall(r'WSP[\s-]?(\d{1,2})', commit['subject'], re.IGNORECASE)
                    wsp_refs.extend([f"WSP {m}" for m in matches])
                
                # Create event for social media posting
                event_data = {
                    'commits': commits_data,
                    'repository': 'Foundups-Agent',
                    'wsp_refs': list(set(wsp_refs)),  # Unique WSP refs
                    'timestamp': datetime.now().isoformat()
                }
                
                # Initialize router and post
                router = SocialMediaEventRouter()
                results = asyncio.run(router.handle_event('git_push', event_data))
                
                # Show results
                print("\nSocial Media Posting Results:")
                for account, result in results.items():
                    if isinstance(result, dict) and result.get('success'):
                        print(f"  [OK] {account}")
                    else:
                        print(f"  [FAIL] {account}: {result.get('error', 'Unknown error')}")
                
            except ImportError:
                print("[WARNING] Social media orchestrator not available")
                print("Git push successful but social media posting skipped")
            except Exception as e:
                print(f"[WARNING] Social media posting failed: {e}")
                print("Git push was successful")
        else:
            print(f"[ERROR] Git push failed: {result.stderr}")
            
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Git operation failed: {e}")
    except FileNotFoundError:
        print("[ERROR] Git not found. Please install Git.")
    
    input("\nPress Enter to continue...")


def main():
    """Main entry point - minimal block orchestrator"""
    # Check for command line arguments
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if arg in ["--help", "-h"]:
            print("Usage: python main.py [option]")
            print("Options:")
            print("  --git        Git push with social media posting")
            print("  --youtube    Launch YouTube DAE")
            print("  --linkedin   Launch LinkedIn DAE")
            print("  --x          Launch X DAE")
            print("  --amo        Launch AMO DAE")
            print("  --remote     Launch Remote DAE")
            print("  --help       Show this help")
            print("\nNo arguments: Show interactive menu")
            return
        elif arg == "--git":
            git_push_and_post()
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