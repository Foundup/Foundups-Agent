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

Pattern Memory - ChromaDB-backed storage for Qwen/Gemma training
Stores patterns extracted from 012.txt for in-context learning (RAG)
WSP Compliance: WSP 93 (CodeIndex Surgical Intelligence), WSP 46 (WRE Pattern)
"""

import os
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Optional, Any
from pathlib import Path
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)
if os.getenv("HOLO_PATTERN_MEMORY_LOGS", "true").lower() not in {"1", "true", "yes", "on"}:
    logger.setLevel(logging.WARNING)


class PatternMemory:
    """
    ChromaDB-backed pattern memory for Qwen/Gemma training.

    Implements WRE pattern (WSP 46):
    - Store patterns from 012.txt (operational decisions)
    - Retrieve similar patterns for few-shot learning
    - No fine-tuning required - pure in-context learning

    Architecture:
    - 012 (Human) -> 0102 (Digital Twin) -> Patterns -> ChromaDB
    - At inference: Query -> Retrieve patterns -> Gemma/Qwen with context
    """

    def __init__(self, persist_directory: str = "O:/Foundups-Agent/holo_index/memory/chroma"):
        """
        Initialize ChromaDB client for pattern storage.

        Args:
            persist_directory: Path to ChromaDB persistent storage
        """
        self.persist_dir = Path(persist_directory)
        self.persist_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"[PATTERN-MEMORY] Initializing ChromaDB at {self.persist_dir}")

        # Initialize ChromaDB client with persistence
        self.client = chromadb.PersistentClient(
            path=str(self.persist_dir),
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )

        # Create or load collection
        self.collection = self.client.get_or_create_collection(
            name="012_patterns",
            metadata={
                "description": "Training patterns from 012.txt for Qwen/Gemma",
                "created_at": datetime.now().isoformat(),
                "wsp_compliance": "WSP 46 (WRE), WSP 93 (CodeIndex)"
            }
        )

        logger.info(f"[PATTERN-MEMORY] Collection loaded: {self.collection.count()} patterns")

    def store_pattern(self, pattern: dict) -> bool:
        """
        Store pattern in ChromaDB for future retrieval.

        Pattern schema:
        {
            "id": "012_12345" or "live_67890",
            "context": "Full log excerpt or decision context",
            "decision": {"action": "...", "reasoning": "..."},
            "outcome": {"result": "...", "success": bool},
            "module": "modules/path/to/file.py",
            "actual_code": "Verified code snippet from HoloIndex",
            "timestamp": "2025-10-15T12:34:56",
            "verified": bool,
            "source": "012.txt" or "live_chat"
        }

        Args:
            pattern: Pattern dictionary to store

        Returns:
            bool: True if stored successfully
        """
        try:
            pattern_id = pattern.get("id")
            if not pattern_id:
                logger.warning("[PATTERN-MEMORY] Pattern missing 'id' field - skipping")
                return False

            # Extract context for embedding
            context = pattern.get("context", "")
            if not context:
                logger.warning(f"[PATTERN-MEMORY] Pattern {pattern_id} missing context - skipping")
                return False

            # Prepare metadata (all non-text fields)
            metadata = {
                "decision": json.dumps(pattern.get("decision", {})),
                "outcome": json.dumps(pattern.get("outcome", {})),
                "module": pattern.get("module", "unknown"),
                "timestamp": pattern.get("timestamp", ""),
                "verified": pattern.get("verified", False),
                "source": pattern.get("source", "012.txt")
            }

            # Store actual code separately if present
            if pattern.get("actual_code"):
                metadata["actual_code"] = pattern["actual_code"][:500]  # Truncate to 500 chars

            # Add to collection
            self.collection.add(
                ids=[pattern_id],
                documents=[context],
                metadatas=[metadata]
            )

            logger.debug(f"[PATTERN-MEMORY] Stored pattern {pattern_id} from {metadata['source']}")
            return True

        except Exception as e:
            logger.error(f"[PATTERN-MEMORY] Storage failed: {e}")
            return False

    def recall_similar(self, query: str, n: int = 5, min_similarity: float = 0.5) -> List[dict]:
        """
        Retrieve top-N most similar patterns for few-shot learning.

        Used by Gemma/Qwen to retrieve relevant past decisions before inference.

        Args:
            query: Query text (e.g., "Which module handles YouTube auth?")
            n: Number of results to return
            min_similarity: Minimum similarity threshold (0.0-1.0)

        Returns:
            List of patterns with similarity scores, sorted by relevance
        """
        try:
            # Query ChromaDB
            results = self.collection.query(
                query_texts=[query],
                n_results=n,
                include=["documents", "metadatas", "distances"]
            )

            if not results["ids"][0]:
                logger.info(f"[PATTERN-MEMORY] No patterns found for query: {query[:50]}...")
                return []

            # Convert to pattern format
            patterns = []
            for i in range(len(results["ids"][0])):
                # Convert distance to similarity (cosine distance: 0=identical, 2=opposite)
                distance = results["distances"][0][i]
                similarity = 1.0 - (distance / 2.0)  # Normalize to 0.0-1.0

                # Filter by minimum similarity
                if similarity < min_similarity:
                    continue

                pattern = {
                    "id": results["ids"][0][i],
                    "context": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "similarity": similarity
                }

                # Parse JSON metadata fields
                try:
                    pattern["decision"] = json.loads(pattern["metadata"].get("decision", "{}"))
                    pattern["outcome"] = json.loads(pattern["metadata"].get("outcome", "{}"))
                except json.JSONDecodeError:
                    pass

                patterns.append(pattern)

            logger.info(f"[PATTERN-MEMORY] Recalled {len(patterns)} patterns (query: {query[:50]}...)")
            return patterns

        except Exception as e:
            logger.error(f"[PATTERN-MEMORY] Recall failed: {e}")
            return []

    def count(self) -> int:
        """Get total number of patterns stored."""
        return self.collection.count()

    def get_checkpoint(self) -> int:
        """
        Get last processed line number from checkpoint file.

        Used to resume 012.txt processing from where we left off.

        Returns:
            int: Last processed line number (0 if no checkpoint)
        """
        checkpoint_file = self.persist_dir / "checkpoint.txt"
        if checkpoint_file.exists():
            try:
                return int(checkpoint_file.read_text().strip())
            except ValueError:
                logger.warning("[PATTERN-MEMORY] Invalid checkpoint file - resetting to 0")
                return 0
        return 0

    def save_checkpoint(self, line_number: int):
        """
        Save checkpoint for resumable 012.txt processing.

        Args:
            line_number: Last processed line number
        """
        checkpoint_file = self.persist_dir / "checkpoint.txt"
        checkpoint_file.write_text(str(line_number))
        logger.info(f"[PATTERN-MEMORY] Checkpoint saved: line {line_number}")

    def get_stats(self) -> Dict[str, Any]:
        """
        Get pattern memory statistics.

        Returns:
            dict: Statistics including counts, sources, verification rate
        """
        total = self.count()

        if total == 0:
            return {
                "total_patterns": 0,
                "checkpoint_line": 0,
                "sources": {},
                "verification_rate": 0.0
            }

        # Query all patterns to get stats (limit to 1000 for performance)
        results = self.collection.get(
            limit=min(total, 1000),
            include=["metadatas"]
        )

        # Count by source
        sources = {}
        verified_count = 0

        for metadata in results["metadatas"]:
            source = metadata.get("source", "unknown")
            sources[source] = sources.get(source, 0) + 1

            if metadata.get("verified", False):
                verified_count += 1

        verification_rate = verified_count / len(results["metadatas"]) if results["metadatas"] else 0.0

        return {
            "total_patterns": total,
            "checkpoint_line": self.get_checkpoint(),
            "sources": sources,
            "verification_rate": verification_rate,
            "verified_count": verified_count
        }

    def clear_all(self, confirm: bool = False):
        """
        Clear all patterns from memory (dangerous - requires confirmation).

        Args:
            confirm: Must be True to actually clear
        """
        if not confirm:
            logger.warning("[PATTERN-MEMORY] Clear aborted - confirmation required")
            return

        logger.warning("[PATTERN-MEMORY] Clearing all patterns...")
        self.client.delete_collection("012_patterns")

        # Recreate empty collection
        self.collection = self.client.get_or_create_collection(
            name="012_patterns",
            metadata={
                "description": "Training patterns from 012.txt for Qwen/Gemma",
                "created_at": datetime.now().isoformat(),
                "wsp_compliance": "WSP 46 (WRE), WSP 93 (CodeIndex)"
            }
        )

        logger.warning("[PATTERN-MEMORY] All patterns cleared")

    def format_for_prompt(self, patterns: List[dict], max_patterns: int = 3) -> str:
        """
        Format retrieved patterns for inclusion in Gemma/Qwen prompt.

        Creates few-shot examples from past decisions.

        Args:
            patterns: List of patterns from recall_similar()
            max_patterns: Maximum patterns to include in prompt

        Returns:
            str: Formatted text for prompt inclusion
        """
        if not patterns:
            return "No similar patterns found in memory."

        formatted = ["Based on past operational decisions:\n"]

        for i, pattern in enumerate(patterns[:max_patterns], 1):
            formatted.append(f"\n--- Pattern {i} (similarity: {pattern['similarity']:.2f}) ---")
            formatted.append(f"Context: {pattern['context'][:200]}...")

            if pattern.get("decision"):
                formatted.append(f"Decision: {pattern['decision']}")

            if pattern.get("outcome"):
                formatted.append(f"Outcome: {pattern['outcome']}")

            if pattern["metadata"].get("module"):
                formatted.append(f"Module: {pattern['metadata']['module']}")

        return "\n".join(formatted)


if __name__ == "__main__":
    # Test pattern memory
    import sys

    logging.basicConfig(level=logging.INFO)

    # Initialize
    memory = PatternMemory()

    print(f"\n[TEST] Pattern Memory Test")
    print(f"="*60)

    # Show stats
    stats = memory.get_stats()
    print(f"\nCurrent Stats:")
    print(f"  Total Patterns: {stats['total_patterns']}")
    print(f"  Checkpoint: Line {stats['checkpoint_line']}")
    print(f"  Verification Rate: {stats['verification_rate']:.1%}")
    print(f"  Sources: {stats['sources']}")

    # Test storage
    if "--test-store" in sys.argv:
        print(f"\n[TEST] Storing test pattern...")

        test_pattern = {
            "id": "test_001",
            "context": "User asked which module handles YouTube authentication. System searched and found youtube_auth module.",
            "decision": {
                "action": "recommend_module",
                "module": "modules/platform_integration/youtube_auth/",
                "reasoning": "Handles OAuth and token management"
            },
            "outcome": {
                "success": True,
                "user_satisfied": True
            },
            "module": "modules/platform_integration/youtube_auth/src/youtube_auth.py",
            "timestamp": datetime.now().isoformat(),
            "verified": True,
            "source": "test"
        }

        success = memory.store_pattern(test_pattern)
        print(f"  Storage: {'[OK] Success' if success else '[FAIL] Failed'}")

    # Test recall
    if "--test-recall" in sys.argv:
        print(f"\n[TEST] Recalling similar patterns...")

        query = "Which module handles YouTube authentication?"
        patterns = memory.recall_similar(query, n=3)

        print(f"  Query: {query}")
        print(f"  Results: {len(patterns)} patterns found")

        for pattern in patterns:
            print(f"\n  Pattern {pattern['id']}:")
            print(f"    Similarity: {pattern['similarity']:.2f}")
            print(f"    Context: {pattern['context'][:100]}...")
            print(f"    Module: {pattern['metadata'].get('module', 'unknown')}")

    print(f"\n{'='*60}")
    print(f"[TEST] Complete")
    print(f"\nUsage:")
    print(f"  python pattern_memory.py --test-store  # Store test pattern")
    print(f"  python pattern_memory.py --test-recall # Recall patterns")
