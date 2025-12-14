"""
Basic validation script for Wardrobe IDE (no pytest dependency)

Tests core functionality manually.
"""
import sys
from pathlib import Path

# Add repo root to path
repo_root = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(repo_root))

from modules.infrastructure.wardrobe_ide.src.skill import WardrobeSkill
from modules.infrastructure.wardrobe_ide.src.skills_store import _slugify
from modules.infrastructure.wardrobe_ide.backends import get_backend

print("\n" + "="*80)
print(" WARDROBE IDE - BASIC VALIDATION")
print("="*80)

# Test 1: WardrobeSkill creation
print("\n[TEST 1] WardrobeSkill creation...")
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
print("  [OK] WardrobeSkill creation works")

# Test 2: to_dict / from_dict
print("\n[TEST 2] Skill serialization...")
data = skill.to_dict()
assert data["name"] == "test_skill"
assert "created_at" in data

restored_skill = WardrobeSkill.from_dict(data)
assert restored_skill.name == skill.name
assert restored_skill.backend == skill.backend
assert len(restored_skill.steps) == len(skill.steps)
print("  [OK] Serialization works")

# Test 3: Slugify
print("\n[TEST 3] Slugify function...")
assert _slugify("YT Like and Reply") == "yt_like_and_reply"
assert _slugify("Test@Skill#123") == "testskill123"
print("  [OK] Slugify works")

# Test 4: Backend resolver
print("\n[TEST 4] Backend resolver...")
playwright_backend = get_backend("playwright")
assert playwright_backend is not None
print("  [OK] Playwright backend loaded")

selenium_backend = get_backend("selenium")
assert selenium_backend is not None
print("  [OK] Selenium backend loaded")

try:
    get_backend("invalid")
    assert False, "Should have raised ValueError"
except ValueError:
    print("  [OK] Invalid backend raises error")

# Test 5: Selenium recording raises NotImplementedError
print("\n[TEST 5] Selenium recording not implemented...")
try:
    selenium_backend.record_session("https://example.com")
    assert False, "Should have raised NotImplementedError"
except NotImplementedError:
    print("  [OK] Selenium recording properly stubbed")

print("\n" + "="*80)
print(" ALL VALIDATION TESTS PASSED")
print("="*80)
print("\nWardrobe IDE foundation layer is working correctly!")
print("\nNext steps:")
print("  1. Test recording with: python -m modules.infrastructure.wardrobe_ide record ...")
print("  2. Test replay with: python -m modules.infrastructure.wardrobe_ide replay ...")
print("  3. List skills with: python -m modules.infrastructure.wardrobe_ide list")
