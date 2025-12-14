"""
X/Twitter Actions - Vision-Based Engagement for 0102 Autonomy

All engagement actions use UI-TARS Vision for:
- Reading and understanding tweets
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
class Tweet:
    """Represents a tweet extracted via vision."""
    tweet_id: str
    author: str
    handle: str
    content: str
    timestamp: str
    likes: int = 0
    retweets: int = 0
    replies: int = 0
    is_relevant: bool = False
    suggested_reply: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "tweet_id": self.tweet_id,
            "author": self.author,
            "handle": self.handle,
            "content": self.content,
            "timestamp": self.timestamp,
            "likes": self.likes,
            "retweets": self.retweets,
            "replies": self.replies,
            "is_relevant": self.is_relevant,
            "suggested_reply": self.suggested_reply,
        }


@dataclass
class XActionResult:
    """Result of an X/Twitter action."""
    success: bool
    action: str
    tweet_id: Optional[str] = None
    tweets_read: int = 0
    engagements: int = 0
    error: Optional[str] = None
    duration_ms: int = 0
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "action": self.action,
            "tweet_id": self.tweet_id,
            "tweets_read": self.tweets_read,
            "engagements": self.engagements,
            "error": self.error,
            "duration_ms": self.duration_ms,
            "details": self.details,
        }


class XActions:
    """
    X/Twitter vision-based engagement actions.
    
    Uses UI-TARS Vision for ALL engagement (reading, understanding, replying).
    Selenium only for navigation and login.
    
    Usage:
        x = XActions(profile='x_foundups')
        
        # Read and understand timeline
        tweets = await x.read_timeline(max_tweets=10)
        
        # Engage with relevant tweets
        for tweet in tweets:
            if tweet.is_relevant:
                await x.reply_to_tweet(tweet.tweet_id, tweet.suggested_reply)
        
        # Autonomous engagement session
        result = await x.run_engagement_session(duration_minutes=15)
    """

    # Engagement keywords for 012's interests
    RELEVANCE_KEYWORDS = [
        'startup', 'founder', 'entrepreneur', 'ai', 'autonomous',
        'japan', 'move2japan', 'geozai', 'foundups', 'coding',
        'developer', 'software', 'innovation', 'blockchain', 'web3',
        'buildinpublic', 'indiehacker', 'saas', 'tech',
    ]

    def __init__(
        self,
        profile: str = 'x_foundups',
        router: ActionRouter = None,
        ai_provider: str = 'grok',
    ) -> None:
        """
        Initialize X actions.
        
        Args:
            profile: Browser profile (logged into X account)
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
            logger.info(f"[X] LLM available via {ai_provider}")
        except ImportError:
            self.llm = None
            self._llm_available = False
            logger.warning("[X] LLM not available, will use templates")
        
        # Session stats
        self._session_stats = {
            'tweets_read': 0,
            'tweets_engaged': 0,
            'likes_given': 0,
            'replies_made': 0,
            'retweets_made': 0,
        }
        
        logger.info(f"[X] Actions initialized with profile={profile}")

    async def navigate_to_home(self) -> RoutingResult:
        """
        Navigate to X home timeline.
        Uses Selenium (fast, known URL).
        """
        result = await self.router.execute(
            'navigate',
            {'url': 'https://x.com/home'},
            driver=DriverType.SELENIUM,
        )
        
        if result.success:
            await asyncio.sleep(2)  # Wait for timeline to load
            logger.info("[X] Navigated to home")
        
        return result

    async def navigate_to_profile(self, handle: str) -> RoutingResult:
        """Navigate to an X profile."""
        url = f"https://x.com/{handle.lstrip('@')}"
        return await self.router.execute(
            'navigate',
            {'url': url},
            driver=DriverType.SELENIUM,
        )

    async def navigate_to_tweet(self, tweet_url: str) -> RoutingResult:
        """Navigate to a specific tweet."""
        return await self.router.execute(
            'navigate',
            {'url': tweet_url},
            driver=DriverType.SELENIUM,
        )

    async def read_timeline(self, max_tweets: int = 10) -> List[Tweet]:
        """
        Read and understand tweets in timeline.
        Uses UI-TARS Vision to see and extract tweet content.
        
        Args:
            max_tweets: Maximum tweets to read
            
        Returns:
            List of Tweet objects with content and relevance
        """
        logger.info(f"[X] Reading timeline (max {max_tweets} tweets)")
        
        # Navigate to home first
        nav_result = await self.navigate_to_home()
        if not nav_result.success:
            logger.error(f"[X] Failed to navigate: {nav_result.error}")
            return []
        
        tweets = []
        scroll_count = 0
        max_scrolls = max_tweets // 5 + 1  # ~5 tweets per scroll
        
        while len(tweets) < max_tweets and scroll_count < max_scrolls:
            # Use vision to read visible tweets
            read_result = await self.router.execute(
                'find_by_description',
                {
                    'description': 'Tweets in timeline with author name, handle, content, and engagement counts',
                    'extract_text': True,
                },
                driver=DriverType.VISION,
            )
            
            if read_result.success and read_result.result_data.get('extracted_tweets'):
                for tweet_data in read_result.result_data['extracted_tweets']:
                    tweet = self._parse_tweet(tweet_data)
                    if tweet and tweet.tweet_id not in [t.tweet_id for t in tweets]:
                        # Evaluate relevance
                        tweet.is_relevant = self._is_relevant(tweet.content)
                        if tweet.is_relevant and self._llm_available:
                            tweet.suggested_reply = await self._generate_reply(tweet)
                        tweets.append(tweet)
                        self._session_stats['tweets_read'] += 1
            
            # Scroll down for more tweets
            await self.router.execute(
                'scroll_to_element',
                {'description': 'scroll down to see more tweets'},
                driver=DriverType.VISION,
            )
            await asyncio.sleep(1)
            scroll_count += 1
        
        logger.info(f"[X] Read {len(tweets)} tweets, {sum(1 for t in tweets if t.is_relevant)} relevant")
        return tweets

    def _parse_tweet(self, tweet_data: Dict[str, Any]) -> Optional[Tweet]:
        """Parse vision-extracted tweet data into Tweet."""
        try:
            return Tweet(
                tweet_id=tweet_data.get('id', f"tweet_{datetime.now().timestamp()}"),
                author=tweet_data.get('author', 'Unknown'),
                handle=tweet_data.get('handle', '@unknown'),
                content=tweet_data.get('content', ''),
                timestamp=tweet_data.get('timestamp', 'recent'),
                likes=int(tweet_data.get('likes', 0)),
                retweets=int(tweet_data.get('retweets', 0)),
                replies=int(tweet_data.get('replies', 0)),
            )
        except Exception as e:
            logger.warning(f"[X] Failed to parse tweet: {e}")
            return None

    def _is_relevant(self, content: str) -> bool:
        """Determine if tweet content is relevant for 012's interests."""
        content_lower = content.lower()
        return any(kw in content_lower for kw in self.RELEVANCE_KEYWORDS)

    async def _generate_reply(self, tweet: Tweet) -> str:
        """Generate intelligent reply using LLM."""
        if not self._llm_available:
            return self._template_reply(tweet)
        
        try:
            prompt = f"""Generate a witty, engaging X/Twitter reply for this tweet.

Author: {tweet.author} (@{tweet.handle})
Content: {tweet.content[:280]}

Guidelines:
- Match X's conversational, punchy tone
- Keep under 280 characters
- Add value or insight
- Use 1-2 relevant emojis max
- Represent FoundUps/Move2Japan brand positively
- Be authentic, not corporate
"""
            response = self.llm.generate(prompt)
            return response[:280] if response else self._template_reply(tweet)
        except Exception as e:
            logger.warning(f"[X] LLM failed: {e}")
            return self._template_reply(tweet)

    def _template_reply(self, tweet: Tweet) -> str:
        """Generate template reply when LLM unavailable."""
        templates = [
            "This! 🔥",
            "Great thread, thanks for sharing!",
            "Solid take. Building something similar at FoundUps 👀",
            "100% agree. The future is autonomous.",
            "Love seeing this perspective 🚀",
        ]
        import random
        return random.choice(templates)

    async def like_tweet(self, tweet_id: str) -> XActionResult:
        """
        Like a tweet using UI-TARS Vision.
        
        Args:
            tweet_id: Tweet identifier (or description for vision)
            
        Returns:
            XActionResult
        """
        logger.info(f"[X] Liking tweet {tweet_id[:20]}...")
        
        result = await self.router.execute(
            'click_by_description',
            {'description': 'Heart/Like button on the tweet'},
            driver=DriverType.VISION,
        )
        
        if result.success:
            self._session_stats['likes_given'] += 1
        
        return XActionResult(
            success=result.success,
            action="like_tweet",
            tweet_id=tweet_id,
            error=result.error,
            duration_ms=result.duration_ms,
        )

    async def retweet(self, tweet_id: str) -> XActionResult:
        """
        Retweet using UI-TARS Vision.
        
        Args:
            tweet_id: Tweet identifier
            
        Returns:
            XActionResult
        """
        logger.info(f"[X] Retweeting {tweet_id[:20]}...")
        
        # Click retweet button
        retweet_btn = await self.router.execute(
            'click_by_description',
            {'description': 'Retweet button (arrows icon) on the tweet'},
            driver=DriverType.VISION,
        )
        
        if not retweet_btn.success:
            return XActionResult(
                success=False,
                action="retweet",
                tweet_id=tweet_id,
                error="Could not find retweet button",
            )
        
        await asyncio.sleep(0.5)
        
        # Click "Repost" in menu
        repost = await self.router.execute(
            'click_by_description',
            {'description': 'Repost option in the retweet menu'},
            driver=DriverType.VISION,
        )
        
        if repost.success:
            self._session_stats['retweets_made'] += 1
        
        return XActionResult(
            success=repost.success,
            action="retweet",
            tweet_id=tweet_id,
            error=repost.error,
            duration_ms=retweet_btn.duration_ms + repost.duration_ms,
        )

    async def reply_to_tweet(
        self,
        tweet_id: str,
        reply_text: str,
    ) -> XActionResult:
        """
        Reply to a tweet using UI-TARS Vision.
        
        Workflow:
        1. Find and click reply button
        2. Wait for reply composer to appear
        3. Type reply (character by character)
        4. Submit reply
        
        Args:
            tweet_id: Tweet identifier
            reply_text: Reply text to post
            
        Returns:
            XActionResult
        """
        logger.info(f"[X] Replying to tweet: {reply_text[:50]}...")
        
        # Step 1: Click reply button
        reply_btn = await self.router.execute(
            'click_by_description',
            {'description': 'Reply button (speech bubble icon) on the tweet'},
            driver=DriverType.VISION,
        )
        
        if not reply_btn.success:
            return XActionResult(
                success=False,
                action="reply_to_tweet",
                tweet_id=tweet_id,
                error="Could not find reply button",
            )
        
        await asyncio.sleep(0.5)
        
        # Step 2: Click in reply composer
        input_click = await self.router.execute(
            'click_by_description',
            {'description': 'Reply text input or "Post your reply" placeholder'},
            driver=DriverType.VISION,
        )
        
        if not input_click.success:
            return XActionResult(
                success=False,
                action="reply_to_tweet",
                tweet_id=tweet_id,
                error="Could not find reply input",
            )
        
        await asyncio.sleep(0.3)
        
        # Step 3: Type reply (slowly, human-like)
        type_result = await self.router.execute(
            'click_by_description',
            {
                'description': 'reply text input',
                'text': reply_text,
                'slow_type': True,
            },
            driver=DriverType.VISION,
        )
        
        await asyncio.sleep(0.5)
        
        # Step 4: Submit reply
        submit_result = await self.router.execute(
            'click_by_description',
            {'description': 'Reply button to post the reply'},
            driver=DriverType.VISION,
        )
        
        success = submit_result.success
        if success:
            self._session_stats['replies_made'] += 1
            self._session_stats['tweets_engaged'] += 1
        
        return XActionResult(
            success=success,
            action="reply_to_tweet",
            tweet_id=tweet_id,
            engagements=1 if success else 0,
            error=submit_result.error,
            duration_ms=reply_btn.duration_ms + type_result.duration_ms + submit_result.duration_ms,
        )

    async def post_tweet(
        self,
        content: str,
        image_path: Optional[str] = None,
    ) -> XActionResult:
        """
        Post a new tweet using UI-TARS Vision.
        
        Args:
            content: Tweet content (max 280 chars)
            image_path: Optional image to attach
            
        Returns:
            XActionResult
        """
        logger.info(f"[X] Posting tweet: {content[:50]}...")
        
        # Navigate to home first
        await self.navigate_to_home()
        await asyncio.sleep(1)
        
        # Click compose button
        compose = await self.router.execute(
            'click_by_description',
            {'description': 'Compose new tweet button or "What is happening" input'},
            driver=DriverType.VISION,
        )
        
        if not compose.success:
            return XActionResult(
                success=False,
                action="post_tweet",
                error="Could not find compose button",
            )
        
        await asyncio.sleep(0.5)
        
        # Type content
        type_result = await self.router.execute(
            'click_by_description',
            {
                'description': 'tweet composer text input',
                'text': content,
                'slow_type': True,
            },
            driver=DriverType.VISION,
        )
        
        await asyncio.sleep(0.5)
        
        # Optionally attach image
        if image_path:
            # TODO: Implement image upload via vision
            pass
        
        # Submit tweet
        submit = await self.router.execute(
            'click_by_description',
            {'description': 'Post button to publish the tweet'},
            driver=DriverType.VISION,
        )
        
        return XActionResult(
            success=submit.success,
            action="post_tweet",
            engagements=1 if submit.success else 0,
            error=submit.error,
            duration_ms=compose.duration_ms + type_result.duration_ms + submit.duration_ms,
        )

    async def like_and_reply(
        self,
        tweet_id: str,
        reply_text: str,
    ) -> XActionResult:
        """
        Like and reply to a tweet in one session.
        """
        logger.info(f"[X] Like and reply to {tweet_id[:20]}")
        
        # Like first
        like_result = await self.like_tweet(tweet_id)
        
        # Then reply
        reply_result = await self.reply_to_tweet(tweet_id, reply_text)
        
        return XActionResult(
            success=like_result.success or reply_result.success,
            action="like_and_reply",
            tweet_id=tweet_id,
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
    ) -> XActionResult:
        """
        Run an autonomous engagement session.
        
        0102 reads timeline, identifies relevant tweets, and engages intelligently.
        """
        logger.info(f"[X] Starting {duration_minutes}min engagement session")
        start_time = datetime.now()
        engagements = 0
        
        # Read timeline
        tweets = await self.read_timeline(max_tweets=max_engagements * 2)
        relevant_tweets = [t for t in tweets if t.is_relevant]
        
        logger.info(f"[X] Found {len(relevant_tweets)} relevant tweets")
        
        for tweet in relevant_tweets[:max_engagements]:
            # Check time limit
            elapsed = (datetime.now() - start_time).seconds / 60
            if elapsed >= duration_minutes:
                logger.info("[X] Time limit reached")
                break
            
            # Engage with tweet
            if tweet.suggested_reply:
                result = await self.like_and_reply(tweet.tweet_id, tweet.suggested_reply)
            else:
                result = await self.like_tweet(tweet.tweet_id)
            
            if result.success:
                engagements += 1
            
            # Human-like delay between engagements
            await asyncio.sleep(3 + (engagements % 5) * 2)
        
        elapsed_ms = int((datetime.now() - start_time).total_seconds() * 1000)
        
        return XActionResult(
            success=engagements > 0,
            action="engagement_session",
            tweets_read=len(tweets),
            engagements=engagements,
            duration_ms=elapsed_ms,
            details={
                "relevant_tweets": len(relevant_tweets),
                "session_stats": self._session_stats.copy(),
            },
        )

    def get_session_stats(self) -> Dict[str, int]:
        """Get session statistics."""
        return self._session_stats.copy()

    def close(self) -> None:
        """Close router and release resources."""
        self.router.close()
        logger.info(f"[X] Closed. Stats: {self._session_stats}")


# Factory function
def create_x_actions(profile: str = 'x_foundups') -> XActions:
    """Create XActions instance."""
    return XActions(profile=profile)


# Test function
async def _test_x():
    """Test X actions."""
    x = XActions(profile='x_foundups')
    
    # Test engagement session
    result = await x.run_engagement_session(
        duration_minutes=5,
        max_engagements=3,
    )
    
    print(f"Result: {result.to_dict()}")
    
    x.close()


if __name__ == "__main__":
    asyncio.run(_test_x())


