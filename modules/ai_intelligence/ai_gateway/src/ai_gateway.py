#!/usr/bin/env python3
"""
FoundUps AI Gateway - Unified AI Service Access
===============================================

Provides intelligent routing, fallback, and load balancing across multiple AI providers.

Features:
- Automatic fallback between providers
- Task-specific model selection
- Cost optimization
- Load balancing
- Usage monitoring

Usage:
    from ai_gateway import AIGateway

    gateway = AIGateway()
    response = gateway.call_with_fallback("Analyze this code", task_type="code_review")
"""

import os
import time
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import requests
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class GatewayResult:
    """Result from AI gateway call"""
    response: str
    provider: str
    model: str
    duration: float
    cost_estimate: float
    success: bool


@dataclass
class ProviderConfig:
    """Configuration for AI provider"""
    name: str
    api_key: Optional[str]
    base_url: str
    models: Dict[str, str]  # task_type -> model_name
    cost_per_token: float
    rate_limit: int  # requests per minute
    timeout: int = 30


class AIGateway:
    """
    AI Gateway for unified access to multiple AI providers.

    Provides intelligent routing, automatic fallback, and cost optimization
    across OpenAI, Anthropic, Grok, and Google Gemini.
    """

    def __init__(self, gateway_key: Optional[str] = None):
        """
        Initialize AI Gateway

        Args:
            gateway_key: Primary gateway API key (optional)
        """
        self.gateway_key = gateway_key or os.getenv('AI_GATEWAY_API_KEY')

        # Configure AI providers
        self.providers = self._setup_providers()

        # Usage tracking
        self.usage_stats = {
            'calls': 0,
            'failures': 0,
            'provider_usage': {},
            'task_distribution': {}
        }

        logger.info(f"[AI-GATEWAY] Initialized with {len([p for p in self.providers.values() if p.api_key])} active providers")

    def _get_env_int(self, name: str, default: int) -> int:
        """Read an int from env with a safe fallback."""
        value = os.getenv(name)
        if value is None or value == "":
            return default
        try:
            return int(value)
        except ValueError:
            logger.warning(f"[AI-GATEWAY] Invalid {name} value: {value}")
            return default

    def _get_env_float(self, name: str, default: float) -> float:
        """Read a float from env with a safe fallback."""
        value = os.getenv(name)
        if value is None or value == "":
            return default
        try:
            return float(value)
        except ValueError:
            logger.warning(f"[AI-GATEWAY] Invalid {name} value: {value}")
            return default

    def _get_provider_max_tokens(self, provider_name: str, default: int) -> int:
        """Resolve max_tokens for provider from env overrides."""
        provider_key = f"{provider_name.upper()}_MAX_TOKENS"
        if os.getenv(provider_key):
            return self._get_env_int(provider_key, default)
        if os.getenv("MAX_TOKENS"):
            return self._get_env_int("MAX_TOKENS", default)
        return self._get_env_int("LLM_MAX_TOKENS", default)

    def _get_provider_temperature(self, provider_name: str, default: float) -> float:
        """Resolve temperature for provider from env overrides."""
        provider_key = f"{provider_name.upper()}_TEMPERATURE"
        if os.getenv(provider_key):
            return self._get_env_float(provider_key, default)
        if os.getenv("TEMPERATURE"):
            return self._get_env_float("TEMPERATURE", default)
        return self._get_env_float("LLM_TEMPERATURE", default)

    def _setup_providers(self) -> Dict[str, ProviderConfig]:
        """Set up AI provider configurations"""

        return {
            'openai': ProviderConfig(
                name='openai',
                api_key=os.getenv('OPENAI_API_KEY'),
                base_url='https://api.openai.com/v1',
                models={
                    'code_review': 'gpt-4',
                    'analysis': 'gpt-4',
                    'creative': 'gpt-3.5-turbo',
                    'quick': 'gpt-3.5-turbo'
                },
                cost_per_token=0.002,
                rate_limit=60
            ),

            'anthropic': ProviderConfig(
                name='anthropic',
                api_key=os.getenv('ANTHROPIC_API_KEY'),
                base_url='https://api.anthropic.com/v1',
                models={
                    'code_review': 'claude-3-opus-20240229',
                    'creative': 'claude-3-haiku-20240307',
                    'analysis': 'claude-3-sonnet-20240229',
                    'quick': 'claude-3-haiku-20240307'
                },
                cost_per_token=0.015,
                rate_limit=50
            ),

            'grok': ProviderConfig(
                name='grok',
                api_key=os.getenv('GROK_API_KEY') or os.getenv('XAI_API_KEY'),
                base_url='https://api.x.ai/v1',
                models={
                    'code_review': 'grok-3',
                    'analysis': 'grok-3',
                    'creative': 'grok-3',
                    'quick': 'grok-3'
                },
                cost_per_token=0.001,
                rate_limit=30
            ),

            'gemini': ProviderConfig(
                name='gemini',
                api_key=os.getenv('GEMINI_API_KEY'),
                base_url='https://generativelanguage.googleapis.com/v1',
                models={
                    'code_review': 'gemini-pro',
                    'analysis': 'gemini-pro',
                    'creative': 'gemini-pro',
                    'quick': 'gemini-pro-vision'  # Cheaper option
                },
                cost_per_token=0.0005,
                rate_limit=60
            )
        }

    def call_with_fallback(self, prompt: str, task_type: str = "general",
                          max_retries: int = 3) -> GatewayResult:
        """
        Call AI providers with automatic fallback

        Args:
            prompt: The prompt to send to AI
            task_type: Type of task (code_review, analysis, creative, quick)
            max_retries: Maximum number of provider retries

        Returns:
            GatewayResult with response and metadata
        """
        self.usage_stats['calls'] += 1
        self.usage_stats['task_distribution'][task_type] = \
            self.usage_stats['task_distribution'].get(task_type, 0) + 1

        # Get provider priority order for this task
        provider_order = self._get_provider_priority(task_type)

        for provider_name in provider_order:
            provider = self.providers[provider_name]

            if not provider.api_key:
                continue

            try:
                start_time = time.time()
                response = self._call_provider(provider, prompt, task_type)
                duration = time.time() - start_time

                # Estimate cost (rough calculation)
                cost_estimate = len(prompt.split()) * provider.cost_per_token

                # Track usage
                self.usage_stats['provider_usage'][provider_name] = \
                    self.usage_stats['provider_usage'].get(provider_name, 0) + 1

                return GatewayResult(
                    response=response,
                    provider=provider_name,
                    model=provider.models.get(task_type, 'default'),
                    duration=duration,
                    cost_estimate=cost_estimate,
                    success=True
                )

            except Exception as e:
                logger.warning(f"[U+26A0]️ {provider_name} failed: {e}")
                self.usage_stats['failures'] += 1
                continue

        # All providers failed
        return GatewayResult(
            response="",
            provider="none",
            model="",
            duration=0,
            cost_estimate=0,
            success=False
        )

    def call_optimized(self, prompt: str, task_type: str = "general") -> GatewayResult:
        """
        Call the most cost-effective provider available for the task

        Args:
            prompt: The prompt to send
            task_type: Type of task

        Returns:
            GatewayResult from cheapest available provider
        """
        # Sort providers by cost for this task
        available_providers = [
            (name, config) for name, config in self.providers.items()
            if config.api_key
        ]

        # Sort by cost_per_token ascending (cheapest first)
        available_providers.sort(key=lambda x: x[1].cost_per_token)

        for provider_name, provider in available_providers:
            try:
                start_time = time.time()
                response = self._call_provider(provider, prompt, task_type)
                duration = time.time() - start_time

                cost_estimate = len(prompt.split()) * provider.cost_per_token

                return GatewayResult(
                    response=response,
                    provider=provider_name,
                    model=provider.models.get(task_type, 'default'),
                    duration=duration,
                    cost_estimate=cost_estimate,
                    success=True
                )

            except Exception as e:
                logger.debug(f"Cost-optimized {provider_name} failed: {e}")
                continue

        return GatewayResult("", "none", "", 0, 0, False)

    def _get_provider_priority(self, task_type: str) -> List[str]:
        """Get provider priority order for task type"""

        # Task-specific routing preferences
        task_routing = {
            'code_review': ['openai', 'anthropic', 'grok', 'gemini'],  # Best for code
            'analysis': ['openai', 'grok', 'anthropic', 'gemini'],     # Analysis focused
            'creative': ['anthropic', 'openai', 'grok', 'gemini'],     # Creative tasks
            'quick': ['grok', 'gemini', 'openai', 'anthropic']         # Fast responses
        }

        return task_routing.get(task_type, ['openai', 'anthropic', 'grok', 'gemini'])

    def _call_provider(self, provider: ProviderConfig, prompt: str, task_type: str) -> str:
        """Call specific AI provider"""

        model = provider.models.get(task_type, provider.models.get('quick', 'default'))

        if provider.name == 'openai':
            return self._call_openai(provider, prompt, model)
        elif provider.name == 'anthropic':
            return self._call_anthropic(provider, prompt, model)
        elif provider.name == 'grok':
            return self._call_grok(provider, prompt, model)
        elif provider.name == 'gemini':
            return self._call_gemini(provider, prompt, model)
        else:
            raise ValueError(f"Unknown provider: {provider.name}")

    def _call_openai(self, provider: ProviderConfig, prompt: str, model: str) -> str:
        """Call OpenAI API"""
        max_tokens = self._get_provider_max_tokens(provider.name, 1000)
        temperature = self._get_provider_temperature(provider.name, 0.7)
        headers = {
            'Authorization': f'Bearer {provider.api_key}',
            'Content-Type': 'application/json'
        }

        data = {
            'model': model,
            'messages': [{'role': 'user', 'content': prompt}],
            'max_tokens': max_tokens,
            'temperature': temperature
        }

        response = requests.post(
            f"{provider.base_url}/chat/completions",
            headers=headers,
            json=data,
            timeout=provider.timeout
        )
        response.raise_for_status()

        result = response.json()
        return result['choices'][0]['message']['content'].strip()

    def _call_anthropic(self, provider: ProviderConfig, prompt: str, model: str) -> str:
        """Call Anthropic API"""
        max_tokens = self._get_provider_max_tokens(provider.name, 1000)
        temperature = self._get_provider_temperature(provider.name, 0.7)
        headers = {
            'x-api-key': provider.api_key,
            'Content-Type': 'application/json',
            'anthropic-version': '2023-06-01'
        }

        data = {
            'model': model,
            'max_tokens': max_tokens,
            'temperature': temperature,
            'messages': [{'role': 'user', 'content': prompt}]
        }

        response = requests.post(
            f"{provider.base_url}/messages",
            headers=headers,
            json=data,
            timeout=provider.timeout
        )
        response.raise_for_status()

        result = response.json()
        return result['content'][0]['text'].strip()

    def _call_grok(self, provider: ProviderConfig, prompt: str, model: str) -> str:
        """Call Grok API"""
        max_tokens = self._get_provider_max_tokens(provider.name, 1000)
        temperature = self._get_provider_temperature(provider.name, 0.7)
        headers = {
            'Authorization': f'Bearer {provider.api_key}',
            'Content-Type': 'application/json'
        }

        data = {
            'model': model,
            'messages': [{'role': 'user', 'content': prompt}],
            'max_tokens': max_tokens,
            'temperature': temperature
        }

        response = requests.post(
            f"{provider.base_url}/chat/completions",
            headers=headers,
            json=data,
            timeout=provider.timeout
        )
        response.raise_for_status()

        result = response.json()
        return result['choices'][0]['message']['content'].strip()

    def _call_gemini(self, provider: ProviderConfig, prompt: str, model: str) -> str:
        """Call Google Gemini API"""
        max_tokens = self._get_provider_max_tokens(provider.name, 1000)
        temperature = self._get_provider_temperature(provider.name, 0.7)
        data = {
            'contents': [{
                'parts': [{'text': prompt}]
            }],
            'generationConfig': {
                'maxOutputTokens': max_tokens,
                'temperature': temperature
            }
        }

        params = {
            'key': provider.api_key
        }

        response = requests.post(
            f"{provider.base_url}/models/{model}:generateContent",
            params=params,
            json=data,
            timeout=provider.timeout
        )
        response.raise_for_status()

        result = response.json()
        return result['candidates'][0]['content']['parts'][0]['text'].strip()

    def get_usage_stats(self) -> Dict[str, Any]:
        """Get usage statistics"""
        return {
            'total_calls': self.usage_stats['calls'],
            'failure_rate': self.usage_stats['failures'] / max(self.usage_stats['calls'], 1),
            'provider_usage': self.usage_stats['provider_usage'],
            'task_distribution': self.usage_stats['task_distribution']
        }

    def get_available_providers(self) -> List[str]:
        """Get list of providers with valid API keys"""
        return [name for name, config in self.providers.items() if config.api_key]


