from modules.ai_intelligence.ai_overseer.src.mission_analysis_mixin import MissionAnalysisMixin
from modules.ai_intelligence.ai_overseer.src.types import MissionType


class _AnalysisStub(MissionAnalysisMixin):
    """Minimal stub to exercise mixin helpers without heavy dependencies."""

    holo_available = False
    orchestrator = None
    daemon_logger = None
    holo_adapter = None
    patterns = {"learned_strategies": {}}

    def _collect_mcp_status(self):  # pragma: no cover - simple stub
        return {}


def test_classify_mission_complexity_scales_with_keywords():
    stub = _AnalysisStub()
    result = stub._classify_mission_complexity("complex architecture change")
    assert result["complexity"] == 5


def test_recommend_team_composition_fixed_roles():
    stub = _AnalysisStub()
    team = stub._recommend_team_composition(MissionType.CUSTOM)
    assert team == {"partner": "qwen", "principal": "0102", "associate": "gemma"}
