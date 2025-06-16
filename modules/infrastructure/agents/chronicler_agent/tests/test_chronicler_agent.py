import unittest
from pathlib import Path
import os
from modules.infrastructure.agents.chronicler_agent.src.chronicler_agent import ChroniclerAgent

class TestChroniclerAgent(unittest.TestCase):

    def setUp(self):
        # Create a temporary ModLog file for testing
        self.test_log_path = Path("test_modlog.md")
        with open(self.test_log_path, "w", encoding="utf-8") as f:
            f.write("# FoundUps Agent - Development Log\\n\\n")
            f.write("## MODLOG - [+UPDATES]:\\n\\n")
            f.write("## AN OLDER ENTRY\\n\\n---\\n\\n")
        
        self.agent = ChroniclerAgent(modlog_path_str=str(self.test_log_path))

    def tearDown(self):
        # Clean up the temporary file
        if os.path.exists(self.test_log_path):
            os.remove(self.test_log_path)

    def test_log_event_inserts_correctly(self):
        """
        Tests that the log_event method correctly formats and inserts
        a new entry at the top of the ModLog.
        """
        print("\\n--- Testing ChroniclerAgent ---")
        event = {
            "title": "Test Event",
            "version": "1.2.3",
            "description": "This is a test description.",
            "achievements": ["Did a thing", "Did another thing"]
        }
        
        result = self.agent.log_event(event)
        self.assertTrue(result["status"] == "success")

        content = self.test_log_path.read_text(encoding="utf-8")
        
        # Check that the new entry is present
        self.assertIn("## TEST EVENT", content)
        self.assertIn("**Version**: 1.2.3", content)
        self.assertIn("- Did a thing", content)
        
        # Check that the new entry is *after* the insertion marker
        # and *before* the old entry
        marker_pos = content.find("## MODLOG - [+UPDATES]:")
        new_entry_pos = content.find("## TEST EVENT")
        old_entry_pos = content.find("## AN OLDER ENTRY")

        self.assertTrue(marker_pos < new_entry_pos < old_entry_pos)
        print("--- ChroniclerAgent Test Passed ---")

if __name__ == '__main__':
    unittest.main() 