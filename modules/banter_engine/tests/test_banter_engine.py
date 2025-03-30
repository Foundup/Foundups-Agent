import logging
import sys
import os

# Add module root to Python path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.banter_engine import BanterEngine

def test_greeting_banter():
    print("🧪 Testing BanterEngine: greeting theme")
    engine = BanterEngine()
    line = engine.get_random_banter(theme="greeting")
    print(f"Result: {line}")
    assert isinstance(line, str) and len(line) > 0, "Empty or invalid banter line"

def test_theme_list():
    print("🧪 Testing BanterEngine: theme list")
    engine = BanterEngine()
    themes = engine.list_themes()
    print(f"Available themes: {themes}")
    assert "greeting" in themes, "Missing 'greeting' theme"

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    test_greeting_banter()
    test_theme_list() 