# Convenience functions
def quick_call(prompt: str, task_type: str = "general") -> str:
    """Quick gateway call without creating instance"""
    gateway = AIGateway()
    result = gateway.call_with_fallback(prompt, task_type)
    return result.response if result.success else "AI call failed"


def test_gateway() -> bool:
    """Test gateway functionality"""
    gateway = AIGateway()

    # Test basic connectivity
    providers = gateway.get_available_providers()
    if not providers:
        print("[ERROR] No AI providers configured")
        return False

    print(f"[SUCCESS] Found {len(providers)} configured providers: {', '.join(providers)}")

    # Test simple call
    try:
        result = gateway.call_with_fallback("Hello, test message", "quick")
        if result.success:
            print(f"[SUCCESS] Gateway test successful - {result.provider} responded in {result.duration:.2f}s")
            return True
        else:
            print("[ERROR] Gateway test failed - no providers responded")
            return False
    except Exception as e:
        print(f"[ERROR] Gateway test error: {e}")
        return False


if __name__ == '__main__':
    # CLI interface
    import argparse

    parser = argparse.ArgumentParser(description='FoundUps AI Gateway')
    parser.add_argument('--test', action='store_true', help='Test gateway connectivity')
    parser.add_argument('--call', help='Make a test call')
    parser.add_argument('--task-type', default='general', help='Task type for call')
    parser.add_argument('--stats', action='store_true', help='Show usage statistics')

    args = parser.parse_args()

    gateway = AIGateway()

    if args.test:
        success = test_gateway()
        exit(0 if success else 1)

    elif args.call:
        result = gateway.call_with_fallback(args.call, args.task_type)
        if result.success:
            print(f"[AI] {result.provider} ({result.model}): {result.response}")
            print(f"[TIME] {result.duration:.2f}s | [COST] ~${result.cost_estimate:.4f}")
        else:
            print("[ERROR] Call failed - no providers available")
            exit(1)

    elif args.stats:
        stats = gateway.get_usage_stats()
        print("[STATS] AI Gateway Usage Statistics:")
        print(f"   Total calls: {stats['total_calls']}")
        print(f"   Failure rate: {stats['failure_rate']:.2%}")
        print(f"   Provider usage: {stats['provider_usage']}")
        print(f"   Task distribution: {stats['task_distribution']}")

    else:
        parser.print_help()
