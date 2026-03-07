#!/usr/bin/env python3
"""
LinkedIn Company Poster Skill

Posts updates and articles to FoundUps LinkedIn company page.
Signature: 0102🦞

Usage:
    # Post update
    python -m modules.ai_intelligence.ai_overseer.skillz.linkedin_company_poster --post "Your content here"

    # Write article
    python -m modules.ai_intelligence.ai_overseer.skillz.linkedin_company_poster --article "Title" --body "Article body"

    # Test article modal
    python -m modules.ai_intelligence.ai_overseer.skillz.linkedin_company_poster --test-article
"""

import argparse
import logging
import sys
import time
from pathlib import Path
from typing import Optional, Tuple

# Add repo root to path
REPO_ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(REPO_ROOT))

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

# Constants
COMPANY_ID = "1263645"
COMPANY_URL = f"https://www.linkedin.com/company/{COMPANY_ID}/admin/page-posts/published/"
ARTICLE_URL = f"https://www.linkedin.com/article/new/?author=urn%3Ali%3Afs_normalized_company%3A{COMPANY_ID}"
SIGNATURE = "0102🦞"
DEFAULT_HASHTAGS = "#FoundUps #pAVS #0102"


def get_browser():
    """Get or create LinkedIn browser session."""
    try:
        from modules.infrastructure.foundups_selenium.src.browser_manager import get_browser_manager
        manager = get_browser_manager()
        browser = manager.get_browser("chrome", f"linkedin_{COMPANY_ID}")
        return browser
    except Exception as e:
        logger.warning(f"BrowserManager fallback: {e}")
        # Fallback to direct selenium
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        options = Options()
        profile_dir = "O:/Foundups-Agent/modules/platform_integration/linkedin_agent/data/chrome_profile"
        options.add_argument(f"--user-data-dir={profile_dir}")
        options.add_argument("--remote-debugging-port=9223")
        return webdriver.Chrome(options=options)


def format_post(content: str, signature: str = SIGNATURE) -> str:
    """Format post with signature and hashtags."""
    return f"{content}\n\n{signature} {DEFAULT_HASHTAGS}"


def post_update(content: str, signature: str = SIGNATURE) -> Tuple[bool, str]:
    """
    Post an update to the FoundUps LinkedIn company page.

    Args:
        content: The post content
        signature: Signature to append (default: 0102🦞)

    Returns:
        Tuple of (success, message)
    """
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.action_chains import ActionChains

    formatted_content = format_post(content, signature)
    logger.info(f"[LINKEDIN] Posting update ({len(formatted_content)} chars)")

    try:
        driver = get_browser()

        # Navigate to company page with share param
        share_url = f"{COMPANY_URL}?share=true"
        driver.get(share_url)
        time.sleep(3)

        # Find text editor
        wait = WebDriverWait(driver, 10)
        text_area = wait.until(EC.presence_of_element_located((
            By.CSS_SELECTOR, "div.ql-editor"
        )))

        # Clear and type content
        text_area.click()
        time.sleep(0.5)

        # Use JavaScript to insert content (more reliable)
        driver.execute_script(
            "arguments[0].innerHTML = arguments[1]",
            text_area,
            formatted_content.replace('\n', '<br>')
        )
        time.sleep(1)

        # Find and click Post button
        post_selectors = [
            "//button[contains(@class, 'share-actions__primary-action') and not(contains(@aria-label, 'Schedule'))]",
            "//button[text()='Post']",
            "//button[contains(@class, 'artdeco-button--primary')]"
        ]

        post_button = None
        for selector in post_selectors:
            try:
                post_button = driver.find_element(By.XPATH, selector)
                if post_button.is_enabled():
                    break
            except:
                continue

        if not post_button:
            return False, "Could not find Post button"

        # Click with ActionChains for reliability
        ActionChains(driver).move_to_element(post_button).click().perform()
        time.sleep(3)

        # Verify redirect (success indicator)
        if "share=true" not in driver.current_url:
            logger.info("[SUCCESS] Post published!")
            return True, "Post published successfully"
        else:
            return False, "Post may not have been published (no redirect)"

    except Exception as e:
        logger.error(f"[ERROR] Post failed: {e}")
        return False, str(e)


