
# === UTF-8 ENFORCEMENT (WSP 90) ===
import sys
import io
if sys.platform.startswith('win'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
# === END UTF-8 ENFORCEMENT ===

import logging
import asyncio
import pytest
from unittest.mock import patch
from modules.infrastructure.token_manager.src.token_manager import TokenManager

def mock_authenticated_service_success(*args, **kwargs):
    class MockChannels:
        def list(self, **_):
            return self
        def execute(self):
            return {"items": [{}]}  # simulate valid API response
    return type("MockService", (), {"channels": lambda self: MockChannels()})()

def mock_authenticated_service_fail(*args, **kwargs):
    return None  # simulate failure

@pytest.mark.asyncio
async def test_check_token_health_pass():
    print("✅ test_check_token_health_pass")
    manager = TokenManager()
    with patch("modules.infrastructure.token_manager.src.token_manager.get_authenticated_service", side_effect=mock_authenticated_service_success):
        result = manager.check_token_health(0)
        print("Result:", result)
        assert result is True

@pytest.mark.asyncio
async def test_check_token_health_fail_and_cooldown():
    print("✅ test_check_token_health_fail_and_cooldown")
    manager = TokenManager()
    with patch("modules.infrastructure.token_manager.src.token_manager.get_authenticated_service", side_effect=mock_authenticated_service_fail):
        result = manager.check_token_health(0)
        print("Initial result (should fail):", result)
        assert result is False

        result = manager.check_token_health(0)
        print("Cooldown result (should skip):", result)
        assert result is False

@pytest.mark.asyncio
async def test_rotate_tokens_mixed():
    print("✅ test_rotate_tokens_mixed")
    manager = TokenManager()

    with patch.object(manager, "check_token_health", side_effect=[False, False, True]):
        result = await manager.rotate_tokens()
        print("Rotated to:", result)
        assert result == 2

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    asyncio.run(test_check_token_health_pass())
    asyncio.run(test_check_token_health_fail_and_cooldown())
    asyncio.run(test_rotate_tokens_mixed()) 