from pathlib import Path

from modules.ai_intelligence.ai_overseer.src.mission_execution_mixin import MissionExecutionMixin
from modules.ai_intelligence.ai_overseer.src.types import AgentRole, AgentTeam, MissionType


class _ExecutionStub(MissionExecutionMixin):
    """Minimal stub for exercising execution mixin routing."""

    repo_root = Path(".")
    holo_available = True
    holo_adapter = None
    daemon_logger = None
    patch_executor = None
    metrics = None
    fix_attempts = {}

    def _ensure_mcp_connected(self):  # pragma: no cover - not needed for unit test
        return None

    def _execute_mcp_tool(self, *args, **kwargs):  # pragma: no cover - stub
        return {"success": True}

    def _collect_mcp_status(self):
        return {"available": False}

    def _delegate_to_gemma(self, phase, team):
        return {"success": True, "agent": AgentRole.ASSOCIATE.value}

    def _delegate_to_qwen(self, phase, team):
        return {"success": True, "agent": AgentRole.PARTNER.value}

    def _execute_as_principal(self, phase, team):
        return {"success": True, "agent": AgentRole.PRINCIPAL.value}


def test_execute_single_phase_routes_to_associate():
    stub = _ExecutionStub()
    team = AgentTeam("m1", MissionType.CUSTOM)
    result = stub._execute_single_phase({"agent": AgentRole.ASSOCIATE.value}, team)
    assert result["agent"] == AgentRole.ASSOCIATE.value


def test_execute_single_phase_routes_to_partner():
    stub = _ExecutionStub()
    team = AgentTeam("m2", MissionType.CUSTOM)
    result = stub._execute_single_phase({"agent": AgentRole.PARTNER.value}, team)
    assert result["agent"] == AgentRole.PARTNER.value


def test_execute_single_phase_routes_to_principal():
    stub = _ExecutionStub()
    team = AgentTeam("m3", MissionType.CUSTOM)
    result = stub._execute_single_phase({"agent": AgentRole.PRINCIPAL.value}, team)
    assert result["agent"] == AgentRole.PRINCIPAL.value
