#!/usr/bin/env python3
"""
Script to fix import paths after Enterprise Domain migration
"""

import os
import re
from pathlib import Path

# Define the import mappings
IMPORT_MAPPINGS = {
    # Old pattern -> New pattern
    r'from modules\.banter_engine\.emoji_sequence_map import': 'from modules.ai_intelligence.banter_engine.banter_engine.src.emoji_sequence_map import',
    r'from modules\.banter_engine import': 'from modules.ai_intelligence.banter_engine.banter_engine import',
    r'from modules\.livechat\.src\.livechat import': 'from modules.communication.livechat.livechat.src.livechat import',
    r'from modules\.livechat import': 'from modules.communication.livechat.livechat import',
    r'from modules\.live_chat_poller\.src\.live_chat_poller import': 'from modules.communication.livechat.live_chat_poller.src.live_chat_poller import',
    r'from modules\.live_chat_poller import': 'from modules.communication.livechat.live_chat_poller import',
    r'from modules\.live_chat_processor\.src\.live_chat_processor import': 'from modules.communication.livechat.live_chat_processor.src.live_chat_processor import',
    r'from modules\.live_chat_processor import': 'from modules.communication.livechat.live_chat_processor import',
    r'from modules\.youtube_auth\.src\.youtube_auth import': 'from modules.platform_integration.youtube_auth.youtube_auth.src.youtube_auth import',
    r'from modules\.youtube_auth import': 'from modules.platform_integration.youtube_auth.youtube_auth import',
    r'from modules\.stream_resolver\.src\.stream_resolver import': 'from modules.platform_integration.stream_resolver.stream_resolver.src.stream_resolver import',
    r'from modules\.stream_resolver import': 'from modules.platform_integration.stream_resolver.stream_resolver import',
    r'from modules\.token_manager\.src\.token_manager import': 'from modules.infrastructure.token_manager.token_manager.src.token_manager import',
    r'from modules\.token_manager import': 'from modules.infrastructure.token_manager.token_manager import',
}

def fix_imports_in_file(file_path):
    """Fix import statements in a single file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        changes_made = []
        
        for old_pattern, new_import in IMPORT_MAPPINGS.items():
            if re.search(old_pattern, content):
                content = re.sub(old_pattern, new_import, content)
                changes_made.append(f"  {old_pattern} -> {new_import}")
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Fixed {file_path}")
            for change in changes_made:
                print(change)
            return True
        else:
            return False
            
    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")
        return False

def main():
    """Main function to fix all import paths"""
    print("🔧 Fixing import paths for Enterprise Domain structure...")
    
    # Find all Python files in the modules directory
    modules_dir = Path("modules")
    python_files = list(modules_dir.rglob("*.py"))
    
    # Also check main.py and other root files
    root_files = ["main.py"]
    for root_file in root_files:
        if Path(root_file).exists():
            python_files.append(Path(root_file))
    
    fixed_count = 0
    total_count = len(python_files)
    
    for file_path in python_files:
        if fix_imports_in_file(file_path):
            fixed_count += 1
    
    print(f"\n📊 Summary:")
    print(f"  Total files checked: {total_count}")
    print(f"  Files fixed: {fixed_count}")
    print(f"  Files unchanged: {total_count - fixed_count}")
    
    if fixed_count > 0:
        print(f"\n✨ Import path fixes complete!")
    else:
        print(f"\n✅ No import fixes needed!")

if __name__ == "__main__":
    main() 