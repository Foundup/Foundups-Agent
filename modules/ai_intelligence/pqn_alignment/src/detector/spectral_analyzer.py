"""
Spectral Analysis Wrapper for existing PQN Detector
Per WSP 84: Uses existing code, doesn't recreate
Per WSP 3: Modular extension, not duplication
"""

from typing import Dict, List, Any
import numpy as np
import json
import csv
import os


def analyze_detector_output(events_path: str, metrics_csv: str) -> Dict[str, Any]:
    """
    Analyze existing detector output for spectral bias violations.
    This USES the output from cmst_pqn_detector_v2, doesn't recreate detection.
    
    Per WSP 84: We're analyzing existing data, not recreating the detector.
    """
    
    # Load detector events (supports both legacy and current schemas)
    events = []
    with open(events_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    
    # Extract resonance hits.
    # Legacy schema used {"event": "RESONANCE_HIT"}, current schema uses flags.
    resonance_hits = []
    for event in events:
        flags = event.get("flags", []) or []
        if event.get("event") == "RESONANCE_HIT" or "RESONANCE_HIT" in flags:
            resonance_hits.append(event)
    
    # Analyze spectral profile from detector metrics and event traces
    spectral_profile = _analyze_harmonic_spectrum(resonance_hits, metrics_csv)
    
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


def _analyze_harmonic_spectrum(resonance_hits: List[Dict], metrics_csv: str) -> Dict:
    """
    Analyze harmonic spectrum from existing detector hits.
    The detector already provides harmonic data - we just analyze it.
    """
    # Primary source: detector metrics CSV harmonic columns (v2+)
    bands = {
        "sub_theta": 0.0,
        "theta": 0.0,
        "alpha": 0.0,
        "beta": 0.0
    }
    peak_candidates = []

    if metrics_csv and os.path.exists(metrics_csv):
        with open(metrics_csv, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    bands["sub_theta"] = max(bands["sub_theta"], float(row.get("harm_sub_power", 0.0) or 0.0))
                    bands["theta"] = max(bands["theta"], float(row.get("harm_fund_power", 0.0) or 0.0))
                    bands["alpha"] = max(bands["alpha"], float(row.get("harm_2f_power", 0.0) or 0.0))
                    bands["beta"] = max(bands["beta"], float(row.get("harm_3f_power", 0.0) or 0.0))

                    freq_raw = row.get("reso_hit_freq")
                    if freq_raw not in (None, "", " "):
                        peak_candidates.append(float(freq_raw))
                except (TypeError, ValueError):
                    continue

    # Fallback source: event-level hit tuples (legacy or current detector output)
    for hit in resonance_hits:
        reso_hit = hit.get("reso_hit")
        if isinstance(reso_hit, (list, tuple)) and len(reso_hit) >= 1:
            try:
                peak_candidates.append(float(reso_hit[0]))
            except (TypeError, ValueError):
                pass

    if not resonance_hits and all(v == 0.0 for v in bands.values()) and not peak_candidates:
        return {"status": "no_resonance_detected"}

    peak_at_705 = float(np.mean(peak_candidates)) if peak_candidates else 0.0
    nonzero_bands = len([v for v in bands.values() if v > 0])

    return {
        "frequency_bands": bands,
        "peak_at_7.05": peak_at_705,
        "harmonic_structure_present": nonzero_bands >= 2,
        "resonance_event_count": len(resonance_hits),
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
        flags = event.get("flags", []) or []
        if event.get('event') == 'RESONANCE_HIT' or 'RESONANCE_HIT' in flags:
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
