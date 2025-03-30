# -*- coding: utf-8 -*-
"""
BanterEngine Module for Windsurf Project

Provides themed, randomized banter lines for agent interactions.
Loads data from memory/banter/banter_data.json with internal fallbacks.
"""

import json
import random
import logging
from pathlib import Path

# Minimal logging setup - prevents NoHandlerFound warning if not configured elsewhere
logger = logging.getLogger(__name__)
if not logger.handlers:
    logger.addHandler(logging.NullHandler())

# Define the expected location for custom banter data
DEFAULT_BANTER_FILE_PATH = Path("memory/banter/banter_data.json")

class BanterEngine:
    """
    Manages and retrieves themed banter lines for an agent.

    Loads data from an external JSON file with fallback to internal defaults.
    Supports themes and optional emoji presence (informational flag for now).
    Designed for fast, modular use within the Windsurf framework.
    """

    def __init__(self, banter_file_path=DEFAULT_BANTER_FILE_PATH, emoji_enabled=True):
        """
        Initializes the BanterEngine.

        Args:
            banter_file_path (Path or str): Path to the banter JSON file.
                                            Defaults to memory/banter/banter_data.json.
            emoji_enabled (bool): Flag to indicate if emoji usage is preferred.
                                  Currently informational, as default lines include them.
                                  Defaults to True.
        """
        self.banter_file_path = Path(banter_file_path)
        self.emoji_enabled = emoji_enabled
        self.banter_data = self._load_banter_data()
        self._all_lines_cache = None # Cache for flattened list of all lines
        self._validate_data_structure()

        if not self.banter_data:
             logger.error("BanterEngine initialized with no banter data (neither file nor defaults worked).")
             self.banter_data = {"error": ["No banter available."]} # Ensure it's never empty

        logger.info(f"BanterEngine initialized. Themes loaded: {list(self.banter_data.keys())}")

    def _get_default_banter(self):
        """Returns the default internal banter data structure."""
        # Structure: { "theme_name": ["line1", "line2", ...], ... }
        return {
            "roast": [
                "You keep 📢yelling but never **say**🫥 a single *thought*🧠 worth hearing 🤡😂",
                "MAGA logic is like 💾dial-up trying to load a 🚀rocket launch—*good luck* 🤣🤣",
                "You're not 💊red-pilled—you're just stuck in a 🌀spin-cycle of old Facebook 🧓feeds 🤯LOL",
                "\"I did my research\" = you scrolled 📲memes in your 🛋️mom's basement 🤓 ROTFL",
                "Every 📝sentence you write is a tripwire for a new 🧨braincell detonation 🤯💀🤣",
                "You chase 🦅freedom with the precision of a toddler and a 🔨hammer 🤪 LOL",
                "Quoting 🍊Trump isn't a 🪞personality—it's a cry for 📡Wi-Fi in a bunker 😂😂",
                "You block 📵facts faster than your 🐢router loads a single 📚truth 🤣💀",
                "You fear 📚books more than 💉needles but swallow 🍮conspiracy like candy 🤡🤢 LOL",
                "You scream 🎤\"freedom!\" while goose-stepping 🥾for billionaires 💵 you'll never meet 🤣💀"
            ],
            "philosophy": [
                "UNs✊ still tweaking on *Truth™ Lite*",
                "DAOs✋ chillin' in the middle like ✨balance with broadband✨",
                "DUs🖐️? Already built a quantum farm with solar flare wifi 💫🌱",
                "UNs: \"I did my own research\"",
                "DAOs: *sips tea with footnotes* ☕📖",
                "DUs: *already merged with O2 and left the chat* 🚀🧘‍♂️"
            ],
            "greeting": [
                "Hey there, streamers! 👋",
                "Welcome to the stream! 🎉",
                "Great to see everyone! ✨",
                "Stream time, let's go! 🚀",
                "Hello wonderful people! 💫"
            ],
            "rebuttal": [
                "That's... an opinion.",
                "Interesting theory. Source: Trust me bro?",
                "Did you stretch before reaching that conclusion?",
                "Hold on, let me get my tinfoil hat to understand this."
            ]
        }

    def _load_banter_data(self):
        """
        Loads banter data from the JSON file specified in banter_file_path.
        Falls back to internal defaults if the file doesn't exist, is invalid,
        or an error occurs during reading.
        """
        if self.banter_file_path.exists() and self.banter_file_path.is_file():
            try:
                with open(self.banter_file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                # Basic validation: Ensure it's a dictionary
                if isinstance(data, dict):
                    logger.info(f"Successfully loaded banter data from {self.banter_file_path}")
                    return data
                else:
                    logger.warning(f"Invalid format in {self.banter_file_path}. Expected a dictionary mapping themes to lists of strings. Falling back to defaults.")
                    return self._get_default_banter()
            except json.JSONDecodeError as e:
                logger.warning(f"Error decoding JSON from {self.banter_file_path}: {e}. Falling back to defaults.")
                return self._get_default_banter()
            except IOError as e:
                 logger.error(f"IOError reading {self.banter_file_path}: {e}. Falling back to defaults.")
                 return self._get_default_banter()
            except Exception as e:
                # Catch unexpected errors during file load
                logger.error(f"Unexpected error loading banter file {self.banter_file_path}: {e}. Falling back to defaults.")
                return self._get_default_banter()
        else:
            logger.info(f"Banter data file not found at '{self.banter_file_path}'. Using internal default banter.")
            return self._get_default_banter()

    def _validate_data_structure(self):
        """Checks if the loaded data structure is valid (dict of lists of strings)."""
        if not isinstance(self.banter_data, dict):
            logger.error("Banter data is not a dictionary. Reverting to default structure.")
            self.banter_data = self._get_default_banter()
            return # Exit early

        valid_structure = True
        for theme, lines in self.banter_data.items():
            if not isinstance(theme, str) or not isinstance(lines, list):
                logger.warning(f"Invalid structure for theme '{theme}'. Expected string theme and list of lines. Skipping this theme.")
                valid_structure = False
                continue

            if not all(isinstance(line, str) for line in lines):
                 logger.warning(f"Not all items in theme '{theme}' are strings. Invalid lines may cause errors.")
                 valid_structure = False

        if not valid_structure:
             logger.warning("Potential issues found in banter data structure.")
        self._all_lines_cache = None

    def _get_all_lines(self):
        """
        Helper method to get a flattened list of all valid banter lines.
        Uses a cache for performance.
        """
        if self._all_lines_cache is None:
            self._all_lines_cache = []
            for theme, lines in self.banter_data.items():
                 if isinstance(theme, str) and isinstance(lines, list):
                     self._all_lines_cache.extend([line for line in lines if isinstance(line, str)])
            if not self._all_lines_cache:
                 logger.warning("Flattened line cache is empty. No valid banter lines found.")

        return self._all_lines_cache

    def get_random_banter(self, theme=None):
        """
        Gets a random banter line, optionally filtered by theme.

        Args:
            theme (str, optional): The theme to filter by (e.g., 'roast', 'greeting').
                                   Case-sensitive. If None or invalid, selects
                                   from all available themes. Defaults to None.

        Returns:
            str: A randomly selected banter line. Returns a default fallback string
                 if no suitable lines are found.
        """
        lines_to_choose_from = []
        safe_fallback_message = "...silence..." # Default message if no lines found

        if theme:
            if theme in self.banter_data and isinstance(self.banter_data.get(theme), list):
                lines_to_choose_from = [line for line in self.banter_data[theme] if isinstance(line, str)]
                if not lines_to_choose_from:
                     logger.warning(f"Theme '{theme}' exists but contains no valid string lines. Selecting from all themes.")
                     lines_to_choose_from = self._get_all_lines()
            else:
                logger.warning(f"Theme '{theme}' not found or invalid in banter data. Selecting from all themes.")
                lines_to_choose_from = self._get_all_lines()
        else:
            lines_to_choose_from = self._get_all_lines()

        if not lines_to_choose_from:
            logger.error("No banter lines available to choose from, returning fallback message.")
            return safe_fallback_message

        try:
            return random.choice(lines_to_choose_from)
        except IndexError:
             logger.error("IndexError during random choice, returning fallback message.")
             return safe_fallback_message
        except Exception as e:
             logger.error(f"Unexpected error getting random banter: {e}, returning fallback message.")
             return safe_fallback_message

    def list_themes(self):
        """Returns a list of available banter themes."""
        return list(self.banter_data.keys())

# --- End of BanterEngine class ---

# Example Usage / Simple Test Harness (typically removed or commented out in production modules)
if __name__ == "__main__":
    print("--- Banter Engine Self-Test ---")
    logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')

    # Ensure potential directories exist for testing file operations
    test_dir = Path("memory/banter")
    test_dir.mkdir(parents=True, exist_ok=True)
    test_file = test_dir / "banter_data.json"

    # --- Test Case 1: No external file ---
    print("\n[Test 1: Using Default Internal Data (File Not Present)]")
    if test_file.exists():
        test_file.unlink() # Ensure file is gone

    engine_default = BanterEngine()
    print(f"Available themes: {engine_default.list_themes()}")
    print(f"Random (any theme): {engine_default.get_random_banter()}")
    print(f"Random (roast): {engine_default.get_random_banter(theme='roast')}")
    print(f"Random (greeting): {engine_default.get_random_banter(theme='greeting')}")
    print(f"Random (nonexistent theme): {engine_default.get_random_banter(theme='flattery')}") # Test fallback

    # --- Test Case 2: Valid external file ---
    print("\n[Test 2: Using Valid External JSON Data]")
    custom_data = {
        "greeting": ["Hello from custom file!", "JSON loaded successfully!"],
        "farewell": ["See ya later!", "Bye from JSON!"],
        "tech_joke": ["Why did the programmer quit his job? He didn't get arrays!"]
    }
    try:
        with open(test_file, 'w', encoding='utf-8') as f:
            json.dump(custom_data, f, indent=2)
        print(f"Created test file: {test_file}")

        engine_custom = BanterEngine() # Re-initialize to load the file
        print(f"Available themes: {engine_custom.list_themes()}")
        print(f"Random (any theme): {engine_custom.get_random_banter()}")
        print(f"Random (greeting): {engine_custom.get_random_banter(theme='greeting')}")
        print(f"Random (farewell): {engine_custom.get_random_banter(theme='farewell')}")
        print(f"Random (tech_joke): {engine_custom.get_random_banter(theme='tech_joke')}")
        print(f"Random (roast - not in file): {engine_custom.get_random_banter(theme='roast')}") # Test fallback for theme not in file

    except Exception as e:
        print(f"Error during Test 2: {e}")
    finally:
        if test_file.exists():
            test_file.unlink() # Clean up

    # --- Test Case 3: Invalid external file ---
    print("\n[Test 3: Handling Invalid JSON File]")
    try:
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write("this is { not valid json syntax")
        print(f"Created invalid test file: {test_file}")

        engine_invalid = BanterEngine() # Re-initialize
        print(f"Available themes (should fallback to defaults): {engine_invalid.list_themes()}")
        print(f"Random (any theme): {engine_invalid.get_random_banter()}")
        print(f"Random (roast): {engine_invalid.get_random_banter(theme='roast')}")

    except Exception as e:
        print(f"Error during Test 3: {e}")
    finally:
        if test_file.exists():
            test_file.unlink() # Clean up

     # --- Test Case 4: Empty external file ---
    print("\n[Test 4: Handling Empty JSON File]")
    try:
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write("") # Empty file
        print(f"Created empty test file: {test_file}")

        engine_empty_file = BanterEngine() # Re-initialize
        print(f"Available themes (should fallback to defaults): {engine_empty_file.list_themes()}")
        print(f"Random (any theme): {engine_empty_file.get_random_banter()}")

    except Exception as e:
        print(f"Error during Test 4: {e}")
    finally:
        if test_file.exists():
            test_file.unlink() # Clean up

     # --- Test Case 5: JSON file with wrong top-level structure (list instead of dict) ---
    print("\n[Test 5: Handling JSON with Incorrect Top-Level Structure (List)]")
    try:
        with open(test_file, 'w', encoding='utf-8') as f:
             json.dump(["just", "a", "list"], f)
        print(f"Created list-based JSON file: {test_file}")

        engine_wrong_structure = BanterEngine() # Re-initialize
        print(f"Available themes (should fallback to defaults): {engine_wrong_structure.list_themes()}")
        print(f"Random (any theme): {engine_wrong_structure.get_random_banter()}")

    except Exception as e:
        print(f"Error during Test 5: {e}")
    finally:
        if test_file.exists():
            test_file.unlink() # Clean up

    print("\n--- Banter Engine Self-Test Complete ---") 