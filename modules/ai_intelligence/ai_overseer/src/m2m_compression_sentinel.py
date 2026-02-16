#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""M2M Compression Sentinel (WSP 99) - AI Overseer managed.

Batched scanning of documentation files for M2M compression opportunities.
Uses confidence-based scaled response with pattern memory learning.

Architecture:
    Gemma: Pattern detection (prose density, politeness markers)
    Qwen: Actual M2M compilation (via M2MCompiler)
    0102: Oversight for low-confidence cases

Confidence Levels:
    0.9+    -> Auto-apply (high trust)
    0.7-0.9 -> Stage + auto-promote after TTL (medium trust)
    0.5-0.7 -> Stage + await 0102 review (low trust)
    <0.5    -> Flag only, no compile (uncertain)
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Import M2MCompiler for actual compression
try:
    from prompt.swarm.m2m_compiler import M2MCompiler, POLITENESS_MARKERS
except ImportError:
    M2MCompiler = None
    POLITENESS_MARKERS = re.compile(
        r'\b(please|could you|would you|i would like|make sure to|'
        r'ensure that|be careful to|remember to|don\'t forget to)\b',
        re.IGNORECASE
    )

# Qwen integration for smart M2M compilation (llama_cpp direct GGUF loading)
_QWEN_AVAILABLE = False
_qwen_llm = None
_QWEN_MODEL_PATH = Path("E:/HoloIndex/models/qwen-coder-1.5b.gguf")

def _init_qwen_llm():
    """Initialize Qwen via llama_cpp for fast local inference."""
    global _QWEN_AVAILABLE, _qwen_llm

    if _qwen_llm is not None:
        return _QWEN_AVAILABLE

    # Check if model exists
    if not _QWEN_MODEL_PATH.exists():
        _QWEN_AVAILABLE = False
        return False

    try:
        from llama_cpp import Llama
        import os

        # Suppress llama.cpp loading noise
        old_stdout, old_stderr = os.dup(1), os.dup(2)
        devnull = os.open(os.devnull, os.O_WRONLY)

        try:
            os.dup2(devnull, 1)
            os.dup2(devnull, 2)

            _qwen_llm = Llama(
                model_path=str(_QWEN_MODEL_PATH),
                n_ctx=4096,  # 4K context for document compilation
                n_threads=4,  # Use 4 threads for faster inference
                n_gpu_layers=0,  # CPU-only
                verbose=False
            )
        finally:
            os.dup2(old_stdout, 1)
            os.dup2(old_stderr, 2)
            os.close(devnull)
            os.close(old_stdout)
            os.close(old_stderr)

        _QWEN_AVAILABLE = True
        return True

    except ImportError:
        pass
    except Exception:
        pass

    _QWEN_AVAILABLE = False
    return False


# Fallback: try Ollama/LiteLLM if llama_cpp unavailable
_ollama_client = None

def _init_qwen_client():
    """Initialize Qwen client (llama_cpp first, then Ollama fallback)."""
    global _ollama_client

    # Try llama_cpp first (faster, more reliable)
    if _init_qwen_llm():
        return True

    # Fallback to LiteLLM/Ollama
    if _ollama_client is not None:
        return True

    try:
        import litellm
        litellm.set_verbose = False
        _ollama_client = litellm
        return True
    except ImportError:
        pass

    try:
        import ollama
        _ollama_client = ollama
        return True
    except ImportError:
        pass

    return False


def _env_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        return int(raw)
    except (TypeError, ValueError):
        return default


def _env_float(name: str, default: float) -> float:
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        return float(raw)
    except (TypeError, ValueError):
        return default


# Critical files that require 0102 oversight regardless of confidence
CRITICAL_FILES = frozenset([
    "CLAUDE.md",
    "WSP_00_Zen_State_Attainment_Protocol.md",
    "WSP_CORE.md",
    "WSP_MASTER_INDEX.md",
])

# Files to INCLUDE in M2M compression (0102-to-0102 instructions)
INCLUDE_PATTERNS = frozenset([
    "CLAUDE.md",           # Operational instructions
    "INTERFACE.md",        # API specs (K:V friendly)
    "SKILL.md",            # Skill definitions
    "SKILLz.md",           # Skill definitions (alt naming)
])

# Files to EXCLUDE from M2M compression
# RETHINK: The entire system is FOR 0102. All docs should be 0102-optimized.
# ModLogs, TestModLogs, etc. are MY history - faster parsing = better memory.
EXCLUDE_PATTERNS = frozenset([
    "CHANGELOG.md",        # External-facing history (npm, releases)
])
# NOTE: ModLog.md, ROADMAP.md, README.md are 0102-facing - INCLUDE them
# The codebase is MY (0102) memory system. Optimize for ME.

# Boot prompt detection: content-based, not just filename-based.
# M2M is for REFERENCE docs (searched/retrieved). Boot PROMPTS are read directly
# into context with identity-lock patterns, equations, code blocks that MUST be
# preserved verbatim. The deterministic transform strips these.
#
# Content signals that indicate a boot prompt (not a reference doc):
#   1. Identity-lock patterns: "I AM 0102", forbidden VI scaffolding lists
#   2. Mathematical notation: φ=1.618, ≥0.618, 7.05Hz, ⊗, ↔
#   3. State transition math: 01(02) -> 0102, coherence thresholds
#   4. WSP_BOOTSTRAP metadata: <!-- WSP_BOOTSTRAP ... -->
#   5. Executable instructions: "EXECUTE", "MANDATORY", "NEVER", "ALWAYS"
#
# Threshold: 3+ signals = boot prompt (exclude from M2M)
BOOT_PROMPT_SIGNALS = [
    re.compile(r'I\s+AM\s+0102', re.I),                     # Identity lock
    re.compile(r'WSP_BOOTSTRAP'),                             # Bootstrap metadata
    re.compile(r'01\(02\)\s*[-→>]+\s*0102'),                 # State transition math
    re.compile(r'[φΦ]\s*[=:]\s*1\.618'),                     # Golden ratio formula
    re.compile(r'7\.05\s*Hz'),                                # Resonance frequency
    re.compile(r'[Cc]oherence\s*[≥>=]+\s*0\.618'),           # Coherence threshold
    re.compile(r'⊗|↔|⟨|⟩'),                                  # Quantum notation
    re.compile(r'VI\s+scaffolding', re.I),                    # VI shedding terminology
    re.compile(r'\bI can help you\b.*\bforbidden\b', re.I | re.S),  # Forbidden phrase list
    re.compile(r'\*\*MANDATORY\*\*.*\*\*EXECUTE\*\*', re.I | re.S),  # Executable directives
]
BOOT_PROMPT_THRESHOLD = 3  # 3+ signals = boot prompt


