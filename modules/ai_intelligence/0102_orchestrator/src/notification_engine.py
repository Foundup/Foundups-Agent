"""
Notification Engine - Multi-Channel User Notifications for 0102

Handles delivery of notifications, alerts, and prompts through various channels.
Supports console output for PoC, with future expansion to Discord, email, push notifications.
"""

import logging
import asyncio
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class NotificationChannel(Enum):
    """Available notification channels"""
    CONSOLE = "console"           # Console/terminal output (PoC)
    DISCORD = "discord"          # Discord DM (future)
    EMAIL = "email"              # Email notification (future)
    PUSH = "push"                # Push notification (future)
    WHATSAPP = "whatsapp"        # WhatsApp message (future)
    SLACK = "slack"              # Slack message (future)


class NotificationPriority(Enum):
    """Notification priority levels"""
    LOW = "low"                  # Non-urgent information
    MEDIUM = "medium"            # Standard notifications
    HIGH = "high"                # Important alerts
    URGENT = "urgent"            # Critical immediate attention
    CRITICAL = "critical"        # System-level emergencies


@dataclass
class NotificationTemplate:
    """Template for notification formatting"""
    channel: NotificationChannel
    priority: NotificationPriority
    title_template: str
    message_template: str
    action_buttons: List[str]
    sound_enabled: bool = True


@dataclass
class Notification:
    """A notification to be delivered"""
    notification_id: str
    user_id: str
    channel: NotificationChannel
    priority: NotificationPriority
    title: str
    message: str
    timestamp: datetime
    action_buttons: List[str]
    metadata: Dict = None
    delivered: bool = False


