#!/usr/bin/env python3
"""
Gemini Vision Analyzer for Social Media UI
Uses Google AI Studio API (FREE) for visual understanding
"""

import os
import base64
import json
from typing import Dict, Any
from dotenv import load_dotenv

class GeminiVisionAnalyzer:
    """Analyze posting UI using Gemini Vision API"""

    def __init__(self, api_key: str = None):
        load_dotenv()
        self.api_key = api_key or os.getenv('GOOGLE_AISTUDIO_API_KEY')

        if not self.api_key:
            print("[GEMINI-VISION] No API key configured; skipping vision analysis")
            self.model = None
            return

        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-2.5-flash')  # 2.0-flash retiring Mar 2026; 2.5-flash recommended
            print("[GEMINI-VISION] Initialized with AI Studio API")
        except ImportError:
            print("[ERROR] Install: pip install google-generativeai")
            self.model = None
        except Exception as e:
            print(f"[GEMINI-VISION] Initialization failed: {e}")
            self.model = None

    def analyze_posting_ui(self, screenshot_bytes: bytes) -> Dict[str, Any]:
        """
        Analyze posting UI screenshot

        Args:
            screenshot_bytes: PNG screenshot from Selenium

        Returns:
            Analysis with button locations, errors, UI state
        """
        if not self.model:
            return {"error": "Gemini not initialized"}

        try:
            import io
            from PIL import Image
            img = Image.open(io.BytesIO(screenshot_bytes))

            prompt = """Analyze this social media posting interface.

Identify:
1. Post button location and state (enabled/disabled)
2. Text area location and state (empty/filled)
3. Any error messages visible
4. Character count if visible
5. Any UI elements blocking posting
6. Success indicators (post published, etc.)

Return JSON format:
{
  "post_button": {"found": true/false, "enabled": true/false, "location": "description"},
  "text_area": {"found": true/false, "has_text": true/false},
  "errors": ["error1", "error2"],
  "success_indicators": ["indicator1"],
  "character_count": number or null,
  "ui_state": "ready_to_post" or "error" or "posted"
}
"""

            # SAFETY: Enforce 30s timeout to prevent hanging calls
            # SAFETY: Heartbeat/Governance check would go here in a full loop
            response = self.model.generate_content(
                [prompt, img],
                request_options={"timeout": 30}
            )

            # Parse response
            try:
                analysis = json.loads(response.text)
                return analysis
            except:
                return {"raw_response": response.text}

        except Exception as e:
            return {"error": str(e)}

    def detect_ui_changes(self, screenshot_bytes: bytes, known_ui_version: str = "2024-01") -> Dict[str, Any]:
        """
        Detect if UI has changed from known version

        Args:
            screenshot_bytes: Current UI screenshot
            known_ui_version: Last known UI version

        Returns:
            Changes detected and updated selectors
        """
        if not self.model:
            return {"error": "Gemini not initialized"}

        try:
            import io
            from PIL import Image
            img = Image.open(io.BytesIO(screenshot_bytes, encoding="utf-8"))

            prompt = f"""Compare this social media UI to known version {known_ui_version}.

Detect:
1. New button locations
2. Changed element IDs
3. New UI patterns
4. Layout changes

Suggest specific, ROBUST Selenium selectors for:
- Post button
- Text area
- Error elements

IMPORTANT: This is a React application with dynamic class names.
- DO NOT use dynamic CSS classes (e.g. .sc-bdVaJa, .css-1a2b3c).
- PREFER 'aria-label' attributes (e.g. //button[@aria-label='Post']).
- PREFER text content (e.g. //button[contains(text(), 'Post')]).
- Use reliable ID attributes if they look static.

Return JSON with:
{{
  "ui_changed": true/false,
  "changes": ["change1", "change2"],
  "suggested_selectors": {{
    "post_button": ["//best_xpath_selector", "//alternative_xpath"],
    "text_area": ["//best_xpath_selector", "//alternative_xpath"]
  }}
}}
"""

            # SAFETY: Enforce 30s timeout
            response = self.model.generate_content(
                [prompt, img],
                request_options={"timeout": 30}
            )

            try:
                return json.loads(response.text)
            except:
                return {"raw_response": response.text}

        except Exception as e:
            return {"error": str(e)}

    def find_element_by_description(self, screenshot_bytes: bytes, description: str) -> Dict[str, Any]:
        """
        Find an element based on natural language description.
        Returns robust selectors (XPath/ARIA).
        """
        if not self.model:
            return {"error": "Gemini not initialized"}

        try:
            import io
            from PIL import Image
            img = Image.open(io.BytesIO(screenshot_bytes))

            prompt = f"""Find the element described as: "{description}".

            Analyze the UI and identify this element.
            
            Return JSON with:
            {{
              "found": true/false,
              "confidence": "high/medium/low",
              "reasoning": "why you think this is the element",
              "suggested_selectors": [
                "//xpath/to/element",
                "//button[@aria-label='...']"
              ]
            }}

            IMPORTANT:
            - PREFER 'aria-label' or text content.
            - AVOID dynamic CSS classes.
            - Return valid XPath selectors.
            """

            # SAFETY: Enforce 30s timeout
            response = self.model.generate_content(
                [prompt, img],
                request_options={"timeout": 30}
            )

            try:
                text = response.text.strip()
                if '```json' in text:
                    text = text.split('```json')[1].split('```')[0]
                elif '```' in text:
                    text = text.split('```')[1].split('```')[0]
                return json.loads(text)
            except:
                return {"raw_response": response.text, "error": "Failed to parse JSON"}

        except Exception as e:
            return {"error": str(e)}
