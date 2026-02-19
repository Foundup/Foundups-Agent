"""FAM bridge symbol-collision hardening tests."""

from __future__ import annotations

from modules.foundups.simulator.adapters.fam_bridge import FAMBridge


def test_create_foundup_auto_resolves_symbol_collision(tmp_path) -> None:
    """Second FoundUp with same symbol should resolve deterministically."""
    bridge = FAMBridge(data_dir=tmp_path, deterministic=True)

    ok1, msg1, first_id = bridge.create_foundup(
        name="First",
        owner_id="founder_001",
        token_symbol="TEST",
    )
    assert ok1, msg1
    assert first_id is not None

    ok2, msg2, second_id = bridge.create_foundup(
        name="Second",
        owner_id="founder_002",
        token_symbol="TEST",
    )
    assert ok2, msg2
    assert second_id is not None
    assert second_id != first_id

    first = bridge.get_foundup(first_id)
    second = bridge.get_foundup(second_id)
    assert first is not None
    assert second is not None
    assert first.token_symbol == "TEST"
    assert second.token_symbol != "TEST"
    assert second.token_symbol.startswith("TEST")

