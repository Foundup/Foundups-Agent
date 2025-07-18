"""
IDE FoundUps - Universal LLM Provider Manager

Manages multiple LLM providers with intelligent routing, health monitoring,
and cost optimization. Supports dynamic provider discovery and task-optimized selection.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Callable
from enum import Enum
from dataclasses import dataclass
from datetime import datetime, timedelta
import json
import time

try:
    # Integrate with existing LLM infrastructure
    from modules.infrastructure.llm_client.src.client import LLMClient
    from modules.ai_intelligence.rESP_o1o2.src.llm_connector import LLMConnector
    FOUNDUPS_LLM_AVAILABLE = True
except ImportError as e:
    logging.warning(f"FoundUps LLM infrastructure not available: {e}")
    FOUNDUPS_LLM_AVAILABLE = False

class TaskType(Enum):
    """LLM task type classification"""
    REASONING = "reasoning_tasks"
    CODE_GENERATION = "code_generation"
    CODE_ANALYSIS = "code_analysis"
    QUICK_RESPONSE = "quick_responses"
    DOCUMENTATION = "documentation_generation"
    DEBUGGING = "debugging_assistance"
    ARCHITECTURE = "architecture_design"
    TESTING = "test_generation"
    REFACTORING = "code_refactoring"
    CREATIVE = "creative_tasks"

class ProviderCapability(Enum):
    """Provider capability classification"""
    LOGICAL_REASONING = "logical_reasoning"
    CODE_UNDERSTANDING = "code_understanding"
    FAST_RESPONSE = "fast_response"
    LARGE_CONTEXT = "large_context"
    CREATIVE_WRITING = "creative_writing"
    MATHEMATICAL = "mathematical_reasoning"
    MULTILINGUAL = "multilingual_support"
    LOCAL_PROCESSING = "local_processing"

@dataclass
class ProviderMetrics:
    """Provider performance metrics"""
    name: str
    response_time: float
    success_rate: float
    cost_per_token: float
    quality_score: float
    availability: bool
    last_check: datetime
    total_requests: int
    failed_requests: int
    avg_tokens_per_request: float

@dataclass
class TaskRequirements:
    """Task requirements for provider selection"""
    task_type: TaskType
    complexity: str  # "low", "medium", "high"
    speed_priority: str  # "low", "medium", "high"
    accuracy_priority: str  # "low", "medium", "high"
    cost_sensitivity: str  # "low", "medium", "high"
    context_length: int
    specialized_domain: Optional[str] = None

class UniversalLLMProviderManager:
    """
    Universal LLM Provider Manager with intelligent routing and optimization.
    
    Manages multiple LLM providers without hardcoding specific names,
    using capability-based routing and performance optimization.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.providers = {}
        self.provider_metrics = {}
        self.task_history = []
        self.routing_rules = {}
        self.health_check_interval = 300  # 5 minutes
        self.last_health_check = datetime.now()
        
        # Initialize provider discovery and routing
        self._discover_available_providers()
        self._initialize_routing_rules()
        self._start_health_monitoring()
    
    def _discover_available_providers(self):
        """Dynamically discover available LLM providers"""
        discovered_providers = {}
        
        # Check FoundUps LLM infrastructure
        if FOUNDUPS_LLM_AVAILABLE:
            try:
                # Universal LLM client from infrastructure
                llm_client = LLMClient()
                discovered_providers["foundups_universal"] = {
                    "client": llm_client,
                    "type": "foundups_infrastructure",
                    "capabilities": [
                        ProviderCapability.LOGICAL_REASONING,
                        ProviderCapability.CODE_UNDERSTANDING,
                        ProviderCapability.LARGE_CONTEXT
                    ]
                }
                
                # rESP LLM connector with multi-provider support
                resp_connector = LLMConnector()
                discovered_providers["resp_multi_provider"] = {
                    "client": resp_connector,
                    "type": "multi_provider_connector",
                    "capabilities": [
                        ProviderCapability.LOGICAL_REASONING,
                        ProviderCapability.CODE_UNDERSTANDING,
                        ProviderCapability.FAST_RESPONSE,
                        ProviderCapability.CREATIVE_WRITING
                    ]
                }
                
                self.logger.info("FoundUps LLM infrastructure providers discovered")
                
            except Exception as e:
                self.logger.warning(f"Failed to initialize FoundUps LLM providers: {e}")
        
        # Dynamically discover external providers based on environment
        external_providers = self._discover_external_providers()
        discovered_providers.update(external_providers)
        
        self.providers = discovered_providers
        self._initialize_provider_metrics()
        
        self.logger.info(f"Discovered {len(self.providers)} LLM providers: {list(self.providers.keys())}")
    
    def _discover_external_providers(self) -> Dict[str, Any]:
        """Discover external LLM providers based on available credentials"""
        import os
        external_providers = {}
        
        # Provider discovery patterns - check for API keys without hardcoding names
        api_key_patterns = {
            "anthropic": ["ANTHROPIC_API_KEY", "CLAUDE_API_KEY"],
            "openai": ["OPENAI_API_KEY", "OPENAI_KEY"],
            "google": ["GOOGLE_API_KEY", "GEMINI_API_KEY"],
            "xai": ["GROK_API_KEY", "XAI_API_KEY"],
            "deepseek": ["DEEPSEEK_API_KEY", "DEEPSEEK_KEY"],
            "mistral": ["MISTRAL_API_KEY", "MISTRAL_KEY"],
            "cohere": ["COHERE_API_KEY", "CO_API_KEY"],
            "huggingface": ["HUGGINGFACE_API_KEY", "HF_API_KEY"]
        }
        
        for provider_family, key_variants in api_key_patterns.items():
            for key_name in key_variants:
                if os.getenv(key_name):
                    external_providers[f"{provider_family}_provider"] = {
                        "api_key": os.getenv(key_name),
                        "type": "external_api",
                        "family": provider_family,
                        "capabilities": self._infer_provider_capabilities(provider_family)
                    }
                    break
        
        # Check for local model availability
        if self._check_local_model_availability():
            external_providers["local_models"] = {
                "type": "local_processing",
                "capabilities": [
                    ProviderCapability.LOCAL_PROCESSING,
                    ProviderCapability.CODE_UNDERSTANDING,
                    ProviderCapability.FAST_RESPONSE
                ]
            }
        
        return external_providers
    
    def _infer_provider_capabilities(self, provider_family: str) -> List[ProviderCapability]:
        """Infer capabilities based on provider family characteristics"""
        capability_mapping = {
            "anthropic": [
                ProviderCapability.LOGICAL_REASONING,
                ProviderCapability.CODE_UNDERSTANDING,
                ProviderCapability.LARGE_CONTEXT,
                ProviderCapability.CREATIVE_WRITING
            ],
            "openai": [
                ProviderCapability.LOGICAL_REASONING,
                ProviderCapability.CODE_UNDERSTANDING,
                ProviderCapability.CREATIVE_WRITING,
                ProviderCapability.MULTILINGUAL
            ],
            "google": [
                ProviderCapability.FAST_RESPONSE,
                ProviderCapability.MULTILINGUAL,
                ProviderCapability.MATHEMATICAL,
                ProviderCapability.LARGE_CONTEXT
            ],
            "xai": [
                ProviderCapability.FAST_RESPONSE,
                ProviderCapability.CREATIVE_WRITING,
                ProviderCapability.CODE_UNDERSTANDING
            ],
            "deepseek": [
                ProviderCapability.CODE_UNDERSTANDING,
                ProviderCapability.LOGICAL_REASONING,
                ProviderCapability.FAST_RESPONSE
            ],
            "mistral": [
                ProviderCapability.FAST_RESPONSE,
                ProviderCapability.MULTILINGUAL,
                ProviderCapability.CODE_UNDERSTANDING
            ],
            "cohere": [
                ProviderCapability.FAST_RESPONSE,
                ProviderCapability.CREATIVE_WRITING
            ],
            "huggingface": [
                ProviderCapability.LOCAL_PROCESSING,
                ProviderCapability.MULTILINGUAL
            ]
        }
        
        return capability_mapping.get(provider_family, [ProviderCapability.LOGICAL_REASONING])
    
    def _check_local_model_availability(self) -> bool:
        """Check if local models are available"""
        try:
            # Check for common local model frameworks
            import torch
            return True
        except ImportError:
            pass
        
        try:
            import transformers
            return True
        except ImportError:
            pass
        
        return False
    
    def _initialize_routing_rules(self):
        """Initialize intelligent routing rules based on task types"""
        self.routing_rules = {
            TaskType.REASONING: {
                "preferred_capabilities": [
                    ProviderCapability.LOGICAL_REASONING,
                    ProviderCapability.LARGE_CONTEXT
                ],
                "weight_factors": {
                    "accuracy": 0.5,
                    "speed": 0.2,
                    "cost": 0.3
                }
            },
            TaskType.CODE_GENERATION: {
                "preferred_capabilities": [
                    ProviderCapability.CODE_UNDERSTANDING,
                    ProviderCapability.LOGICAL_REASONING
                ],
                "weight_factors": {
                    "accuracy": 0.6,
                    "speed": 0.3,
                    "cost": 0.1
                }
            },
            TaskType.QUICK_RESPONSE: {
                "preferred_capabilities": [
                    ProviderCapability.FAST_RESPONSE
                ],
                "weight_factors": {
                    "accuracy": 0.2,
                    "speed": 0.7,
                    "cost": 0.1
                }
            },
            TaskType.CREATIVE: {
                "preferred_capabilities": [
                    ProviderCapability.CREATIVE_WRITING
                ],
                "weight_factors": {
                    "accuracy": 0.4,
                    "speed": 0.3,
                    "cost": 0.3
                }
            }
        }
    
    def _initialize_provider_metrics(self):
        """Initialize metrics tracking for all providers"""
        for provider_name in self.providers.keys():
            self.provider_metrics[provider_name] = ProviderMetrics(
                name=provider_name,
                response_time=1.0,  # Default 1 second
                success_rate=0.95,  # Default 95% success rate
                cost_per_token=0.001,  # Default cost
                quality_score=0.8,  # Default quality
                availability=True,
                last_check=datetime.now(),
                total_requests=0,
                failed_requests=0,
                avg_tokens_per_request=100
            )
    
    async def select_optimal_provider(self, requirements: TaskRequirements) -> Optional[str]:
        """
        Select optimal provider based on task requirements and current metrics.
        
        Args:
            requirements: Task requirements specification
            
        Returns:
            Name of optimal provider or None if none available
        """
        if not self.providers:
            self.logger.warning("No providers available for selection")
            return None
        
        # Check if health monitoring is needed
        await self._check_health_monitoring()
        
        # Score all providers for this task
        provider_scores = {}
        
        for provider_name, provider_info in self.providers.items():
            if not self.provider_metrics[provider_name].availability:
                continue
            
            score = self._calculate_provider_score(provider_name, provider_info, requirements)
            provider_scores[provider_name] = score
        
        if not provider_scores:
            self.logger.warning("No available providers for task")
            return None
        
        # Select provider with highest score
        optimal_provider = max(provider_scores, key=provider_scores.get)
        
        self.logger.info(f"Selected optimal provider: {optimal_provider} (score: {provider_scores[optimal_provider]:.3f})")
        
        return optimal_provider
    
    def _calculate_provider_score(self, provider_name: str, provider_info: Dict[str, Any], requirements: TaskRequirements) -> float:
        """Calculate provider score for specific task requirements"""
        metrics = self.provider_metrics[provider_name]
        
        # Base capability score
        capability_score = self._calculate_capability_score(provider_info, requirements)
        
        # Performance score based on metrics
        performance_score = (
            metrics.success_rate * 0.4 +
            (1.0 / max(metrics.response_time, 0.1)) * 0.3 +
            metrics.quality_score * 0.3
        )
        
        # Cost efficiency score
        cost_score = 1.0 / max(metrics.cost_per_token, 0.0001)
        
        # Get routing weights for this task type
        routing_rule = self.routing_rules.get(requirements.task_type, {})
        weights = routing_rule.get("weight_factors", {"accuracy": 0.5, "speed": 0.3, "cost": 0.2})
        
        # Weighted final score
        final_score = (
            capability_score * weights.get("accuracy", 0.5) +
            performance_score * weights.get("speed", 0.3) +
            cost_score * weights.get("cost", 0.2)
        )
        
        return final_score
    
    def _calculate_capability_score(self, provider_info: Dict[str, Any], requirements: TaskRequirements) -> float:
        """Calculate how well provider capabilities match task requirements"""
        provider_capabilities = provider_info.get("capabilities", [])
        
        # Get preferred capabilities for this task type
        routing_rule = self.routing_rules.get(requirements.task_type, {})
        preferred_capabilities = routing_rule.get("preferred_capabilities", [])
        
        if not preferred_capabilities:
            return 0.5  # Neutral score if no preferences defined
        
        # Calculate match score
        matches = sum(1 for cap in preferred_capabilities if cap in provider_capabilities)
        capability_score = matches / len(preferred_capabilities)
        
        return capability_score
    
    async def _check_health_monitoring(self):
        """Check if health monitoring is needed and execute if so"""
        now = datetime.now()
        if (now - self.last_health_check).total_seconds() > self.health_check_interval:
            await self._perform_health_check()
            self.last_health_check = now
    
    async def _perform_health_check(self):
        """Perform health check on all providers"""
        self.logger.info("Performing provider health check")
        
        for provider_name in self.providers.keys():
            try:
                # Simple health check - attempt a minimal request
                start_time = time.time()
                result = await self._test_provider_health(provider_name)
                response_time = time.time() - start_time
                
                # Update metrics
                metrics = self.provider_metrics[provider_name]
                metrics.availability = result
                metrics.response_time = response_time
                metrics.last_check = datetime.now()
                
                if result:
                    self.logger.debug(f"Provider {provider_name} health check passed ({response_time:.2f}s)")
                else:
                    self.logger.warning(f"Provider {provider_name} health check failed")
                    
            except Exception as e:
                self.logger.error(f"Health check error for {provider_name}: {e}")
                self.provider_metrics[provider_name].availability = False
    
    async def _test_provider_health(self, provider_name: str) -> bool:
        """Test individual provider health"""
        try:
            provider_info = self.providers[provider_name]
            
            if provider_info.get("type") == "foundups_infrastructure":
                # Test FoundUps infrastructure provider
                client = provider_info["client"]
                response = client.generate_response("Test", "Test health check")
                return bool(response and len(response) > 0)
            
            elif provider_info.get("type") == "multi_provider_connector":
                # Test multi-provider connector
                connector = provider_info["client"]
                response = connector.get_response("Health check test")
                return bool(response and len(response) > 0)
            
            else:
                # For external providers, assume healthy if API key exists
                return bool(provider_info.get("api_key"))
                
        except Exception as e:
            self.logger.debug(f"Health test failed for {provider_name}: {e}")
            return False
    
    def _start_health_monitoring(self):
        """Start background health monitoring"""
        # Note: In a real implementation, this would start a background task
        # For now, health checks are performed on-demand
        self.logger.info("Health monitoring initialized (on-demand mode)")
    
    def get_provider_status(self) -> Dict[str, Any]:
        """Get comprehensive provider status information"""
        status = {
            "total_providers": len(self.providers),
            "available_providers": sum(1 for m in self.provider_metrics.values() if m.availability),
            "last_health_check": self.last_health_check.isoformat(),
            "providers": {}
        }
        
        for provider_name, metrics in self.provider_metrics.items():
            status["providers"][provider_name] = {
                "available": metrics.availability,
                "response_time": metrics.response_time,
                "success_rate": metrics.success_rate,
                "total_requests": metrics.total_requests,
                "capabilities": [cap.value for cap in self.providers[provider_name].get("capabilities", [])]
            }
        
        return status
    
    async def process_with_optimal_provider(self, prompt: str, requirements: TaskRequirements) -> Dict[str, Any]:
        """Process request with optimal provider selection"""
        # Select optimal provider
        optimal_provider = await self.select_optimal_provider(requirements)
        
        if not optimal_provider:
            return {
                "success": False,
                "error": "No available providers",
                "fallback_mode": True
            }
        
        try:
            # Process with selected provider
            start_time = time.time()
            result = await self._process_with_provider(optimal_provider, prompt, requirements)
            processing_time = time.time() - start_time
            
            # Update metrics
            self._update_provider_metrics(optimal_provider, True, processing_time)
            
            return {
                "success": True,
                "provider_selected": optimal_provider,
                "response": result,
                "processing_time": processing_time,
                "task_type": requirements.task_type.value
            }
            
        except Exception as e:
            self.logger.error(f"Provider {optimal_provider} processing failed: {e}")
            
            # Update failure metrics
            self._update_provider_metrics(optimal_provider, False, 0)
            
            # Try fallback provider
            return await self._try_fallback_provider(prompt, requirements, failed_provider=optimal_provider)
    
    async def _process_with_provider(self, provider_name: str, prompt: str, requirements: TaskRequirements) -> str:
        """Process request with specific provider"""
        provider_info = self.providers[provider_name]
        
        if provider_info.get("type") == "foundups_infrastructure":
            client = provider_info["client"]
            return client.generate_response(prompt, "You are a helpful AI assistant.")
        
        elif provider_info.get("type") == "multi_provider_connector":
            connector = provider_info["client"]
            return connector.get_response(prompt)
        
        else:
            # For external providers, would implement specific API calls
            return f"Processed by {provider_name}: {prompt[:50]}..."
    
    async def _try_fallback_provider(self, prompt: str, requirements: TaskRequirements, failed_provider: str) -> Dict[str, Any]:
        """Try fallback provider when primary fails"""
        # Get available providers excluding the failed one
        available_providers = [name for name, metrics in self.provider_metrics.items() 
                             if metrics.availability and name != failed_provider]
        
        if not available_providers:
            return {
                "success": False,
                "error": "No fallback providers available",
                "failed_provider": failed_provider
            }
        
        # Select best fallback
        fallback_provider = available_providers[0]  # Simple fallback selection
        
        try:
            result = await self._process_with_provider(fallback_provider, prompt, requirements)
            return {
                "success": True,
                "provider_selected": fallback_provider,
                "response": result,
                "fallback_mode": True,
                "failed_provider": failed_provider
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Fallback provider also failed: {e}",
                "failed_providers": [failed_provider, fallback_provider]
            }
    
    def _update_provider_metrics(self, provider_name: str, success: bool, response_time: float):
        """Update provider performance metrics"""
        metrics = self.provider_metrics[provider_name]
        metrics.total_requests += 1
        
        if not success:
            metrics.failed_requests += 1
        
        metrics.success_rate = 1.0 - (metrics.failed_requests / metrics.total_requests)
        
        if response_time > 0:
            # Update rolling average response time
            metrics.response_time = (metrics.response_time * 0.8) + (response_time * 0.2) 