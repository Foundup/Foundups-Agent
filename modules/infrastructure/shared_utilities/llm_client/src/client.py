# -*- coding: utf-8 -*-
import sys
import io
import os
import requests
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
    A client for interacting with the xAI Grok API.
    """
    def __init__(self, api_key: str = None):
        """
        Initializes the LLMClient for Grok.

        Args:
            api_key (str, optional): The Grok API key. If not provided,
                                     it will be loaded from GROK_API_KEY
                                     (preferred) or XAI_API_KEY.
        """
        load_dotenv()
        self._api_keys = [
            api_key,
            os.getenv("GROK_API_KEY"),
            os.getenv("XAI_API_KEY"),
        ]
        self._api_keys = [k for k in self._api_keys if k]
        if not self._api_keys:
            raise ValueError(
                "Grok API key not found. Please set GROK_API_KEY "
                "(preferred) or XAI_API_KEY."
            )
        self.api_key = self._api_keys[0]
        
        # Allow user to specify the model, with a fallback
        self.model_name = os.getenv("GROK_MODEL_NAME", "grok-3-latest")
        self.api_url = os.getenv("GROK_API_URL", "https://api.x.ai/v1/chat/completions")
        self.timeout = int(os.getenv("GROK_API_TIMEOUT", "30"))
        self.max_tokens = self._get_env_int(
            ["GROK_MAX_TOKENS", "MAX_TOKENS", "LLM_MAX_TOKENS"],
            256
        )
        self.temperature = self._get_env_float(
            ["GROK_TEMPERATURE", "TEMPERATURE", "LLM_TEMPERATURE"],
            0.7
        )

    def _get_env_int(self, names, default: int) -> int:
        """Return the first valid int value from env names."""
        for name in names:
            value = os.getenv(name)
            if value is None or value == "":
                continue
            try:
                return int(value)
            except ValueError:
                print(f"Invalid {name} value: {value}")
                break
        return default

    def _get_env_float(self, names, default: float) -> float:
        """Return the first valid float value from env names."""
        for name in names:
            value = os.getenv(name)
            if value is None or value == "":
                continue
            try:
                return float(value)
            except ValueError:
                print(f"Invalid {name} value: {value}")
                break
        return default

    def generate_response(self, prompt: str, system_prompt: str = "You are a helpful assistant.") -> str:
        """
        Generates a response from the LLM.

        Args:
            prompt (str): The user's prompt.
            system_prompt (str): The system prompt to set the context for the assistant.

        Returns:
            str: The generated response from the LLM.
        """
        last_error = None
        for idx, key in enumerate(self._api_keys):
            try:
                if key != self.api_key:
                    self.api_key = key

                messages = []
                if system_prompt:
                    messages.append({"role": "system", "content": system_prompt})
                messages.append({"role": "user", "content": prompt})

                request_data = {
                    "messages": messages,
                    "model": self.model_name,
                    "stream": False,
                    "temperature": self.temperature,
                    "max_tokens": self.max_tokens
                }

                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.api_key}"
                }

                response = requests.post(
                    self.api_url,
                    headers=headers,
                    json=request_data,
                    timeout=self.timeout
                )

                if response.status_code == 200:
                    response_data = response.json()
                    choices = response_data.get("choices", [])
                    if not choices:
                        return "Error: The model returned an empty response."
                    return choices[0]["message"]["content"]

                last_error = f"{response.status_code} {response.text}"
                error_text = response.text.lower()
                if response.status_code in (401, 403) or "api key" in error_text or "invalid" in error_text:
                    if idx < len(self._api_keys) - 1:
                        print("Grok API key invalid - trying fallback key.")
                        continue
                print(f"An error occurred while communicating with the Grok API: {response.text}")
                break
            except Exception as e:
                last_error = e
                error_text = str(e).lower()
                if "api key" in error_text or "api_key_invalid" in error_text:
                    if idx < len(self._api_keys) - 1:
                        print("Grok API key invalid - trying fallback key.")
                        continue
                print(f"An error occurred while communicating with the Grok API: {e}")
                break

        return f"Error: Could not get a response. {last_error}"
