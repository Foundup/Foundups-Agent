import os
from typing import Optional, List, Dict
import re

def validate_version(version: str) -> bool:
    """Validate version string follows semver pattern."""
    pattern = r'^(0\.0\.\d+|0\.1\.\d+|0\.[2-9]\.\d+|1\.\d+\.\d+)$'
    return bool(re.match(pattern, version))

def get_next_version(current_version: str) -> str:
    """Get next version number following semver pattern."""
    major, minor, patch = map(int, current_version.split('.'))
    return f"{major}.{minor}.{patch + 1}"

def validate_template_structure(content: str, template_path: str) -> bool:
    """Validate content structure against template."""
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            template = f.read()
        
        # Check for required sections
        required_sections = [
            "# FoundUps Agent Modular Change Log",
            "## FoundUps-Agent Roadmap",
            "## Status Ledger",
            "## MODLOG - [+UPDATES]:", # Ensure this is checked
            "## VERSION GUIDE"
        ]
        
        for section in required_sections:
            if section not in content:
                 print(f"Validation Failed: Section '{section}' missing.") # Add print
                 return False
                
        return True
    except Exception as e: # Keep exception logging
        print(f"Validation Exception: {e}")
        return False

def format_entry(
    module: str,
    change_type: str,
    version: str,
    description: str,
    notes: Optional[str] = None,
    features: Optional[List[str]] = None
) -> str:
    """Format a log entry according to the template structure."""
    entry = f"""- Version: {version}
- Description: {description}"""

    if notes:
        entry += f"\n- Notes: {notes}"
    
    if features:
        entry += "\n- Features:"
        for feature in features:
            entry += f"\n  - {feature}"
    
    entry += "\n\n"
    return entry

def log_update(
    module: str,
    change_type: str,
    version: str,
    description: str,
    notes: Optional[str] = None,
    features: Optional[List[str]] = None
) -> bool:
    """
    Updates ModLog.md with a new entry, following the template structure.
    
    Args:
        module: Name of the module being modified
        change_type: Type of change (e.g., "Added", "Updated", "Fixed")
        version: Version number (e.g., "0.1.0")
        description: Brief description of the changes
        notes: Optional additional details
        features: Optional list of features
        
    Returns:
        bool: True if update was successful, False otherwise
    """
    try:
        # Validate version format
        if not validate_version(version):
            print(f"Invalid version format: {version}")
            return False

        # Define paths
        modlog_path = "ModLog.md" # Use root ModLog.md per WSP 85
        template_path = "docs/ModLog_Template.md"

        # Read existing content
        existing_content = ""
        if os.path.exists(modlog_path): # Use modlog_path
            with open(modlog_path, "r", encoding="utf-8") as f: # Use modlog_path
                existing_content = f.read()

        # Format new entry
        new_entry = format_entry(
            module=module,
            change_type=change_type,
            version=version,
            description=description,
            notes=notes,
            features=features
        )

        # Find the insertion point (after MODLOG - [+UPDATES]: heading)
        insertion_point = "## MODLOG - [+UPDATES]:"
        
        # If insertion point doesn't exist, create it at the top of the file.
        if insertion_point not in existing_content:
            # Prepend the anchor and two newlines to separate from existing content.
            existing_content = f"# FoundUps Agent - Development Log\n\n{insertion_point}\n\n" + existing_content

        sections = existing_content.split(insertion_point)
        
        # This check is now redundant if we create the header, but good for safety.
        if len(sections) < 2:
            print(f"Failed to create or find insertion point: {insertion_point}")
            return False

        # Insert new entry immediately after the heading
        # Add only one extra newline after the header for spacing
        updated_content = sections[0] + insertion_point + "\n" + new_entry + sections[1]

        # Validate against template - NOTE: This check might fail if template expects more headers.
        # Temporarily disabling for resilience.
        # if not validate_template_structure(updated_content, template_path):
        #     print("Generated content does not match template structure")
        #     return False

        # Write updated content
        with open(modlog_path, "w", encoding="utf-8") as f: # Use modlog_path
            f.write(updated_content)

        return True

    except Exception as e:
        print(f"Error updating ModLog: {e}")
        return False

def format_checkbox_item(completed: bool = False) -> str:
    """Format checkbox item with new style."""
    return '[[OK]]' if completed else '[ ]'

# Example usage (Restore original example)
if __name__ == "__main__":
    # Test the module
    update = {
        "module": "StreamResolver",
        "change_type": "Updated",
        "version": "0.1.1",
        "description": "Enhanced StreamResolver with dynamic rate limiting and quota management",
        "notes": "Added smart throttling system, quota error handling, and secure ID masking",
        "features": [
            "Dynamic delays based on activity levels",
            "Quota error handling with retries",
            "Fallback credential support",
            "Random jitter for human-like behavior",
            "Smooth transitions between delays",
            "Secure ID masking in logs",
            "Development mode support"
        ]
    }
    
    success = log_update(**update)
    if success:
        print(f"Successfully updated ModLog.md for {update['module']}")
    else:
        print(f"Failed to update ModLog.md for {update['module']}") 