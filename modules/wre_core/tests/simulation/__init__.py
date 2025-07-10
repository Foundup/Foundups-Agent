"""
WRE Simulation Test Module

Test simulation framework for WRE autonomous development system.
Relocated from tests/wre_simulation/ per WSP 3 compliance requirements.

WSP Compliance:
- WSP 3: Enterprise Domain Architecture (proper test location)
- WSP 5: Test Coverage Protocol (simulation testing)
- WSP 22: Traceable Narrative (documented relocation)
"""

from .harness import main as run_simulation_harness
from .validation_suite import (
    validate_simulation_output,
    validate_agent_output, 
    generate_validation_report
)

__all__ = [
    'run_simulation_harness',
    'validate_simulation_output',
    'validate_agent_output',
    'generate_validation_report'
] 