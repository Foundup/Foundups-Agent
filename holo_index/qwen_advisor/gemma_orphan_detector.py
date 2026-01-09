#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gemma Orphan Detector - L0+L1 Module Orphan Detection

Detects "uncontaminated" modules (nothing imports them) and queues
them for Qwen MPS deep analysis.

Architecture:
- L0: Rules-based grep for import patterns (<10ms)
- L1: Gemma fast validation (50-100ms) - is this truly orphaned?
- Output: Queue of orphan modules for Qwen L2 evaluation

WSP Compliance: WSP 15 (MPS), WSP 88 (Orphan Analysis)
"""

import os
import re
import subprocess
from pathlib import Path
from typing import List, Dict, Set, Optional
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)


@dataclass
class OrphanModule:
    """Represents a detected orphan module."""
    path: str
    module_name: str
    lines: int
    last_modified: float
    is_entry_point: bool = False
    gemma_validated: bool = False
    confidence: float = 0.0
    reason: str = ""


@dataclass
class OrphanScanResult:
    """Result of orphan detection scan."""
    orphans: List[OrphanModule] = field(default_factory=list)
    false_positives: List[OrphanModule] = field(default_factory=list)
    total_modules_scanned: int = 0
    scan_duration_ms: float = 0.0


class GemmaOrphanDetector:
    """
    Gemma-powered orphan module detector.
    
    Uses L0 (grep) + L1 (Gemma validation) for fast orphan detection,
    queuing results for Qwen L2 MPS evaluation.
    """
    
    # Known entry points that should NOT be flagged as orphans
    KNOWN_ENTRY_POINTS = {
        "main.py",
        "__main__.py",
        "run_skill.py",
        "run_wre.py",
        "cli.py",
        "dae.py",
        "daemon.py",
        "__init__.py",
    }
    
    # Directories to scan for modules
    MODULE_DIRS = [
        "modules",
        "holo_index",
        "automation",
    ]
    
    # Directories to exclude from scanning
    EXCLUDE_DIRS = {
        "__pycache__",
        ".git",
        "node_modules",
        ".venv",
        "venv",
        "tests",  # Test files are expected to not be imported
    }
    
    def __init__(self, repo_root: Optional[Path] = None):
        """Initialize detector with repository root."""
        self.repo_root = repo_root or Path(__file__).resolve().parents[3]
        self._import_graph: Dict[str, Set[str]] = {}
        self._gemma_engine = None
    
    def _load_gemma(self):
        """Lazy load Gemma engine."""
        if self._gemma_engine is None:
            try:
                from holo_index.qwen_advisor.llm_engine import GemmaInferenceEngine
                self._gemma_engine = GemmaInferenceEngine()
                logger.info("[GEMMA] Loaded Gemma inference engine")
            except ImportError:
                logger.warning("[GEMMA] Gemma unavailable - using rules-only mode")
    
    def scan_for_orphans(self, validate_with_gemma: bool = True) -> OrphanScanResult:
        """
        Scan repository for orphan modules.
        
        Args:
            validate_with_gemma: If True, use Gemma L1 to validate orphans
            
        Returns:
            OrphanScanResult with detected orphans
        """
        import time
        start_time = time.time()
        
        result = OrphanScanResult()
        
        # L0: Build import graph using grep
        logger.info("[L0] Building import graph with grep...")
        all_modules = self._find_all_python_modules()
        import_graph = self._build_import_graph_grep()
        
        result.total_modules_scanned = len(all_modules)
        logger.info(f"[L0] Found {len(all_modules)} Python modules")
        
        # Detect orphans (modules with no incoming edges)
        potential_orphans = []
        for module_path in all_modules:
            module_name = self._path_to_module_name(module_path)
            
            # Check if anything imports this module
            has_importers = self._has_importers(module_name, import_graph)
            
            if not has_importers:
                # Check if it's a known entry point
                is_entry = Path(module_path).name in self.KNOWN_ENTRY_POINTS
                
                orphan = OrphanModule(
                    path=str(module_path),
                    module_name=module_name,
                    lines=self._count_lines(module_path),
                    last_modified=module_path.stat().st_mtime if module_path.exists() else 0,
                    is_entry_point=is_entry,
                )
                
                if is_entry:
                    orphan.reason = "Known entry point - not a true orphan"
                    orphan.confidence = 0.0
                    result.false_positives.append(orphan)
                else:
                    potential_orphans.append(orphan)
        
        logger.info(f"[L0] Detected {len(potential_orphans)} potential orphans")
        
        # L1: Gemma validation (optional)
        if validate_with_gemma and potential_orphans:
            self._load_gemma()
            if self._gemma_engine:
                logger.info("[L1] Validating orphans with Gemma...")
                for orphan in potential_orphans:
                    is_true_orphan, confidence, reason = self._gemma_validate_orphan(orphan)
                    orphan.gemma_validated = True
                    orphan.confidence = confidence
                    orphan.reason = reason
                    
                    if is_true_orphan:
                        result.orphans.append(orphan)
                    else:
                        result.false_positives.append(orphan)
            else:
                # No Gemma - use heuristics
                for orphan in potential_orphans:
                    orphan.confidence = 0.8  # High confidence from L0
                    orphan.reason = "L0 grep detection (no Gemma validation)"
                    result.orphans.append(orphan)
        else:
            result.orphans = potential_orphans
        
        result.scan_duration_ms = (time.time() - start_time) * 1000
        logger.info(f"[SCAN] Complete: {len(result.orphans)} orphans, "
                   f"{len(result.false_positives)} false positives, "
                   f"{result.scan_duration_ms:.0f}ms")
        
        return result
    
    def _find_all_python_modules(self) -> List[Path]:
        """Find all Python modules in module directories."""
        modules = []
        for dir_name in self.MODULE_DIRS:
            dir_path = self.repo_root / dir_name
            if dir_path.exists():
                for py_file in dir_path.rglob("*.py"):
                    # Skip excluded directories
                    if any(excl in py_file.parts for excl in self.EXCLUDE_DIRS):
                        continue
                    modules.append(py_file)
        return modules
    
    def _build_import_graph_grep(self) -> Dict[str, Set[str]]:
        """Build import graph using grep (L0 fast scan)."""
        import_graph: Dict[str, Set[str]] = {}
        
        # Grep for import statements
        try:
            result = subprocess.run(
                ["grep", "-rn", "--include=*.py", "-E", 
                 r"^(from|import)\s+[a-zA-Z_]"],
                cwd=str(self.repo_root),
                capture_output=True,
                text=True,
                timeout=30
            )
            
            for line in result.stdout.split('\n'):
                if ':' not in line:
                    continue
                
                parts = line.split(':', 2)
                if len(parts) < 3:
                    continue
                
                file_path, line_num, content = parts
                
                # Parse import statement
                imported = self._parse_import_statement(content)
                if imported:
                    if file_path not in import_graph:
                        import_graph[file_path] = set()
                    import_graph[file_path].add(imported)
                    
        except subprocess.TimeoutExpired:
            logger.warning("[L0] Grep timeout - using fallback")
        except Exception as e:
            logger.warning(f"[L0] Grep failed: {e}")
        
        return import_graph
    
    def _parse_import_statement(self, line: str) -> Optional[str]:
        """Parse an import statement to extract module name."""
        line = line.strip()
        
        # from X import Y
        match = re.match(r'^from\s+([a-zA-Z_][a-zA-Z0-9_.]*)\s+import', line)
        if match:
            return match.group(1).split('.')[0]
        
        # import X
        match = re.match(r'^import\s+([a-zA-Z_][a-zA-Z0-9_.]*)', line)
        if match:
            return match.group(1).split('.')[0]
        
        return None
    
    def _path_to_module_name(self, path: Path) -> str:
        """Convert file path to module name."""
        try:
            rel_path = path.relative_to(self.repo_root)
            # Convert path to module notation
            parts = list(rel_path.parts[:-1])  # Exclude filename
            if rel_path.stem != "__init__":
                parts.append(rel_path.stem)
            return ".".join(parts)
        except ValueError:
            return path.stem
    
    def _has_importers(self, module_name: str, import_graph: Dict[str, Set[str]]) -> bool:
        """Check if any module imports this module."""
        # Check in import graph
        module_parts = module_name.split('.')
        base_module = module_parts[0] if module_parts else module_name
        
        for file_path, imports in import_graph.items():
            for imp in imports:
                if imp == base_module or imp.startswith(f"{base_module}."):
                    # Don't count self-imports
                    if module_name not in file_path:
                        return True
        
        return False
    
    def _count_lines(self, file_path: Path) -> int:
        """Count lines in a file."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return sum(1 for _ in f)
        except Exception:
            return 0
    
    def _gemma_validate_orphan(self, orphan: OrphanModule) -> tuple:
        """
        Use Gemma L1 to validate if module is truly orphaned.
        
        Returns:
            (is_true_orphan, confidence, reason)
        """
        if not self._gemma_engine:
            return (True, 0.7, "No Gemma validation available")
        
        prompt = f"""You are validating if a Python module is truly orphaned (unused).

Module: {orphan.module_name}
Path: {orphan.path}
Lines: {orphan.lines}

Rules:
- Entry points (main.py, cli.py, daemon.py) are NOT orphans
- Test files in tests/ are NOT orphans
- __init__.py files are NOT orphans
- Skill files (run_skill.py) are NOT orphans
- Modules with "example" or "deprecated" in name may be intentional orphans

Is this a TRUE orphan that should be reviewed for deletion?
Respond: TRUE_ORPHAN or FALSE_POSITIVE with confidence (0.0-1.0) and reason.
Format: [TRUE_ORPHAN|FALSE_POSITIVE] confidence reason
"""
        
        try:
            response = self._gemma_engine.generate_response(prompt, max_tokens=50)
            
            if "TRUE_ORPHAN" in response.upper():
                # Parse confidence
                parts = response.split()
                confidence = 0.85
                for part in parts:
                    try:
                        val = float(part)
                        if 0 <= val <= 1:
                            confidence = val
                            break
                    except ValueError:
                        continue
                return (True, confidence, response.strip())
            else:
                return (False, 0.9, response.strip())
                
        except Exception as e:
            logger.warning(f"[GEMMA] Validation failed: {e}")
            return (True, 0.6, f"Gemma validation failed: {e}")
    
    def queue_for_qwen_mps(self, orphans: List[OrphanModule]) -> List[Dict]:
        """
        Queue orphan modules for Qwen MPS evaluation.
        
        Returns list of issue dictionaries for IssueMPSEvaluator.
        """
        issues = []
        for orphan in orphans:
            issues.append({
                "type": "DEAD_CODE",
                "description": f"Orphan module '{orphan.module_name}' ({orphan.lines} lines) - no imports found",
                "confidence": orphan.confidence,
                "path": orphan.path,
                "metadata": {
                    "lines": orphan.lines,
                    "gemma_validated": orphan.gemma_validated,
                    "reason": orphan.reason,
                }
            })
        return issues


