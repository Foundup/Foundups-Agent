"""
Browser Manager
Manages singleton browser instances to avoid opening multiple windows
Reuses existing browser sessions for posting
"""

import os
import logging
import threading
from typing import Optional, Dict, Any
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.edge.options import Options as EdgeOptions


class BrowserManager:
    """Singleton browser manager to reuse browser instances"""

    _instance = None
    _lock = threading.Lock()
    _browsers = {}  # Store browser instances by key

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance.logger = logging.getLogger(__name__)
                    cls._instance._browsers = {}
                    cls._instance._browser_locks = {}
        return cls._instance

    def get_browser(self, browser_type: str, profile_name: str, options: Dict[str, Any] = None) -> Any:
        """
        Get or create a browser instance

        Args:
            browser_type: 'chrome' or 'edge'
            profile_name: Unique profile identifier (e.g., 'linkedin', 'x_foundups', 'x_move2japan')
            options: Additional browser options

        Returns:
            Browser driver instance
        """
        browser_key = f"{browser_type}_{profile_name}"

        # Check if browser exists and is still valid
        if browser_key in self._browsers:
            browser = self._browsers[browser_key]
            try:
                # Check if browser is still responsive
                _ = browser.current_url
                self.logger.info(f"✅ Reusing existing {browser_type} browser for {profile_name}")
                return browser
            except Exception as e:
                self.logger.warning(f"⚠️ Existing browser unresponsive: {e}")
                # Browser is dead, remove it
                del self._browsers[browser_key]

        # Create new browser instance
        self.logger.info(f"🌐 Creating new {browser_type} browser for {profile_name}")

        if browser_type.lower() == 'chrome':
            browser = self._create_chrome_browser(profile_name, options)
        elif browser_type.lower() == 'edge':
            browser = self._create_edge_browser(profile_name, options)
        else:
            raise ValueError(f"Unsupported browser type: {browser_type}")

        # Store browser instance
        self._browsers[browser_key] = browser
        self.logger.info(f"✅ Browser created and stored: {browser_key}")

        return browser

    def _create_chrome_browser(self, profile_name: str, custom_options: Dict[str, Any] = None):
        """Create Chrome browser with anti-detection settings"""
        chrome_options = ChromeOptions()

        # Anti-detection flags
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)

        # Standard settings
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--start-maximized')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')

        # User agent
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

        # Use existing profile to maintain session and reuse browser
        # Map profile names to actual Chrome profile directories
        profile_mapping = {
            'linkedin_104834798': 'O:/Foundups-Agent/modules/platform_integration/linkedin_agent/data/chrome_profile',  # GeoZai
            'linkedin_1263645': 'O:/Foundups-Agent/modules/platform_integration/linkedin_agent/data/chrome_profile',     # FoundUps
            'linkedin_165749317': 'O:/Foundups-Agent/modules/platform_integration/linkedin_agent/data/chrome_profile',   # UnDaoDu
            'x_move2japan': 'O:/Foundups-Agent/modules/platform_integration/x_twitter/data/chrome_profile_move2japan',
            'x_foundups': 'O:/Foundups-Agent/modules/platform_integration/x_twitter/data/chrome_profile_foundups'
        }

        profile_dir = profile_mapping.get(profile_name)
        if not profile_dir:
            # Fallback to default profile
            profile_dir = f"O:/Foundups-Agent/modules/platform_integration/browser_profiles/{profile_name}/chrome"

        os.makedirs(profile_dir, exist_ok=True)
        chrome_options.add_argument(f'--user-data-dir={profile_dir}')
        chrome_options.add_argument('--profile-directory=Default')

        # Apply custom options if provided
        if custom_options:
            for key, value in custom_options.items():
                if key == 'headless' and value:
                    chrome_options.add_argument('--headless')

        driver = webdriver.Chrome(options=chrome_options)

        # Override navigator.webdriver flag
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        return driver

    def _create_edge_browser(self, profile_name: str, custom_options: Dict[str, Any] = None):
        """Create Edge browser with anti-detection settings"""
        edge_options = EdgeOptions()

        # Anti-detection flags
        edge_options.add_argument('--disable-blink-features=AutomationControlled')
        edge_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        edge_options.add_experimental_option('useAutomationExtension', False)

        # Standard settings
        edge_options.add_argument('--window-size=1920,1080')
        edge_options.add_argument('--start-maximized')
        edge_options.add_argument('--disable-gpu')
        edge_options.add_argument('--no-sandbox')
        edge_options.add_argument('--disable-dev-shm-usage')

        # User agent
        edge_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0')

        # Use profile to maintain session
        profile_dir = f"O:/Foundups-Agent/modules/platform_integration/browser_profiles/{profile_name}/edge"
        os.makedirs(profile_dir, exist_ok=True)
        edge_options.add_argument(f'--user-data-dir={profile_dir}')
        edge_options.add_argument('--profile-directory=Default')

        # Apply custom options if provided
        if custom_options:
            for key, value in custom_options.items():
                if key == 'headless' and value:
                    edge_options.add_argument('--headless')

        driver = webdriver.Edge(options=edge_options)

        # Override navigator.webdriver flag
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        return driver

    def close_browser(self, browser_type: str, profile_name: str):
        """Close a specific browser instance"""
        browser_key = f"{browser_type}_{profile_name}"

        if browser_key in self._browsers:
            try:
                browser = self._browsers[browser_key]
                browser.quit()
                self.logger.info(f"🔒 Closed browser: {browser_key}")
            except Exception as e:
                self.logger.warning(f"⚠️ Error closing browser: {e}")
            finally:
                del self._browsers[browser_key]

    def close_all_browsers(self):
        """Close all browser instances"""
        for browser_key in list(self._browsers.keys()):
            browser_type, profile_name = browser_key.split('_', 1)
            self.close_browser(browser_type, profile_name)

        self.logger.info("🔒 All browsers closed")

    def get_active_browsers(self) -> Dict[str, bool]:
        """Get status of all browser instances"""
        status = {}
        for browser_key, browser in self._browsers.items():
            try:
                _ = browser.current_url
                status[browser_key] = True
            except:
                status[browser_key] = False
        return status


# Singleton instance
_browser_manager = None


def get_browser_manager() -> BrowserManager:
    """Get singleton browser manager instance"""
    global _browser_manager
    if _browser_manager is None:
        _browser_manager = BrowserManager()
    return _browser_manager