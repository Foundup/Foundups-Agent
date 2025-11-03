"""
X Twitter DAE Adapter

Integrates x_twitter_dae.py as a child DAE within social_media_orchestrator.
Provides adapter pattern to coordinate full WSP 26-29 DAE capabilities.

WSP Compliance:
- WSP 77: Agent Coordination Protocol (child DAE within orchestrator)
- WSP 80: Cube-Level DAE Orchestration (parent-child DAE relationship)
- WSP 26-29: Full DAE compliance via x_twitter_dae.py integration

Architecture:
- Parent: SocialMediaOrchestratorDAE
- Child: XTwitterDAEAdapter (this module)
- Core: x_twitter_dae.py (XTwitterDAENode)
"""

import logging
import asyncio
from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

# WSP 77: Agent Coordination - Import child DAE
try:
    from modules.platform_integration.x_twitter.src.x_twitter_dae import XTwitterDAENode
    X_DAE_AVAILABLE = True
except ImportError as e:
    logging.warning(f"X Twitter DAE not available: {e}")
    X_DAE_AVAILABLE = False


@dataclass
class PostingResult:
    """Result of child DAE posting operation"""
    success: bool
    post_id: Optional[str] = None
    message: str = ""
    timestamp: datetime = None
    cabr_score: float = 0.0
    dae_signature: Optional[str] = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class XTwitterDAEAdapter:
    """
    Adapter to integrate x_twitter_dae.py as child DAE within orchestrator.

    WSP 77: Agent Coordination Protocol
    - Acts as child DAE within social_media_orchestrator parent
    - Delegates to full WSP 26-29 compliant XTwitterDAENode
    - Provides clean interface for parent orchestrator

    Architecture Flow:
    Parent Orchestrator -> XTwitterDAEAdapter -> XTwitterDAENode -> Twitter API
    """

    def __init__(self, parent_orchestrator=None, config: Optional[Dict[str, Any]] = None):
        """
        Initialize X Twitter DAE Adapter as child DAE.

        Args:
            parent_orchestrator: Reference to parent orchestrator DAE
            config: Configuration for X/Twitter operations
        """
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.parent_orchestrator = parent_orchestrator
        self.config = config or {}

        # Child DAE state
        self.dae_node: Optional[XTwitterDAENode] = None
        self.enabled = X_DAE_AVAILABLE
        self.authenticated = False

        # Operational metrics (WSP 29 CABR tracking)
        self.posting_history: list[PostingResult] = []
        self.last_post_time = None

        # Initialize child DAE if available
        if self.enabled:
            self._initialize_child_dae()
        else:
            self.logger.warning("X Twitter DAE child not available - adapter operating in simulation mode")

    def _initialize_child_dae(self):
        """Initialize the child X Twitter DAE node"""
        try:
            self.dae_node = XTwitterDAENode(config=self.config)
            self.logger.info("X Twitter child DAE initialized successfully")
            self.logger.info(f"DAE Identity: {self.dae_node.dae_identity.identity_hash[:16]}...")
        except Exception as e:
            self.logger.error(f"Failed to initialize X Twitter child DAE: {e}")
            self.enabled = False

    async def authenticate(self, credentials: Dict[str, Any]) -> bool:
        """
        Authenticate the child DAE with Twitter API.

        Args:
            credentials: Twitter API credentials

        Returns:
            bool: Authentication success
        """
        if not self.enabled or not self.dae_node:
            self.logger.warning("X Twitter child DAE not available - authentication skipped")
            return False

        try:
            # Extract credentials for DAE authentication
            bearer_token = credentials.get('bearer_token')
            api_key = credentials.get('api_key')
            api_secret = credentials.get('api_secret')
            access_token = credentials.get('access_token')
            access_token_secret = credentials.get('access_token_secret')

            # Authenticate child DAE
            success = await self.dae_node.authenticate_twitter(
                bearer_token=bearer_token,
                api_key=api_key,
                api_secret=api_secret,
                access_token=access_token,
                access_token_secret=access_token_secret
            )

            self.authenticated = success

            if success:
                self.logger.info("X Twitter child DAE authenticated successfully")
                # Log authentication state change (WSP 27)
                self.dae_node.authenticator.log_authentication_event("adapter_coordinated_auth")
            else:
                self.logger.error("X Twitter child DAE authentication failed")

            return success

        except Exception as e:
            self.logger.error(f"X Twitter child DAE authentication error: {e}")
            return False

    async def receive_base_content(self, base_content: Dict[str, Any]) -> PostingResult:
        """
        Receive base content from parent orchestrator and post via child DAE.

        This is the primary integration point for WSP 77 agent coordination.

        Args:
            base_content: Base content from parent orchestrator
                {
                    'mention': '@UnDaoDu',
                    'action': 'going live!',
                    'title': stream_title,
                    'url': stream_url,
                    'tags': []
                }

        Returns:
            PostingResult: Result of child DAE posting operation
        """
        if not self.enabled or not self.dae_node:
            return PostingResult(
                success=False,
                message="X Twitter child DAE not available"
            )

        if not self.authenticated:
            return PostingResult(
                success=False,
                message="X Twitter child DAE not authenticated"
            )

        try:
            # Adapt base content for X/Twitter platform (WSP 77 content adaptation)
            adapted_content = self._adapt_content_for_twitter(base_content)

            # Prepare engagement context for child DAE (WSP 29 CABR)
            engagement_context = {
                'parent_orchestrator': True,
                'stream_event': True,
                'content_adaptation': 'twitter_specific',
                'base_content_hash': hash(str(base_content)),
                'timestamp': datetime.now().isoformat()
            }

            # Post via child DAE with full WSP 26-29 protocols
            self.logger.info(f"Child DAE posting adapted content: {adapted_content[:50]}...")
            post_id = await self.dae_node.post_autonomous_content(
                content=adapted_content,
                engagement_context=engagement_context
            )

            # Record successful posting for CABR learning
            result = PostingResult(
                success=True,
                post_id=post_id,
                message="Posted via child DAE",
                cabr_score=self.dae_node.cabr_engine.score_social_interaction(engagement_context),
                dae_signature=self.dae_node.authenticator.generate_outbound_signature(adapted_content)
            )

            self.posting_history.append(result)
            self.last_post_time = result.timestamp

            # Log successful parent-child coordination (WSP 77)
            self.logger.info(f"Child DAE posting successful: {post_id}")
            self.logger.info(f"CABR Score: {result.cabr_score:.3f}")

            return result

        except Exception as e:
            error_msg = f"Child DAE posting failed: {e}"
            self.logger.error(error_msg)

            # Record failed posting for CABR learning
            result = PostingResult(
                success=False,
                message=error_msg
            )
            self.posting_history.append(result)

            return result

    def _adapt_content_for_twitter(self, base_content: Dict[str, Any]) -> str:
        """
        Adapt base content for X/Twitter platform characteristics.

        WSP 77: Agent specialization - Twitter-specific content adaptation
        - 280 character limit
        - Concise, punchy style
        - Emoji and hashtag optimization
        - Thread preparation if needed

        Args:
            base_content: Base content from parent orchestrator

        Returns:
            str: Twitter-adapted content
        """
        mention = base_content.get('mention', '')
        action = base_content.get('action', '')
        title = base_content.get('title', '')
        url = base_content.get('url', '')
        tags = base_content.get('tags', [])

        # Build Twitter-optimized content
        content_parts = []

        # Start with mention and action
        if mention and action:
            content_parts.append(f"{mention} {action}")

        # Add emoji for engagement
        content_parts.append("[U+1F525]")

        # Add shortened title (Twitter's character limit)
        if title:
            # Truncate title to fit within limits
            max_title_len = 100  # Leave room for URL and other elements
            if len(title) > max_title_len:
                title = title[:max_title_len-3] + "..."
            content_parts.append(title)

        # Add URL
        if url:
            content_parts.append(url)

        # Join content
        adapted_content = " ".join(content_parts)

        # Add hashtags if they fit
        hashtags = ["#FoundUps", "#LiveStream"]
        if tags:
            hashtags.extend([f"#{tag.replace(' ', '')}" for tag in tags[:2]])  # Limit to 2 extra

        # Check if hashtags fit within 280 characters
        content_with_hashtags = f"{adapted_content} {' '.join(hashtags)}"
        if len(content_with_hashtags) <= 280:
            adapted_content = content_with_hashtags

        # Final length check
        if len(adapted_content) > 280:
            # Truncate if still too long
            adapted_content = adapted_content[:277] + "..."

        self.logger.debug(f"Content adapted for Twitter: {len(adapted_content)} chars")
        return adapted_content

    def is_enabled(self) -> bool:
        """
        Check if this child DAE is enabled and operational.

        Returns:
            bool: Whether child DAE can accept posting requests
        """
        return self.enabled and self.dae_node is not None and self.authenticated

    def get_status(self) -> Dict[str, Any]:
        """
        Get comprehensive status of child DAE for parent orchestrator.

        Returns:
            dict: Status information including WSP compliance metrics
        """
        if not self.enabled or not self.dae_node:
            return {
                'enabled': False,
                'authenticated': False,
                'wsp_compliance': 'N/A',
                'cabr_score': 0.0,
                'message': 'X Twitter child DAE not available'
            }

        # Get DAE status from child node
        dae_status = self.dae_node.get_dae_status()

        return {
            'enabled': self.enabled,
            'authenticated': self.authenticated,
            'wsp_compliance': dae_status.get('wsp_compliance', {}),
            'cabr_score': dae_status.get('operational_metrics', {}).get('cabr_efficiency', 0.0),
            'posting_history_count': len(self.posting_history),
            'last_post_time': self.last_post_time.isoformat() if self.last_post_time else None,
            'message': 'X Twitter child DAE operational'
        }

    def get_cabr_metrics(self) -> Dict[str, Any]:
        """
        Get CABR metrics for parent orchestrator learning.

        Returns:
            dict: CABR performance metrics from child DAE
        """
        if not self.enabled or not self.dae_node:
            return {'available': False}

        # Get CABR metrics from child DAE
        cabr_metrics = self.dae_node.cabr_engine.get_cabr_metrics()

        # Add adapter-specific metrics
        cabr_metrics.update({
            'adapter_posting_success_rate': self._calculate_success_rate(),
            'adapter_content_adaptation_count': len(self.posting_history),
            'parent_child_coordination_active': True
        })

        return cabr_metrics

    def _calculate_success_rate(self) -> float:
        """Calculate posting success rate for CABR learning"""
        if not self.posting_history:
            return 0.0

        successful_posts = sum(1 for result in self.posting_history if result.success)
        return successful_posts / len(self.posting_history)

    async def cleanup(self):
        """Cleanup child DAE resources"""
        if self.dae_node:
            try:
                # Call cleanup on child DAE if available
                if hasattr(self.dae_node, '_cleanup'):
                    await self.dae_node._cleanup()
            except Exception as e:
                self.logger.error(f"Child DAE cleanup error: {e}")
