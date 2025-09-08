"""
LiveChat Core - WSP Compliant Module (<500 lines)
Core YouTube Live Chat listener using modular components
"""

import logging
import os
import time
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional, List
import googleapiclient.errors

# Import WSP-compliant modules
from modules.communication.livechat.src.moderation_stats import ModerationStats
from modules.communication.livechat.src.session_manager import SessionManager
from modules.communication.livechat.src.message_processor import MessageProcessor
from modules.communication.livechat.src.chat_sender import ChatSender
from modules.communication.livechat.src.chat_poller import ChatPoller
from modules.infrastructure.system_health_monitor.src.system_health_analyzer import SystemHealthAnalyzer
from modules.communication.livechat.src.chat_memory_manager import ChatMemoryManager
try:
    from modules.communication.livechat.src.quota_aware_poller import QuotaAwarePoller
except ImportError:
    QuotaAwarePoller = None
try:
    from modules.communication.livechat.src.intelligent_throttle_manager import IntelligentThrottleManager
except ImportError:
    IntelligentThrottleManager = None

logger = logging.getLogger(__name__)

MAX_RETRIES = 3
MAX_MESSAGES_PER_CALL = 200

class LiveChatCore:
    """
    Core YouTube Live Chat listener - WSP compliant version.
    Uses modular components for functionality.
    """
    
    def __init__(self, youtube_service, video_id: str, live_chat_id: Optional[str] = None, 
                 channel_name: str = None, channel_id: str = None):
        """
        Initialize LiveChatCore with modular components.
        
        Args:
            youtube_service: Authenticated YouTube service
            video_id: YouTube video/stream ID
            live_chat_id: Optional pre-fetched chat ID
            channel_name: Name of the channel owner
            channel_id: Channel ID of the owner
        """
        self.youtube = youtube_service
        self.video_id = video_id
        self.live_chat_id = live_chat_id
        self.channel_name = channel_name or "StreamOwner"
        self.channel_id = channel_id or "owner"
        self.next_page_token = None
        self.is_running = False
        self.memory_dir = "memory"
        self.processed_message_ids = set()
        self.recent_command_cache = {}  # Cache to prevent duplicate command responses
        self.message_timestamps = []  # Track message times for activity monitoring
        
        # WSP-compliant hybrid memory manager (initialize first)
        self.memory_manager = ChatMemoryManager(self.memory_dir)
        
        # Initialize modular components
        self.session_manager = SessionManager(youtube_service, video_id)
        self.mod_stats = ModerationStats(self.memory_dir)
        self.message_processor = MessageProcessor(youtube_service, self.memory_manager)  # Pass memory manager
        self.chat_sender = ChatSender(youtube_service, live_chat_id)
        self.chat_poller = ChatPoller(youtube_service, live_chat_id, self.channel_name, self.channel_id)
        
        # Health monitoring for duplicate detection and error tracking
        self.health_analyzer = SystemHealthAnalyzer()
        self.recent_messages_sent = []  # Track sent messages
        
        # NEW: Quota-aware polling
        try:
            # Get credential set number from service
            cred_set = getattr(youtube_service, 'credential_set', 1)
            self.quota_poller = QuotaAwarePoller(cred_set) if QuotaAwarePoller else None
        except:
            self.quota_poller = None
        
        # AUTOMATIC: Intelligent throttle manager for API quota
        self.intelligent_throttle = None
        if IntelligentThrottleManager:
            try:
                from pathlib import Path
                memory_path = Path(self.memory_dir)
                self.intelligent_throttle = IntelligentThrottleManager(
                    min_delay=1.0,
                    max_delay=60.0,
                    throttle_window=60,
                    memory_path=memory_path
                )
                # Enable all intelligent features by default
                self.intelligent_throttle.enable_learning(True)
                self.intelligent_throttle.set_agentic_mode(True)
                logger.info("[AUTO] Intelligent throttle manager initialized - automatic API management enabled")
            except Exception as e:
                logger.warning(f"[AUTO] Could not initialize intelligent throttle: {e}")
                self.intelligent_throttle = None
        
        # Ensure memory directory exists
        os.makedirs(self.memory_dir, exist_ok=True)
        
        # AUTOMATIC: Initialize WRE monitor for continuous improvement
        try:
            from modules.infrastructure.wre_core.wre_monitor import get_monitor
            self.wre_monitor = get_monitor()
            logger.info("[0102] WRE Monitor attached - Continuous improvement active")
        except Exception as e:
            logger.debug(f"WRE Monitor not available: {e}")
            self.wre_monitor = None
        
        logger.info(f"LiveChatCore initialized for video: {video_id}")
    
    async def initialize(self) -> bool:
        """
        Initialize the chat session.
        
        Returns:
            True if initialization successful
        """
        # Initialize session
        if not await self.session_manager.initialize_session():
            logger.error("Failed to initialize session")
            return False
        
        # Get chat ID and channel info from session manager
        self.live_chat_id = self.session_manager.live_chat_id
        self.channel_name = getattr(self.session_manager, 'channel_title', self.channel_name)
        self.channel_id = getattr(self.session_manager, 'channel_id', self.channel_id)
        
        # Update components with new info
        self.chat_sender.live_chat_id = self.live_chat_id
        self.chat_poller.live_chat_id = self.live_chat_id
        self.chat_poller.channel_name = self.channel_name
        self.chat_poller.channel_id = self.channel_id
        
        # Send greeting
        await self.session_manager.send_greeting(self.send_chat_message)
        
        # Post to LinkedIn when stream goes live
        await self._post_stream_to_linkedin()
        
        logger.info("LiveChatCore initialized successfully")
        return True
    
    async def send_chat_message(self, message_text: str, skip_delay: bool = False, response_type: str = 'general') -> bool:
        """
        Send a message to the live chat with duplicate detection and intelligent throttling.
        
        Args:
            message_text: Message to send
            skip_delay: Whether to skip delay (overridden by intelligent throttle)
            response_type: Type of response for priority handling
            
        Returns:
            True if message sent successfully
        """
        if not self.live_chat_id:
            logger.error("Cannot send message - no live chat ID")
            self.health_analyzer.analyze_message("ERROR: Cannot send message - no live chat ID")
            return False
        
        # AUTOMATIC: Intelligent throttling before sending
        if self.intelligent_throttle and not skip_delay:
            # Track API call
            self.intelligent_throttle.track_api_call(quota_cost=5)  # Chat messages cost more quota
            
            # WRE Monitor: Track API call
            if self.wre_monitor:
                self.wre_monitor.track_api_call('liveChatMessages.insert', 5, True)
            
            # Check if we should send based on intelligent throttling
            if not self.intelligent_throttle.should_respond(response_type):
                delay = self.intelligent_throttle.calculate_adaptive_delay(response_type)
                logger.info(f"[AUTO-THROTTLE] Delaying {response_type} by {delay:.1f}s to conserve quota")
                # Don't send if throttled
                return False
        
        # Check for duplicate messages
        issues = self.health_analyzer.analyze_message(f"SENDING: {message_text}")
        if issues:
            for issue in issues:
                if issue.issue_type == 'duplicate' and issue.severity in ['high', 'critical']:
                    logger.warning(f"⚠️ Duplicate message detected, skipping: {message_text[:50]}...")
                    # Integrate with self-improvement
                    if hasattr(self.message_processor, 'self_improvement'):
                        self.message_processor.self_improvement.observe_system_issue(
                            issue.issue_type, issue.severity, issue.context
                        )
                    return False
        
        # Track message for duplicate detection
        self.recent_messages_sent.append({
            'message': message_text,
            'timestamp': time.time()
        })
        
        # AUTOMATIC: Record response for intelligent learning
        if self.intelligent_throttle:
            self.intelligent_throttle.record_response(response_type, success=True)
            
            # WRE Monitor: Track successful response
            if self.wre_monitor and success:
                self.wre_monitor.messages_processed += 1
        
        # Limit recent messages cache
        if len(self.recent_messages_sent) > 100:
            self.recent_messages_sent = self.recent_messages_sent[-100:]
        
        # Send message
        start_time = time.time()
        success = await self.chat_sender.send_message(message_text, skip_delay=skip_delay, response_type=response_type)
        duration_ms = (time.time() - start_time) * 1000
        
        # Track operation performance
        self.health_analyzer.track_operation('send_message', duration_ms)
        
        return success
    
    async def poll_messages(self) -> tuple:
        """
        Poll for new chat messages.
        
        Returns:
            Tuple of (messages list, poll interval in ms)
        """
        try:
            messages = await self.chat_poller.poll_messages(
                viewer_count=self.session_manager.viewer_count
            )
            
            # ChatPoller returns messages directly
            if messages:
                poll_interval = self.chat_poller.poll_interval_ms
                return messages, poll_interval
            
            return [], 5000
            
        except Exception as e:
            logger.error(f"Error polling messages: {e}")
            return [], 5000
    
    async def process_message(self, message: Dict[str, Any]) -> None:
        """
        Process a single chat message.
        
        Args:
            message: Message data from YouTube API or ban_event
        """
        try:
            # Check if this is a ban/timeout event from chat_poller
            if message.get("type") == "ban_event":
                await self.process_ban_event(message)
                return
            elif message.get("type") == "timeout_event":
                # Timeout events are also ban events for processing
                await self.process_ban_event(message)
                return
                
            # Extract message details for regular messages
            message_id = message.get("id", "")
            
            # Skip if already processed
            if message_id in self.processed_message_ids:
                return
            
            self.processed_message_ids.add(message_id)
            
            # Get message content
            snippet = message.get("snippet", {})
            author_details = message.get("authorDetails", {})
            
            display_message = snippet.get("displayMessage", "")
            author_name = author_details.get("displayName", "Unknown")
            author_id = author_details.get("channelId", "")
            is_moderator = author_details.get("isChatModerator", False)
            is_owner = author_details.get("isChatOwner", False)
            
            # Log the message
            logger.debug(f"[{author_name}]: {display_message}")
            
            # Track message timestamp for activity monitoring
            self.message_timestamps.append(time.time())
            # Clean old timestamps (keep last hour)
            cutoff = time.time() - 3600
            self.message_timestamps = [ts for ts in self.message_timestamps if ts > cutoff]
            
            # Update stats
            self.mod_stats.record_message()
            
            # WRE Monitor: Track message processing
            if self.wre_monitor:
                self.wre_monitor.messages_processed += 1
            
            # Process message through enhanced processor
            processed = self.message_processor.process_message(message)
            
            # Log ALL messages and their processing result
            logger.info(f"📨 [{author_name}] ({author_id}): {display_message[:100]}")
            if processed.get("has_consciousness"):
                logger.info(f"✨ CONSCIOUSNESS DETECTED from {author_name}!")
            if processed.get("has_whack_command"):
                logger.info(f"🎮 WHACK COMMAND DETECTED from {author_name}!")
                logger.info(f"🔍 DEBUG: Whack command message text: '{display_message}'")
            
            # Debug log for slash commands
            if display_message and display_message.startswith('/'):
                logger.info(f"🔍 SLASH COMMAND DETECTED: '{display_message}' from {author_name}")
                
                # Check for duplicate command within 5 seconds
                cache_key = f"{author_id}:{display_message}"
                current_time = time.time()
                
                if cache_key in self.recent_command_cache:
                    last_time = self.recent_command_cache[cache_key]
                    if current_time - last_time < 5:  # 5 second window
                        logger.info(f"⏭️ Skipping duplicate command from {author_name}")
                        return
                
                self.recent_command_cache[cache_key] = current_time
                
                # Clean old cache entries
                self.recent_command_cache = {
                    k: v for k, v in self.recent_command_cache.items() 
                    if current_time - v < 10
                }
            
            # Check if it's a timeout/ban announcement - HIGH PRIORITY, NO DELAYS
            if processed.get("type") in ["timeout_announcement", "ban_announcement"]:
                # Send announcements immediately with skip_delay=True
                if processed.get("announcement"):
                    # Priority message - skip all delays
                    success = await self.chat_sender.send_message(
                        processed["announcement"], 
                        response_type="timeout_announcement"  # Mark as priority
                    )
                    logger.info(f"⚡🎮 Sent timeout announcement IMMEDIATELY: {processed['announcement'][:50]}...")
                if processed.get("level_up"):
                    await asyncio.sleep(0.5)  # Minimal delay between messages
                    success = await self.chat_sender.send_message(
                        processed["level_up"], 
                        response_type="timeout_announcement"  # Mark as priority
                    )
                    logger.info(f"⚡🏆 Sent level up IMMEDIATELY: {processed['level_up']}")
                return  # Skip normal processing for events
            
            # Skip if marked to skip
            if processed.get("skip"):
                return
            
            # Generate response if needed
            response = await self.message_processor.generate_response(processed)
            
            if response:
                logger.info(f"📤 Generated response for {author_name}: {response[:100]}")
                # Check if this is a consciousness response or slash command
                response_type = processed.get("response_type", "general")
                
                # SLASH COMMANDS should respond immediately - no delays!
                if processed.get("has_whack_command") or display_message.startswith('/'):
                    logger.info(f"⚡ Sending slash command response immediately")
                    # Bypass delays for commands
                    success = await self.chat_sender.send_message(response, response_type="command", skip_delay=True)
                elif response_type == "consciousness":
                    logger.info(f"⚡ Sending consciousness response immediately")
                    # Pass response_type to chat_sender for proper handling
                    success = await self.chat_sender.send_message(response, response_type="consciousness")
                else:
                    success = await self.send_chat_message(response)
                if success:
                    logger.info(f"💬 Sent response to {author_name}")
            else:
                # Debug: log why no response
                if display_message.startswith('/'):
                    logger.warning(f"⚠️ NO RESPONSE for command: '{display_message}' from {author_name}")
                    logger.warning(f"⚠️ Processed flags: has_whack={processed.get('has_whack_command')}, has_trigger={processed.get('has_trigger')}")
            
            # Log to user file
            self._log_to_user_file(message)
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
    
    async def process_ban_event(self, ban_event: Dict[str, Any]) -> None:
        """
        Process a ban/timeout event and send announcement.
        
        Args:
            ban_event: Ban event data from chat_poller
        """
        try:
            logger.info(f"🎯 Processing ban/timeout event: {ban_event.get('type')} - {ban_event.get('target_name')}")
            
            # Process through message processor to get announcement
            processed = self.message_processor.process_message(ban_event)
            
            # Check if this was queued for batching
            if processed.get("queued"):
                logger.info(f"📦 Event queued for batching (pending: {self.message_processor.event_handler.get_pending_count()})")
                return
            
            # Check if we should skip (already part of a batch)
            if processed.get("skip") and not processed.get("announcement"):
                logger.info("⏭️ Skipping - part of batch")
                return
            
            logger.info(f"📝 Processed result: announcement={bool(processed.get('announcement'))}, is_batched={processed.get('is_batched', False)}")
            
            # Send announcements
            if processed.get("announcement"):
                if processed.get("is_batched"):
                    logger.info(f"🎯 Sending BATCHED announcement: {processed['announcement'][:50]}...")
                else:
                    logger.info(f"🎮 Sending timeout announcement: {processed['announcement'][:50]}...")
                await self.send_chat_message(processed["announcement"], response_type="timeout_announcement")
            else:
                logger.warning("⚠️ No announcement generated for timeout event")
            
            if processed.get("level_up"):
                await asyncio.sleep(1)  # Small delay between messages
                logger.info(f"🏆 Sending level up: {processed['level_up']}")
                await self.send_chat_message(processed["level_up"])
                
        except Exception as e:
            logger.error(f"Error processing ban event: {e}")
    
    def _log_to_user_file(self, message: Dict[str, Any]) -> None:
        """
        Log message using hybrid memory manager.
        
        Args:
            message: Message data
        """
        try:
            author_details = message.get("authorDetails", {})
            snippet = message.get("snippet", {})
            
            author_name = author_details.get("displayName", "Unknown")
            display_message = snippet.get("displayMessage", "")
            is_moderator = author_details.get("isChatModerator", False)
            is_owner = author_details.get("isChatOwner", False)
            
            # Determine role
            role = 'OWNER' if is_owner else 'MOD' if is_moderator else 'USER'
            
            # Use hybrid memory manager (smart storage based on importance)
            self.memory_manager.store_message(author_name, display_message, role)
            
        except Exception as e:
            logger.error(f"Error logging message: {e}")
    
    async def process_message_batch(self, messages: List[Dict[str, Any]]) -> None:
        """
        Process a batch of messages.
        
        Args:
            messages: List of messages to process
        """
        for message in messages:
            await self.process_message(message)
    
    async def run_polling_loop(self) -> None:
        """Run the main polling loop with health monitoring and proactive trolling."""
        poll_interval_ms = 5000
        
        # Check quota status at start
        if self.quota_poller:
            status = self.quota_poller.get_quota_status()
            logger.warning(f"📊 QUOTA STATUS: {status['status']} - {status['units_used']}/{10000} units used ({status['percentage_used']:.1%})")
            logger.info(f"💡 Recommendation: {status['recommendation']}")
        last_health_check = time.time()
        last_troll = time.time()
        last_stream_check = time.time()  # Track last stream validation
        last_activity = time.time()  # Track last meaningful chat activity
        health_check_interval = 60  # Check health every minute
        stream_check_interval = 120  # Check if stream is still live every 2 minutes (more responsive)
        inactivity_timeout = 180  # Consider stream inactive after 3 minutes of no messages
        consecutive_poll_errors = 0  # Track consecutive polling errors
        consecutive_empty_polls = 0  # Track polls with no messages
        # Dynamic troll interval based on chat activity
        base_troll_interval = 600  # Base: 10 minutes for quiet chat
        troll_interval = base_troll_interval
        
        while self.is_running:
            try:
                # Periodic health check
                if time.time() - last_health_check > health_check_interval:
                    health_report = self.health_analyzer.get_health_report()
                    if health_report['health_score'] < 80:
                        logger.warning(f"⚠️ System health degraded: {health_report['health_score']:.1f}/100")
                        for recommendation in health_report['recommendations']:
                            logger.info(f"💡 Health recommendation: {recommendation}")
                    last_health_check = time.time()
                
                # Periodic MAGA trolling - ONLY if chat is active
                # Count recent messages to determine chat activity
                recent_msg_count = len([ts for ts in getattr(self, 'message_timestamps', []) 
                                       if time.time() - ts < 300])  # Messages in last 5 min
                
                # Adjust troll interval based on activity
                if recent_msg_count == 0:
                    # Dead chat: no proactive messages
                    troll_interval = float('inf')  # Never troll in dead chat
                elif recent_msg_count < 5:
                    # Very quiet: rare trolling
                    troll_interval = 1200  # 20 minutes
                elif recent_msg_count < 20:
                    # Moderate activity: occasional trolling
                    troll_interval = 600  # 10 minutes
                else:
                    # Active chat: more frequent engagement
                    troll_interval = 300  # 5 minutes
                
                if time.time() - last_troll > troll_interval and troll_interval != float('inf'):
                    if hasattr(self.message_processor, 'agentic_engine'):
                        troll_msg = self.message_processor.agentic_engine.generate_proactive_troll()
                        await self.send_chat_message(troll_msg)
                        logger.info(f"🎯 Sent proactive troll (activity: {recent_msg_count} msgs): {troll_msg[:50]}...")
                    last_troll = time.time()
                
                # Periodic stream health check - detect if stream ended
                if time.time() - last_stream_check > stream_check_interval:
                    logger.info("🔍 Checking if stream is still live...")
                    try:
                        # Try to get stream status
                        response = self.youtube.videos().list(
                            part="liveStreamingDetails,snippet",
                            id=self.video_id
                        ).execute()
                        
                        items = response.get('items', [])
                        if not items:
                            logger.warning("⚠️ Stream not found - may have ended")
                            consecutive_poll_errors = 5  # Trigger exit
                        else:
                            live_details = items[0].get('liveStreamingDetails', {})
                            actual_end_time = live_details.get('actualEndTime')
                            if actual_end_time:
                                logger.warning(f"⚠️ Stream has ended at {actual_end_time}")
                                logger.info("🔚 Exiting polling loop - stream ended")
                                self.is_running = False
                                break
                            else:
                                logger.info("✅ Stream is still live")
                                consecutive_poll_errors = 0  # Reset error counter
                    except Exception as e:
                        logger.warning(f"⚠️ Error checking stream status: {e}")
                    
                    last_stream_check = time.time()
                
                # AUTOMATIC: Check quota before polling
                if self.intelligent_throttle:
                    # Get intelligent delay based on current activity
                    messages_per_minute = len([ts for ts in self.message_timestamps if time.time() - ts < 60])
                    intelligent_delay = self.intelligent_throttle.calculate_adaptive_delay('poll')
                    
                    # Use intelligent delay if it's longer than current interval
                    if intelligent_delay * 1000 > poll_interval_ms:
                        poll_interval_ms = int(intelligent_delay * 1000)
                        logger.info(f"[AUTO-THROTTLE] Adjusted poll interval to {intelligent_delay:.1f}s based on activity")
                    
                    # Check quota state
                    status = self.intelligent_throttle.get_status()
                    for set_id, quota_info in status.get('quota_states', {}).items():
                        if quota_info['percentage'] < 10:
                            logger.warning(f"[AUTO-QUOTA] Low quota on set {set_id}: {quota_info['percentage']:.1f}%")
                
                # Original quota poller as fallback
                elif self.quota_poller:
                    should_poll, wait_time = self.quota_poller.should_poll()
                    if not should_poll:
                        logger.critical("🚨 QUOTA EXHAUSTED - Stopping polling")
                        self.is_running = False
                        break
                    
                    # Override poll interval with quota-aware interval
                    if wait_time:
                        poll_interval_ms = int(wait_time * 1000)
                        logger.info(f"⏱️ Quota-aware interval: {wait_time:.1f}s")
                
                # Poll for messages
                logger.info(f"🔄 Polling for messages...")
                try:
                    messages, original_interval = await self.poll_messages()
                    
                    # Let quota poller know about activity
                    if self.quota_poller:
                        poll_interval_ms = int(self.quota_poller.calculate_optimal_interval(
                            messages_received=len(messages),
                            stream_active=self.is_running
                        ) * 1000)
                    # Only reset error counter if we actually got a successful API response
                    # Empty messages list is OK (quiet chat), but API errors are not
                    consecutive_poll_errors = 0
                    
                    # Track activity for agentic stream switching
                    if messages:
                        last_activity = time.time()
                        consecutive_empty_polls = 0
                        logger.debug(f"📬 Got {len(messages)} messages - chat is active")
                    else:
                        consecutive_empty_polls += 1
                        time_since_activity = time.time() - last_activity
                        
                        # Agentic detection: Stream might be inactive/ended
                        if time_since_activity > inactivity_timeout:
                            logger.warning(f"⚠️ No chat activity for {time_since_activity:.0f}s - checking stream status")
                            
                            # Quick stream validation
                            try:
                                response = self.youtube.videos().list(
                                    part="liveStreamingDetails,snippet",
                                    id=self.video_id
                                ).execute()
                                
                                items = response.get('items', [])
                                if not items:
                                    logger.warning("🔚 Stream disappeared - likely ended")
                                    self.is_running = False
                                    break
                                    
                                live_details = items[0].get('liveStreamingDetails', {})
                                actual_end_time = live_details.get('actualEndTime')
                                if actual_end_time:
                                    logger.info(f"🔚 Stream confirmed ended at {actual_end_time}")
                                    self.is_running = False
                                    break
                                    
                                # Stream exists but no chat activity
                                if consecutive_empty_polls > 20:  # ~100 seconds of no activity
                                    logger.warning("💤 Stream appears inactive - may be dead or viewers left")
                                    # Signal to auto_moderator to check for new streams
                                    self.is_running = False
                                    break
                                    
                            except Exception as e:
                                logger.warning(f"⚠️ Could not verify stream: {e}")
                                if consecutive_empty_polls > 30:  # Give up after ~150 seconds
                                    logger.info("🔄 Assuming stream ended due to prolonged inactivity")
                                    self.is_running = False
                                    break
                except googleapiclient.errors.HttpError as e:
                    error_details = str(e)
                    consecutive_poll_errors += 1
                    
                    # AUTOMATIC: Handle quota errors intelligently
                    if "quotaExceeded" in error_details or "403" in error_details:
                        logger.warning(f"[AUTO-QUOTA] Quota exceeded error detected")
                        if self.intelligent_throttle:
                            # Automatically switch credential sets
                            new_set = self.intelligent_throttle.handle_quota_error()
                            logger.info(f"[AUTO-QUOTA] Switching to credential set {new_set}")
                            # Increase delay to conserve quota
                            poll_interval_ms = 30000  # 30 seconds minimum
                        else:
                            logger.error("[AUTO-QUOTA] No intelligent throttle available, stopping")
                            self.is_running = False
                            break
                    # Check if it's a "live chat ended" error
                    elif "liveChatEnded" in error_details or "forbidden" in error_details.lower():
                        logger.warning(f"🔚 Live chat has ended: {e}")
                        self.is_running = False
                        break
                    elif "notFound" in error_details:
                        logger.warning(f"🔚 Live chat not found - stream may have ended: {e}")
                        self.is_running = False
                        break
                    else:
                        logger.error(f"❌ Polling error #{consecutive_poll_errors}: {e}")
                        # Only exit after many consecutive API errors (not just quiet chat)
                        if consecutive_poll_errors >= 10:
                            logger.warning("🔚 Too many API errors - checking if stream ended")
                            # Do one final check before giving up
                            try:
                                response = self.youtube.videos().list(
                                    part="liveStreamingDetails",
                                    id=self.video_id
                                ).execute()
                                items = response.get('items', [])
                                if not items or items[0].get('liveStreamingDetails', {}).get('actualEndTime'):
                                    logger.warning("🔚 Confirmed: Stream has ended")
                                    self.is_running = False
                                    break
                            except:
                                pass
                    
                    messages = []
                    poll_interval_ms = 5000
                except Exception as e:
                    # Other non-API errors
                    logger.error(f"❌ Unexpected error polling: {e}")
                    messages = []
                    poll_interval_ms = 5000
                
                # Process messages
                if messages:
                    logger.info(f"Processing {len(messages)} messages")
                    await self.process_message_batch(messages)
                
                # Check for pending batched announcements
                if hasattr(self.message_processor, 'event_handler'):
                    pending_count = self.message_processor.event_handler.get_pending_count()
                    if pending_count > 0:
                        logger.info(f"📦 Checking {pending_count} pending announcements...")
                        # Force flush if we have old pending announcements
                        flushed = self.message_processor.event_handler.force_flush()
                        if flushed:
                            logger.info(f"💥 Flushing batched announcement: {flushed[:50]}...")
                            await self.send_chat_message(flushed, response_type="timeout_announcement")
                
                # Update viewer count periodically
                if time.time() % 60 < 1:  # Every minute
                    self.session_manager.update_viewer_count()
                
                # Wait before next poll
                sleep_time = max(poll_interval_ms / 1000.0, 1.0)
                await asyncio.sleep(sleep_time)
                
            except KeyboardInterrupt:
                logger.info("Keyboard interrupt - stopping")
                self.is_running = False
            except Exception as e:
                logger.error(f"Error in polling loop: {e}")
                await asyncio.sleep(5)
    
    async def start_listening(self) -> None:
        """Start listening to chat messages."""
        if self.is_running:
            logger.warning("Already listening")
            return
        
        logger.info("Starting LiveChatCore...")
        
        # Initialize session
        if not await self.initialize():
            logger.error("Failed to initialize - cannot start")
            return
        
        # Start polling
        self.is_running = True
        
        try:
            await self.run_polling_loop()
        finally:
            self.stop_listening()
    
    def stop_listening(self) -> None:
        """Stop listening to chat messages."""
        if not self.is_running:
            return
        
        logger.info("Stopping LiveChatCore...")
        self.is_running = False
        self.session_manager.end_session()
        
        # Save stats
        logger.info("Final stats:")
        logger.info(self.mod_stats.get_moderation_stats())
    
    # Convenience methods for compatibility
    
    def get_moderation_stats(self) -> Dict[str, Any]:
        """Get moderation statistics."""
        return self.mod_stats.get_moderation_stats()
    
    def get_user_violations(self, user_id: str) -> Dict[str, Any]:
        """Get violations for a specific user."""
        return self.mod_stats.get_user_violations(user_id)
    
    def get_top_violators(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top violators."""
        return self.mod_stats.get_top_violators(limit)
    
    def clear_user_violations(self, user_id: str) -> bool:
        """Clear violations for a user."""
        return self.mod_stats.clear_user_violations(user_id)
    
    def add_banned_phrase(self, phrase: str) -> bool:
        """Add a banned phrase."""
        return self.mod_stats.add_banned_phrase(phrase)
    
    def remove_banned_phrase(self, phrase: str) -> bool:
        """Remove a banned phrase."""
        return self.mod_stats.remove_banned_phrase(phrase)
    
    def get_banned_phrases(self) -> List[str]:
        """Get list of banned phrases."""
        return self.mod_stats.get_banned_phrases()
    
    def configure_emoji_triggers(self, **kwargs) -> Dict[str, Any]:
        """Configure emoji trigger settings."""
        # Now handled by message_processor's consciousness handler
        return {"status": "configured", "settings": kwargs}
    
    async def _post_stream_to_linkedin(self) -> None:
        """
        Post to social media platforms when a YouTube stream goes live.
        Uses browser automation with anti-detection for both LinkedIn and X.
        """
        try:
            # Get stream URL and title
            stream_url = f"https://www.youtube.com/watch?v={self.video_id}"
            
            # Get stream title from session manager
            stream_title = getattr(self.session_manager, 'stream_title', None)
            
            # Include stream title in content
            if stream_title:
                content = f"""@UnDaoDu going live!

{stream_title}

{stream_url}"""
            else:
                # Fallback if no title available
                content = f"""@UnDaoDu going live!

{stream_url}"""
            
            logger.info(f"[SOCIAL] Posting stream to social media platforms...")
            logger.info(f"[SOCIAL] Stream title: {stream_title}")
            logger.info(f"[SOCIAL] Full content to post:")
            for line in content.split('\n'):
                logger.info(f"  {line}")
            
            # Use browser automation with anti-detection for both platforms
            # SEQUENTIAL POSTING: LinkedIn first, then X after completion to prevent browser conflicts
            
            linkedin_success = False
            
            # Post to LinkedIn first using anti-detection browser automation
            if os.getenv('LINKEDIN_EMAIL') and os.getenv('LINKEDIN_PASSWORD'):
                try:
                    logger.info("[LINKEDIN] Using anti-detection browser automation...")
                    from modules.platform_integration.linkedin_agent.src.anti_detection_poster import AntiDetectionLinkedIn
                    
                    # Run in thread to not block async
                    import threading
                    import time
                    
                    linkedin_completed = threading.Event()
                    
                    def post_to_linkedin():
                        nonlocal linkedin_success
                        try:
                            logger.info("[THREAD] LinkedIn posting thread started")
                            linkedin_poster = AntiDetectionLinkedIn()
                            result = linkedin_poster.post_to_company_page(content)
                            if result:
                                logger.info("[OK] Posted to LinkedIn company page!")
                                print("[OK] Posted to LinkedIn company page!")
                                linkedin_success = True
                            else:
                                logger.warning("[FAIL] LinkedIn posting failed")
                                print("[FAIL] LinkedIn posting failed")
                        except Exception as e:
                            logger.error(f"[ERROR] LinkedIn error: {e}")
                            print(f"[ERROR] LinkedIn error: {e}")
                            import traceback
                            traceback.print_exc()
                        finally:
                            linkedin_completed.set()  # Signal completion regardless of success/failure
                    
                    linkedin_thread = threading.Thread(target=post_to_linkedin, daemon=False)
                    linkedin_thread.start()
                    logger.info("[THREAD] LinkedIn thread launched - waiting for completion...")
                    
                    # Wait for LinkedIn to complete (with timeout)
                    linkedin_completed.wait(timeout=120)  # 2 minute timeout
                    logger.info(f"[SEQUENTIAL] LinkedIn completed - Success: {linkedin_success}")
                    
                    # Add small delay to ensure browser cleanup
                    time.sleep(5)
                    
                except Exception as e:
                    logger.error(f"[ERROR] LinkedIn module error: {e}")
            else:
                logger.info("[INFO] LinkedIn credentials not configured")
            
            # Post to X/Twitter AFTER LinkedIn completes - prevents browser conflicts
            if os.getenv('X_Acc1') and os.getenv('x_Acc_pass'):
                try:
                    logger.info("[X/TWITTER] Starting AFTER LinkedIn completion - anti-detection browser automation...")
                    from modules.platform_integration.x_twitter.src.x_anti_detection_poster import AntiDetectionX
                    
                    # Run in thread to not block async
                    import threading
                    def post_to_x():
                        try:
                            logger.info("[THREAD] X/Twitter posting thread started AFTER LinkedIn")
                            x_poster = AntiDetectionX()
                            result = x_poster.post_to_x(content, video_id=self.video_id)
                            if result:
                                logger.info("[OK] Posted to X/Twitter!")
                                print("[OK] Posted to X/Twitter!")
                            else:
                                logger.warning("[FAIL] X/Twitter posting failed")
                                print("[FAIL] X/Twitter posting failed")
                        except Exception as e:
                            logger.error(f"[ERROR] X/Twitter error: {e}")
                            print(f"[ERROR] X/Twitter error: {e}")
                            import traceback
                            traceback.print_exc()
                    
                    x_thread = threading.Thread(target=post_to_x, daemon=False)
                    x_thread.start()
                    logger.info("[THREAD] X thread launched AFTER LinkedIn completion")
                    
                except ImportError:
                    logger.warning("[WARNING] X anti-detection module not yet implemented")
                except Exception as e:
                    logger.error(f"[ERROR] X/Twitter module error: {e}")
            else:
                logger.info("[INFO] X/Twitter credentials not configured")
                    
        except Exception as e:
            logger.error(f"[ERROR] Error posting to social media: {e}")
            # Don't fail the stream initialization if posting fails