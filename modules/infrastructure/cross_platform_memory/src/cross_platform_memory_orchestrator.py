# -*- coding: utf-8 -*-
"""
Cross-Platform Memory Orchestrator (WSP 60 Enhanced)

Orchestrates memory sharing across all platform domains for unified intelligence.
Provides the foundation for Phase 2 cross-platform learning and coordination.

WSP 60: Module Memory Architecture Protocol
WSP 80: Cube-Level DAE Orchestration
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, asdict
import sys
import io

# WSP 90 UTF-8 Enforcement for Windows compatibility
if sys.platform.startswith('win'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from .pattern_memory import PatternMemory
from .breadcrumb_trail import BreadcrumbTrail
from .agent_coordination import AgentCoordination

logger = logging.getLogger(__name__)


@dataclass
class CrossPlatformEvent:
    """Cross-platform intelligence event"""
    event_id: str
    source_module: str
    source_domain: str
    event_type: str
    data: Dict[str, Any]
    timestamp: datetime
    cross_platform_value: bool = False
    shared_domains: List[str] = None

    def __post_init__(self):
        if self.shared_domains is None:
            self.shared_domains = []


class CrossPlatformMemoryOrchestrator:
    """
    Cross-Platform Memory Orchestrator

    WSP 60 Enhanced: Unified memory architecture for cross-platform intelligence
    Enables Phase 2 cross-platform learning and multi-agent coordination

    Architecture:
    - Pattern Memory: Cross-domain pattern sharing and learning
    - Breadcrumb Trails: Multi-agent discovery coordination
    - Agent Coordination: Strategy synchronization across platforms
    - Event Bus: Real-time cross-platform intelligence sharing
    """

    def __init__(self, base_path: str = "modules"):
        """
        Initialize cross-platform memory orchestrator

        Args:
            base_path: Base path to modules directory
        """
        self.base_path = Path(base_path)
        self.memory_path = self.base_path / "infrastructure" / "cross_platform_memory" / "memory"
        self.memory_path.mkdir(parents=True, exist_ok=True)

        # Core components
        self.pattern_memory = PatternMemory(self.memory_path / "patterns")
        self.breadcrumb_trail = BreadcrumbTrail("cross_platform_orchestrator")
        self.agent_coordination = AgentCoordination()

        # Event bus for cross-platform communication
        self.event_listeners: Dict[str, List[callable]] = {}
        self.event_queue: asyncio.Queue = asyncio.Queue()

        # Domain mapping for cross-platform intelligence
        self.domain_mapping = {
            "communication": ["liberty_alert", "livechat", "intent_manager"],
            "platform_integration": ["linkedin_agent", "youtube_auth", "social_media_orchestrator"],
            "ai_intelligence": ["consciousness_engine", "banter_engine", "pqn_alignment"],
            "infrastructure": ["wre_core", "shared_utilities", "dae_infrastructure"]
        }

        # Active modules tracking
        self.active_modules: Set[str] = set()

        logger.info("[CROSS-PLATFORM] Memory orchestrator initialized")

    async def start(self) -> bool:
        """
        Start cross-platform memory orchestration

        Returns:
            bool: True if started successfully
        """
        try:
            # Initialize pattern memory
            await self.pattern_memory.initialize()

            # Start event processing
            asyncio.create_task(self._process_events())

            # Discover and register active modules
            await self._discover_active_modules()

            # Initialize cross-platform intelligence sharing
            await self._initialize_cross_platform_sharing()

            logger.info("[CROSS-PLATFORM] Memory orchestration started successfully")
            return True

        except Exception as e:
            logger.error(f"[CROSS-PLATFORM] Failed to start: {e}")
            return False

    async def stop(self) -> bool:
        """
        Stop cross-platform memory orchestration

        Returns:
            bool: True if stopped successfully
        """
        try:
            # Save all memory state
            await self.pattern_memory.save_all()
            await self.breadcrumb_trail.save_trail()

            # Clear event queue
            while not self.event_queue.empty():
                try:
                    self.event_queue.get_nowait()
                except asyncio.QueueEmpty:
                    break

            logger.info("[CROSS-PLATFORM] Memory orchestration stopped")
            return True

        except Exception as e:
            logger.error(f"[CROSS-PLATFORM] Failed to stop: {e}")
            return False

    async def _discover_active_modules(self):
        """Discover and register active modules with memory directories"""
        for domain, modules in self.domain_mapping.items():
            domain_path = self.base_path / domain
            if domain_path.exists():
                for module in modules:
                    module_path = domain_path / module
                    memory_path = module_path / "memory"
                    if memory_path.exists():
                        module_key = f"{domain}.{module}"
                        self.active_modules.add(module_key)
                        logger.info(f"[CROSS-PLATFORM] Registered active module: {module_key}")

    async def _initialize_cross_platform_sharing(self):
        """Initialize cross-platform intelligence sharing"""
        # Load existing patterns from all active modules
        for module_key in self.active_modules:
            domain, module = module_key.split(".", 1)
            await self._load_module_patterns(domain, module)

        # Establish coordination channels
        await self.agent_coordination.initialize_coordination(self.active_modules)

        logger.info(f"[CROSS-PLATFORM] Cross-platform sharing initialized for {len(self.active_modules)} modules")

    async def _load_module_patterns(self, domain: str, module: str):
        """Load patterns from a specific module"""
        try:
            module_path = self.base_path / domain / module
            memory_path = module_path / "memory"

            # Look for pattern files
            pattern_files = list(memory_path.glob("**/patterns.json"))
            consciousness_dirs = list(memory_path.glob("consciousness"))

            for pattern_file in pattern_files:
                try:
                    with open(pattern_file, 'r', encoding='utf-8') as f:
                        patterns = json.load(f)

                    # Import patterns into cross-platform memory
                    for pattern_name, pattern_data in patterns.items():
                        await self.pattern_memory.store_pattern(
                            pattern_name,
                            pattern_data,
                            source_module=f"{domain}.{module}",
                            cross_platform=True
                        )

                except Exception as e:
                    logger.warning(f"[CROSS-PLATFORM] Failed to load patterns from {pattern_file}: {e}")

            # Load consciousness state if available
            for consciousness_dir in consciousness_dirs:
                consciousness_file = consciousness_dir / "agentic_state.json"
                if consciousness_file.exists():
                    try:
                        with open(consciousness_file, 'r', encoding='utf-8') as f:
                            state_data = json.load(f)

                        # Share consciousness patterns
                        await self.pattern_memory.store_pattern(
                            f"consciousness_{domain}_{module}",
                            state_data,
                            source_module=f"{domain}.{module}",
                            cross_platform=True
                        )

                    except Exception as e:
                        logger.warning(f"[CROSS-PLATFORM] Failed to load consciousness from {consciousness_file}: {e}")

        except Exception as e:
            logger.error(f"[CROSS-PLATFORM] Failed to load patterns for {domain}.{module}: {e}")

    async def share_cross_platform_event(self, event: CrossPlatformEvent):
        """
        Share an event across platforms

        Args:
            event: Cross-platform event to share
        """
        # Add to event queue for processing
        await self.event_queue.put(event)

        # Record breadcrumb
        await self.breadcrumb_trail.add_action(
            "cross_platform_event",
            {
                "event_id": event.event_id,
                "event_type": event.event_type,
                "source": f"{event.source_domain}.{event.source_module}",
                "shared_domains": event.shared_domains,
                "cross_platform_value": event.cross_platform_value
            }
        )

        # Store in pattern memory if valuable
        if event.cross_platform_value:
            await self.pattern_memory.store_pattern(
                f"event_{event.event_type}_{event.event_id}",
                {
                    "event_data": asdict(event),
                    "learned_patterns": [],
                    "coordination_opportunities": []
                },
                source_module=f"{event.source_domain}.{event.source_module}",
                cross_platform=True
            )

        logger.info(f"[CROSS-PLATFORM] Shared event: {event.event_type} from {event.source_module}")

    async def _process_events(self):
        """Process cross-platform events"""
        while True:
            try:
                event = await self.event_queue.get()

                # Notify listeners
                event_type = event.event_type
                if event_type in self.event_listeners:
                    for listener in self.event_listeners[event_type]:
                        try:
                            await listener(event)
                        except Exception as e:
                            logger.error(f"[CROSS-PLATFORM] Event listener error: {e}")

                # Coordinate with other agents if needed
                if event.cross_platform_value:
                    await self.agent_coordination.coordinate_event(event)

                self.event_queue.task_done()

            except Exception as e:
                logger.error(f"[CROSS-PLATFORM] Event processing error: {e}")
                await asyncio.sleep(1)  # Prevent tight loop on persistent errors

    def register_event_listener(self, event_type: str, listener: callable):
        """
        Register an event listener

        Args:
            event_type: Type of event to listen for
            listener: Async callable that takes a CrossPlatformEvent
        """
        if event_type not in self.event_listeners:
            self.event_listeners[event_type] = []

        self.event_listeners[event_type].append(listener)
        logger.info(f"[CROSS-PLATFORM] Registered listener for event type: {event_type}")

    async def query_cross_platform_patterns(self, query: str, domains: List[str] = None) -> Dict[str, Any]:
        """
        Query patterns across platforms

        Args:
            query: Pattern query
            domains: Specific domains to query (None for all)

        Returns:
            Cross-platform pattern results
        """
        results = await self.pattern_memory.query_patterns(query, domains)

        # Record breadcrumb for cross-platform query
        await self.breadcrumb_trail.add_action(
            "cross_platform_query",
            {
                "query": query,
                "domains_queried": domains or list(self.domain_mapping.keys()),
                "results_found": len(results.get("patterns", []))
            }
        )

        return results

    async def get_coordination_status(self) -> Dict[str, Any]:
        """
        Get current coordination status across platforms

        Returns:
            Coordination status information
        """
        status = await self.agent_coordination.get_status()

        # Add memory statistics
        memory_stats = await self.pattern_memory.get_statistics()

        return {
            "active_modules": list(self.active_modules),
            "coordination_status": status,
            "memory_statistics": memory_stats,
            "event_listeners": list(self.event_listeners.keys()),
            "breadcrumb_count": await self.breadcrumb_trail.get_trail_length()
        }

    async def optimize_cross_platform_learning(self) -> Dict[str, Any]:
        """
        Optimize cross-platform learning based on current patterns

        Returns:
            Optimization recommendations
        """
        # Analyze pattern effectiveness
        pattern_analysis = await self.pattern_memory.analyze_effectiveness()

        # Analyze coordination patterns
        coordination_analysis = await self.agent_coordination.analyze_coordination()

        # Generate optimization recommendations
        recommendations = []

        # Check for under-utilized patterns
        for pattern_name, analysis in pattern_analysis.items():
            if analysis.get("usage_rate", 0) < 0.3:
                recommendations.append({
                    "type": "pattern_promotion",
                    "pattern": pattern_name,
                    "action": "Increase cross-platform sharing",
                    "expected_impact": "Enhanced learning efficiency"
                })

        # Check for coordination gaps
        for domain, status in coordination_analysis.items():
            if status.get("coordination_score", 1.0) < 0.7:
                recommendations.append({
                    "type": "coordination_enhancement",
                    "domain": domain,
                    "action": "Strengthen inter-domain coordination",
                    "expected_impact": "Improved multi-agent collaboration"
                })

        # Record optimization action
        await self.breadcrumb_trail.add_action(
            "learning_optimization",
            {
                "recommendations_generated": len(recommendations),
                "patterns_analyzed": len(pattern_analysis),
                "domains_coordinated": len(coordination_analysis)
            }
        )

        return {
            "pattern_analysis": pattern_analysis,
            "coordination_analysis": coordination_analysis,
            "recommendations": recommendations,
            "optimization_timestamp": datetime.now().isoformat()
        }




