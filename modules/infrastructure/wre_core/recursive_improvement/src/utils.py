# -*- coding: utf-8 -*-
import sys
import io


import json
from pathlib import Path
from .core import ErrorPattern, Solution, Improvement
from typing import Dict

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

def save_pattern(memory_root: Path, pattern: ErrorPattern):
    """Save pattern to memory"""
    patterns_dir = memory_root / "error_patterns" / "by_type"
    patterns_dir.mkdir(parents=True, exist_ok=True)
    
    pattern_file = patterns_dir / f"{pattern.pattern_id}.json"
    with open(pattern_file, 'w') as f:
        json.dump(pattern.to_dict(), f, indent=2)
        
def save_solution(memory_root: Path, solution: Solution):
    """Save solution to memory"""
    solutions_dir = memory_root / "solutions" / solution.source
    solutions_dir.mkdir(parents=True, exist_ok=True)
    
    solution_file = solutions_dir / f"{solution.solution_id}.json"
    with open(solution_file, 'w') as f:
        json.dump(solution.to_dict(), f, indent=2)
        
def save_improvement(memory_root: Path, improvement: Improvement):
    """Save improvement to memory"""
    improvements_dir = memory_root / "improvements" / improvement.change_type
    improvements_dir.mkdir(parents=True, exist_ok=True)
    
    improvement_file = improvements_dir / f"{improvement.improvement_id}.json"
    with open(improvement_file, 'w') as f:
        json.dump(improvement.to_dict(), f, indent=2)

def load_memory(memory_root: Path) -> tuple[Dict[str, ErrorPattern], Dict[str, Solution], Dict[str, Improvement]]:
    """Load existing patterns and solutions from memory"""
    error_patterns = {}
    solutions = {}
    improvements = {}
    
    # Load error patterns
    patterns_dir = memory_root / "error_patterns"
    if patterns_dir.exists():
        for pattern_file in patterns_dir.rglob("*.json"):
            try:
                with open(pattern_file, 'r') as f:
                    data = json.load(f)
                    pattern = ErrorPattern.from_dict(data)
                    error_patterns[pattern.pattern_id] = pattern
            except Exception:
                pass  # Skip corrupted files
                
    # Load solutions
    solutions_dir = memory_root / "solutions"
    if solutions_dir.exists():
        for solution_file in solutions_dir.rglob("*.json"):
            try:
                with open(solution_file, 'r') as f:
                    data = json.load(f)
                    solution = Solution.from_dict(data)
                    solutions[solution.solution_id] = solution
            except Exception:
                pass
                
    # Load improvements
    improvements_dir = memory_root / "improvements"
    if improvements_dir.exists():
        for improvement_file in improvements_dir.rglob("*.json"):
            try:
                with open(improvement_file, 'r') as f:
                    data = json.load(f)
                    improvement = Improvement.from_dict(data)
                    improvements[improvement.improvement_id] = improvement
            except Exception:
                pass
    
    return error_patterns, solutions, improvements
