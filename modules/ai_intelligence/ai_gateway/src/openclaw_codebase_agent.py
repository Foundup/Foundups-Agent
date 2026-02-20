#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OpenClaw 0102 Codebase Agent - AI-powered codebase analysis and optimization.

This agent combines:
  1. HoloIndex semantic code search for intelligent retrieval
  2. Direct file reading/analysis for deep understanding
  3. SIM integration for pAVS parameter optimization (OpenClaw methodology)
  4. Research monitoring for AI/crypto topics relevant to pAVS
  5. Security compliance following openclaw_security_sentinel patterns

Architecture (WSP 73 Digital Twin):
  - Partner: This agent (codebase intelligence layer)
  - Principal: OpenClaw DAE (intent classification + routing)
  - Associates: HoloIndex, SIM Optimizer, Model Registry

WSP Compliance:
  WSP 50  : Pre-Action Verification (file path validation)
  WSP 64  : Violation Prevention (security checks before operations)
  WSP 73  : Digital Twin Architecture (Partner-Principal-Associate)
  WSP 77  : Agent Coordination (4-phase execution)
  WSP 84  : Code Reuse (leverages existing HoloIndex, SIM)
  WSP 91  : Observability (structured logging)

NAVIGATION:
  -> Called by: ai_gateway/main.py, CLI commands
  -> Uses: holo_index/, modules/foundups/simulator/economics/
  -> Related: openclaw_security_sentinel.py, model_registry.py
