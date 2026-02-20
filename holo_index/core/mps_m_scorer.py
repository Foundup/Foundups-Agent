#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MPS-M Scorer for HoloIndex Output Quality Rating

Applies WSP 15 Section 6 Memory Prioritization Scoring to HoloIndex results.
Enables recursive improvement by rating output quality.

WSP Compliance: WSP 15 (MPS System), WSP 60 (Memory Prioritization)
"""

from typing import Dict, List, Any
from dataclasses import dataclass
from enum import Enum


class MemoryPriority(Enum):
    """Priority levels based on MPS-M score."""
    P0_CRITICAL = "P0"   # 16-20
    P1_HIGH = "P1"       # 13-15
    P2_MEDIUM = "P2"     # 10-12
    P3_LOW = "P3"        # 7-9
    P4_BACKLOG = "P4"    # 4-6


# Trust weights per WSP 15 Section 6.2
TRUST_WEIGHTS = {
    "wsp_protocol": 1.0,
    "interface": 0.9,
    "readme": 0.9,
    "modlog": 0.7,
    "testmodlog": 0.7,
    "roadmap": 0.8,
    "generated": 0.5,
    "code": 0.8,
    "skill": 0.85,
    "vocabulary": 0.6,
}


@dataclass
class MpsScore:
    """MPS-M score for a memory card."""
    reconstruction_cost: int   # 1-5: How hard to re-derive
    correctness_impact: int    # 1-5: Consequence if missing
    time_sensitivity: int      # 1-5: Staleness risk
    decision_leverage: int     # 1-5: How useful for next action
    
    @property
    def total(self) -> int:
        return (self.reconstruction_cost + self.correctness_impact + 
                self.time_sensitivity + self.decision_leverage)
    
    @property
    def priority(self) -> MemoryPriority:
        """Map total score to priority level."""
        if self.total >= 16:
            return MemoryPriority.P0_CRITICAL
        elif self.total >= 13:
            return MemoryPriority.P1_HIGH
        elif self.total >= 10:
            return MemoryPriority.P2_MEDIUM
        elif self.total >= 7:
            return MemoryPriority.P3_LOW
        else:
            return MemoryPriority.P4_BACKLOG


class MpsMScorer:
    """
    Scores HoloIndex results using MPS-M methodology.
    
    Enables quality rating for recursive improvement.
    """
    
    def __init__(self):
        """Initialize scorer with default rules."""
        self.doc_type_scores = self._define_default_scores()
    
    def _define_default_scores(self) -> Dict[str, MpsScore]:
        """Define default MPS-M scores by document type."""
        return {
            "wsp_protocol": MpsScore(4, 5, 3, 5),  # Hard to rebuild, critical
            "interface": MpsScore(3, 5, 4, 4),    # API contract, important
            "readme": MpsScore(2, 4, 3, 4),       # Module entry, helpful
            "modlog": MpsScore(1, 3, 5, 3),       # Easy rebuild, time-sensitive
            "roadmap": MpsScore(3, 3, 4, 4),      # Planning docs
            "code": MpsScore(4, 4, 2, 4),         # Implementation, stable
            "skill": MpsScore(3, 4, 2, 5),        # Agent capabilities
            "vocabulary": MpsScore(2, 3, 3, 3),   # STT corrections
        }
    
    def score_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Score a single HoloIndex result.
        
        Args:
            result: HoloIndex search result dict
            
        Returns:
            Result with mps_m scoring added
        """
        # Detect document type
        doc_type = self._detect_doc_type(result)
        
        # Get base score
        base_score = self.doc_type_scores.get(doc_type, MpsScore(2, 2, 2, 2))
        
        # Get trust weight
        trust = TRUST_WEIGHTS.get(doc_type, 0.5)
        
        # Calculate effective score
        effective = base_score.total * trust
        
        result["mps_m"] = {
            "doc_type": doc_type,
            "reconstruction_cost": base_score.reconstruction_cost,
            "correctness_impact": base_score.correctness_impact,
            "time_sensitivity": base_score.time_sensitivity,
            "decision_leverage": base_score.decision_leverage,
            "total": base_score.total,
            "trust_weight": trust,
            "effective_score": round(effective, 2),
            "priority": base_score.priority.value,
        }
        
        return result
    
    def _detect_doc_type(self, result: Dict[str, Any]) -> str:
        """Detect document type from result metadata."""
        # Check explicit type field
        if "type" in result:
            type_val = result["type"].lower()
            if "wsp" in type_val:
                return "wsp_protocol"
            if type_val in TRUST_WEIGHTS:
                return type_val
        
        # Infer from path
        path = result.get("location", result.get("path", "")).lower()
        
        if "wsp_" in path or "wsp-" in path:
            return "wsp_protocol"
        if "interface.md" in path:
            return "interface"
        if "readme.md" in path:
            return "readme"
        if "modlog.md" in path:
            return "modlog"
        if "roadmap.md" in path:
            return "roadmap"
        if "skill" in path:
            return "skill"
        if "vocabulary" in path:
            return "vocabulary"
        if path.endswith(".py"):
            return "code"
        
        return "generated"
    
    def score_bundle(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Score entire HoloIndex bundle and add quality_metrics.
        
        Args:
            results: Full HoloIndex search results
            
        Returns:
            Results with quality_metrics added
        """
        all_scores = []
        
        # Score code hits
        for hit in results.get("code", []):
            self.score_result(hit)
            if "mps_m" in hit:
                all_scores.append(hit["mps_m"]["effective_score"])
        
        # Score WSP hits
        for hit in results.get("wsps", []):
            self.score_result(hit)
            if "mps_m" in hit:
                all_scores.append(hit["mps_m"]["effective_score"])
        
        # Score skill hits
        for hit in results.get("skills", []):
            self.score_result(hit)
            if "mps_m" in hit:
                all_scores.append(hit["mps_m"]["effective_score"])
        
        # Calculate aggregate metrics
        total_mps_m = sum(all_scores)
        avg_score = total_mps_m / len(all_scores) if all_scores else 0
        
        # Determine overall priority
        if avg_score >= 16:
            priority = "P0"
        elif avg_score >= 13:
            priority = "P1"
        elif avg_score >= 10:
            priority = "P2"
        elif avg_score >= 7:
            priority = "P3"
        else:
            priority = "P4"
        
        results["quality_metrics"] = {
            "total_mps_m": round(total_mps_m, 2),
            "avg_score": round(avg_score, 2),
            "result_count": len(all_scores),
            "priority": priority,
            "scoring_method": "WSP 15 Section 6 MPS-M",
        }
        
        return results


def score_holo_output(results: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convenience function to score HoloIndex output.
    
    Usage:
        from holo_index.core.mps_m_scorer import score_holo_output
        scored = score_holo_output(holo.search("query"))
    """
    scorer = MpsMScorer()
    return scorer.score_bundle(results)


if __name__ == "__main__":
    # Test the scorer
    test_results = {
        "code": [
            {"location": "modules/communication/livechat/src/auto_moderator_dae.py", "type": "code"},
            {"location": "modules/ai_intelligence/ai_overseer/INTERFACE.md", "type": "interface"},
        ],
        "wsps": [
            {"path": "WSP_framework/src/WSP_15_Module_Prioritization.md", "type": "wsp"},
        ],
    }
    
    scorer = MpsMScorer()
    scored = scorer.score_bundle(test_results)
    
    print("MPS-M Scoring Test:")
    print(f"Quality Metrics: {scored['quality_metrics']}")
    for hit in scored.get("code", []):
        print(f"  {hit.get('location', 'unknown')}: {hit.get('mps_m', {})}")
