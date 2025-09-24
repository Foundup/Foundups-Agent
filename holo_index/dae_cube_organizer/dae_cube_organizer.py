#!/usr/bin/env python3
"""
DAE Cube Organizer - HoloIndex DAE Rampup Server

Provides immediate DAE context and structure understanding for 0102 agents.
Acts as the foundational intelligence layer that all modules plug into,
forming DAE Cubes that connect in main.py.

WSP Compliance: WSP 80 (Cube-Level DAE Orchestration), WSP 87 (Code Navigation)
"""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class DAECube:
    """Represents a complete DAE Cube structure."""
    name: str
    description: str
    orchestrator: str
    modules: List[str] = field(default_factory=list)
    responsibilities: List[str] = field(default_factory=list)
    health_status: str = "unknown"
    last_active: Optional[str] = None
    main_py_reference: str = ""


@dataclass
class DAEModule:
    """Represents a module within a DAE cube."""
    name: str
    path: str
    domain: str
    description: str
    dependencies: List[str] = field(default_factory=list)
    health_score: int = 0


class DAECubeOrganizer:
    """
    DAE Cube Organizer - The foundational intelligence layer.

    Provides immediate DAE context and structure understanding,
    eliminating the need for 0102 agents to compute DAE relationships.
    """

    def __init__(self):
        self.dae_cubes = self._initialize_dae_cubes()
        self.module_registry = self._build_module_registry()
        self.main_py_analysis = self._analyze_main_py()

    def _initialize_dae_cubes(self) -> Dict[str, DAECube]:
        """Initialize the known DAE cube structures."""
        return {
            "youtube_dae": DAECube(
                name="YouTube Live DAE",
                description="Real-time YouTube chat moderation and gamification system",
                orchestrator="AutoModeratorDAE",
                modules=[
                    "communication/livechat",
                    "platform_integration/stream_resolver",
                    "platform_integration/youtube_auth",
                    "platform_integration/social_media_orchestrator",
                    "gamification/whack_a_magat",
                    "infrastructure/instance_lock"
                ],
                responsibilities=[
                    "Stream detection and monitoring",
                    "Chat message processing and moderation",
                    "Gamification (XP/ranks/levels)",
                    "Social media posting automation",
                    "Multi-channel support (Move2Japan, UnDaoDu, FoundUps)",
                    "Throttling and API quota management"
                ],
                main_py_reference="Option 1: monitor_youtube()"
            ),

            "amo_dae": DAECube(
                name="Autonomous Meeting Orchestrator",
                description="Recursive multi-agent conversation and scheduling system",
                orchestrator="AutoModeratorDAE",
                modules=[
                    "communication/livechat",
                    "ai_intelligence/0102_orchestrator",
                    "infrastructure/wre_core"
                ],
                responsibilities=[
                    "Meeting scheduling and coordination",
                    "Multi-agent conversation orchestration",
                    "Recursive improvement cycles",
                    "Session management and logging"
                ],
                main_py_reference="Option 2: run_amo_dae()"
            ),

            "social_media_dae": DAECube(
                name="Social Media DAE (012 Digital Twin)",
                description="Automated social media presence and engagement system",
                orchestrator="SocialMediaDAE",
                modules=[
                    "platform_integration/social_media_orchestrator",
                    "platform_integration/linkedin_agent",
                    "platform_integration/x_twitter",
                    "ai_intelligence/social_media_dae"
                ],
                responsibilities=[
                    "LinkedIn company page management",
                    "X/Twitter automation and engagement",
                    "Content scheduling and posting",
                    "Digital twin maintenance",
                    "Multi-platform orchestration"
                ],
                main_py_reference="Option 3: run_social_media_dae()"
            ),

            "pqn_dae": DAECube(
                name="P&Q Orchestration DAE",
                description="Quantum research, pattern detection, and rESP analysis system",
                orchestrator="PQNResearchDAEOrchestrator",
                modules=[
                    "ai_intelligence/pqn_alignment",
                    "ai_intelligence/rESP_o1o2",
                    "infrastructure/database"
                ],
                responsibilities=[
                    "PQN alignment validation campaigns",
                    "rESP detector processing and analysis",
                    "Quantum coherence pattern research",
                    "Database-backed learning and memory",
                    "Cross-validation and statistical analysis"
                ],
                main_py_reference="Option 4: run_pqn_dae()"
            ),

            "developer_ops_dae": DAECube(
                name="Developer Ops Orchestrator",
                description="Remote builds, Git integration, and development operations",
                orchestrator="GitOpsOrchestrator",
                modules=[
                    "platform_integration/remote_builder",
                    "infrastructure/git_integration",
                    "development/module_creator"
                ],
                responsibilities=[
                    "Remote repository management",
                    "Automated build and deployment",
                    "ModLog synchronization",
                    "Module scaffolding and creation"
                ],
                main_py_reference="Option 0: git_push_and_post()"
            )
        }

    def _build_module_registry(self) -> Dict[str, DAEModule]:
        """Build comprehensive module registry from codebase."""
        registry = {}

        # Scan modules directory for actual modules
        modules_dir = Path("modules")
        if modules_dir.exists():
            for domain_dir in modules_dir.iterdir():
                if domain_dir.is_dir() and not domain_dir.name.startswith('.'):
                    domain = domain_dir.name

                    for module_dir in domain_dir.iterdir():
                        if module_dir.is_dir() and not module_dir.name.startswith('.'):
                            module_name = module_dir.name
                            module_path = f"{domain}/{module_name}"

                            # Try to read README for description
                            readme_path = module_dir / "README.md"
                            description = f"{domain} {module_name} module"
                            if readme_path.exists():
                                try:
                                    with open(readme_path, 'r', encoding='utf-8') as f:
                                        content = f.read()
                                        # Extract first meaningful line after title
                                        lines = content.split('\n')
                                        for line in lines[1:5]:
                                            line = line.strip()
                                            if line and not line.startswith('#') and len(line) > 10:
                                                description = line
                                                break
                                except:
                                    pass

                            registry[module_path] = DAEModule(
                                name=module_name,
                                path=module_path,
                                domain=domain,
                                description=description
                            )

        return registry

    def _analyze_main_py(self) -> Dict[str, Any]:
        """Analyze main.py to understand DAE orchestration."""
        analysis = {
            "dae_options": {},
            "orchestrators": set(),
            "imports": set()
        }

        try:
            with open("main.py", 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract DAE option descriptions from menu
            menu_matches = re.findall(r'(\d+)\.\s*([^(\n]+)', content)
            for num, desc in menu_matches:
                if num in ['1', '2', '3', '4', '0']:
                    analysis["dae_options"][num] = desc.strip()

            # Extract orchestrator imports
            import_matches = re.findall(r'from\s+modules\.[^\'"]*\s+import\s+([^\'"\n]+)', content)
            for match in import_matches:
                if 'DAE' in match or 'Orchestrator' in match:
                    analysis["orchestrators"].add(match)

            # Extract function definitions
            func_matches = re.findall(r'def\s+(run_\w+_dae|monitor_\w+|git_push_and_post)', content)
            analysis["functions"] = list(set(func_matches))

        except Exception as e:
            logger.warning(f"Could not analyze main.py: {e}")

        return analysis

    def initialize_dae_context(self, dae_focus: Optional[str] = None) -> Dict[str, Any]:
        """
        Initialize DAE context for 0102 agent rampup.

        Args:
            dae_focus: The DAE that 012 wants 0102 to become (optional)

        Returns:
            Complete DAE context and structure information
        """
        if dae_focus:
            detected_dae = self._detect_dae_from_focus(dae_focus)
        else:
            detected_dae = self._detect_active_dae()

        context = {
            "dae_identity": self._get_dae_identity(detected_dae),
            "cube_structure": self._get_cube_structure(detected_dae),
            "module_map": self._get_module_map(detected_dae),
            "orchestration_flow": self._get_orchestration_flow(detected_dae),
            "health_status": self._get_health_status(detected_dae),
            "quick_reference": self._get_quick_reference(detected_dae),
            "rampup_guidance": self._get_rampup_guidance(detected_dae)
        }

        return context

    def _detect_dae_from_focus(self, dae_focus: str) -> str:
        """Detect DAE from 012's focus instruction."""
        focus_lower = dae_focus.lower()

        # Map common focus descriptions to DAE keys
        focus_mapping = {
            "youtube": "youtube_dae",
            "live chat": "youtube_dae",
            "moderation": "amo_dae",
            "meeting": "amo_dae",
            "autonomous meeting": "amo_dae",
            "social media": "social_media_dae",
            "digital twin": "social_media_dae",
            "linkedin": "social_media_dae",
            "twitter": "social_media_dae",
            "pqn": "pqn_dae",
            "quantum": "pqn_dae",
            "research": "pqn_dae",
            "resp": "pqn_dae",
            "developer": "developer_ops_dae",
            "git": "developer_ops_dae",
            "remote build": "developer_ops_dae"
        }

        for keyword, dae_key in focus_mapping.items():
            if keyword in focus_lower:
                return dae_key

        return "youtube_dae"  # Default fallback

    def _detect_active_dae(self) -> str:
        """Detect currently active DAE from system state."""
        # Check for running processes or recent activity
        # For now, default to youtube_dae as it's the most active
        return "youtube_dae"

    def _get_dae_identity(self, dae_key: str) -> Dict[str, Any]:
        """Get DAE identity information."""
        dae = self.dae_cubes.get(dae_key)
        if not dae:
            return {"error": f"Unknown DAE: {dae_key}"}

        return {
            "name": dae.name,
            "description": dae.description,
            "orchestrator": dae.orchestrator,
            "main_py_reference": dae.main_py_reference,
            "emoji": self._get_dae_emoji(dae_key)
        }

    def _get_dae_emoji(self, dae_key: str) -> str:
        """Get emoji representation for DAE."""
        emoji_map = {
            "youtube_dae": "📺",
            "amo_dae": "🧠",
            "social_media_dae": "📢",
            "pqn_dae": "🧬",
            "developer_ops_dae": "⚙️"
        }
        return emoji_map.get(dae_key, "🔧")

    def _get_cube_structure(self, dae_key: str) -> Dict[str, Any]:
        """Get complete cube structure with modules and connections."""
        dae = self.dae_cubes.get(dae_key)
        if not dae:
            return {"error": f"Unknown DAE: {dae_key}"}

        structure = {
            "orchestrator": {
                "name": dae.orchestrator,
                "responsibilities": dae.responsibilities
            },
            "modules": {},
            "connections": self._analyze_module_connections(dae_key)
        }

        # Add detailed module information
        for module_path in dae.modules:
            module = self.module_registry.get(module_path)
            if module:
                structure["modules"][module_path] = {
                    "name": module.name,
                    "domain": module.domain,
                    "description": module.description,
                    "health_score": module.health_score
                }

        return structure

    def _analyze_module_connections(self, dae_key: str) -> List[Dict[str, str]]:
        """Analyze how modules connect within the DAE."""
        connections = []

        if dae_key == "youtube_dae":
            connections = [
                {"from": "stream_resolver", "to": "auto_moderator_dae", "purpose": "Stream detection → Chat processing"},
                {"from": "auto_moderator_dae", "to": "social_media_orchestrator", "purpose": "Stream start → Social posting"},
                {"from": "youtube_auth", "to": "stream_resolver", "purpose": "Authentication → Stream access"},
                {"from": "instance_lock", "to": "auto_moderator_dae", "purpose": "Process management → Safe execution"}
            ]
        elif dae_key == "pqn_dae":
            connections = [
                {"from": "pqn_alignment", "to": "pqn_research_dae_orchestrator", "purpose": "Research campaigns → Orchestration"},
                {"from": "rESP_o1o2", "to": "pqn_research_dae_orchestrator", "purpose": "Detector analysis → Research coordination"},
                {"from": "database", "to": "pqn_alignment", "purpose": "Data persistence → Research continuity"}
            ]

        return connections

    def _get_module_map(self, dae_key: str) -> Dict[str, Any]:
        """Get visual module map for the DAE."""
        dae = self.dae_cubes.get(dae_key)
        if not dae:
            return {}

        # Create ASCII art style module map
        module_map = f"""
{self._get_dae_emoji(dae_key)} {dae.name}
{'=' * (len(dae.name) + 2)}

🎯 ORCHESTRATOR
    └── {dae.orchestrator}

📦 MODULES
"""

        for module_path in dae.modules:
            module = self.module_registry.get(module_path)
            if module:
                domain_emoji = self._get_domain_emoji(module.domain)
                module_map += f"    ├── {domain_emoji} {module.name}\n"
                module_map += f"    │   └── {module.description[:50]}...\n"

        module_map += f"\n🔄 RESPONSIBILITIES\n"
        for resp in dae.responsibilities[:3]:
            module_map += f"    • {resp}\n"

        return {"ascii_map": module_map.strip(), "module_count": len(dae.modules)}

    def _get_domain_emoji(self, domain: str) -> str:
        """Get emoji for domain."""
        domain_emojis = {
            "communication": "💬",
            "platform_integration": "🔌",
            "ai_intelligence": "🧠",
            "infrastructure": "🏗️",
            "gamification": "🎮",
            "development": "⚙️"
        }
        return domain_emojis.get(domain, "📦")

    def _get_orchestration_flow(self, dae_key: str) -> Dict[str, Any]:
        """Get orchestration flow for the DAE."""
        flows = {
            "youtube_dae": {
                "phases": [
                    "🔍 Stream Detection (stream_resolver)",
                    "🔐 Authentication (youtube_auth)",
                    "💬 Chat Processing (auto_moderator_dae)",
                    "🎮 Gamification (whack_a_magat)",
                    "📢 Social Posting (social_media_orchestrator)"
                ],
                "loop_type": "continuous_stream_monitoring",
                "error_handling": "instance_lock_prevention"
            },
            "pqn_dae": {
                "phases": [
                    "🧬 Research Campaign Setup (pqn_alignment)",
                    "🔬 rESP Analysis (rESP_o1o2)",
                    "💾 Data Persistence (database)",
                    "📊 Cross-Validation (pqn_research_dae_orchestrator)"
                ],
                "loop_type": "research_campaign_cycles",
                "error_handling": "statistical_validation"
            }
        }

        return flows.get(dae_key, {"phases": ["Orchestration flow not defined"]})

    def _get_health_status(self, dae_key: str) -> Dict[str, Any]:
        """Get health status for the DAE."""
        # This would integrate with actual health monitoring
        # For now, provide mock health status
        return {
            "overall_status": "healthy",
            "module_health": "4/4 modules operational",
            "last_check": datetime.now().isoformat(),
            "issues": []
        }

    def _get_quick_reference(self, dae_key: str) -> Dict[str, Any]:
        """Get quick reference information."""
        dae = self.dae_cubes.get(dae_key)
        if not dae:
            return {}

        return {
            "menu_option": dae.main_py_reference,
            "key_modules": dae.modules[:3],
            "primary_responsibility": dae.responsibilities[0] if dae.responsibilities else "",
            "emergency_contacts": ["Check main.py logs", "Verify instance locks"]
        }

    def _get_rampup_guidance(self, dae_key: str) -> Dict[str, Any]:
        """Get rampup guidance for 0102 agent."""
        guidance = {
            "immediate_focus": "Understand the orchestrator and module connections",
            "key_resources": [
                "Read orchestrator source code",
                "Check module READMEs",
                "Review main.py integration points"
            ],
            "avoid_common_pitfalls": [
                "Don't modify core orchestration logic without testing",
                "Always check instance locks before starting",
                "Verify module health before assuming functionality"
            ],
            "success_indicators": [
                "Orchestrator initializes without errors",
                "Modules connect and communicate properly",
                "DAE achieves its primary responsibilities"
            ]
        }

        # DAE-specific guidance
        if dae_key == "youtube_dae":
            guidance["special_notes"] = [
                "Multi-channel support requires careful API quota management",
                "Instance locking is critical for preventing conflicts",
                "Stream detection should be tested across all channels"
            ]
        elif dae_key == "pqn_dae":
            guidance["special_notes"] = [
                "Database integrity is critical for research continuity",
                "Statistical validation should be verified regularly",
                "Cross-validation campaigns require significant compute"
            ]

        return guidance
