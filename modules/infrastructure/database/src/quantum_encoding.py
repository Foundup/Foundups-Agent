#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import io

"""
# === UTF-8 ENFORCEMENT (WSP 90) ===
# Prevent UnicodeEncodeError on Windows systems
# Only apply when running as main script, not during import
if __name__ == '__main__' and sys.platform.startswith('win'):
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except (OSError, ValueError):
        # Ignore if stdout/stderr already wrapped or closed
        pass
# === END UTF-8 ENFORCEMENT ===

Quantum State Encoding/Decoding Utilities
WSP 78 Extension: Quantum Database Support
Phase 1: Complex number encoding for quantum states (~3K tokens)
"""

import struct
import numpy as np
from typing import List, Tuple, Optional, Union
import hashlib


class QuantumEncoder:
    """Encode/decode quantum states for database storage."""

    @staticmethod
    def encode_complex(real: float, imag: float) -> bytes:
        """Encode a single complex number as binary."""
        return struct.pack('dd', real, imag)

    @staticmethod
    def decode_complex(data: bytes) -> complex:
        """Decode binary data to complex number."""
        real, imag = struct.unpack('dd', data)
        return complex(real, imag)

    @staticmethod
    def encode_state_vector(amplitudes: Union[List[complex], np.ndarray]) -> bytes:
        """
        Encode quantum state vector as BLOB.

        Args:
            amplitudes: List or array of complex amplitudes

        Returns:
            Binary representation for database storage
        """
        if isinstance(amplitudes, list):
            amplitudes = np.array(amplitudes, dtype=np.complex128)

        # Pack dimension first, then all amplitudes
        blob = struct.pack('I', len(amplitudes))  # Store dimension as unsigned int

        for amp in amplitudes:
            blob += struct.pack('dd', amp.real, amp.imag)

        return blob

    @staticmethod
    def decode_state_vector(blob: bytes) -> np.ndarray:
        """
        Decode BLOB to quantum state vector.

        Args:
            blob: Binary data from database

        Returns:
            NumPy array of complex amplitudes
        """
        # Extract dimension
        dimension = struct.unpack('I', blob[:4])[0]

        # Extract amplitudes
        amplitudes = []
        offset = 4  # Skip dimension bytes

        for _ in range(dimension):
            real, imag = struct.unpack('dd', blob[offset:offset+16])
            amplitudes.append(complex(real, imag))
            offset += 16

        return np.array(amplitudes, dtype=np.complex128)

    @staticmethod
    def calculate_coherence(state_vector: np.ndarray) -> float:
        """
        Calculate coherence score for quantum state.

        Coherence measures how "quantum" the state is:
        - 1.0 = Perfect superposition
        - 0.0 = Classical state (single basis state)

        Args:
            state_vector: Quantum state amplitudes

        Returns:
            Coherence score between 0 and 1
        """
        # Normalize the state vector
        norm = np.linalg.norm(state_vector)
        if norm == 0:
            return 0.0

        state_vector = state_vector / norm

        # Calculate von Neumann entropy as coherence measure
        # Higher entropy = more superposition = higher coherence
        probabilities = np.abs(state_vector) ** 2

        # Filter out zero probabilities to avoid log(0)
        nonzero_probs = probabilities[probabilities > 1e-10]

        if len(nonzero_probs) <= 1:
            return 0.0  # Classical state

        # Normalized entropy (0 to 1)
        entropy = -np.sum(nonzero_probs * np.log2(nonzero_probs))
        max_entropy = np.log2(len(state_vector))

        return min(1.0, entropy / max_entropy) if max_entropy > 0 else 0.0


