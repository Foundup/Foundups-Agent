import os
import types
import sys
import importlib
import pytest
from unittest.mock import MagicMock


@pytest.fixture(autouse=True)
def register_dummy_gemini_module():
    """
    Provide a lightweight GeminiVisionAnalyzer so FoundUpsDriver
    can import vision support without touching real dependencies.
    """
    module_name = (
        "modules.platform_integration.social_media_orchestrator.src."
        "gemini_vision_analyzer"
    )
    dummy_module = types.SimpleNamespace(
        GeminiVisionAnalyzer=lambda: MagicMock(name="GeminiVisionAnalyzer")
    )
    sys.modules[module_name] = dummy_module
    try:
        yield
    finally:
        sys.modules.pop(module_name, None)


@pytest.fixture
def patched_chrome(monkeypatch):
    """
    Replace selenium Chrome initialiser with a controllable stub so
    tests never open a real browser.
    """
    calls = {"count": 0, "options": None}

    def fake_init(self, **kwargs):
        calls["count"] += 1
        calls["options"] = kwargs.get("options")
        # emulate selenium by storing the options attribute
        self._mock_options = calls["options"]

    monkeypatch.setattr(
        "modules.infrastructure.foundups_selenium.src.foundups_driver."
        "webdriver.Chrome.__init__",
        fake_init,
    )
    return calls


@pytest.fixture
def noop_js(monkeypatch):
    """Prevent JS stealth routine from attempting to execute script."""
    monkeypatch.setattr(
        "modules.infrastructure.foundups_selenium.src.foundups_driver."
        "FoundUpsDriver._apply_js_stealth",
        lambda self: None,
    )


def test_driver_initialises_with_port(monkeypatch, patched_chrome, noop_js):
    """Ensure debug port is forwarded to Chrome options and stealth applied."""
    stealth_calls = {}

    def fake_stealth(self, options):
        stealth_calls["called_with"] = options

    monkeypatch.setattr(
        "modules.infrastructure.foundups_selenium.src.foundups_driver."
        "FoundUpsDriver._apply_stealth_options",
        fake_stealth,
    )

    from modules.infrastructure.foundups_selenium.src.foundups_driver import (
        FoundUpsDriver,
    )

    driver = FoundUpsDriver(port=9222)

    # Stealth options should have been applied once
    assert "called_with" in stealth_calls

    # Chrome was initialised and contains debuggerAddress option
    assert patched_chrome["count"] == 1
    chrome_options = patched_chrome["options"]
    assert chrome_options is not None
    experimental = chrome_options._experimental_options
    assert experimental.get("debuggerAddress") == "127.0.0.1:9222"

    # Vision should be enabled because dummy analyzer is available
    assert driver.vision_enabled is True
    assert driver.vision_analyzer is not None


def test_driver_fallback_when_port_connection_fails(monkeypatch, noop_js):
    """If connecting to an existing browser fails, the driver should retry without port."""

    call_log = {"count": 0, "options": []}
    added_options = []
    events = []
    module = importlib.import_module(
        "modules.infrastructure.foundups_selenium.src.foundups_driver"
    )
    original_add = module.ChromeOptions.add_experimental_option

    def record_add(self, name, value):
        added_options.append((name, value))
        return original_add(self, name, value)

    def flaky_init(self, **kwargs):
        call_log["count"] += 1
        call_log["options"].append(kwargs.get("options"))
        # first attempt fails (simulate port connection failure)
        if call_log["count"] == 1:
            raise Exception("Port unavailable")

    monkeypatch.setattr(
        "modules.infrastructure.foundups_selenium.src.foundups_driver."
        "webdriver.Chrome.__init__",
        flaky_init,
    )
    monkeypatch.setattr(
        "modules.infrastructure.foundups_selenium.src.foundups_driver."
        "FoundUpsDriver._apply_stealth_options",
        lambda self, options: None,
    )
    monkeypatch.setattr(
        "modules.infrastructure.foundups_selenium.src.foundups_driver."
        "ChromeOptions.add_experimental_option",
        record_add,
    )

    from modules.infrastructure.foundups_selenium.src.foundups_driver import (
        FoundUpsDriver,
    )

    driver = FoundUpsDriver(
        port=9222,
        observers=[lambda event, payload: events.append((event, payload))],
    )

    # Second attempt should succeed without re-raising
    assert call_log["count"] == 2

    assert ("debuggerAddress", "127.0.0.1:9222") in added_options
    second_opts = call_log["options"][-1]
    # Fallback removes debuggerAddress before reinitialising
    assert "debuggerAddress" not in second_opts._experimental_options

    # Events should capture the retry flow
    assert any(event == "init_retry" for event, _ in events)
    assert any(event == "init_retry_succeeded" for event, _ in events)

    # Driver should disable vision gracefully if import fails (handled via dummy fixture)
    assert hasattr(driver, "vision_enabled")


