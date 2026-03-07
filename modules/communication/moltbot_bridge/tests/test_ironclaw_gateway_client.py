"""
Tests for IronClaw gateway client health probing behavior.
"""

from unittest.mock import MagicMock, patch

from modules.communication.moltbot_bridge.src.ironclaw_gateway_client import (
    IronClawGatewayClient,
)


def _mock_response(ok: bool, status_code: int) -> MagicMock:
    resp = MagicMock()
    resp.ok = ok
    resp.status_code = status_code
    return resp


def test_health_prefers_explicit_health_endpoint():
    client = IronClawGatewayClient()
    with patch(
        "requests.get",
        side_effect=[
            _mock_response(True, 200),  # /api/health
        ],
    ):
        healthy, detail = client.health()

    assert healthy is True
    assert detail == "healthy via /api/health"


def test_health_falls_back_to_models_endpoint():
    client = IronClawGatewayClient()
    with patch(
        "requests.get",
        side_effect=[
            _mock_response(False, 404),  # /api/health
            _mock_response(False, 404),  # /health
            _mock_response(True, 200),   # /v1/models
        ],
    ):
        healthy, detail = client.health()

    assert healthy is True
    assert detail == "healthy via /v1/models"


def test_health_returns_diagnostics_when_all_probes_fail():
    client = IronClawGatewayClient()
    with patch(
        "requests.get",
        side_effect=[
            _mock_response(False, 404),  # /api/health
            Exception("boom"),           # /health
            _mock_response(False, 503),  # /v1/models
        ],
    ):
        healthy, detail = client.health()

    assert healthy is False
    assert detail.startswith("health probes failed (")
    assert "/api/health=404" in detail
    assert "/health=error:Exception" in detail
    assert "/v1/models=503" in detail
