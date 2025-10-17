"""
Monitored YouTube Service Wrapper
WSP-Compliant: Wraps YouTube API service to track quota usage

This wrapper intercepts all YouTube API calls to track quota usage
and provide real-time monitoring and alerting.
"""

# === UTF-8 ENFORCEMENT (WSP 90) ===
import sys
import io
if sys.platform.startswith('win'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
# === END UTF-8 ENFORCEMENT ===


import logging
from typing import Any
from modules.platform_integration.youtube_auth.src.quota_monitor import QuotaMonitor

logger = logging.getLogger(__name__)

class MonitoredResource:
    """Wraps a YouTube API resource to track calls."""
    
    def __init__(self, resource, resource_name: str, credential_set: int, quota_monitor: QuotaMonitor):
        self._resource = resource
        self._resource_name = resource_name
        self._credential_set = credential_set
        self._quota_monitor = quota_monitor
    
    def __getattr__(self, name):
        """Intercept method calls to track quota usage."""
        attr = getattr(self._resource, name)
        
        if callable(attr):
            def wrapped(*args, **kwargs):
                # Track the API call
                operation = f"{self._resource_name}.{name}"
                logger.debug(f"📊 Tracking API call: {operation} on set {self._credential_set}")
                
                try:
                    # Make the actual API call
                    result = attr(*args, **kwargs)
                    
                    # Track successful call
                    self._quota_monitor.track_api_call(self._credential_set, operation)
                    
                    # Check if result has execute method (for batch operations)
                    if hasattr(result, 'execute'):
                        original_execute = result.execute
                        
                        def tracked_execute():
                            # Execute and track
                            exec_result = original_execute()
                            # Already tracked above, no need to track again
                            return exec_result
                        
                        result.execute = tracked_execute
                    
                    return result
                    
                except Exception as e:
                    # Log error but still track quota (failed calls still use quota)
                    logger.error(f"API call failed: {operation} - {e}")
                    self._quota_monitor.track_api_call(self._credential_set, operation)
                    raise
            
            return wrapped
        return attr


class MonitoredYouTubeService:
    """
    Wrapper for YouTube API service that tracks all quota usage.
    
    This wrapper intercepts all API calls to monitor quota consumption
    and provide alerting when limits are approached.
    """
    
    def __init__(self, youtube_service, credential_set: int = None):
        """
        Initialize monitored service.
        
        Args:
            youtube_service: Original YouTube API service object
            credential_set: Which credential set this service uses
        """
        self._service = youtube_service
        self._credential_set = credential_set or getattr(youtube_service, '_credential_set', 1)
        self._quota_monitor = QuotaMonitor()
        
        # Make credential_set accessible as a property
        self.credential_set = self._credential_set
        
        logger.info(f"📊 Monitored YouTube service initialized for set {self._credential_set}")
    
    def __getattr__(self, name):
        """Intercept resource access to wrap with monitoring."""
        resource = getattr(self._service, name)
        
        if callable(resource):
            # This is a resource method like channels(), videos(), etc.
            def get_monitored_resource(*args, **kwargs):
                actual_resource = resource(*args, **kwargs)
                return MonitoredResource(
                    actual_resource, 
                    name,
                    self._credential_set,
                    self._quota_monitor
                )
            return get_monitored_resource
        
        return resource
    
    def get_quota_summary(self):
        """Get current quota usage summary."""
        return self._quota_monitor.get_usage_summary()
    
    def get_quota_report(self):
        """Generate detailed quota report."""
        return self._quota_monitor.generate_report()
    
    def get_remaining_operations(self, operation: str):
        """Get estimated remaining operations for this credential set."""
        return self._quota_monitor.estimate_operations_remaining(self._credential_set, operation)


def create_monitored_service(youtube_service, credential_set: int = None):
    """
    Create a monitored YouTube service from an existing service.
    
    Args:
        youtube_service: Original YouTube API service
        credential_set: Optional credential set number
        
    Returns:
        MonitoredYouTubeService that tracks all API usage
    """
    return MonitoredYouTubeService(youtube_service, credential_set)


# Example usage
if __name__ == "__main__":
    from modules.platform_integration.youtube_auth.src.youtube_auth import get_authenticated_service
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Get regular service
    service = get_authenticated_service()
    
    # Wrap with monitoring
    monitored = create_monitored_service(service)
    
    # Use the service normally - all calls are tracked
    try:
        response = monitored.channels().list(part='snippet', mine=True).execute()
        print(f"Channel: {response['items'][0]['snippet']['title']}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Get quota report
    print("\n" + monitored.get_quota_report())
    
    # Check remaining operations
    remaining = monitored.get_remaining_operations('liveChatMessages.list')
    print(f"\nCan perform {remaining} more chat message polls")