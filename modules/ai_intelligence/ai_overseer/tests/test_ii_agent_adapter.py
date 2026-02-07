#!/usr/bin/env python3
import os
from pathlib import Path

from modules.ai_intelligence.ai_overseer.src.ii_agent_adapter import IIAgentAdapter


def test_adapter_disabled_by_default():
    os.environ.pop("II_AGENT_ENABLED", None)
    adapter = IIAgentAdapter(Path("O:/Foundups-Agent"))
    result = adapter.run_mission("test", "code_analysis")
    assert result.get("skipped") is True
