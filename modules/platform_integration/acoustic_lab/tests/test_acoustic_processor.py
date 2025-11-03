#!/usr/bin/env python3
"""
Acoustic Lab - Test Suite for Acoustic Processor

Tests the core functionality of audio fingerprinting and triangulation.
"""



import unittest
import numpy as np
from src.acoustic_processor import AcousticProcessor, AudioValidationError, GPSValidationError
from src.audio_library import AudioLibrary


class TestAcousticProcessor(unittest.TestCase):
    """Test cases for acoustic processing functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.processor = AcousticProcessor()
        self.library = AudioLibrary()

    def test_audio_library_initialization(self):
        """Test that audio library initializes with synthetic tones."""
        tones = self.library.get_available_tones()
        self.assertEqual(len(tones), 3)
        self.assertIn('Tone A', tones)
        self.assertIn('Tone B', tones)
        self.assertIn('Tone C', tones)

    def test_fingerprint_matching(self):
        """Test MFCC fingerprint matching against synthetic tones."""
        # Get a known fingerprint
        fingerprint_a = self.library.get_tone_fingerprint('Tone A')

        # Match should return high confidence for same tone
        match, confidence = self.library.match_fingerprint(fingerprint_a)
        self.assertEqual(match, 'Tone A')
        self.assertGreater(confidence, 0.8)

    def test_invalid_metadata(self):
        """Test validation of missing or invalid metadata."""
        # Test missing metadata
        with self.assertRaises(GPSValidationError):
            self.processor._validate_metadata({})

        # Test missing GPS
        with self.assertRaises(GPSValidationError):
            self.processor._validate_metadata({'timestamp': '2025-01-01T00:00:00Z'})

        # Test invalid coordinates
        with self.assertRaises(GPSValidationError):
            self.processor._validate_metadata({
                'gps': {'latitude': 100, 'longitude': 0},
                'timestamp': '2025-01-01T00:00:00Z'
            })

    def test_audio_validation(self):
        """Test audio content validation."""
        # Test silence (should fail)
        silence = np.zeros(1000)
        self.assertFalse(self.library.validate_audio_signature(silence))

        # Test high-frequency content (should pass)
        sample_rate = 22050
        t = np.linspace(0, 0.1, int(0.1 * sample_rate))
        high_freq = np.sin(2 * np.pi * 1500 * t)  # 1.5 kHz tone
        self.assertTrue(self.library.validate_audio_signature(high_freq))

    def test_triangulation_calculation(self):
        """Test basic triangulation functionality."""
        # Test data with known sensor positions
        test_metadata = {
            'gps': {'latitude': 40.7649, 'longitude': -111.8421},
            'timestamp': '2025-10-02T14:30:00Z'
        }

        location, triangulation_data = self.processor._calculate_location(test_metadata)

        # Should return valid coordinates
        self.assertIsInstance(location, tuple)
        self.assertEqual(len(location), 2)
        self.assertIsInstance(triangulation_data, dict)
        self.assertIn('sensors_used', triangulation_data)


class TestAudioLibrary(unittest.TestCase):
    """Test cases for audio library functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.library = AudioLibrary()

    def test_synthetic_tone_generation(self):
        """Test generation of synthetic audio tones."""
        tone_a = self.library._generate_synthetic_tone(1000, 1.0)
        self.assertEqual(len(tone_a), 22050)  # 1 second at 22kHz

        # Check that it contains the expected frequency
        fft = np.fft.fft(tone_a)
        freqs = np.fft.fftfreq(len(tone_a), 1/22050)
        peak_freq_idx = np.argmax(np.abs(fft))
        peak_freq = abs(freqs[peak_freq_idx])
        self.assertAlmostEqual(peak_freq, 1000, delta=10)  # Within 10 Hz

    def test_mfcc_fingerprint_consistency(self):
        """Test that MFCC fingerprints are consistent for same audio."""
        tone = self.library._generate_synthetic_tone(1000, 1.0)

        # Generate fingerprint twice
        fp1 = self.library._compute_mfcc_fingerprint(tone)
        fp2 = self.library._compute_mfcc_fingerprint(tone)

        # Should be identical
        np.testing.assert_array_almost_equal(fp1, fp2)


if __name__ == '__main__':
    unittest.main()
