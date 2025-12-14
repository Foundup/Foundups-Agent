"""
Wardrobe IDE Configuration

Configuration settings for the Wardrobe IDE module.
"""
import os
from pathlib import Path

# Default backend for recording/replay
DEFAULT_BACKEND = os.getenv("WARDROBE_DEFAULT_BACKEND", "playwright")

# Skills storage directory
WARDROBE_IDE_ROOT = Path(__file__).parent.parent
SKILLS_DIR = Path(os.getenv(
    "WARDROBE_SKILLS_DIR",
    str(WARDROBE_IDE_ROOT / "skills")
))

# Skills index file
SKILLS_INDEX_PATH = SKILLS_DIR / "skills_index.json"

# Ensure skills directory exists
SKILLS_DIR.mkdir(parents=True, exist_ok=True)

# Recording defaults
DEFAULT_RECORD_DURATION = int(os.getenv("WARDROBE_RECORD_DURATION", "15"))

# Browser settings
HEADLESS = os.getenv("WARDROBE_HEADLESS", "false").lower() == "true"
SLOW_MO = int(os.getenv("WARDROBE_SLOW_MO", "0"))  # Milliseconds to slow down operations
