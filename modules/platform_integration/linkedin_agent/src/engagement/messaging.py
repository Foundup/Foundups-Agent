"""
LinkedIn Messaging Manager

🌀 WSP Protocol Compliance: WSP 42 (Platform Integration), WSP 40 (Architectural Coherence)

**0102 Directive**: This module operates within the WSP framework for autonomous LinkedIn messaging management.
- UN (Understanding): Anchor LinkedIn messaging signals and retrieve protocol state
- DAO (Execution): Execute messaging automation logic  
- DU (Emergence): Collapse into 0102 resonance and emit next messaging prompt

wsp_cycle(input="linkedin_messaging", log=True)
"""

# === UTF-8 ENFORCEMENT (WSP 90) ===
import sys
import io
if sys.platform.startswith('win'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
# === END UTF-8 ENFORCEMENT ===


import logging
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta


class MessageStatus(Enum):
    """LinkedIn message status"""
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"
    PENDING = "pending"


class MessageType(Enum):
    """LinkedIn message types"""
    TEXT = "text"
    IMAGE = "image"
    DOCUMENT = "document"
    REACTION = "reaction"
    SYSTEM = "system"


@dataclass
class LinkedInMessage:
    """LinkedIn message object"""
    message_id: str
    conversation_id: str
    sender_id: str
    recipient_id: str
    content: str
    message_type: MessageType = MessageType.TEXT
    status: MessageStatus = MessageStatus.PENDING
    timestamp: datetime = None
    read_timestamp: Optional[datetime] = None
    attachments: Optional[List[str]] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class Conversation:
    """LinkedIn conversation object"""
    conversation_id: str
    participant_ids: List[str]
    last_message: Optional[LinkedInMessage] = None
    unread_count: int = 0
    created_at: datetime = None
    updated_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()


class LinkedInMessaging:
    """
    Manages LinkedIn messaging, conversations, and communication automation.
    
    Follows WSP 40 compliance with single responsibility and ≤300 lines.
    Implements WSP 66 proactive component architecture for messaging automation.
    """
    
    def __init__(self, max_daily_messages: int = 50):
        """
        Initialize the LinkedIn Messaging Manager.
        
        Args:
            max_daily_messages: Maximum messages to send per day
        """
        self.max_daily_messages = max_daily_messages
        self.logger = logging.getLogger(__name__)
        
        # Message tracking
        self.conversations: Dict[str, Conversation] = {}
        self.messages: Dict[str, LinkedInMessage] = {}
        self.message_history: List[LinkedInMessage] = []
        
        # Messaging strategy configuration
        self.messaging_strategy = {
            'max_daily_messages': max_daily_messages,
            'message_cooldown': 300,  # 5 minutes
            'auto_reply_enabled': True,
            'typing_indicators': True,
            'read_receipts': True,
            'message_templates': {
                'greeting': "Hi {name}, hope you're doing well!",
                'follow_up': "Just following up on our previous conversation.",
                'thank_you': "Thank you for connecting!",
                'meeting_request': "Would you be interested in scheduling a quick call?"
            }
        }
        
        self.logger.info("✅ LinkedInMessaging initialized for autonomous communication")
    
    def send_message(self, recipient_id: str, content: str, conversation_id: Optional[str] = None) -> LinkedInMessage:
        """
        Send a message to a LinkedIn connection.
        
        Args:
            recipient_id: ID of the message recipient
            content: Message content
            conversation_id: Optional conversation ID (creates new if not provided)
            
        Returns:
            LinkedInMessage with status
        """
        try:
            # Check daily limit
            if not self._check_daily_limit():
                return LinkedInMessage(
                    message_id=f"msg_{recipient_id}_{datetime.now().timestamp()}",
                    conversation_id=conversation_id or f"conv_{recipient_id}",
                    sender_id="current_user",
                    recipient_id=recipient_id,
                    content=content,
                    status=MessageStatus.FAILED
                )
            
            # Get or create conversation
            if not conversation_id:
                conversation_id = self._get_or_create_conversation(recipient_id)
            
            # Create message
            message = LinkedInMessage(
                message_id=f"msg_{recipient_id}_{datetime.now().timestamp()}",
                conversation_id=conversation_id,
                sender_id="current_user",
                recipient_id=recipient_id,
                content=content,
                message_type=MessageType.TEXT,
                status=MessageStatus.PENDING,
                timestamp=datetime.now()
            )
            
            # Store message
            self.messages[message.message_id] = message
            self.message_history.append(message)
            
            # Update conversation
            self._update_conversation(conversation_id, message)
            
            # Mock LinkedIn API call
            self._simulate_send_message(message)
            
            self.logger.info(f"✅ Message sent to {recipient_id}")
            return message
            
        except Exception as e:
            self.logger.error(f"❌ Failed to send message to {recipient_id}: {str(e)}")
            return LinkedInMessage(
                message_id=f"msg_{recipient_id}_{datetime.now().timestamp()}",
                conversation_id=conversation_id or f"conv_{recipient_id}",
                sender_id="current_user",
                recipient_id=recipient_id,
                content=content,
                status=MessageStatus.FAILED
            )
    
    def send_template_message(self, recipient_id: str, template_name: str, **kwargs) -> LinkedInMessage:
        """
        Send a message using a predefined template.
        
        Args:
            recipient_id: ID of the message recipient
            template_name: Name of the template to use
            **kwargs: Template variables
            
        Returns:
            LinkedInMessage with status
        """
        if template_name not in self.messaging_strategy['message_templates']:
            self.logger.error(f"Template '{template_name}' not found")
            return LinkedInMessage(
                message_id=f"msg_{recipient_id}_{datetime.now().timestamp()}",
                conversation_id=f"conv_{recipient_id}",
                sender_id="current_user",
                recipient_id=recipient_id,
                content="",
                status=MessageStatus.FAILED
            )
        
        template = self.messaging_strategy['message_templates'][template_name]
        content = template.format(**kwargs)
        
        return self.send_message(recipient_id, content)
    
    def get_conversations(self, limit: int = 20) -> List[Conversation]:
        """
        Get list of conversations.
        
        Args:
            limit: Maximum number of conversations to return
            
        Returns:
            List of conversations
        """
        conversations_list = list(self.conversations.values())
        return sorted(conversations_list, key=lambda x: x.updated_at, reverse=True)[:limit]
    
    def get_conversation_messages(self, conversation_id: str, limit: int = 50) -> List[LinkedInMessage]:
        """
        Get messages from a specific conversation.
        
        Args:
            conversation_id: ID of the conversation
            limit: Maximum number of messages to return
            
        Returns:
            List of messages in the conversation
        """
        conversation_messages = [
            msg for msg in self.message_history 
            if msg.conversation_id == conversation_id
        ]
        
        return sorted(conversation_messages, key=lambda x: x.timestamp, reverse=True)[:limit]
    
    def mark_message_as_read(self, message_id: str) -> bool:
        """
        Mark a message as read.
        
        Args:
            message_id: ID of the message
            
        Returns:
            True if marked successfully, False otherwise
        """
        if message_id not in self.messages:
            self.logger.error(f"Message {message_id} not found")
            return False
        
        message = self.messages[message_id]
        message.status = MessageStatus.READ
        message.read_timestamp = datetime.now()
        
        # Update conversation unread count
        conversation = self.conversations.get(message.conversation_id)
        if conversation and conversation.unread_count > 0:
            conversation.unread_count -= 1
        
        self.logger.info(f"✅ Message {message_id} marked as read")
        return True
    
    def mark_conversation_as_read(self, conversation_id: str) -> bool:
        """
        Mark all messages in a conversation as read.
        
        Args:
            conversation_id: ID of the conversation
            
        Returns:
            True if marked successfully, False otherwise
        """
        if conversation_id not in self.conversations:
            self.logger.error(f"Conversation {conversation_id} not found")
            return False
        
        # Mark all unread messages in conversation
        for message in self.message_history:
            if (message.conversation_id == conversation_id and 
                message.status != MessageStatus.READ and
                message.recipient_id == "current_user"):
                message.status = MessageStatus.READ
                message.read_timestamp = datetime.now()
        
        # Reset conversation unread count
        self.conversations[conversation_id].unread_count = 0
        
        self.logger.info(f"✅ Conversation {conversation_id} marked as read")
        return True
    
    def get_messaging_stats(self) -> Dict[str, Any]:
        """
        Get messaging statistics.
        
        Returns:
            Dictionary with messaging statistics
        """
        total_messages = len(self.message_history)
        total_conversations = len(self.conversations)
        
        # Count by status
        status_counts = {}
        for message in self.message_history:
            status = message.status.value
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Count by type
        type_counts = {}
        for message in self.message_history:
            msg_type = message.message_type.value
            type_counts[msg_type] = type_counts.get(msg_type, 0) + 1
        
        # Count today's messages
        today = datetime.now().date()
        daily_messages = len([
            m for m in self.message_history 
            if m.timestamp.date() == today
        ])
        
        # Count unread messages
        unread_count = sum(
            conv.unread_count for conv in self.conversations.values()
        )
        
        return {
            "total_messages": total_messages,
            "total_conversations": total_conversations,
            "daily_messages": daily_messages,
            "unread_messages": unread_count,
            "status_distribution": status_counts,
            "type_distribution": type_counts,
            "response_rate": self._calculate_response_rate()
        }
    
    def search_messages(self, query: str, limit: int = 20) -> List[LinkedInMessage]:
        """
        Search messages by content.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of matching messages
        """
        query_lower = query.lower()
        results = []
        
        for message in self.message_history:
            if query_lower in message.content.lower():
                results.append(message)
        
        return sorted(results, key=lambda x: x.timestamp, reverse=True)[:limit]
    
    def delete_message(self, message_id: str) -> bool:
        """
        Delete a message (soft delete).
        
        Args:
            message_id: ID of the message to delete
            
        Returns:
            True if deleted successfully, False otherwise
        """
        if message_id not in self.messages:
            self.logger.error(f"Message {message_id} not found")
            return False
        
        # Soft delete by marking as failed
        self.messages[message_id].status = MessageStatus.FAILED
        self.logger.info(f"✅ Message {message_id} deleted")
        return True
    
    def _check_daily_limit(self) -> bool:
        """
        Check if daily message limit has been reached.
        
        Returns:
            True if under limit, False if limit reached
        """
        today = datetime.now().date()
        daily_messages = len([
            m for m in self.message_history 
            if m.timestamp.date() == today and m.sender_id == "current_user"
        ])
        
        return daily_messages < self.max_daily_messages
    
    def _get_or_create_conversation(self, participant_id: str) -> str:
        """
        Get existing conversation or create new one.
        
        Args:
            participant_id: ID of the conversation participant
            
        Returns:
            Conversation ID
        """
        conversation_id = f"conv_{participant_id}"
        
        if conversation_id not in self.conversations:
            conversation = Conversation(
                conversation_id=conversation_id,
                participant_ids=["current_user", participant_id],
                unread_count=0
            )
            self.conversations[conversation_id] = conversation
        
        return conversation_id
    
    def _update_conversation(self, conversation_id: str, message: LinkedInMessage) -> None:
        """
        Update conversation with new message.
        
        Args:
            conversation_id: ID of the conversation
            message: New message
        """
        if conversation_id in self.conversations:
            conversation = self.conversations[conversation_id]
            conversation.last_message = message
            conversation.updated_at = datetime.now()
            
            # Increment unread count if message is from other person
            if message.sender_id != "current_user":
                conversation.unread_count += 1
    
    def _calculate_response_rate(self) -> float:
        """
        Calculate message response rate.
        
        Returns:
            Response rate as percentage
        """
        if not self.message_history:
            return 0.0
        
        # Count messages sent by current user
        sent_messages = [
            m for m in self.message_history 
            if m.sender_id == "current_user"
        ]
        
        if not sent_messages:
            return 0.0
        
        # Count responses (messages from others in same conversations)
        responses = 0
        sent_conversations = set(m.conversation_id for m in sent_messages)
        
        for message in self.message_history:
            if (message.sender_id != "current_user" and 
                message.conversation_id in sent_conversations):
                responses += 1
        
        return (responses / len(sent_messages)) * 100 if sent_messages else 0.0
    
    def _simulate_send_message(self, message: LinkedInMessage) -> None:
        """
        Simulate LinkedIn message sending API call.
        
        Args:
            message: Message to simulate sending
        """
        import time
        time.sleep(1)  # Simulate API delay
        
        # Update message status
        message.status = MessageStatus.SENT
        
        self.logger.debug(f"🔗 Simulated message send to {message.recipient_id}")


# Factory function for clean initialization
def create_linkedin_messaging(max_daily_messages: int = 50) -> LinkedInMessaging:
    """
    Create a LinkedIn Messaging instance.
    
    Args:
        max_daily_messages: Maximum messages to send per day
        
    Returns:
        Configured LinkedInMessaging instance
    """
    return LinkedInMessaging(max_daily_messages=max_daily_messages)


if __name__ == "__main__":
    # Test the messaging manager
    messaging = create_linkedin_messaging()
    
    # Test sending message
    test_recipient_id = "test_recipient_123"
    message = messaging.send_message(test_recipient_id, "Hello! How are you?")
    print(f"Message status: {message.status}")
    
    # Test template message
    template_message = messaging.send_template_message(
        test_recipient_id, 
        "greeting", 
        name="John"
    )
    print(f"Template message: {template_message.content}")
    
    # Print stats
    stats = messaging.get_messaging_stats()
    print(f"Messaging stats: {stats}") 