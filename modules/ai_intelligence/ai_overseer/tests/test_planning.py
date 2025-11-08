from modules.ai_intelligence.ai_overseer.src.mission_planning_mixin import MissionPlanningMixin


class _PlanningStub(MissionPlanningMixin):
    daemon_logger = None


def test_determine_approach_thresholds():
    stub = _PlanningStub()
    assert stub._determine_approach(1) == "autonomous_execution"
    assert stub._determine_approach(3) == "supervised_execution"
    assert stub._determine_approach(5) == "collaborative_orchestration"