# CLI for standalone testing
if __name__ == "__main__":
    import argparse
    
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    
    parser = argparse.ArgumentParser(description="Gemma Orphan Detector")
    parser.add_argument("--no-gemma", action="store_true", help="Skip Gemma validation")
    parser.add_argument("--queue", action="store_true", help="Output as MPS queue")
    args = parser.parse_args()
    
    detector = GemmaOrphanDetector()
    result = detector.scan_for_orphans(validate_with_gemma=not args.no_gemma)
    
    print("\n" + "=" * 60)
    print("ORPHAN DETECTION RESULTS")
    print("=" * 60)
    print(f"Total scanned: {result.total_modules_scanned}")
    print(f"Orphans found: {len(result.orphans)}")
    print(f"False positives: {len(result.false_positives)}")
    print(f"Scan time: {result.scan_duration_ms:.0f}ms")
    
    if result.orphans:
        print("\n[ORPHANS] Modules with no imports:")
        for orphan in sorted(result.orphans, key=lambda x: -x.lines)[:10]:
            print(f"  • {orphan.module_name} ({orphan.lines} lines) - {orphan.confidence:.0%} conf")
    
    if args.queue:
        print("\n[QUEUE] MPS Issues for Qwen:")
        issues = detector.queue_for_qwen_mps(result.orphans)
        for issue in issues[:5]:
            print(f"  • {issue['type']}: {issue['description'][:60]}...")
