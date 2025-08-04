"""
Channel Selector - WSP/WRE Communication Module

WSP Compliance:
- WSP 34 (Testing Protocol): Comprehensive channel selection and testing capabilities
- WSP 54 (Agent Duties): AI-powered channel selection for autonomous communication
- WSP 22 (ModLog): Change tracking and selection history
- WSP 50 (Pre-Action Verification): Enhanced verification before channel selection

Provides AI-powered channel selection capabilities for autonomous communication operations.
Enables 0102 pArtifacts to intelligently select communication channels based on context and requirements.
"""

import json
import re
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path


class ChannelType(Enum):
    """Communication channel types."""
    LIVE_CHAT = "live_chat"
    EMAIL = "email"
    SLACK = "slack"
    DISCORD = "discord"
    TEAMS = "teams"
    ZOOM = "zoom"
    MEET = "meet"
    PHONE = "phone"
    SMS = "sms"
    API = "api"
    WEBHOOK = "webhook"


class MessagePriority(Enum):
    """Message priority levels."""
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4
    MINIMAL = 5


@dataclass
class ChannelConfig:
    """Configuration for a communication channel."""
    channel_type: ChannelType
    name: str
    endpoint: str
    credentials: Dict[str, str]
    capabilities: List[str]
    availability: Dict[str, Any]
    wsp_compliance: Dict[str, bool]
    priority_weight: float


@dataclass
class MessageContext:
    """Context information for message routing."""
    sender: str
    recipients: List[str]
    priority: MessagePriority
    content_type: str
    urgency: float
    confidentiality: float
    wsp_references: List[str]
    metadata: Dict[str, Any]


@dataclass
class ChannelSelection:
    """Result of channel selection operation."""
    selected_channel: ChannelConfig
    alternative_channels: List[ChannelConfig]
    selection_reason: str
    confidence_score: float
    wsp_compliance_score: float
    recommendations: List[str]
    timestamp: datetime


