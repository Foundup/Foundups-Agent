import os
from datetime import datetime
from typing import Optional, List, Tuple

def parse_entry_date(entry: str) -> datetime:
    """Extract and parse the date from a log entry."""
    for line in entry.split('\n'):
        if line.startswith('- Date: '):
            date_str = line.replace('- Date: ', '').strip()
            return datetime.strptime(date_str, "%Y-%m-%d %H:%M")
    return datetime.min

def sort_entries(entries: List[str]) -> List[str]:
    """Sort entries by date in descending order."""
    # Group entries by their header
    entry_groups = []
    current_entry = []
    
    for line in entries:
        if line.startswith('## [') and current_entry:
            entry_groups.append('\n'.join(current_entry))
            current_entry = []
        current_entry.append(line)
    
    if current_entry:
        entry_groups.append('\n'.join(current_entry))
    
    # Sort entries by date
    return sorted(entry_groups, key=parse_entry_date, reverse=True)

def log_update(
    module: str,
    change_type: str,
    version: str,
    description: str,
    notes: Optional[str] = None
) -> bool:
    """
    Prepends a structured log entry to ModLog.md, placing it after the header and roadmap sections.
    Maintains entries in descending chronological order.
    
    Args:
        module: Name of the module being modified
        change_type: Type of change (e.g., "Added", "Updated", "Fixed")
        version: Version number (e.g., "1.0.0")
        description: Brief description of the changes
        notes: Optional additional details
        
    Returns:
        bool: True if update was successful, False otherwise
    """
    try:
        # Format the entry with exact spacing
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        entry = f"""## [{module}] - {change_type}
- Version: {version}
- Date: {timestamp}
- Description: {description}"""

        if notes:
            entry += f"\n- Notes: {notes}"
        
        entry += "\n\n"  # Add spacing between entries

        # Define the header and roadmap structure
        header = """# FoundUps Agent Modular Change Log

This log tracks module changes, updates, and versioning for FoundUps Agent under the Windsurf modular development model.

## Project Roadmap

### ✅ Proof of Concept
- [x] Connect to YouTube livestream
- [x] Authenticate via OAuth
- [x] Send greeting message on join
- [x] Log chat messages per user

### 🚧 Prototype
- [x] StreamResolver module for dynamic video ID
- [ ] Modular chat processor with LLM hooks
- [ ] AI response and moderation module
- [ ] Prompt-throttle logic by channel activity
- [ ] ModLog updater
- [ ] Agent personality framework

### ⏳ Minimum Viable Product (MVP)
- [ ] Make bot publicly usable by other YouTubers
- [ ] Website with user onboarding (landing page + auth)
- [ ] Cloud deployment and user instance spin-up
- [ ] Bot tokenization and usage metering
- [ ] Admin dashboard for managing streams
- [ ] AI persona config for streamers
- [ ] Payment/paywall system

### 🧩 Release Phases

#### Tier 1 — Blockchain Foundation (DAE)
- [ ] Blockchain integration module toggle via `.env`
- [ ] Token drop + reward logic
- [ ] Wallet generation for viewers
- [ ] Token reclaim + decay logic

#### Tier 2 — DAO Evolution
- [ ] Token governance structure
- [ ] Voting logic for protocol decisions
- [ ] DAO treasury and fund routing

## Status Key
- Planned
- In Progress
- Complete
- Deprecated

"""

        # Read existing content if file exists
        existing_content = ""
        if os.path.exists("ModLog.md"):
            with open("ModLog.md", "r", encoding="utf-8") as f:
                existing_content = f.read()

        # Extract existing entries
        content_lines = existing_content.split('\n')
        entries = []
        current_entry = []
        
        for line in content_lines:
            if line.startswith('## [') and current_entry:
                entries.append('\n'.join(current_entry))
                current_entry = []
            if line.startswith('## [') or current_entry:
                current_entry.append(line)
        
        if current_entry:
            entries.append('\n'.join(current_entry))

        # Add new entry and sort all entries
        entries.append(entry)
        sorted_entries = sort_entries(entries)

        # Write the file with sorted entries
        with open("ModLog.md", "w", encoding="utf-8") as f:
            f.write(header)
            f.write('\n'.join(sorted_entries))

        return True

    except Exception as e:
        print(f"Error updating ModLog: {e}")
        return False

# Example usage
if __name__ == "__main__":
    # Test the module
    success = log_update(
        module="ModLog Updater",
        change_type="Updated",
        version="1.4.0",
        description="Fixed entry ordering to maintain descending chronological order",
        notes="Added date parsing and sorting functionality"
    )
    
    if success:
        print("Successfully updated ModLog.md")
    else:
        print("Failed to update ModLog.md") 