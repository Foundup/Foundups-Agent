# Placeholder for the Chronicler Agent
from datetime import datetime
from pathlib import Path

class ChroniclerAgent:
    def __init__(self, modlog_path_str: str = "ModLog.md"):
        print("ChroniclerAgent initialized.")
        self.modlog_path = Path(modlog_path_str)

    def _format_entry(self, event_details: dict) -> str:
        """Formats the event details into a markdown string."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        title = event_details.get("title", "WRE Agent Operation").upper()
        version = event_details.get("version", "N/A")
        wsp_grade = event_details.get("wsp_grade", "B")
        description = event_details.get("description", "No description provided.")
        notes = event_details.get("notes", None)
        achievements = event_details.get("achievements", [])

        entry = f"## {title}\n"
        entry += f"**Date**: {timestamp}\n"
        entry += f"**Version**: {version}\n"
        entry += f"**WSP Grade**: {wsp_grade}\n"
        entry += f"**Description**: {description}\n"
        if notes:
            entry += f"**Notes**: {notes}\n"
        
        if achievements:
            entry += "\n### Key Achievements:\n"
            for item in achievements:
                entry += f"- {item}\n"
        
        return entry + "\n---\n\n"

    def log_event(self, event_details: dict) -> dict:
        """
        Records a significant event to the ModLog.md file by inserting it at the top.

        Args:
            event_details (dict): A dictionary with details of the event.
        """
        print(f"ChroniclerAgent: Logging event to {self.modlog_path}...")
        
        try:
            if not self.modlog_path.exists():
                return {"status": "error", "message": f"ModLog file not found at {self.modlog_path}"}

            content = self.modlog_path.read_text(encoding='utf-8')
            new_entry = self._format_entry(event_details)

            insertion_marker = "## MODLOG - [+UPDATES]:"
            parts = content.split(insertion_marker, 1)

            if len(parts) != 2:
                return {"status": "error", "message": f"Could not find insertion marker '{insertion_marker}' in {self.modlog_path}"}

            new_content = parts[0] + insertion_marker + "\n\n" + new_entry + parts[1]
            
            self.modlog_path.write_text(new_content, encoding='utf-8')

            print(f"  - Successfully added new entry to {self.modlog_path}")
            return {"status": "success", "entry_added": True}

        except Exception as e:
            print(f"  - ERROR: Failed to write to {self.modlog_path}: {e}")
            return {"status": "error", "message": str(e)} 