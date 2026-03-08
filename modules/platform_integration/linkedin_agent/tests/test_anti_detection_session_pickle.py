from pathlib import Path

from modules.platform_integration.linkedin_agent.src.anti_detection_poster import AntiDetectionLinkedIn


class _DriverStub:
    def __init__(self):
        self.loaded_cookies = []
        self.visited = []

    def get_cookies(self):
        return [{"name": "li_at", "value": "token"}]

    def get(self, url):
        self.visited.append(url)

    def add_cookie(self, cookie):
        self.loaded_cookies.append(cookie)

    def refresh(self):
        self.visited.append("refresh")


def test_save_and_load_session_use_binary_pickle_files(tmp_path: Path, monkeypatch):
    poster = AntiDetectionLinkedIn.__new__(AntiDetectionLinkedIn)
    poster.session_file = str(tmp_path / "linkedin_session.pkl")
    poster.driver = _DriverStub()

    monkeypatch.setattr("time.sleep", lambda *_args, **_kwargs: None)

    poster.save_session(verbose=False)
    assert Path(poster.session_file).exists()

    loader = AntiDetectionLinkedIn.__new__(AntiDetectionLinkedIn)
    loader.session_file = poster.session_file
    loader.driver = _DriverStub()

    loader.load_session()

    assert loader.driver.loaded_cookies == [{"name": "li_at", "value": "token"}]
    assert loader.driver.visited[0] == "https://www.linkedin.com"
