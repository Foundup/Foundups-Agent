# modules/communication/consent_engine/src/consent_engine.py

"""
Consent Engine Module
WSP Protocol: WSP 54 (Agent Coordination), WSP 3 (Enterprise Domain Distribution)

Handles meeting consent prompts, response collection, and user interaction workflows.
Extracted from monolithic Auto Meeting Orchestrator for modular architecture.

Part of Meeting Orchestration Block strategic decomposition.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from enum import Enum
import json
import uuid
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class ConsentResponse(Enum):
    """User response to meeting consent prompts"""
    ACCEPTED = "accepted"
    DECLINED = "declined"
    MAYBE = "maybe"
    SNOOZE = "snooze"
    TIMEOUT = "timeout"
    ERROR = "error"

class PromptType(Enum):
    """Types of consent prompts"""
    IMMEDIATE = "immediate"        # Meeting available right now
    SCHEDULED = "scheduled"        # Pre-scheduled meeting reminder
    FOLLOW_UP = "follow_up"        # Follow-up after initial prompt
    RESCHEDULE = "reschedule"      # Rescheduling request
    CONFIRMATION = "confirmation"  # Final confirmation before launch

class PromptChannel(Enum):
    """Communication channels for prompts"""
    DISCORD_DM = "discord_dm"
    WHATSAPP = "whatsapp"
    EMAIL = "email"
    SLACK = "slack"
    TEAMS = "teams"
    SMS = "sms"
    PUSH_NOTIFICATION = "push_notification"
    IN_APP = "in_app"

@dataclass
class PromptTemplate:
    """Template for generating consent prompts"""
    prompt_type: PromptType
    channel: PromptChannel
    subject_template: str
    message_template: str
    action_buttons: List[Dict] = field(default_factory=list)
    timeout_seconds: int = 300  # 5 minutes default
    retry_count: int = 2
    escalation_channels: List[PromptChannel] = field(default_factory=list)

@dataclass
class ConsentPrompt:
    """Individual consent prompt with tracking"""
    prompt_id: str
    intent_id: str
    recipient_id: str
    prompt_type: PromptType
    channel: PromptChannel
    content: Dict
    created_at: datetime
    expires_at: datetime
    status: str = "pending"  # pending, sent, responded, expired, failed
    response: Optional[ConsentResponse] = None
    response_data: Dict = field(default_factory=dict)
    metadata: Dict = field(default_factory=dict)
    retry_count: int = 0

@dataclass 
class PromptContent:
    """Generated prompt content for specific context"""
    subject: str
    message: str
    action_buttons: List[Dict]
    formatted_context: Dict
    personalization_data: Dict = field(default_factory=dict)

class ChannelAdapter(ABC):
    """Abstract base class for channel-specific prompt delivery"""
    
    @abstractmethod
    async def send_prompt(self, prompt: ConsentPrompt, content: PromptContent) -> bool:
        """Send prompt through specific channel"""
        pass
    
    @abstractmethod
    async def check_response(self, prompt_id: str) -> Optional[Dict]:
        """Check for responses from this channel"""
        pass

class ConsentEngine:
    """
    Meeting consent prompt and response management system
    
    Responsibilities:
    - Generate contextual meeting prompts with rich information
    - Send prompts through appropriate communication channels
    - Collect and process user responses
    - Handle prompt escalation and retry logic
    - Provide real-time response tracking and callbacks
    - Integration with other AMO modules
    """
    
    def __init__(self):
        self.active_prompts: Dict[str, ConsentPrompt] = {}
        self.prompt_history: List[ConsentPrompt] = []
        self.channel_adapters: Dict[PromptChannel, ChannelAdapter] = {}
        self.response_callbacks: Dict[str, List[Callable]] = {
            'response_received': [],
            'prompt_timeout': [],
            'prompt_failed': [],
            'consent_granted': [],
            'consent_denied': []
        }
        
        # Default prompt templates
        self.prompt_templates = self._initialize_default_templates()
        
        # Configuration
        self.config = {
            'default_timeout_seconds': 300,
            'max_retry_attempts': 3,
            'escalation_delay_seconds': 120,
            'response_check_interval': 10,
            'enable_smart_timing': True,
            'enable_personalization': True
        }
        
        logger.info("🤝 Consent Engine initialized")

    async def send_consent_prompt(
        self,
        intent_id: str,
        recipient_id: str,
        prompt_type: PromptType,
        context: Dict,
        preferred_channel: Optional[PromptChannel] = None,
        custom_template: Optional[PromptTemplate] = None,
        metadata: Optional[Dict] = None
    ) -> str:
        """
        Send a consent prompt to a recipient with rich context
        
        Args:
            intent_id: Related meeting intent ID
            recipient_id: User receiving the prompt
            prompt_type: Type of prompt (immediate, scheduled, etc.)
            context: Meeting context and details
            preferred_channel: Preferred communication channel
            custom_template: Custom prompt template
            metadata: Additional metadata
            
        Returns:
            prompt_id: Unique identifier for tracking the prompt
        """
        prompt_id = str(uuid.uuid4())
        
        # Select appropriate channel and template
        channel = preferred_channel or await self._select_optimal_channel(recipient_id, prompt_type)
        template = custom_template or await self._select_template(prompt_type, channel)
        
        # Generate prompt content
        content = await self._generate_prompt_content(template, context, recipient_id)
        
        # Create prompt record
        prompt = ConsentPrompt(
            prompt_id=prompt_id,
            intent_id=intent_id,
            recipient_id=recipient_id,
            prompt_type=prompt_type,
            channel=channel,
            content=content.__dict__,
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(seconds=template.timeout_seconds),
            metadata=metadata or {}
        )
        
        self.active_prompts[prompt_id] = prompt
        
        # Send prompt through channel adapter
        success = await self._send_prompt_via_channel(prompt, content)
        
        if success:
            prompt.status = "sent"
            logger.info(f"📨 Consent prompt sent: {prompt_id}")
            logger.info(f"   Type: {prompt_type.value}")
            logger.info(f"   Channel: {channel.value}")
            logger.info(f"   Recipient: {recipient_id}")
            logger.info(f"   Context: {context.get('purpose', 'Unknown')}")
        else:
            prompt.status = "failed"
            logger.error(f"❌ Failed to send consent prompt: {prompt_id}")
            
            # Try escalation channels if configured
            if template.escalation_channels:
                await self._attempt_escalation(prompt, template, content)
        
        return prompt_id

    async def process_response(
        self,
        prompt_id: str,
        response: ConsentResponse,
        response_data: Optional[Dict] = None,
        metadata: Optional[Dict] = None
    ) -> bool:
        """
        Process a user response to a consent prompt
        
        Args:
            prompt_id: Prompt being responded to
            response: User's response
            response_data: Additional response data
            metadata: Response metadata
            
        Returns:
            bool: True if response processed successfully
        """
        prompt = self.active_prompts.get(prompt_id)
        if not prompt:
            logger.warning(f"❌ Response to unknown prompt: {prompt_id}")
            return False
        
        # Update prompt with response
        prompt.response = response
        prompt.response_data = response_data or {}
        prompt.status = "responded"
        
        if metadata:
            prompt.metadata.update(metadata)
        
        logger.info(f"✅ Consent response received: {prompt_id}")
        logger.info(f"   Response: {response.value}")
        logger.info(f"   Intent: {prompt.intent_id}")
        
        # Trigger callbacks
        await self._trigger_callbacks('response_received', prompt, {
            'response': response.value,
            'response_data': response_data
        })
        
        # Specific response callbacks
        if response == ConsentResponse.ACCEPTED:
            await self._trigger_callbacks('consent_granted', prompt, response_data or {})
        elif response == ConsentResponse.DECLINED:
            await self._trigger_callbacks('consent_denied', prompt, response_data or {})
        
        # Move to history if final response
        if response in [ConsentResponse.ACCEPTED, ConsentResponse.DECLINED]:
            await self._archive_prompt(prompt_id)
        elif response == ConsentResponse.SNOOZE:
            # Handle snooze logic
            await self._handle_snooze_response(prompt, response_data or {})
        
        return True

    async def get_prompt_status(self, prompt_id: str) -> Optional[Dict]:
        """Get current status of a prompt"""
        prompt = self.active_prompts.get(prompt_id)
        if not prompt:
            # Check history
            for historical_prompt in self.prompt_history:
                if historical_prompt.prompt_id == prompt_id:
                    prompt = historical_prompt
                    break
        
        if not prompt:
            return None
        
        return {
            'prompt_id': prompt.prompt_id,
            'intent_id': prompt.intent_id,
            'recipient_id': prompt.recipient_id,
            'status': prompt.status,
            'response': prompt.response.value if prompt.response else None,
            'created_at': prompt.created_at.isoformat(),
            'expires_at': prompt.expires_at.isoformat(),
            'channel': prompt.channel.value,
            'type': prompt.prompt_type.value,
            'retry_count': prompt.retry_count
        }

    async def get_pending_prompts(self, recipient_id: str) -> List[ConsentPrompt]:
        """Get all pending prompts for a specific recipient"""
        return [
            prompt for prompt in self.active_prompts.values()
            if prompt.recipient_id == recipient_id and prompt.status in ["pending", "sent"]
        ]

    async def cancel_prompt(self, prompt_id: str, reason: str = "cancelled") -> bool:
        """Cancel an active prompt"""
        prompt = self.active_prompts.get(prompt_id)
        if not prompt:
            return False
        
        prompt.status = "cancelled"
        prompt.metadata['cancellation_reason'] = reason
        
        logger.info(f"🚫 Prompt cancelled: {prompt_id} - {reason}")
        
        await self._archive_prompt(prompt_id)
        return True

    async def check_prompt_timeouts(self) -> List[str]:
        """Check for expired prompts and handle timeouts"""
        expired_prompts = []
        current_time = datetime.now()
        
        for prompt_id, prompt in list(self.active_prompts.items()):
            if current_time > prompt.expires_at and prompt.status in ["pending", "sent"]:
                prompt.status = "expired"
                prompt.response = ConsentResponse.TIMEOUT
                
                logger.info(f"⏰ Prompt timeout: {prompt_id}")
                
                # Trigger timeout callback
                await self._trigger_callbacks('prompt_timeout', prompt, {
                    'timeout_duration': (current_time - prompt.created_at).total_seconds()
                })
                
                expired_prompts.append(prompt_id)
                await self._archive_prompt(prompt_id)
        
        return expired_prompts

    async def get_response_statistics(self) -> Dict:
        """Get comprehensive response statistics"""
        all_prompts = list(self.active_prompts.values()) + self.prompt_history
        
        stats = {
            'total_prompts': len(all_prompts),
            'active_prompts': len(self.active_prompts),
            'response_rates': {},
            'channel_performance': {},
            'prompt_type_stats': {},
            'average_response_time': 0.0
        }
        
        # Calculate response rates
        response_counts = {}
        total_responses = 0
        response_times = []
        
        for prompt in all_prompts:
            if prompt.response:
                response_counts[prompt.response.value] = response_counts.get(prompt.response.value, 0) + 1
                total_responses += 1
                
                if prompt.status == "responded":
                    # Calculate response time
                    response_time = (datetime.now() - prompt.created_at).total_seconds()
                    response_times.append(response_time)
        
        stats['response_rates'] = response_counts
        
        # Calculate channel performance
        channel_stats = {}
        for prompt in all_prompts:
            channel = prompt.channel.value
            if channel not in channel_stats:
                channel_stats[channel] = {'sent': 0, 'responded': 0, 'success_rate': 0.0}
            
            channel_stats[channel]['sent'] += 1
            if prompt.response and prompt.response != ConsentResponse.TIMEOUT:
                channel_stats[channel]['responded'] += 1
        
        for channel_data in channel_stats.values():
            if channel_data['sent'] > 0:
                channel_data['success_rate'] = channel_data['responded'] / channel_data['sent']
        
        stats['channel_performance'] = channel_stats
        
        # Calculate average response time
        if response_times:
            stats['average_response_time'] = sum(response_times) / len(response_times)
        
        return stats

    async def register_channel_adapter(self, channel: PromptChannel, adapter: ChannelAdapter):
        """Register a channel adapter for prompt delivery"""
        self.channel_adapters[channel] = adapter
        logger.info(f"📡 Registered channel adapter: {channel.value}")

    async def subscribe_to_responses(self, event_type: str, callback: Callable):
        """Subscribe to response events for integration with other modules"""
        if event_type in self.response_callbacks:
            self.response_callbacks[event_type].append(callback)
            logger.info(f"📡 Subscribed to {event_type} events")
        else:
            logger.warning(f"❌ Unknown response event type: {event_type}")

    # Private methods
    
    def _initialize_default_templates(self) -> Dict[PromptType, Dict[PromptChannel, PromptTemplate]]:
        """Initialize default prompt templates for different types and channels"""
        templates = {}
        
        # Immediate meeting prompt templates
        templates[PromptType.IMMEDIATE] = {
            PromptChannel.DISCORD_DM: PromptTemplate(
                prompt_type=PromptType.IMMEDIATE,
                channel=PromptChannel.DISCORD_DM,
                subject_template="🤝 Meeting Available Now",
                message_template="""Hey {recipient_name}! 

