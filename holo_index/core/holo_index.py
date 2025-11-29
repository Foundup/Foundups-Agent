# -*- coding: utf-8 -*-
from __future__ import annotations

import sys
import io


"""HoloIndex Core Search Engine - WSP 87 Compliant Module Structure

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

This module provides the core HoloIndex search functionality, extracted
from the monolithic cli.py to maintain WSP 87 size limits.

WSP Compliance: WSP 87 (Size Limits), WSP 49 (Module Structure), WSP 72 (Block Independence)
"""

import json
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime
import time

# Dependency bootstrap for this module
try:
    import chromadb
except ImportError:
    print("Installing required dependencies...")
    import subprocess
    subprocess.check_call([__import__('sys').executable, "-m", "pip", "install", "chromadb"])
    import chromadb

# Lazy load sentence_transformers to prevent crash on import
SentenceTransformer = None

# Optional imports (disabled for stability)
AGENT_LOGGER_AVAILABLE = False
BREADCRUMB_AVAILABLE = False
BreadcrumbTracer = None
CIRCUIT_BREAKER_AVAILABLE = False
circuit_manager = None
CircuitBreakerOpenError = Exception


class HoloIndex:
    """Dual semantic index spanning NAVIGATION entries and WSP protocols."""

    def _log_agent_action(self, message: str, action_tag: str = "0102"):
        """Real-time logging for multi-agent coordination - allows other 0102 agents to follow."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        if not getattr(self, "quiet", False):
            print(f"[{timestamp}] [HOLO-{action_tag}] {message}")

        # Also log to shared file for other agents to follow
        try:
            log_file = Path("holo_index/logs/agent_activity.log")
            log_file.parent.mkdir(exist_ok=True)
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(f"[{timestamp}] [HOLO-{action_tag}] {message}\n")
        except:
            pass  # Don't break if logging fails

    def _announce_breadcrumb_trail(self):
        """Announce breadcrumb availability discreetly."""
        if self._breadcrumb_hint_shown:
            return
        if not hasattr(self, 'breadcrumb_tracer') or not self.breadcrumb_tracer:
            return
        agents = self.breadcrumb_tracer.get_recent_agents()
        if not agents:
            return
        agent_list = ", ".join(agents)
        hint = f"[BREAD] breadcrumbs available (agents: {agent_list}). Run python -m holo_index.utils.log_follower to follow."
        print(f"[{datetime.now().strftime('%H:%M:%S')}] [BREADCRUMB] {hint}")
        self._breadcrumb_hint_shown = True

    def __init__(self, ssd_path: str = "E:/HoloIndex", quiet: bool = False) -> None:
        """
        0102: Initialize HoloIndex with WSP-compliant architecture.
        
        Args:
            ssd_path: Path to SSD for persistent storage
            quiet: Suppress initialization logs
        """
        self.quiet = quiet
        self._log_agent_action(f"Initializing HoloIndex on SSD: {ssd_path}", "INIT")

        # Persistent storage layout (mirrors pre-rebuild behaviour)
        self.project_root = Path(__file__).parent.parent.parent
        self.ssd_path = Path(ssd_path)
        self.vector_path = self.ssd_path / "vectors"
        self.cache_path = self.ssd_path / "cache"
        self.models_path = self.ssd_path / "models"
        self.indexes_path = self.ssd_path / "indexes"
        for path in [self.vector_path, self.cache_path, self.models_path, self.indexes_path]:
            path.mkdir(parents=True, exist_ok=True)

        self._log_agent_action("Setting up persistent ChromaDB collections...", "INFO")
        self.client = chromadb.PersistentClient(path=str(self.vector_path))
        self.code_collection = self._ensure_collection("navigation_code")
        self.wsp_collection = self._ensure_collection("navigation_wsp")

        self._log_agent_action("Loading sentence transformer (cached on SSD)...", "MODEL")
        os.environ['SENTENCE_TRANSFORMERS_HOME'] = str(self.models_path)
        
        global SentenceTransformer
        if SentenceTransformer is None:
            try:
                from sentence_transformers import SentenceTransformer
            except Exception as e:
                self._log_agent_action(f"Failed to import SentenceTransformer: {e}", "ERROR")
                SentenceTransformer = None

        if SentenceTransformer:
            try:
                self.model = SentenceTransformer('all-MiniLM-L6-v2')
            except Exception as e:
                self._log_agent_action(f"Failed to load model: {e}", "ERROR")
                self.model = None
        else:
            self.model = None

        self.need_to: Dict[str, str] = {}
        self.wsp_summary: Dict[str, Dict[str, str]] = {}
        self.wsp_summary_file = self.indexes_path / "wsp_summary.json"
        self._ts_entity_cache: Dict[str, Dict[str, Any]] = {}
        self._breadcrumb_hint_shown: bool = False
        self.breadcrumb_tracer = None

        # Load cached metadata and navigation pointers
        self._load_wsp_summary()
        self._load_navigation()

        # Initialize breadcrumb tracer for multi-agent collaboration
        if BREADCRUMB_AVAILABLE:
            try:
                self.breadcrumb_tracer = BreadcrumbTracer()
                self._log_agent_action("Breadcrumb tracer initialized for multi-agent discovery sharing", "INFO")
            except Exception as e:
                self._log_agent_action(f"Breadcrumb tracer initialization failed: {e}", "WARN")
                self.breadcrumb_tracer = None  # Ensure it's None on failure
        else:
            self.breadcrumb_tracer = None  # Ensure it's always defined

    def get_code_entry_count(self) -> int:
        """Get count of indexed code entries."""
        try:
            return self.code_collection.count()
        except:
            return 0

    def get_wsp_entry_count(self) -> int:
        """Get count of indexed WSP entries."""
        try:
            return self.wsp_collection.count()
        except:
            return 0

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
            self._log_agent_action("NAVIGATION.py not found", "WARN")
            return

        import ast
        self._log_agent_action("Loading NEED_TO map from NAVIGATION.py...", "LOAD")
        tree = ast.parse(nav_path.read_text(encoding='utf-8-sig'))
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == "NEED_TO":
                        self.need_to = ast.literal_eval(node.value)
                        self._log_agent_action(f"Loaded {len(self.need_to)} navigation entries", "OK")
                        return
        self._log_agent_action("NEED_TO dictionary not found in NAVIGATION.py", "WARN")

    def _load_wsp_summary(self) -> None:
        if self.wsp_summary_file.exists():
            try:
                self.wsp_summary = json.loads(self.wsp_summary_file.read_text(encoding='utf-8'))
                self._log_agent_action(f"Loaded {len(self.wsp_summary)} WSP summaries", "OK")
            except json.JSONDecodeError:
                self._log_agent_action("WSP summary cache corrupted; rebuilding will overwrite on next index", "WARN")
                self.wsp_summary = {}

    def _get_embedding(self, text: str) -> List[float]:
        """Generate embedding or return dummy vector if model unavailable."""
        if self.model:
            return self.model.encode(text).tolist()
        # Return 384-dim zero vector (matches all-MiniLM-L6-v2)
        return [0.0] * 384

    # --------- Indexing --------- #

    def index_code_entries(self) -> None:
        if not self.need_to:
            self._log_agent_action("No NEED_TO entries to index", "WARN")
            return

        self._log_agent_action(f"Indexing {len(self.need_to)} code navigation entries...", "INDEX")
        self.code_collection = self._reset_collection("navigation_code")

        ids, embeddings, documents, metadatas = [], [], [], []
        for i, (need, location) in enumerate(self.need_to.items(), start=1):
            ids.append(f"code_{i}")
            embeddings.append(self._get_embedding(need))
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
        self._log_agent_action("Code index refreshed on SSD", "OK")

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
            self._log_agent_action("No WSP documents found to index", "WARN")
            return

        self._log_agent_action(f"Indexing {len(files)} WSP documents...", "INDEX")
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
            doc_type = self._classify_document_type(file_path, title, lines)
            doc_payload = f"{title}\n{summary}"

            ids.append(f"wsp_{idx}")
            embeddings.append(self._get_embedding(doc_payload))
            documents.append(doc_payload)
            cube = self._infer_cube_tag(title, summary, str(file_path))
            metadata = {
                "wsp": wsp_id,
                "title": title,
                "path": str(file_path),
                "summary": summary,
                "type": doc_type,  # <- Enhanced document classification
                "priority": self._calculate_document_priority(doc_type, file_path)  # <- Priority scoring
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

    def _classify_document_type(self, file_path: Path, title: str, lines: List[str]) -> str:
        """
        Classify document type based on filename, path, and content patterns.

        Returns one of:
        - wsp_protocol: Official WSP protocol documents
        - module_readme: Module README.md files
        - roadmap: ROADMAP.md files
        - interface: INTERFACE.md files
        - modlog: ModLog.md files
        - documentation: General documentation in docs/ folders
        - other: Unclassified documents
        """
        filename = file_path.name.lower()
        path_str = str(file_path).lower()

        # WSP Protocol documents
        if filename.startswith('wsp') and filename.endswith('.md'):
            return "wsp_protocol"

        # Module structure files
        if filename == 'readme.md':
            # Check if it's in a module directory (has src/, tests/, etc.)
            parent_dir = file_path.parent
            if any((parent_dir / d).exists() for d in ['src', 'tests', 'docs']):
                return "module_readme"
            return "readme"

        if filename == 'roadmap.md':
            return "roadmap"

        if filename == 'interface.md':
            return "interface"

        if filename == 'modlog.md':
            return "modlog"

        # Documentation in docs/ folders
        if 'docs/' in path_str or 'docs\\' in path_str:
            return "documentation"

        # Module test documentation
        if 'test' in filename and 'readme' in filename:
            return "test_documentation"

        return "other"

    def _calculate_document_priority(self, doc_type: str, file_path: Path) -> int:
        """
        Calculate document priority for search ranking (higher = more important).

        Priority scale: 1-10 (10 = highest priority)
        """
        priority_map = {
            "wsp_protocol": 10,      # Core protocols - highest priority
            "interface": 9,          # API documentation - very important
            "module_readme": 8,      # Module overviews - important for discovery
            "documentation": 7,      # Technical docs - good for detailed info
            "roadmap": 6,            # Planning docs - useful for context
            "modlog": 5,             # Change logs - useful for history
            "readme": 4,             # General READMEs - baseline
            "test_documentation": 3, # Test docs - lower priority
            "other": 2               # Everything else - lowest
        }

        base_priority = priority_map.get(doc_type, 2)

        # Boost priority for certain paths
        path_str = str(file_path).lower()
        if 'wsp_framework' in path_str:
            base_priority += 1  # Framework docs are more important
        elif 'modules/' in path_str and 'platform_integration' in path_str:
            base_priority += 1  # Platform modules are key

        return min(base_priority, 10)  # Cap at 10

    def _extract_wsp_id(self, filename: str, title: str) -> str:
        match = re.search(r"WSP[_-]?(\d+)", filename)
        if match:
            return f"WSP {match.group(1)}"
        match = re.search(r"WSP\s*(\d+)", title, re.IGNORECASE)
        if match:
            return f"WSP {match.group(1)}"
        return title.split()[0] if title else "WSP"

    # --------- Search --------- #

    def search(self, query: str, limit: int = 10, doc_type_filter: str = "all") -> Dict[str, Any]:
        """
        0102: Enhanced search with AST preview extraction for TypeScript/JSX files
        
        Args:
            query: Search query string
            limit: Maximum number of results to return
            doc_type_filter: Filter by document type ('code', 'wsp', 'all')
            
        Returns:
            Dictionary with legacy keys ('code', 'wsps') and modern keys
            ('code_hits', 'wsp_hits') plus metadata for telemetry.
        """
        try:
            # Log search initiation
            self._log_agent_action(f"Searching: '{query}' (limit={limit}, type={doc_type_filter})")
            
            # Perform dual search
            code_hits = []
            wsp_hits = []
            
            # Search code index if requested
            if doc_type_filter in ["code", "all"]:
                code_results = self._search_collection(self.code_collection, query, limit, kind="code")
                # 0102: Enhance with AST previews
                code_hits = self._enhance_code_results_with_previews(code_results)
                
            # Search WSP index if requested  
            if doc_type_filter in ["wsp", "all"]:
                wsp_hits = self._search_collection(self.wsp_collection, query, limit, kind="wsp", doc_type_filter=doc_type_filter)
            
            # Log completion
            self._log_agent_action(f"Search complete: {len(code_hits)} code, {len(wsp_hits)} WSP")

            # Backward-compatible payload for CLI/Qwen integrations
            payload = {
                'code_hits': code_hits,
                'wsp_hits': wsp_hits,
                'code': code_hits,   # legacy key expected by throttler + advisors
                'wsps': wsp_hits,    # legacy key expected by throttler + advisors
                'metadata': {
                    'query': query,
                    'code_count': len(code_hits),
                    'wsp_count': len(wsp_hits),
                    'timestamp': datetime.now().isoformat()
                }
            }
            return payload
            
        except Exception as e:
            self._log_agent_action(f"Search error: {str(e)}", "ERROR")
            return {
                'code_hits': [],
                'wsp_hits': [],
                'code': [],
                'wsps': [],
                'metadata': {'error': str(e)}
            }

    def _notify_holodae_search(self):
        """Notify HoloDAE of recent search activity for agent attribution."""
        try:
            # Try to find and update HoloDAE instance
            import sys
            for module_name, module in sys.modules.items():
                if module_name.startswith('holo_index.qwen_advisor.autonomous_holodae'):
                    if hasattr(module, 'AutonomousHoloDAE'):
                        # This is a simple way to notify - in a real system this would be more robust
                        # For now, we'll use a file-based communication
                        try:
                            with open("holo_index/.holodae_search_signal", "w") as f:
                                f.write(str(time.time()))
                        except:
                            pass
                    break
        except:
            pass  # Don't fail if notification fails

    def _search_collection(self, collection, query: str, limit: int, kind: str, doc_type_filter: str = "all") -> List[Dict[str, Any]]:
        if collection.count() == 0:
            return []

        if self.model is None:
            self._log_agent_action("Embedding model not available - attempting keyword search via ChromaDB", "WARN")
            try:
                # Try letting ChromaDB handle embedding or use simple text matching if available
                results = collection.query(query_texts=[query], n_results=limit)
            except Exception as e:
                self._log_agent_action(f"Keyword search failed: {e}", "ERROR")
                return []
        else:
            embedding = self.model.encode(query).tolist()
            results = collection.query(query_embeddings=[embedding], n_results=limit)

        formatted: List[Dict[str, Any]] = []
        docs = results.get('documents', [[]])[0]
        metas = results.get('metadatas', [[]])[0]
        dists = results.get('distances', [[]])[0]

        # Collect all results first for filtering and ranking
        raw_results = []
        for doc, meta, distance in zip(docs, metas, dists):
            similarity = max(0.0, 1 - float(distance))
            doc_type = meta.get('type', 'other')
            priority = meta.get('priority', 1)

            # Hybrid keyword score (title/path/summary lightweight boosts)
            keyword_score = 0.0
            ql = query.lower()
            title = (meta.get('title') or '').lower()
            path = (meta.get('path') or '').lower()
            summary = (meta.get('summary') or '').lower()
            for token in set(ql.split()):
                if not token:
                    continue
                if token in title:
                    keyword_score += 2.0
                if token in path:
                    keyword_score += 1.0
                if token in summary:
                    keyword_score += 0.5

            # Apply document type filtering
            if doc_type_filter != "all" and doc_type != doc_type_filter:
                continue

            if kind == "code":
                result = {
                    "need": meta.get('need'),
                    "location": doc,
                    "similarity": f"{similarity*100:.1f}%",
                    "cube": meta.get('cube'),
                    "type": doc_type,
                    "priority": priority,
                    "_sort_key": (0.5 * priority + 0.3 * similarity + 0.2 * keyword_score, similarity, priority)
                }
            else:
                result = {
                    "wsp": meta.get('wsp'),
                    "title": meta.get('title'),
                    "summary": meta.get('summary'),
                    "path": meta.get('path'),
                    "similarity": f"{similarity*100:.1f}%",
                    "cube": meta.get('cube'),
                    "type": doc_type,
                    "priority": priority,
                    "_sort_key": (0.5 * priority + 0.3 * similarity + 0.2 * keyword_score, similarity, priority)
                }
            raw_results.append(result)

        # Sort by hybrid score (desc), then similarity, then priority
        raw_results.sort(key=lambda x: x["_sort_key"], reverse=True)

        # Take top results and remove sort key
        formatted = []
        for result in raw_results[:limit]:
            result_copy = result.copy()
            del result_copy["_sort_key"]
            formatted.append(result_copy)
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
    
        project_root = Path(__file__).resolve().parents[2]
        normalized = module_name.strip().strip("/\\")
        normalized = normalized.replace("\\", "/")
    
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
        domain_names = {Path(d).name for d in domains}
    
        candidate_paths = []
        if normalized:
            candidate_paths.append(project_root / normalized)
            if normalized.startswith("modules/"):
                parts = normalized.split("/")
                if len(parts) >= 3:
                    domain_part = parts[1]
                    module_part = parts[2]
                    candidate_paths.append(project_root / "modules" / domain_part / module_part)
            else:
                parts = normalized.split("/")
                if len(parts) >= 2 and parts[0] in domain_names:
                    domain_part = parts[0]
                    module_part = parts[1]
                    candidate_paths.append(project_root / "modules" / domain_part / module_part)
                if len(parts) >= 3 and parts[0] == "modules":
                    domain_part = parts[1]
                    module_part = parts[2]
                    candidate_paths.append(project_root / "modules" / domain_part / module_part)
    
        module_basename = normalized.split("/")[-1] if normalized else module_name.strip()
        for domain in domains:
            domain_path = project_root / domain
            candidate_paths.append(domain_path / module_basename)
    
        module_path = None
        seen = set()
        for candidate in candidate_paths:
            resolved = candidate.resolve()
            if resolved in seen:
                continue
            seen.add(resolved)
            if resolved.exists() and resolved.is_dir():
                module_path = resolved
                break
    
        if not module_path:
            similar_modules = []
            key = normalized.lower() if normalized else module_name.lower()
            for need, location in self.need_to.items():
                if key in need.lower() or key in location.lower():
                    path_parts = location.split('/')
                    if len(path_parts) >= 3 and path_parts[0] == 'modules':
                        module_path_str = '/'.join(path_parts[:4])
                        if module_path_str not in similar_modules:
                            similar_modules.append(module_path_str)
    
            return {
                "exists": False,
                "module_name": module_name,
                "similar_modules": similar_modules,
                "recommendation": f"[BLOCKED] MODULE '{module_name}' DOES NOT EXIST - DO NOT CREATE IT! " +
                                   (f"Similar modules found: {', '.join(similar_modules)}. " if similar_modules else "") +
                                   "ENHANCE EXISTING MODULES - DO NOT VIBECODE (See WSP_84_Module_Evolution). " +
                                   "Use --search to find existing functionality FIRST before ANY code generation."
            }
    
        try:
            module_label = str(module_path.relative_to(project_root))
        except ValueError:
            module_label = str(module_path)
    
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
    
        wsp_compliance = "[VIOLATION] NON-COMPLIANT" if compliance_score < 7 else "[COMPLIANT] COMPLIANT"
    
        health_warnings = []
        if not tests_exist:
            health_warnings.append("Missing tests directory (WSP 49)")
        if not readme_exists:
            health_warnings.append("Missing README.md (WSP 22)")
        if not interface_exists:
            health_warnings.append("Missing INTERFACE.md (WSP 11)")
    
        return {
            "exists": True,
            "module_name": module_label,
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
            "recommendation": f"Module '{module_label}' exists at {module_path}. " +
                               (f"WSP Compliance: {wsp_compliance}. " if wsp_compliance == "[VIOLATION] NON-COMPLIANT" else "[COMPLIANT] WSP Compliant. ") +
                               ("MANDATORY: Read README.md and INTERFACE.md BEFORE making changes. " if readme_exists and interface_exists else "CRITICAL: Create missing documentation FIRST (WSP_22_Documentation). ")
        }

    def _resolve_location_parts(self, location: str) -> Tuple[Optional[Path], Optional[str]]:
        """
        Parse a NAVIGATION location string into file path + optional symbol/line descriptor.
        Returns (Path, symbol_text) or (None, None) if parsing fails.
        """
        if not location:
            return None, None

        normalized = location.strip()
        if not normalized:
            return None, None

        symbol = None
        split_idx = normalized.rfind(':')
        filepath = normalized

        if split_idx > 1:
            filepath = normalized[:split_idx]
            symbol = normalized[split_idx + 1 :].strip() or None

        try:
            file_path = Path(filepath.strip())
            if not file_path.is_absolute():
                file_path = (self.project_root / filepath.strip()).resolve()
            return file_path, symbol
        except Exception:
            return None, symbol

    def _find_symbol_line(self, file_path: Path, symbol: Optional[str]) -> Optional[int]:
        """Heuristic search for a symbol name within a file to approximate its line number."""
        if not symbol or not file_path.exists():
            return None

        target = symbol.replace('()', '').strip()
        if not target:
            return None

        primary = target.split()[0]
        candidates = [target, primary]
        seen: set[str] = set()

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as handle:
                lines = handle.readlines()
        except Exception:
            return None

        for idx, line in enumerate(lines, start=1):
            lowered = line.lower()
            for candidate in candidates:
                key = candidate.lower()
                if key in seen:
                    continue
                if key and key in lowered:
                    seen.add(key)
                    return idx

        return None

    def _extract_typescript_entities(self, file_path: Path) -> Dict[str, Dict[str, Any]]:
        """Parse TypeScript/TSX file for entity metadata with simple caching."""
        suffix = file_path.suffix.lower()
        if suffix not in {'.ts', '.tsx', '.jsx'}:
            return {}

        try:
            stat = file_path.stat()
        except FileNotFoundError:
            return {}

        cache_entry = self._ts_entity_cache.get(str(file_path))
        if cache_entry and cache_entry.get('mtime') == stat.st_mtime:
            return cache_entry.get('entities', {})

        try:
            text = file_path.read_text(encoding='utf-8', errors='ignore')
        except Exception:
            return {}

        lines = text.splitlines()
        entities = parse_typescript_entities(lines)
        self._ts_entity_cache[str(file_path)] = {
            "mtime": stat.st_mtime,
            "entities": entities
        }
        return entities

    def _match_typescript_entity(self, symbol: Optional[str], entities: Dict[str, Dict[str, Any]]) -> Tuple[Optional[str], Optional[int]]:
        """Match a NAVIGATION symbol description to a parsed TypeScript entity."""
        if not symbol or not entities:
            return None, None

        cleaned = symbol.strip()
        if not cleaned:
            return None, None

        cleaned = cleaned.replace('()', '')
        candidates = [cleaned]

        if '(' in symbol:
            candidates.append(symbol.split('(', 1)[0])
        if ' ' in cleaned:
            candidates.append(cleaned.split(' ', 1)[0])

        for candidate in candidates:
            key = _normalize_symbol_key(candidate)
            if key and key in entities:
                entry = entities[key]
                return entry.get('preview'), entry.get('line')

        return None, None

    def _extract_ast_preview(self, filepath: str, match_line: int, context: int = 6) -> str:
        """
        0102: Extract surrounding JSX/TSX AST block for preview using fallback extraction
        
        Args:
            filepath: Path to the TypeScript/JSX file
            match_line: Line number where match was found
            context: Number of lines to include above and below
            
        Returns:
            Extracted code block for preview
        """
        try:
            from pathlib import Path
            
            file_path = Path(filepath)
            if not file_path.exists():
                return "[File not found]"
            
            # Read file content
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.read().splitlines()
            
            if not lines or match_line <= 0 or match_line > len(lines):
                return "[Invalid line range]"
            
            # Calculate context boundaries
            start_line = max(0, match_line - context - 1)  # Convert to 0-based
            end_line = min(len(lines), match_line + context)
            
            # Extract the block
            preview_lines = lines[start_line:end_line]
            
            # Clean up the preview
            preview = '\n'.join(preview_lines).strip()
            
            # Limit preview length for display
            if len(preview) > 400:
                preview = preview[:400] + "..."
            
            return preview if preview else "[No preview available]"
            
        except Exception as e:
            return f"[0102 preview extraction error: {str(e)}]"

    def _enhance_code_results_with_previews(self, code_hits: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        0102: Enhance code results with AST-based previews for empty results
        
        Args:
            code_hits: List of code search results
            
        Returns:
            Enhanced results with previews
        """
        enhanced_hits = []
        
        for hit in code_hits:
            enhanced_hit = hit.copy()

            if enhanced_hit.get('preview'):
                enhanced_hits.append(enhanced_hit)
                continue

            location = (hit.get('location') or '').strip()
            if not location:
                enhanced_hit['preview'] = "[Location unavailable]"
                enhanced_hits.append(enhanced_hit)
                continue

            file_path, symbol = self._resolve_location_parts(location)
            if not file_path:
                enhanced_hit['preview'] = "[Location format error]"
                enhanced_hits.append(enhanced_hit)
                continue

            enhanced_hit['path'] = str(file_path)

            if not file_path.exists():
                enhanced_hit['preview'] = "[File not found]"
                enhanced_hits.append(enhanced_hit)
                continue

            preview = None
            line_num = None
            manual_preview = None

            suffix = file_path.suffix.lower()
            if symbol and suffix in {'.ts', '.tsx', '.jsx'}:
                entities = self._extract_typescript_entities(file_path)
                manual_preview, line_num = self._match_typescript_entity(symbol, entities)

            if line_num is None:
                line_num = self._find_symbol_line(file_path, symbol)

            if line_num:
                preview = self._extract_ast_preview(str(file_path), line_num)
                enhanced_hit['line'] = line_num
            elif manual_preview:
                preview = manual_preview
            else:
                preview = "[No preview available]"

            enhanced_hit['preview'] = preview
            enhanced_hits.append(enhanced_hit)
        
        return enhanced_hits


