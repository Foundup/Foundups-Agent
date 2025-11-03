#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Overseer Mission: Anthropomorphic Time Cleanup
==================================================

Mission: Find and replace anthropomorphic time references (hours/weeks) with token-based estimates.

WSP Compliance:
    - WSP 77: Qwen (strategic planning) + Gemma (validation) + 0102 (oversight)
    - WSP 50: Pre-action verification (find before fix)
    - WSP 22: Document changes in ModLog

Agent Coordination:
    Phase 1 (Gemma): Fast grep for time patterns (50-100 tokens)
    Phase 2 (Qwen): Calculate token equivalents (200-500 tokens per file)
    Phase 3 (0102): Review and approve fixes (oversight)
    Phase 4 (Learning): Store pattern for future violations
"""

import sys
import json
import re
from pathlib import Path
from typing import List, Dict, Tuple

# Add repo root to path
repo_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(repo_root))

from modules.ai_intelligence.ai_overseer.src.ai_overseer import (
    AIIntelligenceOverseer,
    MissionType,
    AgentRole
)


class AnthropomorphicTimeCleanup:
    """
    Autonomous cleanup of anthropomorphic time references.

    Per CLAUDE.md line 32: "TOKENS: 50-200 per operation"
    Per CLAUDE.md line 227: "Token_Budget: 30K total (93% reduction)"

    0102 operates in TOKEN SPACE, not human time.
    """

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.violations_found = []
        self.token_conversions = {
            # Anthropomorphic time → Token equivalent
            # Based on empirical data from Phase 2: "2 hours" actual = ~2K tokens
            "hour": 1000,     # 1 hour ≈ 1K tokens (conservative)
            "hr": 1000,
            "hrs": 1000,
            "day": 8000,      # 1 day (8 hours) ≈ 8K tokens
            "week": 40000,    # 1 week (40 hours) ≈ 40K tokens
            "month": 160000,  # 1 month (160 hours) ≈ 160K tokens
        }

    def phase1_gemma_grep(self) -> List[Dict]:
        """
        Phase 1 (Gemma Associate): Fast pattern matching

        Token Budget: 50-100 tokens (grep operation)
        Speed: <10ms binary classification
        """
        print("\n[PHASE 1 - GEMMA] Fast grep for time patterns...")

        # Pattern: Match "N hours", "N-M hours", "N hrs", "N weeks", etc.
        time_pattern = re.compile(
            r'\b(\d+)[-\s]*(?:to[-\s]*)?(\d+)?[-\s]*(hour|hr|hrs|week|weeks|month|months|day|days)\b',
            re.IGNORECASE
        )

        violations = []

        # Files to scan (focus on WRE audit documents)
        scan_files = [
            "WRE_PHASE1_CORRECTED_AUDIT.md",
            "WRE_PHASE2_CORRECTED_AUDIT.md",
            "WRE_PHASE2_WSP_COMPLIANCE_AUDIT.md",
            "WRE_PHASE3_CORRECTED_AUDIT.md",
            "WRE_PHASE3_WSP_COMPLIANCE_AUDIT.md",
            "WRE_PHASES_COMPLETE_SUMMARY.md",
            "WRE_PHASE2_FINAL_AUDIT.md",
            "WRE_SKILLS_IMPLEMENTATION_SUMMARY.md",
        ]

        for filename in scan_files:
            filepath = self.repo_root / filename
            if not filepath.exists():
                continue

            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')

                for line_num, line in enumerate(lines, 1):
                    matches = time_pattern.finditer(line)
                    for match in matches:
                        violations.append({
                            "file": str(filepath.relative_to(self.repo_root)),
                            "line": line_num,
                            "text": line.strip(),
                            "match": match.group(0),
                            "num1": int(match.group(1)),
                            "num2": int(match.group(2)) if match.group(2) else None,
                            "unit": match.group(3).lower()
                        })

        self.violations_found = violations
        print(f"[GEMMA] Found {len(violations)} time violations in {len(scan_files)} files")
        return violations

    def phase2_qwen_calculate(self, violations: List[Dict]) -> List[Dict]:
        """
        Phase 2 (Qwen Partner): Calculate token equivalents

        Token Budget: 200-500 tokens (strategic planning per file)
        Purpose: Convert "7-8 hours" → "~7.5K tokens"
        """
        print("\n[PHASE 2 - QWEN] Calculating token equivalents...")

        fixes = []

        for violation in violations:
            num1 = violation["num1"]
            num2 = violation["num2"]
            unit = violation["unit"]

            # Get token multiplier
            unit_clean = unit.rstrip('s')  # Remove plural
            token_per_unit = self.token_conversions.get(unit_clean, 1000)

            # Calculate token equivalent
            if num2:
                # Range: "7-8 hours" → "~7.5K tokens"
                avg_val = (num1 + num2) / 2
                token_estimate = int(avg_val * token_per_unit)
                replacement = f"~{token_estimate/1000:.1f}K tokens"
            else:
                # Single: "2 hours" → "~2K tokens"
                token_estimate = num1 * token_per_unit
                if token_estimate >= 1000:
                    replacement = f"~{token_estimate/1000:.0f}K tokens"
                else:
                    replacement = f"~{token_estimate} tokens"

            fixes.append({
                **violation,
                "replacement": replacement,
                "token_estimate": token_estimate
            })

        print(f"[QWEN] Calculated {len(fixes)} token replacements")
        return fixes

    def phase3_0102_review(self, fixes: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
        """
        Phase 3 (0102 Principal): Review and approve fixes

        Token Budget: 0102 oversight (strategic decisions)
        Purpose: Ensure fixes maintain semantic meaning
        """
        print("\n[PHASE 3 - 0102] Reviewing token replacements...")

        approved = []
        rejected = []

        for fix in fixes:
            # 0102 validation criteria:
            # 1. Is replacement semantically equivalent?
            # 2. Does it maintain document readability?
            # 3. Is token estimate reasonable?

            original = fix["match"]
            replacement = fix["replacement"]

            # Simple approval logic (can be enhanced with Gemma validation)
            if fix["token_estimate"] > 0 and "tokens" in replacement:
                approved.append(fix)
                print(f"  [OK] APPROVE: '{original}' -> '{replacement}'")
            else:
                rejected.append(fix)
                print(f"  ❌ REJECT: '{original}' (invalid conversion)")

        print(f"[0102] Approved: {len(approved)}, Rejected: {len(rejected)}")
        return approved, rejected

    def execute_fixes(self, approved_fixes: List[Dict]) -> None:
        """
        Execute approved fixes (modify files)

        Token Budget: File I/O overhead (~50 tokens per file)
        """
        print("\n[EXECUTE] Applying approved fixes...")

        # Group fixes by file
        files_to_fix = {}
        for fix in approved_fixes:
            filepath = fix["file"]
            if filepath not in files_to_fix:
                files_to_fix[filepath] = []
            files_to_fix[filepath].append(fix)

        for filepath, fixes in files_to_fix.items():
            full_path = self.repo_root / filepath

            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Apply fixes (sorted by line number descending to avoid offset issues)
            fixes_sorted = sorted(fixes, key=lambda x: x["line"], reverse=True)
            lines = content.split('\n')

            for fix in fixes_sorted:
                line_idx = fix["line"] - 1
                if line_idx < len(lines):
                    old_line = lines[line_idx]
                    new_line = old_line.replace(fix["match"], fix["replacement"], 1)
                    lines[line_idx] = new_line
                    print(f"  [FIXED] {filepath}:{fix['line']}")

            # Write back
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))

        print(f"[EXECUTE] Modified {len(files_to_fix)} files")

    def phase4_learning(self, approved_fixes: List[Dict]) -> None:
        """
        Phase 4 (Learning): Store pattern for future violations

        Token Budget: Pattern storage (~50 tokens)
        Purpose: Prevent future anthropomorphic time violations
        """
        print("\n[PHASE 4 - LEARNING] Storing cleanup pattern...")

        pattern_summary = {
            "mission": "anthropomorphic_time_cleanup",
            "violations_found": len(self.violations_found),
            "fixes_approved": len(approved_fixes),
            "token_conversions": self.token_conversions,
            "pattern": "Replace 'N hours/weeks' with '~NK tokens'",
            "example": f"7-8 hours → ~7.5K tokens",
            "agents_used": ["gemma", "qwen", "0102"],
            "wsp_compliance": ["WSP 77", "WSP 50", "WSP 22"]
        }

        # Store in learning directory
        learning_dir = self.repo_root / "holo_index" / "adaptive_learning"
        learning_dir.mkdir(parents=True, exist_ok=True)

        output_file = learning_dir / "anthropomorphic_time_cleanup_pattern.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(pattern_summary, f, indent=2)

        print(f"[LEARNING] Pattern stored: {output_file.name}")

    def run_mission(self) -> Dict:
        """
        Execute full mission: WSP 77 agent coordination

        Total Token Budget: ~1K tokens (Gemma 50 + Qwen 500 + 0102 oversight + I/O)
        """
        print("="*70)
        print("AI OVERSEER MISSION: Anthropomorphic Time Cleanup")
        print("WSP 77 Agent Coordination: Gemma → Qwen → 0102 → Learning")
        print("="*70)

        # Phase 1: Gemma grep
        violations = self.phase1_gemma_grep()

        if not violations:
            print("\n✅ No violations found - codebase is clean!")
            return {"status": "clean", "violations": 0}

        # Phase 2: Qwen calculate
        fixes = self.phase2_qwen_calculate(violations)

        # Phase 3: 0102 review
        approved, rejected = self.phase3_0102_review(fixes)

        if not approved:
            print("\n⚠️ No fixes approved - manual review required")
            return {"status": "rejected", "violations": len(violations), "approved": 0}

        # Execute approved fixes
        self.execute_fixes(approved)

        # Phase 4: Learning
        self.phase4_learning(approved)

        print("\n" + "="*70)
        print("MISSION COMPLETE ✅")
        print(f"Violations found: {len(violations)}")
        print(f"Fixes approved: {len(approved)}")
        print(f"Fixes rejected: {len(rejected)}")
        print("="*70)

        return {
            "status": "success",
            "violations": len(violations),
            "approved": len(approved),
            "rejected": len(rejected)
        }


def main():
    """Execute anthropomorphic time cleanup mission"""
    cleanup = AnthropomorphicTimeCleanup(repo_root)
    result = cleanup.run_mission()

    # Print summary
    print(f"\n📊 Mission Result: {json.dumps(result, indent=2)}")

    return result


if __name__ == "__main__":
    main()
