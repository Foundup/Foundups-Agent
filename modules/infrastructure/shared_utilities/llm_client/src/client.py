# -*- coding: utf-8 -*-
import sys
import io


import os
import google.generativeai as genai
from dotenv import load_dotenv

# === UTF-8 ENFORCEMENT (WSP 90) ===
# Prevent UnicodeEncodeError on Windows systems
# Only apply when running as main script, not during import
if __name__ == '__main__' and sys.platform.startswith('win'):
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except (OSError, ValueError):
        # Ignore if stdout/stderr already wrapped or closed
        pass
# === END UTF-8 ENFORCEMENT ===

class LLMClient:
    """
    A client for interacting with the Google Gemini API.
    """
    def __init__(self, api_key: str = None):
        """
        Initializes the LLMClient for Gemini.

        Args:
            api_key (str, optional): The Google API key. If not provided,
                                     it will be loaded from the GEMINI_API_KEY
                                     environment variable.
        """
        load_dotenv()
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("Google API key not found. Please set the GEMINI_API_KEY environment variable.")
        
        genai.configure(api_key=self.api_key)
        
        # Allow user to specify the model, with a fallback
        self.model_name = os.getenv("GEMINI_MODEL_NAME", "gemini-2.5-pro-preview-06-05")


    def generate_response(self, prompt: str, system_prompt: str = "You are a helpful assistant.") -> str:
        """
        Generates a response from the LLM.

        Args:
            prompt (str): The user's prompt.
            system_prompt (str): The system prompt to set the context for the assistant.

        Returns:
            str: The generated response from the LLM.
        """
        try:
            model_instance = genai.GenerativeModel(
                self.model_name,
                system_instruction=system_prompt
            )
            response = model_instance.generate_content(prompt)
            
            if not response.parts:
                 return "Error: The model returned an empty response, possibly due to safety filters."
            
            return response.text
            
        except Exception as e:
            print(f"An error occurred while communicating with the Gemini API: {e}")
            return f"Error: Could not get a response. {e}" 