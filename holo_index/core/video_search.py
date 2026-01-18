# -*- coding: utf-8 -*-
"""
Video Content Index for HoloIndex - 012 Digital Twin Training

Stores video segment content in ChromaDB for semantic search, enabling 0102
to reference 012's actual video content when commenting.

WSP Compliance:
    WSP 72: Module Independence
    WSP 84: Code Reuse (follows holo_index.py patterns)
    WSP 91: DAE Observability (telemetry integration)

Example:
    >>> from holo_index.core.video_search import VideoContentIndex
    >>> index = VideoContentIndex()
    >>> index.index_video(result)  # GeminiAnalysisResult
    >>> matches = index.search("education singularity")
    >>> print(matches[0].url)  # https://youtube.com/watch?v=...&t=70
"""

import json
import logging
import os
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


# =============================================================================
# Entity Correction - Fix common STT errors for 012's terminology
# =============================================================================

ENTITY_CORRECTIONS = {
    # Organization names
    r"\bedu\.org\b": "eduit.org",
    r"\beduit org\b": "eduit.org",
    r"\bedu it org\b": "eduit.org",
    r"\beducate\.org\b": "eduit.org",
    r"\bedu org\b": "eduit.org",
    r"\bEdutit\b": "Eduit",
    r"\bedutit\b": "Eduit",

    # Technical terms
    r"\be-revolution\b": "e-Revolution",
    r"\be3\.?0\b": "E3.0",
    r"\beducation 3\.?0\b": "Education 3.0",

    # Names
    r"\bMichael trout\b": "Michael Trauth",
    r"\bMichael Trout\b": "Michael Trauth",
    r"\btrout\b": "Trauth",
    r"\bTrout\b": "Trauth",

    # 012's terms
    r"\bzero one two\b": "012",
    r"\bZero One Two\b": "012",
    r"\bo one two\b": "012",
    r"\bfoundups\b": "FoundUps",
    r"\bFoundups\b": "FoundUps",
    r"\bundaodu\b": "UnDaoDu",
    r"\bUndaodu\b": "UnDaoDu",
    r"\bun dao du\b": "UnDaoDu",

    # Common STT errors
    r"\brice patties\b": "rice paddies",
    r"\brice Patties\b": "rice paddies",
}


def correct_entities(text: str) -> str:
    """
    Correct known STT errors in transcribed text.

    Args:
        text: Raw transcribed text

    Returns:
        Text with entity corrections applied
    """
    corrected = text
    for pattern, replacement in ENTITY_CORRECTIONS.items():
        corrected = re.sub(pattern, replacement, corrected, flags=re.IGNORECASE)
    return corrected

# Lazy imports to match HoloIndex patterns
try:
    import chromadb
except ImportError:
    chromadb = None
    logger.warning("[VIDEO-INDEX] chromadb not available")


@dataclass
class VideoMatch:
    """A matching video segment from search."""
    video_id: str
    title: str
    channel: str
    start_time: str
    end_time: str
    content: str
    speaker: Optional[str]
    topics: List[str]
    similarity: float
    url: str  # Deep link with timestamp
    
    def to_reference(self) -> str:
        """Format as a reference for comment replies."""
        return f"012 discussed this at {self.url}: \"{self.content[:100]}...\""


