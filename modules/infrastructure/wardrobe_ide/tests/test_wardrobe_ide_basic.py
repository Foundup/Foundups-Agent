"""
Basic unit tests for Wardrobe IDE

Tests core functionality without actually launching browsers (uses mocks).
"""
import json
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest

# Import from the wardrobe_ide module
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from modules.infrastructure.wardrobe_ide.src.skill import WardrobeSkill
from modules.infrastructure.wardrobe_ide.src.skills_store import (
    save_skill,
    load_skill,
    list_skills,
    _slugify,
    import_skill_file,
)
from modules.infrastructure.wardrobe_ide.backends import get_backend
from modules.infrastructure.wardrobe_ide.src.recorder import record_new_skill


class TestWardrobeSkill:
    """Test WardrobeSkill dataclass."""

    def test_skill_creation(self):
        """Test creating a WardrobeSkill."""
        skill = WardrobeSkill(
            name="test_skill",
            backend="playwright",
            steps=[
                {"action": "click", "selector": "#button1"},
                {"action": "type", "selector": "#input1", "text": "hello"}
            ],
            meta={"target_url": "https://example.com"}
        )

        assert skill.name == "test_skill"
        assert skill.backend == "playwright"
        assert len(skill.steps) == 2
        assert skill.meta["target_url"] == "https://example.com"

    def test_skill_to_dict(self):
        """Test WardrobeSkill.to_dict() method."""
        skill = WardrobeSkill(
            name="test",
            backend="selenium",
            steps=[{"action": "click", "selector": "#btn"}]
        )

        data = skill.to_dict()

        assert data["name"] == "test"
        assert data["backend"] == "selenium"
        assert data["steps"] == [{"action": "click", "selector": "#btn"}]
        assert "created_at" in data

    def test_skill_from_dict(self):
        """Test WardrobeSkill.from_dict() method."""
        data = {
            "name": "test",
            "backend": "playwright",
            "steps": [{"action": "click", "selector": "#btn"}],
            "created_at": "2024-01-01T12:00:00",
            "meta": {"target_url": "https://example.com"}
        }

        skill = WardrobeSkill.from_dict(data)

        assert skill.name == "test"
        assert skill.backend == "playwright"
        assert len(skill.steps) == 1
        assert skill.meta["target_url"] == "https://example.com"