"""

from __future__ import annotations

import json
import logging
import os
import re
import time
from dataclasses import dataclass, field
from datetime import datetime, UTC
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("openclaw_codebase_agent")


# =============================================================================
# CONFIGURATION
# =============================================================================

class OperationType(Enum):
    """Types of codebase operations."""
    SEARCH = "search"           # HoloIndex semantic search
    READ = "read"               # Direct file reading
    ANALYZE = "analyze"         # Code analysis (patterns, dependencies)
    OPTIMIZE = "optimize"       # SIM parameter optimization
    RESEARCH = "research"       # AI/crypto research monitoring
    AUDIT = "audit"             # Model version audit
    STATUS = "status"           # System status check


@dataclass
class CodebaseSearchResult:
    """Result from HoloIndex semantic search."""
    query: str
    code_hits: List[Dict[str, Any]] = field(default_factory=list)
    wsp_hits: List[Dict[str, Any]] = field(default_factory=list)
    total_hits: int = 0
    search_time_ms: int = 0
    method: str = "holo_index"


@dataclass
class FileAnalysisResult:
    """Result from file reading and analysis."""
    file_path: str
    exists: bool
    content: str = ""
    line_count: int = 0
    size_bytes: int = 0
    file_type: str = ""
    analysis: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None


@dataclass
class OptimizationResult:
    """Result from SIM parameter optimization."""
    objective: str
    iterations: int
    best_score: float
    best_config: Dict[str, Any] = field(default_factory=dict)
    convergence: str = "unknown"
    execution_time_sec: float = 0.0
    error: Optional[str] = None


# =============================================================================
# SECURITY PATTERNS (from openclaw_security_sentinel.py)
# =============================================================================

# File paths that should never be read or exposed
FORBIDDEN_PATHS = frozenset({
    ".env", ".env.local", ".env.production",
    "credentials.json", "secrets.json", "tokens.json",
    ".git/config", ".ssh/", "id_rsa", "id_ed25519",
    "firebase-adminsdk", "serviceAccount", "private_key",
})

# File patterns that should never be exposed
FORBIDDEN_PATTERNS = [
    r"\.env\b", r"secret", r"credential", r"token",
    r"private[_-]?key", r"api[_-]?key", r"password",
    r"oauth", r"bearer", r"firebase.*admin",
]

# Content patterns that trigger redaction
SECRET_CONTENT_PATTERNS = [
    r"AIza[A-Za-z0-9_-]{33}",          # Google API keys
    r"sk-[A-Za-z0-9]{48,}",            # OpenAI/Anthropic keys
    r"sk-ant-api[A-Za-z0-9_-]{40,}",   # Anthropic keys
    r"xai-[A-Za-z0-9]{40,}",           # Grok keys
    r"ghp_[A-Za-z0-9]{36}",            # GitHub tokens
    r"-----BEGIN.*PRIVATE KEY-----",   # Private keys
    r"Bearer\s+ey[A-Za-z0-9._-]+",     # JWT tokens
]


def is_path_forbidden(path: str) -> bool:
    """Check if a path is forbidden for security reasons."""
    path_lower = path.lower().replace("\\", "/")

    # Check exact matches
    for forbidden in FORBIDDEN_PATHS:
        if forbidden.lower() in path_lower:
            return True

    # Check patterns
    for pattern in FORBIDDEN_PATTERNS:
        if re.search(pattern, path_lower, re.IGNORECASE):
            return True

    return False


def redact_secrets(content: str) -> Tuple[str, bool]:
    """Redact secret patterns from content. Returns (redacted, was_redacted)."""
    was_redacted = False

    for pattern in SECRET_CONTENT_PATTERNS:
        if re.search(pattern, content):
            content = re.sub(pattern, "[REDACTED]", content)
            was_redacted = True

    return content, was_redacted


# =============================================================================
# OPENCLAW 0102 CODEBASE AGENT
# =============================================================================

class OpenClawCodebaseAgent:
    """
    AI-powered codebase analysis and optimization agent.

    Provides intelligent access to the codebase with:
    - Semantic code search via HoloIndex
    - Secure file reading with automatic secret redaction
    - Pattern analysis for code quality and dependencies
    - SIM parameter optimization using OpenClaw methodology
    - Research monitoring for relevant AI/crypto topics

    Security:
    - All file operations validate paths against FORBIDDEN_PATHS
    - Content is automatically scanned and secrets redacted
    - Follows openclaw_security_sentinel patterns
    - TTL-bounded caching for performance
    """

    def __init__(
        self,
        repo_root: Optional[Path] = None,
        *,
        enable_holo_index: bool = True,
        enable_sim_optimizer: bool = True,
        enable_research_monitor: bool = True,
        cache_ttl_sec: int = 300,
    ):
        """
        Initialize the OpenClaw Codebase Agent.

        Args:
            repo_root: Root path of the repository (auto-detected if None)
            enable_holo_index: Enable semantic code search
            enable_sim_optimizer: Enable SIM parameter optimization
            enable_research_monitor: Enable research topic monitoring
            cache_ttl_sec: Cache TTL for repeated operations
        """
        self.repo_root = Path(repo_root) if repo_root else self._detect_repo_root()
        self.enable_holo_index = enable_holo_index
        self.enable_sim_optimizer = enable_sim_optimizer
        self.enable_research_monitor = enable_research_monitor
        self.cache_ttl_sec = cache_ttl_sec

        # Lazy-loaded components
        self._holo_index = None
        self._sim_optimizer = None
        self._model_registry = None
        self._ai_gateway = None

        # Operation cache
        self._cache: Dict[str, Tuple[Any, float]] = {}

        # Statistics
        self.stats = {
            "searches": 0,
            "reads": 0,
            "analyses": 0,
            "optimizations": 0,
            "research_scans": 0,
            "cache_hits": 0,
            "secrets_redacted": 0,
            "paths_blocked": 0,
        }

        logger.info(
            "[CODEBASE-AGENT] Initialized | repo=%s holo=%s sim=%s research=%s",
            self.repo_root, enable_holo_index, enable_sim_optimizer, enable_research_monitor
        )

    @staticmethod
    def _detect_repo_root() -> Path:
        """Auto-detect repository root."""
        # Try common locations
        candidates = [
            Path("O:/Foundups-Agent"),
            Path(__file__).parent.parent.parent.parent.parent,
            Path.cwd(),
        ]

        for candidate in candidates:
            if (candidate / "CLAUDE.md").exists():
                return candidate.resolve()

        return Path.cwd()

    # -------------------------------------------------------------------------
    # Lazy Loaders
    # -------------------------------------------------------------------------

    @property
    def holo_index(self):
        """Lazy-load HoloIndex."""
        if self._holo_index is None and self.enable_holo_index:
            try:
                from holo_index.core.holo_index import HoloIndex
                self._holo_index = HoloIndex()
                logger.info("[CODEBASE-AGENT] HoloIndex loaded")
            except ImportError as exc:
                logger.warning("[CODEBASE-AGENT] HoloIndex unavailable: %s", exc)
        return self._holo_index

    @property
    def sim_optimizer(self):
        """Lazy-load SIM Parameter Optimizer."""
        if self._sim_optimizer is None and self.enable_sim_optimizer:
            try:
                from modules.foundups.simulator.economics.ai_parameter_optimizer import (
                    AIParameterOptimizer,
                    OptimizerConfig,
                    OptimizationObjective,
                )
                # Default balanced config
                config = OptimizerConfig(
                    objective=OptimizationObjective.BALANCED,
                    max_iterations=5,
                    ticks_per_evaluation=300,
                    verbose=True,
                )
                self._sim_optimizer = AIParameterOptimizer(config=config)
                logger.info("[CODEBASE-AGENT] SIM Optimizer loaded")
            except ImportError as exc:
                logger.warning("[CODEBASE-AGENT] SIM Optimizer unavailable: %s", exc)
        return self._sim_optimizer

    @property
    def model_registry(self):
        """Lazy-load Model Registry."""
        if self._model_registry is None:
            try:
                from modules.ai_intelligence.ai_gateway.src import model_registry
                self._model_registry = model_registry
                logger.info("[CODEBASE-AGENT] Model Registry loaded")
            except ImportError as exc:
                logger.warning("[CODEBASE-AGENT] Model Registry unavailable: %s", exc)
        return self._model_registry

    @property
    def ai_gateway(self):
        """Lazy-load AI Gateway."""
        if self._ai_gateway is None:
            try:
                from modules.ai_intelligence.ai_gateway.src.ai_gateway import AIGateway
                self._ai_gateway = AIGateway()
                logger.info("[CODEBASE-AGENT] AI Gateway loaded")
            except ImportError as exc:
                logger.warning("[CODEBASE-AGENT] AI Gateway unavailable: %s", exc)
        return self._ai_gateway

    # -------------------------------------------------------------------------
    # Cache Management
    # -------------------------------------------------------------------------

    def _cache_get(self, key: str) -> Optional[Any]:
        """Get value from cache if not expired."""
        if key in self._cache:
            value, timestamp = self._cache[key]
            if time.time() - timestamp < self.cache_ttl_sec:
                self.stats["cache_hits"] += 1
                return value
            else:
                del self._cache[key]
        return None

    def _cache_set(self, key: str, value: Any) -> None:
        """Set value in cache."""
        self._cache[key] = (value, time.time())

    # -------------------------------------------------------------------------
    # Core Operations
    # -------------------------------------------------------------------------

    def search(
        self,
        query: str,
        *,
        limit: int = 10,
        include_code: bool = True,
        include_wsps: bool = True,
    ) -> CodebaseSearchResult:
        """
        Semantic code search via HoloIndex.

        Args:
            query: Natural language search query
            limit: Maximum number of results
            include_code: Include code file results
            include_wsps: Include WSP documentation results

        Returns:
            CodebaseSearchResult with matching files and snippets
        """
        start_time = time.time()
        self.stats["searches"] += 1

        # Check cache
        cache_key = f"search:{query}:{limit}:{include_code}:{include_wsps}"
        cached = self._cache_get(cache_key)
        if cached:
            return cached

        result = CodebaseSearchResult(query=query)

        if not self.holo_index:
            result.method = "unavailable"
            return result

        try:
            # Execute HoloIndex search
            search_results = self.holo_index.search(query, limit=limit)

            if include_code:
                result.code_hits = search_results.get("code", [])[:limit]

            if include_wsps:
                result.wsp_hits = search_results.get("wsps", [])[:limit]

            result.total_hits = len(result.code_hits) + len(result.wsp_hits)

        except Exception as exc:
            logger.error("[CODEBASE-AGENT] Search error: %s", exc)
            result.method = f"error: {exc}"

        result.search_time_ms = int((time.time() - start_time) * 1000)
        self._cache_set(cache_key, result)

        logger.info(
            "[CODEBASE-AGENT] Search: query='%s' hits=%d time=%dms",
            query[:50], result.total_hits, result.search_time_ms
        )
        return result

    def read_file(
        self,
        file_path: str,
        *,
        max_lines: int = 500,
        start_line: int = 1,
        analyze: bool = False,
    ) -> FileAnalysisResult:
        """
        Read a file with security checks and optional analysis.

        Security:
        - Path is validated against FORBIDDEN_PATHS
        - Content is scanned and secrets are redacted
        - Relative paths are resolved against repo_root

        Args:
            file_path: Path to the file (absolute or relative to repo_root)
            max_lines: Maximum lines to read
            start_line: Line number to start from (1-indexed)
            analyze: Perform code analysis on the file

        Returns:
            FileAnalysisResult with content and optional analysis
        """
        self.stats["reads"] += 1

        # Resolve path
        if not Path(file_path).is_absolute():
            full_path = self.repo_root / file_path
        else:
            full_path = Path(file_path)

        result = FileAnalysisResult(
            file_path=str(full_path),
            exists=False,
        )

        # Security check: forbidden paths
        if is_path_forbidden(str(full_path)):
            self.stats["paths_blocked"] += 1
            result.error = "Path is forbidden by security policy"
            logger.warning(
                "[CODEBASE-AGENT] [SECURITY] Blocked forbidden path: %s",
                file_path
            )
            return result

        # Check file exists
        if not full_path.exists():
            result.error = f"File not found: {full_path}"
            return result

        if not full_path.is_file():
            result.error = f"Path is not a file: {full_path}"
            return result

        result.exists = True
        result.size_bytes = full_path.stat().st_size
        result.file_type = full_path.suffix.lstrip(".")

        try:
            # Read file content
            content = full_path.read_text(encoding="utf-8", errors="replace")
            lines = content.split("\n")
            result.line_count = len(lines)

            # Apply line range
            start_idx = max(0, start_line - 1)
            end_idx = start_idx + max_lines
            selected_lines = lines[start_idx:end_idx]

            # Join with line numbers
            numbered_lines = [
                f"{start_line + i:6d}| {line}"
                for i, line in enumerate(selected_lines)
            ]
            content = "\n".join(numbered_lines)

            # Security: redact secrets
            content, was_redacted = redact_secrets(content)
            if was_redacted:
                self.stats["secrets_redacted"] += 1
                logger.warning(
                    "[CODEBASE-AGENT] [SECURITY] Secrets redacted from: %s",
                    file_path
                )

            result.content = content

            # Optional analysis
            if analyze:
                result.analysis = self._analyze_file_content(
                    content=content,
                    file_type=result.file_type,
                    file_path=str(full_path),
                )
                self.stats["analyses"] += 1

        except Exception as exc:
            result.error = f"Error reading file: {exc}"
            logger.error("[CODEBASE-AGENT] Read error: %s", exc)

        logger.info(
            "[CODEBASE-AGENT] Read: path='%s' lines=%d analyze=%s",
            file_path, result.line_count, analyze
        )
        return result

    def _analyze_file_content(
        self,
        content: str,
        file_type: str,
        file_path: str,
    ) -> Dict[str, Any]:
        """Analyze file content for patterns and structure."""
        analysis = {
            "file_type": file_type,
            "has_imports": False,
            "has_classes": False,
            "has_functions": False,
            "has_tests": False,
            "patterns": [],
        }

        if file_type == "py":
            # Python analysis
            analysis["has_imports"] = bool(re.search(r"^(import|from)\s+", content, re.MULTILINE))
            analysis["has_classes"] = bool(re.search(r"^class\s+\w+", content, re.MULTILINE))
            analysis["has_functions"] = bool(re.search(r"^def\s+\w+", content, re.MULTILINE))
            analysis["has_tests"] = bool(re.search(r"(def test_|pytest|unittest)", content))

            # Count classes and functions
            analysis["class_count"] = len(re.findall(r"^class\s+(\w+)", content, re.MULTILINE))
            analysis["function_count"] = len(re.findall(r"^def\s+(\w+)", content, re.MULTILINE))

            # Detect patterns
            if "dataclass" in content:
                analysis["patterns"].append("dataclass")
            if "@property" in content:
                analysis["patterns"].append("properties")
            if "async def" in content:
                analysis["patterns"].append("async")
            if "WSP" in content:
                analysis["patterns"].append("wsp_compliant")

        elif file_type in ("js", "ts"):
            # JavaScript/TypeScript analysis
            analysis["has_imports"] = bool(re.search(r"(import|require)\s*\(", content))
            analysis["has_classes"] = bool(re.search(r"class\s+\w+", content))
            analysis["has_functions"] = bool(re.search(r"(function\s+\w+|const\s+\w+\s*=\s*(async\s+)?\()", content))

        elif file_type == "md":
            # Markdown analysis
            analysis["has_headers"] = bool(re.search(r"^#+\s+", content, re.MULTILINE))
            analysis["has_code_blocks"] = bool(re.search(r"```", content))
            analysis["has_links"] = bool(re.search(r"\[.*\]\(.*\)", content))

        return analysis

    def run_optimization(
        self,
        objective: str = "balanced",
        max_iterations: int = 5,
        ticks: int = 300,
    ) -> OptimizationResult:
        """
        Run SIM parameter optimization using OpenClaw methodology.

        Args:
            objective: Optimization objective (balanced, staker, growth, velocity)
            max_iterations: Maximum optimization iterations
            ticks: Simulation ticks per evaluation

        Returns:
            OptimizationResult with optimal configuration
        """
        start_time = time.time()
        self.stats["optimizations"] += 1

        result = OptimizationResult(
            objective=objective,
            iterations=0,
            best_score=0.0,
        )

        if not self.enable_sim_optimizer:
            result.error = "SIM optimizer disabled"
            return result

        try:
            from modules.foundups.simulator.economics.ai_parameter_optimizer import (
                AIParameterOptimizer,
                OptimizerConfig,
                OptimizationObjective,
            )

            # Map string to enum
            objective_map = {
                "staker": OptimizationObjective.STAKER_DISTRIBUTION,
                "growth": OptimizationObjective.ECOSYSTEM_GROWTH,
                "velocity": OptimizationObjective.TOKEN_VELOCITY,
                "balanced": OptimizationObjective.BALANCED,
            }

            config = OptimizerConfig(
                objective=objective_map.get(objective, OptimizationObjective.BALANCED),
                max_iterations=max_iterations,
                ticks_per_evaluation=ticks,
                verbose=True,
            )

            optimizer = AIParameterOptimizer(config=config)

            logger.info(
                "[CODEBASE-AGENT] Starting optimization: objective=%s iterations=%d ticks=%d",
                objective, max_iterations, ticks
            )

            optimal_config, history = optimizer.optimize()
            summary = optimizer.get_optimization_summary()

            result.iterations = summary.get("iterations", 0)
            result.best_score = summary.get("best_score", 0.0)
            result.best_config = summary.get("best_config", {})
            result.convergence = summary.get("convergence", "unknown")

        except ImportError as exc:
            result.error = f"SIM optimizer import error: {exc}"
            logger.error("[CODEBASE-AGENT] Optimization import error: %s", exc)
        except Exception as exc:
            result.error = f"Optimization error: {exc}"
            logger.error("[CODEBASE-AGENT] Optimization error: %s", exc)

        result.execution_time_sec = time.time() - start_time

        logger.info(
            "[CODEBASE-AGENT] Optimization complete: score=%.4f iterations=%d time=%.1fs",
            result.best_score, result.iterations, result.execution_time_sec
        )
        return result

    def scan_research(
        self,
        topics: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Scan for relevant research papers and announcements.

        Args:
            topics: List of research topics (uses defaults if None)

        Returns:
            List of research findings with topic, summary, and source
        """
        self.stats["research_scans"] += 1

        if not self.enable_research_monitor:
            return []

        default_topics = [
            "tokenomics simulation optimization",
            "agent swarm coordination patterns",
            "crypto staking reward distribution",
            "demurrage currency implementation",
            "bonding curve mathematics",
            "DAO governance mechanisms",
            "AI parameter optimization reinforcement learning",
        ]

        topics = topics or default_topics
        findings = []

        if not self.ai_gateway:
            logger.warning("[CODEBASE-AGENT] Research scan skipped: AI Gateway unavailable")
            return findings

        logger.info("[CODEBASE-AGENT] Scanning %d research topics...", len(topics))

        for topic in topics:
            try:
                prompt = f"""Find recent research (2025-2026) on: {topic}
Summarize in 1-2 sentences. Include paper title if available.
Focus on practical implementations relevant to autonomous agent systems."""

                result = self.ai_gateway.call_with_fallback(prompt, task_type="analysis")

                if result.success and len(result.response) > 20:
                    findings.append({
                        "topic": topic,
                        "summary": result.response[:500],
                        "provider": result.provider,
                        "timestamp": datetime.now(UTC).isoformat(),
                    })
                    logger.info("[CODEBASE-AGENT] Found research: %s", topic[:30])

            except Exception as exc:
                logger.debug("[CODEBASE-AGENT] Research error for '%s': %s", topic, exc)

        return findings

    def audit_models(self) -> Dict[str, Any]:
        """
        Audit codebase for deprecated model references.

        Returns:
            Audit report with current, legacy, deprecated, and unknown models
        """
        if not self.model_registry:
            return {"error": "Model registry unavailable"}

        # Scan codebase for model references
        scan_extensions = [".py", ".json", ".yaml", ".yml", ".js", ".ts"]
        skip_patterns = [".git", ".venv", "__pycache__", "node_modules", "model_registry.py"]

        found_models = set()

        for ext in scan_extensions:
            for filepath in self.repo_root.rglob(f"*{ext}"):
                if any(skip in str(filepath) for skip in skip_patterns):
                    continue

                try:
                    content = filepath.read_text(encoding="utf-8", errors="ignore")

                    # Look for model IDs in the content
                    for model_id in self.model_registry.ALL_MODELS.keys():
                        if model_id in content:
                            found_models.add(model_id)

                except Exception:
                    pass

        # Audit the found models
        audit_result = self.model_registry.audit_codebase_models(list(found_models))
        audit_result["total_references"] = len(found_models)
        audit_result["migration_map"] = {
            old: new
            for old, new in self.model_registry.MIGRATION_MAP.items()
            if old in found_models
        }

        logger.info(
            "[CODEBASE-AGENT] Model audit: current=%d legacy=%d deprecated=%d unknown=%d",
            len(audit_result.get("current", [])),
            len(audit_result.get("legacy", [])),
            len(audit_result.get("deprecated", [])),
            len(audit_result.get("unknown", [])),
        )

        return audit_result

    def get_status(self) -> Dict[str, Any]:
        """Get agent status and statistics."""
        return {
            "agent": "OpenClaw 0102 Codebase Agent",
            "repo_root": str(self.repo_root),
            "components": {
                "holo_index": self._holo_index is not None,
                "sim_optimizer": self._sim_optimizer is not None,
                "model_registry": self._model_registry is not None,
                "ai_gateway": self._ai_gateway is not None,
            },
            "settings": {
                "enable_holo_index": self.enable_holo_index,
                "enable_sim_optimizer": self.enable_sim_optimizer,
                "enable_research_monitor": self.enable_research_monitor,
                "cache_ttl_sec": self.cache_ttl_sec,
            },
            "statistics": self.stats.copy(),
            "cache_entries": len(self._cache),
            "timestamp": datetime.now(UTC).isoformat(),
        }

    # -------------------------------------------------------------------------
    # High-Level Operations
    # -------------------------------------------------------------------------

    def analyze_module(
        self,
        module_path: str,
        *,
        depth: str = "standard",
    ) -> Dict[str, Any]:
        """
        Analyze a module for structure, dependencies, and WSP compliance.

        Args:
            module_path: Path to module (relative to repo_root)
            depth: Analysis depth (quick, standard, deep)

        Returns:
            Module analysis report
        """
        full_path = self.repo_root / module_path

        if not full_path.exists():
            return {"error": f"Module not found: {module_path}"}

        analysis = {
            "module_path": module_path,
            "depth": depth,
            "files": [],
            "wsp_compliance": {
                "has_readme": False,
                "has_interface": False,
                "has_src": False,
                "has_tests": False,
                "has_modlog": False,
            },
            "summary": {},
        }

        # Check WSP 49 structure
        analysis["wsp_compliance"]["has_readme"] = (full_path / "README.md").exists()
        analysis["wsp_compliance"]["has_interface"] = (full_path / "INTERFACE.md").exists()
        analysis["wsp_compliance"]["has_src"] = (full_path / "src").exists()
        analysis["wsp_compliance"]["has_tests"] = (full_path / "tests").exists()
        analysis["wsp_compliance"]["has_modlog"] = (full_path / "ModLog.md").exists()

        # Count compliant items
        compliant = sum(1 for v in analysis["wsp_compliance"].values() if v)
        analysis["wsp_compliance"]["score"] = compliant / 5

        # Scan files
        if depth in ("standard", "deep"):
            for filepath in full_path.rglob("*.py"):
                if "__pycache__" in str(filepath):
                    continue

                rel_path = filepath.relative_to(full_path)
                file_info = {
                    "path": str(rel_path),
                    "size_bytes": filepath.stat().st_size,
                }

                if depth == "deep":
                    # Read and analyze
                    result = self.read_file(str(filepath), analyze=True, max_lines=100)
                    if result.exists:
                        file_info["line_count"] = result.line_count
                        file_info["analysis"] = result.analysis

                analysis["files"].append(file_info)

        # Summary
        analysis["summary"] = {
            "total_files": len(analysis["files"]),
            "wsp_49_compliant": analysis["wsp_compliance"]["score"] >= 0.8,
        }

        logger.info(
            "[CODEBASE-AGENT] Module analysis: %s | files=%d compliance=%.0f%%",
            module_path, len(analysis["files"]), analysis["wsp_compliance"]["score"] * 100
        )

        return analysis


