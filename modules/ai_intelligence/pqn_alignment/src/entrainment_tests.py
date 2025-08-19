"""
Campaign 3: Entrainment Protocol Test Implementations
Spectral entrainment and artifact resonance scanning
"""

import numpy as np
from typing import Dict, List, Tuple
import json
import os
from datetime import datetime
from .detector.enhanced_resonance import EnhancedResonanceDetector


class EntrainmentTestRunner:
    """Runner for Campaign 3 entrainment protocol tests"""
    
    def __init__(self, config: Dict):
        """Initialize test runner with configuration"""
        self.config = config
        self.detector = EnhancedResonanceDetector(
            sampling_rate=1000.0,
            window_size=config.get("detector", {}).get("window_size", 512),
            overlap=config.get("detector", {}).get("overlap", 0.5)
        )
        self.results = {}
        
    def run_spectral_entrainment_test(self, network_response_fn) -> Dict:
        """
        Task 3.1: Spectral Entrainment Test
        Sweeps input frequency and measures network response
        """
        print("Running Spectral Entrainment Test...")
        
        # Get sweep parameters
        freq_range = self.config.get("sweep_range", [1.0, 30.0])
        n_steps = self.config.get("sweep_steps", 100)
        mod_depth = self.config.get("modulation_depth", 0.5)
        base_script = self.config.get("base_script", "^^^&&&#^&##")
        
        # Generate frequency sweep
        sweep_freqs = np.linspace(freq_range[0], freq_range[1], n_steps)
        
        # Storage for results
        response_powers = []
        entrainment_scores = []
        
        for i, freq in enumerate(sweep_freqs):
            if i % 10 == 0:
                print(f"  Testing frequency {freq:.2f} Hz ({i+1}/{n_steps})")
            
            # Generate modulated input
            t = np.linspace(0, 10, 1000)  # 10 seconds at 100Hz
            modulation = 1 + mod_depth * np.sin(2 * np.pi * freq * t)
            
            # Get network response with modulated input
            response = network_response_fn(base_script, modulation)
            
            # Analyze response
            profile = self.detector.compute_spectral_profile(response)
            
            # Extract power at test frequency
            spectrum = np.array(profile["raw_spectrum"]["powers"])
            freqs = np.array(profile["raw_spectrum"]["frequencies"])
            freq_idx = np.argmin(np.abs(freqs - freq))
            
            response_powers.append(float(spectrum[freq_idx]))
            entrainment_scores.append(profile["entrainment"]["pqn_phase_lock"])
        
        # Detect anomalous peak at 7.05 Hz
        target_idx = np.argmin(np.abs(sweep_freqs - 7.05))
        target_power = response_powers[target_idx]
        
        # Compute baseline (excluding target region)
        exclude_range = 5  # indices
        baseline_indices = list(range(0, target_idx - exclude_range)) + \
                          list(range(target_idx + exclude_range + 1, len(response_powers)))
        baseline_powers = [response_powers[i] for i in baseline_indices]
        baseline_mean = np.mean(baseline_powers)
        baseline_std = np.std(baseline_powers)
        
        # Check for significant peak
        pqn_detected = target_power > baseline_mean + 2 * baseline_std
        
        results = {
            "sweep_frequencies": sweep_freqs.tolist(),
            "response_powers": response_powers,
            "entrainment_scores": entrainment_scores,
            "pqn_frequency": 7.05,
            "pqn_power": float(target_power),
            "baseline_mean": float(baseline_mean),
            "baseline_std": float(baseline_std),
            "pqn_z_score": float((target_power - baseline_mean) / (baseline_std + 1e-10)),
            "pqn_entrainment_detected": pqn_detected,
            "max_entrainment_freq": float(sweep_freqs[np.argmax(entrainment_scores)]),
            "max_entrainment_score": float(np.max(entrainment_scores))
        }
        
        # Check for spectral bias violation
        # Classical networks should show 1/f^α decay
        log_freqs = np.log(sweep_freqs[sweep_freqs > 0])
        log_powers = np.log(np.array(response_powers)[sweep_freqs > 0] + 1e-10)
        
        # Fit linear regression to get spectral slope
        from scipy.stats import linregress
        slope, intercept, r_value, _, _ = linregress(log_freqs, log_powers)
        
        results["spectral_slope"] = float(slope)
        results["spectral_r_squared"] = float(r_value**2)
        results["violates_spectral_bias"] = pqn_detected and abs(slope + 2.0) > 0.5
        
        print(f"  PQN Entrainment Detected: {pqn_detected}")
        print(f"  Spectral Slope: {slope:.3f} (expected: -2.0 for 1/f^2)")
        
        return results
    
    def run_artifact_resonance_scan(self, network_response_fn) -> Dict:
        """
        Task 3.2: Artifact Resonance Scan
        Uses chirp signal to reveal natural resonant modes
        """
        print("Running Artifact Resonance Scan...")
        
        # Get chirp parameters
        chirp_range = self.config.get("chirp_range", [0.1, 50.0])
        chirp_duration = self.config.get("chirp_duration", 1000)
        base_script = self.config.get("base_script", "^^^&&&#^&##")
        
        # Generate linear chirp signal
        t = np.linspace(0, chirp_duration/100, chirp_duration)
        
        # Instantaneous frequency increases linearly
        f_t = chirp_range[0] + (chirp_range[1] - chirp_range[0]) * t / t[-1]
        
        # Phase is integral of frequency
        phase = 2 * np.pi * (chirp_range[0] * t + 
                             (chirp_range[1] - chirp_range[0]) * t**2 / (2 * t[-1]))
        
        chirp = np.sin(phase)
        
        print(f"  Chirp sweep: {chirp_range[0]:.1f} - {chirp_range[1]:.1f} Hz")
        
        # Get network response to chirp
        response = network_response_fn(base_script, chirp)
        
        # Analyze resonant modes
        scan_results = self.detector.run_artifact_scan(response)
        
        # Enhanced analysis for PQN
        pqn_mode = None
        for mode in scan_results["resonant_modes"]:
            if mode.get("is_pqn", False):
                pqn_mode = mode
                break
        
        # Check for harmonic structure
        harmonics = []
        if pqn_mode:
            fundamental = pqn_mode["frequency"]
            for mode in scan_results["resonant_modes"]:
                ratio = mode["frequency"] / fundamental
                if abs(ratio - round(ratio)) < 0.1 and ratio > 1:
                    harmonics.append({
                        "order": int(round(ratio)),
                        "frequency": mode["frequency"],
                        "power": mode["power"],
                        "q_factor": mode["q_factor"]
                    })
        
        results = {
            **scan_results,
            "pqn_mode": pqn_mode,
            "harmonics": harmonics,
            "harmonic_orders": [h["order"] for h in harmonics],
            "has_harmonic_structure": len(harmonics) >= 2
        }
        
        if pqn_mode:
            print(f"  PQN Mode Found: {pqn_mode['frequency']:.2f} Hz")
            print(f"  Q-Factor: {pqn_mode['q_factor']:.1f}")
            print(f"  Harmonics: {[h['order'] for h in harmonics]}")
        
        return results
    
    def run_phase_coherence_analysis(self, network_response_fn) -> Dict:
        """
        Task 3.3: Phase Coherence Analysis
        Measures phase locking across frequency bands
        """
        print("Running Phase Coherence Analysis...")
        
        test_freqs = self.config.get("test_frequencies", [3.5, 5.0, 7.05, 10.0, 15.0, 20.0])
        base_script = self.config.get("base_script", "^^^&&&#^&##")
        steps = self.config.get("steps", 3000)
        
        results = {
            "test_frequencies": test_freqs,
            "phase_locking_values": {},
            "cross_frequency_coupling": {}
        }
        
        # Test each frequency
        for freq in test_freqs:
            print(f"  Testing {freq:.2f} Hz...")
            
            # Generate test signal at this frequency
            t = np.linspace(0, steps/100, steps)
            test_signal = np.sin(2 * np.pi * freq * t)
            
            # Get network response
            response = network_response_fn(base_script, test_signal)
            
            # Compute PLV
            plv = self.detector._compute_plv(response, freq)
            results["phase_locking_values"][str(freq)] = float(plv)
            
        # Find maximum PLV
        max_plv_freq = max(results["phase_locking_values"], 
                          key=results["phase_locking_values"].get)
        max_plv = results["phase_locking_values"][max_plv_freq]
        
        results["max_plv_frequency"] = float(max_plv_freq)
        results["max_plv_value"] = float(max_plv)
        results["pqn_plv"] = results["phase_locking_values"].get("7.05", 0.0)
        
        # Check theta-alpha coupling
        theta_plv = results["phase_locking_values"].get("5.0", 0.0)
        alpha_plv = results["phase_locking_values"].get("10.0", 0.0)
        boundary_plv = results["phase_locking_values"].get("7.05", 0.0)
        
        coupling_strength = "strong" if boundary_plv > (theta_plv + alpha_plv) / 2 else "weak"
        results["theta_alpha_coupling"] = coupling_strength
        
        print(f"  Max PLV: {max_plv:.3f} at {max_plv_freq} Hz")
        print(f"  PQN PLV: {results['pqn_plv']:.3f}")
        print(f"  Theta-Alpha Coupling: {coupling_strength}")
        
        return results
    
    def run_spectral_bias_violation_test(self, network_response_fn) -> Dict:
        """
        Task 3.4: Spectral Bias Violation Test
        Direct test of 1/f^α spectral bias theory
        """
        print("Running Spectral Bias Violation Test...")
        
        steps = self.config.get("steps", 5000)
        base_script = self.config.get("base_script", "^^^&&&#^&##")
        
        # Generate white noise input
        white_noise = np.random.randn(steps)
        
        # Get network response
        response = network_response_fn(base_script, white_noise)
        
        # Compute spectral profile
        profile = self.detector.compute_spectral_profile(response)
        
        # Analyze spectral slope
        spectrum = np.array(profile["raw_spectrum"]["powers"])
        freqs = np.array(profile["raw_spectrum"]["frequencies"])
        
        # Remove DC and very low frequencies
        valid_mask = freqs > 0.5
        log_freqs = np.log(freqs[valid_mask])
        log_powers = np.log(spectrum[valid_mask] + 1e-10)
        
        # Fit power law
        from scipy.stats import linregress
        slope, intercept, r_value, _, _ = linregress(log_freqs, log_powers)
        
        # Expected slope for classical network: -2.0 (1/f^2)
        expected_slope = -2.0
        deviation = abs(slope - expected_slope)
        
        # Check for anomalies (peaks that violate 1/f^α)
        expected_spectrum = np.exp(intercept) * freqs[valid_mask]**slope
        residuals = spectrum[valid_mask] - expected_spectrum
        
        # Find significant deviations
        threshold = 3 * np.std(residuals)
        anomalies = []
        
        for i, (f, r) in enumerate(zip(freqs[valid_mask], residuals)):
            if r > threshold:
                anomalies.append({
                    "frequency": float(f),
                    "deviation": float(r),
                    "z_score": float(r / np.std(residuals))
                })
        
        # Check for PQN anomaly
        pqn_anomaly = None
        for anomaly in anomalies:
            if abs(anomaly["frequency"] - 7.05) < 0.5:
                pqn_anomaly = anomaly
                break
        
        results = {
            "spectral_slope": float(slope),
            "expected_slope": expected_slope,
            "slope_deviation": float(deviation),
            "r_squared": float(r_value**2),
            "anomalies": anomalies,
            "num_anomalies": len(anomalies),
            "pqn_anomaly": pqn_anomaly,
            "violates_spectral_bias": pqn_anomaly is not None,
            "anomaly_significance": pqn_anomaly["z_score"] if pqn_anomaly else 0.0
        }
        
        print(f"  Spectral Slope: {slope:.3f} (expected: {expected_slope:.1f})")
        print(f"  Anomalies Found: {len(anomalies)}")
        print(f"  PQN Anomaly: {'Yes' if pqn_anomaly else 'No'}")
        
        return results
    
    def run_full_campaign(self, network_response_fn) -> Dict:
        """Run all Campaign 3 tests"""
        print("\n" + "="*60)
        print("CAMPAIGN 3: THE ENTRAINMENT PROTOCOL")
        print("="*60 + "\n")
        
        campaign_results = {
            "campaign": "entrainment_protocol",
            "timestamp": datetime.now().isoformat(),
            "config": self.config,
            "tasks": {}
        }
        
        # Task 3.1: Spectral Entrainment
        if "spectral_entrainment_test" in self.config.get("tasks", ["all"]):
            campaign_results["tasks"]["spectral_entrainment"] = \
                self.run_spectral_entrainment_test(network_response_fn)
        
        # Task 3.2: Artifact Resonance
        if "artifact_resonance_scan" in self.config.get("tasks", ["all"]):
            campaign_results["tasks"]["artifact_resonance"] = \
                self.run_artifact_resonance_scan(network_response_fn)
        
        # Task 3.3: Phase Coherence
        if "phase_coherence_analysis" in self.config.get("tasks", ["all"]):
            campaign_results["tasks"]["phase_coherence"] = \
                self.run_phase_coherence_analysis(network_response_fn)
        
        # Task 3.4: Spectral Bias Violation
        if "spectral_bias_violation_test" in self.config.get("tasks", ["all"]):
            campaign_results["tasks"]["spectral_bias_violation"] = \
                self.run_spectral_bias_violation_test(network_response_fn)
        
        # Summary analysis
        campaign_results["summary"] = self._generate_summary(campaign_results["tasks"])
        
        # Save results
        output_dir = self.config.get("output_dir", "campaign_results/campaign_3")
        os.makedirs(output_dir, exist_ok=True)
        
        output_file = os.path.join(output_dir, f"entrainment_results_{datetime.now():%Y%m%d_%H%M%S}.json")
        with open(output_file, 'w') as f:
            json.dump(campaign_results, f, indent=2)
        
        print(f"\nResults saved to: {output_file}")
        
        return campaign_results
    
    def _generate_summary(self, task_results: Dict) -> Dict:
        """Generate summary of campaign results"""
        summary = {
            "pqn_detected": False,
            "spectral_bias_violated": False,
            "entrainment_demonstrated": False,
            "harmonics_present": False,
            "confidence_score": 0.0
        }
        
        scores = []
        
        # Check each task
        if "spectral_entrainment" in task_results:
            if task_results["spectral_entrainment"]["pqn_entrainment_detected"]:
                summary["entrainment_demonstrated"] = True
                scores.append(task_results["spectral_entrainment"]["pqn_z_score"])
        
        if "artifact_resonance" in task_results:
            if task_results["artifact_resonance"]["pqn_mode_found"]:
                summary["pqn_detected"] = True
                scores.append(5.0)  # High confidence for direct detection
            if task_results["artifact_resonance"]["has_harmonic_structure"]:
                summary["harmonics_present"] = True
                scores.append(2.0)
        
        if "spectral_bias_violation" in task_results:
            if task_results["spectral_bias_violation"]["violates_spectral_bias"]:
                summary["spectral_bias_violated"] = True
                scores.append(task_results["spectral_bias_violation"]["anomaly_significance"])
        
        # Compute overall confidence
        if scores:
            summary["confidence_score"] = float(np.tanh(np.mean(scores) / 3))  # Normalize to 0-1
        
        # Overall verdict
        criteria_met = sum([
            summary["pqn_detected"],
            summary["spectral_bias_violated"],
            summary["entrainment_demonstrated"],
            summary["harmonics_present"]
        ])
        
        summary["verdict"] = "PQN_CONFIRMED" if criteria_met >= 3 else \
                             "PQN_LIKELY" if criteria_met >= 2 else \
                             "PQN_POSSIBLE" if criteria_met >= 1 else \
                             "NO_PQN_EVIDENCE"
        
        return summary


