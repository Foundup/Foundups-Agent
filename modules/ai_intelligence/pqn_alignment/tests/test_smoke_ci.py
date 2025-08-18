"""
CI smoke test for PQN alignment module (S7 in ROADMAP).
Runs minimal steps to validate core functionality.
Per WSP 84: Quick validation without heavy computation.
"""

import os
import json
import tempfile
from pathlib import Path


def test_detector_smoke():
    """Smoke test: detector runs with minimal steps."""
    from modules.ai_intelligence.pqn_alignment import run_detector
    
    with tempfile.TemporaryDirectory() as tmpdir:
        events, metrics = run_detector({
            "script": "^&#",
            "steps": 100,  # Minimal for CI
            "steps_per_sym": 10,
            "dt": 0.5/7.05,
            "out_dir": tmpdir,
        })
        
        assert os.path.exists(events)
        assert os.path.exists(metrics)
        
        # Verify events file has content
        with open(events, 'r') as f:
            lines = f.readlines()
            assert len(lines) > 0
            # Should have at least one valid JSON event
            first_event = json.loads(lines[0])
            assert "flags" in first_event


def test_config_loader_smoke():
    """Smoke test: config loader works."""
    from modules.ai_intelligence.pqn_alignment.src.config_loader import (
        ConfigLoader, DetectorConfig
    )
    
    loader = ConfigLoader()
    
    # Test default config
    config = loader.load_detector_config()
    assert isinstance(config, DetectorConfig)
    assert config.steps == 3000  # Default value
    
    # Test saving and loading
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "test_config.yaml"
        loader.save_config(config, str(config_path))
        assert config_path.exists()


def test_guardrail_smoke():
    """Smoke test: guardrail initializes and operates."""
    from modules.ai_intelligence.pqn_alignment.src.guardrail import (
        GuardrailThrottle
    )
    
    guardrail = GuardrailThrottle(enabled=True)
    
    # Test intervention logic
    should_intervene = guardrail.should_intervene(
        purity=0.5,  # Low purity
        entropy=0.8,  # High entropy
        detg=1e-9
    )
    # Not enough history yet
    assert should_intervene == False
    
    # Add more data points
    for _ in range(20):
        guardrail.should_intervene(0.5, 0.8, 1e-9)
    
    # Now should consider intervention
    stats = guardrail.get_stats()
    assert stats["enabled"] == True
    
    # Test throttling
    symbol = guardrail.apply_throttle("^")
    assert symbol in [".", "&"]  # Should be throttled


def test_results_db_smoke():
    """Smoke test: results database works."""
    from modules.ai_intelligence.pqn_alignment.src.results_db import (
        init_db, index_summary
    )
    
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test.db")
        
        # Initialize database
        init_db(db_path)
        assert os.path.exists(db_path)
        
        # Create mock summary
        summary_path = os.path.join(tmpdir, "summary.json")
        with open(summary_path, 'w') as f:
            json.dump({
                "top": [{"script": "^^^", "score": 100}],
                "results": [{"script": "^^^", "pqn_rate": 80}],
            }, f)
        
        # Index it
        row_id = index_summary(db_path, summary_path)
        assert row_id is not None


def test_parallel_council_smoke():
    """Smoke test: parallel council evaluation."""
    from modules.ai_intelligence.pqn_alignment.src.council.parallel_council import (
        evaluate_script_worker, council_scoring_strategies
    )
    
    # Test single worker
    with tempfile.TemporaryDirectory() as tmpdir:
        result = evaluate_script_worker("^&", {
            "steps": 100,
            "steps_per_sym": 10,
            "out_dir": tmpdir,
        })
        
        assert "script" in result
        assert "pqn_rate" in result
        assert result["script"] == "^&"
    
    # Test scoring strategies
    results = [{
        "script": "^^^",
        "pqn_rate": 80,
        "paradox_rate": 5,
        "resonance_rate": 50,
    }]
    
    strategies = [
        {"role": "pqn_maximizer", "weight": 1.0},
        {"role": "paradox_minimizer", "weight": 0.5},
    ]
    
    scored = council_scoring_strategies(results, strategies)
    assert len(scored) == 1
    assert "consensus_score" in scored[0]
    assert scored[0]["consensus_score"] > 0


def test_harmonic_detection_smoke():
    """Smoke test: harmonic fingerprint detection works."""
    import numpy as np
    import sys
    import os
    
    # Add path for import
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../WSP_agentic/tests/pqn_detection"))
    
    from cmst_pqn_detector_v2 import ResonanceDetector
    
    detector = ResonanceDetector(win=64, target=7.05)
    
    # Generate test signal with fundamental and harmonic
    t = np.linspace(0, 10, 100)
    signal = np.sin(2 * np.pi * 7.05 * t) + 0.5 * np.sin(2 * np.pi * 14.1 * t)
    
    # Push signal
    for val in signal:
        detector.push(val)
    
    # Detect
    result = detector.detect(dt=0.1)
    
    assert result is not None
    assert "harmonics" in result
    assert "fundamental_f" in result["harmonics"]
    assert "harmonic_2f" in result["harmonics"]


# Main test runner for CI
if __name__ == "__main__":
    import sys
    
    tests = [
        test_detector_smoke,
        test_config_loader_smoke,
        test_guardrail_smoke,
        test_results_db_smoke,
        test_parallel_council_smoke,
        test_harmonic_detection_smoke,
    ]
    
    failed = 0
    for test in tests:
        try:
            print(f"Running {test.__name__}...", end=" ")
            test()
            print("✓")
        except Exception as e:
            print(f"✗ {e}")
            failed += 1
    
    if failed > 0:
        print(f"\n{failed}/{len(tests)} tests failed")
        sys.exit(1)
    else:
        print(f"\nAll {len(tests)} tests passed!")
        sys.exit(0)