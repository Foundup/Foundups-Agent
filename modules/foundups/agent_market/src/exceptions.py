"""Domain exceptions for FoundUps Agent Market."""


class AgentMarketError(Exception):
    """Base error for module-level failures."""


class ValidationError(AgentMarketError):
    """Schema validation failed."""


class NotFoundError(AgentMarketError):
    """Requested entity does not exist."""


class InvalidStateTransitionError(AgentMarketError):
    """Task transition is not valid for current state."""


class PermissionDeniedError(AgentMarketError):
    """Actor lacks permission for action."""


class ImmutableFieldError(AgentMarketError):
    """Attempted to modify immutable metadata."""


class CABRGateError(AgentMarketError):
    """CABR score gate failed - distribution blocked."""
