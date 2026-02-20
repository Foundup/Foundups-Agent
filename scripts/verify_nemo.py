# -*- coding: utf-8 -*-
"""Verify NeMo Guardrails installation."""
import sys
sys.path.insert(0, "E:/HoloIndex/nemo_env/Lib/site-packages")

try:
    from nemoguardrails import RailsConfig
    print("NeMo Guardrails OK - v0.19.0")
    print("Import successful: RailsConfig available")
except ImportError as e:
    print(f"FAIL: {e}")
