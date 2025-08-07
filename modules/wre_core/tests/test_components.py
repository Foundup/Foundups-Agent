import unittest
from pathlib import Path
import sys
import os
import pytest

# Add project root to Python path to allow for absolute imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from modules.wre_core.src.components.development import roadmap_manager
from modules.ai_intelligence.menu_handler.src.menu_handler import MenuHandler

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
    
    def setUp(self):
        """Set up test environment for MenuHandler."""
        self.project_root = Path(__file__).resolve().parent.parent.parent.parent
        # Mock UI interface and session manager for testing
        self.mock_ui_interface = type('MockUI', (), {
            'display_success': lambda x: None,
            'display_error': lambda x: None,
            'display_warning': lambda x: None,
            'get_user_input': lambda x: 'test',
            '_get_prioritized_modules': lambda: []
        })()
        self.mock_session_manager = type('MockSession', (), {
            'log_operation': lambda x, y: None,
            'log_module_access': lambda x, y: None,
            'log_achievement': lambda x, y: None
        })()
        
    def test_menu_handler_initialization(self):
        """Test that MenuHandler can be initialized."""
        menu_handler = MenuHandler(self.project_root, self.mock_ui_interface, self.mock_session_manager)
        self.assertIsInstance(menu_handler, MenuHandler)
        
    def test_menu_handler_has_required_methods(self):
        """Test that MenuHandler has the required methods."""
        menu_handler = MenuHandler(self.project_root, self.mock_ui_interface, self.mock_session_manager)
        
        # Check that required methods exist
        self.assertTrue(hasattr(menu_handler, 'handle_choice'))
        self.assertTrue(callable(menu_handler.handle_choice))

if __name__ == '__main__':
    unittest.main() 