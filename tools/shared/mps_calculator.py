#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import io

"""
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

WSP Shared Module: MPS Calculator
=================================

Centralized Module Prioritization Score (MPS) calculation logic.
This module consolidates the MPS calculation functionality that was
duplicated across guided_dev_protocol.py, prioritize_module.py, 
and process_and_score_modules.py.

WSP Compliance:
- Follows WSP 13 (Test Creation & Management) guidelines
- Eliminates code duplication across utility tools
- Provides single source of truth for MPS calculations
- Supports both interactive and automated workflows

Author: FoundUps Agent Utility System
Version: 1.0.0
"""

from typing import Dict, Any, List, Tuple, Optional
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MPSCalculator:
    """
    Centralized Module Prioritization Score calculator.
    
    Implements the standard MPS formula:
    MPS = (IM*4) + (IP*5) + (ADV*4) + (ADF*3) + (DF*5) + (RF*3) - (CX*3)
    
    Where:
    - IM: Importance (1-5)
    - IP: Impact (1-5) 
    - ADV: AI Data Value (1-5)
    - ADF: AI Dev Feasibility (1-5)
    - DF: Dependency Factor (1-5)
    - RF: Risk Factor (1-5)
    - CX: Complexity (1-5, weighted negatively)
    """
    
    # Factor definitions - single source of truth
    FACTORS: Dict[str, Dict[str, Any]] = {
        "CX": {
            "name": "Complexity", 
            "weight": -3, 
            "desc": "(1-5): 1=easy, 5=complex. Estimate effort."
        },
        "IM": {
            "name": "Importance", 
            "weight": 4, 
            "desc": "(1-5): 1=low, 5=critical. Essential to core purpose."
        },
        "IP": {
            "name": "Impact", 
            "weight": 5, 
            "desc": "(1-5): 1=minimal, 5=high. Overall positive effect."
        },
        "ADV": {
            "name": "AI Data Value", 
            "weight": 4, 
            "desc": "(1-5): 1=none, 5=high. Usefulness for AI training."
        },
        "ADF": {
            "name": "AI Dev Feasibility", 
            "weight": 3, 
            "desc": "(1-5): 1=infeasible, 5=easy. AI assistance potential."
        },
        "DF": {
            "name": "Dependency Factor", 
            "weight": 5, 
            "desc": "(1-5): 1=none, 5=bottleneck. Others need this."
        },
        "RF": {
            "name": "Risk Factor", 
            "weight": 3, 
            "desc": "(1-5): 1=low, 5=high. Risk if delayed/skipped."
        }
    }
    
    def __init__(self):
        """Initialize the MPS Calculator."""
        logger.info("[U+1F9EE] MPS Calculator initialized")
    
    def calculate(self, scores: Dict[str, int]) -> float:
        """
        Calculate the Module Prioritization Score (MPS).
        
        Args:
            scores: Dictionary mapping factor keys to scores (1-5)
            
        Returns:
            float: Calculated MPS score
            
        Raises:
            ValueError: If scores are invalid or missing
        """
        if not self.validate_scores(scores):
            raise ValueError("Invalid scores provided to MPS calculation")
        
        try:
            mps = 0.0
            for factor_key, factor_info in self.FACTORS.items():
                score = scores[factor_key]
                weight = factor_info['weight']
                contribution = score * weight
                mps += contribution
                
                logger.debug(f"  {factor_key}: {score} × {weight} = {contribution}")
            
            logger.info(f"[DATA] MPS Calculated: {mps:.2f}")
            return mps
            
        except Exception as e:
            logger.error(f"[FAIL] Error calculating MPS: {e}")
            raise ValueError(f"MPS calculation failed: {e}")
    
    def validate_scores(self, scores: Dict[str, int]) -> bool:
        """
        Validate that all required scores are present and within range.
        
        Args:
            scores: Dictionary of factor scores to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        if not isinstance(scores, dict):
            logger.error("[FAIL] Scores must be a dictionary")
            return False
        
        # Check all required factors are present
        missing_factors = set(self.FACTORS.keys()) - set(scores.keys())
        if missing_factors:
            logger.error(f"[FAIL] Missing required factors: {missing_factors}")
            return False
        
        # Check all scores are in valid range (1-5)
        for factor_key, score in scores.items():
            if not isinstance(score, int) or not (1 <= score <= 5):
                logger.error(f"[FAIL] Invalid score for {factor_key}: {score} (must be 1-5)")
                return False
        
        logger.debug("[OK] All scores validated successfully")
        return True
    
    def get_factor_definitions(self) -> Dict[str, Dict[str, Any]]:
        """
        Get the complete factor definitions dictionary.
        
        Returns:
            Dict: Complete factor definitions with weights and descriptions
        """
        return self.FACTORS.copy()
    
    def get_factor_names(self) -> List[str]:
        """
        Get list of all factor keys.
        
        Returns:
            List[str]: List of factor keys (CX, IM, IP, etc.)
        """
        return list(self.FACTORS.keys())
    
    def calculate_multiple(self, modules: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Calculate MPS for multiple modules and sort by score.
        
        Args:
            modules: List of module dictionaries with 'name' and 'scores' keys
            
        Returns:
            List[Dict]: Modules with calculated MPS, sorted by score (highest first)
        """
        results = []
        
        for module in modules:
            if 'name' not in module or 'scores' not in module:
                logger.warning(f"[U+26A0]️ Skipping invalid module: {module}")
                continue
            
            try:
                mps = self.calculate(module['scores'])
                result = module.copy()
                result['mps'] = mps
                results.append(result)
                
                logger.info(f"[OK] {module['name']}: MPS = {mps:.2f}")
                
            except Exception as e:
                logger.error(f"[FAIL] Failed to calculate MPS for {module['name']}: {e}")
                continue
        
        # Sort by MPS (highest first)
        results.sort(key=lambda x: x['mps'], reverse=True)
        
        logger.info(f"[CLIPBOARD] Calculated MPS for {len(results)} modules")
        return results
    
    def get_top_priority(self, modules: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Get the highest priority module after MPS calculation.
        
        Args:
            modules: List of module dictionaries
            
        Returns:
            Dict or None: Highest priority module, or None if no valid modules
        """
        calculated = self.calculate_multiple(modules)
        
        if calculated:
            top_module = calculated[0]
            logger.info(f"[TARGET] Top Priority: {top_module['name']} (MPS: {top_module['mps']:.2f})")
            return top_module
        
        logger.warning("[U+26A0]️ No valid modules found for prioritization")
        return None
    
    def generate_summary_report(self, modules: List[Dict[str, Any]]) -> str:
        """
        Generate a formatted summary report of MPS calculations.
        
        Args:
            modules: List of modules with calculated MPS
            
        Returns:
            str: Formatted report text
        """
        calculated = self.calculate_multiple(modules)
        
        if not calculated:
            return "No modules available for reporting."
        
        lines = [
            "=" * 60,
            "MODULE PRIORITIZATION SCORE (MPS) REPORT",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "=" * 60,
            ""
        ]
        
        # Top priority highlight
        top = calculated[0]
        lines.extend([
            f"[TARGET] HIGHEST PRIORITY: {top['name']}",
            f"   MPS Score: {top['mps']:.2f}",
            ""
        ])
        
        # Full ranking table
        lines.extend([
            "FULL RANKING:",
            "-" * 40
        ])
        
        for i, module in enumerate(calculated, 1):
            lines.append(f"  {i:2d}. {module['name']:<25} {module['mps']:6.2f}")
        
        lines.extend([
            "",
            "=" * 60,
            "* Higher MPS indicates higher development priority",
            "* Use this ranking to guide development resource allocation"
        ])
        
        return "\n".join(lines)


# Convenience functions for backward compatibility
def calculate_mps(scores: Dict[str, int]) -> float:
    """
    Convenience function for direct MPS calculation.
    Maintains compatibility with existing tool interfaces.
    """
    calculator = MPSCalculator()
    return calculator.calculate(scores)


def get_factors() -> Dict[str, Dict[str, Any]]:
    """
    Convenience function to get factor definitions.
    Maintains compatibility with existing tool interfaces.
    """
    calculator = MPSCalculator()
    return calculator.get_factor_definitions()


# Example usage and testing
if __name__ == "__main__":
    # Example module data for testing
    test_modules = [
        {
            "name": "banter_engine",
            "scores": {"CX": 4, "IM": 5, "IP": 5, "ADV": 5, "ADF": 4, "DF": 5, "RF": 4}
        },
        {
            "name": "livechat",
            "scores": {"CX": 3, "IM": 5, "IP": 5, "ADV": 4, "ADF": 5, "DF": 4, "RF": 4}
        },
        {
            "name": "stream_resolver", 
            "scores": {"CX": 3, "IM": 4, "IP": 4, "ADV": 3, "ADF": 4, "DF": 3, "RF": 3}
        }
    ]
    
    print("[U+1F9EA] Testing MPS Calculator")
    print("=" * 40)
    
    calculator = MPSCalculator()
    
    # Test individual calculation
    print("\n1. Individual MPS Calculation:")
    test_scores = {"CX": 3, "IM": 5, "IP": 4, "ADV": 4, "ADF": 3, "DF": 4, "RF": 3}
    mps = calculator.calculate(test_scores)
    print(f"   Test Module MPS: {mps:.2f}")
    
    # Test multiple modules
    print("\n2. Multiple Module Prioritization:")
    results = calculator.calculate_multiple(test_modules)
    for i, module in enumerate(results, 1):
        print(f"   {i}. {module['name']}: {module['mps']:.2f}")
    
    # Test top priority
    print("\n3. Top Priority Selection:")
    top = calculator.get_top_priority(test_modules)
    if top:
        print(f"   Top Priority: {top['name']} (MPS: {top['mps']:.2f})")
    
    # Test summary report
    print("\n4. Summary Report:")
    report = calculator.generate_summary_report(test_modules)
    print(report)
    
    print("\n[OK] All tests completed successfully!") 