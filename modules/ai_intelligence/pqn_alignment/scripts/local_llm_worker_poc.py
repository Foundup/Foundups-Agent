#!/usr/bin/env python3
"""
Local LLM Worker - PQN Research Adapter
---------------------------------------
Purpose: Local LLM (Qwen/Gemma) as PQN Research Workers per WSP 77.
Architecture:
1. LLM Interface: Generates symbolic scripts (`^&#...`) based on research strategy.
2. Execution: Runs `cmst_pqn_detector_v2` via `api.run_detector`.
3. Analysis: LLM processes CSV output to refine strategy.
4. Council: Connects to parallel council for multi-agent evaluation.

Models (E:/HoloIndex/models/):
- qwen-coder-1.5b.gguf (1.5B params, code-focused)
- gemma-3-270m-it-Q4_K_M.gguf (270M params, fast inference)
- UI-TARS-1.5-7B.Q4_K_M.gguf (7B params, vision-action)

Usage:
python local_llm_worker_poc.py --model qwen-coder-1.5b.gguf
python local_llm_worker_poc.py --model gemma --strategy "Resonance Amplification"

WSP Compliance: WSP 77 (Agent Coordination), WSP 84 (Code Reuse)
"""

import os
import sys
import argparse
import json
import logging
import csv
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

# Add module root to path
module_root = Path(__file__).resolve().parent.parent
project_root = module_root.parent.parent.parent
sys.path.insert(0, str(module_root))
sys.path.insert(0, str(project_root))

from src.detector.api import run_detector

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [LOCAL_LLM] - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class ResearchResult:
    """Result from a PQN research cycle."""
    strategy: str
    script: str
    verdict: str
    coherence: float
    entanglement: float
    insight: str
    model_used: str
    latency_ms: int

