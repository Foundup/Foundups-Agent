import os


def test_should_perform_action_fixed_mode_extremes():
    from modules.infrastructure.foundups_selenium.src.human_behavior import HumanBehavior

    os.environ["YT_ACTION_RANDOMNESS_MODE"] = "fixed"
    hb = HumanBehavior(driver=None)

    for _ in range(50):
        assert hb.should_perform_action(0.0) is False

    for _ in range(50):
        assert hb.should_perform_action(1.0) is True

