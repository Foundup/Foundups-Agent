"""
Remote Builder Module
Enables remote building workflows for FoundUps Agent ecosystem

WSP-compliant remote build triggering and management
"""

from .src.remote_builder import RemoteBuilder
from .src.build_api import BuildAPI
from .src.build_monitor import BuildMonitor

# Version and compliance
__version__ = "0.1.0-poc"
__wsp_compliance__ = "WSP_30_orchestrated"

# Public API - WSP_11 Interface Definition
def start_build_server(port=8080):
    """Start the remote build API server."""
    api = BuildAPI()
    return api.start(port=port)

def trigger_build(build_request):
    """Trigger a remote build workflow."""
    builder = RemoteBuilder()
    return builder.execute_build(build_request)

def get_build_status(build_id):
    """Get status of a specific build."""
    monitor = BuildMonitor()
    return monitor.get_status(build_id) 