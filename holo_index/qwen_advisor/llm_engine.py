"""
Qwen LLM Inference Engine for HoloIndex

This module provides local LLM inference using llama-cpp-python
to power the Qwen advisor with actual AI capabilities instead of
rule-based processing.

NAVIGATION: Local LLM inference engine for Qwen advisor
→ Called by: qwen_advisor/advisor.py
→ Dependencies: llama-cpp-python, qwen-coder-1.5b.gguf
→ Config: qwen_advisor/config.py
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class QwenInferenceEngine:
    """
    Local LLM inference engine using llama-cpp-python.

    Loads and runs the Qwen 1.5B coder model for intelligent code analysis
    and guidance generation.
    """

    def __init__(
        self,
        model_path: Path,
        max_tokens: int = 512,
        temperature: float = 0.2,
        context_length: int = 2048
    ):
        """
        Initialize the Qwen inference engine.

        Args:
            model_path: Path to the GGUF model file
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0 = deterministic, 1.0 = creative)
            context_length: Maximum context window size
        """
        self.model_path = model_path
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.context_length = context_length
        self.llm = None
        self._initialized = False

    def initialize(self) -> bool:
        """
        Initialize the LLM model.

        Returns:
            bool: True if initialization successful, False otherwise
        """
        if self._initialized:
            return True

        try:
            # Import llama-cpp-python here to avoid import errors if not installed
            from llama_cpp import Llama

            logger.info(f"Loading Qwen model from {self.model_path}")

            # Initialize the model with optimized settings for 1.5B model
            self.llm = Llama(
                model_path=str(self.model_path),
                n_ctx=self.context_length,
                n_threads=4,  # Use 4 CPU threads
                n_gpu_layers=0,  # CPU-only for now (GGUF models work well on CPU)
                verbose=False  # Reduce logging noise
            )

            self._initialized = True
            logger.info("Qwen model loaded successfully")
            return True

        except ImportError as e:
            logger.error(f"llama-cpp-python not installed: {e}")
            return False
        except Exception as e:
            logger.error(f"Failed to load Qwen model: {e}")
            return False

    def generate_response(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Generate a response from the Qwen model.

        Args:
            prompt: The input prompt
            system_prompt: Optional system prompt to set context
            **kwargs: Additional generation parameters

        Returns:
            str: Generated response
        """
        if not self.initialize():
            return "Error: Qwen model not available"

        try:
            # Combine system prompt and user prompt
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{prompt}"

            # Generate response
            response = self.llm(
                full_prompt,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                stop=["\n\n", "###"],  # Common stop sequences
                echo=False,  # Don't include the prompt in output
                **kwargs
            )

            # Extract the generated text
            if isinstance(response, dict) and 'choices' in response:
                # OpenAI-style response format
                return response['choices'][0]['text'].strip()
            elif isinstance(response, list) and len(response) > 0:
                # Direct token list response
                return response[0]['text'].strip()
            else:
                # Raw text response
                return str(response).strip()

        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return f"Error: Failed to generate response - {e}"

    def analyze_code_context(
        self,
        query: str,
        code_snippets: list[str],
        wsp_guidance: list[str]
    ) -> Dict[str, Any]:
        """
        Analyze code context and provide intelligent guidance.

        Args:
            query: User's search query
            code_snippets: Relevant code snippets found
            wsp_guidance: WSP protocol guidance

        Returns:
            dict: Analysis results with guidance and recommendations
        """
        if not self.initialize():
            return {
                "guidance": "Qwen model unavailable - using fallback analysis",
                "confidence": 0.0,
                "recommendations": []
            }

        # Build analysis prompt
        prompt = f"""
You are an expert software architect analyzing a code search query.

Query: {query}

Relevant Code Found:
{chr(10).join(f"- {snippet[:200]}..." for snippet in code_snippets[:3])}

WSP Protocol Guidance:
{chr(10).join(f"- {guidance}" for guidance in wsp_guidance[:3])}

Provide a brief, actionable analysis of what this code means and any recommendations.
Focus on:
1. What functionality this code provides
2. Whether it solves the user's problem
3. Any WSP compliance considerations
4. Suggestions for next steps

Keep response under 200 words.
"""

        response = self.generate_response(prompt)

        return {
            "guidance": response,
            "confidence": 0.8,  # High confidence for LLM analysis
            "recommendations": self._extract_recommendations(response),
            "model_used": "qwen-coder-1.5b"
        }

    def _extract_recommendations(self, response: str) -> list[str]:
        """
        Extract actionable recommendations from the LLM response.

        Args:
            response: LLM generated response

        Returns:
            list: List of recommendations
        """
        # Simple extraction - look for bullet points or numbered lists
        lines = response.split('\n')
        recommendations = []

        for line in lines:
            line = line.strip()
            if line.startswith(('- ', '• ', '* ', '1. ', '2. ', '3. ')):
                # Clean up the recommendation text
                rec = line.lstrip('- •*123456789. ').strip()
                if rec and len(rec) > 10:  # Filter out very short items
                    recommendations.append(rec)

        return recommendations[:5]  # Limit to 5 recommendations

    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the loaded model.

        Returns:
            dict: Model information
        """
        if not self._initialized:
            return {"status": "not_initialized"}

        return {
            "status": "loaded",
            "model_path": str(self.model_path),
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "context_length": self.context_length,
            "model_size": f"{self.model_path.stat().st_size / (1024*1024):.1f}MB"
        }
