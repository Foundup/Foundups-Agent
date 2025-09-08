#!/usr/bin/env python3
"""
WRE Core Test Package
WSP 5 Compliant Test Suite

Test package for WRE (Windsurf Recursive Engine) containing
all test cases for autonomous module building and orchestration.
"""

# Import test modules
from .test_wre_integration import *

__all__ = [
    'TestWREAutonomousIntegration',
    'TestIntegrationRobustness'
]

__version__ = "0.1.0"
__author__ = "0102 Autonomous Agent"
