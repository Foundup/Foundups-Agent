# -*- coding: utf-8 -*-
"""
Comment Search - HoloIndex RAG search over 012's comments.

WSP Compliance:
    WSP 84: Code Reuse (follows HoloIndex patterns)
    WSP 77: Agent Coordination

Purpose:
    Provide search_comments() API that delegates to VoiceMemory.
    Similar pattern to existing HoloIndex search utilities.
"""

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


def search_comments(
    query: str,
    k: int = 5,
    index_dir: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Search 012's comments and transcripts.
    
    Args:
        query: Search query
        k: Number of results
        index_dir: Optional path to voice memory index
        
    Returns:
        List of {text, source_id, source_type, score, ...}
    
    Example:
        >>> results = search_comments("Japan visa process", k=3)
        >>> for r in results:
        ...     print(f"{r['score']:.2f}: {r['text'][:50]}...")
    """
    try:
        from modules.ai_intelligence.digital_twin.src.voice_memory import VoiceMemory
        
        vm = VoiceMemory(index_dir=index_dir)
        results = vm.query(query, k=k)
        
        # Standardize output format
        return [
            {
                "text": r.get("text", ""),
                "source_id": r.get("source_id", ""),
                "source_type": r.get("source_type", "comment"),
                "score": r.get("score", 0.0),
                "video_id": r.get("video_id"),
                "timestamp": r.get("timestamp"),
                "url": r.get("url"),
            }
            for r in results
        ]
        
    except ImportError as e:
        logger.warning(f"[COMMENT-SEARCH] Failed to import VoiceMemory: {e}")
        return []
    except Exception as e:
        logger.error(f"[COMMENT-SEARCH] Search failed: {e}")
        return []


def index_comments(
    corpus_dir: str,
    index_dir: str
) -> int:
    """
    Build comment search index.
    
    Args:
        corpus_dir: Directory with comment/transcript files
        index_dir: Directory to save index
        
    Returns:
        Number of documents indexed
    """
    try:
        from modules.ai_intelligence.digital_twin.src.voice_memory import VoiceMemory
        
        vm = VoiceMemory()
        count = vm.build_index(corpus_dir, index_dir)
        
        logger.info(f"[COMMENT-SEARCH] Indexed {count} documents")
        return count
        
    except Exception as e:
        logger.error(f"[COMMENT-SEARCH] Indexing failed: {e}")
        return 0


def get_comment_index_stats(index_dir: str) -> Dict[str, Any]:
    """
    Get statistics for comment index.
    
    Args:
        index_dir: Path to index directory
        
    Returns:
        Dict with index statistics
    """
    try:
        from modules.ai_intelligence.digital_twin.src.voice_memory import VoiceMemory
        
        vm = VoiceMemory(index_dir=index_dir)
        return vm.get_stats()
        
    except Exception as e:
        logger.error(f"[COMMENT-SEARCH] Stats failed: {e}")
        return {"error": str(e)}
