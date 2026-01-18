# -*- coding: utf-8 -*-
"""
Vocabulary Indexer Extension for HoloIndex

Indexes channel vocabulary files (memory/vocabulary/*.json) into HoloIndex
for STT transcript correction using semantic search.

WSP Compliance: WSP 72 (Module Independence)
"""
import json
import logging
from pathlib import Path
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


def index_vocabulary(holo_index, project_root: Path = None) -> int:
    """
    Index vocabulary files into HoloIndex.
    
    Args:
        holo_index: HoloIndex instance with active client
        project_root: Root directory (defaults to holo_index.project_root)
        
    Returns:
        Number of terms indexed
    """
    if project_root is None:
        project_root = holo_index.project_root
    
    vocab_dir = project_root / "memory" / "vocabulary"
    
    if not vocab_dir.exists():
        logger.warning("[VOCAB-INDEX] No vocabulary directory found")
        return 0
    
    vocab_files = list(vocab_dir.glob("*.json"))
    if not vocab_files:
        logger.warning("[VOCAB-INDEX] No vocabulary files found")
        return 0
    
    logger.info(f"[VOCAB-INDEX] Indexing {len(vocab_files)} vocabulary files...")
    
    # Ensure collection exists
    try:
        vocabulary_collection = holo_index._ensure_collection("navigation_vocabulary")
    except:
        vocabulary_collection = holo_index._reset_collection("navigation_vocabulary")
    
    ids, embeddings, documents, metadatas = [], [], [], []
    
    for idx, vocab_file in enumerate(vocab_files, start=1):
        try:
            data = json.loads(vocab_file.read_text(encoding='utf-8'))
            channel = data.get('channel', vocab_file.stem)
            proper_nouns = data.get('proper_nouns', [])
            mishearings = data.get('common_mishearings', {})
            
            # Index proper nouns
            for noun in proper_nouns:
                doc_id = f"vocab_{idx}_{len(ids)}"
                doc_payload = f"Proper noun: {noun} (Channel: {channel})"
                ids.append(doc_id)
                embeddings.append(holo_index._get_embedding(doc_payload))
                documents.append(doc_payload)
                metadatas.append({
                    "term": noun,
                    "channel": channel,
                    "type": "proper_noun",
                    "path": str(vocab_file),
                    "priority": 8
                })
            
            # Index mishearings for correction lookup
            for misheard, correct in mishearings.items():
                doc_id = f"vocab_{idx}_{len(ids)}"
                doc_payload = f"STT correction: '{misheard}' -> '{correct}'"
                ids.append(doc_id)
                embeddings.append(holo_index._get_embedding(doc_payload))
                documents.append(doc_payload)
                metadatas.append({
                    "misheard": misheard,
                    "correct": correct,
                    "channel": channel,
                    "type": "mishearing",
                    "path": str(vocab_file),
                    "priority": 9
                })
                
        except Exception as e:
            logger.warning(f"[VOCAB-INDEX] Failed to parse {vocab_file}: {e}")
            continue
    
    if embeddings:
        vocabulary_collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )
        logger.info(f"[VOCAB-INDEX] Indexed {len(embeddings)} vocabulary terms")
    
    return len(embeddings)


def search_vocabulary(holo_index, query: str, limit: int = 5) -> List[Dict[str, Any]]:
    """
    Search vocabulary collection for corrections.
    
    Args:
        holo_index: HoloIndex instance
        query: Search query (e.g., misheard term)
        limit: Max results
        
    Returns:
        List of matching vocabulary entries
    """
    try:
        vocabulary_collection = holo_index._ensure_collection("navigation_vocabulary")
        embedding = holo_index._get_embedding(query)
        
        results = vocabulary_collection.query(
            query_embeddings=[embedding],
            n_results=limit,
            include=["documents", "metadatas"]
        )
        
        hits = []
        docs = results.get("documents", [[]])[0]
        metas = results.get("metadatas", [[]])[0]
        
        for doc, meta in zip(docs, metas):
            hits.append({
                "document": doc,
                "term": meta.get("term") or meta.get("correct"),
                "type": meta.get("type"),
                "channel": meta.get("channel"),
                "misheard": meta.get("misheard"),
            })
        
        return hits
        
    except Exception as e:
        logger.error(f"[VOCAB-INDEX] Search failed: {e}")
        return []
