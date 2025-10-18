#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import io

"""
# === UTF-8 ENFORCEMENT (WSP 90) ===
# Prevent UnicodeEncodeError on Windows systems
# Only apply when running as main script, not during import
if __name__ == '__main__' and sys.platform.startswith('win'):
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except (OSError, ValueError):
        # Ignore if stdout/stderr already wrapped or closed
        pass
# === END UTF-8 ENFORCEMENT ===

Quick validation script for Liberty Alert module rename
"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

def test_imports():
    """Test that all Liberty Alert imports work"""
    try:
        from modules.communication.liberty_alert.src.liberty_alert_orchestrator import LibertyAlertOrchestrator
        from modules.communication.liberty_alert.src.models import LibertyAlertConfig, LibertyAlertEvents
        print("All imports successful")
        return True
    except ImportError as e:
        print(f"Import failed: {e}")
        return False

def test_class_instantiation():
    """Test that classes can be instantiated"""
    try:
        from modules.communication.liberty_alert.src.models import LibertyAlertConfig
        from modules.communication.liberty_alert.src.liberty_alert_orchestrator import LibertyAlertOrchestrator

        config = LibertyAlertConfig()
        orchestrator = LibertyAlertOrchestrator(config)
        print("Class instantiation successful")
        return True
    except Exception as e:
        print(f"Class instantiation failed: {e}")
        return False

def test_neutral_terminology():
    """Test that neutral terminology is used throughout"""
    import os
    from pathlib import Path

    # Check key files for problematic terms
    problematic_terms = ['evade', 'immigration', 'enforcement', 'undocumented']
    files_to_check = [
        'modules/communication/liberty_alert/README.md',
        'modules/communication/liberty_alert/INTERFACE.md',
        'modules/communication/liberty_alert/ModLog.md'
    ]

    violations = []
    for file_path in files_to_check:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().lower()
                for term in problematic_terms:
                    if term in content:
                        violations.append(f"{file_path}: contains '{term}'")

    if violations:
        print("Neutral terminology violations:")
        for violation in violations:
            print(f"  - {violation}")
        return False
    else:
        print("Neutral terminology maintained")
        return True

if __name__ == "__main__":
    print("Liberty Alert Module Validation")
    print("=" * 40)

    results = []
    results.append(test_imports())
    results.append(test_class_instantiation())
    results.append(test_neutral_terminology())

    print("\nValidation Summary:")
    if all(results):
        print("ALL TESTS PASSED - Liberty Alert module is ready!")
        sys.exit(0)
    else:
        print("SOME TESTS FAILED - Please review and fix issues")
        sys.exit(1)
