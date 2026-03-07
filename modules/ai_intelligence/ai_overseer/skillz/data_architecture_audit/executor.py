"""Data Architecture Audit Executor - WSP 78 Compliance Auditing.

Qwen-orchestrated skillz for auditing FoundUps data architecture.

4-Phase Pipeline:
  Phase 1: SQLite Scanner (Python, no LLM) - collect pragma states
  Phase 2: WSP 78 Checker (Gemma 270M) - binary compliance checks
  Phase 3: Gap Analyzer (Qwen 1.5B) - identify missing documentation
  Phase 4: Report Generator (Qwen 1.5B) - synthesize findings

WSP Compliance: WSP 78 (Database Architecture), WSP 96 (WRE Skills), WSP 77 (Agent Coordination)
"""

from __future__ import annotations

import json
import logging
import os
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from modules.infrastructure.shared_utilities.local_model_selection import (
    resolve_code_model_path,
    resolve_triage_model_path,
)

logger = logging.getLogger(__name__)

# Scopes map to target paths
AUDIT_SCOPES = {
    "core": [
        Path("data/foundups.db"),
        Path("modules/infrastructure/database/data/foundups.db"),
        Path("modules/infrastructure/database/data/agent_db.sqlite"),
    ],
    "sim": [
        Path("modules/foundups/simulator/memory/fam_audit.db"),
        Path("modules/foundups/simulator/memory/epoch_ledger.db"),
    ],
    "events": [
        Path("modules/foundups/agent_market/memory/fam_audit.db"),
        Path("modules/infrastructure/dae_daemon/memory/dae_audit.db"),
    ],
    "full": None,  # Uses default from sqlite_audit
}

# WSP 78 compliance checks
WSP78_CHECKS = {
    "WSP78-01": {
        "description": "WAL mode on long-lived DBs",
        "method": "journal_mode",
        "expected": "wal",
    },
    "WSP78-02": {
        "description": "foreign_keys=ON per connection",
        "method": "foreign_keys_after_enable",
        "expected": 1,
    },
    "WSP78-03": {
        "description": "busy_timeout configured",
        "method": "busy_timeout",
        "expected": ">0",
    },
    "WSP78-04": {
        "description": "Event store dedupe keys",
        "method": "schema_inspection",
        "expected": "event_id UNIQUE",
    },
    "WSP78-05": {
        "description": "Event store sequence monotonic",
        "method": "sequence_check",
        "expected": "monotonic",
    },
    "WSP78-06": {
        "description": "JSONL/SQLite parity",
        "method": "parity_check",
        "expected": "match",
    },
    "WSP78-07": {
        "description": "Satellite stores documented",
        "method": "doc_check",
        "expected": "SATELLITE_STORES.md exists",
    },
    "WSP78-08": {
        "description": "Namespace contract",
        "method": "prefix_validation",
        "expected": "modules_|agents_|foundups_",
    },
}

# Model paths (consistent with existing patterns)
DEFAULT_GEMMA_PATH = resolve_triage_model_path()
DEFAULT_QWEN_PATH = resolve_code_model_path()


@dataclass
class ComplianceResult:
    """Result of a single WSP 78 compliance check."""
    check_id: str
    status: str  # "pass", "fail", "skip"
    evidence: str
    recommendation: Optional[str] = None


@dataclass
class GapFinding:
    """Identified gap in data architecture."""
    gap_type: str  # "missing_doc", "missing_pragma", "schema_issue"
    path: str
    description: str
    recommendation: str
    priority: str  # "critical", "warning", "info"


@dataclass
class AuditReport:
    """Complete audit report."""
    audit_id: str
    scope: str
    generated_at: str
    summary: Dict[str, Any]
    compliance: Dict[str, Dict[str, Any]]
    gaps: List[Dict[str, Any]]
    patches: List[Dict[str, Any]]


