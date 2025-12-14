import logging
import json
import asyncio
import time
from typing import Dict, Any, Optional
from dataclasses import dataclass

from modules.platform_integration.social_media_orchestrator.src.gemini_vision_analyzer import GeminiVisionAnalyzer

logger = logging.getLogger(__name__)

@dataclass
class VisionResult:
    success: bool
    confidence: float
    duration_ms: int
    screenshot_before: Optional[str] = None
    error: Optional[str] = None

class GeminiVisionBridge:
    """
    Adaptor to use Gemini Vision (Tier 2) as a drop-in replacement for UI-TARS.
    Implements the execute_action interface required by ActionRouter.
    """
    
    def __init__(self, driver, feedback_mode: bool = False):
        self.driver = driver
        self.feedback_mode = feedback_mode
        self.analyzer = GeminiVisionAnalyzer()
        logger.info(f"[GEMINI-BRIDGE] Initialized (Feedback Mode: {feedback_mode})")
        
    def _verify_step_012(self, step_name: str, question: str) -> bool:
        """
        012 Protocol: User verification loop.
        """
        if not self.feedback_mode:
            return True
            
        try:
            import tkinter as tk
            from tkinter import messagebox, simpledialog
            
            # Ensure root window is hidden and clean
            root = tk.Tk()
            root.withdraw()
            root.attributes('-topmost', True)
            
            print(f"\n[012 FEEDBACK] {step_name}: {question}")
            success = messagebox.askyesno("012 Feedback", f"{step_name}\n\n{question}")
            
            if not success:
                comment = simpledialog.askstring("Issue Report", "What went wrong?")
                logger.warning(f"[012 FAIL] {step_name}: {comment}")
            
            root.destroy()
            return success
        except Exception as e:
            logger.error(f"[012 ERROR] GUI failed: {e}")
            return True # Fail open if GUI breaks

    async def connect(self):
        """Mock connect method for compatibility"""
        pass
        
    async def close(self):
        """Mock close method for compatibility"""
        pass

    async def execute_action(self, action: str, description: str, context: Dict[str, Any], timeout: int = 30) -> VisionResult:
        """
        Execute an action using Gemini Vision analysis + Selenium JS execution.
        """
        # 012 PRE-CHECK
        if not self._verify_step_012(f"Pre-Action: {action}", f"Allow agent to: {description}?"):
             return VisionResult(False, 0.0, 0, error="User rejected action (012)")

        start_time = time.time()
        
        try:
            # 1. Take Screenshot
            if not self.driver:
                return VisionResult(False, 0.0, 0, error="No driver available")
                
            screenshot_bytes = self.driver.get_screenshot_as_png()
            
            # 2. Analyze with Gemini
            logger.info(f"[GEMINI-BRIDGE] Analyzing UI for action: {action} - {description}")
            
            # Use the new generic finder method
            result = self.analyzer.find_element_by_description(screenshot_bytes, description)
            
            if result.get("error"):
                return VisionResult(False, 0.0, int((time.time() - start_time)*1000), error=result["error"])
                
            if not result.get("found"):
                # 012 VISUAL CHECK
                self._verify_step_012("Vision Failure", f"Agent could not find: {description}. correct?")
                return VisionResult(False, 0.0, int((time.time() - start_time)*1000), error="Element not found by Vision")
                
            # 3. Execute Action (JS Click)
            selectors = result.get("suggested_selectors", [])
            success = False
            from selenium.webdriver.common.by import By
            
            if selectors:
                # 012 CONFIRM SELECTOR (Optional? Maybe too granular, let's stick to outcome)
                pass

            for selector in selectors:
                try:
                    logger.info(f"[GEMINI-BRIDGE] Trying selector: {selector}")
                    elements = self.driver.find_elements(By.XPATH, selector)
                    
                    if elements:
                        element = elements[0]
                        
                        # Scroll and Highlight
                        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                        self.driver.execute_script("arguments[0].style.border = '3px solid red';", element)
                        await asyncio.sleep(0.5)
                        
                        # JS Click (Robust)
                        if action == 'type_text':
                            text_to_type = context.get('text', '')
                            logger.info(f"[GEMINI-BRIDGE] Typing text: {text_to_type}")
                            element.click() # Focus first
                            element.clear()
                            element.send_keys(text_to_type)
                        else:
                            self.driver.execute_script("arguments[0].click();", element)
                        
                        success = True
                        break
                except Exception as e:
                    logger.warning(f"[GEMINI-BRIDGE] Selector failed {selector}: {e}")
                    continue
            
            # 012 POST-CHECK
            if self.feedback_mode:
                if success:
                    self._verify_step_012(f"Post-Action: {action}", f"Agent successfully performed: {description}. Confirm?")
                else:
                    self._verify_step_012(f"Action Failed", f"Agent failed to: {description}. Correct?")

            duration = int((time.time() - start_time) * 1000)
            return VisionResult(
                success=success,
                confidence=0.9 if success else 0.0, # Mock confidence
                duration_ms=duration,
                error=None if success else "All selectors failed"
            )

        except Exception as e:
            duration = int((time.time() - start_time) * 1000)
            return VisionResult(False, 0.0, duration, error=str(e))
