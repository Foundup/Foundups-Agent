#!/usr/bin/env python3
"""
Enterprise Domain Import Path Migration Tool
WSP 3 Compliance: Tool for migrating import paths to Enterprise Domain structure

This tool assists with migrating flat module imports to the hierarchical
Enterprise Domain structure defined in WSP 3.
"""

import os
import re
import sys
from pathlib import Path

# Add project root to path for WSP compliance
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Define the import mappings for Enterprise Domain migration
ENTERPRISE_DOMAIN_MAPPINGS = {
    # AI Intelligence Domain
    r'from modules\.banter_engine\.emoji_sequence_map import': 'from modules.ai_intelligence.banter_engine.emoji_sequence_map import',
    r'from modules\.banter_engine import': 'from modules.ai_intelligence.banter_engine import',
    r'from modules\.banter_engine\.src\.banter_engine import': 'from modules.ai_intelligence.banter_engine.banter_engine.src.banter_engine import',
    
    # Communication Domain
    r'from modules\.livechat\.src\.livechat import': 'from modules.communication.livechat.src.livechat import',
    r'from modules\.livechat import': 'from modules.communication.livechat.livechat import',
    r'from modules\.live_chat_poller\.src\.live_chat_poller import': 'from modules.communication.livechat.live_chat_poller.src.live_chat_poller import',
    r'from modules\.live_chat_poller import': 'from modules.communication.livechat.live_chat_poller import',
    r'from modules\.live_chat_processor\.src\.live_chat_processor import': 'from modules.communication.livechat.live_chat_processor.src.live_chat_processor import',
    r'from modules\.live_chat_processor import': 'from modules.communication.livechat.live_chat_processor import',
    
    # Platform Integration Domain
    r'from modules\.youtube_auth\.src\.youtube_auth import': 'from modules.platform_integration.authentication.youtube_auth.src.youtube_auth import',
    r'from modules\.youtube_auth import': 'from modules.platform_integration.authentication.youtube_auth import',
    r'from modules\.stream_resolver\.src\.stream_resolver import': 'from modules.platform_integration.stream_resolver.src.stream_resolver import',
    r'from modules\.stream_resolver import': 'from modules.platform_integration.stream_resolver.stream_resolver import',
    
    # Infrastructure Domain
    r'from modules\.token_manager\.src\.token_manager import': 'from modules.infrastructure.token_manager.src.token_manager import',
    r'from modules\.token_manager import': 'from modules.infrastructure.token_manager.token_manager import',
    r'from modules\.agent_management\.src\.multi_agent_manager import': 'from modules.infrastructure.agent_management.src.multi_agent_manager import',
    r'from modules\.oauth_management\.src\.oauth_manager import': 'from modules.infrastructure.oauth_management.src.oauth_manager import',
}

def fix_imports_in_file(file_path: Path) -> bool:
    """
    Fix import statements in a single file to comply with Enterprise Domain structure.
    
    Args:
        file_path: Path to the file to process
        
    Returns:
        True if changes were made, False otherwise
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        changes_made = []
        
        for old_pattern, new_import in ENTERPRISE_DOMAIN_MAPPINGS.items():
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

def scan_for_violations() -> list:
    """
    Scan for files that may need Enterprise Domain import fixes.
    
    Returns:
        List of files that need attention
    """
    violations = []
    
    # Check for flat imports that violate WSP 3
    modules_dir = Path("modules")
    if modules_dir.exists():
        python_files = list(modules_dir.rglob("*.py"))
        
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Look for flat module imports
                flat_patterns = [
                    r'from modules\.[^.]+\s+import',
                    r'import modules\.[^.]+'
                ]
                
                for pattern in flat_patterns:
                    if re.search(pattern, content):
                        violations.append(file_path)
                        break
                        
            except Exception:
                continue
    
    return violations

def main():
    """Main function to fix all import paths for Enterprise Domain compliance"""
    print("🔧 Enterprise Domain Import Migration Tool (WSP 3 Compliance)")
    print("=" * 60)
    
    # First, scan for violations
    print("🔍 Scanning for WSP 3 violations...")
    violations = scan_for_violations()
    
    if violations:
        print(f"⚠️  Found {len(violations)} files with potential flat import violations")
        for violation in violations[:5]:  # Show first 5
            print(f"   - {violation}")
        if len(violations) > 5:
            print(f"   ... and {len(violations) - 5} more")
    
    # Find all Python files to process
    modules_dir = Path("modules")
    python_files = list(modules_dir.rglob("*.py")) if modules_dir.exists() else []
    
    # Also check main.py and other root files
    root_files = ["main.py", "test_multi_agent_discovery.py"]
    for root_file in root_files:
        if Path(root_file).exists():
            python_files.append(Path(root_file))
    
    print(f"\n🔧 Processing {len(python_files)} Python files...")
    
    fixed_count = 0
    total_count = len(python_files)
    
    for file_path in python_files:
        if fix_imports_in_file(file_path):
            fixed_count += 1
    
    print(f"\n📊 Migration Summary:")
    print(f"  Total files checked: {total_count}")
    print(f"  Files updated: {fixed_count}")
    print(f"  Files unchanged: {total_count - fixed_count}")
    
    if fixed_count > 0:
        print(f"\n✨ Enterprise Domain import migration complete!")
        print("📝 Remember to run FMAS to verify WSP 3 compliance:")
        print("   python tools/modular_audit/modular_audit.py ./modules")
    else:
        print(f"\n✅ All imports already comply with Enterprise Domain structure!")

if __name__ == "__main__":
    main() 