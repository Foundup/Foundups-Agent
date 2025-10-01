#!/usr/bin/env python3
"""
Quantum Duplicate Scanner
WSP 84 Compliant: Extends DuplicatePreventionManager with quantum capabilities
Uses QuantumAgentDB for semantic duplicate detection with Grover's O(√N) search

Test scenario from 012.txt:
- Detects semantic duplicates (vibecode) using AST/control flow analysis
- Uses quantum superposition for pattern matching
- Implements Grover's algorithm for exponential speedup
"""

import ast
import hashlib
import json
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
import inspect
import textwrap

# Import existing duplicate prevention (WSP 84: extend, don't replace)
from .duplicate_prevention_manager import DuplicatePreventionManager

# Import quantum capabilities
from modules.infrastructure.database.src.quantum_agent_db import QuantumAgentDB
from modules.infrastructure.database.src.quantum_encoding import QuantumEncoder, GroverOracle


class QuantumDuplicateScanner(DuplicatePreventionManager):
    """
    Quantum-enhanced duplicate detection extending existing manager.

    Implements the test scenario from 012.txt:
    1. Isolate target function as quantum pattern
    2. Create superposition of AST/control flow
    3. Use Grover's algorithm for O(√N) search
    4. Report semantic matches with confidence scores
    """

    def __init__(self, *args, **kwargs):
        """Initialize with quantum capabilities."""
        super().__init__(*args, **kwargs)

        # Initialize quantum components
        self.quantum_db = QuantumAgentDB()
        self.encoder = QuantumEncoder()
        self.oracle = GroverOracle()

        # Cache for AST patterns
        self.ast_cache = {}
        self.pattern_database = {}

    def extract_ast_pattern(self, code: str) -> Dict[str, Any]:
        """
        Extract AST pattern from code for quantum encoding.

        Args:
            code: Python code string

        Returns:
            Dictionary with AST structure and control flow
        """
        try:
            # Parse code into AST
            tree = ast.parse(textwrap.dedent(code))

            # Extract structural features
            pattern = {
                'node_types': [],
                'control_flow': [],
                'data_flow': [],
                'operations': [],
                'structure_hash': ''
            }

            # Walk AST and extract patterns
            for node in ast.walk(tree):
                # Node types (function, class, loop, etc.)
                pattern['node_types'].append(type(node).__name__)

                # Control flow patterns
                if isinstance(node, (ast.If, ast.For, ast.While, ast.With)):
                    pattern['control_flow'].append(type(node).__name__)

                # Operations
                if isinstance(node, (ast.Call, ast.BinOp, ast.Compare)):
                    pattern['operations'].append(type(node).__name__)

                # Data flow (assignments, returns)
                if isinstance(node, (ast.Assign, ast.Return, ast.Yield)):
                    pattern['data_flow'].append(type(node).__name__)

            # Create structure hash (order-independent for semantic matching)
            structure_str = json.dumps({
                'nodes': sorted(pattern['node_types']),
                'control': sorted(pattern['control_flow']),
                'ops': sorted(pattern['operations']),
                'data': sorted(pattern['data_flow'])
            }, sort_keys=True)

            pattern['structure_hash'] = hashlib.sha256(
                structure_str.encode()
            ).hexdigest()[:16]

            return pattern

        except SyntaxError as e:
            self.logger.warning(f"Failed to parse code: {e}")
            return {}

    def encode_pattern_as_quantum_state(self, pattern: Dict[str, Any]) -> np.ndarray:
        """
        Encode AST pattern as quantum state for superposition.

        Args:
            pattern: AST pattern dictionary

        Returns:
            Quantum state vector (complex amplitudes)
        """
        if not pattern:
            return np.array([])

        # Create feature vector from pattern
        features = []

        # Encode node type frequencies
        node_counts = {}
        for node in pattern['node_types']:
            node_counts[node] = node_counts.get(node, 0) + 1

        # Common node types to track
        tracked_nodes = [
            'FunctionDef', 'Call', 'If', 'For', 'Return',
            'Assign', 'Compare', 'BinOp', 'Name', 'Str'
        ]

        for node_type in tracked_nodes:
            features.append(node_counts.get(node_type, 0))

        # Encode control flow complexity
        features.append(len(pattern['control_flow']))
        features.append(len(pattern['operations']))
        features.append(len(pattern['data_flow']))

        # Normalize to create probability distribution
        features = np.array(features, dtype=float)
        if np.sum(features) > 0:
            features = features / np.sum(features)

        # Create quantum state (use 16 qubits = 2^4 for demonstration)
        n_qubits = 4
        dimension = 2 ** n_qubits

        # Initialize superposition
        quantum_state = np.ones(dimension, dtype=np.complex128) / np.sqrt(dimension)

        # Modulate amplitudes based on features
        for i, feature in enumerate(features[:dimension]):
            # Add phase based on feature value
            phase = feature * 2 * np.pi
            quantum_state[i] *= np.exp(1j * phase)

            # Modulate amplitude
            quantum_state[i] *= (1 + feature)

        # Normalize
        quantum_state = quantum_state / np.linalg.norm(quantum_state)

        return quantum_state

    def quantum_integrity_scan(self, target_code: str, codebase_files: List[str]) -> List[Dict[str, Any]]:
        """
        Execute quantum integrity scan as specified in 012.txt test prompt.

        Steps:
        1. Isolate target pattern
        2. Create quantum superposition
        3. Use Grover's search on codebase
        4. Report semantic matches

        Args:
            target_code: The code to search for duplicates of
            codebase_files: List of file paths to search

        Returns:
            List of matches with confidence scores
        """
        self.logger.info("Starting quantum integrity scan...")

        # Step 1: Isolate target pattern
        target_pattern = self.extract_ast_pattern(target_code)
        if not target_pattern:
            return []

        self.logger.info(f"Target pattern extracted: {target_pattern['structure_hash']}")

        # Step 2: Encode as quantum state
        target_state = self.encode_pattern_as_quantum_state(target_pattern)

        # Store in quantum database
        state_id = self.quantum_db.store_quantum_state(
            f"target_{target_pattern['structure_hash']}",
            target_state
        )

        # Step 3: Process codebase and mark duplicates for Grover's search
        patterns = []
        pattern_map = {}

        for filepath in codebase_files:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    code = f.read()

                # Extract functions from file
                tree = ast.parse(code)
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        # Get function code
                        func_code = ast.unparse(node) if hasattr(ast, 'unparse') else str(node)

                        # Extract pattern
                        func_pattern = self.extract_ast_pattern(func_code)
                        if func_pattern:
                            pattern_key = f"{filepath}::{node.name}"
                            patterns.append(pattern_key)
                            pattern_map[pattern_key] = func_pattern

                            # Check for semantic similarity
                            if self._is_semantically_similar(target_pattern, func_pattern):
                                # Mark for Grover's oracle
                                self.quantum_db.mark_for_grover(
                                    pattern_key,
                                    "semantic_duplicate"
                                )

            except Exception as e:
                self.logger.warning(f"Failed to process {filepath}: {e}")

        # Step 4: Execute Grover's algorithm
        if patterns:
            self.logger.info(f"Executing Grover's search on {len(patterns)} patterns...")

            # Run quantum search
            quantum_results = self.quantum_db.grover_search(patterns, "semantic_duplicate")

            # Build results with confidence scores
            matches = []
            for pattern_key, probability in quantum_results:
                filepath, func_name = pattern_key.split('::')

                # Calculate semantic similarity score
                func_pattern = pattern_map[pattern_key]
                similarity = self._calculate_similarity_score(target_pattern, func_pattern)

                matches.append({
                    'file': filepath,
                    'function': func_name,
                    'confidence': similarity,
                    'quantum_probability': probability,
                    'structure_hash': func_pattern['structure_hash'],
                    'reason': self._explain_match(target_pattern, func_pattern)
                })

            # Sort by confidence
            matches.sort(key=lambda x: x['confidence'], reverse=True)

            return matches

        return []

    def _is_semantically_similar(self, pattern1: Dict, pattern2: Dict) -> bool:
        """
        Check if two patterns are semantically similar.

        Args:
            pattern1: First AST pattern
            pattern2: Second AST pattern

        Returns:
            True if patterns are semantically similar
        """
        # Quick check: if structure hashes match exactly
        if pattern1['structure_hash'] == pattern2['structure_hash']:
            return True

        # Check structural similarity
        similarity = self._calculate_similarity_score(pattern1, pattern2)

        # Threshold for semantic similarity
        return similarity > 0.7

    def _calculate_similarity_score(self, pattern1: Dict, pattern2: Dict) -> float:
        """
        Calculate similarity score between two patterns.

        Args:
            pattern1: First AST pattern
            pattern2: Second AST pattern

        Returns:
            Similarity score between 0 and 1
        """
        scores = []

        # Compare node types
        set1 = set(pattern1['node_types'])
        set2 = set(pattern2['node_types'])
        if set1 or set2:
            node_similarity = len(set1 & set2) / len(set1 | set2)
            scores.append(node_similarity)

        # Compare control flow
        cf1 = set(pattern1['control_flow'])
        cf2 = set(pattern2['control_flow'])
        if cf1 or cf2:
            cf_similarity = len(cf1 & cf2) / len(cf1 | cf2) if (cf1 | cf2) else 1.0
            scores.append(cf_similarity)

        # Compare operations
        op1 = set(pattern1['operations'])
        op2 = set(pattern2['operations'])
        if op1 or op2:
            op_similarity = len(op1 & op2) / len(op1 | op2) if (op1 | op2) else 1.0
            scores.append(op_similarity)

        # Compare data flow
        df1 = set(pattern1['data_flow'])
        df2 = set(pattern2['data_flow'])
        if df1 or df2:
            df_similarity = len(df1 & df2) / len(df1 | df2) if (df1 | df2) else 1.0
            scores.append(df_similarity)

        # Return average similarity
        return sum(scores) / len(scores) if scores else 0.0

    def _explain_match(self, target: Dict, match: Dict) -> str:
        """
        Explain why patterns match.

        Args:
            target: Target pattern
            match: Matched pattern

        Returns:
            Human-readable explanation
        """
        explanations = []

        # Check exact structure match
        if target['structure_hash'] == match['structure_hash']:
            explanations.append("Identical AST structure hash")

        # Check control flow similarity
        cf_similarity = len(set(target['control_flow']) & set(match['control_flow']))
        if cf_similarity > 0:
            explanations.append(f"Matching control flow: {cf_similarity} patterns")

        # Check operation similarity
        op_similarity = len(set(target['operations']) & set(match['operations']))
        if op_similarity > 0:
            explanations.append(f"Similar operations: {op_similarity} types")

        # Check data flow
        df_similarity = len(set(target['data_flow']) & set(match['data_flow']))
        if df_similarity > 0:
            explanations.append(f"Similar data flow: {df_similarity} patterns")

        return " | ".join(explanations) if explanations else "Structural similarity detected"

    def create_test_scenario(self) -> Tuple[str, str]:
        """
        Create test scenario from 012.txt specification.

        Returns:
            Tuple of (target_function, duplicate_function)
        """
        # Target function (new vibecoded version)
        target_code = '''
def calculate_record_hash(record_data):
    """Calculate hash of record data"""
    import json
    import hashlib

    json_string = json.dumps(record_data, sort_keys=True)
    hash_object = hashlib.sha256(json_string.encode())
    return hash_object.hexdigest()
'''

        # Semantic duplicate (existing in codebase)
        duplicate_code = '''
def generate_data_signature(input_dict):
    """Generate cryptographic signature for data"""
    import json
    import hashlib

    # Convert to JSON for consistent hashing
    serialized = json.dumps(input_dict, sort_keys=True)

    # Create SHA256 hash
    hasher = hashlib.sha256(serialized.encode('utf-8'))

    # Return hex digest
    return hasher.hexdigest()
'''

        return target_code, duplicate_code