import asyncio
from pathlib import Path

from modules.infrastructure.git_push_dae.scripts import post_commit_social_runner as runner


def test_build_git_push_event(monkeypatch, tmp_path):
    responses = {
        ("diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD"): "a.py\nb.py\n",
        ("rev-parse", "--short", "HEAD"): "abc1234",
        ("log", "-1", "--pretty=%s"): "Fix hook latency",
        ("log", "-1", "--pretty=%B"): "Fix hook latency\n\nMore detail",
        ("branch", "--show-current"): "fix/test-branch",
    }

    def fake_run_git(repo_root: Path, *args: str) -> str:
        return responses[args]

    monkeypatch.setattr(runner, "_run_git", fake_run_git)

    event = runner.build_git_push_event(tmp_path / "Foundups-Agent")

    assert event["event"] == "git_push"
    assert event["payload"]["repository"] == "Foundups-Agent"
    assert event["payload"]["branch"] == "fix/test-branch"
    assert event["payload"]["commits"][0]["hash"] == "abc1234"
    assert event["payload"]["commits"][0]["files_changed"] == 2
    assert event["dedupe_key"] == "git_push:fix/test-branch:abc1234"


def test_append_jsonl_record(tmp_path):
    output = tmp_path / "memory" / "events.jsonl"
    runner.append_jsonl_record(output, {"event": "git_push", "payload": {"ok": True}})

    text = output.read_text(encoding="utf-8")
    assert '"event": "git_push"' in text
    assert '"ok": true' in text


def test_dispatch_git_push_event(monkeypatch):
    class FakeRouter:
        async def handle_event(self, event_type, payload):
            return {"event_type": event_type, "count": len(payload["commits"])}

    monkeypatch.setattr(runner, "_get_social_media_router_class", lambda: FakeRouter)

    result = asyncio.run(
        runner.dispatch_git_push_event(
            {
                "payload": {
                    "commits": [{"hash": "abc1234"}],
                    "repository": "Foundups-Agent",
                    "branch": "main",
                }
            }
        )
    )

    assert result == {"event_type": "git_push", "count": 1}
