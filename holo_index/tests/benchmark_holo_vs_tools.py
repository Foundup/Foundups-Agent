#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick Benchmark: HoloIndex vs Traditional Tools

Generates comparison report for:
- HoloIndex semantic search
- ripgrep (rg)
- grep
- glob (Python)
- Visual Studio Code search

Run with:
    python holo_index/tests/benchmark_holo_vs_tools.py
"""

import time
import subprocess
import shutil
import os
from pathlib import Path
from typing import Dict, List, Tuple, Optional


REPO_ROOT = Path(__file__).resolve().parents[2]
PYTHON_EXE = REPO_ROOT / ".venv" / "Scripts" / "python.exe" if shutil.which("python") is None else "python"


class BenchmarkRunner:
    """Run benchmarks and collect metrics."""

    def __init__(self):
        self.results = []

    def run_holo(self, query: str, limit: int = 3) -> Tuple[bool, float, int]:
        """
        Run HoloIndex search.

        Returns:
            (found: bool, time: float, result_count: int)
        """
        cmd = [str(PYTHON_EXE), "holo_index.py", "--search", query, "--limit", str(limit)]

        start = time.time()
        try:
            result = subprocess.run(
                cmd,
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=int(os.getenv("BENCH_HOLO_TIMEOUT", "60"))
            )
            elapsed = time.time() - start

            found = "[SOLUTION FOUND]" in result.stdout or "[RESULTS]" in result.stdout
            # Count results
            result_count = (
                result.stdout.count("[CODE]") +
                result.stdout.count("[WSP]") +
                result.stdout.count("[TEST]") +
                result.stdout.count("[SKILL]")
            )

            return found, elapsed, result_count

        except Exception as e:
            elapsed = time.time() - start
            return False, elapsed, 0

    def run_ripgrep(self, pattern: str, path: str = "modules") -> Tuple[bool, float, int]:
        """Run ripgrep."""
        rg_path = shutil.which("rg")
        if not rg_path:
            return False, 0.0, 0

        start = time.time()
        try:
            result = subprocess.run(
                [rg_path, "-n", pattern, path],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=int(os.getenv("BENCH_RG_TIMEOUT", "30"))
            )
            elapsed = time.time() - start

            found = len(result.stdout.strip()) > 0
            result_count = len(result.stdout.strip().split('\n')) if found else 0

            return found, elapsed, result_count

        except Exception as e:
            elapsed = time.time() - start
            return False, elapsed, 0

    def run_grep(self, pattern: str, path: str = "modules") -> Tuple[bool, float, int]:
        """Run traditional grep."""
        grep_path = shutil.which("grep")
        if not grep_path:
            return False, 0.0, 0

        start = time.time()
        try:
            result = subprocess.run(
                [grep_path, "-r", "-n", pattern, path],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=int(os.getenv("BENCH_GREP_TIMEOUT", "60"))
            )
            elapsed = time.time() - start

            found = len(result.stdout.strip()) > 0
            result_count = len(result.stdout.strip().split('\n')) if found else 0

            return found, elapsed, result_count

        except Exception as e:
            elapsed = time.time() - start
            return False, elapsed, 0

    def run_glob(self, pattern: str) -> Tuple[bool, float, int]:
        """Run Python glob search."""
        start = time.time()
        try:
            matches = list(REPO_ROOT.glob(f"**/*{pattern}*"))
            elapsed = time.time() - start

            return len(matches) > 0, elapsed, len(matches)

        except Exception as e:
            elapsed = time.time() - start
            return False, elapsed, 0

    def benchmark_query(self, query: str, query_type: str) -> Dict:
        """
        Benchmark a single query across all tools.

        Args:
            query: Search query
            query_type: Type of query (literal, semantic, natural_language, filename)
        """
        print(f"\nBenchmarking: {query_type.upper()} - '{query}'")

        # HoloIndex
        print("  Running HoloIndex...", end=" ")
        holo_found, holo_time, holo_count = self.run_holo(query)
        print(f"{'FOUND' if holo_found else 'NOT FOUND'} ({holo_time:.2f}s, {holo_count} results)")

        # ripgrep
        print("  Running ripgrep...", end=" ")
        rg_found, rg_time, rg_count = self.run_ripgrep(query)
        print(f"{'FOUND' if rg_found else 'NOT FOUND'} ({rg_time:.2f}s, {rg_count} results)")

        # grep
        print("  Running grep...", end=" ")
        grep_found, grep_time, grep_count = self.run_grep(query)
        print(f"{'FOUND' if grep_found else 'NOT FOUND'} ({grep_time:.2f}s, {grep_count} results)")

        result = {
            "query": query,
            "type": query_type,
            "holo": {"found": holo_found, "time": holo_time, "count": holo_count},
            "ripgrep": {"found": rg_found, "time": rg_time, "count": rg_count},
            "grep": {"found": grep_found, "time": grep_time, "count": grep_count},
        }

        self.results.append(result)
        return result

    def generate_report(self):
        """Generate comparison report."""
        print("\n" + "="*100)
        print("HOLOINDEX VS TRADITIONAL TOOLS - BENCHMARK REPORT")
        print("="*100)

        # Summary table
        print("\n{:<40} {:<20} {:<20} {:<20}".format(
            "Query", "HoloIndex", "ripgrep", "grep"
        ))
        print("-"*100)

        for r in self.results:
            holo_status = f"{'OK' if r['holo']['found'] else 'NO'} {r['holo']['time']:.2f}s ({r['holo']['count']})"
            rg_status = f"{'OK' if r['ripgrep']['found'] else 'NO'} {r['ripgrep']['time']:.2f}s ({r['ripgrep']['count']})"
            grep_status = f"{'OK' if r['grep']['found'] else 'NO'} {r['grep']['time']:.2f}s ({r['grep']['count']})"

            query_display = r['query'][:37] + "..." if len(r['query']) > 40 else r['query']

            print("{:<40} {:<20} {:<20} {:<20}".format(
                query_display, holo_status, rg_status, grep_status
            ))

        # Analysis
        print("\n" + "="*100)
        print("ANALYSIS")
        print("="*100)

        # Semantic queries found by HoloIndex but not by grep tools
        semantic_results = [r for r in self.results if r['type'] == 'semantic']
        semantic_advantage = [
            r for r in semantic_results
            if r['holo']['found'] and not r['ripgrep']['found'] and not r['grep']['found']
        ]

        print(f"\nSemantic Queries:")
        print(f"  Total tested: {len(semantic_results)}")
        print(f"  HoloIndex advantage (found by Holo, not by grep tools): {len(semantic_advantage)}")

        if semantic_advantage:
            print(f"  Examples:")
            for r in semantic_advantage[:3]:
                print(f"    - '{r['query']}'")

        # Performance comparison (literal queries)
        literal_results = [r for r in self.results if r['type'] == 'literal']
        if literal_results:
            avg_holo_time = sum(r['holo']['time'] for r in literal_results) / len(literal_results)
            avg_rg_time = sum(r['ripgrep']['time'] for r in literal_results if r['ripgrep']['found']) / max(1, len([r for r in literal_results if r['ripgrep']['found']]))

            print(f"\nLiteral Query Performance (average):")
            print(f"  HoloIndex: {avg_holo_time:.2f}s")
            print(f"  ripgrep: {avg_rg_time:.2f}s")
            print(f"  Speedup: {avg_holo_time / avg_rg_time:.2f}x {'slower' if avg_holo_time > avg_rg_time else 'faster'}")

        # Success rates
        holo_success = len([r for r in self.results if r['holo']['found']]) / len(self.results) * 100
        rg_success = len([r for r in self.results if r['ripgrep']['found']]) / len(self.results) * 100
        grep_success = len([r for r in self.results if r['grep']['found']]) / len(self.results) * 100

        print(f"\nSuccess Rates (% of queries finding results):")
        print(f"  HoloIndex: {holo_success:.1f}%")
        print(f"  ripgrep: {rg_success:.1f}%")
        print(f"  grep: {grep_success:.1f}%")

        print("\n" + "="*100)
        print("CONCLUSION")
        print("="*100)

        if len(semantic_advantage) > 0:
            print("\nOK: HoloIndex successfully finds semantic queries that traditional tools cannot")
            print("OK: Semantic search capability verified")
        else:
            print("\nWARN: Semantic advantage not demonstrated in this test set")

        if holo_success >= rg_success:
            print("OK: HoloIndex finds equal or more results than ripgrep")
        else:
            print("WARN: ripgrep found more literal matches (expected for grep tools)")

        print("\nHoloIndex Value Proposition:")
        print("  1. Semantic understanding (finds conceptual matches)")
        print("  2. Natural language queries (user-friendly)")
        print("  3. WSP compliance guidance (not just code results)")
        print("  4. Function-level precision (not just file matches)")
        print("  5. Module context awareness (prevents vibecoding)")

        print("\n" + "="*100)


def main():
    """Run benchmark suite."""
    print("HOLOINDEX BENCHMARK vs TRADITIONAL TOOLS")
    print("="*100)
    print(f"Repository: {REPO_ROOT}")
    print(f"Python: {PYTHON_EXE}")
    print(f"ripgrep: {shutil.which('rg') or 'NOT INSTALLED'}")
    print(f"grep: {shutil.which('grep') or 'NOT INSTALLED'}")

    runner = BenchmarkRunner()

    # Test queries
    test_suite = [
        # Literal queries (should be found by all tools)
        ("pendingClassificationItem", "literal"),
        ("def handle_holoindex_request", "literal"),
        ("HoloDAE", "literal"),

        # Semantic queries (HoloIndex advantage)
        ("code that handles chat messages", "semantic"),
        ("module health checking system", "semantic"),
        ("youtube live stream integration", "semantic"),
        ("database connection management", "semantic"),

        # Natural language queries (HoloIndex strength)
        ("how do I send messages to youtube", "natural_language"),
        ("check if module exists", "natural_language"),

        # Filename queries
        ("coordinator", "filename"),
    ]

    max_queries = int(os.getenv("BENCH_MAX_QUERIES", "0"))
    if max_queries > 0:
        test_suite = test_suite[:max_queries]

    for query, query_type in test_suite:
        runner.benchmark_query(query, query_type)

    # Generate report
    runner.generate_report()


if __name__ == "__main__":
    main()