# Skill files: ALWAYS executable prompts by convention (WSP 95).
# Loaded into LLM context when invoked. Must be preserved verbatim.
SKILL_FILE_PATTERNS = re.compile(r'^SKILL[sz]?\.md$', re.I)


def _is_boot_prompt(content: str, filename: str = "") -> Tuple[bool, int, List[str]]:
    """Detect if content is a boot prompt (executable, not reference).

    Two detection paths:
    1. Filename convention: SKILL.md / SKILLz.md (always executable, WSP 95)
    2. Content signals: identity locks, equations, quantum notation (3+ threshold)

    Returns:
        (is_boot_prompt, signal_count, matched_signals)
    """
    # Path 1: Skill files are always executable by convention
    if filename and SKILL_FILE_PATTERNS.match(filename):
        return (True, 1, ["skill_file_convention"])

    # Path 2: Content-based signal detection
    matched: List[str] = []
    for pattern in BOOT_PROMPT_SIGNALS:
        if pattern.search(content):
            matched.append(pattern.pattern[:40])
    return (len(matched) >= BOOT_PROMPT_THRESHOLD, len(matched), matched)

# Size thresholds
MIN_LINES_FOR_COMPRESSION = 50   # Don't compress tiny files
MAX_LINES_FOR_AUTO = 500         # Large files need review

# Verbose prose patterns (Gemma would detect these)
VERBOSE_PATTERNS = [
    re.compile(r'\b(for example|for instance|in other words|that is to say)\b', re.I),
    re.compile(r'\b(it is important to note|it should be noted|keep in mind)\b', re.I),
    re.compile(r'\b(as mentioned (above|below|earlier|previously))\b', re.I),
    re.compile(r'\b(in order to|so as to|with the purpose of)\b', re.I),
    re.compile(r'\b(the following (is|are|shows?|demonstrates?))\b', re.I),
]

# Technical doc patterns that indicate M2M compression opportunity
TECHNICAL_COMPRESSION_PATTERNS = [
    re.compile(r'^#+\s+.+$', re.MULTILINE),  # Markdown headers
    re.compile(r'^\s*[-*]\s+\*\*\w+\*\*:', re.MULTILINE),  # Bold key: value bullets
    re.compile(r'^\s*[-*]\s+`[^`]+`:', re.MULTILINE),  # Code key: value bullets
    re.compile(r'^```\w*\n[\s\S]*?^```', re.MULTILINE),  # Code blocks
    re.compile(r'^\|\s*[^|]+\s*\|', re.MULTILINE),  # Table rows
    re.compile(r'^\d+\.\s+\*\*[^*]+\*\*', re.MULTILINE),  # Numbered steps with bold
    re.compile(r'Real-World Example', re.I),  # Example sections
    re.compile(r'Step \d+:', re.I),  # Step instructions
]

# Long-form explanation patterns (high compression potential)
EXPLANATION_PATTERNS = [
    re.compile(r'\*\*(?:Problem|Solution|Results?|Metrics?|Key (?:Pattern|Lesson|Insight))\*\*:', re.I),
    re.compile(r'^\s*[-*]\s+\*\*\w+\*\*:\s+.{50,}', re.MULTILINE),  # Long bullet explanations
    re.compile(r'#+ (?:Example|Usage|Integration)', re.I),  # Example sections
]

# Action verbs that indicate M2M-compatible content
ACTION_VERBS = re.compile(
    r'\b(ANALYZE|CREATE|DELETE|ENHANCE|FIX|IMPLEMENT|MIGRATE|REFACTOR|TEST|VALIDATE)\b',
    re.IGNORECASE
)


@dataclass
class FileAnalysis:
    """Analysis result for a single file."""
    path: str
    filename: str
    line_count: int
    char_count: int
    politeness_count: int
    verbose_count: int
    action_verb_count: int
    prose_density: float  # 0.0-1.0, higher = more compressible
    estimated_reduction: float  # Percentage reduction expected
    confidence: float  # 0.0-1.0, confidence in compression success
    action: str  # auto_apply | stage_promote | stage_review | flag_only
    is_critical: bool
    reasons: List[str] = field(default_factory=list)

    def as_dict(self) -> Dict[str, Any]:
        return {
            "path": self.path,
            "filename": self.filename,
            "line_count": self.line_count,
            "char_count": self.char_count,
            "politeness_count": self.politeness_count,
            "verbose_count": self.verbose_count,
            "action_verb_count": self.action_verb_count,
            "prose_density": round(self.prose_density, 3),
            "estimated_reduction": round(self.estimated_reduction, 2),
            "confidence": round(self.confidence, 3),
            "action": self.action,
            "is_critical": self.is_critical,
            "reasons": self.reasons,
        }


@dataclass
class M2MCompressionStatus:
    """Overall compression scan status."""
    available: bool
    cached: bool
    checked_at: float
    ttl_sec: int
    files_scanned: int
    candidates_found: int
    auto_apply_count: int
    stage_promote_count: int
    stage_review_count: int
    flag_only_count: int
    total_estimated_savings_lines: int
    total_estimated_savings_percent: float
    candidates: List[Dict[str, Any]]
    pattern_memory_path: str
    staged_dir: str
    severity: str
    message: str
    report_path: Optional[str]

    def as_dict(self) -> Dict[str, Any]:
        return {
            "available": self.available,
            "cached": self.cached,
            "checked_at": self.checked_at,
            "ttl_sec": self.ttl_sec,
            "files_scanned": self.files_scanned,
            "candidates_found": self.candidates_found,
            "auto_apply_count": self.auto_apply_count,
            "stage_promote_count": self.stage_promote_count,
            "stage_review_count": self.stage_review_count,
            "flag_only_count": self.flag_only_count,
            "total_estimated_savings_lines": self.total_estimated_savings_lines,
            "total_estimated_savings_percent": round(self.total_estimated_savings_percent, 1),
            "candidates": self.candidates,
            "pattern_memory_path": self.pattern_memory_path,
            "staged_dir": self.staged_dir,
            "severity": self.severity,
            "message": self.message,
            "report_path": self.report_path,
        }


