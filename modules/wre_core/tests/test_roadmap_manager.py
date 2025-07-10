import sys
import pytest
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from modules.wre_core.src.components.development import roadmap_manager
from modules.wre_core.src.components.development.roadmap_manager import parse_roadmap, add_new_objective

@pytest.fixture
def mock_roadmap_file(tmp_path):
    """Creates a temporary ROADMAP.md file for testing."""
    content = """
# Project Roadmap

## 🚀 Vision
A self-aware, agentic coding system.

---

## 🎭 0102 Theaters of Operation
-   **YouTube Agent:** `modules/platform_agents/youtube`
-   **Remote Agent:** `modules/platform_agents/remote`
-   **Discord Bot:** `modules/platform_agents/discord`

---

## ✅ Completed
-   Initial WRE setup.
"""
    roadmap_path = tmp_path / "ROADMAP.md"
    roadmap_path.write_text(content, encoding='utf-8')
    return tmp_path

def test_parse_roadmap_success(mock_roadmap_file):
    """
    Tests that parse_roadmap correctly extracts objectives from a valid file.
    """
    # The 'mock_roadmap_file' fixture provides a directory with ROADMAP.md in it.
    objectives = roadmap_manager.parse_roadmap(mock_roadmap_file)
    
    assert len(objectives) == 3
    assert objectives[0] == ("YouTube Agent", "modules/platform_agents/youtube")
    assert objectives[1] == ("Remote Agent", "modules/platform_agents/remote")
    assert objectives[2] == ("Discord Bot", "modules/platform_agents/discord")

def test_parse_roadmap_no_file(tmp_path):
    """
    Tests that parse_roadmap returns an empty list when ROADMAP.md doesn't exist.
    """
    objectives = roadmap_manager.parse_roadmap(tmp_path)
    assert objectives == []

def test_parse_roadmap_empty_file(tmp_path):
    """
    Tests that parse_roadmap returns an empty list for an empty ROADMAP.md.
    """
    (tmp_path / "ROADMAP.md").touch()
    objectives = roadmap_manager.parse_roadmap(tmp_path)
    assert objectives == []

def test_parse_roadmap_no_theaters_section(tmp_path):
    """
    Tests that parse_roadmap returns an empty list if the theaters section is missing.
    """
    content = """
# Project Roadmap
## ✅ Completed
- Stuff
"""
    (tmp_path / "ROADMAP.md").write_text(content, encoding='utf-8')
    objectives = roadmap_manager.parse_roadmap(tmp_path)
    assert objectives == [] 