"""
Parallel council evaluation using multiprocessing (S5 in ROADMAP).
Per WSP 84: Extends existing council with parallel execution.
"""

import os
import json
import multiprocessing as mp
from typing import Dict, List, Tuple, Any
from concurrent.futures import ProcessPoolExecutor, as_completed
from functools import partial


def evaluate_script_worker(script: str, config: Dict) -> Dict:
    """
    Worker function to evaluate a single script.
    Runs in separate process for parallelism.
    """
    from modules.ai_intelligence.pqn_alignment.src.detector.api import run_detector
    
    # Run detector for this script
    events_path, metrics_csv = run_detector({
        "script": script,
        "steps": config.get("steps", 1200),
        "steps_per_sym": config.get("steps_per_sym", 120),
        "dt": config.get("dt", 0.5/7.05),
        "seed": config.get("seed", 0),
        "out_dir": config.get("out_dir", "logs/council"),
        "log_csv": f"council_{script.replace('.', 'dot')}.csv",
        "events": f"council_{script.replace('.', 'dot')}.jsonl",
    })
    
    # Count PQN and paradox events
    pqn_count = 0
    paradox_count = 0
    resonance_count = 0
    
    if os.path.exists(events_path):
        with open(events_path, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    event = json.loads(line)
                    flags = event.get("flags", [])
                    if "PQN_DETECTED" in flags:
                        pqn_count += 1
                    if "PARADOX_RISK" in flags:
                        paradox_count += 1
                    if "RESONANCE_HIT" in flags:
                        resonance_count += 1
                except:
                    continue
    
    # Normalize rates per 1k steps
    steps = config.get("steps", 1200)
    pqn_rate = (pqn_count * 1000) / steps
    paradox_rate = (paradox_count * 1000) / steps
    resonance_rate = (resonance_count * 1000) / steps
    
    return {
        "script": script,
        "pqn_rate": pqn_rate,
        "paradox_rate": paradox_rate,
        "resonance_rate": resonance_rate,
        "pqn_count": pqn_count,
        "paradox_count": paradox_count,
        "resonance_count": resonance_count,
    }


def parallel_council_evaluate(proposals: List[Dict], 
                            config: Dict,
                            max_workers: int = None) -> List[Dict]:
    """
    Evaluate multiple proposals in parallel.
    
    Args:
        proposals: List of proposal dicts with 'scripts' key
        config: Evaluation config (steps, dt, seed, etc.)
        max_workers: Max parallel processes (default: CPU count)
    
    Returns:
        List of evaluation results
    """
    if max_workers is None:
        max_workers = min(mp.cpu_count(), 4)  # Cap at 4 for stability
    
    # Flatten all scripts from proposals
    all_scripts = []
    for prop in proposals:
        scripts = prop.get("scripts", [])
        for script in scripts:
            all_scripts.append({
                "script": script,
                "author": prop.get("author", "unknown"),
                "proposal_idx": proposals.index(prop),
            })
    
    results = []
    
    # Evaluate scripts in parallel
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        # Submit all evaluations
        future_to_script = {}
        for script_info in all_scripts:
            future = executor.submit(
                evaluate_script_worker,
                script_info["script"],
                config
            )
            future_to_script[future] = script_info
        
        # Collect results as they complete
        for future in as_completed(future_to_script):
            script_info = future_to_script[future]
            try:
                result = future.result(timeout=60)  # 60s timeout per script
                result.update(script_info)  # Add metadata
                results.append(result)
            except Exception as e:
                print(f"Error evaluating {script_info['script']}: {e}")
                # Add failed result
                results.append({
                    **script_info,
                    "pqn_rate": 0,
                    "paradox_rate": 0,
                    "resonance_rate": 0,
                    "error": str(e),
                })
    
    return results


def council_scoring_strategies(results: List[Dict], 
                              strategies: List[Dict]) -> List[Dict]:
    """
    Apply different scoring strategies to results.
    
    Strategies:
    - pqn_maximizer: Maximize PQN detection
    - paradox_minimizer: Minimize paradox risk
    - alternation_explorer: Favor alternating patterns
    - harmonic_seeker: Maximize resonance hits
    """
    scored_results = []
    
    for result in results:
        scores = {}
        
        for strategy in strategies:
            role = strategy.get("role", "balanced")
            weight = strategy.get("weight", 1.0)
            
            if role == "pqn_maximizer":
                score = result["pqn_rate"] * 3.0
            elif role == "paradox_minimizer":
                score = 100.0 - result["paradox_rate"] * 2.0
            elif role == "alternation_explorer":
                # Favor scripts with alternating symbols
                script = result.get("script", "")
                alternations = sum(1 for i in range(len(script)-1) 
                                 if script[i] != script[i+1])
                score = alternations * 10.0 + result["pqn_rate"]
            elif role == "harmonic_seeker":
                score = result["resonance_rate"] * 2.0
            else:  # balanced
                score = (result["pqn_rate"] * 2.0 - 
                        result["paradox_rate"] * 1.5 + 
                        result["resonance_rate"] * 0.5)
            
            scores[role] = score * weight
        
        # Compute consensus score
        result["scores"] = scores
        result["consensus_score"] = sum(scores.values()) / len(scores)
        scored_results.append(result)
    
    # Sort by consensus score
    scored_results.sort(key=lambda x: x["consensus_score"], reverse=True)
    
    return scored_results


def parallel_council_run(config: Dict) -> Tuple[str, str]:
    """
    Enhanced council run with parallel evaluation.
    
    Config keys:
        proposals: List of proposal dicts
        strategies: List of scoring strategies
        max_workers: Max parallel processes
        consensus_threshold: Minimum consensus for selection
        top_n: Number of top results to return
    """
    proposals = config.get("proposals", [])
    strategies = config.get("strategies", [
        {"role": "pqn_maximizer", "weight": 1.0},
        {"role": "paradox_minimizer", "weight": 0.8},
        {"role": "alternation_explorer", "weight": 0.6},
    ])
    max_workers = config.get("max_workers", 4)
    top_n = config.get("top_n", 5)
    out_dir = config.get("out_dir", "logs/council")
    
    os.makedirs(out_dir, exist_ok=True)
    
    # Parallel evaluation
    print(f"Evaluating {len(proposals)} proposals with {max_workers} workers...")
    results = parallel_council_evaluate(proposals, config, max_workers)
    
    # Apply scoring strategies
    print(f"Applying {len(strategies)} scoring strategies...")
    scored_results = council_scoring_strategies(results, strategies)
    
    # Select top results
    top_results = scored_results[:top_n]
    
    # Save results
    summary_path = os.path.join(out_dir, "parallel_summary.json")
    archive_path = os.path.join(out_dir, "parallel_archive.json")
    
    with open(summary_path, "w") as f:
        json.dump({
            "results": scored_results,
            "top": top_results,
            "strategies": strategies,
            "config": config,
        }, f, indent=2)
    
    with open(archive_path, "w") as f:
        json.dump({
            "top_scripts": [r["script"] for r in top_results],
            "top_scores": [r["consensus_score"] for r in top_results],
        }, f, indent=2)
    
    print(f"Results saved to {summary_path}")
    return summary_path, archive_path