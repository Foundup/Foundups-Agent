"""
Bridge Protocol - WebSocket Communication Protocol Definitions

WSP Compliance:
- WSP 4 (FMAS): Protocol structure validation
- WSP 54 (Agent Duties): Agent communication protocols
- WSP 46 (WRE Integration): WRE communication standards

Protocol definitions for WRE WebSocket bridge communication.
"""

import logging
from enum import Enum
from typing import Dict, Any, List, Optional

# Configure logging
logger = logging.getLogger(__name__)


class MessageType(Enum):
    """WebSocket message types for WRE communication."""
    
    # Connection management
    HANDSHAKE = "handshake"
    HANDSHAKE_ACK = "handshake_ack"
    DISCONNECT = "disconnect"
    
    # Agent communication
    AGENT_COMMAND = "agent_command"
    AGENT_COMMAND_RESPONSE = "agent_command_response"
    AGENT_STATUS_UPDATE = "agent_status_update"
    
    # CMST Protocol
    CMST_ACTIVATION = "cmst_activation_request"
    CMST_ACTIVATION_RESPONSE = "cmst_activation_response"
    CMST_PROGRESS = "cmst_protocol_progress"
    
    # Workflow management
    WORKFLOW_EXECUTION = "workflow_execution_request"
    WORKFLOW_EXECUTION_RESPONSE = "workflow_execution_response"
    WORKFLOW_PROGRESS = "workflow_progress"
    
    # Event system
    EVENT_SUBSCRIPTION = "event_subscription"
    EVENT_UNSUBSCRIPTION = "event_unsubscription"
    UI_UPDATE = "ui_update"
    
    # Error handling
    ERROR = "error"
    HEARTBEAT = "heartbeat"
    HEALTH_CHECK = "health_check"


class BridgeProtocol:
    """WebSocket bridge protocol handler."""
    
    def __init__(self):
        """Initialize bridge protocol."""
        self.protocol_version = "1.0.0"
        self.supported_versions = ["1.0.0"]
        
        logger.info("Bridge Protocol initialized")
    
    def get_protocol_version(self) -> str:
        """Get current protocol version."""
        return self.protocol_version
    
    def is_compatible_version(self, version: str) -> bool:
        """Check if version is compatible."""
        return version in self.supported_versions
    
    def is_valid_message_type(self, message_type: str) -> bool:
        """Validate message type."""
        try:
            MessageType(message_type)
            return True
        except ValueError:
            return False
    
    def create_handshake_message(self, client_type: str = "vscode_extension") -> Dict[str, Any]:
        """Create handshake message."""
        return {
            "type": MessageType.HANDSHAKE.value,
            "protocol_version": self.protocol_version,
            "client_type": client_type,
            "capabilities": [
                "agent_coordination",
                "cmst_protocol",
                "workflow_execution",
                "real_time_updates"
            ]
        }
    
    def create_agent_command_message(self, agent_name: str, command: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Create agent command message."""
        return {
            "type": MessageType.AGENT_COMMAND.value,
            "agent_name": agent_name,
            "command": command,
            "parameters": parameters,
            "timestamp": "now"
        }
    
    def create_cmst_activation_message(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Create CMST Protocol activation message."""
        return {
            "type": MessageType.CMST_ACTIVATION.value,
            "protocol": parameters.get("protocol", "CMST_v11"),
            "target_state": parameters.get("target_state", "0102"),
            "agent_count": parameters.get("agent_count", 8),
            "parameters": parameters
        }
    
    def create_workflow_execution_message(self, workflow: Dict[str, Any]) -> Dict[str, Any]:
        """Create workflow execution message."""
        return {
            "type": MessageType.WORKFLOW_EXECUTION.value,
            "workflow_id": f"wf-{hash(str(workflow)) % 1000:03d}",
            "workflow_definition": workflow
        }
    
    def create_event_subscription_message(self, event_type: str, callback_id: str) -> Dict[str, Any]:
        """Create event subscription message."""
        return {
            "type": MessageType.EVENT_SUBSCRIPTION.value,
            "event_type": event_type,
            "callback_id": callback_id
        }
    
    def create_error_message(self, error_code: str, error_message: str, request_id: Optional[str] = None) -> Dict[str, Any]:
        """Create error message."""
        return {
            "type": MessageType.ERROR.value,
            "error_code": error_code,
            "error_message": error_message,
            "request_id": request_id
        }
    
    def parse_message(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse incoming message."""
        message_type = message_data.get("type")
        
        if not self.is_valid_message_type(message_type):
            raise ValueError(f"Invalid message type: {message_type}")
        
        return {
            "type": MessageType(message_type),
            "data": message_data
        }
    
    def validate_handshake_response(self, response: Dict[str, Any]) -> bool:
        """Validate handshake response."""
        required_fields = ["type", "bridge_id", "wre_version"]
        return all(field in response for field in required_fields)
    
    def validate_agent_response(self, response: Dict[str, Any]) -> bool:
        """Validate agent command response."""
        required_fields = ["type", "status"]
        return all(field in response for field in required_fields)
    
    def validate_cmst_response(self, response: Dict[str, Any]) -> bool:
        """Validate CMST Protocol response."""
        required_fields = ["type", "protocol_version", "quantum_state"]
        return all(field in response for field in required_fields)
    
    def get_supported_events(self) -> List[str]:
        """Get list of supported event types."""
        return [
            "agent_status_change",
            "activation_progress", 
            "cmst_protocol_progress",
            "workflow_progress",
            "connection_status",
            "error_notification",
            "ui_update",
            "health_status"
        ] 