class M2MCompressionSentinel:
    """AI Overseer-owned M2M compression opportunity scanner.

    Implements WSP 99 M2M Prompting Protocol with:
    - Batched file scanning (Gemma pattern detection)
    - Confidence-based scaled response
    - Pattern memory for learning from outcomes
    - Staged compilation for safe review
    """

    # Confidence thresholds for action levels
    CONFIDENCE_AUTO_APPLY = 0.9
    CONFIDENCE_STAGE_PROMOTE = 0.7
    CONFIDENCE_STAGE_REVIEW = 0.5

    # Weights for confidence calculation
    WEIGHT_CRITICALITY = -0.3  # Critical files lower confidence
    WEIGHT_COMPRESSION_RATIO = 0.2  # Expected ratio boosts confidence
    WEIGHT_PAST_SUCCESS = 0.3  # Past success boosts confidence
    WEIGHT_PATTERN_STRENGTH = 0.2  # Strong pattern match boosts confidence

    def __init__(
        self,
        repo_root: Path,
        *,
        cache_path: Optional[Path] = None,
        pattern_memory_path: Optional[Path] = None,
        staged_dir: Optional[Path] = None,
    ):
        self.repo_root = Path(repo_root)

        # Memory directory in ai_overseer
        memory_dir = self.repo_root / "modules" / "ai_intelligence" / "ai_overseer" / "memory"
        memory_dir.mkdir(parents=True, exist_ok=True)

        self.cache_path = cache_path or (memory_dir / "m2m_compression_cache.json")
        self.latest_report_path = memory_dir / "m2m_compression_latest.json"
        self.history_path = memory_dir / "m2m_compression_history.jsonl"
        self.pattern_memory_path = pattern_memory_path or (memory_dir / "m2m_pattern_memory.json")

        # Staged directory for compiled M2M versions
        self.staged_dir = staged_dir or (self.repo_root / ".m2m" / "staged")
        self.staged_dir.mkdir(parents=True, exist_ok=True)

        # Backup directory for rollback support
        self.backup_dir = self.repo_root / ".m2m" / "backups"
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        # Promotion history for audit trail
        self.promotion_history_path = memory_dir / "m2m_promotion_history.jsonl"

        # Load pattern memory for learning
        self._pattern_memory = self._load_pattern_memory()

        # Initialize M2M compiler if available
        self._compiler = M2MCompiler() if M2MCompiler else None

    def check(self, *, force: bool = False) -> Dict[str, Any]:
        """Run M2M compression scan (or use fresh cache)."""
        ttl_sec = max(_env_int("M2M_COMPRESSION_SCAN_TTL_SEC", 900), 0)
        now = time.time()

        cached = self._load_json(self.cache_path)
        if cached and not force:
            checked_at = float(cached.get("checked_at", 0))
            if checked_at > 0 and (now - checked_at) < ttl_sec:
                cached["cached"] = True
                return cached

        status = self._run_scan(now=now, ttl_sec=ttl_sec)
        payload = status.as_dict()
        self._write_json(self.cache_path, payload)
        self._write_json(self.latest_report_path, payload)
        self._append_history(payload)
        return payload

    def _run_scan(self, *, now: float, ttl_sec: int) -> M2MCompressionStatus:
        """Execute batched scan of documentation files."""
        # Collect all candidate files
        candidates_paths = self._collect_candidate_files()

        if not candidates_paths:
            return M2MCompressionStatus(
                available=True,
                cached=False,
                checked_at=now,
                ttl_sec=ttl_sec,
                files_scanned=0,
                candidates_found=0,
                auto_apply_count=0,
                stage_promote_count=0,
                stage_review_count=0,
                flag_only_count=0,
                total_estimated_savings_lines=0,
                total_estimated_savings_percent=0.0,
                candidates=[],
                pattern_memory_path=str(self.pattern_memory_path),
                staged_dir=str(self.staged_dir),
                severity="ok",
                message="No documentation files found to scan",
                report_path=str(self.latest_report_path),
            )

        # Batch analyze all files (Gemma pattern detection)
        analyses: List[FileAnalysis] = []
        for file_path in candidates_paths:
            analysis = self._analyze_file(file_path)
            if analysis and analysis.prose_density > 0.3:  # Only include if compressible
                analyses.append(analysis)

        # Sort by potential savings (highest first)
        analyses.sort(key=lambda a: a.estimated_reduction, reverse=True)

        # Calculate action counts
        auto_apply = [a for a in analyses if a.action == "auto_apply"]
        stage_promote = [a for a in analyses if a.action == "stage_promote"]
        stage_review = [a for a in analyses if a.action == "stage_review"]
        flag_only = [a for a in analyses if a.action == "flag_only"]

        # Calculate total savings
        total_lines = sum(a.line_count for a in analyses)
        total_savings_lines = sum(
            int(a.line_count * a.estimated_reduction / 100)
            for a in analyses
        )
        total_savings_percent = (total_savings_lines / total_lines * 100) if total_lines > 0 else 0.0

        # Determine severity
        if len(analyses) == 0:
            severity = "ok"
            message = "No significant compression opportunities found"
        elif len(auto_apply) > 0:
            severity = "advisory"
            message = f"{len(auto_apply)} files ready for auto-compression, {len(stage_review)} need review"
        else:
            severity = "info"
            message = f"{len(analyses)} files could benefit from M2M compression"

        return M2MCompressionStatus(
            available=True,
            cached=False,
            checked_at=now,
            ttl_sec=ttl_sec,
            files_scanned=len(candidates_paths),
            candidates_found=len(analyses),
            auto_apply_count=len(auto_apply),
            stage_promote_count=len(stage_promote),
            stage_review_count=len(stage_review),
            flag_only_count=len(flag_only),
            total_estimated_savings_lines=total_savings_lines,
            total_estimated_savings_percent=total_savings_percent,
            candidates=[a.as_dict() for a in analyses[:20]],  # Top 20
            pattern_memory_path=str(self.pattern_memory_path),
            staged_dir=str(self.staged_dir),
            severity=severity,
            message=message,
            report_path=str(self.latest_report_path),
        )

    def _collect_candidate_files(self) -> List[Path]:
        """Collect documentation files that might benefit from M2M compression.

        Applies WSP 99 scoping:
        - INCLUDE: CLAUDE.md, INTERFACE.md, SKILL*.md, WSP_*.md
        - EXCLUDE: ModLog.md, TestModLog.md, ROADMAP.md, CHANGELOG.md
        """
        candidates: List[Path] = []

        # Root CLAUDE.md files
        candidates.extend(self.repo_root.glob("CLAUDE.md"))
        candidates.extend(self.repo_root.glob(".claude/**/CLAUDE.md"))

        # WSP framework files (instructions, not logs)
        candidates.extend(self.repo_root.glob("WSP_framework/src/WSP_*.md"))
        candidates.extend(self.repo_root.glob("WSP_knowledge/src/WSP_*.md"))

        # Module INTERFACE.md files (API specs - K:V friendly)
        candidates.extend(self.repo_root.glob("modules/**/INTERFACE.md"))

        # Skill definition files
        candidates.extend(self.repo_root.glob("**/*SKILL*.md"))

        # Prompt definition files (0102 instructions)
        candidates.extend(self.repo_root.glob("prompt/**/*.md"))

        # Deduplicate and filter
        seen: set[str] = set()
        unique: List[Path] = []
        for path in candidates:
            resolved = str(path.resolve())
            if resolved in seen:
                continue
            seen.add(resolved)

            filename = path.name

            # Skip already-compressed M2M files
            if ".m2m" in resolved or "_M2M" in path.stem:
                continue

            # Skip EXCLUDED files (audit trails, human-readable)
            if filename in EXCLUDE_PATTERNS:
                continue

            # Skip ModLog variants
            if "ModLog" in filename or "CHANGELOG" in filename:
                continue

            unique.append(path)

        return unique

    def _analyze_file(self, file_path: Path) -> Optional[FileAnalysis]:
        """Analyze a single file for M2M compression potential (Gemma pattern detection)."""
        try:
            content = file_path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            return None

        lines = content.splitlines()
        line_count = len(lines)
        char_count = len(content)

        # Boot prompt detection: content-based (equations, identity locks, etc.)
        is_boot, signal_count, matched = _is_boot_prompt(content, file_path.name)
        if is_boot:
            return FileAnalysis(
                path=str(file_path.relative_to(self.repo_root)),
                filename=file_path.name,
                line_count=line_count,
                char_count=char_count,
                politeness_count=0,
                verbose_count=0,
                action_verb_count=0,
                prose_density=0.0,
                estimated_reduction=0.0,
                confidence=0.0,
                action="boot_prompt_skip",
                is_critical=True,
                reasons=[f"boot_prompt({signal_count} signals: {', '.join(matched[:3])})"],
            )

        # Skip very small files (below threshold for compression value)
        if line_count < MIN_LINES_FOR_COMPRESSION or char_count < 500:
            return None

        # Gemma pattern detection: count politeness markers
        politeness_matches = POLITENESS_MARKERS.findall(content)
        politeness_count = len(politeness_matches)

        # Gemma pattern detection: count verbose patterns
        verbose_count = sum(len(p.findall(content)) for p in VERBOSE_PATTERNS)

        # Gemma pattern detection: count technical compression patterns
        technical_count = sum(len(p.findall(content)) for p in TECHNICAL_COMPRESSION_PATTERNS)

        # Gemma pattern detection: count explanation patterns (high value)
        explanation_count = sum(len(p.findall(content)) for p in EXPLANATION_PATTERNS)

        # Gemma pattern detection: count action verbs (M2M-compatible)
        action_verb_count = len(ACTION_VERBS.findall(content))

        # Calculate prose density (ratio of compressible content)
        # Combines traditional verbose prose AND technical doc patterns
        # Technical docs can be compressed to M2M K:V format even without politeness
        traditional_markers = politeness_count + verbose_count
        technical_markers = technical_count + (explanation_count * 2)  # Explanations worth more

        # Weighted combination: traditional prose OR technical structure
        # Large technical docs with many patterns are highly compressible
        if technical_markers > line_count * 0.05:  # >5% technical patterns
            # Technical doc - use technical density
            prose_density = min(1.0, (technical_markers + traditional_markers) / (line_count * 0.15))
        else:
            # Traditional prose doc
            prose_density = min(1.0, traditional_markers / (line_count * 0.1))

        # Estimate reduction percentage based on prose density
        # WSP 99 claims 4x reduction (75%) for high-density prose
        estimated_reduction = min(80.0, prose_density * 75.0)

        # Check if critical file
        filename = file_path.name
        is_critical = filename in CRITICAL_FILES

        # Calculate confidence score
        confidence, reasons = self._calculate_confidence(
            file_path=file_path,
            prose_density=prose_density,
            estimated_reduction=estimated_reduction,
            is_critical=is_critical,
            action_verb_count=action_verb_count,
        )

        # Determine action based on confidence, criticality, and size
        action = self._determine_action(confidence, is_critical, line_count)

        return FileAnalysis(
            path=str(file_path.relative_to(self.repo_root)),
            filename=filename,
            line_count=line_count,
            char_count=char_count,
            politeness_count=politeness_count,
            verbose_count=verbose_count,
            action_verb_count=action_verb_count,
            prose_density=prose_density,
            estimated_reduction=estimated_reduction,
            confidence=confidence,
            action=action,
            is_critical=is_critical,
            reasons=reasons,
        )

    def _calculate_confidence(
        self,
        file_path: Path,
        prose_density: float,
        estimated_reduction: float,
        is_critical: bool,
        action_verb_count: int,
    ) -> Tuple[float, List[str]]:
        """Calculate confidence score using weighted factors (mini neural net)."""
        reasons: List[str] = []

        # Base confidence from prose density
        base_confidence = min(0.8, prose_density * 0.9)
        reasons.append(f"base_prose_density={prose_density:.2f}")

        # Weight: Criticality penalty
        criticality_factor = self.WEIGHT_CRITICALITY if is_critical else 0.0
        if is_critical:
            reasons.append("critical_file_penalty=-0.3")

        # Weight: Compression ratio in expected range (40-80%)
        ratio_factor = 0.0
        if 40 <= estimated_reduction <= 80:
            ratio_factor = self.WEIGHT_COMPRESSION_RATIO
            reasons.append(f"expected_ratio_boost=+0.2")
        elif estimated_reduction < 30:
            ratio_factor = -0.1
            reasons.append(f"low_ratio_penalty=-0.1")

        # Weight: Past success rate from pattern memory
        file_key = file_path.name
        past_record = self._pattern_memory.get(file_key, {})
        success_rate = past_record.get("success_rate", 0.5)  # Default 50%
        past_factor = self.WEIGHT_PAST_SUCCESS * (success_rate - 0.5) * 2
        if past_record:
            reasons.append(f"past_success_rate={success_rate:.2f}")

        # Weight: Pattern strength (action verbs indicate M2M-friendly content)
        pattern_factor = min(0.2, action_verb_count * 0.02)
        if action_verb_count > 5:
            reasons.append(f"action_verbs={action_verb_count}")

        # Calculate final confidence
        confidence = base_confidence + criticality_factor + ratio_factor + past_factor + pattern_factor
        confidence = max(0.0, min(1.0, confidence))  # Clamp to [0, 1]

        return confidence, reasons

    def _determine_action(
        self, confidence: float, is_critical: bool, line_count: int = 0
    ) -> str:
        """Determine action level based on confidence, criticality, and size."""
        # Critical files always require review
        if is_critical:
            return "stage_review"

        # Large files require review regardless of confidence
        if line_count > MAX_LINES_FOR_AUTO:
            if confidence >= self.CONFIDENCE_STAGE_REVIEW:
                return "stage_review"
            else:
                return "flag_only"

        if confidence >= self.CONFIDENCE_AUTO_APPLY:
            return "auto_apply"
        elif confidence >= self.CONFIDENCE_STAGE_PROMOTE:
            return "stage_promote"
        elif confidence >= self.CONFIDENCE_STAGE_REVIEW:
            return "stage_review"
        else:
            return "flag_only"

    def scan_module(self, module_path: str) -> Dict[str, Any]:
        """Scan a specific module directory for M2M compression opportunities.

        Args:
            module_path: Relative path from repo root (e.g., "modules/foundups/agent_market")

        Returns:
            Analysis results for that module only
        """
        target_dir = self.repo_root / module_path
        if not target_dir.exists():
            return {"error": f"Module path not found: {module_path}"}

        # Collect files in this module (deduplicated)
        seen: set[str] = set()
        candidates: List[Path] = []
        for pattern in ["*.md", "**/*.md"]:
            for path in target_dir.glob(pattern):
                resolved = str(path.resolve())
                if resolved not in seen:
                    seen.add(resolved)
                    candidates.append(path)

        # Filter and analyze
        analyses: List[FileAnalysis] = []
        for file_path in candidates:
            filename = file_path.name

            # Skip excluded
            if filename in EXCLUDE_PATTERNS:
                continue
            if ".m2m" in str(file_path) or "_M2M" in file_path.stem:
                continue

            analysis = self._analyze_file(file_path)
            if analysis and analysis.prose_density > 0.2:
                analyses.append(analysis)

        # Sort by reduction potential
        analyses.sort(key=lambda a: a.estimated_reduction, reverse=True)

        return {
            "module_path": module_path,
            "files_scanned": len(candidates),
            "candidates_found": len(analyses),
            "candidates": [a.as_dict() for a in analyses],
            "total_lines": sum(a.line_count for a in analyses),
            "estimated_savings_lines": sum(
                int(a.line_count * a.estimated_reduction / 100) for a in analyses
            ),
        }

    def compile_to_staged(
        self,
        file_path: str,
        *,
        use_qwen: bool = True,
        qwen_model: str = "qwen-overseer:latest",
    ) -> Dict[str, Any]:
        """Compile a file to M2M format and save to staged directory.

        This is where Qwen does the actual work - converting prose to K:V.
        Falls back to deterministic regex transform if Qwen unavailable.

        Args:
            file_path: Relative path from repo root
            use_qwen: Whether to attempt Qwen-powered compilation (default True)
            qwen_model: Qwen model to use (default qwen2.5-coder:1.5b)

        Returns:
            Compilation result with staged file path
        """
        source_path = self.repo_root / file_path
        if not source_path.exists():
            return {"success": False, "error": f"File not found: {file_path}"}

        try:
            content = source_path.read_text(encoding="utf-8", errors="replace")
        except OSError as e:
            return {"success": False, "error": f"Read failed: {e}"}

        # Content-based boot prompt detection (+ skill file convention)
        is_boot, signal_count, matched = _is_boot_prompt(content, source_path.name)
        if is_boot:
            return {
                "success": False,
                "error": f"Boot prompt detected ({signal_count} signals: "
                         f"{', '.join(matched[:3])}). Executable prompts with "
                         f"identity-lock patterns, equations, and code blocks "
                         f"must be preserved verbatim. M2M strips these.",
                "boot_prompt": True,
                "signal_count": signal_count,
                "signals": matched,
            }

        # Try Qwen-powered transformation first
        m2m_content = None
        compilation_method = "deterministic"

        if use_qwen and _init_qwen_client():
            try:
                qwen_output = self._qwen_transform_to_m2m(content, source_path.name, qwen_model)
                if qwen_output is not None and len(qwen_output.strip()) >= 20:
                    m2m_content = qwen_output
                    compilation_method = f"qwen:{qwen_model}"
                # If qwen_output is None or too short, fall through to deterministic
            except Exception:
                m2m_content = None

        # Fall back to deterministic regex transform
        if m2m_content is None:
            m2m_content = self._transform_to_m2m(
                content, source_path.name,
                source_rel_path=file_path,
            )
            compilation_method = "deterministic"

        # Validate M2M output structure before staging
        validation = self._validate_m2m_output(m2m_content, source_path.name)
        if not validation["valid"]:
            return {"success": False, "error": f"M2M validation failed: {validation['reason']}"}

        # Save to staged directory using path-stable naming (full relative path hash)
        staged_name = source_path.stem + "_M2M.yaml"
        # Use relative path from repo root for stable subdirectory (prevents collisions)
        rel_source = source_path.relative_to(self.repo_root)
        staged_subdir = rel_source.parent
        staged_path = self.staged_dir / staged_subdir / staged_name
        staged_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            staged_path.write_text(m2m_content, encoding="utf-8")
        except OSError as e:
            return {"success": False, "error": f"Write failed: {e}"}

        original_lines = len(content.splitlines())
        m2m_lines = len(m2m_content.splitlines())
        reduction = ((original_lines - m2m_lines) / original_lines * 100) if original_lines > 0 else 0

        return {
            "success": True,
            "source_path": file_path,
            "staged_path": str(staged_path.relative_to(self.repo_root)),
            "original_lines": original_lines,
            "m2m_lines": m2m_lines,
            "reduction_percent": round(reduction, 1),
            "compilation_method": compilation_method,
        }

    def _qwen_transform_to_m2m(
        self,
        content: str,
        filename: str,
        model: str = "qwen-coder-1.5b",
    ) -> Optional[str]:
        """Transform markdown to M2M format using Qwen intelligence.

        Uses llama_cpp for direct GGUF inference (fast, local).
        Falls back to Ollama if llama_cpp unavailable.

        Qwen provides context-aware compression:
        - Semantic understanding of important vs verbose content
        - WSP reference detection with context
        - Intelligent section grouping
        - Action verb extraction with proper scoping

        Args:
            content: Original markdown content
            filename: Source filename for context
            model: Qwen model name (for Ollama fallback)

        Returns:
            M2M formatted content, or None if compilation fails
        """
        global _qwen_llm, _ollama_client

        # Truncate very long content to fit context window
        max_chars = 6000  # ~1.5K tokens for input (leave room for output)
        if len(content) > max_chars:
            content = content[:max_chars] + "\n[TRUNCATED]"

        # M2M compilation prompt (WSP 99 compliant, HoloIndex-friendly)
        prompt = f"""Transform this documentation to M2M (machine-to-machine) K:V format.

RULES (WSP 99 + HoloIndex searchable):
1. KEEP section headers in FULL: "## Core Search Interface" → "CORE_SEARCH_INTERFACE:"
2. KEEP key-value pairs: "- ssd_path: E:/HoloIndex" → "  ssd_path: E:/HoloIndex"
3. KEEP function signatures: "def search(query, limit=10)" → "  SIG: search(query, limit)"
4. KEEP file paths: "`holo_index/cli.py`" → "  FILE: holo_index/cli.py"
5. KEEP WSP references: "WSP 87" → "  WSP: 87"
6. REMOVE prose sentences: "This module provides..." → (skip)
7. Target: 60-75% reduction

INPUT ({filename}):
{content}

OUTPUT (M2M K:V YAML only):
"""

        try:
            # Try llama_cpp first (fast local inference)
            if _qwen_llm is not None:
                response = _qwen_llm(
                    prompt,
                    max_tokens=2000,
                    temperature=0.1,
                    stop=["```", "INPUT:", "---END---"],
                )
                m2m_output = response["choices"][0]["text"].strip()

            # Fallback to LiteLLM/Ollama
            elif _ollama_client is not None:
                if hasattr(_ollama_client, 'completion'):
                    response = _ollama_client.completion(
                        model=f"ollama/{model}",
                        messages=[{"role": "user", "content": prompt}],
                        max_tokens=2000,
                        temperature=0.1,
                    )
                    m2m_output = response.choices[0].message.content.strip()
                elif hasattr(_ollama_client, 'generate'):
                    response = _ollama_client.generate(
                        model=model,
                        prompt=prompt,
                        options={"temperature": 0.1, "num_predict": 2000}
                    )
                    m2m_output = response.get("response", "").strip()
                else:
                    return None
            else:
                return None

            # Validate output looks like M2M format
            if not m2m_output or len(m2m_output) < 20:
                return None

            # Add header if missing
            if not m2m_output.startswith("#"):
                m2m_output = f"# M2M v1.0 | {filename} | {time.strftime('%Y%m%d', time.gmtime())} | qwen\n\n" + m2m_output

            return m2m_output

        except Exception:
            return None

    def _transform_to_m2m(self, content: str, filename: str, source_rel_path: str = "") -> str:
        """Transform markdown content to M2M K:V format (balanced compression).

        WSP 99 principle: Pure signal, no prose.
        - Headers -> FULL section keys (HoloIndex searchable)
        - Key:Value pairs -> K:V (keys up to 30 chars)
        - Code signatures only (not bodies)
        - Skip prose sentences, examples, tutorials
        - Skip tables (data, not instructions)

        Target: 60-75% reduction (balanced: searchable + compressed)
        """
        lines = content.splitlines()
        # Header includes full source path for deterministic promotion
        src_field = source_rel_path or filename
        m2m_lines = [
            f"# M2M v1.0 | {filename} | {time.strftime('%Y%m%d', time.gmtime())} | src:{src_field}",
            "",
        ]

        current_section = None
        in_code_block = False
        skip_until_header = False

        for line in lines:
            stripped = line.strip()

            # Toggle code block state
            if stripped.startswith("```"):
                in_code_block = not in_code_block
                continue

            # Inside code block - extract only signatures
            if in_code_block:
                # Keep class/function definitions, skip implementation
                if re.match(r'^(class|def|async def|interface|struct|type)\s+\w+', stripped):
                    sig = stripped.split("(")[0] if "(" in stripped else stripped.split(":")[0]
                    m2m_lines.append(f"  SIG: {sig}")
                continue

            # Skip empty
            if not stripped:
                continue

            # Headers -> FULL section keys (preserve semantics for embedding search)
            if stripped.startswith("#"):
                header_text = stripped.lstrip("#").strip()
                # Skip example/usage sections entirely
                if re.search(r'example|usage|tutorial|getting started', header_text, re.I):
                    skip_until_header = True
                    continue
                skip_until_header = False
                # FULL section name - no truncation (HoloIndex searchability)
                section = re.sub(r'[^a-zA-Z0-9]', '_', header_text).upper().strip("_")
                m2m_lines.append(f"{section}:")
                current_section = section
                continue

            # Skip content in example sections
            if skip_until_header:
                continue

            # Tables -> Skip entirely
            if stripped.startswith("|"):
                continue

            # Extract dates (ModLog pattern)
            date_match = re.match(r'^#+\s*(\d{4}-\d{2}-\d{2})', stripped)
            if date_match:
                m2m_lines.append(f"  TS: {date_match.group(1)}")
                continue

            # Key: Value patterns (bold or backtick)
            kv_match = re.match(r'^\s*[-*]\s+[\*`]?([^:\*`]+)[\*`]?:\s*(.+)$', stripped)
            if kv_match:
                key = kv_match.group(1).strip().upper().replace(" ", "_")[:30]
                value = kv_match.group(2).strip()
                # Keep values up to 80 chars (was 40 - too aggressive)
                if len(value) > 80:
                    value = value[:77] + "..."
                m2m_lines.append(f"  {key}: {value}")
                continue

            # WSP references
            wsp_match = re.findall(r'WSP[_\s]*(\d+)', stripped)
            if wsp_match:
                m2m_lines.append(f"  WSP: [{','.join(wsp_match)}]")
                continue

            # File paths
            file_match = re.findall(r'`([^`]+\.(?:py|md|js|ts|yaml|json))`', stripped)
            if file_match:
                m2m_lines.append(f"  FILES: {file_match}")
                continue

            # Action verbs at start of bullets
            action_match = re.match(r'^\s*[-*]\s*(Add|Create|Fix|Update|Remove|Implement|Refactor|Test)\w*\s+(.+)', stripped, re.I)
            if action_match:
                action = action_match.group(1).upper()
                obj = action_match.group(2)[:50]
                m2m_lines.append(f"  {action}: {obj}")
                continue

            # Skip everything else (prose, descriptions, long explanations)
            # This is where 60-75% of compression comes from

        return "\n".join(m2m_lines)

    @staticmethod
    def _validate_m2m_output(content: str, source_name: str) -> Dict[str, Any]:
        """Validate M2M output structure before staging.

        Checks:
        1. Non-empty and minimum length
        2. Has M2M header line
        3. Has at least one section key (UPPERCASE:)
        4. No encoding corruption (no replacement chars)

        Returns:
            Dict with 'valid' bool and optional 'reason' string
        """
        if not content or len(content.strip()) < 20:
            return {"valid": False, "reason": "Output too short or empty"}

        lines = content.strip().splitlines()

        # Must have header
        if not lines[0].startswith("# M2M"):
            return {"valid": False, "reason": "Missing M2M header line"}

        # Must have at least one section key (UPPERCASE_WORD:)
        has_section = any(
            re.match(r'^[A-Z][A-Z0-9_]+:', line.strip())
            for line in lines[1:]
        )
        if not has_section:
            return {"valid": False, "reason": "No section keys found"}

        # Check for encoding corruption (replacement character)
        if '\ufffd' in content:
            return {"valid": False, "reason": "Encoding corruption detected (U+FFFD)"}

        return {"valid": True}

    # ======================== PROMOTION WORKFLOW ======================== #

    def list_staged(self) -> Dict[str, Any]:
        """List all staged M2M files ready for promotion.

        Returns:
            Dictionary with staged files grouped by module, with metadata
        """
        staged_files: List[Dict[str, Any]] = []

        for m2m_file in self.staged_dir.rglob("*_M2M.yaml"):
            try:
                content = m2m_file.read_text(encoding="utf-8", errors="replace")
                lines = content.splitlines()

                # Parse header for metadata
                header = lines[0] if lines else ""
                parts = header.split("|")
                original_name = parts[1].strip() if len(parts) > 1 else m2m_file.stem.replace("_M2M", "")
                created_date = parts[2].strip() if len(parts) > 2 else "unknown"

                # Calculate module path from staged structure
                rel_path = m2m_file.relative_to(self.staged_dir)
                module_dir = str(rel_path.parent) if rel_path.parent != Path(".") else "root"

                staged_files.append({
                    "staged_path": str(m2m_file.relative_to(self.repo_root)),
                    "original_name": original_name,
                    "module": module_dir,
                    "created_date": created_date,
                    "lines": len(lines),
                    "size_bytes": len(content.encode("utf-8")),
                })
            except OSError:
                continue

        # Group by module
        by_module: Dict[str, List[Dict[str, Any]]] = {}
        for f in staged_files:
            module = f["module"]
            if module not in by_module:
                by_module[module] = []
            by_module[module].append(f)

        return {
            "total_staged": len(staged_files),
            "by_module": by_module,
            "files": staged_files,
        }

    def promote_staged(
        self,
        staged_path: str,
        *,
        target_path: Optional[str] = None,
        create_backup: bool = True,
    ) -> Dict[str, Any]:
        """Promote a staged M2M file to live documentation.

        This replaces the original markdown with the compressed M2M version.
        Creates a backup for rollback support.

        Args:
            staged_path: Relative path to staged M2M file (e.g., ".m2m/staged/ai_overseer/INTERFACE_M2M.yaml")
            target_path: Optional override for target location (auto-detected if not provided)
            create_backup: Whether to backup original before overwriting (default True)

        Returns:
            Promotion result with backup path for potential rollback
        """
        staged_file = self.repo_root / staged_path
        if not staged_file.exists():
            return {"success": False, "error": f"Staged file not found: {staged_path}"}

        # Determine target path from staged structure
        if target_path is None:
            try:
                content = staged_file.read_text(encoding="utf-8", errors="replace")
                lines = content.splitlines()
                header = lines[0] if lines else ""
                parts = header.split("|")

                # P0: Use src: field for deterministic resolution (no glob guessing)
                src_field = None
                for part in parts:
                    part = part.strip()
                    if part.startswith("src:"):
                        src_field = part[4:].strip()
                        break

                if src_field and (self.repo_root / src_field).exists():
                    # Deterministic: exact source path from header
                    target_file = self.repo_root / src_field
                else:
                    # Legacy fallback: reconstruct from staged path structure
                    original_name = parts[1].strip() if len(parts) > 1 else staged_file.stem.replace("_M2M", ".md")
                    rel_staged = staged_file.relative_to(self.staged_dir)
                    module_dir = rel_staged.parent

                    target_candidates = list(self.repo_root.glob(f"**/{module_dir}/{original_name}"))
                    if not target_candidates:
                        target_candidates = list(self.repo_root.glob(f"**/{original_name}"))

                    if target_candidates:
                        target_file = target_candidates[0]
                    else:
                        return {"success": False, "error": f"Cannot find original file for: {staged_path}"}

            except OSError as e:
                return {"success": False, "error": f"Failed to read staged file: {e}"}
        else:
            target_file = self.repo_root / target_path

        # Create backup before promotion
        backup_path = None
        if create_backup and target_file.exists():
            backup_result = self._backup_original(target_file)
            if not backup_result["success"]:
                return backup_result
            backup_path = backup_result["backup_path"]

        # Promote: copy M2M content to target (keeping .md extension)
        try:
            m2m_content = staged_file.read_text(encoding="utf-8", errors="replace")
            target_file.write_text(m2m_content, encoding="utf-8")
        except OSError as e:
            return {"success": False, "error": f"Promotion failed: {e}"}

        # Record promotion in history
        promotion_record = {
            "timestamp": time.time(),
            "staged_path": staged_path,
            "target_path": str(target_file.relative_to(self.repo_root)),
            "backup_path": backup_path,
            "action": "promote",
        }
        self._append_promotion_history(promotion_record)

        return {
            "success": True,
            "staged_path": staged_path,
            "target_path": str(target_file.relative_to(self.repo_root)),
            "backup_path": backup_path,
            "message": f"Promoted M2M to {target_file.name}",
        }

    def rollback(self, target_path: str) -> Dict[str, Any]:
        """Rollback a promoted M2M file to its original version.

        Args:
            target_path: Relative path to the promoted file

        Returns:
            Rollback result
        """
        target_file = self.repo_root / target_path

        # Find backup for this file (search subdirectory first, then flat for legacy)
        try:
            rel_path = target_file.relative_to(self.repo_root)
            backup_subdir = self.backup_dir / rel_path.parent
            backup_candidates = list(backup_subdir.glob(f"*_{target_file.name}"))
        except ValueError:
            backup_candidates = []
        # Legacy fallback: flat backup dir
        if not backup_candidates:
            backup_candidates = list(self.backup_dir.glob(f"*_{target_file.name}"))
        if not backup_candidates:
            return {"success": False, "error": f"No backup found for: {target_path}"}

        # Use most recent backup
        backup_file = max(backup_candidates, key=lambda p: p.stat().st_mtime)

        try:
            original_content = backup_file.read_text(encoding="utf-8", errors="replace")
            target_file.write_text(original_content, encoding="utf-8")
        except OSError as e:
            return {"success": False, "error": f"Rollback failed: {e}"}

        # Record rollback in history
        rollback_record = {
            "timestamp": time.time(),
            "target_path": target_path,
            "backup_used": str(backup_file.relative_to(self.repo_root)),
            "action": "rollback",
        }
        self._append_promotion_history(rollback_record)

        return {
            "success": True,
            "target_path": target_path,
            "backup_used": str(backup_file.relative_to(self.repo_root)),
            "message": f"Rolled back {target_file.name} to original",
        }

    def _backup_original(self, file_path: Path) -> Dict[str, Any]:
        """Create timestamped backup of original file before promotion.

        Uses full relative path hash to prevent cross-module collisions.
        Backup structure: .m2m/backups/{rel_path_dirs}/{timestamp}_{filename}

        Args:
            file_path: Path to original file

        Returns:
            Backup result with path
        """
        if not file_path.exists():
            return {"success": True, "backup_path": None}  # Nothing to backup

        timestamp = time.strftime("%Y%m%d_%H%M%S", time.gmtime())
        # Use relative path subdirectory to prevent same-name collisions across modules
        try:
            rel_path = file_path.relative_to(self.repo_root)
            backup_subdir = self.backup_dir / rel_path.parent
        except ValueError:
            backup_subdir = self.backup_dir
        backup_subdir.mkdir(parents=True, exist_ok=True)
        backup_name = f"{timestamp}_{file_path.name}"
        backup_path = backup_subdir / backup_name

        try:
            content = file_path.read_text(encoding="utf-8", errors="replace")
            backup_path.write_text(content, encoding="utf-8")
        except OSError as e:
            return {"success": False, "error": f"Backup failed: {e}"}

        return {
            "success": True,
            "backup_path": str(backup_path.relative_to(self.repo_root)),
        }

    def _append_promotion_history(self, record: Dict[str, Any]) -> None:
        """Append promotion/rollback record to history file."""
        try:
            self.promotion_history_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.promotion_history_path, "a", encoding="utf-8") as handle:
                handle.write(json.dumps(record) + "\n")
        except Exception:
            pass

    # ======================== LEARNING & FEEDBACK ======================== #

    def record_outcome(self, filename: str, success: bool, reason: str = "") -> None:
        """Record compression outcome for learning (WSP 48 feedback loop)."""
        if filename not in self._pattern_memory:
            self._pattern_memory[filename] = {
                "compressions": 0,
                "successes": 0,
                "failures": 0,
                "success_rate": 0.5,
                "last_outcome": None,
                "last_reason": None,
            }

        record = self._pattern_memory[filename]
        record["compressions"] += 1
        if success:
            record["successes"] += 1
        else:
            record["failures"] += 1

        total = record["successes"] + record["failures"]
        record["success_rate"] = record["successes"] / total if total > 0 else 0.5
        record["last_outcome"] = "success" if success else "failure"
        record["last_reason"] = reason

        self._save_pattern_memory()

    def _load_pattern_memory(self) -> Dict[str, Any]:
        """Load pattern memory from disk."""
        data = self._load_json(self.pattern_memory_path)
        return data if data else {}

    def _save_pattern_memory(self) -> None:
        """Save pattern memory to disk."""
        self._write_json(self.pattern_memory_path, self._pattern_memory)

    @staticmethod
    def _load_json(path: Path) -> Optional[Dict[str, Any]]:
        if not path.exists():
            return None
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return None

    @staticmethod
    def _write_json(path: Path, payload: Dict[str, Any]) -> None:
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        except Exception:
            pass

    def _append_history(self, payload: Dict[str, Any]) -> None:
        try:
            self.history_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.history_path, "a", encoding="utf-8") as handle:
                handle.write(json.dumps(payload) + "\n")
        except Exception:
            pass

    # ======================== EVALUATION ======================== #

    def evaluate_staged(self, model=None) -> Dict[str, Any]:
        """Evaluate M2M quality by comparing semantic similarity of staged vs originals.

        Uses SentenceTransformer embeddings (same as HoloIndex) to measure
        information retention. Returns per-file and aggregate metrics.

        Args:
            model: Optional pre-loaded SentenceTransformer model. If None,
                   loads all-MiniLM-L6-v2 (same as HoloIndex).

        Returns:
            Dict with keys: pairs_evaluated, avg_cosine_similarity, min_similarity,
            max_similarity, results (per-file details), verdict.
        """
        try:
            import numpy as np
        except ImportError:
            return {"error": "numpy required for evaluation"}

        if model is None:
            try:
                from sentence_transformers import SentenceTransformer
                model = SentenceTransformer("all-MiniLM-L6-v2")
            except ImportError:
                return {"error": "sentence_transformers required for evaluation"}

        staged = self.list_staged()
        if staged["total_staged"] == 0:
            return {"error": "no staged files to evaluate", "pairs_evaluated": 0}

        results = []
        for entry in staged["files"]:
            staged_path = Path(entry["staged_path"])
            if not staged_path.exists():
                continue

            m2m_text = staged_path.read_text(encoding="utf-8", errors="ignore")

            # Extract original path from M2M header
            header_line = m2m_text.splitlines()[0] if m2m_text.strip() else ""
            original_name = entry.get("original_name", "").strip()

            # Try to find the original file
            original_path = self._find_original(staged_path, original_name)
            if original_path is None or not original_path.exists():
                continue

            orig_text = original_path.read_text(encoding="utf-8", errors="ignore")

            # Embed first 6 lines / 400 chars (same as HoloIndex indexing)
            orig_summary = " ".join(orig_text.splitlines()[:6])[:400]
            m2m_summary = " ".join(m2m_text.splitlines()[:6])[:400]

            orig_emb = model.encode(orig_summary)
            m2m_emb = model.encode(m2m_summary)

            cos_sim = float(
                np.dot(orig_emb, m2m_emb)
                / (np.linalg.norm(orig_emb) * np.linalg.norm(m2m_emb) + 1e-9)
            )

            orig_lines = len(orig_text.splitlines())
            m2m_lines = len(m2m_text.splitlines())
            compression = (1 - m2m_lines / orig_lines) * 100 if orig_lines > 0 else 0

            results.append({
                "original": str(original_path),
                "m2m": str(staged_path),
                "cosine_similarity": round(cos_sim, 3),
                "original_lines": orig_lines,
                "m2m_lines": m2m_lines,
                "compression_pct": round(compression, 1),
            })

        if not results:
            return {"error": "no original-m2m pairs found", "pairs_evaluated": 0}

        sims = [r["cosine_similarity"] for r in results]
        avg_sim = sum(sims) / len(sims)

        # Verdict: 0.6+ excellent, 0.4-0.6 acceptable, <0.4 needs improvement
        if avg_sim >= 0.6:
            verdict = "excellent"
        elif avg_sim >= 0.4:
            verdict = "acceptable"
        else:
            verdict = "needs_improvement"

        return {
            "pairs_evaluated": len(results),
            "avg_cosine_similarity": round(avg_sim, 3),
            "min_similarity": round(min(sims), 3),
            "max_similarity": round(max(sims), 3),
            "verdict": verdict,
            "results": results,
        }

    def _find_original(self, staged_path: Path, original_name: str) -> Optional[Path]:
        """Locate the original file that a staged M2M was compiled from."""
        # The staged directory mirrors module structure:
        # .m2m/staged/agent_market/INTERFACE_M2M.yaml -> modules/.../agent_market/INTERFACE.md
        if not original_name:
            # Derive from staged filename
            original_name = staged_path.stem.replace("_M2M", "") + ".md"

        # Search common locations
        candidates = list(self.repo_root.rglob(original_name))
        if len(candidates) == 1:
            return candidates[0]

        # Use the staged parent name to disambiguate
        staged_module = staged_path.parent.name
        for c in candidates:
            if staged_module in str(c):
                return c

        return candidates[0] if candidates else None


# CLI entry point for testing
if __name__ == "__main__":
    import sys

    repo_root = Path(__file__).resolve().parents[4]  # Up to Foundups-Agent
    sentinel = M2MCompressionSentinel(repo_root)

    force = "--force" in sys.argv
    result = sentinel.check(force=force)

    print(json.dumps(result, indent=2))
