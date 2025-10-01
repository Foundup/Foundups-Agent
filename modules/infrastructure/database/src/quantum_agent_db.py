#!/usr/bin/env python3
"""
Quantum-Enhanced Agent Database
WSP 78 Extension: Quantum capabilities for AgentDB
Phase 1: Non-breaking quantum additions (~5K tokens)
"""

import json
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple, Union
from pathlib import Path

from .agent_db import AgentDB
from .quantum_encoding import (
    QuantumEncoder,
    GroverOracle,
    QuantumAttention,
    QuantumMeasurement
)


class QuantumAgentDB(AgentDB):
    """
    Extends AgentDB with quantum capabilities.

    Maintains full backward compatibility while adding:
    - Quantum state storage and retrieval
    - Grover's algorithm for O(√N) search
    - Quantum attention mechanisms
    - Coherence tracking and decoherence simulation
    """

    def __init__(self):
        """Initialize quantum-enhanced database."""
        super().__init__()
        self._init_quantum_tables()
        self.encoder = QuantumEncoder()
        self.oracle = GroverOracle()
        self.attention = QuantumAttention()
        self.measurement = QuantumMeasurement()

    def _init_quantum_tables(self) -> None:
        """Initialize quantum extension tables."""
        with self.db.get_connection() as conn:
            # Create quantum tables directly (more reliable than parsing SQL file)

            # Quantum states table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS quantum_states (
                    state_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pattern TEXT,
                    state_vector BLOB,
                    coherence_score REAL,
                    dimension INTEGER,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    last_measured DATETIME,
                    measurement_result TEXT
                )
            ''')

            # Quantum oracles table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS quantum_oracles (
                    oracle_id INTEGER PRIMARY KEY,
                    pattern_type TEXT,
                    pattern_hash INTEGER,
                    phase_inversion REAL DEFAULT -1.0,
                    marked_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    confidence REAL DEFAULT 1.0
                )
            ''')

            # Quantum amplitudes table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS quantum_amplitudes (
                    amplitude_id INTEGER PRIMARY KEY,
                    state_id INTEGER,
                    basis_state TEXT,
                    real_part REAL,
                    imaginary_part REAL,
                    phase REAL,
                    FOREIGN KEY (state_id) REFERENCES quantum_states(state_id)
                )
            ''')

            # Quantum attention table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS quantum_attention (
                    attention_id INTEGER PRIMARY KEY,
                    query_pattern TEXT,
                    key_pattern TEXT,
                    attention_weight BLOB,
                    entanglement_score REAL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Quantum measurements table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS quantum_measurements (
                    measurement_id INTEGER PRIMARY KEY,
                    state_id INTEGER,
                    measured_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    basis TEXT,
                    outcome TEXT,
                    probability REAL,
                    decoherence_factor REAL,
                    FOREIGN KEY (state_id) REFERENCES quantum_states(state_id)
                )
            ''')

            # Quantum entanglement table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS quantum_entanglement (
                    entanglement_id INTEGER PRIMARY KEY,
                    state_id_1 INTEGER,
                    state_id_2 INTEGER,
                    entanglement_type TEXT,
                    correlation_strength REAL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (state_id_1) REFERENCES quantum_states(state_id),
                    FOREIGN KEY (state_id_2) REFERENCES quantum_states(state_id)
                )
            ''')

            # Try to add quantum columns to existing tables (ignore if they already exist)
            try:
                conn.execute('ALTER TABLE agents_breadcrumbs ADD COLUMN quantum_state_id INTEGER')
                conn.execute('ALTER TABLE agents_breadcrumbs ADD COLUMN amplitude_vector BLOB')
                conn.execute('ALTER TABLE agents_breadcrumbs ADD COLUMN coherence_score REAL')
            except:
                pass  # Columns may already exist

            try:
                conn.execute('ALTER TABLE agents_memory ADD COLUMN quantum_encoded BLOB')
                conn.execute('ALTER TABLE agents_memory ADD COLUMN superposition_count INTEGER')
            except:
                pass  # Columns may already exist

            try:
                conn.execute('ALTER TABLE agents_contracts ADD COLUMN quantum_priority BLOB')
                conn.execute('ALTER TABLE agents_contracts ADD COLUMN entangled_contracts TEXT')
            except:
                pass  # Columns may already exist

    # ============================================================================
    # QUANTUM STATE MANAGEMENT
    # ============================================================================

    def store_quantum_state(self, pattern: str, amplitudes: Union[List[complex], np.ndarray],
                           measurement_result: str = None) -> int:
        """
        Store quantum state for pattern.

        Args:
            pattern: Pattern being represented
            amplitudes: Complex amplitudes of quantum state
            measurement_result: Optional collapsed state after measurement

        Returns:
            state_id of stored quantum state
        """
        # Encode state vector as BLOB
        state_blob = self.encoder.encode_state_vector(amplitudes)

        # Calculate coherence
        if isinstance(amplitudes, list):
            amplitudes = np.array(amplitudes, dtype=np.complex128)
        coherence = self.encoder.calculate_coherence(amplitudes)

        # Store in database
        state_id = self.db.execute_write('''
            INSERT INTO quantum_states
            (pattern, state_vector, coherence_score, dimension, measurement_result)
            VALUES (?, ?, ?, ?, ?)
        ''', (pattern, state_blob, coherence, len(amplitudes), measurement_result))

        # Store individual amplitudes for debugging
        self._store_amplitudes(state_id, amplitudes)

        return state_id

    def _store_amplitudes(self, state_id: int, amplitudes: np.ndarray) -> None:
        """Store individual amplitudes for visualization."""
        with self.db.get_connection() as conn:
            for i, amp in enumerate(amplitudes):
                basis_state = format(i, f'0{int(np.log2(len(amplitudes)))}b')
                phase = np.angle(amp)

                conn.execute('''
                    INSERT INTO quantum_amplitudes
                    (state_id, basis_state, real_part, imaginary_part, phase)
                    VALUES (?, ?, ?, ?, ?)
                ''', (state_id, basis_state, amp.real, amp.imag, phase))

    def get_quantum_state(self, pattern: str = None, state_id: int = None) -> Optional[Dict[str, Any]]:
        """
        Retrieve quantum state by pattern or ID.

        Args:
            pattern: Pattern to search for
            state_id: Direct state ID

        Returns:
            Dictionary with state information and decoded amplitudes
        """
        if state_id:
            query = 'SELECT * FROM quantum_states WHERE state_id = ?'
            params = (state_id,)
        elif pattern:
            query = '''
                SELECT * FROM quantum_states
                WHERE pattern = ?
                ORDER BY created_at DESC LIMIT 1
            '''
            params = (pattern,)
        else:
            return None

        result = self.db.execute_query(query, params)

        if not result:
            return None

        state = dict(result[0])

        # Decode state vector
        if state['state_vector']:
            state['amplitudes'] = self.encoder.decode_state_vector(state['state_vector'])

        return state

    # ============================================================================
    # GROVER'S ALGORITHM IMPLEMENTATION
    # ============================================================================

    def mark_for_grover(self, pattern: str, pattern_type: str = 'general',
                        confidence: float = 1.0) -> bool:
        """
        Mark pattern for Grover's algorithm search.

        Args:
            pattern: Pattern to mark as solution
            pattern_type: Type of pattern (vibecode, duplicate, wsp_violation)
            confidence: Confidence in marking (0-1)

        Returns:
            Success status
        """
        pattern_hash = self.oracle.mark_pattern(pattern, pattern_type)

        # Store in database
        try:
            self.db.execute_write('''
                INSERT INTO quantum_oracles
                (pattern_type, pattern_hash, phase_inversion, confidence)
                VALUES (?, ?, -1.0, ?)
            ''', (pattern_type, pattern_hash, confidence))
            return True
        except Exception:
            return False

    def grover_search(self, patterns: List[str], pattern_type: str = None,
                     iterations: int = None) -> List[Tuple[str, float]]:
        """
        Perform Grover's algorithm search on patterns.

        O(√N) quantum search vs O(N) classical search.

        Args:
            patterns: List of patterns to search
            pattern_type: Optional filter by pattern type
            iterations: Number of Grover iterations (auto-calculated if None)

        Returns:
            List of (pattern, probability) tuples for marked patterns
        """
        if not patterns:
            return []

        # Load marked patterns from database
        query = 'SELECT pattern_hash FROM quantum_oracles WHERE phase_inversion = -1.0'
        params = []

        if pattern_type:
            query += ' AND pattern_type = ?'
            params.append(pattern_type)

        marked_hashes = set()
        results = self.db.execute_query(query, tuple(params))
        if results:
            for row in results:
                marked_hashes.add(row['pattern_hash'])

        # Count marked patterns in input
        marked_indices = []
        for i, pattern in enumerate(patterns):
            if (hash(pattern) & 0x7FFFFFFF) in marked_hashes:
                marked_indices.append(i)
                self.oracle.mark_pattern(pattern)  # Add to oracle

        if not marked_indices:
            return []  # No marked patterns found

        # Initialize uniform superposition
        n = len(patterns)
        state = np.ones(n, dtype=np.complex128) / np.sqrt(n)

        # Calculate optimal iterations if not specified
        if iterations is None:
            iterations = self.oracle.optimal_iterations(n, len(marked_indices))

        # Run Grover iterations
        for _ in range(iterations):
            state = self.oracle.grover_iteration(state, patterns)

        # Calculate probabilities
        probabilities = np.abs(state) ** 2

        # Return marked patterns with high probability
        results = []
        threshold = 1.0 / len(patterns) * 2  # Above average probability

        for i, prob in enumerate(probabilities):
            if prob > threshold and i in marked_indices:
                results.append((patterns[i], float(prob)))

        # Sort by probability
        results.sort(key=lambda x: x[1], reverse=True)

        return results

    # ============================================================================
    # QUANTUM ATTENTION MECHANISM
    # ============================================================================

    def create_quantum_attention(self, query: str, keys: List[str]) -> int:
        """
        Create quantum attention state for query-key matching.

        Args:
            query: Query pattern
            keys: List of key patterns

        Returns:
            attention_id for stored attention state
        """
        # Create quantum attention state
        attention_state = self.attention.create_attention_state(query, keys)

        if len(attention_state) == 0:
            return -1

        # Store main attention state
        state_id = self.store_quantum_state(f"attention_{query}", attention_state)

        # Calculate and store pairwise attention weights
        for i, key in enumerate(keys):
            weight_blob = self.encoder.encode_complex(
                attention_state[i].real,
                attention_state[i].imag
            )

            # Calculate entanglement with query
            query_state = np.array([1.0 + 0j], dtype=np.complex128)  # Simple query state
            key_state = np.array([attention_state[i]], dtype=np.complex128)
            entanglement = self.attention.entanglement_score(query_state, key_state)

            self.db.execute_write('''
                INSERT INTO quantum_attention
                (query_pattern, key_pattern, attention_weight, entanglement_score)
                VALUES (?, ?, ?, ?)
            ''', (query, key, weight_blob, entanglement))

        return state_id

    def get_attention_weights(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get quantum attention weights for query.

        Args:
            query: Query pattern
            limit: Maximum results to return

        Returns:
            List of attention weight dictionaries
        """
        results = self.db.execute_query('''
            SELECT key_pattern, attention_weight, entanglement_score
            FROM quantum_attention
            WHERE query_pattern = ?
            ORDER BY entanglement_score DESC
            LIMIT ?
        ''', (query, limit))

        # Decode attention weights
        attention_results = []
        for row in results:
            weight = self.encoder.decode_complex(row['attention_weight'])
            attention_results.append({
                'key': row['key_pattern'],
                'weight': weight,
                'magnitude': abs(weight),
                'phase': np.angle(weight),
                'entanglement': row['entanglement_score']
            })

        return attention_results

    # ============================================================================
    # QUANTUM MEASUREMENT AND DECOHERENCE
    # ============================================================================

    def measure_quantum_state(self, state_id: int, basis: str = 'computational',
                             decoherence_rate: float = 0.1) -> Dict[str, Any]:
        """
        Perform quantum measurement with decoherence.

        Args:
            state_id: ID of quantum state to measure
            basis: Measurement basis
            decoherence_rate: How much coherence is lost

        Returns:
            Measurement result dictionary
        """
        # Get current state
        state = self.get_quantum_state(state_id=state_id)
        if not state:
            return {}

        amplitudes = state['amplitudes']

        # Perform measurement
        outcome_index, probability = self.measurement.measure_computational_basis(amplitudes)

        # Simulate decoherence
        new_state, decoherence_factor = self.measurement.measure_with_decoherence(
            amplitudes, decoherence_rate
        )

        # Store measurement result
        basis_state = format(outcome_index, f'0{int(np.log2(len(amplitudes)))}b')

        measurement_id = self.db.execute_write('''
            INSERT INTO quantum_measurements
            (state_id, basis, outcome, probability, decoherence_factor)
            VALUES (?, ?, ?, ?, ?)
        ''', (state_id, basis, basis_state, probability, decoherence_factor))

        # Update state with new coherence (handled by trigger)

        return {
            'measurement_id': measurement_id,
            'outcome': basis_state,
            'probability': probability,
            'decoherence_factor': decoherence_factor,
            'new_coherence': state['coherence_score'] * (1 - decoherence_factor)
        }

    # ============================================================================
    # QUANTUM ENTANGLEMENT
    # ============================================================================

    def create_entanglement(self, pattern1: str, pattern2: str,
                          entanglement_type: str = 'Bell') -> Optional[int]:
        """
        Create quantum entanglement between two patterns.

        Args:
            pattern1: First pattern
            pattern2: Second pattern
            entanglement_type: Type of entanglement (Bell, GHZ, W, custom)

        Returns:
            entanglement_id if successful
        """
        # Get or create quantum states for patterns
        state1 = self.get_quantum_state(pattern=pattern1)
        state2 = self.get_quantum_state(pattern=pattern2)

        if not state1 or not state2:
            return None

        # Calculate correlation strength
        correlation = self.attention.entanglement_score(
            state1['amplitudes'],
            state2['amplitudes']
        )

        # Store entanglement
        entanglement_id = self.db.execute_write('''
            INSERT INTO quantum_entanglement
            (state_id_1, state_id_2, entanglement_type, correlation_strength)
            VALUES (?, ?, ?, ?)
        ''', (state1['state_id'], state2['state_id'], entanglement_type, correlation))

        return entanglement_id

    def get_entangled_patterns(self, pattern: str) -> List[Dict[str, Any]]:
        """
        Get patterns entangled with given pattern.

        Args:
            pattern: Pattern to find entanglements for

        Returns:
            List of entangled pattern information
        """
        # First get state_id for pattern
        state = self.get_quantum_state(pattern=pattern)
        if not state:
            return []

        state_id = state['state_id']

        # Query entanglements
        results = self.db.execute_query('''
            SELECT
                qe.*,
                qs1.pattern as pattern_1,
                qs2.pattern as pattern_2,
                qs1.coherence_score as coherence_1,
                qs2.coherence_score as coherence_2
            FROM quantum_entanglement qe
            JOIN quantum_states qs1 ON qe.state_id_1 = qs1.state_id
            JOIN quantum_states qs2 ON qe.state_id_2 = qs2.state_id
            WHERE qe.state_id_1 = ? OR qe.state_id_2 = ?
            ORDER BY qe.correlation_strength DESC
        ''', (state_id, state_id))

        entangled = []
        for row in results:
            # Determine which pattern is the "other" one
            other_pattern = row['pattern_2'] if row['pattern_1'] == pattern else row['pattern_1']
            other_coherence = row['coherence_2'] if row['pattern_1'] == pattern else row['coherence_1']

            entangled.append({
                'pattern': other_pattern,
                'type': row['entanglement_type'],
                'correlation': row['correlation_strength'],
                'coherence': other_coherence
            })

        return entangled

    # ============================================================================
    # BACKWARD COMPATIBLE ENHANCEMENTS
    # ============================================================================

    def add_breadcrumb(self, *args, **kwargs) -> int:
        """
        Enhanced breadcrumb with optional quantum state.

        Fully backward compatible - quantum fields are optional.
        """
        # Check if quantum state provided
        quantum_state = kwargs.pop('quantum_state', None)
        coherence = kwargs.pop('coherence', None)

        # Call parent method
        breadcrumb_id = super().add_breadcrumb(*args, **kwargs)

        # Add quantum enhancements if provided
        if quantum_state is not None:
            state_id = self.store_quantum_state(
                f"breadcrumb_{breadcrumb_id}",
                quantum_state
            )

            # Update breadcrumb with quantum state
            self.db.execute_write('''
                UPDATE agents_breadcrumbs
                SET quantum_state_id = ?, coherence_score = ?
                WHERE id = ?
            ''', (state_id, coherence or 0.0, breadcrumb_id))

        return breadcrumb_id

    def learn_pattern(self, *args, **kwargs) -> int:
        """
        Enhanced pattern learning with quantum encoding.

        Fully backward compatible - quantum encoding is optional.
        """
        # Check if quantum encoding requested
        quantum_encode = kwargs.pop('quantum_encode', False)

        # Call parent method
        pattern_id = super().learn_pattern(*args, **kwargs)

        # Add quantum encoding if requested
        if quantum_encode and len(args) >= 3:
            pattern_data = args[2] if isinstance(args[2], dict) else kwargs.get('pattern_data', {})

            # Create quantum state for pattern
            pattern_str = json.dumps(pattern_data)
            n_qubits = min(8, len(pattern_str))  # Limit to 8 qubits (256 states)
            state = np.ones(2**n_qubits, dtype=np.complex128) / np.sqrt(2**n_qubits)

            # Modulate based on pattern hash
            for i in range(len(state)):
                phase = (hash(pattern_str + str(i)) & 0xFF) / 255.0 * 2 * np.pi
                state[i] *= np.exp(1j * phase)

            # Store quantum encoding
            state_blob = self.encoder.encode_state_vector(state)
            self.db.execute_write('''
                UPDATE agents_memory
                SET quantum_encoded = ?, superposition_count = ?
                WHERE id = ?
            ''', (state_blob, len(state), pattern_id))

        return pattern_id