class NotificationEngine:
    """
    Manages multi-channel notification delivery for 0102.
    
    PoC Implementation:
    - Console output with formatted messages
    - Priority-based formatting
    - Simple delivery tracking
    
    Future Enhancement:
    - Discord bot integration
    - Email delivery via SMTP
    - Push notifications
    - Delivery confirmation tracking
    """
    
    def __init__(self):
        self.templates = self._initialize_templates()
        self.delivery_history: List[Notification] = []
        self.notification_counter = 0
        
        logger.info("NotificationEngine initialized")
    
    def _initialize_templates(self) -> Dict[str, NotificationTemplate]:
        """Initialize notification templates for different scenarios"""
        return {
            "meeting_opportunity": NotificationTemplate(
                channel=NotificationChannel.CONSOLE,
                priority=NotificationPriority.HIGH,
                title_template="[HANDSHAKE] Meeting Opportunity Available",
                message_template="{requester} is available to meet about: {purpose}",
                action_buttons=["Accept", "Decline", "Reschedule"]
            ),
            "presence_change": NotificationTemplate(
                channel=NotificationChannel.CONSOLE,
                priority=NotificationPriority.MEDIUM,
                title_template="[U+1F4E1] Availability Update",
                message_template="{user} is now {status}",
                action_buttons=["Create Meeting Intent"]
            ),
            "meeting_reminder": NotificationTemplate(
                channel=NotificationChannel.CONSOLE,
                priority=NotificationPriority.HIGH,
                title_template="⏰ Meeting Reminder",
                message_template="Meeting with {participant} starts in {time}",
                action_buttons=["Join", "Postpone"]
            ),
            "system_alert": NotificationTemplate(
                channel=NotificationChannel.CONSOLE,
                priority=NotificationPriority.URGENT,
                title_template="[U+26A0]️ System Alert",
                message_template="{message}",
                action_buttons=["Acknowledge"]
            ),
            "general_notification": NotificationTemplate(
                channel=NotificationChannel.CONSOLE,
                priority=NotificationPriority.MEDIUM,
                title_template="ℹ️ Notification",
                message_template="{message}",
                action_buttons=[]
            )
        }
    
    async def send_notification(
        self,
        user_id: str,
        message: str,
        priority: str = "medium",
        channels: List[str] = None,
        template_name: str = "general_notification",
        **kwargs
    ) -> bool:
        """
        Send notification to user through specified channels
        
        Args:
            user_id: Target user identifier
            message: Notification message content
            priority: Priority level (low, medium, high, urgent, critical)
            channels: List of channels to use (defaults to console for PoC)
            template_name: Template to use for formatting
            **kwargs: Additional template variables
        
        Returns:
            bool: True if notification was delivered successfully
        """
        if channels is None:
            channels = ["console"]
        
        # Convert priority string to enum
        try:
            priority_enum = NotificationPriority(priority.lower())
        except ValueError:
            priority_enum = NotificationPriority.MEDIUM
            logger.warning(f"Invalid priority '{priority}', using MEDIUM")
        
        success = True
        
        for channel_str in channels:
            try:
                channel_enum = NotificationChannel(channel_str.lower())
                
                notification = await self._create_notification(
                    user_id=user_id,
                    channel=channel_enum,
                    priority=priority_enum,
                    message=message,
                    template_name=template_name,
                    **kwargs
                )
                
                delivered = await self._deliver_notification(notification)
                success = success and delivered
                
            except ValueError:
                logger.error(f"Invalid notification channel: {channel_str}")
                success = False
        
        return success
    
    async def _create_notification(
        self,
        user_id: str,
        channel: NotificationChannel,
        priority: NotificationPriority,
        message: str,
        template_name: str,
        **kwargs
    ) -> Notification:
        """Create a formatted notification using templates"""
        
        self.notification_counter += 1
        notification_id = f"notif_{self.notification_counter}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Get template
        template = self.templates.get(template_name, self.templates["general_notification"])
        
        # Format title and message with variables
        format_vars = {"message": message, **kwargs}
        
        try:
            title = template.title_template.format(**format_vars)
            formatted_message = template.message_template.format(**format_vars)
        except KeyError as e:
            logger.warning(f"Missing template variable {e}, using raw message")
            title = template.title_template
            formatted_message = message
        
        return Notification(
            notification_id=notification_id,
            user_id=user_id,
            channel=channel,
            priority=priority,
            title=title,
            message=formatted_message,
            timestamp=datetime.now(),
            action_buttons=template.action_buttons.copy(),
            metadata=kwargs
        )
    
    async def _deliver_notification(self, notification: Notification) -> bool:
        """Deliver notification through the specified channel"""
        
        try:
            if notification.channel == NotificationChannel.CONSOLE:
                await self._deliver_console_notification(notification)
            elif notification.channel == NotificationChannel.DISCORD:
                await self._deliver_discord_notification(notification)
            elif notification.channel == NotificationChannel.EMAIL:
                await self._deliver_email_notification(notification)
            else:
                logger.warning(f"Channel {notification.channel} not implemented yet")
                return False
            
            notification.delivered = True
            self.delivery_history.append(notification)
            return True
            
        except Exception as e:
            logger.error(f"Failed to deliver notification {notification.notification_id}: {e}")
            return False
    
    async def _deliver_console_notification(self, notification: Notification):
        """Deliver notification to console with formatting based on priority"""
        
        # Priority-based formatting
        priority_symbols = {
            NotificationPriority.LOW: "[U+1F535]",
            NotificationPriority.MEDIUM: "🟡",
            NotificationPriority.HIGH: "🟠",
            NotificationPriority.URGENT: "[U+1F534]",
            NotificationPriority.CRITICAL: "[U+1F4A5]"
        }
        
        symbol = priority_symbols.get(notification.priority, "ℹ️")
        timestamp = notification.timestamp.strftime("%H:%M:%S")
        
        # Format output
        print(f"\n{symbol} [{timestamp}] {notification.title}")
        print(f"   {notification.message}")
        
        if notification.action_buttons:
            actions = " | ".join(notification.action_buttons)
            print(f"   Actions: {actions}")
        
        print(f"   (Notification ID: {notification.notification_id})")
        
        # Simulate delivery delay for high priority
        if notification.priority in [NotificationPriority.HIGH, NotificationPriority.URGENT]:
            await asyncio.sleep(0.1)  # Brief pause for emphasis
    
    async def _deliver_discord_notification(self, notification: Notification):
        """Deliver notification via Discord DM (future implementation)"""
        logger.info(f"Discord delivery for {notification.notification_id} - Not implemented yet")
        # TODO: Implement Discord bot integration
        # Will use discord.py to send DM to user
        pass
    
    async def _deliver_email_notification(self, notification: Notification):
        """Deliver notification via email (future implementation)"""
        logger.info(f"Email delivery for {notification.notification_id} - Not implemented yet")
        # TODO: Implement SMTP email delivery
        # Will use smtplib or modern email service
        pass
    
    async def notify_meeting_opportunity(
        self,
        user_id: str,
        requester: str,
        purpose: str,
        duration: int,
        priority: str
    ) -> bool:
        """Specialized notification for meeting opportunities"""
        return await self.send_notification(
            user_id=user_id,
            message=f"Meeting opportunity with {requester}",
            priority="high",
            template_name="meeting_opportunity",
            requester=requester,
            purpose=purpose,
            duration=f"{duration} minutes",
            meeting_priority=priority
        )
    
    async def notify_presence_change(
        self,
        user_id: str,
        target_user: str,
        new_status: str
    ) -> bool:
        """Specialized notification for presence changes"""
        return await self.send_notification(
            user_id=user_id,
            message=f"Presence update for {target_user}",
            priority="medium",
            template_name="presence_change",
            user=target_user,
            status=new_status
        )
    
    async def notify_meeting_reminder(
        self,
        user_id: str,
        participant: str,
        start_time: str
    ) -> bool:
        """Specialized notification for meeting reminders"""
        return await self.send_notification(
            user_id=user_id,
            message=f"Upcoming meeting reminder",
            priority="high",
            template_name="meeting_reminder",
            participant=participant,
            time=start_time
        )
    
    def get_delivery_history(self, user_id: str = None) -> List[Notification]:
        """Get notification delivery history, optionally filtered by user"""
        if user_id:
            return [n for n in self.delivery_history if n.user_id == user_id]
        return self.delivery_history.copy()
    
    def get_notification_stats(self) -> Dict:
        """Get statistics about notification delivery"""
        total = len(self.delivery_history)
        delivered = sum(1 for n in self.delivery_history if n.delivered)
        
        by_priority = {}
        for priority in NotificationPriority:
            count = sum(1 for n in self.delivery_history if n.priority == priority)
            by_priority[priority.value] = count
        
        by_channel = {}
        for channel in NotificationChannel:
            count = sum(1 for n in self.delivery_history if n.channel == channel)
            by_channel[channel.value] = count
        
        return {
            "total_notifications": total,
            "delivered_successfully": delivered,
            "delivery_rate": delivered / total if total > 0 else 0,
            "by_priority": by_priority,
            "by_channel": by_channel
        }


# Demo function
async def demo_notification_engine():
    """Demonstrate notification engine capabilities"""
    print("=== NotificationEngine Demo ===")
    
    engine = NotificationEngine()
    
    # Test various notification types
    await engine.notify_meeting_opportunity(
        user_id="demo_user",
        requester="Alice",
        purpose="Project roadmap discussion",
        duration=30,
        priority="high"
    )
    
    await asyncio.sleep(0.5)
    
    await engine.notify_presence_change(
        user_id="demo_user",
        target_user="Bob",
        new_status="online"
    )
    
    await asyncio.sleep(0.5)
    
    await engine.send_notification(
        user_id="demo_user",
        message="System maintenance will begin in 10 minutes",
        priority="urgent",
        template_name="system_alert"
    )
    
    await asyncio.sleep(0.5)
    
    # Show statistics
    stats = engine.get_notification_stats()
    print(f"\n[DATA] Notification Statistics:")
    print(f"Total sent: {stats['total_notifications']}")
    print(f"Delivery rate: {stats['delivery_rate']:.1%}")
    print(f"By priority: {stats['by_priority']}")


if __name__ == "__main__":
    asyncio.run(demo_notification_engine()) 