class DataArchitectureAuditExecutor:
    """Executes /audit-data skillz for WSP 78 compliance.

    Example:
        executor = DataArchitectureAuditExecutor()
        report = executor.execute(scope="core")
        print(report.summary["compliance_score"])
    """

    def __init__(
        self,
        repo_root: Optional[Path] = None,
        gemma_path: Optional[Path] = None,
        qwen_path: Optional[Path] = None,
    ) -> None:
        """Initialize audit executor.

        Args:
            repo_root: Repository root path
            gemma_path: Path to Gemma GGUF model
            qwen_path: Path to Qwen GGUF model
        """
        self.repo_root = repo_root or Path("O:/Foundups-Agent")
        self.gemma_path = gemma_path or DEFAULT_GEMMA_PATH
        self.qwen_path = qwen_path or DEFAULT_QWEN_PATH

        # LLM instances (lazy loaded)
        self._gemma_llm: Any = None
        self._qwen_llm: Any = None

        # Phase outputs
        self._raw_audit: Dict[str, Any] = {}
        self._compliance_results: List[ComplianceResult] = []
        self._gaps: List[GapFinding] = []

        logger.info("[AUDIT-DATA] Initialized DataArchitectureAuditExecutor")

    def execute(self, scope: str = "core") -> AuditReport:
        """Execute full 4-phase audit pipeline.

        Args:
            scope: One of "core", "full", "sim", "events"

        Returns:
            Complete AuditReport
        """
        audit_id = f"audit_{datetime.now(timezone.utc).strftime('%Y-%m-%d_%H%M%S')}"
        logger.info(f"[AUDIT-DATA] Starting audit {audit_id} with scope={scope}")

        start_time = time.time()

        # Phase 1: SQLite Scanner (Python, no LLM)
        self._phase1_sqlite_scan(scope)

        # Phase 2: WSP 78 Checker (Gemma)
        self._phase2_wsp78_check()

        # Phase 3: Gap Analyzer (Qwen)
        self._phase3_gap_analysis()

        # Phase 4: Report Generator (Qwen)
        report = self._phase4_generate_report(audit_id, scope)

        elapsed = time.time() - start_time
        logger.info(f"[AUDIT-DATA] Audit complete in {elapsed:.1f}s")

        return report

    def _phase1_sqlite_scan(self, scope: str) -> None:
        """Phase 1: Run sqlite_audit.py scanner (no LLM)."""
        logger.info("[AUDIT-DATA] Phase 1: SQLite Scanner")

        try:
            from modules.infrastructure.database.src.sqlite_audit import (
                run_sqlite_audit,
                AuditOptions,
            )

            # Get targets for scope
            targets = AUDIT_SCOPES.get(scope)
            if targets:
                # Convert to absolute paths
                abs_targets = [self.repo_root / t for t in targets]
            else:
                abs_targets = None  # Use defaults

            options = AuditOptions(max_tables=20, include_table_counts=True)
            self._raw_audit = run_sqlite_audit(targets=abs_targets, options=options)

            logger.info(
                f"[AUDIT-DATA] Phase 1 complete: "
                f"{self._raw_audit['existing_count']} stores scanned"
            )

        except ImportError as e:
            logger.error(f"[AUDIT-DATA] Phase 1 failed - import error: {e}")
            self._raw_audit = {"error": str(e), "target_count": 0}

    def _phase2_wsp78_check(self) -> None:
        """Phase 2: Binary compliance checks using Gemma."""
        logger.info("[AUDIT-DATA] Phase 2: WSP 78 Compliance Checker")

        self._compliance_results = []

        for target in self._raw_audit.get("targets", []):
            if target.get("status") != "ok":
                continue

            path = target.get("path", "unknown")

            # WSP78-01: WAL mode
            journal_mode = target.get("journal_mode", "").lower()
            self._compliance_results.append(
                ComplianceResult(
                    check_id="WSP78-01",
                    status="pass" if journal_mode == "wal" else "fail",
                    evidence=f"journal_mode={journal_mode}",
                    recommendation=(
                        None if journal_mode == "wal"
                        else f"Set PRAGMA journal_mode=WAL on {path}"
                    ),
                )
            )

            # WSP78-02: foreign_keys
            fk = target.get("foreign_keys_after_enable", 0)
            self._compliance_results.append(
                ComplianceResult(
                    check_id="WSP78-02",
                    status="pass" if fk == 1 else "fail",
                    evidence=f"foreign_keys_after_enable={fk}",
                    recommendation=(
                        None if fk == 1
                        else f"Ensure PRAGMA foreign_keys=ON per connection on {path}"
                    ),
                )
            )

            # WSP78-03: busy_timeout (check if any pragmas set it)
            # Note: sqlite_audit doesn't currently capture busy_timeout directly
            # Mark as "skip" for now - Gemma could help classify
            self._compliance_results.append(
                ComplianceResult(
                    check_id="WSP78-03",
                    status="skip",
                    evidence="busy_timeout not captured in audit",
                    recommendation="Add busy_timeout check to sqlite_audit.py",
                )
            )

        # Use Gemma for binary classification of ambiguous cases
        if self._initialize_gemma():
            self._gemma_classify_compliance()

        passes = sum(1 for r in self._compliance_results if r.status == "pass")
        total = len(self._compliance_results)
        logger.info(f"[AUDIT-DATA] Phase 2 complete: {passes}/{total} checks passed")

    def _gemma_classify_compliance(self) -> None:
        """Use Gemma for binary classification of ambiguous compliance."""
        # Find skipped checks that Gemma could help classify
        for result in self._compliance_results:
            if result.status == "skip" and "ambiguous" in result.evidence.lower():
                # Build classification prompt
                prompt = (
                    f"Is this WSP 78 compliant? Answer PASS or FAIL only.\n"
                    f"Check: {result.check_id}\n"
                    f"Evidence: {result.evidence}\n"
                    f"Answer:"
                )

                try:
                    response = self._gemma_llm(
                        prompt,
                        max_tokens=10,
                        temperature=0.1,
                        stop=["\n"],
                    )

                    text = response["choices"][0]["text"].strip().upper()
                    if "PASS" in text:
                        result.status = "pass"
                    elif "FAIL" in text:
                        result.status = "fail"

                except Exception as e:
                    logger.warning(f"[AUDIT-DATA] Gemma classification failed: {e}")

    def _phase3_gap_analysis(self) -> None:
        """Phase 3: Identify gaps using Qwen analysis."""
        logger.info("[AUDIT-DATA] Phase 3: Gap Analyzer")

        self._gaps = []

        # Check for missing SATELLITE_STORES.md (WSP78-07)
        satellite_doc = self.repo_root / "docs" / "SATELLITE_STORES.md"
        if not satellite_doc.exists():
            self._gaps.append(
                GapFinding(
                    gap_type="missing_doc",
                    path=str(satellite_doc),
                    description="No satellite stores documentation found",
                    recommendation="Create SATELLITE_STORES.md documenting all non-core SQLite files",
                    priority="warning",
                )
            )

        # Check failed compliance for critical gaps
        for result in self._compliance_results:
            if result.status == "fail" and result.check_id in ["WSP78-01", "WSP78-02"]:
                self._gaps.append(
                    GapFinding(
                        gap_type="missing_pragma",
                        path=result.evidence,
                        description=f"{result.check_id} failed",
                        recommendation=result.recommendation or "Fix compliance issue",
                        priority="critical",
                    )
                )

        # Use Qwen for deeper gap analysis if available
        if self._initialize_qwen():
            self._qwen_analyze_gaps()

        logger.info(f"[AUDIT-DATA] Phase 3 complete: {len(self._gaps)} gaps identified")

    def _qwen_analyze_gaps(self) -> None:
        """Use Qwen for deeper gap analysis."""
        if not self._qwen_llm:
            return

        # Build context from raw audit
        audit_summary = json.dumps(
            {
                "stores_audited": self._raw_audit.get("existing_count", 0),
                "missing": self._raw_audit.get("missing_count", 0),
                "integrity_failures": self._raw_audit.get("integrity_failures", 0),
            },
            indent=2,
        )

        prompt = (
            f"Analyze this SQLite audit for WSP 78 gaps:\n"
            f"{audit_summary}\n\n"
            f"List any additional gaps not captured by binary checks. "
            f"Format: GAP_TYPE|PATH|DESCRIPTION|PRIORITY\n"
            f"Answer:"
        )

        try:
            response = self._qwen_llm(
                prompt,
                max_tokens=200,
                temperature=0.2,
                stop=["###"],
            )

            text = response["choices"][0]["text"].strip()

            # Parse Qwen's gap suggestions
            for line in text.split("\n"):
                if "|" in line:
                    parts = line.split("|")
                    if len(parts) >= 4:
                        self._gaps.append(
                            GapFinding(
                                gap_type=parts[0].strip(),
                                path=parts[1].strip(),
                                description=parts[2].strip(),
                                recommendation="See WSP 78 for remediation",
                                priority=parts[3].strip().lower(),
                            )
                        )

        except Exception as e:
            logger.warning(f"[AUDIT-DATA] Qwen gap analysis failed: {e}")

    def _phase4_generate_report(self, audit_id: str, scope: str) -> AuditReport:
        """Phase 4: Generate final audit report."""
        logger.info("[AUDIT-DATA] Phase 4: Report Generator")

        # Calculate summary metrics
        total_checks = len(self._compliance_results)
        passes = sum(1 for r in self._compliance_results if r.status == "pass")
        fails = sum(1 for r in self._compliance_results if r.status == "fail")
        critical_gaps = sum(1 for g in self._gaps if g.priority == "critical")
        warnings = sum(1 for g in self._gaps if g.priority == "warning")

        compliance_score = passes / max(1, total_checks)

        # Build compliance dict
        compliance_dict = {}
        for result in self._compliance_results:
            if result.check_id not in compliance_dict:
                compliance_dict[result.check_id] = {
                    "status": result.status,
                    "evidence": result.evidence,
                }
            else:
                # Aggregate multiple checks of same type
                existing = compliance_dict[result.check_id]
                if result.status == "fail":
                    existing["status"] = "fail"
                existing["evidence"] += f"; {result.evidence}"

        # Generate patch recommendations
        patches = []
        for gap in self._gaps:
            if gap.priority == "critical":
                patches.append({
                    "file": gap.path,
                    "action": gap.recommendation,
                    "priority": gap.priority,
                })

        return AuditReport(
            audit_id=audit_id,
            scope=scope,
            generated_at=datetime.now(timezone.utc).isoformat(),
            summary={
                "stores_audited": self._raw_audit.get("existing_count", 0),
                "compliance_score": round(compliance_score, 3),
                "checks_passed": passes,
                "checks_failed": fails,
                "critical_findings": critical_gaps,
                "warnings": warnings,
            },
            compliance=compliance_dict,
            gaps=[asdict(g) for g in self._gaps],
            patches=patches,
        )

    def _initialize_gemma(self) -> bool:
        """Lazy-load Gemma 270M model."""
        if self._gemma_llm is not None:
            return True

        if not self.gemma_path.exists():
            logger.warning(f"[AUDIT-DATA] Gemma model not found: {self.gemma_path}")
            return False

        try:
            from llama_cpp import Llama

            logger.info(f"[AUDIT-DATA] Loading Gemma from {self.gemma_path}")

            # Suppress llama.cpp loading noise
            old_stdout, old_stderr = os.dup(1), os.dup(2)
            devnull = os.open(os.devnull, os.O_WRONLY)

            try:
                os.dup2(devnull, 1)
                os.dup2(devnull, 2)

                self._gemma_llm = Llama(
                    model_path=str(self.gemma_path),
                    n_ctx=512,
                    n_threads=2,
                    n_gpu_layers=0,
                    verbose=False,
                )

            finally:
                os.dup2(old_stdout, 1)
                os.dup2(old_stderr, 2)
                os.close(devnull)
                os.close(old_stdout)
                os.close(old_stderr)

            logger.info("[AUDIT-DATA] Gemma loaded successfully")
            return True

        except ImportError:
            logger.warning("[AUDIT-DATA] llama_cpp not installed")
            return False
        except Exception as e:
            logger.error(f"[AUDIT-DATA] Failed to load Gemma: {e}")
            return False

    def _initialize_qwen(self) -> bool:
        """Lazy-load Qwen 1.5B model."""
        if self._qwen_llm is not None:
            return True

        if not self.qwen_path.exists():
            logger.warning(f"[AUDIT-DATA] Qwen model not found: {self.qwen_path}")
            return False

        try:
            from llama_cpp import Llama

            logger.info(f"[AUDIT-DATA] Loading Qwen from {self.qwen_path}")

            # Suppress llama.cpp loading noise
            old_stdout, old_stderr = os.dup(1), os.dup(2)
            devnull = os.open(os.devnull, os.O_WRONLY)

            try:
                os.dup2(devnull, 1)
                os.dup2(devnull, 2)

                self._qwen_llm = Llama(
                    model_path=str(self.qwen_path),
                    n_ctx=2048,
                    n_threads=4,
                    n_gpu_layers=0,
                    verbose=False,
                )

            finally:
                os.dup2(old_stdout, 1)
                os.dup2(old_stderr, 2)
                os.close(devnull)
                os.close(old_stdout)
                os.close(old_stderr)

            logger.info("[AUDIT-DATA] Qwen loaded successfully")
            return True

        except ImportError:
            logger.warning("[AUDIT-DATA] llama_cpp not installed")
            return False
        except Exception as e:
            logger.error(f"[AUDIT-DATA] Failed to load Qwen: {e}")
            return False

    def to_json(self, report: AuditReport) -> str:
        """Serialize report to JSON string."""
        return json.dumps(asdict(report), indent=2)

    def to_markdown(self, report: AuditReport) -> str:
        """Generate markdown report."""
        lines = [
            f"# Data Architecture Audit Report",
            f"",
            f"**Audit ID**: {report.audit_id}",
            f"**Scope**: {report.scope}",
            f"**Generated**: {report.generated_at}",
            f"",
            f"## Summary",
            f"",
            f"| Metric | Value |",
            f"|--------|-------|",
            f"| Stores Audited | {report.summary['stores_audited']} |",
            f"| Compliance Score | {report.summary['compliance_score']:.1%} |",
            f"| Checks Passed | {report.summary['checks_passed']} |",
            f"| Checks Failed | {report.summary['checks_failed']} |",
            f"| Critical Findings | {report.summary['critical_findings']} |",
            f"| Warnings | {report.summary['warnings']} |",
            f"",
            f"## WSP 78 Compliance",
            f"",
            f"| Check ID | Status | Evidence |",
            f"|----------|--------|----------|",
        ]

        for check_id, data in report.compliance.items():
            status_icon = "PASS" if data["status"] == "pass" else "FAIL"
            lines.append(f"| {check_id} | {status_icon} | {data['evidence'][:50]}... |")

        if report.gaps:
            lines.extend([
                f"",
                f"## Gaps Identified",
                f"",
            ])
            for gap in report.gaps:
                lines.append(f"- **[{gap['priority'].upper()}]** {gap['description']}")
                lines.append(f"  - Path: `{gap['path']}`")
                lines.append(f"  - Recommendation: {gap['recommendation']}")

        if report.patches:
            lines.extend([
                f"",
                f"## Recommended Patches",
                f"",
            ])
            for patch in report.patches:
                lines.append(f"1. **{patch['priority'].upper()}**: {patch['action']}")
                lines.append(f"   - File: `{patch['file']}`")

        return "\n".join(lines)


