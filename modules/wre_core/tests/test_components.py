import unittest
from pathlib import Path
import sys
import os
import pytest
from modules.wre_core.src.components.menu_handler import present_harmonic_query, display_menu

# Add project root to Python path to allow for absolute imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from modules.wre_core.src.components import roadmap_manager
from modules.wre_core.src.components import menu_handler

## 🎭 0102 Theaters of Operation
# This test suite validates the integration and functionality of various WRE
# components, ensuring they work together as part of the cohesive 0102
# operational architecture.

class TestWREComponents(unittest.TestCase):

    def setUp(self):
        """Set up a temporary test directory and dummy roadmap file."""
        self.test_dir = Path("test_wre_temp")
        self.test_dir.mkdir(exist_ok=True)
        self.roadmap_path = self.test_dir / "ROADMAP.md"
        
        roadmap_content = """
## 🎭 O1O2 Theaters of Operation

-   **YouTube Agent:** `modules/platform_integration/youtube_proxy`
-   **LinkedIn Agent:** `modules/platform_integration/linkedin_proxy`
-   **X Agent:** `modules/platform_integration/x_proxy`
-   **Remote Agent:** `modules/platform_integration/remote_proxy`

---
"""
        self.roadmap_path.write_text(roadmap_content, encoding='utf-8')

    def tearDown(self):
        """Clean up the temporary directory and files."""
        self.roadmap_path.unlink()
        try:
            self.test_dir.rmdir()
        except OSError:
            # The directory might not be empty if other tests use it
            pass

    def test_parse_roadmap(self):
        """
        Tests that the roadmap_manager correctly parses the strategic
        objectives from a dummy ROADMAP.md file.
        """
        expected_objectives = [
            ('YouTube Agent', 'modules/platform_integration/youtube_proxy'),
            ('LinkedIn Agent', 'modules/platform_integration/linkedin_proxy'),
            ('X Agent', 'modules/platform_integration/x_proxy'),
            ('Remote Agent', 'modules/platform_integration/remote_proxy')
        ]
        
        # Pass the directory containing the dummy ROADMAP.md
        parsed_objectives = roadmap_manager.parse_roadmap(self.test_dir)
        
        self.assertEqual(parsed_objectives, expected_objectives)
        self.assertEqual(len(parsed_objectives), 4)

class TestMenuHandler(unittest.TestCase):
    """Test menu handler functionality."""
    
    def test_present_harmonic_query(self):
        """Test that present_harmonic_query function exists and can be called."""
        system_state = {'janitor_status': 'OK', 'semantic_status': 'OK', 'readme_coherence': 'OK', 'next_wsp_number': 57}
        roadmap_objectives = [('Test Objective', 'test/path')]
        
        # This would normally require user input, so we'll just test the function exists
        self.assertTrue(callable(present_harmonic_query))
        
    def test_display_menu_function(self):
        """Test that display_menu function exists."""
        self.assertTrue(callable(display_menu))

if __name__ == '__main__':
    unittest.main() 