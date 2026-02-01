#!/usr/bin/env python3
"""
Layer 0: Context Gate - Validate target post before Digital Twin action.

Test Modes:
    --selenium: Pure Selenium DOM automation
    --info: Show layer info only

Usage:
    python -m modules.platform_integration.linkedin_agent.tests.test_layer0_context_gate
    python -m modules.platform_integration.linkedin_agent.tests.test_layer0_context_gate --selenium
"""

import argparse
import json
import os
import sys
import time
from typing import Any, Dict, Optional

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))))


def test_layer0_selenium(prompt_ai_gate: bool = False) -> dict:
    """
    Test Layer 0 with pure Selenium.
    
    Returns:
        dict with keys: success, author, post_url, is_ai_post
    """
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from modules.platform_integration.linkedin_agent.tests.linkedin_browser import (
        get_linkedin_driver,
        ensure_linkedin_logged_in,
        check_lm_studio_ready,
    )
    try:
        from modules.ai_intelligence.ai_gateway.src.ai_gateway import AIGateway
        AI_GATEWAY_AVAILABLE = True
    except ImportError:
        AI_GATEWAY_AVAILABLE = False
        AIGateway = None
    try:
        from holo_index.qwen_advisor.llm_engine import QwenInferenceEngine
        QWEN_AVAILABLE = True
    except ImportError:
        QWEN_AVAILABLE = False
        QwenInferenceEngine = None

    print("\n[L0] Layer 0: Context Gate - Selenium Mode")
    print("=" * 60)

    result = {
        "success": False,
        "author": None,
        "post_url": None,
        "is_ai_post": False,
        "is_promoted": False,
        "is_repost": False,
        "ai_gate_passed": False,
        "error": None
    }

    # Connect to Chrome (debug port or BrowserManager)
    try:
        driver = get_linkedin_driver()
        print(f"[OK] Connected to Chrome: {driver.title[:50]}...")
    except Exception as e:
        print(f"[ERROR] Failed to connect: {e}")
        result["error"] = str(e)
        return result

    if not ensure_linkedin_logged_in(driver):
        result["error"] = "LinkedIn login not confirmed"
        return result

    require_lm_studio = os.getenv("LINKEDIN_REQUIRE_LM_STUDIO", "true").lower() in {"1", "true", "yes"}
    if require_lm_studio and not check_lm_studio_ready():
        result["error"] = "LM Studio not ready"
        return result

    # Refresh feed (F5 equivalent)
    print("[STEP 0.0] Refresh feed...")
    driver.refresh()
    time.sleep(3)

    # Verify we're on LinkedIn feed
    current_url = driver.current_url
    if "linkedin.com" not in current_url:
        print(f"[ERROR] Not on LinkedIn: {current_url}")
        result["error"] = "Not on LinkedIn"
        return result

    print(f"[OK] On LinkedIn: {current_url}")
    result["post_url"] = current_url

    # Step 0.2: Locate top post author
    author_selectors = [
        ".update-components-actor__title span[aria-hidden='true']",
        ".feed-shared-actor__name",
        ".update-components-actor__name",
        ".feed-shared-update-v2__actor-name",
    ]

    author_name = None
    for selector in author_selectors:
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            if elements:
                author_name = elements[0].text.strip()
                if author_name:
                    print(f"[OK] Top post author: {author_name}")
                    result["author"] = author_name
                    break
        except Exception:
            continue

    if not author_name:
        print("[WARNING] Could not extract author name from DOM")
        # Try broader search
        try:
            first_post = driver.find_element(By.CSS_SELECTOR, ".feed-shared-update-v2")
            post_text = first_post.text[:200]
            print(f"[INFO] First post preview: {post_text}...")
        except Exception as e:
            print(f"[WARNING] Could not find first post: {e}")

    # Step 0.3: Detect promoted/repost (AI gate)
    def _parse_json_block(text: str) -> Optional[Dict[str, Any]]:
        if not text:
            return None
        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1 or end <= start:
            return None
        try:
            return json.loads(text[start:end + 1])
        except Exception:
            return None

    def _ai_classify_post(post_text: str) -> Dict[str, Any]:
        prompt = (
            "Classify this LinkedIn post. Return JSON only:\n"
            '{"is_promoted": true|false, "is_repost": true|false, '
            '"confidence": 0.0-1.0, "rationale": "short"}\n'
            f"POST:\n{post_text}"
        )
        verdict = {
            "is_promoted": False,
            "is_repost": False,
            "confidence": 0.0,
            "source": "heuristic",
        }

        use_api = os.getenv("LINKEDIN_USE_AI_GATEWAY", "true").lower() in {"1", "true", "yes"}
        if use_api and AI_GATEWAY_AVAILABLE:
            try:
                gateway = AIGateway()
                api_result = gateway.call_with_fallback(prompt, task_type="analysis", max_retries=2)
                if api_result and api_result.success:
                    parsed = _parse_json_block(api_result.response)
                    if parsed:
                        verdict.update({
                            "is_promoted": bool(parsed.get("is_promoted", False)),
                            "is_repost": bool(parsed.get("is_repost", False)),
                            "confidence": float(parsed.get("confidence", 0.0)),
                            "source": f"api:{api_result.provider}",
                        })
                        return verdict
            except Exception:
                pass

        if QWEN_AVAILABLE:
            try:
                qwen = QwenInferenceEngine()
                response = qwen.generate(prompt, max_tokens=120)
                parsed = _parse_json_block(response)
                if parsed:
                    verdict.update({
                        "is_promoted": bool(parsed.get("is_promoted", False)),
                        "is_repost": bool(parsed.get("is_repost", False)),
                        "confidence": float(parsed.get("confidence", 0.0)),
                        "source": "qwen_local",
                    })
                    return verdict
            except Exception:
                pass

        normalized = f" {post_text.lower()} "
        promoted_tokens = ["promoted", "sponsored", "advertisement"]
        repost_tokens = ["repost", "reposted", "reshared"]
        verdict["is_promoted"] = any(token in normalized for token in promoted_tokens) or " ad " in normalized
        verdict["is_repost"] = any(token in normalized for token in repost_tokens)
        return verdict

    try:
        first_post = driver.find_element(By.CSS_SELECTOR, ".feed-shared-update-v2")
        post_text = first_post.text.strip()
        gate = _ai_classify_post(post_text)
        result["is_promoted"] = bool(gate.get("is_promoted"))
        result["is_repost"] = bool(gate.get("is_repost"))
        if result["is_promoted"] or result["is_repost"]:
            reason = "promoted" if result["is_promoted"] else "repost"
            print(f"[OK] AI gate detected {reason} - skip comment/repost")
        else:
            print("[OK] AI gate clear (not promoted/repost)")
    except Exception as e:
        print(f"[WARNING] Could not classify promoted/repost status: {e}")

    # Step 0.4: AI-post gate (keyword detection)
    ai_keywords = [
        "AI", "artificial intelligence", "AGI", "machine learning",
        "neural network", "GPT", "LLM", "automation", "robot",
        "future of work", "job displacement", "singularity"
    ]

    try:
        if "first_post" not in locals():
            first_post = driver.find_element(By.CSS_SELECTOR, ".feed-shared-update-v2")
        post_content = first_post.text.lower()
        
        matched_keywords = [kw for kw in ai_keywords if kw.lower() in post_content]
        
        if matched_keywords:
            print(f"[OK] AI-post detected! Keywords: {matched_keywords[:3]}")
            result["is_ai_post"] = True
        else:
            print("[INFO] No AI keywords detected in top post")
            result["is_ai_post"] = False
            
    except Exception as e:
        print(f"[WARNING] Could not analyze post content: {e}")

    # Step 0.5: Capture post permalink (if available)
    try:
        permalink_elem = driver.find_element(
            By.CSS_SELECTOR, 
            ".feed-shared-update-v2 a[href*='/posts/'], .feed-shared-update-v2 a[href*='/activity/']"
        )
        permalink = permalink_elem.get_attribute("href")
        if permalink:
            result["post_url"] = permalink
            print(f"[OK] Post permalink: {permalink[:60]}...")
    except Exception:
        print("[INFO] Using feed URL (no permalink found)")

    # AI gate (optional interactive prompt)
    if result["is_promoted"] or result["is_repost"]:
        result["ai_gate_passed"] = False
    elif prompt_ai_gate:
        answer = input("AI post? (y/n): ").strip().lower()
        result["ai_gate_passed"] = answer in {"y", "yes"}
    else:
        result["ai_gate_passed"] = result["is_ai_post"]

    # Success if we're on LinkedIn (author/AI gate are advisory)
    result["success"] = True
    print(f"\n[SUCCESS] Layer 0 complete!")
    print(f"  Author: {result['author']}")
    print(f"  Promoted: {result['is_promoted']}")
    print(f"  Repost: {result['is_repost']}")
    print(f"  AI Post: {result['is_ai_post']}")
    print(f"  AI Gate: {result['ai_gate_passed']}")
    print(f"  URL: {result['post_url'][:60] if result['post_url'] else 'N/A'}...")

    return result