class VideoContentIndex:
    """
    Store and search video segments in ChromaDB.
    
    Enables 0102 to find relevant 012 video content when responding to
    comments, creating a more accurate digital twin experience.
    
    Example:
        >>> index = VideoContentIndex()
        >>> index.index_video(gemini_result, channel="undaodu")
        >>> matches = index.search("education revolution", k=3)
        >>> for m in matches:
        ...     print(f"{m.title} @ {m.start_time}: {m.content[:50]}")
    """
    
    COLLECTION_NAME = "video_segments"
    
    def __init__(
        self,
        ssd_path: str = "E:/HoloIndex",
        model_name: str = "all-MiniLM-L6-v2",
    ):
        """
        Initialize VideoContentIndex.
        
        Args:
            ssd_path: Path to SSD for persistent ChromaDB storage
            model_name: SentenceTransformer model for embeddings
        """
        if chromadb is None:
            raise ImportError("chromadb is required. Install with: pip install chromadb")
        
        self.ssd_path = Path(ssd_path)
        self.vector_path = self.ssd_path / "vectors"
        self.vector_path.mkdir(parents=True, exist_ok=True)
        
        self.client = chromadb.PersistentClient(path=str(self.vector_path))
        self.collection = self._ensure_collection()
        
        # Lazy load model
        self.model = None
        self.model_name = model_name
        
        logger.info(f"[VIDEO-INDEX] Initialized with {self.collection.count()} segments")
    
    def _ensure_collection(self):
        """Get or create the video segments collection."""
        try:
            return self.client.get_collection(self.COLLECTION_NAME)
        except Exception:
            return self.client.create_collection(self.COLLECTION_NAME)
    
    def _get_model(self):
        """Lazy load SentenceTransformer model."""
        if self.model is None:
            try:
                from sentence_transformers import SentenceTransformer
                self.model = SentenceTransformer(self.model_name)
                logger.info(f"[VIDEO-INDEX] Loaded model: {self.model_name}")
            except Exception as e:
                logger.warning(f"[VIDEO-INDEX] Model load failed: {e}")
                self.model = None
        return self.model
    
    def _get_embedding(self, text: str) -> List[float]:
        """Generate embedding for text."""
        model = self._get_model()
        if model:
            return model.encode(text, show_progress_bar=False).tolist()
        # Fallback: 384-dim zero vector (matches all-MiniLM-L6-v2)
        return [0.0] * 384
    
    @staticmethod
    def _timestamp_to_seconds(ts: str) -> int:
        """Convert 'M:SS' or 'H:MM:SS' to seconds."""
        try:
            parts = ts.split(":")
            if len(parts) == 2:
                return int(parts[0]) * 60 + int(parts[1])
            elif len(parts) == 3:
                return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
            return 0
        except (ValueError, IndexError):
            return 0
    
    def index_video(
        self,
        result: Any,  # GeminiAnalysisResult
        channel: str = "undaodu",
    ) -> int:
        """
        Index all segments from a video analysis result.
        
        Args:
            result: GeminiAnalysisResult from video analyzer
            channel: Channel name for metadata
            
        Returns:
            Number of segments indexed
        """
        if not hasattr(result, 'segments') or not result.segments:
            logger.warning(f"[VIDEO-INDEX] No segments to index for {result.video_id}")
            return 0
        
        ids = []
        embeddings = []
        documents = []
        metadatas = []
        
        for seg in result.segments:
            seg_id = f"{result.video_id}_{seg.start_time.replace(':', '_')}"

            # Skip if already indexed
            try:
                existing = self.collection.get(ids=[seg_id])
                if existing and existing.get('ids'):
                    continue
            except Exception:
                pass

            # Build searchable content with entity correction
            content = correct_entities(seg.content)
            speaker = correct_entities(seg.speaker) if seg.speaker else None

            doc_content = content
            if speaker:
                doc_content = f"{speaker}: {content}"
            
            ids.append(seg_id)
            embeddings.append(self._get_embedding(doc_content))
            documents.append(doc_content)

            metadatas.append({
                "video_id": result.video_id,
                "title": correct_entities(result.title) if result.title else "",
                "channel": channel,
                "start_time": seg.start_time,
                "end_time": seg.end_time,
                "speaker": speaker or "",
                "topics": ",".join(seg.topics) if seg.topics else "",
                "segment_type": getattr(seg, 'segment_type', 'content'),
                "indexed_at": datetime.now().isoformat(),
            })
        
        if ids:
            self.collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas,
            )
            logger.info(f"[VIDEO-INDEX] Indexed {len(ids)} segments from {result.video_id}")
        
        return len(ids)
    
    def search(
        self,
        query: str,
        k: int = 5,
        channel: Optional[str] = None,
    ) -> List[VideoMatch]:
        """
        Search for video segments matching query.
        
        Args:
            query: Search query text
            k: Maximum number of results
            channel: Optional channel filter
            
        Returns:
            List of VideoMatch objects with deep links
        """
        if self.collection.count() == 0:
            logger.warning("[VIDEO-INDEX] No videos indexed yet")
            return []
        
        embedding = self._get_embedding(query)
        
        # Build filter if channel specified
        where_filter = None
        if channel:
            where_filter = {"channel": channel}
        
        try:
            results = self.collection.query(
                query_embeddings=[embedding],
                n_results=k,
                where=where_filter,
                include=["documents", "metadatas", "distances"],
            )
        except Exception as e:
            logger.error(f"[VIDEO-INDEX] Search failed: {e}")
            return []
        
        matches = []
        docs = results.get("documents", [[]])[0]
        metas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]
        
        for doc, meta, dist in zip(docs, metas, distances):
            # Convert distance to similarity (ChromaDB uses L2)
            similarity = max(0, 1 - (dist / 2))
            
            # Build deep link URL
            video_id = meta.get("video_id", "")
            start_time = meta.get("start_time", "0:00")
            start_seconds = self._timestamp_to_seconds(start_time)
            url = f"https://youtube.com/watch?v={video_id}&t={start_seconds}"
            
            matches.append(VideoMatch(
                video_id=video_id,
                title=meta.get("title", ""),
                channel=meta.get("channel", ""),
                start_time=start_time,
                end_time=meta.get("end_time", ""),
                content=doc,
                speaker=meta.get("speaker") or None,
                topics=meta.get("topics", "").split(",") if meta.get("topics") else [],
                similarity=similarity,
                url=url,
            ))
        
        logger.info(f"[VIDEO-INDEX] Found {len(matches)} matches for '{query[:30]}...'")
        return matches
    
    def index_from_json(
        self,
        json_path: str,
        channel: str = "undaodu",
    ) -> int:
        """
        Index video from a saved JSON file (gemini analyzer output).

        Args:
            json_path: Path to video index JSON file
            channel: Channel name

        Returns:
            Number of segments indexed
        """
        from dataclasses import dataclass

        @dataclass
        class SegmentProxy:
            start_time: str
            end_time: str
            content: str
            speaker: Optional[str] = None
            topics: List[str] = None
            segment_type: str = "content"

        @dataclass
        class ResultProxy:
            video_id: str
            title: str
            segments: List[SegmentProxy]

        try:
            with open(json_path, encoding="utf-8") as f:
                data = json.load(f)

            segments = []
            for seg in data.get("audio", {}).get("segments", []):
                # Convert seconds to MM:SS format
                start_sec = int(seg.get("start", 0))
                end_sec = int(seg.get("end", 0))
                start_time = f"{start_sec // 60}:{start_sec % 60:02d}"
                end_time = f"{end_sec // 60}:{end_sec % 60:02d}"

                segments.append(SegmentProxy(
                    start_time=start_time,
                    end_time=end_time,
                    content=seg.get("text", ""),
                    speaker=seg.get("speaker"),
                    topics=[],
                ))

            result = ResultProxy(
                video_id=data.get("video_id", ""),
                title=data.get("title", ""),
                segments=segments,
            )

            return self.index_video(result, channel=channel)

        except Exception as e:
            logger.error(f"[VIDEO-INDEX] Failed to index {json_path}: {e}")
            return 0

    def batch_index_channel(
        self,
        index_dir: str = "memory/video_index",
        channel: str = "undaodu",
    ) -> Dict[str, Any]:
        """
        Batch index all videos from a channel directory.

        Args:
            index_dir: Base directory for video indexes
            channel: Channel name

        Returns:
            Summary of indexing results
        """
        channel_dir = Path(index_dir) / channel
        if not channel_dir.exists():
            return {"error": f"Channel directory not found: {channel_dir}"}

        results = {
            "channel": channel,
            "videos_found": 0,
            "videos_indexed": 0,
            "segments_indexed": 0,
            "errors": [],
        }

        json_files = list(channel_dir.glob("*.json"))
        results["videos_found"] = len(json_files)

        for json_file in json_files:
            if json_file.stem in ["metadata", "config"]:
                continue

            try:
                count = self.index_from_json(str(json_file), channel=channel)
                if count > 0:
                    results["videos_indexed"] += 1
                    results["segments_indexed"] += count
                    logger.info(f"[VIDEO-INDEX] Indexed {json_file.stem}: {count} segments")
            except Exception as e:
                results["errors"].append(f"{json_file.stem}: {e}")

        logger.info(
            f"[VIDEO-INDEX] Batch complete: {results['videos_indexed']}/{results['videos_found']} videos, "
            f"{results['segments_indexed']} segments"
        )
        return results

    def get_stats(self) -> Dict[str, Any]:
        """Get index statistics."""
        try:
            count = self.collection.count()

            # Sample to get channel distribution
            sample = self.collection.get(limit=min(100, count), include=["metadatas"])
            channels = {}
            videos = set()
            for meta in sample.get("metadatas", []):
                ch = meta.get("channel", "unknown")
                channels[ch] = channels.get(ch, 0) + 1
                videos.add(meta.get("video_id", ""))

            return {
                "total_segments": count,
                "unique_videos": len(videos),
                "channels": channels,
                "collection": self.COLLECTION_NAME,
            }
        except Exception as e:
            return {"error": str(e)}


# =============================================================================
# Quick Test
# =============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    print("=" * 60)
    print("VIDEO CONTENT INDEX - Test")
    print("=" * 60)
    
    try:
        index = VideoContentIndex()
        stats = index.get_stats()
        print(f"\nIndex Stats: {stats}")
        
        if stats.get("total_segments", 0) > 0:
            print("\nTesting search...")
            matches = index.search("education", k=3)
            for m in matches:
                print(f"  [{m.start_time}] {m.content[:60]}...")
                print(f"    -> {m.url}")
        else:
            print("\nNo videos indexed yet. Run VideoIndexer first.")
            
    except Exception as e:
        print(f"Error: {e}")
