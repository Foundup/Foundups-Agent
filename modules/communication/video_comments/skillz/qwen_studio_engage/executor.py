"""
Qwen Studio Engage - Autonomous YouTube Studio Comment Engagement

Executor for the qwen_studio_engage WRE Skill.
Implements WSP 96 Micro Chain-of-Thought paradigm.
"""

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class CommentData:
    """Extracted comment data from Studio UI"""
    author_name: str
    comment_text: str
    timestamp: str
    likes_count: int = 0
    replies_count: int = 0
    already_liked: bool = False
    already_hearted: bool = False


@dataclass
class EngagementDecision:
    """Qwen's engagement decision"""
    sentiment: str  # positive/neutral/negative
    engagement_value: int  # 1-5
    recommended_action: str  # like_only/like_and_reply/creator_heart/ignore
    reply_text: Optional[str] = None
    confidence: float = 0.0
    reasoning: str = ""


@dataclass
class EngagementResult:
    """Result of engagement attempt"""
    success: bool
    action_taken: str
    like_success: bool = False
    heart_success: bool = False
    reply_success: bool = False
    error: Optional[str] = None
    duration_ms: int = 0


async def execute_skill(
    channel_id: str,
    max_comments_to_check: int = 10,
    engagement_policy: Optional[Dict[str, Any]] = None,
    existing_browser: bool = True,
) -> Dict[str, Any]:
    """
    Execute the Qwen Studio Engage skill.

    Args:
        channel_id: YouTube channel ID (e.g., UC-LSSlOZwpGIRIYihaz8zCw)
        max_comments_to_check: Max comments to analyze per execution
        engagement_policy: Engagement thresholds and rules
        existing_browser: Use existing logged-in browser session

    Returns:
        Dict with execution results and metrics
    """
    start_time = datetime.now()

    # Default engagement policy
    if engagement_policy is None:
        engagement_policy = {
            "like_threshold": 0.7,
            "reply_threshold": 0.8,
            "ignore_spam": True,
            "ignore_toxicity": True,
            "brand_voice": "helpful, friendly, professional"
        }

    logger.info(f"[QWEN-STUDIO] Starting autonomous engagement")
    logger.info(f"[QWEN-STUDIO] Channel: {channel_id}")
    logger.info(f"[QWEN-STUDIO] Max comments: {max_comments_to_check}")

    try:
        # Step 1: Connect to existing browser
        browser = await _connect_to_browser(existing_browser)

        # Step 2: Navigate to Studio inbox
        await _navigate_to_studio_inbox(browser, channel_id)

        # Step 3: Get comments from UI (Vision)
        comments = await _extract_comments_from_ui(browser, max_comments_to_check)

        logger.info(f"[QWEN-STUDIO] Found {len(comments)} comments to analyze")

        # Step 4: Process each comment
        results = []
        for comment in comments:
            result = await _process_comment(
                browser,
                comment,
                engagement_policy
            )
            results.append(result)

            # Brief pause between comments (human-like)
            await asyncio.sleep(2)

        # Calculate metrics
        duration = (datetime.now() - start_time).total_seconds() * 1000

        engagements_made = sum(1 for r in results if r.success)
        likes_given = sum(1 for r in results if r.like_success)
        hearts_given = sum(1 for r in results if r.heart_success)
        replies_sent = sum(1 for r in results if r.reply_success)

        summary = {
            "success": True,
            "comments_analyzed": len(comments),
            "engagements_made": engagements_made,
            "likes_given": likes_given,
            "hearts_given": hearts_given,
            "replies_sent": replies_sent,
            "engagement_rate": engagements_made / len(comments) if comments else 0,
            "duration_ms": int(duration),
            "results": [_result_to_dict(r) for r in results]
        }

        logger.info(f"[QWEN-STUDIO] ✅ Complete: {engagements_made}/{len(comments)} engaged")
        return summary

    except Exception as e:
        logger.error(f"[QWEN-STUDIO] ❌ Skill execution failed: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "comments_analyzed": 0,
            "engagements_made": 0,
        }


