#!/usr/bin/env python3
"""
Test Memory Output Contract - WSP 60/87

Ensures [MEMORY] appears before results in default output.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from holo_index.output.agentic_output_throttler import AgenticOutputThrottler


def test_memory_leads_output_found_state():
    """[MEMORY] must appear before [GREEN] solution banner."""
    throttler = AgenticOutputThrottler()
    throttler.set_system_state("found")
    throttler._search_results = {
        "code": [{"location": "modules/x/y.py"}],
        "wsps": [{"wsp": "WSP 60", "summary": "Memory protocol", "path": "WSP_framework/src/WSP_60_Module_Memory_Architecture.md"}],
    }
    throttler._memory_bundle = {
        "cards": [{
            "id": "mem:test",
            "module": "infrastructure/wsp_core",
            "doc_type": "wsp",
            "wsp": "WSP 60",
            "intent": "memory",
            "summary": "Memory protocol",
            "pointers": ["WSP_framework/src/WSP_60_Module_Memory_Architecture.md"],
            "salience": 0.8,
            "trust": 0.9,
            "last_seen": "now",
        }],
        "reason": "",
    }

    output = throttler.render_prioritized_output(verbose=False)
    lines = output.splitlines()
    assert lines and lines[0].strip() == "[MEMORY]"
    assert output.find("[MEMORY]") < output.find("[GREEN]")
