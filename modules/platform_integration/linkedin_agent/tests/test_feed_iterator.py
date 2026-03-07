#!/usr/bin/env python3
"""
Feed Iterator Test - DOM-First Feed Processing with Refresh.

Test Modes:
    --selenium: Pure Selenium DOM automation
    --iterate: Iterate through posts
    --engagement: Test engagement session
    --dry-run: Read only, no actions
    --info: Show test info only

Usage:
    python -m modules.platform_integration.linkedin_agent.tests.test_feed_iterator --selenium
    python -m modules.platform_integration.linkedin_agent.tests.test_feed_iterator --iterate --max-posts 10
    python -m modules.platform_integration.linkedin_agent.tests.test_feed_iterator --engagement --dry-run

WSP Compliance:
    - WSP 50: Pre-action verification (DOM selectors validated)
    - WSP 91: Observability (structured prints)
    - WSP 22: ModLog (DOM-first architecture per 2026-02-24)
"""

import argparse
import asyncio
import os
import sys
import time

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))))


def test_feed_iterator_selenium(
    max_posts: int = 5,
    skip_reposts: bool = True,
    dry_run: bool = False,
) -> dict:
    """
    Test Feed Iterator with pure Selenium DOM.

    Args:
        max_posts: Maximum posts to iterate through
        skip_reposts: Skip reposted content
        dry_run: Read only, no engagement

    Returns:
        dict with keys: success, posts_read, engage_worthy, reposts_skipped
    """
    from modules.platform_integration.linkedin_agent.tests.linkedin_browser import (
        get_linkedin_driver,
        ensure_linkedin_logged_in,
    )

    print("\n[FEED] Feed Iterator Test - Selenium Mode")
    print(f"[MODE] max_posts={max_posts} | skip_reposts={skip_reposts} | dry_run={dry_run}")
    print("=" * 60)

    result = {
        "success": False,
        "posts_read": 0,
        "engage_worthy": 0,
        "reposts_skipped": 0,
        "ai_posts": 0,
        "capital_posts": 0,
        "target_author_posts": 0,
        "errors": [],
    }

    # Connect to Chrome
    try:
        driver = get_linkedin_driver()
        print(f"[OK] Connected to Chrome: {driver.title[:50]}...")
    except Exception as e:
        print(f"[ERROR] Failed to connect: {e}")
        result["errors"].append(str(e))
        return result

    if not ensure_linkedin_logged_in(driver):
        result["errors"].append("LinkedIn login not confirmed")
        return result

    # Refresh feed (F5 equivalent)
    print("\n[STEP 1] Refreshing feed...")
    driver.get("https://www.linkedin.com/feed/")
    time.sleep(3)

    # Verify on LinkedIn
    if "linkedin.com" not in driver.current_url:
        print(f"[ERROR] Not on LinkedIn: {driver.current_url}")
        result["errors"].append("Not on LinkedIn")
        return result

    print(f"[OK] On LinkedIn feed: {driver.current_url[:50]}...")

    # Iterate through posts using DOM
    print(f"\n[STEP 2] Iterating through {max_posts} posts...")
    step_delay = float(os.getenv("LINKEDIN_ACTION_DELAY_SEC", "1") or 1)

    for i in range(max_posts):
        print(f"\n[POST {i+1}/{max_posts}]")
        time.sleep(step_delay)

        # Read post at index i
        try:
            post_data = driver.execute_script("""
            const index = arguments[0];

            // Find all post content containers
            const textBoxes = document.querySelectorAll('span[data-testid="expandable-text-box"]');
            if (textBoxes.length <= index) {
                return { ok: false, error: 'Post not found', index: index, found: textBoxes.length };
            }

            const textBox = textBoxes[index];
            const content = textBox.textContent || '';

            // Find post container (traverse up)
            let postContainer = textBox;
            for (let j = 0; j < 15; j++) {
                postContainer = postContainer.parentElement;
                if (!postContainer) break;
                if (postContainer.classList.contains('feed-shared-update-v2') ||
                    postContainer.getAttribute('data-urn') ||
                    postContainer.classList.contains('occludable-update')) {
                    break;
                }
            }

            // Extract author
            let author = 'Unknown';
            if (postContainer) {
                const authorLink = postContainer.querySelector('a[href*="/in/"]') ||
                                   postContainer.querySelector('a[href*="/company/"]');
                if (authorLink) {
                    const authorSpan = authorLink.querySelector('span[dir="ltr"] span') ||
                                       authorLink.querySelector('span');
                    if (authorSpan) author = authorSpan.textContent.trim();
                }
            }

            // Detect repost
            let isRepost = false;
            if (postContainer) {
                const headerText = postContainer.innerText.slice(0, 300).toLowerCase();
                if (headerText.includes('reposted') || headerText.includes('shared')) {
                    isRepost = true;
                }
            }

            // AI detection
            const aiKeywords = [
                'ai', 'artificial intelligence', 'machine learning', 'llm',
                'gpt', 'chatgpt', 'claude', 'gemini', 'openai', 'anthropic',
                'autonomous', 'agent', 'automation', 'neural', 'deep learning'
            ];

            // Capital pushback
            const capitalKeywords = [
                'series a', 'series b', 'funding round', 'venture capital',
                'raised', 'seed round', 'investor', 'valuation'
            ];

            // Target authors
            const targetAuthors = [
                'salim ismail', 'peter diamandis', 'ray kurzweil', 'pieter franken'
            ];

            const contentLower = content.toLowerCase();
            const authorLower = author.toLowerCase();

            const isAiPost = aiKeywords.some(kw => contentLower.includes(kw));
            const isCapitalPost = capitalKeywords.some(kw => contentLower.includes(kw));
            const isTargetAuthor = targetAuthors.some(name => authorLower.includes(name));

            const shouldEngage = !isRepost && (isAiPost || isCapitalPost || isTargetAuthor);
            const engagementReason = isAiPost ? 'ai_topic' :
                                     isCapitalPost ? 'capital_pushback' :
                                     isTargetAuthor ? 'target_author' : 'none';

            return {
                ok: true,
                index: index,
                author: author,
                content: content.substring(0, 200),
                content_length: content.length,
                is_repost: isRepost,
                is_ai_post: isAiPost,
                is_capital_post: isCapitalPost,
                is_target_author: isTargetAuthor,
                should_engage: shouldEngage,
                engagement_reason: engagementReason,
            };
            """, i)

            if not post_data or not post_data.get('ok'):
                # Try scrolling for more posts
                print(f"  [SCROLL] Loading more posts...")
                driver.execute_script("window.scrollBy(0, 800);")
                time.sleep(2)

                # Retry
                post_data = driver.execute_script("""
                    const textBoxes = document.querySelectorAll('span[data-testid="expandable-text-box"]');
                    return { found: textBoxes.length };
                """)
                print(f"  [INFO] Posts in DOM after scroll: {post_data.get('found', 0)}")
                continue

            result["posts_read"] += 1

            # Display post info
            is_repost = post_data.get('is_repost', False)
            should_engage = post_data.get('should_engage', False)
            reason = post_data.get('engagement_reason', 'none')
            author = post_data.get('author', 'Unknown')[:30]
            preview = post_data.get('content', '')[:50].replace('\n', ' ')

            status = "[REPOST]" if is_repost else "[ENGAGE]" if should_engage else "[SKIP]"
            print(f"  {status} {author}")
            print(f"  Reason: {reason} | Preview: {preview}...")

            # Track stats
            if is_repost:
                result["reposts_skipped"] += 1
            if should_engage:
                result["engage_worthy"] += 1
            if post_data.get('is_ai_post'):
                result["ai_posts"] += 1
            if post_data.get('is_capital_post'):
                result["capital_posts"] += 1
            if post_data.get('is_target_author'):
                result["target_author_posts"] += 1

        except Exception as e:
            print(f"  [ERROR] {e}")
            result["errors"].append(str(e))

    # Summary
    result["success"] = result["posts_read"] > 0
    print(f"\n{'='*60}")
    print(f"[{'SUCCESS' if result['success'] else 'PARTIAL'}] Feed Iterator Complete!")
    print(f"  Posts read: {result['posts_read']}")
    print(f"  Engage-worthy: {result['engage_worthy']}")
    print(f"  Reposts skipped: {result['reposts_skipped']}")
    print(f"  AI posts: {result['ai_posts']}")
    print(f"  Capital pushback: {result['capital_posts']}")
    print(f"  Target authors: {result['target_author_posts']}")

    return result