async def _connect_to_browser(existing_browser: bool):
    """Connect to existing browser session (user already logged in)"""
    from modules.infrastructure.foundups_selenium.src.browser_manager import get_browser_manager

    browser_manager = get_browser_manager()

    # Use existing youtube_move2japan profile (already logged in)
    # API: get_browser(browser_type, profile_name, options)
    browser = browser_manager.get_browser(
        browser_type='chrome',
        profile_name='youtube_move2japan'
    )

    logger.info("[QWEN-STUDIO] Connected to existing browser session")
    return browser


async def _navigate_to_studio_inbox(browser, channel_id: str):
    """Navigate to YouTube Studio comments inbox"""
    studio_url = f"https://studio.youtube.com/channel/{channel_id}/comments/inbox"

    browser.get(studio_url)
    logger.info(f"[QWEN-STUDIO] Navigated to Studio inbox")

    # Wait for Studio UI to load (React app)
    await asyncio.sleep(5)


async def _extract_comments_from_ui(browser, max_comments: int) -> List[CommentData]:
    """
    Extract comment data from Studio UI using Vision.

    For now, returns mock data. Full Vision integration requires:
    - Vision OCR to extract comment text
    - Vision element detection to find action bars
    - Vision state detection (already liked/hearted)
    """
    # TODO: Implement Vision extraction
    # This would use ActionRouter with Vision driver to:
    # 1. Identify comment elements
    # 2. Extract text via OCR
    # 3. Detect action bar state (likes, hearts)

    # Mock data for now (replace with Vision)
    logger.warning("[QWEN-STUDIO] Using mock comment data (Vision extraction TODO)")

    return [
        CommentData(
            author_name="@testuser1",
            comment_text="This is so helpful! Thank you for the information about moving to Japan.",
            timestamp="2 hours ago",
            likes_count=0,
            replies_count=0,
            already_liked=False,
            already_hearted=False,
        )
    ]


async def _process_comment(
    browser,
    comment: CommentData,
    engagement_policy: Dict[str, Any]
) -> EngagementResult:
    """
    Process a single comment through Qwen analysis → Gemma validation → Vision engagement.
    """
    start_time = datetime.now()

    logger.info(f"[QWEN-STUDIO] Analyzing comment from {comment.author_name}")

    # Step 1: Qwen sentiment analysis
    decision = await _qwen_analyze_comment(comment, engagement_policy)

    logger.info(f"[QWEN-STUDIO] Qwen decision: {decision.recommended_action} (confidence: {decision.confidence:.2f})")

    # Step 2: Gemma validation
    validation_passed = await _gemma_validate_decision(decision)

    if not validation_passed:
        logger.warning(f"[QWEN-STUDIO] Gemma validation failed - skipping engagement")
        return EngagementResult(
            success=False,
            action_taken="skipped_validation_failed",
            error="Gemma validation failed"
        )

    # Step 3: Check confidence thresholds
    if decision.recommended_action == "ignore":
        logger.info(f"[QWEN-STUDIO] Skipping comment (low value)")
        return EngagementResult(
            success=True,
            action_taken="ignored",
        )

    # Check thresholds
    if decision.recommended_action == "like_and_reply":
        if decision.confidence < engagement_policy["reply_threshold"]:
            decision.recommended_action = "like_only"  # Downgrade to like only
            logger.info(f"[QWEN-STUDIO] Downgraded to like_only (confidence < threshold)")

    # Step 4: Execute engagement via Vision
    engagement_result = await _execute_engagement_vision(
        browser,
        decision
    )

    duration = (datetime.now() - start_time).total_seconds() * 1000
    engagement_result.duration_ms = int(duration)

    # Step 5: Record pattern (Pattern Memory)
    await _record_pattern(comment, decision, engagement_result)

    return engagement_result


