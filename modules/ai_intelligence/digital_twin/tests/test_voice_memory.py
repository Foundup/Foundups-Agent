# -*- coding: utf-8 -*-
"""Tests for VoiceMemory."""

import json
import tempfile
from pathlib import Path

import pytest


def test_voice_memory_build_and_query():
    """Test building index and querying."""
    from modules.ai_intelligence.digital_twin.src.voice_memory import VoiceMemory
    
    with tempfile.TemporaryDirectory() as corpus_dir:
        with tempfile.TemporaryDirectory() as index_dir:
            # Create sample corpus
            sample = [
                {"text": "Japan visa requires a sponsor.", "id": "c1"},
                {"text": "Tokyo has great startups.", "id": "c2"},
            ]
            
            with open(f"{corpus_dir}/sample.json", "w") as f:
                json.dump(sample, f)
            
            # Build index
            vm = VoiceMemory(include_videos=False)
            count = vm.build_index(corpus_dir, index_dir)

            assert count == 2

            # Query
            results = vm.query("How do I get a visa for Japan?", k=2)
            
            assert len(results) > 0
            assert "text" in results[0]
            assert "score" in results[0]


def test_voice_memory_empty_corpus():
    """Test handling of empty corpus."""
    from modules.ai_intelligence.digital_twin.src.voice_memory import VoiceMemory

    with tempfile.TemporaryDirectory() as corpus_dir:
        with tempfile.TemporaryDirectory() as index_dir:
            vm = VoiceMemory(include_videos=False)
            count = vm.build_index(corpus_dir, index_dir)
            
            assert count == 0


def test_voice_memory_query_no_index():
    """Test query with no index returns empty."""
    from modules.ai_intelligence.digital_twin.src.voice_memory import VoiceMemory

    vm = VoiceMemory(include_videos=False)
    results = vm.query("test query", k=5)
    
    assert results == []


def test_voice_memory_stats():
    """Test get_stats returns correct info."""
    from modules.ai_intelligence.digital_twin.src.voice_memory import VoiceMemory

    with tempfile.TemporaryDirectory() as corpus_dir:
        with tempfile.TemporaryDirectory() as index_dir:
            sample = [{"text": "Test comment", "id": "c1", "type": "comment"}]

            with open(f"{corpus_dir}/sample.json", "w") as f:
                json.dump(sample, f)

            vm = VoiceMemory(include_videos=False)
            vm.build_index(corpus_dir, index_dir)
            
            stats = vm.get_stats()
            
            assert stats["total_documents"] == 1
            assert "backend" in stats


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
