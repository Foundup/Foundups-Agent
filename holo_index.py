#!/usr/bin/env python3
"""
HoloIndex - Dual Semantic Navigation for Code + WSP
Leverages the E: SSD for ultra-fast, persistent search

WSP 87 Compliant - Prevents vibecoding by pairing code discovery with protocol guidance
"""

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

# SSD locations (Phase 1 requirement)
os.environ.setdefault('CHROMADB_DATA_PATH', 'E:/HoloIndex/vectors')
os.environ.setdefault('SENTENCE_TRANSFORMERS_HOME', 'E:/HoloIndex/models')
os.environ.setdefault('HOLO_CACHE_PATH', 'E:/HoloIndex/cache')

# Dependency bootstrap
try:
    import chromadb
    from sentence_transformers import SentenceTransformer
except ImportError:
    print("Installing required dependencies...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "chromadb", "sentence-transformers"])
    import chromadb
    from sentence_transformers import SentenceTransformer

# -------------------- Heuristic Configuration -------------------- #

VIOLATION_RULES: List[Dict[str, str]] = [
    {
        "pattern": r"\benhanced\b|\benhanced_",
        "wsp": "WSP 84",
        "message": "WSP 84: evolve existing modules; never create enhanced_* duplicates."
    },
    {
        "pattern": r"create\s+new",
        "wsp": "WSP 50",
        "message": "WSP 50: run pre-action verification before starting new code."
    },
    {
        "pattern": r"rename|naming",
        "wsp": "WSP 57",
        "message": "WSP 57: verify naming coherence before renaming components."
    },
]

CONTEXT_WSP_MAP: Dict[str, List[str]] = {
    "document": ["WSP 22", "WSP 83"],
    "modlog": ["WSP 22"],
    "test": ["WSP 5", "WSP 6"],
    "structure": ["WSP 49"],
    "naming": ["WSP 57"],
    "token": ["WSP 75"],
    "create": ["WSP 50", "WSP 84"],
}

WSP_HINTS: Dict[str, str] = {
    "WSP 22": "Keep module documentation and ModLogs synchronized.",
    "WSP 49": "Follow module directory scaffolding (src/tests/memory/docs).",
    "WSP 50": "Log intent in pre-action journal before coding.",
    "WSP 57": "Maintain naming coherence across files and identifiers.",
    "WSP 75": "Track effort in tokens, not wall-clock minutes.",
    "WSP 84": "Evolve existing modules instead of cloning new versions.",
    "WSP 87": "Consult navigation assets before writing new code.",
}

DEFAULT_WSP_PATHS = [Path("WSP_framework/src"), Path("WSP_knowledge/docs")]

# -------------------- HoloIndex Implementation -------------------- #

class HoloIndex:
    """Dual semantic index spanning NAVIGATION entries and WSP protocols."""

    def __init__(self, ssd_path: str = "E:/HoloIndex") -> None:
        print(f"[INIT] Initializing HoloIndex on SSD: {ssd_path}")
        self.ssd_path = Path(ssd_path)
        self.vector_path = self.ssd_path / "vectors"
        self.cache_path = self.ssd_path / "cache"
        self.models_path = self.ssd_path / "models"
        self.indexes_path = self.ssd_path / "indexes"
        for path in [self.vector_path, self.cache_path, self.models_path, self.indexes_path]:
            path.mkdir(parents=True, exist_ok=True)

        print("[INFO] Setting up persistent ChromaDB collections...")
        self.client = chromadb.PersistentClient(path=str(self.vector_path))
        self.code_collection = self._ensure_collection("navigation_code")
        self.wsp_collection = self._ensure_collection("navigation_wsp")

        print("[MODEL] Loading sentence transformer (cached on SSD)...")
        os.environ['SENTENCE_TRANSFORMERS_HOME'] = str(self.models_path)
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

        self.need_to: Dict[str, str] = {}
        self.wsp_summary: Dict[str, Dict[str, str]] = {}
        self.wsp_summary_file = self.indexes_path / "wsp_summary.json"

        self._load_wsp_summary()
        self._load_navigation()

    # --------- Collection Helpers --------- #

    def _ensure_collection(self, name: str):
        try:
            return self.client.get_collection(name)
        except Exception:
            return self.client.create_collection(name)

    def _reset_collection(self, name: str):
        try:
            self.client.delete_collection(name)
        except Exception:
            pass
        return self.client.create_collection(name)

    # --------- Data Loading --------- #

    def _load_navigation(self) -> None:
        nav_path = Path("NAVIGATION.py")
        if not nav_path.exists():
            print("[WARN] NAVIGATION.py not found")
            return

        import ast
        print("[LOAD] Loading NEED_TO map from NAVIGATION.py...")
        tree = ast.parse(nav_path.read_text(encoding='utf-8-sig'))
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == "NEED_TO":
                        self.need_to = ast.literal_eval(node.value)
                        print(f"[OK] Loaded {len(self.need_to)} navigation entries")
                        return
        print("[WARN] NEED_TO dictionary not found in NAVIGATION.py")

    def _load_wsp_summary(self) -> None:
        if self.wsp_summary_file.exists():
            try:
                self.wsp_summary = json.loads(self.wsp_summary_file.read_text(encoding='utf-8'))
                print(f"[OK] Loaded {len(self.wsp_summary)} WSP summaries")
            except json.JSONDecodeError:
                print("[WARN] WSP summary cache corrupted; rebuilding will overwrite on next index")
                self.wsp_summary = {}

    # --------- Indexing --------- #

    def index_code_entries(self) -> None:
        if not self.need_to:
            print("[WARN] No NEED_TO entries to index")
            return

        print(f"[INDEX] Indexing {len(self.need_to)} code navigation entries...")
        self.code_collection = self._reset_collection("navigation_code")

        ids, embeddings, documents, metadatas = [], [], [], []
        for i, (need, location) in enumerate(self.need_to.items(), start=1):
            ids.append(f"code_{i}")
            embeddings.append(self.model.encode(need).tolist())
            documents.append(location)
            metadatas.append({
                "need": need,
                "type": "code",
                "source": "NAVIGATION.py"
            })

        self.code_collection.add(ids=ids, embeddings=embeddings, documents=documents, metadatas=metadatas)
        print("[OK] Code index refreshed on SSD")

    def index_wsp_entries(self, paths: Optional[List[Path]] = None) -> None:
        paths = paths or DEFAULT_WSP_PATHS
        files: List[Path] = []
        for base in paths:
            if base.exists():
                files.extend(sorted(base.rglob("*.md")))
        if not files:
            print("[WARN] No WSP documents found to index")
            return

        print(f"[INDEX] Indexing {len(files)} WSP documents...")
        self.wsp_collection = self._reset_collection("navigation_wsp")

        ids, embeddings, documents, metadatas = [], [], [], []
        summary_cache: Dict[str, Dict[str, str]] = {}

        for idx, file_path in enumerate(files, start=1):
            text = file_path.read_text(encoding='utf-8', errors='ignore')
            lines = [line.strip() for line in text.splitlines() if line.strip()]
            if not lines:
                continue

            title = lines[0].lstrip('# ')
            summary = ' '.join(lines[1:6])[:400]
            wsp_id = self._extract_wsp_id(file_path.name, title)
            doc_payload = f"{title}\n{summary}"

            ids.append(f"wsp_{idx}")
            embeddings.append(self.model.encode(doc_payload).tolist())
            documents.append(doc_payload)
            metadata = {
                "wsp": wsp_id,
                "title": title,
                "path": str(file_path),
                "summary": summary,
                "type": "wsp"
            }
            metadatas.append(metadata)
            summary_cache[wsp_id] = {
                "title": title,
                "path": str(file_path),
                "summary": summary
            }

        if embeddings:
            self.wsp_collection.add(ids=ids, embeddings=embeddings, documents=documents, metadatas=metadatas)
            self.wsp_summary = summary_cache
            self.wsp_summary_file.write_text(json.dumps(self.wsp_summary, indent=2), encoding='utf-8')
            print("[OK] WSP index refreshed and summary cache saved")
        else:
            print("[WARN] No WSP entries were indexed (empty content)")

    def _extract_wsp_id(self, filename: str, title: str) -> str:
        match = re.search(r"WSP[_-]?(\d+)", filename)
        if match:
            return f"WSP {match.group(1)}"
        match = re.search(r"WSP\s*(\d+)", title, re.IGNORECASE)
        if match:
            return f"WSP {match.group(1)}"
        return title.split()[0] if title else "WSP"

    # --------- Search --------- #

    def search(self, query: str, limit: int = 5) -> Dict[str, Any]:
        print(f"\n[SEARCH] Searching for: '{query}'")
        start_time = time.time()

        code_hits = self._search_collection(self.code_collection, query, limit, kind="code")
        wsp_hits = self._search_collection(self.wsp_collection, query, limit, kind="wsp")

        warnings = self._generate_warnings(query)
        warnings.extend(self._warnings_from_wsp_hits(wsp_hits))
        warnings = self._dedupe(warnings)

        reminders = self._generate_context_reminders(query)
        reminders.extend(self._reminders_from_wsp_hits(wsp_hits))
        reminders = self._dedupe(reminders)

        elapsed = (time.time() - start_time) * 1000
        print(f"[PERF] Dual search completed in {elapsed:.1f}ms")

        return {
            "query": query,
            "code": code_hits,
            "wsps": wsp_hits,
            "warnings": warnings,
            "reminders": reminders,
            "elapsed_ms": f"{elapsed:.1f}"
        }

    def _search_collection(self, collection, query: str, limit: int, kind: str) -> List[Dict[str, Any]]:
        if collection.count() == 0:
            return []

        embedding = self.model.encode(query).tolist()
        results = collection.query(query_embeddings=[embedding], n_results=limit)

        formatted: List[Dict[str, Any]] = []
        docs = results.get('documents', [[]])[0]
        metas = results.get('metadatas', [[]])[0]
        dists = results.get('distances', [[]])[0]

        for doc, meta, distance in zip(docs, metas, dists):
            similarity = max(0.0, 1 - float(distance))
            if kind == "code":
                formatted.append({
                    "need": meta.get('need'),
                    "location": doc,
                    "similarity": f"{similarity*100:.1f}%"
                })
            else:
                formatted.append({
                    "wsp": meta.get('wsp'),
                    "title": meta.get('title'),
                    "summary": meta.get('summary'),
                    "path": meta.get('path'),
                    "similarity": f"{similarity*100:.1f}%"
                })
        return formatted

    # --------- Warning & Reminder Generation --------- #

    def _generate_warnings(self, query: str) -> List[str]:
        warnings = []
        lower = query.lower()
        for rule in VIOLATION_RULES:
            if re.search(rule["pattern"], lower):
                warnings.append(f"[{rule['wsp']}] {rule['message']}")
        return warnings

    def _warnings_from_wsp_hits(self, wsp_hits: List[Dict[str, Any]]) -> List[str]:
        warnings = []
        for hit in wsp_hits:
            wsp_id = hit.get('wsp')
            if wsp_id in WSP_HINTS:
                warnings.append(f"[{wsp_id}] {WSP_HINTS[wsp_id]}")
        return warnings

    def _generate_context_reminders(self, query: str) -> List[str]:
        reminders = []
        lower = query.lower()
        for keyword, wsps in CONTEXT_WSP_MAP.items():
            if keyword in lower:
                for wsp in wsps:
                    message = WSP_HINTS.get(wsp, f"Review {wsp} guidance")
                    reminders.append(f"{wsp}: {message}")
        return reminders

    def _reminders_from_wsp_hits(self, wsp_hits: List[Dict[str, Any]]) -> List[str]:
        reminders = []
        for hit in wsp_hits[:3]:
            wsp_id = hit.get('wsp')
            title = hit.get('title')
            if wsp_id and title:
                reminders.append(f"{wsp_id}: {title}")
        return reminders

    @staticmethod
    def _dedupe(items: List[str]) -> List[str]:
        seen = set()
        deduped = []
        for item in items:
            if item and item not in seen:
                seen.add(item)
                deduped.append(item)
        return deduped

    # --------- CLI Helpers --------- #

    def benchmark_ssd(self) -> None:
        """Benchmark SSD throughput and vector search latency."""
        print("\n[INFO] Benchmarking SSD performance...")
        test_file = self.cache_path / "benchmark.tmp"
        payload = b"x" * (10 * 1024 * 1024)

        start = time.time()
        with open(test_file, 'wb') as handle:
            handle.write(payload)
        write_time = time.time() - start
        write_speed = 10 / write_time if write_time else float('inf')

        start = time.time()
        with open(test_file, 'rb') as handle:
            _ = handle.read()
        read_time = time.time() - start
        read_speed = 10 / read_time if read_time else float('inf')

        try:
            test_file.unlink()
        except FileNotFoundError:
            pass

        print(f"[OK] Write speed: {write_speed:.1f} MB/s")
        print(f"[OK] Read speed:  {read_speed:.1f} MB/s")

        if self.code_collection.count() > 0:
            start = time.time()
            _ = self.search("test query", limit=1)
            elapsed = (time.time() - start) * 1000
            print(f"[PERF] Vector query time: {elapsed:.1f} ms")
        else:
            print("[WARN] Code collection empty; run --index-code first for vector benchmark")

    def display_results(self, result: Dict[str, Any]) -> None:
        code_hits = result.get('code', [])
        wsp_hits = result.get('wsps', [])
        warnings = result.get('warnings', [])
        reminders = result.get('reminders', [])

        print("\n[CODE] Code Results:")
        if not code_hits:
            print("  (no matching code entries)")
        for idx, hit in enumerate(code_hits, start=1):
            print(f"  {idx}. [{hit['similarity']}] {hit['need']}")
            print(f"     -> {hit['location']}")

        print("\n[WSP] WSP Guidance:")
        if not wsp_hits:
            print("  (no relevant WSP protocols)")
        for idx, hit in enumerate(wsp_hits, start=1):
            print(f"  {idx}. [{hit['similarity']}] {hit['wsp']} - {hit['title']}")
            if hit.get('summary'):
                print(f"     " + hit['summary'][:120] + ('...' if len(hit['summary']) > 120 else ''))
            print(f"     -> {hit['path']}")

        print("\n[WARN] Warnings:")
        if not warnings:
            print("  (no immediate WSP violations detected)")
        for warning in warnings:
            print(f"  - {warning}")

        print("\n[REM] Reminders:")
        if not reminders:
            print("  (no additional reminders)")
        for reminder in reminders:
            print(f"  - {reminder}")

# -------------------- CLI Entry Point -------------------- #

def main() -> None:
    parser = argparse.ArgumentParser(description="HoloIndex - Semantic Navigation with WSP guardrails")
    parser.add_argument('--index', action='store_true', help='Index code + WSP (backward compatible shorthand)')
    parser.add_argument('--index-code', action='store_true', help='Index NAVIGATION.py entries only')
    parser.add_argument('--index-wsp', action='store_true', help='Index WSP documentation only')
    parser.add_argument('--index-all', action='store_true', help='Index both code and WSP documents')
    parser.add_argument('--wsp-path', nargs='*', help='Additional WSP directories to include in the index')
    parser.add_argument('--search', type=str, help='Search for code + WSP guidance')
    parser.add_argument('--limit', type=int, default=5, help='Number of results per category (default: 5)')
    parser.add_argument('--benchmark', action='store_true', help='Benchmark SSD performance')
    parser.add_argument('--ssd', type=str, default='E:/HoloIndex', help='SSD base path (default: E:/HoloIndex)')

    args = parser.parse_args()
    holo = HoloIndex(ssd_path=args.ssd)

    index_code = args.index_code or args.index or args.index_all
    index_wsp = args.index_wsp or args.index or args.index_all

    if index_code:
        holo.index_code_entries()
    if index_wsp:
        wsp_dirs = [Path(p) for p in args.wsp_path] if args.wsp_path else None
        holo.index_wsp_entries(paths=wsp_dirs)

    if args.search:
        results = holo.search(args.search, limit=args.limit)
        holo.display_results(results)

    if args.benchmark:
        holo.benchmark_ssd()

    if not any([index_code, index_wsp, args.search, args.benchmark]):
        print("\n[USAGE] Usage:")
        print("  python holo_index.py --index-all             # Index NAVIGATION + WSP")
        print("  python holo_index.py --index-code            # Index NAVIGATION only")
        print("  python holo_index.py --index-wsp             # Index WSP docs")
        print("  python holo_index.py --search 'query'        # Search code + WSP guidance")
        print("  python holo_index.py --search 'query' --limit 3")
        print("  python holo_index.py --benchmark             # Test SSD performance")

if __name__ == "__main__":
    main()