async def _qwen_analyze_comment(
    comment: CommentData,
    engagement_policy: Dict[str, Any]
) -> EngagementDecision:
    """
    Qwen strategic analysis of comment sentiment and engagement value.

    TODO: Integrate actual Qwen model.
    For now, uses rule-based heuristics.
    """
    text = comment.comment_text.lower()

    # Simple sentiment analysis (replace with Qwen)
    if any(word in text for word in ['thank', 'helpful', 'love', 'great', 'amazing']):
        sentiment = "positive"
        engagement_value = 4
    elif any(word in text for word in ['question', '?', 'how', 'where', 'when']):
        sentiment = "neutral"
        engagement_value = 5  # Questions are high value
    else:
        sentiment = "neutral"
        engagement_value = 3

    # Determine action
    if engagement_value >= 5:
        recommended_action = "like_and_reply"
        reply_text = "Thanks for your question! I'll create content about this soon. 🎌"
    elif engagement_value >= 4:
        recommended_action = "creator_heart"
        reply_text = None
    elif engagement_value >= 3:
        recommended_action = "like_only"
        reply_text = None
    else:
        recommended_action = "ignore"
        reply_text = None

    return EngagementDecision(
        sentiment=sentiment,
        engagement_value=engagement_value,
        recommended_action=recommended_action,
        reply_text=reply_text,
        confidence=0.85,
        reasoning=f"Sentiment: {sentiment}, Value: {engagement_value}/5"
    )


async def _gemma_validate_decision(decision: EngagementDecision) -> bool:
    """
    Gemma validation of Qwen's decision.

    Checks:
    - Required fields present
    - Values in valid ranges
    - Reply quality (if present)
    """
    # Check required fields
    if not decision.sentiment or not decision.recommended_action:
        return False

    # Check engagement value range
    if not (1 <= decision.engagement_value <= 5):
        return False

    # Check confidence range
    if not (0.0 <= decision.confidence <= 1.0):
        return False

    # Validate action type
    valid_actions = ['like_only', 'like_and_reply', 'creator_heart', 'ignore']
    if decision.recommended_action not in valid_actions:
        return False

    # If like_and_reply, must have reply text
    if decision.recommended_action == 'like_and_reply':
        if not decision.reply_text or len(decision.reply_text) < 10:
            return False

    return True