async def test_feed_iterator_async(max_posts: int = 5, dry_run: bool = True) -> dict:
    """
    Test Feed Iterator using LinkedInActions class.

    Args:
        max_posts: Maximum posts to iterate
        dry_run: Read only, no engagement

    Returns:
        dict with results
    """
    from modules.infrastructure.browser_actions.src.linkedin_actions import LinkedInActions

    print("\n[FEED] Feed Iterator Test - LinkedInActions (Async)")
    print(f"[MODE] max_posts={max_posts} | dry_run={dry_run}")
    print("=" * 60)

    result = {
        "success": False,
        "posts_collected": 0,
        "errors": [],
    }

    try:
        # Initialize LinkedInActions
        browser_port = int(os.getenv("CHROME_PORT", "9222"))
        linkedin = LinkedInActions(browser_port=browser_port)

        # Refresh and iterate
        posts = await linkedin.iterate_feed(
            max_posts=max_posts,
            skip_reposts=True,
            engagement_filter=False,  # Get all posts, not just engage-worthy
        )

        result["posts_collected"] = len(posts)
        result["success"] = len(posts) > 0

        # Display results
        print(f"\n[OK] Collected {len(posts)} posts")
        for i, post in enumerate(posts):
            author = post.get('author', 'Unknown')[:30]
            reason = post.get('engagement_reason', 'none')
            is_repost = post.get('is_repost', False)
            print(f"  [{i+1}] {author} | repost={is_repost} | reason={reason}")

        linkedin.close()

    except Exception as e:
        print(f"[ERROR] {e}")
        result["errors"].append(str(e))

    return result


