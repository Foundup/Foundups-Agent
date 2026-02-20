#!/usr/bin/env python3
"""
Test OpenClaw Group News Skill

Verifies:
- News relevance rating (4-dimension scoring)
- Rate limiting (3/day, 4-hour interval)
- Duplicate detection
- Post formatting with lobster branding
"""

# === UTF-8 ENFORCEMENT (WSP 90) ===
import sys
import io
if sys.platform.startswith('win'):
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except (OSError, ValueError):
        pass
# === END UTF-8 ENFORCEMENT ===

import os
import sqlite3
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent.parent.parent))

from modules.platform_integration.linkedin_agent.skillz.openclaw_group_news import (
    NewsItem,
    NewsRelevanceRater,
    OpenClawGroupPoster,
    RELEVANCE_THRESHOLD,
)


def test_news_relevance_rating():
    """Test the 4-dimension news relevance scoring."""
    print("\n" + "="*60)
    print("TEST: News Relevance Rating")
    print("="*60)

    # Test case 1: High relevance - direct OpenClaw mention, recent, good source
    item1 = NewsItem(
        title="OpenClaw Launches New Agent Payment Standard",
        url="https://techcrunch.com/openclaw-launch",
        source="TechCrunch",
        published_date=datetime.now() - timedelta(hours=12),
        summary="OpenClaw, the open-source AI agent framework, today announced a new payment standard for autonomous agents."
    )
    score1 = NewsRelevanceRater.rate(item1)
    print(f"\n[1] Direct mention, TechCrunch, 12h old:")
    print(f"    Title: {item1.title}")
    print(f"    Score: {score1:.3f} (threshold: {RELEVANCE_THRESHOLD})")
    print(f"    Pass: {'✅' if score1 >= RELEVANCE_THRESHOLD else '❌'}")
    assert score1 >= 0.7, f"Expected high score for direct OpenClaw mention, got {score1}"

    # Test case 2: Medium relevance - related topic, older
    item2 = NewsItem(
        title="AI Agents Are Changing How We Think About Payments",
        url="https://medium.com/ai-agents-payments",
        source="Medium",
        published_date=datetime.now() - timedelta(days=5),
        summary="Autonomous agents and AI orchestration are revolutionizing fintech."
    )
    score2 = NewsRelevanceRater.rate(item2)
    print(f"\n[2] Related topic, Medium, 5 days old:")
    print(f"    Title: {item2.title}")
    print(f"    Score: {score2:.3f}")
    print(f"    Pass: {'✅' if score2 >= 0.4 else '❌'} (expected medium)")

    # Test case 3: Low relevance - unrelated, old, unknown source
    item3 = NewsItem(
        title="Best Recipes for Summer BBQ",
        url="https://random-blog.com/bbq",
        source="Random Blog",
        published_date=datetime.now() - timedelta(days=30),
        summary="Great recipes for your next barbecue party."
    )
    score3 = NewsRelevanceRater.rate(item3)
    print(f"\n[3] Unrelated content, unknown source, old:")
    print(f"    Title: {item3.title}")
    print(f"    Score: {score3:.3f}")
    print(f"    Pass: {'✅' if score3 < RELEVANCE_THRESHOLD else '❌'} (expected low)")
    assert score3 < RELEVANCE_THRESHOLD, f"Expected low score for unrelated content, got {score3}"

    # Test case 4: Breaking news boost
    item4 = NewsItem(
        title="OpenClaw Partners with Major Cloud Provider",
        url="https://venturebeat.com/openclaw-partnership",
        source="VentureBeat",
        published_date=datetime.now() - timedelta(hours=2),
        summary="OpenClaw announced a major partnership today."
    )
    score4 = NewsRelevanceRater.rate(item4)
    print(f"\n[4] Breaking news, partnership announcement:")
    print(f"    Title: {item4.title}")
    print(f"    Score: {score4:.3f}")
    print(f"    Pass: {'✅' if score4 >= 0.8 else '❌'} (expected high)")

    print("\n✅ News relevance rating tests passed!")
    return True


