#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Shared type definitions for AI Overseer components.

Provides enums and dataclasses that were previously declared inside
`ai_overseer.py` so helper mixins can reuse them without circular imports.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List


class AgentRole(Enum):
    """WSP 54 Agent Team Roles (NOT traditional 012/0102 roles)"""

    PARTNER = "qwen"  # Qwen: Does simple stuff, scales up
    PRINCIPAL = "0102"  # 0102: Lays out plan, oversees execution
    ASSOCIATE = "gemma"  # Gemma: Pattern recognition, scales up


class MissionType(Enum):
    """Types of missions AI Overseer can coordinate"""

    CODE_ANALYSIS = "code_analysis"
    ARCHITECTURE_DESIGN = "architecture_design"
    MODULE_INTEGRATION = "module_integration"
    TESTING_ORCHESTRATION = "testing_orchestration"
    DOCUMENTATION_GENERATION = "documentation_generation"
    WSP_COMPLIANCE = "wsp_compliance"
    DAEMON_MONITORING = "daemon_monitoring"  # Monitor daemon bash shells
    BUG_DETECTION = "bug_detection"  # Detect bugs in daemon output
    AUTO_REMEDIATION = "auto_remediation"  # Auto-fix low-hanging fruit
    CUSTOM = "custom"


@dataclass
class AgentTeam:
    """Represents a coordinated agent team following WSP 54"""

    mission_id: str
    mission_type: MissionType
    partner: str = "qwen"  # Qwen Partner: Simple tasks, scales up
    principal: str = "0102"  # 0102 Principal: Plans and oversees
    associate: str = "gemma"  # Gemma Associate: Pattern recognition
    status: str = "initialized"
    created_at: float = field(default_factory=time.time)
    results: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CoordinationPlan:
    """Strategic coordination plan from WSP 77 Phase 2 (Qwen Partner)"""

    mission_id: str
    mission_type: MissionType
    phases: List[Dict[str, Any]]
    estimated_complexity: int  # 1-5 scale
    recommended_approach: str
    learning_patterns: List[str] = field(default_factory=list)