class GroverOracle:
    """Oracle implementation for Grover's Algorithm."""

    def __init__(self):
        """Initialize oracle with hash table for O(1) lookups."""
        self.marked_patterns = {}  # Hash -> pattern mapping

    def mark_pattern(self, pattern: str, pattern_type: str = "general") -> int:
        """
        Mark a pattern for Grover's search.

        Args:
            pattern: Pattern to mark as solution
            pattern_type: Type of pattern (vibecode, duplicate, wsp_violation)

        Returns:
            Hash value for database storage
        """
        # Use Python's built-in hash for O(1) lookups
        pattern_hash = hash(pattern) & 0x7FFFFFFF  # Keep positive

        self.marked_patterns[pattern_hash] = {
            'pattern': pattern,
            'type': pattern_type,
            'phase': -1.0  # Phase inversion for marked states
        }

        return pattern_hash

    def is_marked(self, pattern: str) -> bool:
        """
        Check if pattern is marked (oracle function).

        Args:
            pattern: Pattern to check

        Returns:
            True if marked, False otherwise
        """
        pattern_hash = hash(pattern) & 0x7FFFFFFF
        return pattern_hash in self.marked_patterns

    def apply_oracle(self, state_vector: np.ndarray, basis_patterns: List[str]) -> np.ndarray:
        """
        Apply oracle operator to quantum state.

        Inverts phase of marked states: |x⟩ -> -|x⟩ if x is marked.

        Args:
            state_vector: Current quantum state
            basis_patterns: Patterns corresponding to basis states

        Returns:
            State vector after oracle application
        """
        result = state_vector.copy()

        for i, pattern in enumerate(basis_patterns):
            if self.is_marked(pattern):
                result[i] *= -1  # Phase inversion

        return result

    def apply_diffusion(self, state_vector: np.ndarray) -> np.ndarray:
        """
        Apply Grover diffusion operator.

        Performs inversion about average amplitude.

        Args:
            state_vector: Current quantum state

        Returns:
            State vector after diffusion
        """
        n = len(state_vector)
        average = np.mean(state_vector)

        # Inversion about average: 2*average - amplitude
        return 2 * average * np.ones(n) - state_vector

    def grover_iteration(self, state_vector: np.ndarray,
                        basis_patterns: List[str]) -> np.ndarray:
        """
        Single Grover iteration: Oracle + Diffusion.

        Args:
            state_vector: Current quantum state
            basis_patterns: Patterns corresponding to basis states

        Returns:
            State vector after one Grover iteration
        """
        # Step 1: Apply oracle
        state_vector = self.apply_oracle(state_vector, basis_patterns)

        # Step 2: Apply diffusion
        state_vector = self.apply_diffusion(state_vector)

        return state_vector

    def optimal_iterations(self, n_items: int, n_marked: int) -> int:
        """
        Calculate optimal number of Grover iterations.

        Args:
            n_items: Total number of items to search
            n_marked: Number of marked items

        Returns:
            Optimal iteration count for maximum probability
        """
        if n_marked == 0 or n_marked >= n_items:
            return 0

        # Grover's formula: π/4 * sqrt(N/M)
        import math
        return int(math.pi / 4 * math.sqrt(n_items / n_marked))