TS_FUNCTION_PATTERN = re.compile(r'^(?:export\s+)?(?:default\s+)?(?:async\s+)?function\s+(?P<name>[A-Za-z0-9_]+)\s*\(')
TS_CLASS_PATTERN = re.compile(r'^(?:export\s+)?(?:abstract\s+)?class\s+(?P<name>[A-Za-z0-9_]+)\b')
TS_INTERFACE_PATTERN = re.compile(r'^(?:export\s+)?interface\s+(?P<name>[A-Za-z0-9_]+)\b')
TS_TYPE_PATTERN = re.compile(r'^(?:export\s+)?type\s+(?P<name>[A-Za-z0-9_]+)\b')
TS_ENUM_PATTERN = re.compile(r'^(?:export\s+)?enum\s+(?P<name>[A-Za-z0-9_]+)\b')
TS_CONST_PATTERN = re.compile(r'^(?:export\s+)?const\s+(?P<name>[A-Za-z0-9_]+)\s*(?::[^=]+)?=')
TS_ARRAY_STATE_PATTERN = re.compile(r'^(?:export\s+)?const\s+\[\s*(?P<name>[A-Za-z0-9_]+)')


def _normalize_symbol_key(symbol: str) -> str:
    """Normalize symbol names for consistent dictionary lookups."""
    if not symbol:
        return ""
    return re.sub(r'[^a-z0-9]+', '', symbol.lower())


