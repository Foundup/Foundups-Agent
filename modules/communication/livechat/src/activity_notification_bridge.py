"""
Activity Notification Bridge - WSP Compliant Module
Bridges activity control system with live stream chat notifications.

WSP Compliance: WSP 3 (Module Organization), WSP 49 (Module Structure)
"""

import logging
import asyncio
from typing import Optional
import sys
import os

# Import activity control system
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../../'))
try:
    from modules.infrastructure.activity_control.src.activity_control import controller
except ImportError:
    controller = None

logger = logging.getLogger(__name__)


class ActivityNotificationBridge:
    """
    Bridges activity control system notifications with live stream chat.
    Automatically sends notifications to viewers when system activities are controlled.
    """
    
    def __init__(self, chat_sender=None):
        """
        Initialize the notification bridge.
        
        Args:
            chat_sender: ChatSender instance for sending notifications to stream
        """
        self.chat_sender = chat_sender
        self._notification_queue = asyncio.Queue()
        self._notification_task = None
        self.enabled = True
        
        # Register with activity controller if available
        if controller:
            controller.set_notification_callback(self._queue_notification)
            logger.info("🎛️ Activity notification bridge registered with controller")
        else:
            logger.warning("⚠️ Activity controller not available - notifications disabled")
    
    def set_chat_sender(self, chat_sender):
        """Set or update the chat sender instance"""
        self.chat_sender = chat_sender
        logger.info("📢 Chat sender registered with notification bridge")
    
    def _queue_notification(self, message: str):
        """Queue notification for async processing"""
        if self.enabled and self._notification_queue:
            try:
                self._notification_queue.put_nowait(message)
            except asyncio.QueueFull:
                logger.warning("⚠️ Notification queue full, dropping message")
    
    async def start_notification_processor(self):
        """Start the background notification processor"""
        if self._notification_task is None:
            self._notification_task = asyncio.create_task(self._process_notifications())
            logger.info("📢 Activity notification processor started")
    
    async def stop_notification_processor(self):
        """Stop the background notification processor"""
        if self._notification_task:
            self._notification_task.cancel()
            try:
                await self._notification_task
            except asyncio.CancelledError:
                pass
            self._notification_task = None
            logger.info("📢 Activity notification processor stopped")
    
    async def _process_notifications(self):
        """Background task to process queued notifications"""
        while True:
            try:
                # Wait for notification with timeout
                try:
                    message = await asyncio.wait_for(
                        self._notification_queue.get(), 
                        timeout=1.0
                    )
                    await self._send_stream_notification(message)
                except asyncio.TimeoutError:
                    continue
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Error processing notification: {e}")
                await asyncio.sleep(1)
    
    async def _send_stream_notification(self, message: str):
        """Send notification to live stream chat"""
        if not self.chat_sender:
            logger.debug(f"📢 Notification (no chat sender): {message}")
            return
        
        try:
            # Send notification with system response type
            success = await self.chat_sender.send_message(
                message_text=message,
                response_type='system',
                skip_delay=True  # System notifications should be immediate
            )
            
            if success:
                logger.info(f"📢 Stream notification sent: {message}")
            else:
                logger.warning(f"⚠️ Failed to send stream notification: {message}")
                
        except Exception as e:
            logger.error(f"❌ Error sending stream notification: {e}")
    
    def enable_notifications(self):
        """Enable stream notifications"""
        self.enabled = True
        logger.info("📢 Activity stream notifications enabled")
    
    def disable_notifications(self):
        """Disable stream notifications"""
        self.enabled = False
        logger.info("📢 Activity stream notifications disabled")


# Global instance for system-wide access
notification_bridge = ActivityNotificationBridge()


async def initialize_activity_notifications(chat_sender):
    """
    Initialize activity notifications with chat sender.
    Call this when the LiveChat system is ready.
    """
    notification_bridge.set_chat_sender(chat_sender)
    await notification_bridge.start_notification_processor()
    logger.info("✅ Activity notifications initialized and ready")


async def shutdown_activity_notifications():
    """Shutdown activity notifications gracefully"""
    await notification_bridge.stop_notification_processor()
    logger.info("✅ Activity notifications shut down")