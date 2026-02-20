"""
LinkedIn Actions - Vision-Based Engagement for 0102 Autonomy

All engagement actions use UI-TARS Vision for:
- Reading and understanding posts
- Intelligent reply decisions
- Contextual engagement
- Dynamic UI handling

Selenium only for: navigation, login (known forms)

WSP Compliance:
    - WSP 3: Infrastructure domain
    - WSP 77: AI Overseer integration
    - WSP 80: DAE coordination
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from .action_router import ActionRouter, DriverType, RoutingResult

logger = logging.getLogger(__name__)


@dataclass
class LinkedInPost:
    """Represents a LinkedIn post extracted via vision."""
    post_id: str
    author: str
    content: str
    timestamp: str
    likes: int = 0
    comments: int = 0
    is_relevant: bool = False
    suggested_reply: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "post_id": self.post_id,
            "author": self.author,
            "content": self.content,
            "timestamp": self.timestamp,
            "likes": self.likes,
            "comments": self.comments,
            "is_relevant": self.is_relevant,
            "suggested_reply": self.suggested_reply,
        }


@dataclass
class LinkedInActionResult:
    """Result of a LinkedIn action."""
    success: bool
    action: str
    post_id: Optional[str] = None
    posts_read: int = 0
    engagements: int = 0
    error: Optional[str] = None
    duration_ms: int = 0
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "action": self.action,
            "post_id": self.post_id,
            "posts_read": self.posts_read,
            "engagements": self.engagements,
            "error": self.error,
            "duration_ms": self.duration_ms,
            "details": self.details,
        }


class LinkedInActions:
    """
    LinkedIn vision-based engagement actions.
    
    Uses UI-TARS Vision for ALL engagement (reading, understanding, replying).
    Selenium only for navigation and login.
    
    Usage:
        linkedin = LinkedInActions(profile='linkedin_foundups')
        
        # Read and understand feed
        posts = await linkedin.read_feed(max_posts=10)
        
        # Engage with relevant posts
        for post in posts:
            if post.is_relevant:
                await linkedin.reply_to_post(post.post_id, post.suggested_reply)
        
        # Autonomous engagement session
        result = await linkedin.run_engagement_session(duration_minutes=15)
    """

    # Engagement keywords for 012's interests
    RELEVANCE_KEYWORDS = [
        'startup', 'founder', 'entrepreneur', 'ai', 'autonomous',
        'japan', 'move2japan', 'geozai', 'foundups', 'coding',
        'developer', 'software', 'innovation', 'blockchain', 'web3',
    ]

    def __init__(
        self,
        profile: str = 'linkedin_foundups',
        router: ActionRouter = None,
        ai_provider: str = 'grok',
    ) -> None:
        """
        Initialize LinkedIn actions.
        
        Args:
            profile: Browser profile (logged into LinkedIn account)
            router: Pre-configured ActionRouter (optional)
            ai_provider: AI provider for response generation
        """
        self.profile = profile
        self.router = router or ActionRouter(profile=profile)
        self.ai_provider = ai_provider
        
        # Try to import LLM for intelligent responses
        try:
            from modules.communication.video_comments.src.llm_comment_generator import LLMCommentGenerator
            self.llm = LLMCommentGenerator(provider=ai_provider)
            self._llm_available = True
            logger.info(f"[LINKEDIN] LLM available via {ai_provider}")
        except ImportError:
            self.llm = None
            self._llm_available = False
            logger.warning("[LINKEDIN] LLM not available, will use templates")
        
        # Session stats
        self._session_stats = {
            'posts_read': 0,
            'posts_engaged': 0,
            'likes_given': 0,
            'comments_made': 0,
            'connections_sent': 0,
        }
        
        logger.info(f"[LINKEDIN] Actions initialized with profile={profile}")

    async def navigate_to_feed(self) -> RoutingResult:
        """
        Navigate to LinkedIn feed.
        Uses Selenium (fast, known URL).
        """
        result = await self.router.execute(
            'navigate',
            {'url': 'https://www.linkedin.com/feed/'},
            driver=DriverType.SELENIUM,
        )
        
        if result.success:
            await asyncio.sleep(2)  # Wait for feed to load
            logger.info("[LINKEDIN] Navigated to feed")
        
        return result

    async def navigate_to_profile(self, profile_url: str) -> RoutingResult:
        """Navigate to a LinkedIn profile."""
        return await self.router.execute(
            'navigate',
            {'url': profile_url},
            driver=DriverType.SELENIUM,
        )

    async def read_feed(self, max_posts: int = 10) -> List[LinkedInPost]:
        """
        Read and understand posts in LinkedIn feed.
        Uses UI-TARS Vision to see and extract post content.
        
        Args:
            max_posts: Maximum posts to read
            
        Returns:
            List of LinkedInPost objects with content and relevance
        """
        logger.info(f"[LINKEDIN] Reading feed (max {max_posts} posts)")
        
        # Navigate to feed first
        nav_result = await self.navigate_to_feed()
        if not nav_result.success:
            logger.error(f"[LINKEDIN] Failed to navigate: {nav_result.error}")
            return []
        
        posts = []
        scroll_count = 0
        max_scrolls = max_posts // 3 + 1  # ~3 posts per scroll
        
        while len(posts) < max_posts and scroll_count < max_scrolls:
            # Use vision to read visible posts
            read_result = await self.router.execute(
                'find_by_description',
                {
                    'description': 'LinkedIn feed posts with author name, content text, and engagement counts',
                    'extract_text': True,
                },
                driver=DriverType.VISION,
            )
            
            if read_result.success and read_result.result_data.get('extracted_posts'):
                for post_data in read_result.result_data['extracted_posts']:
                    post = self._parse_post(post_data)
                    if post and post.post_id not in [p.post_id for p in posts]:
                        # Evaluate relevance
                        post.is_relevant = self._is_relevant(post.content)
                        if post.is_relevant and self._llm_available:
                            post.suggested_reply = await self._generate_reply(post)
                        posts.append(post)
                        self._session_stats['posts_read'] += 1
            
            # Scroll down for more posts
            await self.router.execute(
                'scroll_to_element',
                {'description': 'scroll down to see more posts'},
                driver=DriverType.VISION,
            )
            await asyncio.sleep(1)
            scroll_count += 1
        
        logger.info(f"[LINKEDIN] Read {len(posts)} posts, {sum(1 for p in posts if p.is_relevant)} relevant")
        return posts

    def _parse_post(self, post_data: Dict[str, Any]) -> Optional[LinkedInPost]:
        """Parse vision-extracted post data into LinkedInPost."""
        try:
            return LinkedInPost(
                post_id=post_data.get('id', f"post_{datetime.now().timestamp()}"),
                author=post_data.get('author', 'Unknown'),
                content=post_data.get('content', ''),
                timestamp=post_data.get('timestamp', 'recent'),
                likes=int(post_data.get('likes', 0)),
                comments=int(post_data.get('comments', 0)),
            )
        except Exception as e:
            logger.warning(f"[LINKEDIN] Failed to parse post: {e}")
            return None

    def _is_relevant(self, content: str) -> bool:
        """Determine if post content is relevant for 012's interests."""
        content_lower = content.lower()
        return any(kw in content_lower for kw in self.RELEVANCE_KEYWORDS)

    async def _generate_reply(self, post: LinkedInPost) -> str:
        """Generate intelligent reply using LLM."""
        if not self._llm_available:
            return self._template_reply(post)
        
        try:
            prompt = f"""Generate a professional LinkedIn comment for this post.
            
Author: {post.author}
Content: {post.content[:500]}

Guidelines:
- Professional but friendly tone
- Add value to the conversation
- Keep under 200 characters
- Reference specific points from the post
- Represent FoundUps/Move2Japan brand positively
"""
            response = self.llm.generate(prompt)
            return response[:200] if response else self._template_reply(post)
        except Exception as e:
            logger.warning(f"[LINKEDIN] LLM failed: {e}")
            return self._template_reply(post)

    def _template_reply(self, post: LinkedInPost) -> str:
        """Generate template reply when LLM unavailable."""
        templates = [
            "Great insights! Thanks for sharing.",
            "This resonates with our work at FoundUps. Appreciate the perspective!",
            "Valuable points here. Looking forward to more content like this.",
            "Well said! This aligns with what we're building.",
        ]
        import random
        return random.choice(templates)

    async def like_post(self, post_id: str) -> LinkedInActionResult:
        """
        Like a LinkedIn post using UI-TARS Vision.
        
        Args:
            post_id: Post identifier (or description for vision)
            
        Returns:
            LinkedInActionResult
        """
        logger.info(f"[LINKEDIN] Liking post {post_id[:20]}...")
        
        result = await self.router.execute(
            'click_by_description',
            {'description': 'Like button (thumbs up icon) on the post'},
            driver=DriverType.VISION,
        )
        
        if result.success:
            self._session_stats['likes_given'] += 1
        
        return LinkedInActionResult(
            success=result.success,
            action="like_post",
            post_id=post_id,
            error=result.error,
            duration_ms=result.duration_ms,
        )

    async def reply_to_post(
        self,
        post_id: str,
        reply_text: str,
    ) -> LinkedInActionResult:
        """
        Reply to a LinkedIn post using UI-TARS Vision.
        
        Workflow:
        1. Find and click comment button
        2. Wait for comment input to appear
        3. Type reply (character by character for human-like behavior)
        4. Submit comment
        
        Args:
            post_id: Post identifier
            reply_text: Comment text to post
            
        Returns:
            LinkedInActionResult
        """
        logger.info(f"[LINKEDIN] Replying to post: {reply_text[:50]}...")
        
        # Step 1: Click comment button
        comment_btn = await self.router.execute(
            'click_by_description',
            {'description': 'Comment button on the post'},
            driver=DriverType.VISION,
        )
        
        if not comment_btn.success:
            return LinkedInActionResult(
                success=False,
                action="reply_to_post",
                post_id=post_id,
                error="Could not find comment button",
            )
        
        await asyncio.sleep(0.5)
        
        # Step 2: Click in comment input
        input_click = await self.router.execute(
            'click_by_description',
            {'description': 'Comment text input field or "Add a comment" placeholder'},
            driver=DriverType.VISION,
        )
        
        if not input_click.success:
            return LinkedInActionResult(
                success=False,
                action="reply_to_post",
                post_id=post_id,
                error="Could not find comment input",
            )
        
        await asyncio.sleep(0.3)
        
        # Step 3: Type reply (slowly, human-like)
        # UI-TARS types character by character
        type_result = await self.router.execute(
            'click_by_description',
            {
                'description': 'comment input field',
                'text': reply_text,
                'slow_type': True,  # Character by character
            },
            driver=DriverType.VISION,
        )
        
        await asyncio.sleep(0.5)
        
        # Step 4: Submit comment
        submit_result = await self.router.execute(
            'click_by_description',
            {'description': 'Post comment button or send button'},
            driver=DriverType.VISION,
        )
        
        success = submit_result.success
        if success:
            self._session_stats['comments_made'] += 1
            self._session_stats['posts_engaged'] += 1
        
        return LinkedInActionResult(
            success=success,
            action="reply_to_post",
            post_id=post_id,
            engagements=1 if success else 0,
            error=submit_result.error,
            duration_ms=comment_btn.duration_ms + type_result.duration_ms + submit_result.duration_ms,
        )

    async def like_and_reply(
        self,
        post_id: str,
        reply_text: str,
    ) -> LinkedInActionResult:
        """
        Like and reply to a post in one session.
        
        Args:
            post_id: Post identifier
            reply_text: Comment text
            
        Returns:
            LinkedInActionResult with both outcomes
        """
        logger.info(f"[LINKEDIN] Like and reply to {post_id[:20]}")
        
        # Like first
        like_result = await self.like_post(post_id)
        
        # Then reply
        reply_result = await self.reply_to_post(post_id, reply_text)
        
        return LinkedInActionResult(
            success=like_result.success or reply_result.success,
            action="like_and_reply",
            post_id=post_id,
            engagements=2 if (like_result.success and reply_result.success) else 1 if reply_result.success else 0,
            details={
                "like_success": like_result.success,
                "reply_success": reply_result.success,
            },
            duration_ms=like_result.duration_ms + reply_result.duration_ms,
        )

    async def run_engagement_session(
        self,
        duration_minutes: int = 15,
        max_engagements: int = 10,
    ) -> LinkedInActionResult:
        """
        Run an autonomous engagement session.
        
        0102 reads feed, identifies relevant posts, and engages intelligently.
        
        Args:
            duration_minutes: Max session duration
            max_engagements: Max posts to engage with
            
        Returns:
            LinkedInActionResult with session summary
        """
        logger.info(f"[LINKEDIN] Starting {duration_minutes}min engagement session")
        start_time = datetime.now()
        engagements = 0
        
        # Read feed
        posts = await self.read_feed(max_posts=max_engagements * 2)
        relevant_posts = [p for p in posts if p.is_relevant]
        
        logger.info(f"[LINKEDIN] Found {len(relevant_posts)} relevant posts")
        
        for post in relevant_posts[:max_engagements]:
            # Check time limit
            elapsed = (datetime.now() - start_time).seconds / 60
            if elapsed >= duration_minutes:
                logger.info("[LINKEDIN] Time limit reached")
                break
            
            # Engage with post
            if post.suggested_reply:
                result = await self.like_and_reply(post.post_id, post.suggested_reply)
            else:
                result = await self.like_post(post.post_id)
            
            if result.success:
                engagements += 1
            
            # Human-like delay between engagements
            await asyncio.sleep(5 + (engagements % 3) * 2)
        
        elapsed_ms = int((datetime.now() - start_time).total_seconds() * 1000)
        
        return LinkedInActionResult(
            success=engagements > 0,
            action="engagement_session",
            posts_read=len(posts),
            engagements=engagements,
            duration_ms=elapsed_ms,
            details={
                "relevant_posts": len(relevant_posts),
                "session_stats": self._session_stats.copy(),
            },
        )

    def get_session_stats(self) -> Dict[str, int]:
        """Get session statistics."""
        return self._session_stats.copy()

    async def run_digital_twin_flow(
        self,
        comment_text: str,
        repost_text: str,
        schedule_date: str,
        schedule_time: str,
        mentions: Optional[List[str]] = None,
        identity_cycle: Optional[List[str]] = None,
        dry_run: bool = False,
    ) -> LinkedInActionResult:
        """
        Execute the LinkedIn Digital Twin workflow (L0-L3).
        
        Skill: linkedin_comment_digital_twin.json
        
        Flow:
            L0: Context gate (validate post, AI gate)
            L1: Post comment with @mentions, UI-TARS verification
            L2: Identity cycle — switch accounts and like comment
            L3: Schedule repost with thoughts
        
        Args:
            comment_text: 012 Digital Twin comment text
            repost_text: Repost-with-thoughts text
            schedule_date: Scheduled date (calendar selection)
            schedule_time: Scheduled time (15-min increments)
            mentions: Mentions to insert (default: @foundups)
            identity_cycle: Identities to like comment
            dry_run: If True, validate without submitting
        
        Returns:
            LinkedInActionResult with layer results
        """
        logger.info("[LINKEDIN] Starting Digital Twin flow (L0-L3)")
        
        mentions = mentions or ["@foundups"]
        identity_cycle = identity_cycle or ["FOUNDUPS", "Move2Japan", "UnDaoDu", "EDUIT, Inc"]
        
        layer_results = {}
        start_time = datetime.now()
        
        # Import layer tests
        try:
            from modules.platform_integration.linkedin_agent.tests.test_layer0_context_gate import (
                test_layer0_selenium,
            )
            from modules.platform_integration.linkedin_agent.tests.test_layer1_comment import (
                test_layer1_selenium,
            )
            from modules.platform_integration.linkedin_agent.tests.test_layer2_identity_likes import (
                test_layer2_selenium,
            )
            from modules.platform_integration.linkedin_agent.tests.test_layer3_schedule_repost import (
                test_layer3_selenium,
            )
        except ImportError as e:
            logger.error(f"[LINKEDIN] Digital Twin tests not available: {e}")
            return LinkedInActionResult(
                success=False,
                action="digital_twin_flow",
                error=f"Layer tests unavailable: {e}",
            )
        
        # L0: Context Gate
        logger.info("[LINKEDIN] L0: Context Gate")
        l0_result = test_layer0_selenium()
        layer_results["L0"] = l0_result
        
        if not l0_result.get("success"):
            return LinkedInActionResult(
                success=False,
                action="digital_twin_flow",
                error=f"L0 failed: {l0_result.get('error')}",
                details={"layer_results": layer_results},
            )
        
        ai_gate_passed = l0_result.get("ai_post", False)
        if not ai_gate_passed:
            logger.info("[LINKEDIN] AI gate not passed — skipping engagement")
            return LinkedInActionResult(
                success=True,
                action="digital_twin_flow",
                details={"layer_results": layer_results, "skipped": "AI gate not passed"},
            )
        
        # L1: Comment
        logger.info("[LINKEDIN] L1: Comment")
        l1_result = test_layer1_selenium(dry_run=dry_run, ai_gate_passed=ai_gate_passed)
        layer_results["L1"] = l1_result
        
        if not l1_result.get("success"):
            return LinkedInActionResult(
                success=False,
                action="digital_twin_flow",
                error=f"L1 failed: {l1_result.get('error')}",
                details={"layer_results": layer_results},
            )
        
        # L2: Identity Likes
        logger.info("[LINKEDIN] L2: Identity Likes")
        l2_result = test_layer2_selenium(dry_run=dry_run)
        layer_results["L2"] = l2_result
        
        # L3: Schedule Repost
        logger.info("[LINKEDIN] L3: Schedule Repost")
        l3_result = test_layer3_selenium(
            schedule_date=schedule_date,
            schedule_time=schedule_time,
            dry_run=dry_run,
        )
        layer_results["L3"] = l3_result
        
        elapsed_ms = int((datetime.now() - start_time).total_seconds() * 1000)
        
        all_success = all(
            r.get("success", False)
            for r in [l0_result, l1_result, l2_result, l3_result]
        )
        
        self._session_stats["posts_engaged"] += 1
        self._session_stats["comments_made"] += 1 if l1_result.get("success") else 0
        
        logger.info(f"[LINKEDIN] Digital Twin flow complete: {all_success}")
        
        return LinkedInActionResult(
            success=all_success,
            action="digital_twin_flow",
            engagements=1 if all_success else 0,
            duration_ms=elapsed_ms,
            details={"layer_results": layer_results},
        )

    def close(self) -> None:
        """Close router and release resources."""
        self.router.close()
        logger.info(f"[LINKEDIN] Closed. Stats: {self._session_stats}")


# Factory function
def create_linkedin_actions(profile: str = 'linkedin_foundups') -> LinkedInActions:
    """Create LinkedInActions instance."""
    return LinkedInActions(profile=profile)


# Test function
async def _test_linkedin():
    """Test LinkedIn actions."""
    linkedin = LinkedInActions(profile='linkedin_foundups')
    
    # Test engagement session
    result = await linkedin.run_engagement_session(
        duration_minutes=5,
        max_engagements=3,
    )
    
    print(f"Result: {result.to_dict()}")
    
    linkedin.close()


if __name__ == "__main__":
    asyncio.run(_test_linkedin())


