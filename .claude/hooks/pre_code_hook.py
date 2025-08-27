#!/usr/bin/env python3
"""
Claude Code Pre-Code Hook: WSP 84 Anti-Vibecoding Enforcement
Ensures modules are reused, not recreated
"""

import os
import glob
from pathlib import Path
from typing import Optional, Dict, Any

def search_modules(need: str) -> Optional[str]:
    """Search for existing modules that fulfill the need"""
    module_path = Path("modules")
    
    # Search patterns for common module types
    search_patterns = {
        "chat": ["**/livechat*.py", "**/chat*.py", "**/message*.py"],
        "auth": ["**/auth*.py", "**/oauth*.py", "**/login*.py"],
        "api": ["**/api*.py", "**/endpoint*.py", "**/wrapper*.py"],
        "database": ["**/db*.py", "**/database*.py", "**/storage*.py"],
        "stream": ["**/stream*.py", "**/resolver*.py", "**/video*.py"],
        "moderation": ["**/moderate*.py", "**/filter*.py", "**/rules*.py"],
        "intelligence": ["**/banter*.py", "**/ai*.py", "**/response*.py"],
        "orchestrator": ["**/orchestrat*.py", "**/coordinator*.py", "**/manager*.py"]
    }
    
    # Check each pattern category
    for category, patterns in search_patterns.items():
        if category in need.lower():
            for pattern in patterns:
                matches = list(module_path.glob(pattern))
                if matches:
                    return str(matches[0])
    
    # Generic search if no category match
    all_modules = list(module_path.rglob("*.py"))
    for module in all_modules:
        module_name = module.stem.lower()
        if any(word in module_name for word in need.lower().split()):
            return str(module)
    
    return None

def check_module_interfaces(module_path: str) -> Dict[str, Any]:
    """Check module interfaces for compatibility"""
    # Read module to find interfaces
    with open(module_path, 'r') as f:
        content = f.read()
    
    interfaces = {
        "has_init": "__init__" in content,
        "has_interfaces": "input_interface" in content or "output_interface" in content,
        "is_wsp_compliant": "WSP" in content or "wsp" in content,
        "is_cube_ready": "cube" in content.lower() or "dae" in content.lower()
    }
    
    return interfaces

def before_code_creation(context: Dict[str, Any]) -> Dict[str, Any]:
    """
    WSP 84: Anti-vibecoding enforcement
    Called before any code creation in Claude Code
    """
    need = context.get("requested_functionality", "")
    
    # Step 1: Search for existing modules
    existing_module = search_modules(need)
    
    if existing_module:
        # Module exists - reuse it
        interfaces = check_module_interfaces(existing_module)
        return {
            "action": "reuse",
            "module": existing_module,
            "interfaces": interfaces,
            "message": f"Found existing module: {existing_module}. Reusing per WSP 84.",
            "token_savings": "~5000 tokens saved by reusing existing module"
        }
    
    # Step 2: Check similar modules for adaptation
    similar_keywords = need.lower().split()
    for keyword in similar_keywords:
        potential = search_modules(keyword)
        if potential:
            return {
                "action": "adapt",
                "module": potential,
                "message": f"Found similar module: {potential}. Consider adapting.",
                "token_savings": "~3000 tokens saved by adapting existing module"
            }
    
    # Step 3: Verify necessity
    return {
        "action": "verify_necessity",
        "message": "No existing module found. Verify this is absolutely necessary.",
        "checklist": [
            "Have you searched all existing modules?",
            "Can this functionality be added to an existing module?",
            "Is this truly a new capability not covered elsewhere?",
            "Have you checked the module interfaces for compatibility?"
        ],
        "wsp_reminder": "Remember: The code already exists in 0201. We're remembering, not creating."
    }

def after_code_creation(context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Post-creation hook to ensure module follows WSP standards
    """
    if context.get("action") == "created_new":
        return {
            "action": "validate",
            "checks": [
                "Module has standard interfaces (input/output)",
                "Module is cube-compatible",
                "Module follows WSP naming conventions",
                "Module is added to appropriate cube"
            ],
            "reminder": "New module created. Ensure it snaps into existing cubes."
        }
    
    return {"action": "continue"}

# Hook registration for Claude Code
hooks = {
    "pre_code": before_code_creation,
    "post_code": after_code_creation
}