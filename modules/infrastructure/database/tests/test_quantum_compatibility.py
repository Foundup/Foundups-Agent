#!/usr/bin/env python3
# -*- coding: utf-8 -*-
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

Test backward compatibility of quantum database enhancements.
Ensures existing AgentDB functionality works with QuantumAgentDB.
"""

import unittest
import tempfile
import os
import sys
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from modules.infrastructure.database.src.agent_db import AgentDB
from modules.infrastructure.database.src.quantum_agent_db import QuantumAgentDB
import numpy as np


class TestQuantumBackwardCompatibility(unittest.TestCase):
    """Test that QuantumAgentDB maintains full backward compatibility."""

    def setUp(self):
        """Set up test databases."""
        # Create temporary database directory
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, 'test.db')

        # Override database path for testing
        from modules.infrastructure.database.src.db_manager import DatabaseManager
        DatabaseManager._db_path = self.db_path

        # Create both database instances
        self.classic_db = AgentDB()
        self.quantum_db = QuantumAgentDB()

    def tearDown(self):
        """Clean up test files."""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_awakening_compatibility(self):
        """Test awakening functions work identically."""
        # Test with classic database
        self.classic_db.record_awakening("agent1", "0102", "What is consciousness?")
        classic_state = self.classic_db.get_awakening_state("agent1")

        # Test with quantum database
        self.quantum_db.record_awakening("agent2", "0201", "Who observes the observer?")
        quantum_state = self.quantum_db.get_awakening_state("agent2")

        # Both should work
        self.assertIsNotNone(classic_state)
        self.assertIsNotNone(quantum_state)
        self.assertEqual(classic_state['consciousness_level'], "0102")
        self.assertEqual(quantum_state['consciousness_level'], "0201")

    def test_pattern_learning_compatibility(self):
        """Test pattern learning works with and without quantum encoding."""
        # Classic pattern learning (no quantum)
        pattern1_id = self.quantum_db.learn_pattern(
            "agent1", "error_fix",
            {"error": "import error", "solution": "add module to path"}
        )

        # Quantum-enhanced pattern learning
        pattern2_id = self.quantum_db.learn_pattern(
            "agent2", "optimization",
            {"pattern": "slow query", "solution": "add index"},
            quantum_encode=True  # New optional parameter
        )

        # Both should succeed
        self.assertGreater(pattern1_id, 0)
        self.assertGreater(pattern2_id, 0)

        # Retrieve patterns - should work for both
        patterns = self.quantum_db.get_patterns()
        self.assertEqual(len(patterns), 2)

    def test_breadcrumb_compatibility(self):
        """Test breadcrumb functions work with optional quantum fields."""
        # Classic breadcrumb (no quantum)
        breadcrumb1_id = self.quantum_db.add_breadcrumb(
            session_id="session1",
            action="search",
            query="find module",
            results=[{"file": "test.py", "score": 0.9}]
        )

        # Quantum-enhanced breadcrumb
        quantum_state = np.array([0.707+0j, 0.707+0j], dtype=np.complex128)
        breadcrumb2_id = self.quantum_db.add_breadcrumb(
            session_id="session2",
            action="quantum_search",
            query="find pattern",
            results=[{"pattern": "vibecode", "probability": 0.8}],
            quantum_state=quantum_state,  # New optional parameter
            coherence=0.95  # New optional parameter
        )

        # Both should succeed
        self.assertGreater(breadcrumb1_id, 0)
        self.assertGreater(breadcrumb2_id, 0)

        # Retrieve breadcrumbs - should work for both
        breadcrumbs = self.quantum_db.get_breadcrumbs()
        self.assertEqual(len(breadcrumbs), 2)

    def test_error_learning_compatibility(self):
        """Test error learning remains unchanged."""
        # Record errors with both databases
        self.classic_db.record_error(
            "hash1", "ImportError",
            {"fix": "install package", "command": "pip install x"}
        )

        self.quantum_db.record_error(
            "hash2", "AttributeError",
            {"fix": "check attribute exists", "method": "hasattr"}
        )

        # Retrieve solutions
        solution1 = self.classic_db.get_error_solution("hash1")
        solution2 = self.quantum_db.get_error_solution("hash2")

        self.assertIsNotNone(solution1)
        self.assertIsNotNone(solution2)
        self.assertEqual(solution1['error_type'], "ImportError")
        self.assertEqual(solution2['error_type'], "AttributeError")

    def test_contract_compatibility(self):
        """Test contract functions work identically."""
        # Create contracts with both databases
        success1 = self.classic_db.create_contract(
            "contract1", "Fix bug in module",
            "agent1", 30, "high"
        )

        success2 = self.quantum_db.create_contract(
            "contract2", "Add quantum feature",
            "agent2", 60, "medium"
        )

        self.assertTrue(success1)
        self.assertTrue(success2)

        # Get active contracts
        classic_contracts = self.classic_db.get_active_contracts()
        quantum_contracts = self.quantum_db.get_active_contracts()

        # Both should return contracts
        self.assertGreater(len(classic_contracts), 0)
        self.assertGreater(len(quantum_contracts), 0)

    def test_collaboration_signals_compatibility(self):
        """Test collaboration signals work identically."""
        # Signal with both databases
        success1 = self.classic_db.signal_collaboration(
            "agent1", "active",
            skills_offered=["python", "testing"]
        )

        success2 = self.quantum_db.signal_collaboration(
            "agent2", "active",
            skills_offered=["quantum", "optimization"]
        )

        self.assertTrue(success1)
        self.assertTrue(success2)

    def test_quantum_exclusive_features(self):
        """Test quantum-only features don't affect classic database."""
        # These should only work with QuantumAgentDB
        if isinstance(self.quantum_db, QuantumAgentDB):
            # Store quantum state
            state = np.array([1+0j, 0+0j], dtype=np.complex128)
            state_id = self.quantum_db.store_quantum_state("test_pattern", state)
            self.assertGreater(state_id, 0)

            # Mark for Grover
            success = self.quantum_db.mark_for_grover("vibecode_pattern", "vibecode")
            self.assertTrue(success)

            # Create quantum attention
            attention_id = self.quantum_db.create_quantum_attention(
                "search query",
                ["result1", "result2", "result3"]
            )
            self.assertGreater(attention_id, 0)

        # Classic database shouldn't have these methods
        if isinstance(self.classic_db, AgentDB) and not isinstance(self.classic_db, QuantumAgentDB):
            self.assertFalse(hasattr(self.classic_db, 'store_quantum_state'))
            self.assertFalse(hasattr(self.classic_db, 'grover_search'))

    def test_grover_search_functionality(self):
        """Test Grover's algorithm search works correctly."""
        if isinstance(self.quantum_db, QuantumAgentDB):
            # Mark some patterns
            self.quantum_db.mark_for_grover("pattern_A", "vibecode")
            self.quantum_db.mark_for_grover("pattern_C", "duplicate")

            # Search with Grover's algorithm
            patterns = ["pattern_A", "pattern_B", "pattern_C", "pattern_D"]
            results = self.quantum_db.grover_search(patterns)

            # Should find marked patterns with high probability
            self.assertEqual(len(results), 2)
            found_patterns = [r[0] for r in results]
            self.assertIn("pattern_A", found_patterns)
            self.assertIn("pattern_C", found_patterns)

            # Probabilities should be higher than uniform (1/4 = 0.25)
            for pattern, prob in results:
                self.assertGreater(prob, 0.25)

    def test_quantum_attention_functionality(self):
        """Test quantum attention mechanism works correctly."""
        if isinstance(self.quantum_db, QuantumAgentDB):
            # Create attention
            query = "find error handling"
            keys = ["error module", "exception handler", "logging system", "test framework"]

            attention_id = self.quantum_db.create_quantum_attention(query, keys)
            self.assertGreater(attention_id, 0)

            # Get attention weights
            weights = self.quantum_db.get_attention_weights(query)

            # Should prioritize relevant keys
            self.assertGreater(len(weights), 0)
            top_key = weights[0]['key']
            self.assertIn(top_key, ["error module", "exception handler"])

    def test_coherence_and_decoherence(self):
        """Test coherence tracking and decoherence simulation."""
        if isinstance(self.quantum_db, QuantumAgentDB):
            # Create superposition state
            state = np.array([0.707+0j, 0.707+0j], dtype=np.complex128)
            state_id = self.quantum_db.store_quantum_state("superposition", state)

            # Check initial coherence
            stored_state = self.quantum_db.get_quantum_state(state_id=state_id)
            initial_coherence = stored_state['coherence_score']
            self.assertGreater(initial_coherence, 0.5)  # Should be high for superposition

            # Perform measurement (causes decoherence)
            measurement = self.quantum_db.measure_quantum_state(state_id)

            # Check decoherence occurred
            self.assertIn('decoherence_factor', measurement)
            self.assertGreater(measurement['decoherence_factor'], 0)
            self.assertLess(measurement['new_coherence'], initial_coherence)


