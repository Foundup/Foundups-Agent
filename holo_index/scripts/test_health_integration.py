#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test script to verify module health integration."""

import sys
import os
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

from pathlib import Path
from qwen_advisor.rules_engine import ComplianceRulesEngine
from qwen_advisor.advisor import QwenAdvisor, AdvisorContext

# Test the path resolver
engine = ComplianceRulesEngine()

test_locations = [
    "modules.communication.livechat.src.chat_sender.ChatSender.send_message()",
    "modules/communication/livechat/src/chat_sender.py",
    "modules.communication.livechat.src.agentic_chat_engine",
]

print(f"Project root: {engine.project_root}")
print("Testing path resolution:")
for loc in test_locations:
    hit = {"location": loc}
    resolved = engine._resolve_file_path(hit)
    print(f"  {loc[:50]}... -> {resolved}")

    # Debug: try manual resolution
    if resolved is None and "modules.communication" in loc:
        manual_path = Path("modules/communication/livechat/src/chat_sender.py")
        print(f"    Manual check: {manual_path} exists? {manual_path.exists()}")

print("\nTesting health checks on resolved paths:")
# Create mock search hits
search_hits = [
    {"location": "modules.communication.livechat.src.chat_sender.ChatSender.send_message()"},
    {"location": "modules.communication.livechat.src.agentic_chat_engine"},
]

# Run health checks
size_results = engine.check_module_size_health(search_hits)
print(f"Size check results: {len(size_results)} issues found")
for result in size_results:
    print(f"  - {result.guidance}")

structure_results = engine.check_module_structure_health(search_hits)
print(f"Structure check results: {len(structure_results)} issues found")
for result in structure_results:
    print(f"  - {result.guidance}")

# Test full advisor flow
print("\nTesting full advisor integration:")
advisor = QwenAdvisor()
context = AdvisorContext(
    query="check livechat module",
    code_hits=search_hits,
    wsp_hits=[]
)
result = advisor.generate_guidance(context)
try:
    print(f"Advisor guidance: {result.guidance}")
except UnicodeEncodeError:
    print(f"Advisor guidance: {result.guidance.encode('ascii', 'replace').decode('ascii')}")
print(f"Violations in metadata: {len(result.metadata.get('violations', []))}")
for violation in result.metadata.get('violations', []):
    try:
        print(f"  - {violation}")
    except UnicodeEncodeError:
        print(f"  - {str(violation).encode('ascii', 'replace').decode('ascii')}")