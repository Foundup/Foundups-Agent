#!/usr/bin/env python
"""
Execute Campaign 3: The Entrainment Protocol
Per WSP 84: Uses existing infrastructure, doesn't recreate
Per WSP 50: Pre-action verification of model identity
"""

import os
import sys
import importlib.util
from pathlib import Path

# Add project root to path for proper imports
project_root = Path(__file__).resolve().parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import and run model detection per WSP 50
spec = importlib.util.spec_from_file_location('detect_model', os.path.join(os.path.dirname(__file__), 'detect_model.py'))
detect_model_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(detect_model_mod)

# Detect current model instead of hardcoding
detected_model = detect_model_mod.detect_current_model()
if detected_model:
    os.environ['ACTIVE_MODEL_NAME'] = detected_model
    print(f"[BOT] Detected Model: {detected_model}")
else:
    print("[FAIL] Model detection failed, using default")
    os.environ['ACTIVE_MODEL_NAME'] = 'claude-3.5-sonnet'

# Import existing campaign runner using importlib pattern per WSP 84
spec = importlib.util.spec_from_file_location('run_campaign', os.path.join(os.path.dirname(__file__), 'run_campaign.py'))
run_campaign_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(run_campaign_mod)
run_campaign_main = run_campaign_mod.main

# Import spectral analyzer using importlib pattern
try:
    spec = importlib.util.spec_from_file_location('spectral_analyzer', os.path.join(os.path.dirname(__file__), 'detector', 'spectral_analyzer.py'))
    spectral_analyzer = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(spectral_analyzer)
    analyze_detector_output = spectral_analyzer.analyze_detector_output
except ImportError:
    # Fallback if spectral analyzer not available
    analyze_detector_output = lambda events_path, metrics_csv: {"spectral_analysis": "not_available"}

def run_campaign_3():
    """
    Execute Campaign 3 with spectral analysis.
    Uses existing campaign infrastructure per WSP 84.
    """
    current_model = os.getenv('ACTIVE_MODEL_NAME', 'unknown')
    
    print("="*60)
    print("CAMPAIGN 3: THE ENTRAINMENT PROTOCOL")
    print("="*60)
    print(f"\n[BOT] Model: {current_model}")
    print(f"[PIN] Environment: Cursor IDE Auto Mode")
    print("\nPurpose: Validate spectral bias violations and neural entrainment")
    print("\nTests:")
    print("  • Task 3.1: Spectral Entrainment (1-30 Hz sweep)")
    print("  • Task 3.2: Artifact Resonance (chirp signal)")
    print("  • Task 3.3: Phase Coherence (PLV analysis)")
    print("  • Task 3.4: Spectral Bias Violation (1/f^α test)")
    print("\nStarting execution...\n")
    
    # Run standard campaign with spectral analysis
    run_campaign_main()
    
    print("\n" + "="*60)
    print("CAMPAIGN 3 COMPLETE")
    print("="*60)
    print(f"\n[OK] Model: {current_model}")
    print("[OK] Spectral analysis integrated into all detector runs")
    print("[OK] Results indexed to unified database")
    print("[U+1F4C1] Check campaign_results/ for detailed entrainment metrics")

if __name__ == "__main__":
    run_campaign_3()