def _build_preview_from_lines(lines: List[str], index: int, context: int = 6) -> str:
    start = max(0, index - context)
    end = min(len(lines), index + context + 1)
    preview = '\n'.join(lines[start:end]).strip()
    if len(preview) > 400:
        preview = preview[:400] + "..."
    return preview or "[No preview available]"


def parse_typescript_entities(lines: List[str], context: int = 6) -> Dict[str, Dict[str, Any]]:
    """Extract TypeScript/TSX entities (components, hooks, interfaces, etc.) from raw lines."""
    entities: Dict[str, Dict[str, Any]] = {}

    for idx, raw_line in enumerate(lines):
        stripped = raw_line.strip()
        if not stripped or stripped.startswith('//'):
            continue

        entry: Optional[Dict[str, Any]] = None
        match = TS_ARRAY_STATE_PATTERN.match(stripped)
        if match and ('useState' in stripped or 'useReducer' in stripped):
            name = match.group('name')
            entry = {"name": name, "kind": "state"}
        else:
            for kind, pattern in (
                ("function", TS_FUNCTION_PATTERN),
                ("const", TS_CONST_PATTERN),
                ("class", TS_CLASS_PATTERN),
                ("interface", TS_INTERFACE_PATTERN),
                ("type", TS_TYPE_PATTERN),
                ("enum", TS_ENUM_PATTERN),
            ):
                match = pattern.match(stripped)
                if match:
                    name = match.group('name')
                    entry = {"name": name, "kind": kind}
                    break

        if not entry:
            continue

        normalized_key = _normalize_symbol_key(entry["name"])
        if not normalized_key:
            continue

        preview = _build_preview_from_lines(lines, idx, context)
        entities[normalized_key] = {
            "name": entry["name"],
            "line": idx + 1,
            "preview": preview,
            "kind": entry["kind"]
        }

        # Capture both state variable and setter for destructured hooks
        if entry["kind"] == "state" and 'set' in stripped:
            setter_match = re.search(r'set([A-Za-z0-9_]+)', stripped)
            if setter_match:
                setter_name = setter_match.group(1)
                setter_key = _normalize_symbol_key(setter_name)
                if setter_key and setter_key not in entities:
                    entities[setter_key] = {
                        "name": setter_name,
                        "line": idx + 1,
                        "preview": preview,
                        "kind": "state_setter"
                    }

    return entities
