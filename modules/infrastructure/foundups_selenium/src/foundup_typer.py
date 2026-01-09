"""
FoundUps Unified Typer - Single Lego Piece for All Typing Operations
=====================================================================

WSP 77 (AI Coordination): Shared typing module across all DAEs
WSP 49 (Module Structure): Reusable lego block for browser automation

This module unifies all typing operations across the platform:
- YouTube Studio (contenteditable divs)
- X/Twitter (contenteditable divs)  
- LinkedIn (standard inputs)
- Any future social media integration

Auto-detects element type and uses appropriate method:
- Standard inputs → send_keys()
- Contenteditable divs → JS character injection
- Shadow DOM → JS character injection

Configurable via environment variables:
- FOUNDUP_TYPING_SPEED: 0.5=fast, 1.0=normal, 2.0=slow (default 1.0)
- FOUNDUP_TYPO_RATE: 0.0-1.0 (default 0.05 = 5%)
- FOUNDUP_HESITATION_RATE: 0.0-1.0 (default 0.03 = 3%)
"""

import asyncio
import logging
import os
import random
import time
from typing import Any, Optional, Tuple, Union

logger = logging.getLogger(__name__)

# Base delays (these get multiplied by FOUNDUP_TYPING_SPEED)
BASE_CHAR_DELAY = 0.064      # Normal characters (20% faster than original 0.08)
BASE_SPACE_DELAY = 0.096     # Spaces (20% faster than original 0.12)
BASE_PUNCT_DELAY = 0.128     # Punctuation (20% faster than original 0.16)
BASE_HESITATION_MIN = 0.5    # Min hesitation pause
BASE_HESITATION_MAX = 2.0    # Max hesitation pause


