"""
Tests for the `!party` command wiring.

Goal: ensure `!party` is detected as a command and does not crash when invoked
from inside the LiveChat async loop.
"""

import asyncio
import os


def test_party_command_detected_as_whack_command() -> None:
    from modules.communication.livechat.src.message_processor import MessageProcessor

    processor = MessageProcessor.__new__(MessageProcessor)
    assert processor._check_whack_command("!party") is True


def test_party_command_runs_in_event_loop_without_asyncio_run_crash() -> None:
    from modules.communication.livechat.src.command_handler import CommandHandler
    from modules.communication.livechat.src import party_reactor

    class MockTimeoutManager:
        pass

    handler = CommandHandler(MockTimeoutManager(), None)

    async def fake_trigger_party(total_clicks: int = 30) -> str:
        return f"FAKE PARTY COMPLETE ({total_clicks})"

    original_trigger_party = party_reactor.trigger_party
    original_env = {}
    env_keys = [
        "YT_AUTOMATION_ENABLED",
        "YT_LIVECHAT_UI_ACTIONS_ENABLED",
        "YT_PARTY_REACTIONS_ENABLED",
    ]

    for key in env_keys:
        original_env[key] = os.environ.get(key)

    try:
        party_reactor.trigger_party = fake_trigger_party
        os.environ["YT_AUTOMATION_ENABLED"] = "true"
        os.environ["YT_LIVECHAT_UI_ACTIONS_ENABLED"] = "true"
        os.environ["YT_PARTY_REACTIONS_ENABLED"] = "true"

        async def run() -> None:
            response = handler.handle_whack_command("!party 5", "TestOwner", "test_id_123", "OWNER")
            assert response is not None
            assert "Party started" in response

            # Allow background task to run to completion before closing the loop.
            await asyncio.sleep(0)
            pending = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
            if pending:
                await asyncio.gather(*pending)

        asyncio.run(run())
    finally:
        party_reactor.trigger_party = original_trigger_party
        for key in env_keys:
            if original_env[key] is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = original_env[key]