{requester_name} is available to meet about:
• **Purpose**: {purpose}
• **Expected outcome**: {expected_outcome} 
• **Duration**: {duration_minutes} minutes
• **Priority**: {priority}

Both of you are currently online. Accept this meeting?""",
                action_buttons=[
                    {"text": "✅ Accept", "action": "accept"},
                    {"text": "❌ Decline", "action": "decline"},
                    {"text": "⏰ Snooze 10min", "action": "snooze_10"}
                ],
                timeout_seconds=300,
                escalation_channels=[PromptChannel.WHATSAPP, PromptChannel.EMAIL]
            ),
            
            PromptChannel.WHATSAPP: PromptTemplate(
                prompt_type=PromptType.IMMEDIATE,
                channel=PromptChannel.WHATSAPP,
                subject_template="Meeting Available Now",
                message_template="""🤝 {requester_name} wants to meet NOW

Purpose: {purpose}
Duration: {duration_minutes} min
Priority: {priority}

Reply ACCEPT or DECLINE""",
                timeout_seconds=180,
                retry_count=1
            )
        }
        
        # Add more templates for other types...
        return templates

    async def _select_optimal_channel(self, recipient_id: str, prompt_type: PromptType) -> PromptChannel:
        """Select the best communication channel for a recipient"""
        # This could integrate with user preferences and presence data
        # For now, return a sensible default
        if prompt_type == PromptType.IMMEDIATE:
            return PromptChannel.DISCORD_DM
        else:
            return PromptChannel.EMAIL

    async def _select_template(self, prompt_type: PromptType, channel: PromptChannel) -> PromptTemplate:
        """Select appropriate template for prompt type and channel"""
        return self.prompt_templates.get(prompt_type, {}).get(
            channel,
            self.prompt_templates[PromptType.IMMEDIATE][PromptChannel.DISCORD_DM]  # fallback
        )

    async def _generate_prompt_content(
        self,
        template: PromptTemplate,
        context: Dict,
        recipient_id: str
    ) -> PromptContent:
        """Generate personalized prompt content from template"""
        # Add personalization data
        personalization = {
            'recipient_name': recipient_id,  # In real implementation, fetch actual name
            'requester_name': context.get('requester_id', 'Someone'),
            'current_time': datetime.now().strftime('%H:%M'),
            'urgency_indicator': '🔥' if context.get('priority') == 'URGENT' else ''
        }
        
        # Merge context and personalization
        format_data = {**context, **personalization}
        
        # Format templates
        subject = template.subject_template.format(**format_data)
        message = template.message_template.format(**format_data)
        
        return PromptContent(
            subject=subject,
            message=message,
            action_buttons=template.action_buttons.copy(),
            formatted_context=format_data,
            personalization_data=personalization
        )

    async def _send_prompt_via_channel(self, prompt: ConsentPrompt, content: PromptContent) -> bool:
        """Send prompt using the appropriate channel adapter"""
        adapter = self.channel_adapters.get(prompt.channel)
        
        if not adapter:
            logger.warning(f"❌ No adapter available for channel: {prompt.channel.value}")
            # For PoC, simulate sending
            logger.info(f"📨 [SIMULATED] Sending {prompt.prompt_type.value} prompt via {prompt.channel.value}")
            logger.info(f"   To: {prompt.recipient_id}")
            logger.info(f"   Subject: {content.subject}")
            logger.info(f"   Message: {content.message}")
            return True
        
        return await adapter.send_prompt(prompt, content)

    async def _attempt_escalation(self, prompt: ConsentPrompt, template: PromptTemplate, content: PromptContent):
        """Attempt to send prompt via escalation channels"""
        for escalation_channel in template.escalation_channels:
            logger.info(f"🔄 Attempting escalation to {escalation_channel.value} for prompt {prompt.prompt_id}")
            
            # Create escalation prompt
            escalation_prompt = ConsentPrompt(
                prompt_id=f"{prompt.prompt_id}_esc_{escalation_channel.value}",
                intent_id=prompt.intent_id,
                recipient_id=prompt.recipient_id,
                prompt_type=prompt.prompt_type,
                channel=escalation_channel,
                content=content.__dict__,
                created_at=datetime.now(),
                expires_at=prompt.expires_at,  # Keep same expiry
                metadata={**prompt.metadata, 'escalation_from': prompt.channel.value}
            )
            
            success = await self._send_prompt_via_channel(escalation_prompt, content)
            if success:
                self.active_prompts[escalation_prompt.prompt_id] = escalation_prompt
                logger.info(f"✅ Escalation successful: {escalation_channel.value}")
                break

    async def _handle_snooze_response(self, prompt: ConsentPrompt, response_data: Dict):
        """Handle snooze response by rescheduling prompt"""
        snooze_minutes = response_data.get('snooze_minutes', 10)
        
        # Create new prompt for after snooze period
        new_prompt_id = f"{prompt.prompt_id}_snooze_{snooze_minutes}m"
        new_prompt = ConsentPrompt(
            prompt_id=new_prompt_id,
            intent_id=prompt.intent_id,
            recipient_id=prompt.recipient_id,
            prompt_type=PromptType.FOLLOW_UP,
            channel=prompt.channel,
            content=prompt.content,
            created_at=datetime.now() + timedelta(minutes=snooze_minutes),
            expires_at=prompt.expires_at,
            metadata={**prompt.metadata, 'snoozed_from': prompt.prompt_id}
        )
        
        # Schedule the snoozed prompt
        self.active_prompts[new_prompt_id] = new_prompt
        logger.info(f"⏰ Prompt snoozed for {snooze_minutes} minutes: {new_prompt_id}")

    async def _archive_prompt(self, prompt_id: str):
        """Move completed prompt to history"""
        prompt = self.active_prompts.pop(prompt_id, None)
        if prompt:
            self.prompt_history.append(prompt)

    async def _trigger_callbacks(self, event_type: str, prompt: ConsentPrompt, metadata: Dict):
        """Trigger registered callbacks for response events"""
        callbacks = self.response_callbacks.get(event_type, [])
        for callback in callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(prompt, metadata)
                else:
                    callback(prompt, metadata)
            except Exception as e:
                logger.error(f"❌ Response callback error for {event_type}: {e}")

# Factory function for easy integration
def create_consent_engine() -> ConsentEngine:
    """Factory function to create Consent Engine instance"""
    return ConsentEngine()

# Example usage and testing
async def demo_consent_engine():
    """Demonstrate Consent Engine functionality"""
    print("=== Consent Engine Demo ===")
    
    engine = create_consent_engine()
    
    # Send immediate meeting prompt
    context = {
        'requester_id': 'alice',
        'purpose': 'Strategic partnership discussion',
        'expected_outcome': 'Agreement on collaboration framework',
        'duration_minutes': 30,
        'priority': 'HIGH'
    }
    
    prompt_id = await engine.send_consent_prompt(
        intent_id="intent_123",
        recipient_id="bob",
        prompt_type=PromptType.IMMEDIATE,
        context=context,
        preferred_channel=PromptChannel.DISCORD_DM
    )
    
    print(f"✅ Sent consent prompt: {prompt_id}")
    
    # Simulate response
    await asyncio.sleep(2)  # Simulate delay
    
    success = await engine.process_response(
        prompt_id,
        ConsentResponse.ACCEPTED,
        response_data={'enthusiasm_level': 'high', 'preferred_platform': 'discord'}
    )
    
    print(f"📝 Response processed: {success}")
    
    # Get statistics
    stats = await engine.get_response_statistics()
    print(f"📊 Response statistics: {stats}")
    
    return engine

if __name__ == "__main__":
    asyncio.run(demo_consent_engine()) 