class ChannelSelector:
    """
    AI-powered channel selector for autonomous communication operations.
    
    Provides comprehensive channel selection including:
    - Multi-factor channel selection algorithm
    - WSP compliance integration
    - Priority-based routing
    - Availability checking
    - Security and confidentiality assessment
    """
    
    def __init__(self):
        """Initialize the channel selector with WSP compliance standards."""
        self.channels = {}
        self.selection_weights = {
            'priority': 0.25,
            'availability': 0.20,
            'capabilities': 0.18,
            'security': 0.15,
            'wsp_compliance': 0.12,
            'performance': 0.10
        }
        
        self.wsp_keywords = [
            'wsp', 'protocol', 'compliance', '0102', 'partifact', 'quantum',
            'autonomous', 'agent', 'modular', 'testing', 'documentation'
        ]
        
        self._initialize_default_channels()
    
    def _initialize_default_channels(self):
        """Initialize default communication channels."""
        default_channels = [
            {
                'type': ChannelType.LIVE_CHAT,
                'name': 'YouTube Live Chat',
                'endpoint': 'youtube_live_chat',
                'capabilities': ['real_time', 'text', 'emoji', 'moderation'],
                'priority_weight': 0.8
            },
            {
                'type': ChannelType.EMAIL,
                'name': 'Email System',
                'endpoint': 'smtp_server',
                'capabilities': ['asynchronous', 'attachments', 'threading'],
                'priority_weight': 0.6
            },
            {
                'type': ChannelType.API,
                'name': 'WSP API Gateway',
                'endpoint': 'wre_api_gateway',
                'capabilities': ['programmatic', 'structured', 'automated'],
                'priority_weight': 0.9
            },
            {
                'type': ChannelType.WEBHOOK,
                'name': 'Webhook System',
                'endpoint': 'webhook_endpoint',
                'capabilities': ['event_driven', 'real_time', 'automated'],
                'priority_weight': 0.7
            }
        ]
        
        for channel_data in default_channels:
            config = ChannelConfig(
                channel_type=channel_data['type'],
                name=channel_data['name'],
                endpoint=channel_data['endpoint'],
                credentials={},
                capabilities=channel_data['capabilities'],
                availability={'status': 'available', 'hours': '24/7'},
                wsp_compliance={'modlog_present': True, 'readme_present': True},
                priority_weight=channel_data['priority_weight']
            )
            self.channels[channel_data['type']] = config
    
    def select_channel(self, message_context: MessageContext) -> ChannelSelection:
        """
        Select the best communication channel for a message.
        
        Args:
            message_context: MessageContext object containing routing information
            
        Returns:
            ChannelSelection with selected channel and alternatives
        """
        try:
            # Score all available channels
            channel_scores = {}
            for channel_type, config in self.channels.items():
                score = self._calculate_channel_score(config, message_context)
                channel_scores[channel_type] = score
            
            # Sort channels by score (higher is better)
            sorted_channels = sorted(
                channel_scores.items(), 
                key=lambda x: x[1], 
                reverse=True
            )
            
            # Select best channel
            selected_type, selected_score = sorted_channels[0]
            selected_channel = self.channels[selected_type]
            
            # Get alternative channels
            alternative_channels = []
            for channel_type, score in sorted_channels[1:3]:  # Top 3 alternatives
                alternative_channels.append(self.channels[channel_type])
            
            # Generate selection reason
            selection_reason = self._generate_selection_reason(
                selected_channel, message_context, selected_score
            )
            
            # Calculate confidence score
            confidence_score = self._calculate_confidence(
                selected_score, len(sorted_channels)
            )
            
            # Calculate WSP compliance score
            wsp_compliance_score = self._calculate_wsp_compliance(
                selected_channel, message_context
            )
            
            # Generate recommendations
            recommendations = self._generate_recommendations(
                selected_channel, message_context, selected_score
            )
            
            return ChannelSelection(
                selected_channel=selected_channel,
                alternative_channels=alternative_channels,
                selection_reason=selection_reason,
                confidence_score=confidence_score,
                wsp_compliance_score=wsp_compliance_score,
                recommendations=recommendations,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            # Return default selection on error
            default_channel = self.channels.get(ChannelType.API, list(self.channels.values())[0])
            return ChannelSelection(
                selected_channel=default_channel,
                alternative_channels=[],
                selection_reason=f"Error during selection: {str(e)}",
                confidence_score=0.0,
                wsp_compliance_score=0.0,
                recommendations=["Use default channel due to selection error"],
                timestamp=datetime.now()
            )
    
    def add_channel(self, channel_config: ChannelConfig) -> bool:
        """
        Add a new communication channel.
        
        Args:
            channel_config: ChannelConfig object for the new channel
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.channels[channel_config.channel_type] = channel_config
            return True
        except Exception as e:
            print(f"Error adding channel: {e}")
            return False
    
    def remove_channel(self, channel_type: ChannelType) -> bool:
        """
        Remove a communication channel.
        
        Args:
            channel_type: ChannelType to remove
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if channel_type in self.channels:
                del self.channels[channel_type]
                return True
            return False
        except Exception as e:
            print(f"Error removing channel: {e}")
            return False
    
    def _calculate_channel_score(self, channel: ChannelConfig, 
                                context: MessageContext) -> float:
        """Calculate score for a channel based on context."""
        score = 0.0
        
        # Priority factor
        priority_score = self._calculate_priority_score(channel, context)
        score += priority_score * self.selection_weights['priority']
        
        # Availability factor
        availability_score = self._calculate_availability_score(channel)
        score += availability_score * self.selection_weights['availability']
        
        # Capabilities factor
        capabilities_score = self._calculate_capabilities_score(channel, context)
        score += capabilities_score * self.selection_weights['capabilities']
        
        # Security factor
        security_score = self._calculate_security_score(channel, context)
        score += security_score * self.selection_weights['security']
        
        # WSP compliance factor
        wsp_score = self._calculate_wsp_compliance_score(channel)
        score += wsp_score * self.selection_weights['wsp_compliance']
        
        # Performance factor
        performance_score = self._calculate_performance_score(channel)
        score += performance_score * self.selection_weights['performance']
        
        return min(max(score, 0.0), 100.0)
    
    def _calculate_priority_score(self, channel: ChannelConfig, 
                                 context: MessageContext) -> float:
        """Calculate priority-based score."""
        # Higher priority messages should use higher priority channels
        priority_multiplier = {
            MessagePriority.CRITICAL: 1.0,
            MessagePriority.HIGH: 0.8,
            MessagePriority.MEDIUM: 0.6,
            MessagePriority.LOW: 0.4,
            MessagePriority.MINIMAL: 0.2
        }
        
        base_score = channel.priority_weight * 100
        return base_score * priority_multiplier.get(context.priority, 0.5)
    
    def _calculate_availability_score(self, channel: ChannelConfig) -> float:
        """Calculate availability score."""
        availability = channel.availability.get('status', 'unknown')
        
        if availability == 'available':
            return 100.0
        elif availability == 'limited':
            return 60.0
        elif availability == 'unavailable':
            return 0.0
        else:
            return 50.0  # Unknown status
    
    def _calculate_capabilities_score(self, channel: ChannelConfig, 
                                    context: MessageContext) -> float:
        """Calculate capabilities score."""
        score = 50.0  # Base score
        
        # Check if channel supports required capabilities
        required_capabilities = self._get_required_capabilities(context)
        
        for capability in required_capabilities:
            if capability in channel.capabilities:
                score += 10.0
        
        return min(score, 100.0)
    
    def _calculate_security_score(self, channel: ChannelConfig, 
                                context: MessageContext) -> float:
        """Calculate security score."""
        score = 70.0  # Base security score
        
        # Adjust based on confidentiality requirements
        if context.confidentiality > 0.8:
            # High confidentiality - prefer secure channels
            if channel.channel_type in [ChannelType.EMAIL, ChannelType.API]:
                score += 20.0
            elif channel.channel_type == ChannelType.LIVE_CHAT:
                score -= 10.0
        
        return min(max(score, 0.0), 100.0)
    
    def _calculate_wsp_compliance_score(self, channel: ChannelConfig) -> float:
        """Calculate WSP compliance score."""
        compliance = channel.wsp_compliance
        
        score = 0.0
        if compliance.get('modlog_present', False):
            score += 50.0
        if compliance.get('readme_present', False):
            score += 50.0
        
        return score
    
    def _calculate_performance_score(self, channel: ChannelConfig) -> float:
        """Calculate performance score."""
        # Base performance scores for different channel types
        performance_scores = {
            ChannelType.LIVE_CHAT: 90.0,
            ChannelType.API: 95.0,
            ChannelType.WEBHOOK: 85.0,
            ChannelType.EMAIL: 70.0,
            ChannelType.SLACK: 80.0,
            ChannelType.DISCORD: 75.0
        }
        
        return performance_scores.get(channel.channel_type, 60.0)
    
    def _get_required_capabilities(self, context: MessageContext) -> List[str]:
        """Get required capabilities based on message context."""
        capabilities = []
        
        # Add capabilities based on content type
        if context.content_type == 'text':
            capabilities.append('text')
        elif context.content_type == 'file':
            capabilities.append('attachments')
        elif context.content_type == 'real_time':
            capabilities.append('real_time')
        
        # Add capabilities based on urgency
        if context.urgency > 0.8:
            capabilities.append('real_time')
        
        # Add capabilities based on WSP references
        if context.wsp_references:
            capabilities.append('structured')
        
        return capabilities
    
    def _generate_selection_reason(self, channel: ChannelConfig, 
                                 context: MessageContext, score: float) -> str:
        """Generate reason for channel selection."""
        reasons = []
        
        if score > 80:
            reasons.append("Excellent match for message requirements")
        elif score > 60:
            reasons.append("Good match for message requirements")
        else:
            reasons.append("Adequate match for message requirements")
        
        # Add specific reasons
        if context.priority == MessagePriority.CRITICAL:
            reasons.append("High priority message requires reliable channel")
        
        if context.confidentiality > 0.8:
            reasons.append("High confidentiality requirements")
        
        if context.wsp_references:
            reasons.append("WSP compliance requirements")
        
        return "; ".join(reasons)
    
    def _calculate_confidence(self, score: float, num_channels: int) -> float:
        """Calculate confidence in the selection."""
        confidence = score / 100.0  # Base confidence from score
        
        # Adjust based on number of available channels
        if num_channels > 5:
            confidence += 0.1  # More options = higher confidence
        elif num_channels < 2:
            confidence -= 0.2  # Few options = lower confidence
        
        return min(max(confidence, 0.0), 1.0) * 100.0
    
    def _calculate_wsp_compliance(self, channel: ChannelConfig, 
                                context: MessageContext) -> float:
        """Calculate WSP compliance score for the selection."""
        base_score = self._calculate_wsp_compliance_score(channel)
        
        # Adjust based on WSP references in context
        if context.wsp_references:
            base_score += 20.0
        
        return min(base_score, 100.0)
    
    def _generate_recommendations(self, channel: ChannelConfig, 
                                context: MessageContext, score: float) -> List[str]:
        """Generate recommendations for the selection."""
        recommendations = []
        
        if score < 60:
            recommendations.append("Consider alternative channels for better performance")
        
        if context.confidentiality > 0.8 and channel.channel_type == ChannelType.LIVE_CHAT:
            recommendations.append("Consider more secure channel for confidential content")
        
        if context.wsp_references and not channel.wsp_compliance.get('modlog_present', False):
            recommendations.append("Ensure WSP compliance documentation is maintained")
        
        if context.urgency > 0.8 and 'real_time' not in channel.capabilities:
            recommendations.append("Consider real-time channel for urgent messages")
        
        return recommendations
    
    def save_configuration(self, output_path: str) -> bool:
        """
        Save channel configuration to file.
        
        Args:
            output_path: Path to save the configuration
            
        Returns:
            True if successful, False otherwise
        """
        try:
            config_data = {}
            for channel_type, config in self.channels.items():
                config_data[channel_type.value] = {
                    'name': config.name,
                    'endpoint': config.endpoint,
                    'capabilities': config.capabilities,
                    'availability': config.availability,
                    'wsp_compliance': config.wsp_compliance,
                    'priority_weight': config.priority_weight
                }
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            print(f"Error saving configuration: {e}")
            return False
    
    def load_configuration(self, file_path: str) -> bool:
        """
        Load channel configuration from file.
        
        Args:
            file_path: Path to the configuration file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            for channel_type_str, data in config_data.items():
                channel_type = ChannelType(channel_type_str)
                config = ChannelConfig(
                    channel_type=channel_type,
                    name=data['name'],
                    endpoint=data['endpoint'],
                    credentials={},
                    capabilities=data['capabilities'],
                    availability=data['availability'],
                    wsp_compliance=data['wsp_compliance'],
                    priority_weight=data['priority_weight']
                )
                self.channels[channel_type] = config
            
            return True
            
        except Exception as e:
            print(f"Error loading configuration: {e}")
            return False


def select_channel(message_context: MessageContext) -> ChannelSelection:
    """
    Convenience function to select a communication channel.
    
    Args:
        message_context: MessageContext object
        
    Returns:
        ChannelSelection with selected channel
    """
    selector = ChannelSelector()
    return selector.select_channel(message_context)


if __name__ == "__main__":
    """Test the channel selector with sample data."""
    # Sample message context
    context = MessageContext(
        sender="0102 Agent",
        recipients=["ComplianceAgent"],
        priority=MessagePriority.HIGH,
        content_type="text",
        urgency=0.8,
        confidentiality=0.6,
        wsp_references=["WSP 22", "WSP 34"],
        metadata={"module": "channel_selector"}
    )
    
    selector = ChannelSelector()
    selection = selector.select_channel(context)
    
    print("Channel Selection Results:")
    print(f"Selected Channel: {selection.selected_channel.name}")
    print(f"Selection Reason: {selection.selection_reason}")
    print(f"Confidence Score: {selection.confidence_score:.1f}%")
    print(f"WSP Compliance Score: {selection.wsp_compliance_score:.1f}%")
    print(f"Recommendations: {selection.recommendations}") 