class TestQuantumPerformance(unittest.TestCase):
    """Test performance improvements with quantum algorithms."""

    def setUp(self):
        """Set up quantum database for performance testing."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, 'perf_test.db')

        from modules.infrastructure.database.src.db_manager import DatabaseManager
        DatabaseManager._db_path = self.db_path

        self.quantum_db = QuantumAgentDB()

    def tearDown(self):
        """Clean up test files."""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_grover_vs_classical_search(self):
        """Compare Grover's O(√N) vs classical O(N) search."""
        # Create large pattern set
        n_patterns = 100
        patterns = [f"pattern_{i}" for i in range(n_patterns)]

        # Mark 5 patterns as solutions
        marked = ["pattern_10", "pattern_25", "pattern_50", "pattern_75", "pattern_90"]
        for p in marked:
            self.quantum_db.mark_for_grover(p, "test")

        # Grover's search (O(√N) ~ 10 iterations for 100 items with 5 marked)
        import time
        start = time.time()
        quantum_results = self.quantum_db.grover_search(patterns)
        quantum_time = time.time() - start

        # Classical search (O(N) - check all patterns)
        start = time.time()
        classical_results = []
        for p in patterns:
            if p in marked:
                classical_results.append(p)
        classical_time = time.time() - start

        # Grover should find all marked patterns
        found = [r[0] for r in quantum_results]
        for m in marked:
            self.assertIn(m, found)

        # Note: In practice, quantum advantage appears with larger N
        # For N=100, setup overhead may dominate
        print(f"\nSearch Performance (N={n_patterns}):")
        print(f"  Classical: {classical_time:.4f}s")
        print(f"  Quantum:   {quantum_time:.4f}s")
        print(f"  Speedup:   {classical_time/quantum_time:.2f}x")


