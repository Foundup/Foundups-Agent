#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Create a temporary large file to test health warnings."""

import tempfile
from pathlib import Path
import sys
import os

# Add parent to path
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

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from module_health.size_audit import SizeAuditor, RiskTier

# Create a temporary large file
with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
    temp_path = Path(f.name)
    # Write 1200 lines (should trigger CRITICAL)
    for i in range(1200):
        f.write(f"# Line {i+1}\n")
    print(f"Created temp file: {temp_path}")

# Test size audit
auditor = SizeAuditor()
result = auditor.audit_file(temp_path)

print(f"\nSize audit result:")
print(f"  Lines: {result.line_count}")
print(f"  Risk tier: {result.risk_tier}")
print(f"  Needs attention: {result.needs_attention}")
print(f"  Guidance: {result.guidance}")

# Test with rules engine
from qwen_advisor.rules_engine import ComplianceRulesEngine

engine = ComplianceRulesEngine()

# Create a mock hit pointing to our large file
mock_hits = [{"location": str(temp_path), "path": str(temp_path)}]
size_checks = engine.check_module_size_health(mock_hits)

print(f"\nRules engine health checks:")
print(f"  Found {len(size_checks)} issues")
for check in size_checks:
    print(f"  - Severity: {check.severity}")
    print(f"    Guidance: {check.guidance}")
    print(f"    Suggested fix: {check.suggested_fix}")

# Clean up
temp_path.unlink()
print(f"\nCleaned up temp file")