async def test_engagement_session_async(
    duration_minutes: int = 5,
    max_engagements: int = 3,
    dry_run: bool = True,
) -> dict:
    """
    Test engagement session with DOM-based iterator.

    Args:
        duration_minutes: Max session duration
        max_engagements: Max engagements
        dry_run: Read only, no engagement

    Returns:
        dict with results
    """
    from modules.infrastructure.browser_actions.src.linkedin_actions import LinkedInActions

    print("\n[SESSION] Engagement Session Test - DOM Iterator")
    print(f"[MODE] duration={duration_minutes}min | max={max_engagements} | dry_run={dry_run}")
    print("=" * 60)

    result = {
        "success": False,
        "posts_read": 0,
        "engagements": 0,
        "errors": [],
    }

    if dry_run:
        print("[DRY RUN] Engagement actions will be simulated")

    try:
        browser_port = int(os.getenv("CHROME_PORT", "9222"))
        linkedin = LinkedInActions(browser_port=browser_port)

        if dry_run:
            # Just iterate without engaging
            posts = await linkedin.iterate_feed(
                max_posts=max_engagements * 2,
                skip_reposts=True,
                engagement_filter=True,
            )

            result["posts_read"] = len(posts)
            result["success"] = True

            print(f"\n[OK] Found {len(posts)} engagement opportunities:")
            for i, post in enumerate(posts):
                author = post.get('author', 'Unknown')[:30]
                reason = post.get('engagement_reason', 'none')
                print(f"  [{i+1}] {author} | {reason}")
                print(f"       Would {'like + reply' if reason in ['ai_topic', 'capital_pushback'] else 'like'}")

        else:
            # Real engagement session
            session_result = await linkedin.run_engagement_session(
                duration_minutes=duration_minutes,
                max_engagements=max_engagements,
                use_dom_iterator=True,
            )

            result["posts_read"] = session_result.posts_read
            result["engagements"] = session_result.engagements
            result["success"] = session_result.success
            result["details"] = session_result.details

            print(f"\n[{'SUCCESS' if result['success'] else 'PARTIAL'}] Session complete!")
            print(f"  Posts read: {result['posts_read']}")
            print(f"  Engagements: {result['engagements']}")

        linkedin.close()

    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        result["errors"].append(str(e))

    return result


def test_feed_iterator_info():
    """Show test info without running."""
    print("\n[FEED] Feed Iterator Test")
    print("=" * 60)
    print("Purpose: Test DOM-first feed processing with refresh")
    print("")
    print("Steps:")
    print("  1. Refresh feed (navigate to /feed/)")
    print("  2. Iterate through posts using DOM selectors")
    print("  3. Detect: reposts, AI posts, capital pushback, target authors")
    print("  4. Track engagement opportunities")
    print("")
    print("DOM Selectors:")
    print("  - Post content: span[data-testid='expandable-text-box']")
    print("  - Author: a[href*='/in/'] span or a[href*='/company/'] span")
    print("  - Repost: header text contains 'reposted' or 'shared'")
    print("")
    print("Engagement Reasons:")
    print("  - ai_topic: AI/ML/automation keywords detected")
    print("  - capital_pushback: VC/funding keywords (FoundUps alternative)")
    print("  - target_author: Salim Ismail, Peter Diamandis, etc.")
    print("")
    print("Usage:")
    print("  python -m ...test_feed_iterator --selenium")
    print("  python -m ...test_feed_iterator --iterate --max-posts 10")
    print("  python -m ...test_feed_iterator --engagement --dry-run")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Feed Iterator Test")
    parser.add_argument("--selenium", action="store_true", help="Run Selenium DOM test")
    parser.add_argument("--iterate", action="store_true", help="Run async iterator test")
    parser.add_argument("--engagement", action="store_true", help="Run engagement session test")
    parser.add_argument("--max-posts", type=int, default=5, help="Max posts to process")
    parser.add_argument("--dry-run", action="store_true", help="Read only, no actions")
    parser.add_argument("--info", action="store_true", help="Show test info only")

    args = parser.parse_args()

    if args.info:
        test_feed_iterator_info()
    elif args.selenium:
        result = test_feed_iterator_selenium(
            max_posts=args.max_posts,
            skip_reposts=True,
            dry_run=args.dry_run,
        )
        sys.exit(0 if result["success"] else 1)
    elif args.iterate:
        result = asyncio.run(test_feed_iterator_async(
            max_posts=args.max_posts,
            dry_run=args.dry_run,
        ))
        sys.exit(0 if result["success"] else 1)
    elif args.engagement:
        result = asyncio.run(test_engagement_session_async(
            max_engagements=args.max_posts,
            dry_run=args.dry_run,
        ))
        sys.exit(0 if result["success"] else 1)
    else:
        test_feed_iterator_info()
        print("\n[TIP] Add --selenium, --iterate, or --engagement to run tests")