def test_connect_or_create_reuses_existing_session(
    monkeypatch, patched_chrome, noop_js
):
    """Ensure connect_or_create short-circuits when session already active."""
    from modules.infrastructure.foundups_selenium.src.foundups_driver import (
        FoundUpsDriver,
    )

    driver = FoundUpsDriver()
    monkeypatch.setattr(
        type(driver),
        "current_url",
        property(lambda self: "https://existing.example"),
    )

    events = []
    driver.register_observer(lambda event, payload: events.append((event, payload)))

    quit_calls = {"count": 0}
    nav_log = {"url": None}

    def fake_quit(self):
        quit_calls["count"] += 1

    def fake_get(self, url):
        nav_log["url"] = url

    monkeypatch.setattr(
        "modules.infrastructure.foundups_selenium.src.foundups_driver."
        "FoundUpsDriver.quit",
        fake_quit,
    )
    monkeypatch.setattr(
        "modules.infrastructure.foundups_selenium.src.foundups_driver."
        "FoundUpsDriver.get",
        fake_get,
    )

    connected = driver.connect_or_create(port=9222, url="https://target.example")

    assert connected is True
    assert quit_calls["count"] == 0
    assert nav_log["url"] == "https://target.example"
    assert any(event == "connect_or_create_reused" for event, _ in events)
    assert any(event == "connect_or_create_navigated" for event, _ in events)


def test_analyze_ui_saves_screenshot_and_calls_vision(
    monkeypatch, patched_chrome, noop_js, tmp_path
):
    """Vision analysis should call analyzer, persist screenshots, and emit telemetry."""
    from modules.infrastructure.foundups_selenium.src.foundups_driver import (
        FoundUpsDriver,
    )

    driver = FoundUpsDriver()
    screenshot_bytes = b"fake-bytes"
    monkeypatch.setattr(
        driver,
        "get_screenshot_as_png",
        lambda: screenshot_bytes,
    )
    driver.vision_analyzer.analyze_posting_ui.return_value = {"status": "ok"}

    events = []
    driver.register_observer(lambda event, payload: events.append((event, payload)))

    result = driver.analyze_ui(save_screenshot=True, screenshot_dir=str(tmp_path))

    driver.vision_analyzer.analyze_posting_ui.assert_called_once_with(screenshot_bytes)
    assert result["status"] == "ok"
    assert "screenshot_path" in result
    assert os.path.exists(result["screenshot_path"])
    completed_payload = next(
        payload for event, payload in events if event == "vision_analyze_completed"
    )
    assert completed_payload["save_screenshot"] is True
    assert os.path.exists(completed_payload["screenshot_path"])


def test_analyze_ui_returns_error_when_vision_disabled(
    monkeypatch, patched_chrome, noop_js
):
    """Vision analysis should short-circuit when vision is disabled."""
    from modules.infrastructure.foundups_selenium.src.foundups_driver import (
        FoundUpsDriver,
    )

    driver = FoundUpsDriver(vision_enabled=False)
    driver.vision_analyzer = None

    events = []
    driver.register_observer(lambda event, payload: events.append((event, payload)))

    result = driver.analyze_ui()

    assert result == {"error": "Vision not enabled"}
    assert any(
        event == "vision_analyze_skipped" and payload.get("reason") == "vision_disabled"
        for event, payload in events
    )


def test_human_type_types_characters(monkeypatch, patched_chrome, noop_js):
    """Typing helper should clear element, send characters, and emit event."""
    from modules.infrastructure.foundups_selenium.src.foundups_driver import (
        FoundUpsDriver,
    )

    monkeypatch.setattr(
        "modules.infrastructure.foundups_selenium.src.foundups_driver.random.uniform",
        lambda *args, **kwargs: 0,
    )
    monkeypatch.setattr(
        "modules.infrastructure.foundups_selenium.src.foundups_driver.time.sleep",
        lambda *args, **kwargs: None,
    )

    driver = FoundUpsDriver()
    events = []
    driver.register_observer(lambda event, payload: events.append((event, payload)))

    class DummyElement:
        def __init__(self):
            self.calls = []

        def clear(self):
            self.calls.append("clear")

        def send_keys(self, char):
            self.calls.append(char)

    element = DummyElement()
    driver.human_type(element, "hi", min_delay=0, max_delay=0)

    assert element.calls == ["clear", "h", "i"]
    assert any(
        event == "human_type" and payload.get("characters") == 2
        for event, payload in events
    )


def test_post_to_x_emits_events(monkeypatch, patched_chrome, noop_js):
    """Posting flow should emit start/completion telemetry and delegate correctly."""
    from modules.infrastructure.foundups_selenium.src.foundups_driver import (
        FoundUpsDriver,
    )

    events = []

    class DummyPoster:
        def __init__(self, use_foundups):
            self.use_foundups = use_foundups
            self.driver = None

        def post_to_x(self, content):
            assert self.driver is not None
            return True

    monkeypatch.setattr(
        "modules.platform_integration.x_twitter.src.x_anti_detection_poster.AntiDetectionX",
        DummyPoster,
    )

    driver = FoundUpsDriver()
    driver.register_observer(lambda event, payload: events.append((event, payload)))

    result = driver.post_to_x("Hello FoundUps!", account="foundups")

    assert result is True
    assert any(event == "post_to_x_started" for event, _ in events)
    assert any(
        event == "post_to_x_completed" and payload.get("success") is True
        for event, payload in events
    )