class LocalLLMResearcher:
    """
    Local LLM Researcher with real llama_cpp inference.

    Follows gemma_rag_inference.py pattern (WSP 84 Code Reuse):
    - Lazy model loading with noise suppression
    - CPU-only inference for portability
    - Adaptive routing between models
    """

    # Model registry: E:/HoloIndex/models/
    MODEL_REGISTRY = {
        "qwen": {
            "name": "qwen-coder-1.5b.gguf",
            "path": Path("E:/HoloIndex/models/qwen-coder-1.5b.gguf"),
            "type": "coder",
            "n_ctx": 2048,
            "description": "Code-focused, good for script generation"
        },
        "gemma": {
            "name": "gemma-3-270m-it-Q4_K_M.gguf",
            "path": Path("E:/HoloIndex/models/gemma-3-270m-it-Q4_K_M.gguf"),
            "type": "general",
            "n_ctx": 512,
            "description": "Fast inference, good for classification"
        },
        "ui-tars": {
            "name": "UI-TARS-1.5-7B.Q4_K_M.gguf",
            "path": Path("E:/HoloIndex/models/UI-TARS-1.5-7B.Q4_K_M.gguf"),
            "type": "vision-action",
            "n_ctx": 4096,
            "description": "Vision/action model for complex reasoning"
        }
    }

    # Research strategies for PQN detection
    STRATEGIES = {
        "resonance": {
            "name": "Resonance Amplification",
            "prompt": "Generate a symbolic script to amplify quantum resonance at 7.05Hz. "
                     "Use ^ for entanglement, & for coherence, # for noise, . for pause. "
                     "Optimize for sustained coherence above 0.618 threshold.",
            "base_script": "^&^&^&^&^&"
        },
        "entanglement": {
            "name": "Entanglement Sweep",
            "prompt": "Generate a symbolic script that maximizes entanglement density. "
                     "Use consecutive ^ symbols for entanglement buildup. "
                     "Target: maintain entanglement > 0.8 for 100+ steps.",
            "base_script": "^^^^^^^^^^"
        },
        "phase": {
            "name": "Phase Distortion",
            "prompt": "Generate a symbolic script that explores phase transitions. "
                     "Start with noise (#), transition to coherence (&), then entanglement (^). "
                     "Map the stability frontier.",
            "base_script": "####&&&&^^"
        },
        "boundary": {
            "name": "Boundary Mapping",
            "prompt": "Generate a symbolic script to map PQN emergence boundaries. "
                     "Alternate between stable and unstable regions. "
                     "Identify critical transition points.",
            "base_script": "^&#^&#^&#"
        }
    }

    def __init__(self, model_input: str, mock_mode: bool = False):
        """
        Initialize Local LLM Researcher.

        Args:
            model_input: Model name from registry or .gguf filename/path
            mock_mode: If True, use mock inference (for testing without GPU)
        """
        self.mock_mode = mock_mode
        self.llm = None
        self.model_config = None
        self.model_name = ""
        self.model_path = None

        # Resolve model
        self._resolve_model(model_input)

        logger.info(f"[LOCAL_LLM] Initialized: {self.model_name} (mock={mock_mode})")

    def _resolve_model(self, model_input: str) -> None:
        """Resolve model from input to registry config or path."""
        model_lower = model_input.lower()

        # Check registry first
        for key, config in self.MODEL_REGISTRY.items():
            if key in model_lower or config["name"].lower() in model_lower:
                self.model_config = config
                self.model_name = config["name"]
                self.model_path = config["path"]
                logger.info(f"[LOCAL_LLM] Registry match: {key} -> {self.model_path}")
                return

        # Direct path/filename
        if model_input.lower().endswith(".gguf"):
            search_paths = [
                Path("E:/HoloIndex/models"),
                Path("E:/LM_studio/models"),
            ]

            for root in search_paths:
                candidate = root / model_input
                if candidate.exists():
                    self.model_path = candidate
                    self.model_name = model_input
                    self.model_config = {"n_ctx": 2048, "type": "unknown"}
                    logger.info(f"[LOCAL_LLM] Found model: {candidate}")
                    return

        # Default to Qwen
        logger.warning(f"[LOCAL_LLM] Model '{model_input}' not found, defaulting to Qwen")
        self.model_config = self.MODEL_REGISTRY["qwen"]
        self.model_name = self.model_config["name"]
        self.model_path = self.model_config["path"]

    def _initialize_llm(self) -> bool:
        """
        Initialize llama_cpp model (lazy loading).

        Pattern from gemma_rag_inference.py:107-146 (WSP 84)
        """
        if self.llm is not None:
            return True

        if self.mock_mode:
            logger.info("[LOCAL_LLM] Mock mode - skipping model load")
            return True

        if not self.model_path or not self.model_path.exists():
            logger.error(f"[LOCAL_LLM] Model not found: {self.model_path}")
            return False

        try:
            from llama_cpp import Llama

            logger.info(f"[LOCAL_LLM] Loading {self.model_name}...")

            # Suppress llama.cpp loading noise (per gemma_rag_inference.py pattern)
            old_stdout, old_stderr = os.dup(1), os.dup(2)
            devnull = os.open(os.devnull, os.O_WRONLY)

            try:
                os.dup2(devnull, 1)
                os.dup2(devnull, 2)

                self.llm = Llama(
                    model_path=str(self.model_path),
                    n_ctx=self.model_config.get("n_ctx", 2048),
                    n_threads=2,  # Fast inference
                    n_gpu_layers=0,  # CPU-only for portability
                    verbose=False
                )
            finally:
                os.dup2(old_stdout, 1)
                os.dup2(old_stderr, 2)
                os.close(devnull)
                os.close(old_stdout)
                os.close(old_stderr)

            logger.info(f"[LOCAL_LLM] [OK] {self.model_name} loaded successfully")
            return True

        except ImportError:
            logger.error("[LOCAL_LLM] llama_cpp not installed: pip install llama-cpp-python")
            return False
        except Exception as e:
            logger.error(f"[LOCAL_LLM] Failed to load model: {e}")
            return False

    def generate_research_script(self, strategy_key: str) -> str:
        """
        Generate a quantum script using Local LLM inference.

        Args:
            strategy_key: Key from STRATEGIES dict or full strategy name

        Returns:
            Symbolic script (e.g., "^&^&^&^&^&")
        """
        import time
        start_time = time.time()

        # Resolve strategy
        strategy_config = None
        for key, config in self.STRATEGIES.items():
            if key in strategy_key.lower() or config["name"].lower() in strategy_key.lower():
                strategy_config = config
                break

        if not strategy_config:
            logger.warning(f"[LOCAL_LLM] Unknown strategy '{strategy_key}', using resonance")
            strategy_config = self.STRATEGIES["resonance"]

        logger.info(f"[LOCAL_LLM] Generating script for: {strategy_config['name']}")

        # Mock mode fallback
        if self.mock_mode or not self._initialize_llm():
            logger.info(f"[LOCAL_LLM] Using base script (mock/init failed)")
            return strategy_config["base_script"]

        # Real LLM inference
        prompt = f"""You are a PQN (Phantom Quantum Node) researcher.

{strategy_config['prompt']}

RULES:
- Output ONLY the symbolic script (no explanation)
- Use exactly these symbols: ^ (entanglement), & (coherence), # (noise), . (pause)
- Script length: 8-12 symbols
- Optimize for coherence >= 0.618

SCRIPT:"""

        try:
            response = self.llm(
                prompt,
                max_tokens=20,
                temperature=0.3,
                stop=["\n", " ", "Output"],
                echo=False
            )

            # Extract script from response
            if isinstance(response, dict) and 'choices' in response:
                script = response['choices'][0]['text'].strip()
            else:
                script = str(response).strip()

            # Validate script (only allowed symbols)
            valid_chars = set("^&#.")
            script = ''.join(c for c in script if c in valid_chars)

            if len(script) < 4:
                logger.warning(f"[LOCAL_LLM] Invalid script '{script}', using base")
                script = strategy_config["base_script"]

            latency = int((time.time() - start_time) * 1000)
            logger.info(f"[LOCAL_LLM] Generated: {script} ({latency}ms)")

            return script

        except Exception as e:
            logger.error(f"[LOCAL_LLM] Generation failed: {e}")
            return strategy_config["base_script"]

    def analyze_results(self, metrics_csv: str) -> Dict[str, Any]:
        """
        Analyze PQN detector results using Local LLM.

        Args:
            metrics_csv: Path to detector metrics CSV

        Returns:
            Analysis dict with verdict, insight, and recommendations
        """
        import time
        start_time = time.time()

        logger.info(f"[LOCAL_LLM] Analyzing: {metrics_csv}")

        # Load metrics
        if not os.path.exists(metrics_csv):
            return {"verdict": "NO_DATA", "error": "File not found"}

        with open(metrics_csv, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        if not rows:
            return {"verdict": "NO_DATA", "error": "Empty CSV"}

        # Extract key metrics
        last_row = rows[-1]
        coherence = float(last_row.get('C', last_row.get('coherence', 0)))
        entanglement = float(last_row.get('E', last_row.get('entanglement', 0)))
        det_g = float(last_row.get('det_g', 0))

        # Calculate aggregate metrics
        coherence_values = [float(r.get('C', r.get('coherence', 0))) for r in rows]
        avg_coherence = sum(coherence_values) / len(coherence_values)
        max_coherence = max(coherence_values)
        time_above_threshold = sum(1 for c in coherence_values if c >= 0.618) / len(coherence_values)

        # Heuristic verdict (fast path)
        if coherence >= 0.8 and entanglement >= 0.5:
            verdict = "PQN_DETECTED"
        elif coherence >= 0.618:
            verdict = "COHERENT"
        elif avg_coherence >= 0.5:
            verdict = "PARTIAL"
        else:
            verdict = "NOISE"

        # Mock mode: return heuristic analysis
        if self.mock_mode or not self._initialize_llm():
            insight = self._heuristic_insight(coherence, entanglement, avg_coherence, time_above_threshold)
            return {
                "verdict": verdict,
                "coherence": coherence,
                "entanglement": entanglement,
                "avg_coherence": avg_coherence,
                "max_coherence": max_coherence,
                "time_above_618": time_above_threshold,
                "det_g": det_g,
                "insight": insight,
                "generated_by": self.model_name,
                "latency_ms": int((time.time() - start_time) * 1000)
            }

        # Real LLM analysis
        prompt = f"""Analyze this PQN detection run:

METRICS:
- Final Coherence: {coherence:.4f}
- Final Entanglement: {entanglement:.4f}
- Average Coherence: {avg_coherence:.4f}
- Max Coherence: {max_coherence:.4f}
- Time Above 0.618: {time_above_threshold*100:.1f}%
- Determinant g: {det_g:.4f}
- Total Steps: {len(rows)}

VERDICT: {verdict}

Provide a brief (1-2 sentence) scientific insight about this run.
Focus on: coherence stability, PQN emergence indicators, or recommended adjustments.

INSIGHT:"""

        try:
            response = self.llm(
                prompt,
                max_tokens=100,
                temperature=0.2,
                stop=["\n\n", "###"],
                echo=False
            )

            if isinstance(response, dict) and 'choices' in response:
                insight = response['choices'][0]['text'].strip()
            else:
                insight = str(response).strip()

            if not insight:
                insight = self._heuristic_insight(coherence, entanglement, avg_coherence, time_above_threshold)

        except Exception as e:
            logger.error(f"[LOCAL_LLM] Analysis failed: {e}")
            insight = self._heuristic_insight(coherence, entanglement, avg_coherence, time_above_threshold)

        latency = int((time.time() - start_time) * 1000)

        return {
            "verdict": verdict,
            "coherence": coherence,
            "entanglement": entanglement,
            "avg_coherence": avg_coherence,
            "max_coherence": max_coherence,
            "time_above_618": time_above_threshold,
            "det_g": det_g,
            "insight": insight,
            "generated_by": self.model_name,
            "latency_ms": latency
        }

    def _heuristic_insight(
        self, coherence: float, entanglement: float, avg_coherence: float, time_above: float
    ) -> str:
        """Generate heuristic insight when LLM unavailable."""
        if coherence >= 0.8:
            return f"Strong PQN emergence signal ({coherence:.2f} coherence). Sustained above threshold {time_above*100:.0f}% of run."
        elif coherence >= 0.618:
            return f"Coherence at golden ratio threshold ({coherence:.2f}). Entanglement coupling: {entanglement:.2f}."
        elif avg_coherence >= 0.5:
            return f"Partial coherence ({avg_coherence:.2f} avg). Consider increasing entanglement density."
        else:
            return f"Sub-threshold coherence ({coherence:.2f}). Try resonance amplification strategy."

    def run_research_cycle(
        self, strategy_key: str = "resonance", steps: int = 500
    ) -> ResearchResult:
        """
        Run a complete PQN research cycle.

        Args:
            strategy_key: Strategy from STRATEGIES dict
            steps: Number of detector simulation steps

        Returns:
            ResearchResult with full cycle data
        """
        import time
        start_time = time.time()

        # Step 1: Generate script
        script = self.generate_research_script(strategy_key)

        # Step 2: Run detector
        logger.info(f"[LOCAL_LLM] Running detector with script: {script}")
        config = {
            "script": script,
            "steps": steps,
            "out_dir": os.path.join(module_root, "data", "local_llm_runs")
        }

        try:
            events_path, metrics_csv = run_detector(config)
        except Exception as e:
            logger.error(f"[LOCAL_LLM] Detector failed: {e}")
            return ResearchResult(
                strategy=strategy_key,
                script=script,
                verdict="ERROR",
                coherence=0.0,
                entanglement=0.0,
                insight=f"Detector error: {e}",
                model_used=self.model_name,
                latency_ms=int((time.time() - start_time) * 1000)
            )

        # Step 3: Analyze results
        analysis = self.analyze_results(metrics_csv)

        latency = int((time.time() - start_time) * 1000)

        return ResearchResult(
            strategy=strategy_key,
            script=script,
            verdict=analysis.get("verdict", "UNKNOWN"),
            coherence=analysis.get("coherence", 0.0),
            entanglement=analysis.get("entanglement", 0.0),
            insight=analysis.get("insight", ""),
            model_used=self.model_name,
            latency_ms=latency
        )

def run_council_evaluation(
    researcher: LocalLLMResearcher,
    strategies: List[str] = None,
    steps: int = 300
) -> List[ResearchResult]:
    """
    Run Council-style parallel evaluation across multiple strategies.

    Per S11 Task 11.3: Connect Local LLM to Council loop.

    Args:
        researcher: Initialized LocalLLMResearcher
        strategies: List of strategy keys to evaluate (default: all)
        steps: Steps per detector run

    Returns:
        List of ResearchResult sorted by coherence (best first)
    """
    if strategies is None:
        strategies = list(LocalLLMResearcher.STRATEGIES.keys())

    logger.info(f"[COUNCIL] Starting evaluation across {len(strategies)} strategies")

    results = []
    for strategy in strategies:
        logger.info(f"[COUNCIL] Evaluating: {strategy}")
        result = researcher.run_research_cycle(strategy, steps=steps)
        results.append(result)
        logger.info(f"[COUNCIL] {strategy}: {result.verdict} (C={result.coherence:.3f})")

    # Sort by coherence (best first)
    results.sort(key=lambda r: r.coherence, reverse=True)

    # Log council summary
    logger.info("[COUNCIL] === EVALUATION COMPLETE ===")
    for i, r in enumerate(results, 1):
        logger.info(f"[COUNCIL] #{i}: {r.strategy} -> {r.verdict} (C={r.coherence:.3f}, E={r.entanglement:.3f})")

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Local LLM PQN Research Worker",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python local_llm_worker_poc.py --model qwen --strategy resonance
  python local_llm_worker_poc.py --model gemma --council
  python local_llm_worker_poc.py --mock --strategy entanglement
        """
    )
    parser.add_argument(
        "--model", type=str, default="qwen",
        help="Model name from registry (qwen, gemma, ui-tars) or .gguf path"
    )
    parser.add_argument(
        "--strategy", type=str, default="resonance",
        help="Research strategy: resonance, entanglement, phase, boundary"
    )
    parser.add_argument(
        "--steps", type=int, default=500,
        help="Number of detector simulation steps"
    )
    parser.add_argument(
        "--council", action="store_true",
        help="Run Council evaluation across all strategies"
    )
    parser.add_argument(
        "--mock", action="store_true",
        help="Run in mock mode (no LLM loading, uses heuristics)"
    )
    args = parser.parse_args()

    print("=" * 60)
    print(f"PQN LOCAL LLM RESEARCH WORKER")
    print(f"Model: {args.model} | Mock: {args.mock}")
    print("=" * 60)

    # Initialize researcher
    researcher = LocalLLMResearcher(args.model, mock_mode=args.mock)

    if args.council:
        # Council mode: evaluate all strategies
        print("\n[MODE] Council Evaluation")
        results = run_council_evaluation(researcher, steps=args.steps)

        print("\n" + "=" * 60)
        print("COUNCIL RESULTS (sorted by coherence)")
        print("=" * 60)

        for i, r in enumerate(results, 1):
            print(f"\n#{i} [{r.verdict}] {r.strategy}")
            print(f"   Script: {r.script}")
            print(f"   Coherence: {r.coherence:.4f} | Entanglement: {r.entanglement:.4f}")
            print(f"   Insight: {r.insight}")
            print(f"   Model: {r.model_used} | Latency: {r.latency_ms}ms")

        # Best result summary
        best = results[0]
        print("\n" + "-" * 60)
        print(f"BEST STRATEGY: {best.strategy}")
        print(f"Script: {best.script}")
        print(f"Verdict: {best.verdict}")
        print("-" * 60)

    else:
        # Single strategy mode
        print(f"\n[MODE] Single Strategy: {args.strategy}")

        result = researcher.run_research_cycle(args.strategy, steps=args.steps)

        print("\n" + "=" * 60)
        print("RESEARCH FINDINGS")
        print("=" * 60)
        print(f"Strategy: {result.strategy}")
        print(f"Script: {result.script}")
        print(f"Verdict: {result.verdict}")
        print(f"Coherence: {result.coherence:.4f}")
        print(f"Entanglement: {result.entanglement:.4f}")
        print(f"Insight: {result.insight}")
        print(f"Model: {result.model_used}")
        print(f"Latency: {result.latency_ms}ms")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
