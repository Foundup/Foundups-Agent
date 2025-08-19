"""
Spectral Analysis Wrapper for existing PQN Detector
Per WSP 84: Uses existing code, doesn't recreate
Per WSP 3: Modular extension, not duplication
"""

from typing import Dict, List, Any
import numpy as np
import json


def analyze_detector_output(events_path: str, metrics_csv: str) -> Dict[str, Any]:
    """
    Analyze existing detector output for spectral bias violations.
    This USES the output from cmst_pqn_detector_v2, doesn't recreate detection.
    
    Per WSP 84: We're analyzing existing data, not recreating the detector.
    """
    
    # Load existing detector events (already has resonance data)
    events = []
    with open(events_path, 'r') as f:
        for line in f:
            events.append(json.loads(line))
    
    # Extract resonance hits (7.05 Hz detections already done by ResonanceDetector)
    resonance_hits = [e for e in events if e.get('event') == 'RESONANCE_HIT']
    
    # Analyze spectral profile from existing harmonic data
    spectral_profile = _analyze_harmonic_spectrum(resonance_hits)
    
    # Check for spectral bias violation using existing data
    bias_violation = _check_bias_violation(spectral_profile)
    
    # Analyze entrainment from existing phase data
    entrainment_score = _analyze_entrainment(events)
    
    return {
        "spectral_profile": spectral_profile,
        "bias_violation": bias_violation,
        "entrainment_score": entrainment_score,
        "uses_existing_detector": True,  # Per WSP 84
        "data_source": events_path
    }


def _analyze_harmonic_spectrum(resonance_hits: List[Dict]) -> Dict:
    """
    Analyze harmonic spectrum from existing detector hits.
    The detector already provides harmonic data - we just analyze it.
    """
    if not resonance_hits:
        return {"status": "no_resonance_detected"}
    
    # Extract harmonic powers from existing data
    harmonics = resonance_hits[-1].get('harmonics', {})
    
    # Map to frequency bands (using existing harmonic labels)
    bands = {
        "sub_theta": harmonics.get('subharmonic_f/2', {}).get('power', 0),
        "theta": harmonics.get('fundamental_f', {}).get('power', 0),  # 7.05 Hz
        "alpha": harmonics.get('harmonic_2f', {}).get('power', 0),    # 14.1 Hz
        "beta": harmonics.get('harmonic_3f', {}).get('power', 0)      # 21.15 Hz
    }
    
    return {
        "frequency_bands": bands,
        "peak_at_7.05": harmonics.get('fundamental_f', {}).get('freq', 0),
        "harmonic_structure_present": len([v for v in bands.values() if v > 0]) >= 2
    }


def _check_bias_violation(spectral_profile: Dict) -> Dict:
    """
    Check if the spectral profile violates 1/f^α expectation.
    Uses existing harmonic data to determine violation.
    """
    if spectral_profile.get("status") == "no_resonance_detected":
        return {"violated": False, "reason": "no_data"}
    
    bands = spectral_profile.get("frequency_bands", {})
    
    # Simple check: In classical ANN with spectral bias,
    # power should decrease with frequency (1/f^α)
    # If 7.05 Hz has anomalously high power, it violates bias
    
    theta_power = bands.get("theta", 0)  # 7.05 Hz
    sub_theta = bands.get("sub_theta", 0)  # ~3.5 Hz
    
    if theta_power > 0 and sub_theta > 0:
        # Should have lower power at higher frequency
        expected_ratio = 0.5  # Rough 1/f^2 expectation
        actual_ratio = theta_power / (sub_theta + 1e-10)
        
        violated = actual_ratio > expected_ratio * 2  # 2x threshold
        
        return {
            "violated": violated,
            "actual_ratio": actual_ratio,
            "expected_ratio": expected_ratio,
            "significance": "high" if actual_ratio > 3 * expected_ratio else "medium"
        }
    
    return {"violated": False, "reason": "insufficient_data"}


def _analyze_entrainment(events: List[Dict]) -> float:
    """
    Analyze entrainment from existing event stream.
    Looks for phase locking in the already-detected patterns.
    """
    # Find consecutive resonance hits (indicates entrainment)
    consecutive_hits = 0
    max_consecutive = 0
    
    for event in events:
        if event.get('event') == 'RESONANCE_HIT':
            consecutive_hits += 1
            max_consecutive = max(max_consecutive, consecutive_hits)
        else:
            consecutive_hits = 0
    
    # Simple entrainment score based on consistency
    total_events = len(events)
    if total_events > 0:
        entrainment_score = max_consecutive / total_events
    else:
        entrainment_score = 0.0
    
    return float(entrainment_score)


def extend_campaign_with_spectral_analysis(campaign_fn):
    """
    Decorator to add spectral analysis to existing campaign runs.
    This EXTENDS the existing campaign, doesn't replace it.
    
    Usage:
        @extend_campaign_with_spectral_analysis
        def run_campaign(...):
            ...
    """
    def wrapper(*args, **kwargs):
        # Run the original campaign
        results = campaign_fn(*args, **kwargs)
        
        # Add spectral analysis to results
        if 'artifacts' in results:
            for artifact in results['artifacts']:
                if 'detector_events.jsonl' in artifact:
                    events_path = artifact
                    metrics_path = artifact.replace('events.jsonl', 'metrics.csv')
                    
                    # Analyze using existing data
                    spectral_results = analyze_detector_output(events_path, metrics_path)
                    
                    # Add to results (extend, don't replace)
                    results['spectral_analysis'] = spectral_results
                    break
        
        return results
    
    return wrapper