def open_article_editor() -> Tuple[bool, str]:
    """
    Open the LinkedIn article editor using direct URL.

    Returns:
        Tuple of (success, message)
    """
    logger.info("[LINKEDIN] Opening article editor via direct URL...")

    try:
        driver = get_browser()

        # Use direct article URL (012 provided this)
        driver.get(ARTICLE_URL)
        time.sleep(3)

        # Verify we're in article editor
        current_url = driver.current_url
        logger.info(f"[NAV] Current URL: {current_url}")

        if "article" in current_url.lower():
            logger.info("[SUCCESS] Article editor opened!")
            return True, f"Article editor opened: {current_url}"
        else:
            # Take screenshot for debugging
            screenshot_path = REPO_ROOT / "linkedin_article_debug.png"
            driver.save_screenshot(str(screenshot_path))
            logger.info(f"[DEBUG] Screenshot saved: {screenshot_path}")
            return False, f"Unexpected page: {current_url}"

    except Exception as e:
        logger.error(f"[ERROR] Failed to open article editor: {e}")
        return False, str(e)


def write_article(title: str, body: str, signature: str = SIGNATURE) -> Tuple[bool, str]:
    """
    Write an article to the FoundUps LinkedIn page.

    Args:
        title: Article title
        body: Article body (can include markdown)
        signature: Signature to append

    Returns:
        Tuple of (success, message)
    """
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.keys import Keys

    logger.info(f"[LINKEDIN] Writing article: {title}")

    try:
        driver = get_browser()

        # Navigate directly to article editor
        driver.get(ARTICLE_URL)
        time.sleep(4)

        wait = WebDriverWait(driver, 15)

        # Find title field - LinkedIn article uses contenteditable h1
        title_selectors = [
            "h1[data-placeholder]",
            "h1[contenteditable='true']",
            "[data-placeholder='Title']",
            ".article-title-input",
        ]

        title_field = None
        for selector in title_selectors:
            try:
                title_field = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                logger.info(f"[FOUND] Title field: {selector}")
                break
            except:
                continue

        if title_field:
            title_field.click()
            time.sleep(0.3)
            title_field.send_keys(title)
            logger.info(f"[TYPED] Title: {title}")
            time.sleep(0.5)

        # Find body field - LinkedIn uses ProseMirror editor
        body_selectors = [
            ".ProseMirror",
            "[data-placeholder*='Write']",
            ".article-body-editor",
            "div[contenteditable='true']:not(h1)",
        ]

        body_field = None
        for selector in body_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for el in elements:
                    if el.is_displayed() and el != title_field:
                        body_field = el
                        logger.info(f"[FOUND] Body field: {selector}")
                        break
                if body_field:
                    break
            except:
                continue

        if body_field:
            body_field.click()
            time.sleep(0.3)
            formatted_body = f"{body}\n\n---\n{signature} {DEFAULT_HASHTAGS}"
            # Type slowly for LinkedIn's editor
            body_field.send_keys(formatted_body)
            logger.info(f"[TYPED] Body: {len(body)} chars")
            time.sleep(1)

        # Take screenshot
        screenshot_path = REPO_ROOT / "linkedin_article_ready.png"
        driver.save_screenshot(str(screenshot_path))
        logger.info(f"[SCREENSHOT] {screenshot_path}")

        logger.info("[SUCCESS] Article content entered. Review and click Publish.")
        return True, f"Article ready - review and publish. Screenshot: {screenshot_path}"

    except Exception as e:
        logger.error(f"[ERROR] Article write failed: {e}")
        return False, str(e)


def main():
    parser = argparse.ArgumentParser(
        description="LinkedIn Company Poster - Post to FoundUps page (0102🦞)"
    )
    parser.add_argument("--post", "-p", type=str, help="Post an update")
    parser.add_argument("--article", "-a", type=str, help="Article title")
    parser.add_argument("--body", "-b", type=str, help="Article body")
    parser.add_argument("--test-article", action="store_true", help="Test opening article editor")
    parser.add_argument("--signature", "-s", type=str, default=SIGNATURE, help="Custom signature")

    args = parser.parse_args()

    if args.test_article:
        success, msg = open_article_editor()
        print(f"{'[OK]' if success else '[FAIL]'} {msg}")
        sys.exit(0 if success else 1)

    if args.post:
        success, msg = post_update(args.post, args.signature)
        print(f"{'[OK]' if success else '[FAIL]'} {msg}")
        sys.exit(0 if success else 1)

    if args.article:
        if not args.body:
            print("[ERROR] --body required for article")
            sys.exit(1)
        success, msg = write_article(args.article, args.body, args.signature)
        print(f"{'[OK]' if success else '[FAIL]'} {msg}")
        sys.exit(0 if success else 1)

    parser.print_help()


if __name__ == "__main__":
    main()