async def _vision_verified_action(
    bridge,
    driver,
    click_description: str,
    verify_description: str,
    action_name: str,
    pattern_memory,
    max_retries: int = 3,
    dom_selector: Optional[str] = None,
    expected_state_change: Optional[str] = None
) -> Dict[str, Any]:
    """
    Self-correcting vision action with DOM state verification.

    Pattern: Action → Pic → DOM Verify → If NO (retry + store) → If YES (proceed)

    Args:
        bridge: UI-TARS Bridge for vision operations
        driver: Selenium WebDriver instance
        click_description: What to click (e.g., "thumbs up button")
        verify_description: How to verify success (e.g., "thumbs up is now blue")
        action_name: Name for pattern memory (e.g., "like")
        pattern_memory: Pattern memory instance for learning
        max_retries: Max retry attempts
        dom_selector: CSS selector for DOM verification (optional)
        expected_state_change: Expected DOM attribute change (e.g., "aria-pressed=true")

    Returns:
        Dict with success, confidence, and pattern data
    """
    for attempt in range(max_retries):
        try:
            # CAPTURE BEFORE STATE (DOM ground truth)
            dom_before = None
            if dom_selector:
                dom_before = driver.execute_script("""
                    const el = document.querySelector(arguments[0]);
                    if (!el) return null;
                    return {
                        aria_pressed: el.getAttribute('aria-pressed'),
                        aria_label: el.getAttribute('aria-label'),
                        classes: Array.from(el.classList),
                        text: el.textContent.trim()
                    };
                """, dom_selector)
                logger.info(f"[DOM-VERIFY] {action_name} BEFORE: {dom_before}")

            # ACTION: Click element via UI-TARS vision
            click_result = await bridge.click(click_description, driver=driver)

            if not click_result.success:
                logger.warning(f"[VISION-VERIFY] {action_name} click failed: {click_result.error}")
                continue

            # Wait for UI update
            await asyncio.sleep(0.5)

            # CAPTURE AFTER STATE (DOM ground truth)
            dom_after = None
            if dom_selector:
                dom_after = driver.execute_script("""
                    const el = document.querySelector(arguments[0]);
                    if (!el) return null;
                    return {
                        aria_pressed: el.getAttribute('aria-pressed'),
                        aria_label: el.getAttribute('aria-label'),
                        classes: Array.from(el.classList),
                        text: el.textContent.trim()
                    };
                """, dom_selector)
                logger.info(f"[DOM-VERIFY] {action_name} AFTER: {dom_after}")

            # VERIFY: Check DOM state change (deterministic)
            verification_passed = False
            confidence = 0.0

            if dom_before and dom_after and expected_state_change:
                # Parse expected change (e.g., "aria-pressed=true")
                attr, expected_val = expected_state_change.split('=')

                if dom_before.get(attr) != expected_val and dom_after.get(attr) == expected_val:
                    # State changed as expected!
                    verification_passed = True
                    confidence = 1.0  # DOM verification = 100% confidence
                    logger.info(f"[DOM-VERIFY] ✓ {action_name} verified - {attr}: {dom_before.get(attr)} → {dom_after.get(attr)}")
                else:
                    logger.warning(f"[DOM-VERIFY] ✗ {action_name} - Expected {attr}={expected_val}, got BEFORE={dom_before.get(attr)}, AFTER={dom_after.get(attr)}")
            else:
                # Fallback to vision verification (KNOWN TO GIVE FALSE POSITIVES)
                verify_result = await bridge.verify(verify_description, driver=driver)
                verification_passed = verify_result.success and verify_result.confidence >= 0.7
                confidence = verify_result.confidence
                logger.warning(f"[VISION-VERIFY] Using vision (UNRELIABLE): {verification_passed}, confidence={confidence:.2f}")

            if verification_passed:
                # Store successful pattern
                await _store_action_pattern(
                    pattern_memory,
                    action_name=action_name,
                    success=True,
                    click_description=click_description,
                    verify_description=verify_description,
                    confidence=confidence,
                    attempt=attempt + 1
                )

                return {
                    "success": True,
                    "confidence": confidence,
                    "attempts": attempt + 1,
                    "dom_verified": dom_selector is not None
                }

            # FAILED VERIFICATION: Store pattern of what was actually found
            logger.warning(f"[VERIFY] ✗ {action_name} not verified (attempt {attempt+1}/{max_retries})")

            # Store failed pattern for learning
            await _store_action_pattern(
                pattern_memory,
                action_name=action_name,
                success=False,
                click_description=click_description,
                verify_description=verify_description,
                confidence=confidence,
                attempt=attempt + 1,
                notes=f"Verification failed - DOM state didn't change as expected"
            )

        except Exception as e:
            logger.error(f"[VERIFY] {action_name} error on attempt {attempt+1}: {e}")
            continue

    # All retries exhausted
    return {
        "success": False,
        "confidence": 0.0,
        "attempts": max_retries,
        "error": "Max retries exhausted",
        "dom_verified": False
    }


async def _store_action_pattern(
    pattern_memory,
    action_name: str,
    success: bool,
    click_description: str,
    verify_description: str,
    confidence: float,
    attempt: int,
    notes: Optional[str] = None
):
    """Store action pattern for recursive learning."""
    try:
        import json
        from modules.infrastructure.wre_core.src.pattern_memory import SkillOutcome

        outcome = SkillOutcome(
            execution_id=f"vision_{action_name}_{datetime.now().timestamp()}",
            skill_name="qwen_studio_engage",
            agent="ui-tars",
            timestamp=datetime.now().isoformat(),
            input_context=json.dumps({
                "action": action_name,
                "click_description": click_description,
                "verify_description": verify_description,
                "attempt": attempt
            }),
            output_result=json.dumps({
                "success": success,
                "confidence": confidence
            }),
            success=success,
            pattern_fidelity=confidence,
            outcome_quality=1.0 if success else 0.0,
            execution_time_ms=500,  # Approximate
            step_count=2,  # Click + Verify
            failed_at_step=2 if not success else None,
            notes=notes
        )

        pattern_memory.store_outcome(outcome)
        logger.debug(f"[PATTERN-MEMORY] Stored {action_name} pattern: success={success}, confidence={confidence:.2f}")

    except Exception as e:
        logger.debug(f"[PATTERN-MEMORY] Failed to store pattern: {e}")