class TestSkillsStore:
    """Test skills store (save/load/list)."""

    @pytest.fixture
    def temp_skills_dir(self):
        """Create a temporary skills directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Patch the SKILLS_DIR and SKILLS_INDEX_PATH
            from modules.infrastructure.wardrobe_ide.src import skills_store
            original_dir = skills_store.SKILLS_DIR
            original_index = skills_store.SKILLS_INDEX_PATH

            skills_store.SKILLS_DIR = Path(tmpdir)
            skills_store.SKILLS_INDEX_PATH = Path(tmpdir) / "skills_index.json"

            yield Path(tmpdir)

            # Restore original paths
            skills_store.SKILLS_DIR = original_dir
            skills_store.SKILLS_INDEX_PATH = original_index

    def test_slugify(self):
        """Test _slugify function."""
        assert _slugify("YT Like and Reply") == "yt_like_and_reply"
        assert _slugify("Test@Skill#123") == "testskill123"
        assert _slugify("  spaces  ") == "spaces"

    def test_save_and_load_skill_roundtrip(self, temp_skills_dir):
        """Test saving and loading a skill."""
        # Create a skill
        skill = WardrobeSkill(
            name="Test Skill",
            backend="playwright",
            steps=[
                {"action": "click", "selector": "#btn1"},
                {"action": "type", "selector": "#input1", "text": "test"}
            ],
            meta={"target_url": "https://example.com", "tags": ["test"]}
        )

        # Save it
        filepath = save_skill(skill)
        assert filepath.exists()

        # Load it back
        loaded_skill = load_skill("Test Skill", backend="playwright")

        assert loaded_skill is not None
        assert loaded_skill.name == skill.name
        assert loaded_skill.backend == skill.backend
        assert len(loaded_skill.steps) == len(skill.steps)
        assert loaded_skill.meta["target_url"] == skill.meta["target_url"]

    def test_list_skills(self, temp_skills_dir):
        """Test listing all skills."""
        # Create and save multiple skills
        for i in range(3):
            skill = WardrobeSkill(
                name=f"Skill {i}",
                backend="playwright" if i % 2 == 0 else "selenium",
                steps=[{"action": "click", "selector": f"#btn{i}"}],
                meta={"target_url": f"https://example{i}.com"}
            )
            save_skill(skill)

        # List all skills
        all_skills = list_skills()
        assert len(all_skills) == 3

        # List with filter
        playwright_skills = list_skills(filter_backend="playwright")
        assert len(playwright_skills) == 2  # Skills 0 and 2

    def test_import_skill_file_maps_chrome_extension(self, temp_skills_dir):
        """Importing chrome_extension skills should map to selenium by default."""
        sample = {
            "name": "demo",
            "backend": "chrome_extension",
            "steps": [{"action": "click", "selector": "#btn"}],
            "meta": {"target_url": "https://example.com", "tags": ["demo"]},
        }
        src = temp_skills_dir / "sample.json"
        src.write_text(json.dumps(sample), encoding="utf-8")

        imported = import_skill_file(src)

        assert imported.name == "demo"
        assert imported.backend == "selenium"
        assert imported.meta["recorded_with"] == "chrome_extension"
        assert imported.meta["source_file"] == str(src)
        # Confirm it was saved to store
        loaded = load_skill("demo", backend="selenium")
        assert loaded is not None

class TestBackendResolver:
    """Test backend resolver."""

    def test_get_backend_playwright(self):
        """Test getting Playwright backend."""
        from modules.infrastructure.wardrobe_ide.backends.playwright_backend import PlaywrightBackend

        backend = get_backend("playwright")
        assert isinstance(backend, PlaywrightBackend)

    def test_get_backend_selenium(self):
        """Test getting Selenium backend."""
        from modules.infrastructure.wardrobe_ide.backends.selenium_backend import SeleniumBackend

        backend = get_backend("selenium")
        assert isinstance(backend, SeleniumBackend)

    def test_get_backend_invalid(self):
        """Test getting invalid backend."""
        with pytest.raises(ValueError, match="Unknown backend"):
            get_backend("invalid_backend")


class TestRecorder:
    """Test recorder orchestration (with mocked backends)."""

    def test_record_new_skill_calls_backend(self, tmp_path):
        """Test that record_new_skill calls the backend's record_session method."""
        # Patch skills store to use temp directory
        from modules.infrastructure.wardrobe_ide.src import skills_store
        original_dir = skills_store.SKILLS_DIR
        original_index = skills_store.SKILLS_INDEX_PATH

        skills_store.SKILLS_DIR = tmp_path
        skills_store.SKILLS_INDEX_PATH = tmp_path / "skills_index.json"

        try:
            # Mock the backend
            # Patch where it's used (recorder.get_backend is imported at module load)
            with patch("modules.infrastructure.wardrobe_ide.src.recorder.get_backend") as mock_get_backend:
                mock_backend = MagicMock()
                mock_backend.record_session.return_value = [
                    {"action": "click", "selector": "#btn", "timestamp": 0.5}
                ]
                mock_get_backend.return_value = mock_backend

                # Record a skill
                skill = record_new_skill(
                    name="Test Record",
                    target_url="https://example.com",
                    backend="playwright",
                    duration_seconds=10
                )

                # Verify backend was called
                mock_get_backend.assert_called_once_with("playwright")
                mock_backend.record_session.assert_called_once_with(
                    target_url="https://example.com",
                    duration_seconds=10
                )

                # Verify skill was created correctly
                assert skill.name == "Test Record"
                assert skill.backend == "playwright"
                assert len(skill.steps) == 1
                assert skill.steps[0]["action"] == "click"

        finally:
            # Restore original paths
            skills_store.SKILLS_DIR = original_dir
            skills_store.SKILLS_INDEX_PATH = original_index


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
