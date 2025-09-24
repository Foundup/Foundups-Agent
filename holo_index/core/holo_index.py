"""HoloIndex Core Search Engine - WSP 87 Compliant Module Structure

This module provides the core HoloIndex search functionality, extracted
from the monolithic cli.py to maintain WSP 87 size limits.

WSP Compliance: WSP 87 (Size Limits), WSP 49 (Module Structure), WSP 72 (Block Independence)
"""

from __future__ import annotations
import json
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

# Dependency bootstrap for this module
try:
    import chromadb
    from sentence_transformers import SentenceTransformer
except ImportError:
    print("Installing required dependencies...")
    import subprocess
    subprocess.check_call([__import__('sys').executable, "-m", "pip", "install", "chromadb", "sentence-transformers"])
    import chromadb
    from sentence_transformers import SentenceTransformer


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

    def _infer_cube_tag(self, *values: Any) -> Optional[str]:
        text = ' '.join(v for v in values if isinstance(v, str)).lower()
        if not text:
            return None
        if 'pqn' in text or 'phantom quantum' in text:
            return 'pqn'
        return None

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
            cube = self._infer_cube_tag(need, location)
            meta = {
                "need": need,
                "type": "code",
                "source": "NAVIGATION.py"
            }
            if cube:
                meta["cube"] = cube
            metadatas.append(meta)

        self.code_collection.add(ids=ids, embeddings=embeddings, documents=documents, metadatas=metadatas)
        print("[OK] Code index refreshed on SSD")

    def index_wsp_entries(self, paths: Optional[List[Path]] = None) -> None:
        from ..utils.helpers import DEFAULT_WSP_PATHS

        paths = paths or DEFAULT_WSP_PATHS
        files: List[Path] = []
        for base in paths:
            if base.exists():
                # Get all .md files but exclude node_modules and CHANGELOG files
                all_md_files = sorted(base.rglob("*.md"))
                filtered_files = [
                    f for f in all_md_files
                    if 'node_modules' not in str(f)
                    and 'CHANGELOG' not in f.name.upper()
                    and 'package-lock' not in f.name.lower()
                ]
                files.extend(filtered_files)
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
            cube = self._infer_cube_tag(title, summary, str(file_path))
            metadata = {
                "wsp": wsp_id,
                "title": title,
                "path": str(file_path),
                "summary": summary,
                "type": "wsp"
            }
            if cube:
                metadata["cube"] = cube
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
        start_time = __import__('time').time()

        code_hits = self._search_collection(self.code_collection, query, limit, kind="code")
        wsp_hits = self._search_collection(self.wsp_collection, query, limit, kind="wsp")

        warnings = self._generate_warnings(query)
        warnings.extend(self._warnings_from_wsp_hits(wsp_hits))
        warnings = self._dedupe(warnings)

        reminders = self._generate_context_reminders(query)
        reminders.extend(self._reminders_from_wsp_hits(wsp_hits))
        reminders = self._dedupe(reminders)

        elapsed = (__import__('time').time() - start_time) * 1000
        print(f"[PERF] Dual search completed in {elapsed:.1f}ms")

        cube_tags = sorted({hit.get('cube') for hit in code_hits + wsp_hits if hit.get('cube')})
        fmas_hint = self._should_show_fmas_hint(query, code_hits)

        return {
            "query": query,
            "code": code_hits,
            "wsps": wsp_hits,
            "warnings": warnings,
            "reminders": reminders,
            "cubes": cube_tags,
            "warnings_count": len(warnings),
            "reminders_count": len(reminders),
            "fmas_hint": fmas_hint,
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
                    "similarity": f"{similarity*100:.1f}%",
                    "cube": meta.get('cube')
                })
            else:
                formatted.append({
                    "wsp": meta.get('wsp'),
                    "title": meta.get('title'),
                    "summary": meta.get('summary'),
                    "path": meta.get('path'),
                    "similarity": f"{similarity*100:.1f}%",
                    "cube": meta.get('cube')
                })
        return formatted

    # --------- Warning & Reminder Generation --------- #

    def _generate_warnings(self, query: str) -> List[str]:
        from ..utils.helpers import VIOLATION_RULES
        warnings = []
        lower = query.lower()
        for rule in VIOLATION_RULES:
            if re.search(rule["pattern"], lower):
                warnings.append(f"[{rule['wsp']}] {rule['message']}")
        return warnings

    def _warnings_from_wsp_hits(self, wsp_hits: List[Dict[str, Any]]) -> List[str]:
        from ..utils.helpers import WSP_HINTS
        warnings = []
        for hit in wsp_hits:
            wsp_id = hit.get('wsp')
            if wsp_id in WSP_HINTS:
                warnings.append(f"[{wsp_id}] {WSP_HINTS[wsp_id]}")
        return warnings

    def _generate_context_reminders(self, query: str) -> List[str]:
        from ..utils.helpers import CONTEXT_WSP_MAP, WSP_HINTS
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

        start = __import__('time').time()
        with open(test_file, 'wb') as handle:
            handle.write(payload)
        write_time = __import__('time').time() - start
        write_speed = 10 / write_time if write_time else float('inf')

        start = __import__('time').time()
        with open(test_file, 'rb') as handle:
            _ = handle.read()
        read_time = __import__('time').time() - start
        read_speed = 10 / read_time if read_time else float('inf')

        try:
            test_file.unlink()
        except FileNotFoundError:
            pass

        print(f"[OK] Write speed: {write_speed:.1f} MB/s")
        print(f"[OK] Read speed:  {read_speed:.1f} MB/s")

        if self.code_collection.count() > 0:
            start = __import__('time').time()
            _ = self.search("test query", limit=1)
            elapsed = (__import__('time').time() - start) * 1000
            print(f"[PERF] Vector query time: {elapsed:.1f} ms")
        else:
            print("[WARN] Code collection empty; run --index-code first for vector benchmark")

    def _should_show_fmas_hint(self, query: str, code_hits: List[Dict[str, Any]]) -> bool:
        query_lower = query.lower()
        if "test" in query_lower:
            return True
        for hit in code_hits:
            need = (hit.get("need") or "").lower()
            if "test" in need:
                return True
        return False

    def check_module_exists(self, module_name: str) -> Dict[str, Any]:
        """
        WSP Compliance: Check if a module exists before code generation.
        This method should be called by 0102 agents before creating ANY new code.

        Args:
            module_name: Name of the module to check (e.g., "youtube_auth", "livechat")

        Returns:
            Dict containing:
            - exists: bool - Whether the module exists
            - path: str - Full path if exists
            - readme_exists: bool - Whether README.md exists
            - interface_exists: bool - Whether INTERFACE.md exists
            - tests_exist: bool - Whether tests directory exists
            - wsp_compliance: str - Basic compliance status
            - recommendation: str - What 0102 should do next
        """
        from pathlib import Path

        # Check all possible domains for the module
        domains = [
            "modules/ai_intelligence",
            "modules/communication",
            "modules/platform_integration",
            "modules/infrastructure",
            "modules/monitoring",
            "modules/development",
            "modules/foundups",
            "modules/gamification",
            "modules/blockchain"
        ]

        module_path = None
        for domain in domains:
            candidate_path = Path(domain) / module_name
            if candidate_path.exists() and candidate_path.is_dir():
                module_path = candidate_path
                break

        if not module_path:
            # Search in navigation entries for similar modules
            similar_modules = []
            for need, location in self.need_to.items():
                if module_name.lower() in need.lower() or module_name.lower() in location.lower():
                    # Extract module path from location
                    path_parts = location.split('/')
                    if len(path_parts) >= 3 and path_parts[0] == 'modules':
                        module_path_str = '/'.join(path_parts[:4])  # modules/domain/module
                        if module_path_str not in similar_modules:
                            similar_modules.append(module_path_str)

            return {
                "exists": False,
                "module_name": module_name,
                "similar_modules": similar_modules,
                "recommendation": f"🚫 MODULE '{module_name}' DOES NOT EXIST - DO NOT CREATE IT! " +
                                (f"Similar modules found: {', '.join(similar_modules)}. " if similar_modules else "") +
                                "ENHANCE EXISTING MODULES - DO NOT VIBECODE (See WSP_84_Module_Evolution). " +
                                "Use --search to find existing functionality FIRST before ANY code generation."
            }

        # Module exists - check compliance
        readme_exists = (module_path / "README.md").exists()
        interface_exists = (module_path / "INTERFACE.md").exists()
        roadmap_exists = (module_path / "ROADMAP.md").exists()
        modlog_exists = (module_path / "ModLog.md").exists()
        requirements_exists = (module_path / "requirements.txt").exists()
        tests_exist = (module_path / "tests").exists()
        memory_exists = (module_path / "memory").exists()

        compliance_score = sum([
            readme_exists, interface_exists, roadmap_exists,
            modlog_exists, requirements_exists, tests_exist, memory_exists
        ])

        wsp_compliance = "❌ NON-COMPLIANT" if compliance_score < 7 else "✅ COMPLIANT"

        # Check for health issues
        health_warnings = []
        if not tests_exist:
            health_warnings.append("Missing tests directory (WSP 49)")
        if not readme_exists:
            health_warnings.append("Missing README.md (WSP 22)")
        if not interface_exists:
            health_warnings.append("Missing INTERFACE.md (WSP 11)")

        return {
            "exists": True,
            "module_name": module_name,
            "path": str(module_path),
            "readme_exists": readme_exists,
            "interface_exists": interface_exists,
            "roadmap_exists": roadmap_exists,
            "modlog_exists": modlog_exists,
            "requirements_exists": requirements_exists,
            "tests_exist": tests_exist,
            "memory_exists": memory_exists,
            "wsp_compliance": wsp_compliance,
            "compliance_score": f"{compliance_score}/7",
            "health_warnings": health_warnings,
            "recommendation": f"Module '{module_name}' exists at {module_path}. " +
                            (f"WSP Compliance: {wsp_compliance}. " if wsp_compliance == "❌ NON-COMPLIANT" else "✅ WSP Compliant. ") +
                            ("MANDATORY: Read README.md and INTERFACE.md BEFORE making changes. " if readme_exists and interface_exists else "CRITICAL: Create missing documentation FIRST (WSP_22_Documentation). ")
        }
