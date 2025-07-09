"""
Module Development Components - Public API

WSP-compliant module development handling with proper separation of concerns.
Replaces the massive module_development_handler.py with focused components.

WSP Compliance:
- WSP 1: Single responsibility per component  
- WSP 11: Clean interfaces and API design
- WSP 49: Modular cohesion and loose coupling
"""

from .module_development_coordinator import ModuleDevelopmentCoordinator

# Public API - Single entry point following WSP principles
__all__ = [
    'ModuleDevelopmentCoordinator'
]

# WSP Compliance Status
WSP_COMPLIANCE = {
    'WSP_1': 'Single responsibility per component',
    'WSP_11': 'Clean interfaces and API design', 
    'WSP_49': 'Modular cohesion and loose coupling',
    'REFACTORED_FROM': 'module_development_handler.py (978 lines)',
    'BENEFITS': [
        'Reduced complexity through separation of concerns',
        'Improved maintainability and testability',
        'Better adherence to WSP architectural principles',
        'Easier extension and modification'
    ]
}

def get_wsp_compliance_status():
    """Get WSP compliance status for this component refactoring."""
    return WSP_COMPLIANCE 