#!/usr/bin/env python3
"""Policy tests for DuckDuckGo news ingestion and no-video posting."""

import sqlite3
import tempfile

from modules.platform_integration.linkedin_agent.skillz.openclaw_group_news.executor import (
    NewsItem,
    OpenClawGroupPoster,
    _classify_news_priority,
    _is_allowed_news_candidate,
    _is_policy_news_candidate,
    _looks_like_video_candidate,
    run_openclaw_news_flow,
)


def test_video_detection_blocks_direct_video_hosts():
    assert _looks_like_video_candidate("https://www.youtube.com/watch?v=abc123")
    assert _looks_like_video_candidate("https://vimeo.com/123456")
    assert _looks_like_video_candidate("https://www.tiktok.com/@a/video/123")


def test_video_detection_blocks_ddg_redirect_wrapped_video():
    wrapped = (
        "https://duckduckgo.com/l/?uddg="
        "https%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3Dxyz987"
    )
    assert _looks_like_video_candidate(wrapped)


def test_allowed_candidate_rejects_non_http_and_video():
    assert not _is_allowed_news_candidate("javascript:alert(1)")
    assert not _is_allowed_news_candidate("https://youtu.be/xyz987")
    assert _is_allowed_news_candidate("https://techcrunch.com/2026/02/openclaw-update")


def test_post_to_group_rejects_video_item_before_posting():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as handle:
        db_path = handle.name

    poster = OpenClawGroupPoster(db_path=db_path)
    item = NewsItem(
        title="Video only update",
        url="https://www.youtube.com/watch?v=blocked",
        source="youtube",
        summary="Official video release",
    )
    assert poster.post_to_group(item, dry_run=True) is False

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM agents_social_posts")
    count = cur.fetchone()[0]
    conn.close()
    assert count == 0


def test_news_flow_reports_duckduck_provider(monkeypatch):
    monkeypatch.setattr(
        "modules.platform_integration.linkedin_agent.skillz.openclaw_group_news.executor.search_openclaw_news",
        lambda max_results=10: [],
    )
    result = run_openclaw_news_flow(dry_run=True)
    assert result["search_provider"] == "duckduckgo"
    assert result["video_policy"] == "blocked"


def test_format_post_includes_cli_comment():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as handle:
        db_path = handle.name

    poster = OpenClawGroupPoster(db_path=db_path)
    item = NewsItem(
        title="OpenClaw test item",
        url="https://example.com/news",
        source="example",
        summary="summary",
    )
    content = poster.format_post(item, extra_comment="custom cli comment")
    assert "custom cli comment" in content


def test_policy_classifies_openclaw_actionable_update():
    bucket = _classify_news_priority(
        "OpenClaw security patch fixes agent escalation bug",
        "Release notes and patch details for v2.1",
        "TechCrunch",
    )
    assert bucket == "openclaw_update"


def test_policy_rejects_non_actionable_openclaw_general_news():
    item = NewsItem(
        title="OpenClaw creator shares lessons on playful prototyping",
        url="https://example.com/interview",
        source="example",
        summary="Interview and opinion piece without release details.",
    )
    assert _is_policy_news_candidate(item) is False


def test_policy_accepts_major_ai_security_update():
    item = NewsItem(
        title="OpenAI announces API deprecation and security update",
        url="https://example.com/openai-update",
        source="example",
        summary="Migration timeline for developers and security controls update.",
    )
    assert _is_policy_news_candidate(item) is True


def test_news_flow_prefers_policy_aligned_item(monkeypatch):
    fake_items = [
        NewsItem(
            title="OpenClaw creator discusses philosophy",
            url="https://example.com/philosophy",
            source="example",
            summary="Opinion discussion without concrete updates.",
        ),
        NewsItem(
            title="OpenClaw release notes: security patch and API fix",
            url="https://example.com/release-notes",
            source="TechCrunch",
            summary="Patch details and migration notes.",
        ),
    ]

    monkeypatch.setattr(
        "modules.platform_integration.linkedin_agent.skillz.openclaw_group_news.executor.search_openclaw_news",
        lambda max_results=10: fake_items,
    )
    monkeypatch.setattr(
        "modules.platform_integration.linkedin_agent.skillz.openclaw_group_news.executor.OpenClawGroupPoster.post_to_group",
        lambda self, item, dry_run=False, extra_comment="": True,
    )

    result = run_openclaw_news_flow(dry_run=True)
    assert result["posted"] is True
    assert result["top_item"] == "OpenClaw release notes: security patch and API fix"
    assert result["top_item_bucket"] == "openclaw_update"