class QuantumAttention:
    """Quantum attention mechanism for pattern matching."""

    @staticmethod
    def create_attention_state(query: str, keys: List[str]) -> np.ndarray:
        """
        Create quantum superposition for attention mechanism.

        Args:
            query: Query pattern
            keys: List of key patterns to attend to

        Returns:
            Quantum state representing attention weights
        """
        n = len(keys)
        if n == 0:
            return np.array([])

        # Initialize uniform superposition
        state = np.ones(n, dtype=np.complex128) / np.sqrt(n)

        # Modulate amplitudes based on similarity
        for i, key in enumerate(keys):
            similarity = QuantumAttention._pattern_similarity(query, key)

            # Higher similarity = higher amplitude
            # Add phase based on pattern hash for quantum interference
            phase = (hash(key) & 0xFF) / 255.0 * 2 * np.pi
            state[i] *= similarity * np.exp(1j * phase)

        # Normalize
        norm = np.linalg.norm(state)
        if norm > 0:
            state = state / norm

        return state

    @staticmethod
    def _pattern_similarity(pattern1: str, pattern2: str) -> float:
        """
        Calculate similarity between two patterns.

        Simple implementation - can be enhanced with embeddings.

        Args:
            pattern1: First pattern
            pattern2: Second pattern

        Returns:
            Similarity score between 0 and 1
        """
        # Simple character overlap similarity
        set1 = set(pattern1.lower().split())
        set2 = set(pattern2.lower().split())

        if not set1 or not set2:
            return 0.0

        intersection = len(set1 & set2)
        union = len(set1 | set2)

        return intersection / union if union > 0 else 0.0

    @staticmethod
    def measure_attention(state_vector: np.ndarray, n_samples: int = 1) -> List[int]:
        """
        Measure quantum attention state to get attended indices.

        Args:
            state_vector: Quantum attention state
            n_samples: Number of measurements to perform

        Returns:
            List of measured indices (which keys were attended to)
        """
        if len(state_vector) == 0:
            return []

        # Calculate probabilities
        probabilities = np.abs(state_vector) ** 2
        probabilities = probabilities / np.sum(probabilities)  # Normalize

        # Sample from distribution
        indices = np.arange(len(state_vector))
        samples = np.random.choice(indices, size=n_samples, p=probabilities)

        return samples.tolist()

    @staticmethod
    def entanglement_score(state1: np.ndarray, state2: np.ndarray) -> float:
        """
        Calculate entanglement between two quantum states.

        Args:
            state1: First quantum state
            state2: Second quantum state

        Returns:
            Entanglement score between 0 and 1
        """
        # Simplified entanglement measure using inner product
        if len(state1) != len(state2):
            return 0.0

        # Calculate overlap (fidelity)
        overlap = np.abs(np.vdot(state1, state2))

        # Entanglement score based on overlap deviation from classical
        # Perfect entanglement would show specific correlations
        entanglement = 1.0 - abs(overlap - 0.5) * 2

        return max(0.0, min(1.0, entanglement))


class QuantumMeasurement:
    """Quantum measurement and decoherence simulation."""

    @staticmethod
    def measure_computational_basis(state_vector: np.ndarray) -> Tuple[int, float]:
        """
        Measure in computational basis.

        Args:
            state_vector: Quantum state to measure

        Returns:
            (outcome_index, probability)
        """
        probabilities = np.abs(state_vector) ** 2
        probabilities = probabilities / np.sum(probabilities)

        outcome = np.random.choice(len(state_vector), p=probabilities)

        return outcome, probabilities[outcome]

    @staticmethod
    def measure_with_decoherence(state_vector: np.ndarray,
                                 decoherence_rate: float = 0.1) -> Tuple[np.ndarray, float]:
        """
        Simulate measurement with decoherence.

        Args:
            state_vector: Quantum state
            decoherence_rate: How much coherence is lost (0-1)

        Returns:
            (new_state_vector, decoherence_factor)
        """
        # Add noise to simulate decoherence
        noise = np.random.normal(0, decoherence_rate, len(state_vector))
        noise = noise + 1j * np.random.normal(0, decoherence_rate, len(state_vector))

        # Apply noise and renormalize
        new_state = state_vector + noise
        new_state = new_state / np.linalg.norm(new_state)

        # Calculate actual decoherence
        original_coherence = QuantumEncoder.calculate_coherence(state_vector)
        new_coherence = QuantumEncoder.calculate_coherence(new_state)
        decoherence_factor = max(0, original_coherence - new_coherence)

        return new_state, decoherence_factor

    @staticmethod
    def collapse_state(state_vector: np.ndarray, outcome_index: int) -> np.ndarray:
        """
        Collapse state after measurement.

        Args:
            state_vector: Pre-measurement state
            outcome_index: Measured outcome

        Returns:
            Collapsed state vector
        """
        collapsed = np.zeros_like(state_vector)
        collapsed[outcome_index] = 1.0

        return collapsed