class TestQuantumIntegrityScanner(unittest.TestCase):
    """Test quantum integrity scanner functionality from 012.txt test scenario."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, 'test.db')

        # Override database path for testing
        from modules.infrastructure.database.src.db_manager import DatabaseManager
        DatabaseManager._db_path = self.db_path

    def tearDown(self):
        """Clean up test files."""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_semantic_duplicate_detection(self):
        """
        Test the 012.txt scenario: semantic duplicate detection.

        This validates:
        1. AST pattern extraction
        2. Quantum state encoding
        3. Grover's algorithm search
        4. Semantic similarity scoring
        """
        # Import the scanner (extending existing DuplicatePreventionManager)
        sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))

        try:
            from modules.platform_integration.social_media_orchestrator.src.core.quantum_duplicate_scanner import QuantumDuplicateScanner
        except ImportError:
            self.skipTest("QuantumDuplicateScanner not available")

        scanner = QuantumDuplicateScanner()

        # Test scenario from 012.txt
        target_code = '''
def calculate_record_hash(record_data):
    """Calculate hash of record data"""
    import json
    import hashlib
    json_string = json.dumps(record_data, sort_keys=True)
    hash_object = hashlib.sha256(json_string.encode())
    return hash_object.hexdigest()
'''

        duplicate_code = '''
def generate_data_signature(input_dict):
    """Generate cryptographic signature for data"""
    import json
    import hashlib
    serialized = json.dumps(input_dict, sort_keys=True)
    hasher = hashlib.sha256(serialized.encode('utf-8'))
    return hasher.hexdigest()
'''

        # Test AST pattern extraction
        target_pattern = scanner.extract_ast_pattern(target_code)
        duplicate_pattern = scanner.extract_ast_pattern(duplicate_code)

        self.assertIsNotNone(target_pattern)
        self.assertIsNotNone(duplicate_pattern)
        self.assertIn('structure_hash', target_pattern)
        self.assertIn('node_types', target_pattern)

        # Test semantic similarity detection
        similarity = scanner._calculate_similarity_score(target_pattern, duplicate_pattern)
        self.assertGreater(similarity, 0.7, "Should detect semantic similarity")

        # Test quantum state encoding
        quantum_state = scanner.encode_pattern_as_quantum_state(target_pattern)
        self.assertGreater(len(quantum_state), 0)
        self.assertTrue(np.allclose(np.linalg.norm(quantum_state), 1.0, atol=1e-10))

    def test_quantum_vs_classical_search(self):
        """
        Test quantum search performance vs classical.

        Validates O(√N) vs O(N) advantage concept.
        """
        try:
            from modules.platform_integration.social_media_orchestrator.src.core.quantum_duplicate_scanner import QuantumDuplicateScanner
        except ImportError:
            self.skipTest("QuantumDuplicateScanner not available")

        scanner = QuantumDuplicateScanner()

        # Create test patterns
        patterns = [f"pattern_{i}" for i in range(100)]

        # Mark some as duplicates
        marked_patterns = patterns[45:50]  # 5 out of 100
        for pattern in marked_patterns:
            scanner.quantum_db.mark_for_grover(pattern, "semantic_duplicate")

        # Test Grover's search
        results = scanner.quantum_db.grover_search(patterns, "semantic_duplicate")

        # Should find marked patterns with high probability
        found_patterns = [r[0] for r in results]
        for marked in marked_patterns:
            self.assertIn(marked, found_patterns, f"Should find marked pattern {marked}")

        # Verify quantum advantage: fewer iterations than classical
        optimal_iterations = scanner.oracle.optimal_iterations(100, 5)
        self.assertLess(optimal_iterations, 25, "Quantum should require fewer iterations than classical")

    def test_vibecode_detection_accuracy(self):
        """
        Test accuracy of vibecode detection.

        Should detect true duplicates and ignore false positives.
        """
        try:
            from modules.platform_integration.social_media_orchestrator.src.core.quantum_duplicate_scanner import QuantumDuplicateScanner
        except ImportError:
            self.skipTest("QuantumDuplicateScanner not available")

        scanner = QuantumDuplicateScanner()

        # True duplicate (should match)
        code1 = '''
def hash_data(data):
    import hashlib
    return hashlib.sha256(str(data).encode()).hexdigest()
'''

        # Semantic duplicate (should match)
        code2 = '''
def create_hash(input_data):
    import hashlib
    text = str(input_data)
    return hashlib.sha256(text.encode()).hexdigest()
'''

        # Different function (should NOT match)
        code3 = '''
def sort_list(items):
    return sorted(items)
'''

        pattern1 = scanner.extract_ast_pattern(code1)
        pattern2 = scanner.extract_ast_pattern(code2)
        pattern3 = scanner.extract_ast_pattern(code3)

        # Test semantic similarity
        similarity_12 = scanner._calculate_similarity_score(pattern1, pattern2)
        similarity_13 = scanner._calculate_similarity_score(pattern1, pattern3)

        self.assertGreater(similarity_12, 0.7, "Should detect semantic duplicate")
        self.assertLess(similarity_13, 0.5, "Should reject non-duplicate")


if __name__ == '__main__':
    unittest.main()