"""
BanterEngine module for generating chat banter and responses.
"""

import random
import logging

logger = logging.getLogger(__name__)

class BanterEngine:
    """Engine for generating chat banter and responses."""
    
    def _load_default_data(self):
        """Load default banter data."""
        return {
            "greeting": [
                "Hey there! 👋",
                "Hello everyone! ✨",
                "Welcome to the stream! 🎮",
                "Glad to be here! 🌟",
                "Hey folks! 🎯"
            ],
            "farewell": [
                "See you next time! 👋",
                "Take care everyone! ✨",
                "Thanks for hanging out! 🎮",
                "Until next time! 🌟",
                "Goodbye! 🎯"
            ]
        }

    def _validate_data_structure(self):
        """Validate the data structure has required themes."""
        required_themes = ["greeting", "farewell"]
        for theme in required_themes:
            if theme not in self.data:
                logger.warning(f"Missing required theme: {theme}")
                self.data[theme] = ["Hello! 👋"]  # Default fallback

    def __init__(self):
        """Initialize the BanterEngine with default data."""
        self.data = self._load_default_data()
        self._validate_data_structure()
        logger.info("BanterEngine initialized with themes: %s", list(self.data.keys()))
        logger.info("BanterEngine is actively looking for emoji triggers: ✊✋🖐")

    def get_random_banter(self, theme="greeting"):
        """
        Get a random banter line for the specified theme.
        
        Args:
            theme (str): The theme to get banter for. Defaults to "greeting".
            
        Returns:
            str: A random banter line for the theme.
        """
        if theme not in self.data:
            logger.warning("Theme '%s' not found, using 'greeting'", theme)
            theme = "greeting"
            
        banter = random.choice(self.data[theme])
        logger.debug("Generated banter for theme '%s': %s", theme, banter)
        return banter

    def list_themes(self):
        """
        Get a list of available themes.
        
        Returns:
            list: List of available theme names.
        """
        return list(self.data.keys())

    def check_for_emojis(self, message):
        """
        Logs any detected trigger emojis from a message.
        
        Args:
            message: The message to check for emojis
        """
        for emoji in ['✊', '✋', '🖐']:
            if emoji in message:
                logger.info(f"[Emoji Trigger Detected] {emoji} found in: {message}")

if __name__ == "__main__":
    # Test the BanterEngine
    print("🧪 Testing BanterEngine...")
    
    # Create a test instance
    engine_default = BanterEngine()
    
    # Test getting random banter
    print("\n🧪 Testing random banter generation:")
    for _ in range(3):
        line = engine_default.get_random_banter(theme="greeting")
        print(f"Generated: {line}")
    
    # Test emoji detection
    print("\n🧪 Testing emoji detection:")
    test_messages = [
        "Hey everyone ✊", 
        "What up ✋", 
        "Stream is live 🖐", 
        "No emojis here"
    ]
    
    for msg in test_messages:
        engine_default.check_for_emojis(msg) 