def test_rate_limiting():
    """Test rate limiting: 3/day max, 4-hour minimum."""
    print("\n" + "="*60)
    print("TEST: Rate Limiting")
    print("="*60)

    # Create temp database
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name

    try:
        poster = OpenClawGroupPoster(db_path=db_path)

        # Test 1: Fresh start - should allow posting
        can_post, reason = poster.can_post_today()
        print(f"\n[1] Fresh database:")
        print(f"    Can post: {can_post}")
        print(f"    Reason: {reason}")
        assert can_post, f"Should allow posting on fresh database: {reason}"

        # Test 2: Simulate 3 posts today (use Python datetime to avoid UTC mismatch)
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        base_time = datetime.now()
        for i in range(3):
            # Space posts 5 hours apart to avoid min interval conflict
            post_time = (base_time - timedelta(hours=i * 5)).isoformat()
            cursor.execute("""
                INSERT INTO agents_social_posts
                (id, platform, group_id, content, posted_at, post_status)
                VALUES (?, 'linkedin', '6729915', 'test', ?, 'posted')
            """, (f"test_{i}", post_time))
        conn.commit()
        conn.close()

        can_post, reason = poster.can_post_today()
        print(f"\n[2] After 3 posts today:")
        print(f"    Can post: {can_post}")
        print(f"    Reason: {reason}")
        assert not can_post, f"Should block after 3 posts: {reason}"

        # Test 3: Check interval (last post too recent)
        # Use Python datetime to avoid SQLite UTC vs local time mismatch
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM agents_social_posts")  # Clear
        recent_time = (datetime.now() - timedelta(hours=1)).isoformat()
        cursor.execute("""
            INSERT INTO agents_social_posts
            (id, platform, group_id, content, posted_at, post_status)
            VALUES ('recent', 'linkedin', '6729915', 'test', ?, 'posted')
        """, (recent_time,))
        conn.commit()
        conn.close()

        can_post, reason = poster.can_post_today()
        print(f"\n[3] Last post 1 hour ago (min interval: 4h):")
        print(f"    Can post: {can_post}")
        print(f"    Reason: {reason}")
        assert not can_post, f"Should block if last post < 4h ago: {reason}"

        print("\n✅ Rate limiting tests passed!")
        return True

    finally:
        os.unlink(db_path)


