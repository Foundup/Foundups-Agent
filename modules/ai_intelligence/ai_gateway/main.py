#!/usr/bin/env python3
"""AI Gateway 0102 Agent - Auto-updates models, monitors research, runs OpenClaw.

Usage:
    python main.py                    # Full run: update models + research + OpenClaw
    python main.py --models           # Update model registry only
    python main.py --research         # Scan for relevant research only
    python main.py --openclaw         # Run OpenClaw optimizer on SIM only
    python main.py --status           # Show current registry status
"""

import argparse
import json
import re
import sys
from datetime import datetime, UTC
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from modules.ai_intelligence.ai_gateway.src.model_registry import (
    ALL_MODELS,
    MIGRATION_MAP,
    ModelStatus,
    ModelInfo,
    get_deprecated_models,
    get_current_models,
    print_registry_status,
)

# =============================================================================
# PROVIDER MODEL DISCOVERY URLS
# =============================================================================
PROVIDER_MODEL_SOURCES = {
    "openai": {
        "url": "https://platform.openai.com/docs/models",
        "search_terms": ["gpt-5", "gpt-5.2", "o3", "o4-mini", "latest model"],
    },
    "anthropic": {
        "url": "https://docs.anthropic.com/en/docs/about-claude/models",
        "search_terms": ["claude-opus-4", "claude-sonnet-4", "claude-5", "latest model"],
    },
    "google": {
        "url": "https://ai.google.dev/gemini-api/docs/models/gemini",
        "search_terms": ["gemini-3", "gemini-2.5", "latest model"],
    },
    "xai": {
        "url": "https://docs.x.ai/docs/models",
        "search_terms": ["grok-4", "grok-code", "latest model"],
    },
}

# Research topics to monitor
RESEARCH_TOPICS = [
    "tokenomics simulation optimization",
    "agent swarm coordination patterns",
    "crypto staking reward distribution",
    "demurrage currency implementation",
    "bonding curve mathematics",
    "DAO governance mechanisms",
    "AI parameter optimization reinforcement learning",
]

# Files/patterns to skip during codebase scan
SKIP_PATTERNS = [
    ".git", ".venv", "__pycache__", "node_modules", ".pyc",
    "model_registry.py", "ModLog.md", "CHANGELOG", "external_research",
]

SCAN_EXTENSIONS = {".py", ".json", ".yaml", ".yml", ".js", ".ts"}


def should_skip(path: Path) -> bool:
    """Check if path should be skipped."""
    return any(skip in str(path) for skip in SKIP_PATTERNS)


# =============================================================================
# MODEL AUTO-DISCOVERY
# =============================================================================

def discover_latest_models() -> Dict[str, List[str]]:
    """Discover latest models from provider documentation via web search.

    Returns dict of provider -> list of discovered model IDs.
    """
    discoveries = {}

    try:
        # Try to use web search if available
        from modules.ai_intelligence.ai_gateway.src.ai_gateway import AIGateway
        gateway = AIGateway()

        for provider, config in PROVIDER_MODEL_SOURCES.items():
            print(f"\n[DISCOVERY] Checking {provider}...")

            # Search for latest model announcements
            search_query = f"{provider} AI latest model 2026"

            try:
                # Use gateway to query about latest models
                prompt = f"""What are the latest {provider} AI models available as of February 2026?
List only the model IDs (e.g., gpt-4o, claude-opus-4-6).
Focus on production-ready models, not preview/beta."""

                result = gateway.call_with_fallback(prompt, task_type="quick")
                if result.success:
                    # Extract model IDs from response
                    model_ids = extract_model_ids(result.response, provider)
                    discoveries[provider] = model_ids
                    print(f"  Found: {model_ids}")
                else:
                    print(f"  No response from gateway")

            except Exception as e:
                print(f"  Error: {e}")

    except ImportError:
        print("[DISCOVERY] AIGateway not available - using static registry")

    return discoveries


def extract_model_ids(text: str, provider: str) -> List[str]:
    """Extract model IDs from text response."""
    model_ids = []

    # Provider-specific patterns (Feb 2026 current)
    patterns = {
        "openai": r"(gpt-5(?:\.\d+)?(?:-codex)?|o[34](?:-mini|-pro)?|gpt-\d+(?:\.\d+)?)",
        "anthropic": r"(claude-(?:opus|sonnet|haiku)-[\d\.-]+)",
        "google": r"(gemini-[\d\.]+-(?:pro|flash|ultra)(?:-preview|-lite)?)",
        "xai": r"(grok-(?:\d+|code-fast-\d+)(?:-fast|-mini)?)",
    }

    pattern = patterns.get(provider, r"[\w\-\.]+")
    matches = re.findall(pattern, text, re.IGNORECASE)

    return list(set(matches))