# =============================================================================
# SINGLETON ACCESS
# =============================================================================

_agent_instance: Optional[OpenClawCodebaseAgent] = None


def get_codebase_agent(
    repo_root: Optional[Path] = None,
    **kwargs,
) -> OpenClawCodebaseAgent:
    """Get or create the singleton codebase agent instance."""
    global _agent_instance

    if _agent_instance is None:
        _agent_instance = OpenClawCodebaseAgent(repo_root=repo_root, **kwargs)

    return _agent_instance


# =============================================================================
# CLI INTERFACE
# =============================================================================

def main():
    """CLI interface for the OpenClaw Codebase Agent."""
    import argparse

    parser = argparse.ArgumentParser(
        description="OpenClaw 0102 Codebase Agent - AI-powered codebase analysis"
    )
    parser.add_argument(
        "operation",
        choices=["search", "read", "analyze", "optimize", "research", "audit", "status"],
        help="Operation to perform",
    )
    parser.add_argument(
        "--query", "-q",
        help="Search query (for search operation)",
    )
    parser.add_argument(
        "--path", "-p",
        help="File or module path (for read/analyze operations)",
    )
    parser.add_argument(
        "--objective", "-o",
        default="balanced",
        choices=["balanced", "staker", "growth", "velocity"],
        help="Optimization objective",
    )
    parser.add_argument(
        "--iterations", "-i",
        type=int,
        default=5,
        help="Max optimization iterations",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON",
    )

    args = parser.parse_args()
    agent = get_codebase_agent()

    result = None

    if args.operation == "search":
        if not args.query:
            print("Error: --query required for search operation")
            return 1
        result = agent.search(args.query)
        if not args.json:
            print(f"\n=== Search Results for: {args.query} ===")
            print(f"Total hits: {result.total_hits}")
            print(f"Time: {result.search_time_ms}ms")
            for hit in result.code_hits[:5]:
                print(f"  - {hit.get('file', 'unknown')}")

    elif args.operation == "read":
        if not args.path:
            print("Error: --path required for read operation")
            return 1
        result = agent.read_file(args.path, analyze=True)
        if not args.json:
            if result.exists:
                print(f"\n=== {result.file_path} ===")
                print(f"Lines: {result.line_count}, Size: {result.size_bytes} bytes")
                print(result.content[:2000])
            else:
                print(f"Error: {result.error}")

    elif args.operation == "analyze":
        if not args.path:
            print("Error: --path required for analyze operation")
            return 1
        result = agent.analyze_module(args.path)
        if not args.json:
            print(f"\n=== Module Analysis: {args.path} ===")
            print(f"WSP 49 Compliance: {result['wsp_compliance']['score']*100:.0f}%")
            print(f"Total Files: {result['summary']['total_files']}")

    elif args.operation == "optimize":
        result = agent.run_optimization(
            objective=args.objective,
            max_iterations=args.iterations,
        )
        if not args.json:
            print(f"\n=== Optimization Results ===")
            print(f"Objective: {result.objective}")
            print(f"Best Score: {result.best_score:.4f}")
            print(f"Iterations: {result.iterations}")
            print(f"Convergence: {result.convergence}")

    elif args.operation == "research":
        result = agent.scan_research()
        if not args.json:
            print(f"\n=== Research Findings ===")
            for finding in result:
                print(f"\n[{finding['topic']}]")
                print(f"  {finding['summary'][:200]}...")

    elif args.operation == "audit":
        result = agent.audit_models()
        if not args.json:
            print(f"\n=== Model Audit ===")
            print(f"Current: {len(result.get('current', []))}")
            print(f"Legacy: {len(result.get('legacy', []))}")
            print(f"Deprecated: {len(result.get('deprecated', []))}")
            if result.get("migration_map"):
                print("\nMigrations needed:")
                for old, new in result["migration_map"].items():
                    print(f"  {old} -> {new}")

    elif args.operation == "status":
        result = agent.get_status()
        if not args.json:
            print("\n=== OpenClaw Codebase Agent Status ===")
            print(f"Repository: {result['repo_root']}")
            print(f"Components:")
            for comp, loaded in result["components"].items():
                status = "LOADED" if loaded else "NOT LOADED"
                print(f"  - {comp}: {status}")
            print(f"\nStatistics:")
            for stat, value in result["statistics"].items():
                print(f"  - {stat}: {value}")

    if args.json and result:
        import json as json_lib

        # Handle dataclass serialization
        if hasattr(result, "__dataclass_fields__"):
            result = {
                k: getattr(result, k)
                for k in result.__dataclass_fields__.keys()
            }

        print(json_lib.dumps(result, indent=2, default=str))

    return 0


if __name__ == "__main__":
    exit(main())