class FoundupsTyper:
    """
    Unified typing module for all FoundUps browser automation.
    
    Usage:
        typer = FoundupsTyper(driver)
        await typer.type_text(element, "Hello world!")  # Async
        typer.type_text_sync(element, "Hello world!")   # Sync
    """
    
    def __init__(self, driver, speed_multiplier: Optional[float] = None):
        """
        Initialize the typer.
        
        Args:
            driver: Selenium WebDriver instance
            speed_multiplier: Override for FOUNDUP_TYPING_SPEED env var
                             0.5 = 2x faster, 1.0 = normal, 2.0 = 2x slower
        """
        self.driver = driver
        
        # Load config from env or use defaults
        self.speed_multiplier = speed_multiplier or float(
            os.getenv("FOUNDUP_TYPING_SPEED", "1.0")
        )
        self.typo_rate = float(os.getenv("FOUNDUP_TYPO_RATE", "0.05"))
        self.hesitation_rate = float(os.getenv("FOUNDUP_HESITATION_RATE", "0.03"))
        
        logger.info(
            f"[TYPER] Initialized: speed={self.speed_multiplier}x, "
            f"typos={self.typo_rate*100:.0f}%, hesitations={self.hesitation_rate*100:.0f}%"
        )
    
    def _detect_element_type(self, element) -> str:
        """
        Detect what type of element we're typing into.
        
        Returns:
            'input' - Standard input/textarea (use send_keys)
            'contenteditable' - Contenteditable div (use JS injection)
            'shadow' - Shadow DOM element (use JS injection)
        """
        try:
            tag = element.tag_name.lower()
            
            # Standard input elements
            if tag in ('input', 'textarea'):
                return 'input'
            
            # Check for contenteditable
            contenteditable = element.get_attribute('contenteditable')
            if contenteditable and contenteditable.lower() == 'true':
                return 'contenteditable'
            
            # Check for role="textbox" (common in modern web apps)
            role = element.get_attribute('role')
            if role and role.lower() == 'textbox':
                return 'contenteditable'
            
            # Default to contenteditable for divs (safer for modern web apps)
            if tag == 'div':
                return 'contenteditable'
            
            return 'input'
            
        except Exception as e:
            logger.warning(f"[TYPER] Element detection failed: {e}, defaulting to input")
            return 'input'
    
    def _get_char_delay(self, char: str) -> float:
        """Get appropriate delay for character type with randomness."""
        if char == ' ':
            base = BASE_SPACE_DELAY
        elif char in '.,!?;:':
            base = BASE_PUNCT_DELAY
        else:
            base = BASE_CHAR_DELAY
        
        # Apply speed multiplier and add randomness (0.7x to 1.5x)
        delay = base * self.speed_multiplier * random.uniform(0.7, 1.5)
        return delay
    
    def _should_typo(self) -> bool:
        """Randomly decide if we should make a typo."""
        return random.random() < self.typo_rate
    
    def _should_hesitate(self) -> bool:
        """Randomly decide if we should pause (simulates thinking)."""
        return random.random() < self.hesitation_rate
    
    def _get_typo_char(self) -> str:
        """Get a random typo character."""
        return random.choice('abcdefghijklmnopqrstuvwxyz')
    
    # =========== ASYNC METHODS (for asyncio-based DAEs) ===========
    
    async def type_text(
        self, 
        element, 
        text: str, 
        clear_first: bool = True,
        click_first: bool = True
    ) -> bool:
        """
        Type text into element with human-like behavior (async version).
        
        Args:
            element: Selenium WebElement to type into
            text: Text to type
            clear_first: Clear element before typing
            click_first: Click element to focus before typing
            
        Returns:
            True if successful, False otherwise
        """
        try:
            element_type = self._detect_element_type(element)
            logger.debug(f"[TYPER] Element type: {element_type}")
            
            if click_first:
                self.driver.execute_script("arguments[0].click();", element)
                await asyncio.sleep(0.1)
            
            if clear_first:
                await self._clear_element(element, element_type)
            
            if element_type == 'input':
                return await self._type_via_send_keys(element, text)
            else:
                return await self._type_via_js(element, text)
                
        except Exception as e:
            logger.error(f"[TYPER] Typing failed: {e}")
            return False
    
    async def _clear_element(self, element, element_type: str):
        """Clear element content."""
        if element_type == 'input':
            element.clear()
        else:
            self.driver.execute_script("arguments[0].textContent = '';", element)
        await asyncio.sleep(0.05)
    
    async def _type_via_send_keys(self, element, text: str) -> bool:
        """Type using Selenium send_keys (for standard inputs)."""
        from selenium.webdriver.common.keys import Keys
        
        for i, char in enumerate(text):
            # Occasional typo
            if self._should_typo() and i > 0:
                typo_char = self._get_typo_char()
                element.send_keys(typo_char)
                await asyncio.sleep(self._get_char_delay(typo_char))
                element.send_keys(Keys.BACKSPACE)
                await asyncio.sleep(0.05)
            
            # Type the actual character
            element.send_keys(char)
            await asyncio.sleep(self._get_char_delay(char))
            
            # Occasional hesitation
            if self._should_hesitate():
                hesitate = random.uniform(BASE_HESITATION_MIN, BASE_HESITATION_MAX)
                logger.debug(f"[TYPER] Hesitation: {hesitate:.1f}s")
                await asyncio.sleep(hesitate)
        
        logger.info(f"[TYPER] Typed {len(text)} chars via send_keys")
        return True
    
    async def _type_via_js(self, element, text: str) -> bool:
        """Type using JS character injection (for contenteditable/shadow DOM)."""
        for i, char in enumerate(text):
            # Occasional typo
            if self._should_typo() and i > 0:
                typo_char = self._get_typo_char()
                self._inject_char(element, typo_char)
                await asyncio.sleep(self._get_char_delay(typo_char))
                self._delete_last_char(element)
                await asyncio.sleep(0.05)
            
            # Type the actual character
            self._inject_char(element, char)
            await asyncio.sleep(self._get_char_delay(char))
            
            # Occasional hesitation
            if self._should_hesitate():
                hesitate = random.uniform(BASE_HESITATION_MIN, BASE_HESITATION_MAX)
                logger.debug(f"[TYPER] Hesitation: {hesitate:.1f}s")
                await asyncio.sleep(hesitate)
        
        # Trigger final events
        self.driver.execute_script("""
            const el = arguments[0];
            el.dispatchEvent(new Event('change', { bubbles: true }));
            el.dispatchEvent(new KeyboardEvent('keyup', {'key': 'a'}));
        """, element)
        
        logger.info(f"[TYPER] Typed {len(text)} chars via JS injection")
        return True
    
    def _inject_char(self, element, char: str):
        """Inject a single character via JS."""
        self.driver.execute_script("""
            const el = arguments[0];
            const char = arguments[1];
            el.textContent += char;
            el.dispatchEvent(new Event('input', { bubbles: true }));
        """, element, char)
    
    def _delete_last_char(self, element):
        """Delete last character via JS (for typo correction)."""
        self.driver.execute_script("""
            const el = arguments[0];
            el.textContent = el.textContent.slice(0, -1);
            el.dispatchEvent(new Event('input', { bubbles: true }));
        """, element)
    
    # =========== SYNC METHODS (for non-async code) ===========
    
    def type_text_sync(
        self, 
        element, 
        text: str, 
        clear_first: bool = True,
        click_first: bool = True
    ) -> bool:
        """
        Type text into element with human-like behavior (sync version).
        
        Uses time.sleep() instead of asyncio.sleep().
        """
        try:
            element_type = self._detect_element_type(element)
            logger.debug(f"[TYPER] Element type: {element_type}")
            
            if click_first:
                self.driver.execute_script("arguments[0].click();", element)
                time.sleep(0.1)
            
            if clear_first:
                self._clear_element_sync(element, element_type)
            
            if element_type == 'input':
                return self._type_via_send_keys_sync(element, text)
            else:
                return self._type_via_js_sync(element, text)
                
        except Exception as e:
            logger.error(f"[TYPER] Typing failed: {e}")
            return False
    
    def _clear_element_sync(self, element, element_type: str):
        """Clear element content (sync)."""
        if element_type == 'input':
            element.clear()
        else:
            self.driver.execute_script("arguments[0].textContent = '';", element)
        time.sleep(0.05)
    
    def _type_via_send_keys_sync(self, element, text: str) -> bool:
        """Type using Selenium send_keys (sync version)."""
        from selenium.webdriver.common.keys import Keys
        
        for i, char in enumerate(text):
            if self._should_typo() and i > 0:
                typo_char = self._get_typo_char()
                element.send_keys(typo_char)
                time.sleep(self._get_char_delay(typo_char))
                element.send_keys(Keys.BACKSPACE)
                time.sleep(0.05)
            
            element.send_keys(char)
            time.sleep(self._get_char_delay(char))
            
            if self._should_hesitate():
                hesitate = random.uniform(BASE_HESITATION_MIN, BASE_HESITATION_MAX)
                time.sleep(hesitate)
        
        logger.info(f"[TYPER] Typed {len(text)} chars via send_keys (sync)")
        return True
    
    def _type_via_js_sync(self, element, text: str) -> bool:
        """Type using JS character injection (sync version)."""
        for i, char in enumerate(text):
            if self._should_typo() and i > 0:
                typo_char = self._get_typo_char()
                self._inject_char(element, typo_char)
                time.sleep(self._get_char_delay(typo_char))
                self._delete_last_char(element)
                time.sleep(0.05)
            
            self._inject_char(element, char)
            time.sleep(self._get_char_delay(char))
            
            if self._should_hesitate():
                hesitate = random.uniform(BASE_HESITATION_MIN, BASE_HESITATION_MAX)
                time.sleep(hesitate)
        
        self.driver.execute_script("""
            const el = arguments[0];
            el.dispatchEvent(new Event('change', { bubbles: true }));
            el.dispatchEvent(new KeyboardEvent('keyup', {'key': 'a'}));
        """, element)
        
        logger.info(f"[TYPER] Typed {len(text)} chars via JS injection (sync)")
        return True


# Convenience function for one-off usage
def get_typer(driver, speed_multiplier: Optional[float] = None) -> FoundupsTyper:
    """Get a FoundupsTyper instance."""
    return FoundupsTyper(driver, speed_multiplier)