# =============================================================================
# RESEARCH MONITORING
# =============================================================================

def scan_research() -> List[Dict]:
    """Scan for relevant research papers and announcements."""
    findings = []

    try:
        from modules.ai_intelligence.ai_gateway.src.ai_gateway import AIGateway
        gateway = AIGateway()

        print("\n[RESEARCH] Scanning for relevant research...")

        for topic in RESEARCH_TOPICS:
            print(f"  Checking: {topic}")

            prompt = f"""Find recent research (2025-2026) on: {topic}
Summarize in 1-2 sentences. Include paper title if available.
Focus on practical implementations relevant to autonomous agent systems."""

            try:
                result = gateway.call_with_fallback(prompt, task_type="analysis")
                if result.success and len(result.response) > 20:
                    findings.append({
                        "topic": topic,
                        "summary": result.response[:500],
                        "provider": result.provider,
                    })
            except Exception as e:
                pass

    except ImportError:
        print("[RESEARCH] AIGateway not available")

    return findings


# =============================================================================
# CODEBASE MODEL SCANNER
# =============================================================================

def scan_codebase_models(root: Path) -> Dict[Path, List[Tuple[str, int, str]]]:
    """Scan codebase for deprecated model references."""
    results = {}
    deprecated = get_deprecated_models()

    for ext in SCAN_EXTENSIONS:
        for filepath in root.rglob(f"*{ext}"):
            if should_skip(filepath):
                continue

            try:
                content = filepath.read_text(encoding="utf-8", errors="ignore")
                lines = content.split("\n")

                findings = []
                for i, line in enumerate(lines, 1):
                    for model_id in deprecated.keys():
                        if model_id in line:
                            findings.append((model_id, i, line.strip()[:100]))

                if findings:
                    results[filepath] = findings

            except Exception:
                pass

    return results


def update_codebase_models(root: Path) -> int:
    """Update deprecated models in codebase."""
    updated = 0
    results = scan_codebase_models(root)

    for filepath in results.keys():
        try:
            content = filepath.read_text(encoding="utf-8")
            original = content

            for old_model, new_model in MIGRATION_MAP.items():
                for quote in ['"', "'"]:
                    content = content.replace(
                        f"{quote}{old_model}{quote}",
                        f"{quote}{new_model}{quote}"
                    )

            if content != original:
                filepath.write_text(content, encoding="utf-8")
                updated += 1
                print(f"  Updated: {filepath.relative_to(root)}")

        except Exception as e:
            print(f"  Error: {filepath}: {e}")

    return updated


# =============================================================================
# OPENCLAW SIMULATOR OPTIMIZATION
# =============================================================================

def run_openclaw_optimizer(
    objective: str = "balanced",
    max_iterations: int = 5,
    ticks: int = 300,
) -> Dict:
    """Run OpenClaw optimizer on the pAVS simulator."""

    print("\n" + "=" * 70)
    print("OPENCLAW 0102 - pAVS SIMULATOR OPTIMIZATION")
    print("=" * 70)
    print(f"Objective: {objective}")
    print(f"Max iterations: {max_iterations}")
    print(f"Ticks per evaluation: {ticks}")
    print()

    try:
        from modules.foundups.simulator.economics.ai_parameter_optimizer import (
            AIParameterOptimizer,
            OptimizerConfig,
            OptimizationObjective,
        )

        # Map string to enum
        objective_map = {
            "staker": OptimizationObjective.STAKER_DISTRIBUTION,
            "staker_distribution": OptimizationObjective.STAKER_DISTRIBUTION,
            "growth": OptimizationObjective.ECOSYSTEM_GROWTH,
            "ecosystem_growth": OptimizationObjective.ECOSYSTEM_GROWTH,
            "velocity": OptimizationObjective.TOKEN_VELOCITY,
            "token_velocity": OptimizationObjective.TOKEN_VELOCITY,
            "balanced": OptimizationObjective.BALANCED,
        }

        config = OptimizerConfig(
            objective=objective_map.get(objective, OptimizationObjective.BALANCED),
            max_iterations=max_iterations,
            ticks_per_evaluation=ticks,
            verbose=True,
        )

        optimizer = AIParameterOptimizer(config=config)

        print("[OPENCLAW] Starting optimization loop...")
        optimal_config, history = optimizer.optimize()

        summary = optimizer.get_optimization_summary()

        print("\n" + "=" * 70)
        print("OPTIMIZATION COMPLETE")
        print("=" * 70)
        print(f"Iterations: {summary['iterations']}")
        print(f"Best Score: {summary['best_score']:.4f}")
        print(f"Converged: {summary['convergence']}")
        print("\nOptimal Parameters:")
        for param, value in summary.get('best_config', {}).items():
            print(f"  {param}: {value}")

        return summary

    except ImportError as e:
        print(f"[OPENCLAW] Import error: {e}")
        return {"error": str(e)}
    except Exception as e:
        print(f"[OPENCLAW] Error: {e}")
        return {"error": str(e)}


