"""Video Transcript Index - Semantic search across 012 video transcripts.

Sprint 7 implementation for Digital Twin learning.

WSP Compliance:
    - WSP 3: communication domain (transcript search)
    - WSP 72: Module independence (standalone index)
    - WSP 84: Reuses HoloIndex patterns (ChromaDB + sentence-transformers)
    - WSP 87: Size limits (separate file)

Architecture:
    JSONL Transcripts → Embeddings → ChromaDB → Semantic Search → Deep Links

Key Feature:
    "What did 012 say about X?" → Search → https://youtu.be/VIDEO_ID?t=TIMESTAMP
"""

import json
import logging
import os
from pathlib import Path
from typing import Dict, List, Optional, Generator, Any
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    """Single search result with deep link to video moment."""
    video_id: str
    title: str
    timestamp_sec: float
    end_sec: float
    text: str
    confidence: float
    url: str  # Deep link
    score: float  # Semantic similarity score


class VideoTranscriptIndex:
    """Semantic search index for video transcripts.

    Uses ChromaDB + sentence-transformers (same as HoloIndex).
    Enables "What did 012 say about X?" queries with deep links.

    WSP Compliance:
    - WSP 84: Reuses HoloIndex infrastructure
    - WSP 60: Module memory architecture
    """

    def __init__(
        self,
        ssd_path: Optional[str] = None,
        collection_name: str = "video_transcripts"
    ) -> None:
        """Initialize video transcript index.

        Args:
            ssd_path: Path to SSD for vector storage (default: E:/HoloIndex)
            collection_name: ChromaDB collection name
        """
        self.ssd_path = Path(ssd_path) if ssd_path else Path("E:/HoloIndex")
        self.vector_path = self.ssd_path / "vectors"
        self.models_path = self.ssd_path / "models"
        self.collection_name = collection_name

        # Lazy initialization
        self._client = None
        self._collection = None
        self._model = None
        self._initialized = False

    def _ensure_initialized(self) -> bool:
        """Lazy initialization of ChromaDB and model."""
        if self._initialized:
            return True

        try:
            import chromadb

            # Ensure directories
            self.vector_path.mkdir(parents=True, exist_ok=True)
            self.models_path.mkdir(parents=True, exist_ok=True)

            # Initialize ChromaDB
            self._client = chromadb.PersistentClient(path=str(self.vector_path))
            self._collection = self._client.get_or_create_collection(
                name=self.collection_name,
                metadata={"description": "012 video transcripts with timestamps"}
            )

            # Initialize sentence transformer
            os.environ['SENTENCE_TRANSFORMERS_HOME'] = str(self.models_path)

            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer("all-MiniLM-L6-v2")

            logger.info(f"[TRANSCRIPT-INDEX] Initialized - collection={self.collection_name}")
            self._initialized = True
            return True

        except ImportError as e:
            logger.error(f"[TRANSCRIPT-INDEX] Missing dependency: {e}")
            return False
        except Exception as e:
            logger.error(f"[TRANSCRIPT-INDEX] Initialization failed: {e}")
            return False

    def index_transcript(
        self,
        video_id: str,
        title: str,
        timestamp_sec: float,
        end_sec: float,
        text: str,
        confidence: float,
        url: str
    ) -> bool:
        """Index a single transcript segment.

        Args:
            video_id: YouTube video ID
            title: Video title
            timestamp_sec: Start position in video
            end_sec: End position in video
            text: Transcript text
            confidence: STT confidence
            url: Deep link URL

        Returns:
            True if indexed successfully
        """
        if not self._ensure_initialized():
            return False

        try:
            # Create unique ID
            doc_id = f"{video_id}_{int(timestamp_sec)}"

            # Generate embedding
            embedding = self._model.encode(text).tolist()

            # Store in ChromaDB
            self._collection.upsert(
                ids=[doc_id],
                embeddings=[embedding],
                documents=[text],
                metadatas=[{
                    "video_id": video_id,
                    "title": title,
                    "timestamp_sec": timestamp_sec,
                    "end_sec": end_sec,
                    "confidence": confidence,
                    "url": url
                }]
            )

            return True

        except Exception as e:
            logger.error(f"[TRANSCRIPT-INDEX] Index failed: {e}")
            return False

    def index_from_jsonl(self, jsonl_path: str) -> int:
        """Index transcripts from JSONL file.

        Args:
            jsonl_path: Path to JSONL file with TranscriptSegment records

        Returns:
            Number of segments indexed
        """
        if not self._ensure_initialized():
            return 0

        count = 0
        path = Path(jsonl_path)

        if not path.exists():
            logger.error(f"[TRANSCRIPT-INDEX] File not found: {jsonl_path}")
            return 0

        logger.info(f"[TRANSCRIPT-INDEX] Indexing from {jsonl_path}")

        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    segment = json.loads(line.strip())
                    if self.index_transcript(
                        video_id=segment['video_id'],
                        title=segment['title'],
                        timestamp_sec=segment['timestamp_sec'],
                        end_sec=segment['end_sec'],
                        text=segment['text'],
                        confidence=segment['confidence'],
                        url=segment['url']
                    ):
                        count += 1
                except Exception as e:
                    logger.warning(f"[TRANSCRIPT-INDEX] Skip line: {e}")
                    continue

        logger.info(f"[TRANSCRIPT-INDEX] Indexed {count} segments")
        return count

    def search(
        self,
        query: str,
        limit: int = 10,
        min_score: float = 0.3
    ) -> List[SearchResult]:
        """Search transcripts semantically.

        Args:
            query: Search query (e.g., "What did 012 say about WSP?")
            limit: Maximum results
            min_score: Minimum similarity score (0-1)

        Returns:
            List of SearchResult with deep links
        """
        if not self._ensure_initialized():
            return []

        try:
            # Generate query embedding
            query_embedding = self._model.encode(query).tolist()

            # Search ChromaDB
            results = self._collection.query(
                query_embeddings=[query_embedding],
                n_results=limit,
                include=["documents", "metadatas", "distances"]
            )

            # Convert to SearchResult
            search_results = []

            if results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    metadata = results['metadatas'][0][i]
                    distance = results['distances'][0][i]

                    # Convert distance to score (ChromaDB uses L2 distance)
                    # Lower distance = higher similarity
                    score = max(0, 1 - (distance / 2))

                    if score < min_score:
                        continue

                    search_results.append(SearchResult(
                        video_id=metadata['video_id'],
                        title=metadata['title'],
                        timestamp_sec=metadata['timestamp_sec'],
                        end_sec=metadata['end_sec'],
                        text=doc,
                        confidence=metadata['confidence'],
                        url=metadata['url'],
                        score=score
                    ))

            # Sort by score descending
            search_results.sort(key=lambda x: x.score, reverse=True)

            logger.info(f"[TRANSCRIPT-INDEX] Search '{query}' -> {len(search_results)} results")
            return search_results

        except Exception as e:
            logger.error(f"[TRANSCRIPT-INDEX] Search failed: {e}")
            return []

    def get_stats(self) -> Dict[str, Any]:
        """Get index statistics."""
        if not self._ensure_initialized():
            return {"error": "Not initialized"}

        try:
            count = self._collection.count()
            return {
                "collection": self.collection_name,
                "segment_count": count,
                "ssd_path": str(self.ssd_path),
                "initialized": self._initialized
            }
        except Exception as e:
            return {"error": str(e)}

    def clear(self) -> bool:
        """Clear all indexed transcripts."""
        if not self._ensure_initialized():
            return False

        try:
            # Delete and recreate collection
            self._client.delete_collection(self.collection_name)
            self._collection = self._client.create_collection(
                name=self.collection_name,
                metadata={"description": "012 video transcripts with timestamps"}
            )
            logger.info(f"[TRANSCRIPT-INDEX] Cleared collection: {self.collection_name}")
            return True
        except Exception as e:
            logger.error(f"[TRANSCRIPT-INDEX] Clear failed: {e}")
            return False


# Convenience function
def get_transcript_index(
    ssd_path: Optional[str] = None,
    collection_name: str = "video_transcripts"
) -> VideoTranscriptIndex:
    """Get a configured transcript index instance."""
    return VideoTranscriptIndex(ssd_path=ssd_path, collection_name=collection_name)


# MCP-compatible search function for Sprint 8
def search_012_transcripts(
    query: str,
    limit: int = 10
) -> List[Dict[str, Any]]:
    """Search 012's video transcripts.

    MCP-compatible function for digital twin queries.

    Args:
        query: Natural language query (e.g., "What did 012 say about WSP?")
        limit: Maximum results

    Returns:
        List of dicts with video_id, title, timestamp, text, url, score
    """
    index = get_transcript_index()
    results = index.search(query, limit=limit)
    return [asdict(r) for r in results]