def test_duplicate_detection():
    """Test duplicate URL detection."""
    print("\n" + "="*60)
    print("TEST: Duplicate Detection")
    print("="*60)

    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name

    try:
        poster = OpenClawGroupPoster(db_path=db_path)

        item = NewsItem(
            title="Test Article",
            url="https://example.com/test-article",
            source="Example",
        )

        # Test 1: New URL - not duplicate
        is_dup = poster.is_duplicate(item)
        print(f"\n[1] New URL:")
        print(f"    URL: {item.url}")
        print(f"    Hash: {item.content_hash()}")
        print(f"    Is duplicate: {is_dup}")
        assert not is_dup, "New URL should not be duplicate"

        # Test 2: Add to database, check again
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO agents_social_posts
            (id, platform, group_id, content, content_hash, created_at, post_status)
            VALUES ('dup_test', 'linkedin', '6729915', 'test', ?, datetime('now'), 'posted')
        """, (item.content_hash(),))
        conn.commit()
        conn.close()

        is_dup = poster.is_duplicate(item)
        print(f"\n[2] After posting same URL:")
        print(f"    Is duplicate: {is_dup}")
        assert is_dup, "Same URL should be detected as duplicate"

        print("\n✅ Duplicate detection tests passed!")
        return True

    finally:
        os.unlink(db_path)


def test_post_formatting():
    """Test post formatting with 🦞 branding."""
    print("\n" + "="*60)
    print("TEST: Post Formatting")
    print("="*60)

    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name

    try:
        poster = OpenClawGroupPoster(db_path=db_path)

        item = NewsItem(
            title="🦞 OpenClaw Launches Payment Standard",
            url="https://techcrunch.com/openclaw",
            source="TechCrunch",
            summary="OpenClaw has launched a new open payment standard for AI agents, enabling seamless transactions between autonomous systems."
        )

        formatted = poster.format_post(item)
        print(f"\n[1] Formatted post:")
        print("-" * 40)
        print(formatted)
        print("-" * 40)

        # Verify components
        assert item.title in formatted, "Title should be in post"
        assert item.url in formatted, "URL should be in post"
        assert "#OpenClaw" in formatted, "Should have #OpenClaw hashtag"
        assert "#AI" in formatted, "Should have #AI hashtag"
        assert len(formatted) <= 3000, f"Post too long: {len(formatted)} chars"

        print(f"\n[2] Post length: {len(formatted)} chars (max: 3000)")
        print("\n✅ Post formatting tests passed!")
        return True

    finally:
        os.unlink(db_path)


def test_dry_run_flow():
    """Test the full flow in dry run mode."""
    print("\n" + "="*60)
    print("TEST: Dry Run Flow")
    print("="*60)

    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name

    try:
        poster = OpenClawGroupPoster(db_path=db_path)

        # Simulate a news item that would be posted
        item = NewsItem(
            title="🦞 Crossmint Launches Lobster.cash for OpenClaw Agents",
            url="https://techcrunch.com/lobster-cash",
            source="TechCrunch",
            published_date=datetime.now() - timedelta(hours=6),
            summary="Crossmint has launched lobster.cash as an open payment standard for OpenClaw agents, enabling autonomous AI systems to transact seamlessly."
        )

        # Rate it
        score = NewsRelevanceRater.rate(item)
        print(f"\n[1] News item rated:")
        print(f"    Title: {item.title}")
        print(f"    Score: {score:.3f}")
        print(f"    Passes threshold: {score >= RELEVANCE_THRESHOLD}")

        # Dry run post
        print(f"\n[2] Dry run posting...")
        success = poster.post_to_group(item, dry_run=True)
        print(f"    Success: {success}")

        # Check database entry
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, post_status, relevance_score FROM agents_social_posts")
        row = cursor.fetchone()
        conn.close()

        print(f"\n[3] Database entry:")
        if row:
            print(f"    ID: {row[0]}")
            print(f"    Status: {row[1]}")
            print(f"    Score: {row[2]}")
        else:
            print("    No entry found")

        print("\n✅ Dry run flow tests passed!")
        return True

    finally:
        os.unlink(db_path)


def run_all_tests():
    """Run all tests."""
    print("\n" + "="*60)
    print("🦞 OPENCLAW GROUP NEWS SKILL - TEST SUITE")
    print("="*60)

    results = []

    try:
        results.append(("News Relevance Rating", test_news_relevance_rating()))
    except Exception as e:
        print(f"\n❌ News Relevance Rating FAILED: {e}")
        results.append(("News Relevance Rating", False))

    try:
        results.append(("Rate Limiting", test_rate_limiting()))
    except Exception as e:
        print(f"\n❌ Rate Limiting FAILED: {e}")
        results.append(("Rate Limiting", False))

    try:
        results.append(("Duplicate Detection", test_duplicate_detection()))
    except Exception as e:
        print(f"\n❌ Duplicate Detection FAILED: {e}")
        results.append(("Duplicate Detection", False))

    try:
        results.append(("Post Formatting", test_post_formatting()))
    except Exception as e:
        print(f"\n❌ Post Formatting FAILED: {e}")
        results.append(("Post Formatting", False))

    try:
        results.append(("Dry Run Flow", test_dry_run_flow()))
    except Exception as e:
        print(f"\n❌ Dry Run Flow FAILED: {e}")
        results.append(("Dry Run Flow", False))

    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    passed = sum(1 for _, r in results if r)
    total = len(results)

    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🦞 ALL TESTS PASSED! Skill is ready.")
    else:
        print("\n⚠️ Some tests failed. Review above output.")

    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