def test_layer0_info():
    """Show layer info without running."""
    print("\n[L0] Layer 0: Context Gate")
    print("=" * 60)
    print("Purpose: Validate browser is on target LinkedIn post")
    print("")
    print("Steps:")
    print("  0.1 Verify LinkedIn feed URL")
    print("  0.2 Extract top post author name")
    print("  0.3 AI gate: detect Promoted/Repost (API -> Qwen -> heuristic)")
    print("  0.4 AI-post gate (keyword detection)")
    print("  0.5 Capture post permalink for Layer 1")
    print("")
    print("DOM Selectors:")
    print("  - Author: .update-components-actor__title span[aria-hidden='true']")
    print("  - Post: .feed-shared-update-v2")
    print("  - Permalink: a[href*='/posts/']")
    print("")
    print("Validation:")
    print("  - URL contains linkedin.com")
    print("  - Author name extracted (advisory)")
    print("  - Promoted/Sponsored/Repost detected (skip)")
    print("  - AI keywords present (advisory)")
    print("")
    print("Usage:")
    print("  python -m ...test_layer0_context_gate --selenium")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Layer 0: Context Gate Test")
    parser.add_argument("--selenium", action="store_true", help="Run with pure Selenium")
    parser.add_argument("--prompt-ai-gate", action="store_true", help="Prompt for AI gate decision")
    parser.add_argument("--info", action="store_true", help="Show layer info only")

    args = parser.parse_args()

    if args.info:
        test_layer0_info()
    elif args.selenium:
        result = test_layer0_selenium(prompt_ai_gate=args.prompt_ai_gate)
        sys.exit(0 if result["success"] else 1)
    else:
        test_layer0_info()
        print("\n[TIP] Add --selenium to run the test")
