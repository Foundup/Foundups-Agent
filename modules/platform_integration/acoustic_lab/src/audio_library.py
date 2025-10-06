#!/usr/bin/env python3
"""
Acoustic Lab - Synthetic Audio Library

Generates and manages MFCC fingerprints for three synthetic audio tones:
- Tone A: 1000 Hz sine wave
- Tone B: 1500 Hz sine wave
- Tone C: 2000 Hz sine wave

All audio is synthetic and generated programmatically for educational purposes.
"""

import numpy as np
import librosa
from typing import Dict, Tuple, List
import hashlib


class AudioLibrary:
    """
    Manages the synthetic audio fingerprint database for educational acoustic analysis.

    Generates three distinct synthetic tones and computes their MFCC fingerprints
    for pattern matching against uploaded audio samples.
    """

    def __init__(self, sample_rate: int = 22050):
        """
        Initialize the audio library with synthetic tone fingerprints.

        Args:
            sample_rate: Audio sample rate in Hz (default: 22050)
        """
        self.sample_rate = sample_rate
        self.fingerprints: Dict[str, np.ndarray] = {}
        self.tone_frequencies = {
            'Tone A': 1000,  # 1 kHz
            'Tone B': 1500,  # 1.5 kHz
            'Tone C': 2000   # 2 kHz
        }

        # Generate fingerprints for all tones
        self._generate_fingerprints()

    def _generate_synthetic_tone(self, frequency: float, duration: float = 1.0) -> np.ndarray:
        """
        Generate a synthetic sine wave tone.

        Args:
            frequency: Tone frequency in Hz
            duration: Tone duration in seconds

        Returns:
            Numpy array containing the synthetic audio samples
        """
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        # Generate sine wave with slight amplitude modulation for realism
        amplitude = 0.8 * (1 + 0.1 * np.sin(2 * np.pi * 0.5 * t))  # 10% modulation at 0.5 Hz
        tone = amplitude * np.sin(2 * np.pi * frequency * t)

        # Add subtle noise for realism (very low amplitude)
        noise = 0.01 * np.random.normal(0, 1, len(tone))
        return tone + noise

    def _compute_mfcc_fingerprint(self, audio: np.ndarray, window_size: float = 0.2) -> np.ndarray:
        """
        Compute MFCC fingerprint for a short audio window.

        Args:
            audio: Audio samples
            window_size: Analysis window size in seconds

        Returns:
            MFCC feature matrix (averaged across time)
        """
        # Extract a window from the middle of the audio
        window_samples = int(self.sample_rate * window_size)
        start_idx = max(0, len(audio) // 2 - window_samples // 2)
        end_idx = min(len(audio), start_idx + window_samples)
        window = audio[start_idx:end_idx]

        # Compute MFCC features
        mfcc = librosa.feature.mfcc(
            y=window,
            sr=self.sample_rate,
            n_mfcc=13,  # Standard 13 MFCC coefficients
            n_fft=512,
            hop_length=256,
            window='hann'
        )

        # Return mean across time (global fingerprint)
        return np.mean(mfcc, axis=1)

    def _generate_fingerprints(self):
        """Generate MFCC fingerprints for all synthetic tones."""
        print("[AUDIO] Generating synthetic audio fingerprints...")

        for tone_name, frequency in self.tone_frequencies.items():
            # Generate synthetic tone
            tone_audio = self._generate_synthetic_tone(frequency)

            # Compute MFCC fingerprint
            fingerprint = self._compute_mfcc_fingerprint(tone_audio)

            # Store fingerprint
            self.fingerprints[tone_name] = fingerprint

            # Generate a hash for verification
            fingerprint_hash = hashlib.sha256(fingerprint.tobytes()).hexdigest()[:16]
            print(f"  [OK] {tone_name} ({frequency} Hz): {fingerprint_hash}")

        print(f"[LIBRARY] Audio library initialized with {len(self.fingerprints)} synthetic tones")

    def match_fingerprint(self, query_fingerprint: np.ndarray, threshold: float = 0.8) -> Tuple[str, float]:
        """
        Match a query MFCC fingerprint against the known tone library.

        Args:
            query_fingerprint: MFCC features from query audio
            threshold: Minimum confidence threshold for matching

        Returns:
            Tuple of (matched_tone_name, confidence_score)
            Returns ('Unknown', 0.0) if no match meets threshold
        """
        best_match = 'Unknown'
        best_confidence = 0.0

        for tone_name, library_fingerprint in self.fingerprints.items():
            # Compute cosine similarity between fingerprints
            dot_product = np.dot(query_fingerprint, library_fingerprint)
            query_norm = np.linalg.norm(query_fingerprint)
            library_norm = np.linalg.norm(library_fingerprint)

            if query_norm > 0 and library_norm > 0:
                confidence = dot_product / (query_norm * library_norm)
                confidence = max(0.0, min(1.0, confidence))  # Clamp to [0, 1]

                if confidence > best_confidence:
                    best_confidence = confidence
                    best_match = tone_name

        # Only return match if confidence meets threshold
        if best_confidence >= threshold:
            return best_match, best_confidence
        else:
            return 'Unknown', 0.0

    def get_available_tones(self) -> List[str]:
        """Get list of available synthetic tone names."""
        return list(self.fingerprints.keys())

    def get_tone_fingerprint(self, tone_name: str) -> np.ndarray:
        """
        Get the MFCC fingerprint for a specific tone.

        Args:
            tone_name: Name of the tone ('Tone A', 'Tone B', 'Tone C')

        Returns:
            MFCC fingerprint array

        Raises:
            KeyError: If tone_name not found
        """
        return self.fingerprints[tone_name]

    def validate_audio_signature(self, audio: np.ndarray) -> bool:
        """
        Validate that audio contains a detectable peak (>1kHz) suitable for analysis.

        Args:
            audio: Audio samples to validate

        Returns:
            True if audio contains required frequency content
        """
        # Compute FFT to check for high-frequency content
        fft = np.fft.fft(audio)
        freqs = np.fft.fftfreq(len(audio), 1/self.sample_rate)

        # Check for significant energy above 1kHz
        high_freq_mask = np.abs(freqs) > 1000
        high_freq_energy = np.sum(np.abs(fft[high_freq_mask])**2)
        total_energy = np.sum(np.abs(fft)**2)

        if total_energy > 0:
            high_freq_ratio = high_freq_energy / total_energy
            return high_freq_ratio > 0.1  # At least 10% energy in high frequencies
        else:
            return False


# Global library instance for reuse
_audio_library_instance = None

def get_audio_library() -> AudioLibrary:
    """Get the global audio library instance (singleton pattern)."""
    global _audio_library_instance
    if _audio_library_instance is None:
        _audio_library_instance = AudioLibrary()
    return _audio_library_instance