def run_audit_skill(scope: str = "core", output_dir: Optional[Path] = None) -> Dict[str, Any]:
    """Entry point for /audit-data skillz invocation.

    Args:
        scope: Audit scope (core, full, sim, events)
        output_dir: Directory to write report files

    Returns:
        Dict with audit results and file paths
    """
    executor = DataArchitectureAuditExecutor()
    report = executor.execute(scope=scope)

    result = {
        "audit_id": report.audit_id,
        "compliance_score": report.summary["compliance_score"],
        "critical_findings": report.summary["critical_findings"],
    }

    if output_dir:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        json_path = output_dir / f"{report.audit_id}.json"
        json_path.write_text(executor.to_json(report), encoding="utf-8")
        result["json_report"] = str(json_path)

        md_path = output_dir / f"{report.audit_id}.md"
        md_path.write_text(executor.to_markdown(report), encoding="utf-8")
        result["markdown_report"] = str(md_path)

    return result


if __name__ == "__main__":
    import argparse

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

    parser = argparse.ArgumentParser(description="Run data architecture audit")
    parser.add_argument(
        "--scope",
        choices=["core", "full", "sim", "events"],
        default="core",
        help="Audit scope",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("audit_reports"),
        help="Output directory for reports",
    )
    args = parser.parse_args()

    result = run_audit_skill(scope=args.scope, output_dir=args.output)

    print("\n" + "=" * 60)
    print("AUDIT COMPLETE")
    print("=" * 60)
    print(f"Audit ID: {result['audit_id']}")
    print(f"Compliance Score: {result['compliance_score']:.1%}")
    print(f"Critical Findings: {result['critical_findings']}")

    if "json_report" in result:
        print(f"\nReports written to:")
        print(f"  JSON: {result['json_report']}")
        print(f"  Markdown: {result['markdown_report']}")
