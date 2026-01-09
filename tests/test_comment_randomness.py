import os
from pathlib import Path


class _DummyDriver:
    current_url = "https://studio.youtube.com/"

    def __init__(self, png_bytes: bytes = b"\x89PNG\r\n\x1a\n"):
        self._png = png_bytes

    def get_screenshot_as_png(self):
        return self._png

    def execute_script(self, *args, **kwargs):
        # Unit tests do not execute real DOM scripts.
        return {}


class _DummyReplyExecutor:
    pass


def _make_processor(tmp_path: Path):
    from modules.communication.video_comments.skillz.tars_like_heart_reply.src.comment_processor import CommentProcessor

    os.environ["YT_UI_SNAPSHOT_DIR"] = str(tmp_path)
    os.environ["YT_UI_PRE_ACTION_SNAPSHOT"] = "true"
    os.environ["YT_0102_BEHAVIOR_INTERFACE"] = "0102"
    os.environ["YT_ACTION_RANDOMNESS_MODE"] = "dynamic"

    selectors = {
        "comment_thread": "ytcp-comment-thread",
        "like": "#like-button",
        "heart": "#creator-heart-button",
    }

    return CommentProcessor(
        driver=_DummyDriver(),
        human=None,
        stats={},
        reply_executor=_DummyReplyExecutor(),
        selectors=selectors,
        vision_descriptions={},
        use_vision=False,
        use_dom=True,
        ui_tars_bridge=None,
        session_id="test_session",
    )


def test_dynamic_probability_is_bounded(tmp_path: Path):
    proc = _make_processor(tmp_path)
    for _ in range(200):
        p = proc._dynamic_probability(0.8)
        assert 0.0 <= p <= 1.0


def test_fixed_randomness_mode_returns_base_probability(tmp_path: Path):
    proc = _make_processor(tmp_path)
    os.environ["YT_ACTION_RANDOMNESS_MODE"] = "fixed"
    proc.randomness_mode = "fixed"
    _ok, p = proc._should_attempt("like", 0.42)
    assert abs(p - 0.42) < 1e-9


def test_pre_action_snapshot_writes_files(tmp_path: Path):
    proc = _make_processor(tmp_path)
    png_path = proc._capture_pre_action_snapshot(
        action="like",
        comment_idx=1,
        ui_state={"found": True, "disabled": False, "pressed": False},
    )
    assert png_path is not None
    assert Path(png_path).exists()
    assert Path(png_path).with_suffix(".json").exists()

