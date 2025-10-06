#!/usr/bin/env python3
"""
Acoustic Lab - Main Acoustic Processor

Combines audio fingerprinting and acoustic triangulation for educational analysis.
Processes uploaded synthetic audio files and returns location/sound analysis results.
"""

import io
import json
import hashlib
from typing import Dict, Any, Tuple
import numpy as np
import librosa
from .audio_library import get_audio_library
from .triangulation_engine import get_triangulation_engine
from .ethereum_logger import get_ethereum_logger


class AudioValidationError(Exception):
    """Raised when uploaded audio doesn't meet analysis requirements."""
    pass


class GPSValidationError(Exception):
    """Raised when GPS metadata is missing or invalid."""
    pass


class AcousticProcessor:
    """
    Main processor for acoustic triangulation and audio signature analysis.

    Educational implementation demonstrating:
    1. MFCC-based audio fingerprinting
    2. Time-of-arrival acoustic triangulation
    3. Synthetic audio analysis for learning
    """

    def __init__(self):
        """Initialize the acoustic processor with required components."""
        self.audio_library = get_audio_library()
        self.triangulation_engine = get_triangulation_engine()
        self.sample_rate = 22050  # Match library sample rate

    def process_audio(self, file_data: bytes, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process uploaded audio file and perform complete acoustic analysis.

        Args:
            file_data: Raw WAV file bytes
            metadata: Dictionary containing GPS coordinates and timestamp

        Returns:
            Analysis results with location, sound type, confidence, and triangulation data

        Raises:
            AudioValidationError: Invalid audio format or missing required features
            GPSValidationError: Missing or invalid GPS metadata
        """
        # Validate metadata
        self._validate_metadata(metadata)

        # Load and validate audio
        audio = self._load_audio(file_data)

        # Analyze audio for required characteristics
        self._validate_audio_content(audio)

        # Extract MFCC fingerprint from peak region
        mfcc_features = self._extract_fingerprint(audio)

        # Match against known audio library
        sound_type, confidence = self.audio_library.match_fingerprint(mfcc_features)

        # Perform triangulation calculation
        location, triangulation_data = self._calculate_location(metadata)

        # Generate Ethereum proof-of-existence hash
        ethereum_hash = self._generate_ethereum_hash({
            'location': location,
            'sound_type': sound_type,
            'confidence': confidence,
            'triangulation_data': triangulation_data
        })

        return {
            'location': location,
            'sound_type': sound_type,
            'confidence': round(confidence, 3),
            'triangulation_data': triangulation_data,
            'ethereum_hash': ethereum_hash
        }

    def _validate_metadata(self, metadata: Dict[str, Any]):
        """Validate required GPS and timestamp metadata."""
        if not metadata:
            raise GPSValidationError("Missing metadata")

        gps = metadata.get('gps', {})
        if not gps or 'latitude' not in gps or 'longitude' not in gps:
            raise GPSValidationError("Missing GPS coordinates (latitude, longitude required)")

        # Validate coordinate ranges
        lat, lon = gps['latitude'], gps['longitude']
        if not (-90 <= lat <= 90):
            raise GPSValidationError(f"Invalid latitude: {lat}")
        if not (-180 <= lon <= 180):
            raise GPSValidationError(f"Invalid longitude: {lon}")

        if 'timestamp' not in metadata:
            raise GPSValidationError("Missing timestamp")

    def _load_audio(self, file_data: bytes) -> np.ndarray:
        """
        Load audio from bytes data using in-memory processing.

        Args:
            file_data: Raw WAV file bytes

        Returns:
            Numpy array of audio samples

        Raises:
            AudioValidationError: If audio cannot be loaded
        """
        try:
            # Load audio using BytesIO for in-memory processing
            audio_buffer = io.BytesIO(file_data)
            audio, sr = librosa.load(audio_buffer, sr=self.sample_rate, mono=True)

            if len(audio) == 0:
                raise AudioValidationError("Empty audio file")

            if sr != self.sample_rate:
                # Resample if necessary (librosa.load should handle this)
                audio = librosa.resample(audio, orig_sr=sr, target_sr=self.sample_rate)

            return audio

        except Exception as e:
            raise AudioValidationError(f"Failed to load audio: {str(e)}")

    def _validate_audio_content(self, audio: np.ndarray):
        """Validate that audio contains required acoustic characteristics."""
        # Check duration (at least 0.5 seconds for analysis)
        duration = len(audio) / self.sample_rate
        if duration < 0.5:
            raise AudioValidationError(f"Audio too short: {duration:.2f}s (minimum 0.5s required)")

        # Validate audio contains detectable peaks
        if not self.audio_library.validate_audio_signature(audio):
            raise AudioValidationError("Audio does not contain required frequency content (>1kHz peaks)")

        # Check for reasonable amplitude (not silence)
        rms = np.sqrt(np.mean(audio**2))
        if rms < 0.01:  # Very quiet
            raise AudioValidationError("Audio amplitude too low (possible silence)")

    def _extract_fingerprint(self, audio: np.ndarray) -> np.ndarray:
        """
        Extract MFCC fingerprint from the most prominent audio peak.

        Args:
            audio: Audio samples

        Returns:
            MFCC feature vector for the peak region
        """
        # Find the peak region (highest energy 0.2-second window)
        window_size = int(0.2 * self.sample_rate)  # 0.2 second window
        hop_size = window_size // 4  # 75% overlap

        max_energy = 0
        best_start = 0

        # Slide window and find highest energy region
        for start in range(0, len(audio) - window_size, hop_size):
            window = audio[start:start + window_size]
            energy = np.sum(window ** 2)

            if energy > max_energy:
                max_energy = energy
                best_start = start

        # Extract MFCC from the best window
        peak_window = audio[best_start:best_start + window_size]

        mfcc = librosa.feature.mfcc(
            y=peak_window,
            sr=self.sample_rate,
            n_mfcc=13,
            n_fft=512,
            hop_length=256,
            window='hann'
        )

        # Return mean across time (fingerprint)
        return np.mean(mfcc, axis=1)

    def _calculate_location(self, metadata: Dict[str, Any]) -> Tuple[Tuple[float, float], Dict[str, Any]]:
        """
        Calculate sound source location using triangulation.

        For educational purposes, simulates multiple sensor detections
        based on the single uploaded file's GPS location and timestamp.

        Args:
            metadata: GPS and timestamp data

        Returns:
            Tuple of (location_coords, triangulation_details)
        """
        # For Phase 1, simulate triangulation using fixed sensor network
        # In a real implementation, this would aggregate data from multiple sensors

        gps = metadata['gps']
        timestamp = metadata['timestamp']

        # Simulate multiple sensor detections with time delays
        # This creates an educational example of triangulation
        sensor_data = [
            {
                'sensor_id': 'sensor_1',
                'timestamp': timestamp,
                'gps': {'lat': gps['latitude'], 'lon': gps['longitude']}
            },
            {
                'sensor_id': 'sensor_2',
                'timestamp': timestamp + 0.012,  # 12ms delay (~13m at 1100 ft/s)
                'gps': {'lat': gps['latitude'], 'lon': gps['longitude'] + 0.001}  # ~100m east
            },
            {
                'sensor_id': 'sensor_3',
                'timestamp': timestamp + 0.025,  # 25ms delay (~27m at 1100 ft/s)
                'gps': {'lat': gps['latitude'] + 0.001, 'lon': gps['longitude']}  # ~100m north
            }
        ]

        # Calculate triangulated location
        location = self.triangulation_engine.calculate_location(sensor_data)

        # Calculate error estimate
        error_estimate = self.triangulation_engine.calculate_error_estimate(
            location,
            [(s['gps']['lat'], s['gps']['lon']) for s in sensor_data],
            [0.0, 13.2, 27.5]  # Distances in meters
        )

        triangulation_data = {
            'sensors_used': len(sensor_data),
            'time_delays': [0.0, 0.012, 0.025],
            'error_estimate': round(error_estimate, 1)
        }

        return location, triangulation_data

    def _generate_ethereum_hash(self, results: Dict[str, Any]) -> str:
        """
        Generate SHA-256 hash of analysis results for educational proof-of-existence.

        Args:
            results: Analysis results dictionary

        Returns:
            SHA-256 hash for Ethereum logging
        """
        # Use the Ethereum logger to generate the hash consistently
        logger = get_ethereum_logger()
        return logger._create_results_hash(results)

    def get_processing_stats(self) -> Dict[str, Any]:
        """Get processing statistics for monitoring."""
        return {
            'audio_library_size': len(self.audio_library.get_available_tones()),
            'sample_rate': self.sample_rate,
            'sound_speed': self.triangulation_engine.SOUND_SPEED,
            'mfcc_coefficients': 13,
            'analysis_window': 0.2  # seconds
        }


# Global processor instance
_acoustic_processor_instance = None

def get_acoustic_processor() -> AcousticProcessor:
    """Get the global acoustic processor instance (singleton pattern)."""
    global _acoustic_processor_instance
    if _acoustic_processor_instance is None:
        _acoustic_processor_instance = AcousticProcessor()
    return _acoustic_processor_instance