async def _execute_engagement_vision(
    browser,
    decision: EngagementDecision
) -> EngagementResult:
    """
    Execute engagement action using Vision AI with self-correcting loop.

    Based on VISION_UI_REFERENCE.md specifications.
    Uses recursive pattern: Action → Pic → Ask → Verify → Retry
    """
    from modules.infrastructure.foundups_vision.src.ui_tars_bridge import UITarsBridge
    from modules.infrastructure.wre_core.src.pattern_memory import PatternMemory

    # Initialize UI-TARS Bridge
    bridge = UITarsBridge(browser_port=9222)
    await bridge.connect()

    # Initialize Pattern Memory
    pattern_memory = PatternMemory()

    result = EngagementResult(
        success=False,
        action_taken=decision.recommended_action
    )

    try:
        if decision.recommended_action == "like_only":
            # Self-correcting LIKE action
            like_result = await _vision_verified_action(
                bridge,
                browser,  # Pass Selenium driver
                click_description="gray thumbs up button in the comment action bar on the first comment",
                verify_description="thumbs up button is now blue or highlighted",
                action_name="like",
                pattern_memory=pattern_memory
            )
            result.like_success = like_result["success"]
            result.success = like_result["success"]

        elif decision.recommended_action == "creator_heart":
            # Self-correcting HEART action
            heart_result = await _vision_verified_action(
                bridge,
                browser,  # Pass Selenium driver
                click_description="gray heart icon in the comment action bar on the first comment",
                verify_description="heart icon is now red or filled",
                action_name="heart",
                pattern_memory=pattern_memory
            )
            result.heart_success = heart_result["success"]
            result.success = heart_result["success"]

        elif decision.recommended_action == "like_and_reply":
            # 1. Self-correcting LIKE action
            like_result = await _vision_verified_action(
                bridge,
                browser,  # Pass Selenium driver
                click_description="gray thumbs up button in the comment action bar on the first comment",
                verify_description="thumbs up button is now blue or highlighted",
                action_name="like",
                pattern_memory=pattern_memory
            )
            result.like_success = like_result["success"]

            # 2. Self-correcting REPLY button click
            await asyncio.sleep(0.5)
            reply_open_result = await _vision_verified_action(
                bridge,
                browser,  # Pass Selenium driver
                click_description="Reply button on the first comment",
                verify_description="reply text box is now visible below the comment",
                action_name="reply_open",
                pattern_memory=pattern_memory
            )

            if reply_open_result["success"]:
                # 3. Type reply text
                await asyncio.sleep(1)
                type_result = await bridge.type_text(
                    description="reply text input field below the comment",
                    text=decision.reply_text,
                    driver=browser  # Pass Selenium driver
                )

                if type_result.success:
                    # 4. Submit reply
                    await asyncio.sleep(0.5)
                    submit_result = await _vision_verified_action(
                        bridge,
                        browser,  # Pass Selenium driver
                        click_description="blue Reply submit button at bottom right of reply box",
                        verify_description="reply is now visible under the comment with the text I typed",
                        action_name="reply_submit",
                        pattern_memory=pattern_memory
                    )
                    result.reply_success = submit_result["success"]

            result.success = result.like_success and result.reply_success

        logger.info(f"[QWEN-STUDIO] Engagement complete: {result.action_taken} - Success: {result.success}")

    except Exception as e:
        logger.error(f"[QWEN-STUDIO] Engagement failed: {e}")
        result.error = str(e)

    return result


async def _record_pattern(
    comment: CommentData,
    decision: EngagementDecision,
    result: EngagementResult
):
    """Record engagement outcome to Pattern Memory for learning"""
    try:
        from modules.infrastructure.wre_core.src.pattern_memory import PatternMemory

        memory = PatternMemory()

        # TODO: Implement actual pattern storage
        # For now, just log
        logger.info(f"[QWEN-STUDIO] Pattern recorded: {decision.sentiment} → {result.action_taken} → {result.success}")

    except Exception as e:
        logger.debug(f"[QWEN-STUDIO] Pattern recording failed: {e}")


def _result_to_dict(result: EngagementResult) -> Dict[str, Any]:
    """Convert EngagementResult to dict for JSON serialization"""
    return {
        "success": result.success,
        "action_taken": result.action_taken,
        "like_success": result.like_success,
        "heart_success": result.heart_success,
        "reply_success": result.reply_success,
        "error": result.error,
        "duration_ms": result.duration_ms,
    }
