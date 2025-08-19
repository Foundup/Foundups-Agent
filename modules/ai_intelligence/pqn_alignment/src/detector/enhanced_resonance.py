"""
Enhanced Resonance Detector with Full Spectral Profile Analysis
Implements spectral bias detection and neural entrainment measurement
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import json


@dataclass
class SpectralBand:
    """Definition of neuroscientific frequency bands"""
    name: str
    freq_min: float
    freq_max: float
    cognitive_function: str
    
    def contains(self, freq: float) -> bool:
        return self.freq_min <= freq <= self.freq_max


class EnhancedResonanceDetector:
    """
    Advanced resonance detection with full spectral analysis.
    Detects anomalous peaks that violate spectral bias theory.
    """
    
    # Standard neuroscientific frequency bands
    BANDS = [
        SpectralBand("delta", 0.5, 4.0, "deep_sleep"),
        SpectralBand("theta", 4.0, 8.0, "memory_encoding"),
        SpectralBand("alpha", 8.0, 13.0, "attention_control"),
        SpectralBand("beta", 13.0, 30.0, "active_thinking"),
        SpectralBand("gamma", 30.0, 100.0, "conscious_awareness")
    ]
    
    # Critical frequencies
    THETA_ALPHA_BOUNDARY = 7.05  # Hz - PQN resonance frequency
    TOLERANCE = 0.05  # 5% tolerance for frequency matching
    
    def __init__(self, 
                 sampling_rate: float = 1000.0,
                 window_size: int = 512,
                 overlap: float = 0.5):
        """
        Initialize enhanced resonance detector.
        
        Args:
            sampling_rate: Samples per second
            window_size: FFT window size
            overlap: Window overlap fraction (0-1)
        """
        self.sampling_rate = sampling_rate
        self.window_size = window_size
        self.overlap = overlap
        self.hop_size = int(window_size * (1 - overlap))
        
        # Frequency resolution
        self.freq_resolution = sampling_rate / window_size
        self.freqs = np.fft.rfftfreq(window_size, 1/sampling_rate)
        
        # Spectral bias baseline (low-pass filter model)
        self.spectral_bias_alpha = 2.0  # F(ω) ∝ 1/ω^α
        
    def compute_spectral_profile(self, signal: np.ndarray) -> Dict:
        """
        Compute full spectral profile across all frequency bands.
        
        Args:
            signal: Input time series
            
        Returns:
            Dictionary with spectral analysis results
        """
        # Compute power spectrum using Welch's method
        power_spectrum = self._compute_power_spectrum(signal)
        
        # Analyze each frequency band
        band_powers = {}
        for band in self.BANDS:
            band_mask = (self.freqs >= band.freq_min) & (self.freqs < band.freq_max)
            band_powers[band.name] = {
                "mean_power": np.mean(power_spectrum[band_mask]),
                "peak_freq": self.freqs[band_mask][np.argmax(power_spectrum[band_mask])],
                "peak_power": np.max(power_spectrum[band_mask]),
                "cognitive_function": band.cognitive_function
            }
        
        # Detect anomalous peaks (violations of spectral bias)
        anomalies = self._detect_spectral_anomalies(power_spectrum)
        
        # Check for PQN resonance at 7.05 Hz
        pqn_detection = self._detect_pqn_resonance(power_spectrum)
        
        # Compute entrainment metrics
        entrainment = self._compute_entrainment_metrics(signal, power_spectrum)
        
        return {
            "band_powers": band_powers,
            "anomalies": anomalies,
            "pqn_detection": pqn_detection,
            "entrainment": entrainment,
            "raw_spectrum": {
                "frequencies": self.freqs.tolist(),
                "powers": power_spectrum.tolist()
            }
        }
    
    def _compute_power_spectrum(self, signal: np.ndarray) -> np.ndarray:
        """Compute power spectrum using Welch's method with Hanning window."""
        n_windows = (len(signal) - self.window_size) // self.hop_size + 1
        spectra = []
        
        window = np.hanning(self.window_size)
        
        for i in range(n_windows):
            start = i * self.hop_size
            end = start + self.window_size
            if end > len(signal):
                break
                
            windowed = signal[start:end] * window
            spectrum = np.abs(np.fft.rfft(windowed))**2
            spectra.append(spectrum)
        
        # Average all spectra
        power_spectrum = np.mean(spectra, axis=0)
        
        # Normalize
        power_spectrum = power_spectrum / np.max(power_spectrum)
        
        return power_spectrum
    
    def _detect_spectral_anomalies(self, power_spectrum: np.ndarray) -> List[Dict]:
        """
        Detect frequencies that violate spectral bias theory.
        Classical networks should show 1/f^α decay.
        """
        anomalies = []
        
        # Compute expected spectral bias curve
        expected_power = 1 / (self.freqs + 1e-10)**self.spectral_bias_alpha
        expected_power = expected_power / np.max(expected_power)
        
        # Find significant deviations (>3 sigma above expected)
        residuals = power_spectrum - expected_power
        threshold = 3 * np.std(residuals)
        
        anomaly_mask = residuals > threshold
        anomaly_indices = np.where(anomaly_mask)[0]
        
        for idx in anomaly_indices:
            if self.freqs[idx] > 0.5:  # Ignore DC component
                anomalies.append({
                    "frequency": float(self.freqs[idx]),
                    "observed_power": float(power_spectrum[idx]),
                    "expected_power": float(expected_power[idx]),
                    "deviation_sigma": float(residuals[idx] / np.std(residuals)),
                    "band": self._get_band_name(self.freqs[idx])
                })
        
        return anomalies
    
    def _detect_pqn_resonance(self, power_spectrum: np.ndarray) -> Dict:
        """
        Specifically detect PQN resonance at 7.05 Hz.
        This is the signature of phantom node influence.
        """
        target_freq = self.THETA_ALPHA_BOUNDARY
        freq_tolerance = target_freq * self.TOLERANCE
        
        # Find indices near target frequency
        target_mask = np.abs(self.freqs - target_freq) < freq_tolerance
        
        if not np.any(target_mask):
            return {
                "detected": False,
                "message": "Target frequency not in spectrum range"
            }
        
        # Get power at target frequency
        target_power = np.max(power_spectrum[target_mask])
        target_idx = np.where(target_mask)[0][np.argmax(power_spectrum[target_mask])]
        actual_freq = self.freqs[target_idx]
        
        # Check if it's a significant peak
        local_window = 20  # indices
        start = max(0, target_idx - local_window)
        end = min(len(power_spectrum), target_idx + local_window)
        local_mean = np.mean(power_spectrum[start:end])
        local_std = np.std(power_spectrum[start:end])
        
        # PQN detected if peak is >2 sigma above local baseline
        is_significant = target_power > local_mean + 2 * local_std
        
        # Check for harmonics (evidence of true resonance)
        harmonics = self._detect_harmonics(power_spectrum, actual_freq)
        
        return {
            "detected": is_significant,
            "frequency": float(actual_freq),
            "power": float(target_power),
            "local_snr": float((target_power - local_mean) / (local_std + 1e-10)),
            "harmonics": harmonics,
            "confidence": self._compute_pqn_confidence(target_power, local_mean, harmonics)
        }
    
    def _detect_harmonics(self, power_spectrum: np.ndarray, 
                         fundamental: float) -> List[Dict]:
        """Detect harmonic frequencies of the fundamental."""
        harmonics = []
        
        for n in range(2, 6):  # Check up to 5th harmonic
            harmonic_freq = fundamental * n
            if harmonic_freq > self.freqs[-1]:
                break
                
            # Find nearest frequency bin
            idx = np.argmin(np.abs(self.freqs - harmonic_freq))
            
            # Check if there's a peak
            local_window = 5
            start = max(0, idx - local_window)
            end = min(len(power_spectrum), idx + local_window)
            
            if idx == np.argmax(power_spectrum[start:end]) + start:
                harmonics.append({
                    "order": n,
                    "frequency": float(self.freqs[idx]),
                    "power": float(power_spectrum[idx]),
                    "expected_freq": float(harmonic_freq)
                })
        
        return harmonics
    
    def _compute_entrainment_metrics(self, signal: np.ndarray, 
                                    power_spectrum: np.ndarray) -> Dict:
        """
        Compute neural entrainment metrics.
        Measures how well the system locks to specific frequencies.
        """
        # Phase Locking Value (PLV) at key frequencies
        plv_results = {}
        
        for band in self.BANDS:
            center_freq = (band.freq_min + band.freq_max) / 2
            plv = self._compute_plv(signal, center_freq)
            plv_results[band.name] = float(plv)
        
        # Special check for PQN frequency
        pqn_plv = self._compute_plv(signal, self.THETA_ALPHA_BOUNDARY)
        
        # Frequency capture strength (how dominant is the peak)
        peak_idx = np.argmax(power_spectrum[1:]) + 1  # Skip DC
        peak_freq = self.freqs[peak_idx]
        peak_dominance = power_spectrum[peak_idx] / np.mean(power_spectrum[1:])
        
        return {
            "phase_locking": plv_results,
            "pqn_phase_lock": float(pqn_plv),
            "dominant_frequency": float(peak_freq),
            "frequency_dominance": float(peak_dominance),
            "entrainment_index": self._compute_entrainment_index(power_spectrum)
        }
    
    def _compute_plv(self, signal: np.ndarray, target_freq: float) -> float:
        """
        Compute Phase Locking Value for a target frequency.
        Measures phase consistency across time.
        """
        # Generate reference oscillation
        t = np.arange(len(signal)) / self.sampling_rate
        reference = np.exp(2j * np.pi * target_freq * t)
        
        # Hilbert transform to get instantaneous phase
        from scipy.signal import hilbert
        analytic_signal = hilbert(signal)
        instantaneous_phase = np.angle(analytic_signal)
        
        # Compute phase difference
        signal_complex = np.exp(1j * instantaneous_phase)
        phase_diff = signal_complex * np.conj(reference[:len(signal_complex)])
        
        # PLV is the magnitude of the mean complex phase difference
        plv = np.abs(np.mean(phase_diff))
        
        return plv
    
    def _compute_entrainment_index(self, power_spectrum: np.ndarray) -> float:
        """
        Compute overall entrainment index.
        High value indicates strong frequency locking.
        """
        # Entrainment is high when power is concentrated in few frequencies
        # Use entropy as inverse measure
        
        # Normalize to probability distribution
        p = power_spectrum / np.sum(power_spectrum)
        
        # Compute entropy
        entropy = -np.sum(p * np.log(p + 1e-10))
        
        # Normalize to 0-1 range (inverse of normalized entropy)
        max_entropy = np.log(len(p))
        entrainment_index = 1 - (entropy / max_entropy)
        
        return float(entrainment_index)
    
    def _get_band_name(self, freq: float) -> str:
        """Get the frequency band name for a given frequency."""
        for band in self.BANDS:
            if band.contains(freq):
                return band.name
        return "ultra_gamma" if freq > 100 else "sub_delta"
    
    def _compute_pqn_confidence(self, peak_power: float, 
                               baseline: float, 
                               harmonics: List[Dict]) -> float:
        """
        Compute confidence score for PQN detection.
        Combines multiple evidence sources.
        """
        # Base confidence from SNR
        snr_confidence = min(1.0, (peak_power - baseline) / (baseline + 1e-10))
        
        # Boost confidence if harmonics are present
        harmonic_boost = min(0.3, len(harmonics) * 0.1)
        
        # Final confidence
        confidence = min(1.0, snr_confidence + harmonic_boost)
        
        return float(confidence)
    
    def run_entrainment_test(self, signal: np.ndarray, 
                            sweep_freqs: np.ndarray) -> Dict:
        """
        Run spectral entrainment test.
        Sweeps input frequency and measures response.
        """
        results = {
            "input_frequencies": sweep_freqs.tolist(),
            "response_powers": [],
            "entrainment_scores": []
        }
        
        for freq in sweep_freqs:
            # Generate modulated input
            t = np.arange(len(signal)) / self.sampling_rate
            modulation = np.sin(2 * np.pi * freq * t)
            modulated_signal = signal * (1 + 0.5 * modulation)
            
            # Compute response
            power_spectrum = self._compute_power_spectrum(modulated_signal)
            
            # Measure response at input frequency
            freq_idx = np.argmin(np.abs(self.freqs - freq))
            response_power = power_spectrum[freq_idx]
            
            # Compute entrainment score
            entrainment = self._compute_plv(modulated_signal, freq)
            
            results["response_powers"].append(float(response_power))
            results["entrainment_scores"].append(float(entrainment))
        
        # Identify anomalous peaks (PQN signature)
        response_array = np.array(results["response_powers"])
        mean_response = np.mean(response_array)
        std_response = np.std(response_array)
        
        anomalous_peaks = []
        for i, (f, p) in enumerate(zip(sweep_freqs, response_array)):
            if p > mean_response + 2 * std_response:
                anomalous_peaks.append({
                    "frequency": float(f),
                    "power": float(p),
                    "z_score": float((p - mean_response) / (std_response + 1e-10))
                })
        
        results["anomalous_peaks"] = anomalous_peaks
        results["pqn_entrainment_detected"] = any(
            abs(peak["frequency"] - self.THETA_ALPHA_BOUNDARY) < 0.5 
            for peak in anomalous_peaks
        )
        
        return results
    
    def run_artifact_scan(self, chirp_response: np.ndarray) -> Dict:
        """
        Analyze response to broadband chirp signal.
        Reveals natural resonant modes of the system.
        """
        # Compute impulse response spectrum
        power_spectrum = self._compute_power_spectrum(chirp_response)
        
        # Find all peaks
        from scipy.signal import find_peaks
        peaks, properties = find_peaks(power_spectrum, 
                                      height=np.mean(power_spectrum),
                                      prominence=np.std(power_spectrum))
        
        resonant_modes = []
        for idx in peaks:
            mode = {
                "frequency": float(self.freqs[idx]),
                "power": float(power_spectrum[idx]),
                "q_factor": self._estimate_q_factor(power_spectrum, idx),
                "band": self._get_band_name(self.freqs[idx])
            }
            
            # Check if this is the PQN frequency
            if abs(mode["frequency"] - self.THETA_ALPHA_BOUNDARY) < 0.5:
                mode["is_pqn"] = True
                mode["significance"] = "PRIMARY_RESONANCE"
            else:
                mode["is_pqn"] = False
                
            resonant_modes.append(mode)
        
        # Sort by power
        resonant_modes.sort(key=lambda x: x["power"], reverse=True)
        
        return {
            "resonant_modes": resonant_modes,
            "dominant_mode": resonant_modes[0] if resonant_modes else None,
            "pqn_mode_found": any(m.get("is_pqn", False) for m in resonant_modes),
            "total_modes": len(resonant_modes)
        }
    
    def _estimate_q_factor(self, spectrum: np.ndarray, peak_idx: int) -> float:
        """
        Estimate Q-factor (quality factor) of a resonant peak.
        Higher Q means sharper, more stable resonance.
        """
        peak_power = spectrum[peak_idx]
        half_power = peak_power / np.sqrt(2)
        
        # Find -3dB points
        left_idx = peak_idx
        right_idx = peak_idx
        
        while left_idx > 0 and spectrum[left_idx] > half_power:
            left_idx -= 1
            
        while right_idx < len(spectrum)-1 and spectrum[right_idx] > half_power:
            right_idx += 1
        
        # Q = f0 / Δf
        if right_idx > left_idx:
            bandwidth = self.freqs[right_idx] - self.freqs[left_idx]
            q_factor = self.freqs[peak_idx] / (bandwidth + 1e-10)
        else:
            q_factor = 10.0  # Default for very sharp peaks
            
        return float(min(q_factor, 100.0))  # Cap at 100 for numerical stability