# =============================================================================
# MAIN ORCHESTRATION
# =============================================================================

def run_full_agent(
    root: Path,
    update_models: bool = True,
    scan_research: bool = True,
    run_optimizer: bool = True,
    optimizer_objective: str = "balanced",
):
    """Run full 0102 agent: models + research + OpenClaw."""

    timestamp = datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC")

    print("=" * 70)
    print("AI GATEWAY 0102 AGENT")
    print("=" * 70)
    print(f"Timestamp: {timestamp}")
    print(f"Root: {root}")
    print()

    results = {
        "timestamp": timestamp,
        "model_updates": 0,
        "research_findings": [],
        "optimization": None,
    }

    # Phase 1: Model Discovery & Update
    if update_models:
        print("\n" + "-" * 70)
        print("PHASE 1: MODEL REGISTRY UPDATE")
        print("-" * 70)

        # Discover latest models
        discoveries = discover_latest_models()

        # Scan and update codebase
        print("\n[SCAN] Checking codebase for deprecated models...")
        scan_results = scan_codebase_models(root)

        if scan_results:
            total_refs = sum(len(f) for f in scan_results.values())
            print(f"  Found {total_refs} deprecated refs in {len(scan_results)} files")

            print("\n[UPDATE] Migrating deprecated models...")
            results["model_updates"] = update_codebase_models(root)
            print(f"  Updated {results['model_updates']} files")
        else:
            print("  All models are current!")

    # Phase 2: Research Monitoring
    if scan_research:
        print("\n" + "-" * 70)
        print("PHASE 2: RESEARCH MONITORING")
        print("-" * 70)

        findings = scan_research()
        results["research_findings"] = findings

        if findings:
            print(f"\nFound {len(findings)} relevant topics:")
            for f in findings:
                print(f"\n  [{f['topic']}]")
                print(f"  {f['summary'][:200]}...")
        else:
            print("  No new research findings")

    # Phase 3: OpenClaw Optimizer
    if run_optimizer:
        print("\n" + "-" * 70)
        print("PHASE 3: OPENCLAW OPTIMIZATION")
        print("-" * 70)

        results["optimization"] = run_openclaw_optimizer(
            objective=optimizer_objective,
            max_iterations=5,
            ticks=300,
        )

    # Summary
    print("\n" + "=" * 70)
    print("AGENT RUN COMPLETE")
    print("=" * 70)
    print(f"Model files updated: {results['model_updates']}")
    print(f"Research findings: {len(results['research_findings'])}")
    if results['optimization']:
        opt = results['optimization']
        if 'error' not in opt:
            print(f"Optimization score: {opt.get('best_score', 'N/A')}")
        else:
            print(f"Optimization: {opt.get('error')}")

    return results


def main():
    parser = argparse.ArgumentParser(
        description="AI Gateway 0102 Agent - Models, Research, OpenClaw"
    )
    parser.add_argument(
        "--models", action="store_true",
        help="Update model registry only"
    )
    parser.add_argument(
        "--research", action="store_true",
        help="Scan for relevant research only"
    )
    parser.add_argument(
        "--openclaw", action="store_true",
        help="Run OpenClaw optimizer only"
    )
    parser.add_argument(
        "--status", action="store_true",
        help="Show registry status"
    )
    parser.add_argument(
        "--objective", default="balanced",
        choices=["balanced", "staker", "growth", "velocity"],
        help="OpenClaw optimization objective"
    )
    parser.add_argument(
        "--path", type=Path, default=PROJECT_ROOT,
        help="Path to scan"
    )
    parser.add_argument(
        "--no-update", action="store_true",
        help="Scan only, don't update files"
    )

    args = parser.parse_args()

    if args.status:
        print_registry_status()
        return

    # Determine what to run
    run_models = args.models or not (args.research or args.openclaw)
    run_research_scan = args.research or not (args.models or args.openclaw)
    run_opt = args.openclaw or not (args.models or args.research)

    # If specific flags are set, only run those
    if args.models or args.research or args.openclaw:
        run_models = args.models
        run_research_scan = args.research
        run_opt = args.openclaw

    run_full_agent(
        root=args.path,
        update_models=run_models and not args.no_update,
        scan_research=run_research_scan,
        run_optimizer=run_opt,
        optimizer_objective=args.objective,
    )


if __name__ == "__main__":
    main()
