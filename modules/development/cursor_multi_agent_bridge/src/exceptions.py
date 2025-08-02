"""
Custom Exceptions for Cursor Multi-Agent Bridge

WSP Compliance:
- WSP 54 (Agent Duties): Error handling and recovery protocols
- WSP 22 (ModLog): Error tracking and documentation
- WSP 11 (Interface): Exception documentation and standards

Custom exceptions for the Cursor Multi-Agent Bridge module.
"""


class CursorWSPBridgeError(Exception):
    """Base exception for Cursor Multi-Agent Bridge errors."""
    
    def __init__(self, message: str, error_code: str = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class AgentActivationError(CursorWSPBridgeError):
    """
    Raised when WSP agents cannot be activated in Cursor workspace.
    
    Error Code: ACT001
    Recovery: Retry activation or check Cursor agent availability
    """
    
    def __init__(self, message: str):
        super().__init__(message, "ACT001")


class CoordinationError(CursorWSPBridgeError):
    """
    Raised when agent coordination fails during development tasks.
    
    Error Code: COORD001
    Recovery: Check agent status and retry coordination
    """
    
    def __init__(self, message: str):
        super().__init__(message, "COORD001")


class ValidationError(CursorWSPBridgeError):
    """
    Raised when WSP compliance validation fails.
    
    Error Code: VAL001
    Recovery: Review module structure and protocol requirements
    """
    
    def __init__(self, message: str):
        super().__init__(message, "VAL001")


class ConfigError(CursorWSPBridgeError):
    """
    Raised when agent configuration is invalid.
    
    Error Code: CONFIG001
    Recovery: Validate configuration parameters
    """
    
    def __init__(self, message: str):
        super().__init__(message, "CONFIG001")


class ProtocolError(CursorWSPBridgeError):
    """
    Raised when WSP protocol operations fail.
    
    Error Code: PROTO001
    Recovery: Check protocol definitions and validation rules
    """
    
    def __init__(self, message: str):
        super().__init__(message, "PROTO001")


class AgentCommunicationError(CursorWSPBridgeError):
    """
    Raised when communication with Cursor agents fails.
    
    Error Code: COMM001
    Recovery: Check Cursor API connectivity and agent availability
    """
    
    def __init__(self, message: str):
        super().__init__(message, "COMM001")


class WorkflowError(CursorWSPBridgeError):
    """
    Raised when autonomous development workflow fails.
    
    Error Code: WORK001
    Recovery: Review workflow configuration and agent coordination
    """
    
    def __init__(self, message: str):
        super().__init__(message, "WORK001")


# Error code mapping for easy reference
ERROR_CODES = {
    "ACT001": "Agent Activation Error",
    "COORD001": "Coordination Error", 
    "VAL001": "Validation Error",
    "CONFIG001": "Configuration Error",
    "PROTO001": "Protocol Error",
    "COMM001": "Communication Error",
    "WORK001": "Workflow Error"
}


def get_error_description(error_code: str) -> str:
    """
    Get description for an error code.
    
    Args:
        error_code: The error code to look up
        
    Returns:
        str: Error description
    """
    return ERROR_CODES.get(error_code, "Unknown Error")


def is_recoverable_error(error: CursorWSPBridgeError) -> bool:
    """
    Check if an error is recoverable.
    
    Args:
        error: The error to check
        
    Returns:
        bool: True if error is recoverable, False otherwise
    """
    # Define recoverable error codes
    recoverable_codes = ["ACT001", "COORD001", "COMM001"]
    return error.error_code in recoverable_codes 