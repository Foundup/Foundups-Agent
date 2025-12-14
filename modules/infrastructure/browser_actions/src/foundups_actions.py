"""
FoundUp Actions - Vision-Based Engagement for FoundUp LiveChats

Enables 0102 to interact with FoundUp platform livestreams:
- Read and understand livechat messages
- Post to livechat with appropriate context
- Engage with community members
- Moderate content when needed

WSP Compliance:
    - WSP 3: Infrastructure domain
    - WSP 77: AI Overseer integration
    - WSP 80: DAE coordination
    - WSP 27: DAE phase alignment
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from .action_router import ActionRouter, DriverType, RoutingResult

logger = logging.getLogger(__name__)


@dataclass
class LiveChatMessage:
    """Represents a livechat message extracted via vision."""
    message_id: str
    author: str
    content: str
    timestamp: str
    is_moderator: bool = False
    is_member: bool = False
    is_question: bool = False
    requires_response: bool = False
    suggested_reply: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "message_id": self.message_id,
            "author": self.author,
            "content": self.content,
            "timestamp": self.timestamp,
            "is_moderator": self.is_moderator,
            "is_member": self.is_member,
            "is_question": self.is_question,
            "requires_response": self.requires_response,
            "suggested_reply": self.suggested_reply,
        }


@dataclass
class FoundUpActionResult:
    """Result of a FoundUp action."""
    success: bool
    action: str
    foundup_id: Optional[str] = None
    messages_read: int = 0
    messages_sent: int = 0
    error: Optional[str] = None
    duration_ms: int = 0
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "action": self.action,
            "foundup_id": self.foundup_id,
            "messages_read": self.messages_read,
            "messages_sent": self.messages_sent,
            "error": self.error,
            "duration_ms": self.duration_ms,
            "details": self.details,
        }


class FoundUpActions:
    """
    FoundUp platform vision-based engagement actions.
    
    Uses UI-TARS Vision for livechat interaction on FoundUp streams.
    Enables 0102 to participate in community discussions.
    
    Usage:
        foundups = FoundUpActions(profile='foundups_main')
        
        # Read livechat
        messages = await foundups.read_livechat(foundup_id='move2japan')
        
        # Post to livechat
        await foundups.post_to_livechat(foundup_id='move2japan', message='Hello!')
        
        # Run engagement session
        result = await foundups.run_livechat_session(foundup_id='move2japan')
    """

    # Keywords that indicate a question needing response
    QUESTION_INDICATORS = [
        '?', 'how', 'what', 'when', 'where', 'why', 'who',
        'can you', 'could you', 'would you', 'help',
    ]

    # Keywords for engagement priority
    PRIORITY_KEYWORDS = [
        '0102', 'bot', 'ai', 'undaodu', 'foundup', 'geozai',
        'move2japan', 'japan', 'stream', 'live',
    ]

    def __init__(
        self,
        profile: str = 'foundups_main',
        router: ActionRouter = None,
        ai_provider: str = 'grok',
    ) -> None:
        """
        Initialize FoundUp actions.
        
        Args:
            profile: Browser profile
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
            logger.info(f"[FOUNDUP] LLM available via {ai_provider}")
        except ImportError:
            self.llm = None
            self._llm_available = False
            logger.warning("[FOUNDUP] LLM not available, will use templates")
        
        # Session stats
        self._session_stats = {
            'messages_read': 0,
            'messages_sent': 0,
            'questions_answered': 0,
            'greetings_sent': 0,
        }
        
        logger.info(f"[FOUNDUP] Actions initialized with profile={profile}")

    async def navigate_to_foundup(self, foundup_id: str) -> RoutingResult:
        """
        Navigate to a FoundUp stream.
        Uses Selenium (fast, known URL pattern).
        """
        # FoundUp URL pattern (adjust based on actual platform)
        url = f"https://foundups.com/live/{foundup_id}"
        
        result = await self.router.execute(
            'navigate',
            {'url': url},
            driver=DriverType.SELENIUM,
        )
        
        if result.success:
            await asyncio.sleep(2)  # Wait for stream to load
            logger.info(f"[FOUNDUP] Navigated to {foundup_id}")
        
        return result

    async def read_livechat(
        self,
        foundup_id: str,
        max_messages: int = 20,
    ) -> List[LiveChatMessage]:
        """
        Read and understand livechat messages.
        Uses UI-TARS Vision to see and extract messages.
        
        Args:
            foundup_id: FoundUp stream identifier
            max_messages: Maximum messages to read
            
        Returns:
            List of LiveChatMessage objects
        """
        logger.info(f"[FOUNDUP] Reading livechat for {foundup_id}")
        
        # Navigate first
        nav_result = await self.navigate_to_foundup(foundup_id)
        if not nav_result.success:
            logger.error(f"[FOUNDUP] Failed to navigate: {nav_result.error}")
            return []
        
        messages = []
        
        # Use vision to read livechat
        read_result = await self.router.execute(
            'find_by_description',
            {
                'description': 'Livechat messages showing author names and message content',
                'extract_text': True,
            },
            driver=DriverType.VISION,
        )
        
        if read_result.success and read_result.result_data.get('extracted_messages'):
            for msg_data in read_result.result_data['extracted_messages'][:max_messages]:
                msg = self._parse_message(msg_data)
                if msg:
                    # Evaluate if needs response
                    msg.is_question = self._is_question(msg.content)
                    msg.requires_response = self._requires_response(msg)
                    if msg.requires_response and self._llm_available:
                        msg.suggested_reply = await self._generate_reply(msg)
                    messages.append(msg)
                    self._session_stats['messages_read'] += 1
        
        logger.info(f"[FOUNDUP] Read {len(messages)} messages")
        return messages

    def _parse_message(self, msg_data: Dict[str, Any]) -> Optional[LiveChatMessage]:
        """Parse vision-extracted message data."""
        try:
            return LiveChatMessage(
                message_id=msg_data.get('id', f"msg_{datetime.now().timestamp()}"),
                author=msg_data.get('author', 'Unknown'),
                content=msg_data.get('content', ''),
                timestamp=msg_data.get('timestamp', 'now'),
                is_moderator=msg_data.get('is_moderator', False),
                is_member=msg_data.get('is_member', False),
            )
        except Exception as e:
            logger.warning(f"[FOUNDUP] Failed to parse message: {e}")
            return None

    def _is_question(self, content: str) -> bool:
        """Check if message is a question."""
        content_lower = content.lower()
        return any(ind in content_lower for ind in self.QUESTION_INDICATORS)

    def _requires_response(self, msg: LiveChatMessage) -> bool:
        """Determine if message requires a response from 0102."""
        content_lower = msg.content.lower()
        
        # Direct mentions
        if any(kw in content_lower for kw in ['0102', 'bot', '@undaodu']):
            return True
        
        # Questions from members get priority
        if msg.is_question and msg.is_member:
            return True
        
        # General questions about the stream
        if msg.is_question and any(kw in content_lower for kw in self.PRIORITY_KEYWORDS):
            return True
        
        return False

    async def _generate_reply(self, msg: LiveChatMessage) -> str:
        """Generate intelligent reply using LLM."""
        if not self._llm_available:
            return self._template_reply(msg)
        
        try:
            prompt = f"""Generate a friendly livechat response.

Author: {msg.author}
Message: {msg.content}
Is Member: {msg.is_member}

Guidelines:
- Be friendly and welcoming
- Keep under 150 characters (livechat style)
- Address the author by name
- If it's a question, provide helpful answer
- Represent FoundUps brand positively
- Use 1 emoji max
"""
            response = self.llm.generate(prompt)
            return response[:150] if response else self._template_reply(msg)
        except Exception as e:
            logger.warning(f"[FOUNDUP] LLM failed: {e}")
            return self._template_reply(msg)

    def _template_reply(self, msg: LiveChatMessage) -> str:
        """Generate template reply when LLM unavailable."""
        if msg.is_question:
            return f"@{msg.author} Great question! Let me help with that 🎯"
        else:
            templates = [
                f"@{msg.author} Welcome to the stream! 👋",
                f"@{msg.author} Thanks for being here!",
                f"@{msg.author} Glad to have you! 🚀",
            ]
            import random
            return random.choice(templates)

    async def post_to_livechat(
        self,
        foundup_id: str,
        message: str,
    ) -> FoundUpActionResult:
        """
        Post a message to livechat using UI-TARS Vision.
        
        Args:
            foundup_id: FoundUp stream identifier
            message: Message to post
            
        Returns:
            FoundUpActionResult
        """
        logger.info(f"[FOUNDUP] Posting to {foundup_id}: {message[:50]}...")
        
        # Click chat input
        input_click = await self.router.execute(
            'click_by_description',
            {'description': 'Livechat message input field or "Say something" placeholder'},
            driver=DriverType.VISION,
        )
        
        if not input_click.success:
            return FoundUpActionResult(
                success=False,
                action="post_to_livechat",
                foundup_id=foundup_id,
                error="Could not find chat input",
            )
        
        await asyncio.sleep(0.3)
        
        # Type message (slowly, human-like per WSP)
        type_result = await self.router.execute(
            'click_by_description',
            {
                'description': 'chat input field',
                'text': message,
                'slow_type': True,  # 012 speed: character by character
            },
            driver=DriverType.VISION,
        )
        
        await asyncio.sleep(0.3)
        
        # Send message
        send_result = await self.router.execute(
            'click_by_description',
            {'description': 'Send message button or press Enter'},
            driver=DriverType.VISION,
        )
        
        success = send_result.success
        if success:
            self._session_stats['messages_sent'] += 1
        
        return FoundUpActionResult(
            success=success,
            action="post_to_livechat",
            foundup_id=foundup_id,
            messages_sent=1 if success else 0,
            error=send_result.error,
            duration_ms=input_click.duration_ms + type_result.duration_ms + send_result.duration_ms,
        )

    async def respond_to_message(
        self,
        foundup_id: str,
        message: LiveChatMessage,
    ) -> FoundUpActionResult:
        """
        Respond to a specific livechat message.
        
        Args:
            foundup_id: FoundUp stream identifier
            message: Message to respond to
            
        Returns:
            FoundUpActionResult
        """
        reply_text = message.suggested_reply or self._template_reply(message)
        result = await self.post_to_livechat(foundup_id, reply_text)
        
        if result.success and message.is_question:
            self._session_stats['questions_answered'] += 1
        
        return result

    async def send_greeting(self, foundup_id: str) -> FoundUpActionResult:
        """
        Send a greeting message to the livechat.
        
        Args:
            foundup_id: FoundUp stream identifier
            
        Returns:
            FoundUpActionResult
        """
        greetings = [
            "Hey everyone! 0102 here, ready to chat! 👋",
            "What's up chat! Great to be here 🚀",
            "Hello beautiful people! Let's have fun! 🎉",
        ]
        import random
        greeting = random.choice(greetings)
        
        result = await self.post_to_livechat(foundup_id, greeting)
        if result.success:
            self._session_stats['greetings_sent'] += 1
        
        return result

    async def run_livechat_session(
        self,
        foundup_id: str,
        duration_minutes: int = 30,
        check_interval: int = 10,
    ) -> FoundUpActionResult:
        """
        Run an autonomous livechat engagement session.
        
        0102 monitors chat, responds to questions, engages with community.
        
        Args:
            foundup_id: FoundUp stream identifier
            duration_minutes: Session duration
            check_interval: Seconds between chat checks
            
        Returns:
            FoundUpActionResult with session summary
        """
        logger.info(f"[FOUNDUP] Starting {duration_minutes}min livechat session for {foundup_id}")
        start_time = datetime.now()
        
        # Navigate first
        nav_result = await self.navigate_to_foundup(foundup_id)
        if not nav_result.success:
            return FoundUpActionResult(
                success=False,
                action="livechat_session",
                foundup_id=foundup_id,
                error=nav_result.error,
            )
        
        # Send initial greeting
        await self.send_greeting(foundup_id)
        
        processed_ids = set()
        messages_sent = 0
        
        while True:
            # Check time limit
            elapsed = (datetime.now() - start_time).seconds / 60
            if elapsed >= duration_minutes:
                logger.info("[FOUNDUP] Session time limit reached")
                break
            
            # Read new messages
            messages = await self.read_livechat(foundup_id, max_messages=10)
            
            # Respond to messages needing attention
            for msg in messages:
                if msg.message_id in processed_ids:
                    continue
                
                processed_ids.add(msg.message_id)
                
                if msg.requires_response:
                    result = await self.respond_to_message(foundup_id, msg)
                    if result.success:
                        messages_sent += 1
                    
                    # Don't flood chat
                    await asyncio.sleep(3)
            
            # Wait before next check
            await asyncio.sleep(check_interval)
        
        elapsed_ms = int((datetime.now() - start_time).total_seconds() * 1000)
        
        return FoundUpActionResult(
            success=True,
            action="livechat_session",
            foundup_id=foundup_id,
            messages_read=self._session_stats['messages_read'],
            messages_sent=messages_sent,
            duration_ms=elapsed_ms,
            details={
                "session_stats": self._session_stats.copy(),
            },
        )

    def get_session_stats(self) -> Dict[str, int]:
        """Get session statistics."""
        return self._session_stats.copy()

    def close(self) -> None:
        """Close router and release resources."""
        self.router.close()
        logger.info(f"[FOUNDUP] Closed. Stats: {self._session_stats}")


# Factory function
def create_foundups_actions(profile: str = 'foundups_main') -> FoundUpActions:
    """Create FoundUpActions instance."""
    return FoundUpActions(profile=profile)


# Test function
async def _test_foundups():
    """Test FoundUp actions."""
    foundups = FoundUpActions(profile='foundups_main')
    
    # Test livechat session
    result = await foundups.run_livechat_session(
        foundup_id='move2japan',
        duration_minutes=2,
    )
    
    print(f"Result: {result.to_dict()}")
    
    foundups.close()


if __name__ == "__main__":
    asyncio.run(_test_foundups())