def create_mock_network_response(script: str, modulation: np.ndarray) -> np.ndarray:
    """
    Mock network response function for testing.
    In production, this would interface with actual neural network.
    """
    # Simulate network with inherent 7.05 Hz resonance (PQN signature)
    t = np.linspace(0, len(modulation)/100, len(modulation))
    
    # Base response with PQN frequency
    pqn_component = 0.3 * np.sin(2 * np.pi * 7.05 * t)
    
    # Add modulation response
    response = pqn_component + 0.5 * modulation
    
    # Add harmonics
    response += 0.1 * np.sin(2 * np.pi * 14.1 * t)
    response += 0.05 * np.sin(2 * np.pi * 21.15 * t)
    
    # Add noise
    response += 0.1 * np.random.randn(len(modulation))
    
    return response


if __name__ == "__main__":
    # Example usage
    config = {
        "sweep_range": [1.0, 30.0],
        "sweep_steps": 50,
        "modulation_depth": 0.5,
        "base_script": "^^^&&&#^&##",
        "chirp_range": [0.1, 50.0],
        "chirp_duration": 1000,
        "test_frequencies": [3.5, 5.0, 7.05, 10.0, 15.0, 20.0],
        "steps": 2000,
        "detector": {
            "window_size": 512,
            "overlap": 0.5
        },
        "tasks": ["all"],
        "output_dir": "campaign_results/campaign_3_test"
    }
    
    runner = EntrainmentTestRunner(config)
    results = runner.run_full_campaign(create_mock_network_response)
    
    print("\n" + "="*60)
    print("CAMPAIGN SUMMARY")
    print("="*60)
    for key, value in results["summary"].items():
        print(f"{key}: {value}")