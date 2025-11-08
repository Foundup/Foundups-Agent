#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HoloSingleton Manager - AI Overseer's Resource Control Spigot
=============================================================

"Everything in the DAEmon should be like a spigot that can be tightened
or loosened with AI Overseer as the agentic wrench" - 012

This module provides AI Overseer with centralized control over HoloIndex
instantiation. AI Overseer learns optimal configuration through missions.

WSP Compliance:
- WSP 77: Agent Coordination (AI Overseer controls resource allocation)
- WSP 48: Recursive Learning (Configuration learned from missions)
- WSP 60: Module Memory (Wardrobe config stored in overseer memory)
"""

import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class LazyHoloIndex:
    """
    Lazy-loading wrapper for HoloIndex.

    Delays actual HoloIndex creation until first search is requested.
    Reduces startup time for components that may not use HoloIndex.
    """

    def __init__(self, component_name: str, manager: 'HoloSingletonManager'):
        self.component_name = component_name
        self.manager = manager
        self._real_instance = None
        logger.info(f"[SPIGOT] Created lazy HoloIndex wrapper for {component_name}")

    def _ensure_loaded(self):
        """Load HoloIndex on first actual use"""
        if self._real_instance is None:
            logger.info(f"[SPIGOT] Lazy-loading HoloIndex for {self.component_name} on first use")
            try:
                from holo_index.core.holo_index import HoloIndex
                self._real_instance = HoloIndex()
                self.manager._record_instantiation(self.component_name, "lazy_load")
            except Exception as e:
                logger.error(f"[SPIGOT] Failed to load HoloIndex for {self.component_name}: {e}")
                raise

    def search(self, *args, **kwargs):
        """Delegate search to real HoloIndex (loading if needed)"""
        self._ensure_loaded()
        return self._real_instance.search(*args, **kwargs)

    def index_code_entries(self, *args, **kwargs):
        self._ensure_loaded()
        return self._real_instance.index_code_entries(*args, **kwargs)

    def index_wsp_entries(self, *args, **kwargs):
        self._ensure_loaded()
        return self._real_instance.index_wsp_entries(*args, **kwargs)


class HoloSingletonManager:
    """
    AI Overseer's agentic resource control system.

    The "wrench" that tightens/loosens "spigots" based on learned patterns.
    AI Overseer learns optimal configuration through missions.

    Spigot Modes (learned by AI Overseer):
    - shared_singleton: All components share one instance (tightened)
    - lazy_load: Create on first use, not on __init__ (partially open)
    - per_component: Each component gets own instance (loosened)
    - deny: Component doesn't get HoloIndex (closed)
    """

    _instance: Optional['HoloSingletonManager'] = None
    _shared_holo: Optional[Any] = None
    _component_instances: Dict[str, Any] = {}

    def __init__(self, wardrobe_path: Optional[Path] = None):
        """
        Initialize the singleton manager.

        Args:
            wardrobe_path: Path to AI Overseer learned configuration
        """
        self.wardrobe_path = wardrobe_path or Path(
            "modules/ai_intelligence/ai_overseer/memory/holo_wardrobe.json"
        )
        self.config = self._load_wardrobe()
        self.components_using_holo = []
        self.instantiation_log = []
        self._graph_export_done = False

        logger.info(f"[SPIGOT] HoloSingletonManager initialized with policy: {self.config.get('holo_policy', 'adaptive')}")

    @classmethod
    def get_instance(cls, wardrobe_path: Optional[Path] = None) -> 'HoloSingletonManager':
        """Get or create the singleton manager"""
        if cls._instance is None:
            cls._instance = HoloSingletonManager(wardrobe_path)
        return cls._instance

    @classmethod
    def get_holo_for_component(cls, component_name: str) -> Optional[Any]:
        """
        The SPIGOT: AI Overseer controls if component gets HoloIndex.

        Args:
            component_name: Name of requesting component (e.g., "AIIntelligenceOverseer")

        Returns:
            HoloIndex instance, LazyHoloIndex wrapper, or None based on policy
        """
        manager = cls.get_instance()
        return manager._get_or_create(component_name)

    def _get_or_create(self, component_name: str) -> Optional[Any]:
        """AI Overseer's learned decision logic for resource allocation"""
        policy = self.config.get("holo_policy", "shared_singleton")

        # Check if component is explicitly denied
        denied_components = self.config.get("denied_components", [])
        if component_name in denied_components:
            logger.info(f"[SPIGOT] Denied HoloIndex for {component_name} (wardrobe policy)")
            return None

        # Apply policy
        if policy == "shared_singleton":
            return self._get_shared_instance(component_name)

        elif policy == "lazy_load":
            return self._get_lazy_instance(component_name)

        elif policy == "per_component":
            return self._get_per_component_instance(component_name)

        elif policy == "deny":
            logger.info(f"[SPIGOT] Denied HoloIndex for {component_name} (global deny)")
            return None

        else:
            # Adaptive mode: AI Overseer hasn't decided yet, use shared as default
            logger.warning(f"[SPIGOT] Unknown policy '{policy}', defaulting to shared_singleton")
            return self._get_shared_instance(component_name)

    def _get_shared_instance(self, component_name: str) -> Any:
        """Tightened spigot: Everyone shares one instance"""
        if HoloSingletonManager._shared_holo is None:
            logger.info(f"[SPIGOT] Creating shared HoloIndex for {component_name}")
            try:
                from holo_index.core.holo_index import HoloIndex
                HoloSingletonManager._shared_holo = HoloIndex()
                self._record_instantiation(component_name, "shared_singleton")
                self._maybe_trigger_graph_export(HoloSingletonManager._shared_holo)
            except Exception as e:
                logger.error(f"[SPIGOT] Failed to create shared HoloIndex: {e}")
                return None
        else:
            logger.info(f"[SPIGOT] Reusing shared HoloIndex for {component_name}")
            if not self._graph_export_done:
                self._maybe_trigger_graph_export(HoloSingletonManager._shared_holo)

        self.components_using_holo.append(component_name)
        return HoloSingletonManager._shared_holo

    def _get_lazy_instance(self, component_name: str) -> LazyHoloIndex:
        """Partially open: Create on first actual use, not on __init__"""
        return LazyHoloIndex(component_name, self)

    def _get_per_component_instance(self, component_name: str) -> Any:
        """Loosened spigot: Each component gets own instance"""
        if component_name not in HoloSingletonManager._component_instances:
            logger.info(f"[SPIGOT] Creating dedicated HoloIndex for {component_name}")
            try:
                from holo_index.core.holo_index import HoloIndex
                HoloSingletonManager._component_instances[component_name] = HoloIndex()
                self._record_instantiation(component_name, "per_component")
            except Exception as e:
                logger.error(f"[SPIGOT] Failed to create HoloIndex for {component_name}: {e}")
                return None
        else:
            logger.info(f"[SPIGOT] Reusing dedicated HoloIndex for {component_name}")

        return HoloSingletonManager._component_instances[component_name]

    def _record_instantiation(self, component_name: str, mode: str):
        """Record instantiation for AI Overseer learning"""
        self.instantiation_log.append({
            "component": component_name,
            "mode": mode,
            "timestamp": datetime.now().isoformat()
        })

    def _load_wardrobe(self) -> Dict[str, Any]:
        """
        Load AI Overseer learned configuration.

        Configuration is learned through missions (Phase 4 learning).
        If no learned config exists, use sensible defaults.
        """
        try:
            if self.wardrobe_path.exists():
                with open(self.wardrobe_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    logger.info(f"[SPIGOT] Loaded wardrobe from {self.wardrobe_path}")
                    return config
        except Exception as e:
            logger.warning(f"[SPIGOT] Could not load wardrobe: {e}")

        # Default policy (AI Overseer will learn better through missions)
        return {
            "holo_policy": "shared_singleton",
            "lazy_load_threshold": 5.0,  # Lazy load if startup time > 5s
            "denied_components": [],
            "breadcrumbs_during_startup": False,
            "learned_at": None,
            "learned_from": "default_config",
            "notes": "Default configuration - AI Overseer will optimize through missions"
        }

    def save_wardrobe(self, config: Dict[str, Any]):
        """
        Save learned configuration (called by AI Overseer missions).

        This is Phase 4 learning - AI Overseer stores what it learned.
        """
        try:
            self.wardrobe_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.wardrobe_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
            logger.info(f"[SPIGOT] Saved wardrobe to {self.wardrobe_path}")
            self.config = config
        except Exception as e:
            logger.error(f"[SPIGOT] Failed to save wardrobe: {e}")

    def get_stats(self) -> Dict[str, Any]:
        """Get usage statistics for AI Overseer analysis"""
        return {
            "policy": self.config.get("holo_policy"),
            "components_using_holo": self.components_using_holo,
            "total_instantiations": len(self.instantiation_log),
            "shared_instance_active": HoloSingletonManager._shared_holo is not None,
            "per_component_instances": len(HoloSingletonManager._component_instances),
            "instantiation_log": self.instantiation_log
        }

    def _maybe_trigger_graph_export(self, holo_instance: Any):
        """Optionally export GraphRAG bundle when wardrobe requests it (WSP 96/98)."""
        if self._graph_export_done:
            return

        graph_cfg = self.config.get("graph_export", {})
        if not graph_cfg.get("enabled"):
            self._graph_export_done = True
            return

        if holo_instance is None:
            return

        try:
            refresh_hours = float(graph_cfg.get("refresh_hours", 0) or 0)
        except (TypeError, ValueError):
            refresh_hours = 0

        last_exported = graph_cfg.get("last_exported")
        should_run = True
        if last_exported:
            try:
                last_dt = datetime.fromisoformat(last_exported)
            except ValueError:
                last_dt = None
            if last_dt:
                if refresh_hours > 0:
                    if datetime.utcnow() - last_dt < timedelta(hours=refresh_hours):
                        should_run = False
                else:
                    should_run = False

        if not should_run:
            self._graph_export_done = True
            return

        try:
            from holo_index.exporters.graphrag_exporter import GraphRAGExporter

            exporter = GraphRAGExporter(holo_instance)
            output_dir = graph_cfg.get("output_dir", "out/graphrag_bundle")
            queries = graph_cfg.get("queries") or None
            limit = int(graph_cfg.get("limit", 10) or 10)

            bundle_path = exporter.export(output_dir, queries=queries, limit=limit)
            logger.info(f"[GRAPH-RAG] Exported Holo knowledge bundle to {bundle_path}")

            graph_cfg["last_exported"] = datetime.utcnow().isoformat()
            self.save_wardrobe(self.config)
        except Exception as exc:
            logger.warning(f"[GRAPH-RAG] Export skipped due to error: {exc}")
        finally:
            self._graph_export_done = True


# Global convenience function
def get_holo_instance(component_name: str) -> Optional[Any]:
    """
    Convenience function for components to request HoloIndex.

    Usage:
        from modules.ai_intelligence.ai_overseer.src.holo_singleton_manager import get_holo_instance
        holo = get_holo_instance("MyComponent")
    """
    return HoloSingletonManager.get_holo_for_component(component_name)
