"""
Undetected Browser Manager
==========================

Creates browser instances with advanced anti-detection measures.

Requires: pip install undetected-chromedriver

WSP References: WSP 77 (AI Coordination), WSP 49 (Platform Integration Safety)
"""

import os
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class UndetectedBrowserManager:
    """Creates browser instances that evade automation detection."""

    @staticmethod
    def create_undetected_chrome(profile_path: Optional[str] = None,
                                 options: Optional[Dict[str, Any]] = None):
        """
        Create Chrome browser with advanced anti-detection.

        This uses undetected-chromedriver which bypasses:
        - navigator.webdriver flag
        - Chrome DevTools Protocol detection
        - Browser fingerprinting
        - Headless detection

        Args:
            profile_path: Path to Chrome user data directory
            options: Additional Chrome options

        Returns:
            Undetected Chrome driver instance

        Raises:
            ImportError: If undetected-chromedriver not installed
        """
        try:
            import undetected_chromedriver as uc
        except ImportError:
            logger.error("undetected-chromedriver not installed!")
            logger.error("Install: pip install undetected-chromedriver")
            raise

        # Create options
        uc_options = uc.ChromeOptions()

        # Standard settings
        uc_options.add_argument('--window-size=1920,1080')
        uc_options.add_argument('--start-maximized')
        uc_options.add_argument('--disable-gpu')
        uc_options.add_argument('--no-sandbox')
        uc_options.add_argument('--disable-dev-shm-usage')

        # Use existing profile (maintains cookies, session)
        if profile_path:
            uc_options.add_argument(f'--user-data-dir={profile_path}')

        # User agent (match real browser)
        uc_options.add_argument(
            'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/120.0.0.0 Safari/537.36'
        )

        # Additional custom options
        if options:
            for key, value in options.items():
                uc_options.add_argument(f'--{key}={value}')

        logger.info("[UNDETECTED] Creating undetected Chrome browser...")

        # Create undetected Chrome instance
        driver = uc.Chrome(
            options=uc_options,
            version_main=120,  # Match installed Chrome version
            use_subprocess=False,  # Avoid extra processes
        )

        # Inject additional stealth JavaScript
        UndetectedBrowserManager._inject_stealth_js(driver)

        logger.info("[UNDETECTED] Browser created successfully")
        logger.info(f"[UNDETECTED] navigator.webdriver = {driver.execute_script('return navigator.webdriver')}")

        return driver

    @staticmethod
    def _inject_stealth_js(driver):
        """
        Inject additional JavaScript to evade detection.

        This adds properties that YouTube checks for bot detection.
        """
        stealth_js = """
        // Hide webdriver flag
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });

        // Add plugins (bots have empty plugins)
        Object.defineProperty(navigator, 'plugins', {
            get: () => [1, 2, 3, 4, 5]
        });

        // Add languages
        Object.defineProperty(navigator, 'languages', {
            get: () => ['en-US', 'en']
        });

        // Add chrome runtime (missing in automation)
        window.chrome = {
            runtime: {}
        };

        // Spoof permissions API (bots have limited permissions)
        const originalQuery = window.navigator.permissions.query;
        window.navigator.permissions.query = (parameters) => (
            parameters.name === 'notifications' ?
                Promise.resolve({ state: Notification.permission }) :
                originalQuery(parameters)
        );

        // Connection detection (bots show 'undefined')
        Object.defineProperty(navigator, 'connection', {
            get: () => ({
                effectiveType: '4g',
                downlink: 10,
                rtt: 50
            })
        });

        // Hardware concurrency (bots show low values)
        Object.defineProperty(navigator, 'hardwareConcurrency', {
            get: () => 8
        });

        // Device memory (bots show undefined)
        Object.defineProperty(navigator, 'deviceMemory', {
            get: () => 8
        });

        console.log('[STEALTH] Anti-detection JavaScript injected');
        """

        try:
            driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': stealth_js
            })
            logger.info("[STEALTH] Anti-detection JavaScript injected")
        except Exception as e:
            logger.warning(f"[STEALTH] Could not inject stealth JS: {e}")

    @staticmethod
    def test_detection(driver):
        """
        Test if browser is detected as automation.

        Returns dict with detection test results.
        """
        tests = {}

        # Test 1: navigator.webdriver
        tests['webdriver'] = driver.execute_script('return navigator.webdriver')

        # Test 2: Chrome webdriver property
        tests['chrome_webdriver'] = driver.execute_script(
            'return window.chrome && window.chrome.webdriver'
        )

        # Test 3: Plugins count
        tests['plugins_count'] = driver.execute_script('return navigator.plugins.length')

        # Test 4: Languages
        tests['languages'] = driver.execute_script('return navigator.languages')

        # Test 5: Connection
        tests['connection'] = driver.execute_script(
            'return navigator.connection ? "present" : "missing"'
        )

        # Test 6: Hardware concurrency
        tests['hardware'] = driver.execute_script('return navigator.hardwareConcurrency')

        # Analysis
        detected = (
            tests['webdriver'] is True or
            tests['chrome_webdriver'] is True or
            tests['plugins_count'] == 0 or
            not tests['languages'] or
            tests['connection'] == 'missing'
        )

        return {
            'detected': detected,
            'tests': tests,
            'verdict': 'DETECTED AS BOT' if detected else 'PASSES AS HUMAN'
        }


def get_undetected_browser(profile_path: Optional[str] = None):
    """
    Factory function to create undetected browser.

    Usage:
        driver = get_undetected_browser('/path/to/profile')
        driver.get('https://youtube.com')
    """
    return UndetectedBrowserManager.create_undetected_chrome(profile_path)
