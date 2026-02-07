# -*- coding: utf-8 -*-
"""
AutoGate Component for AI Overseer
==================================

Implements "Smart Auto-Gating" (Passive Resistance).
Intercepts mission plans and validates them against HoloIndex documentation using Qwen.

Role: "The Compliance Officer"
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
import logging
import json
from pathlib import Path
import time

# Core Interfaces
from .holo_adapter import HoloAdapter
from holo_index.qwen_advisor.config import QwenAdvisorConfig

try:
    from holo_index.qwen_advisor.llm_engine import QwenInferenceEngine
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False

logger = logging.getLogger(__name__)

@dataclass
class GateVerdict:
    status: str  # PASS, WARN, BLOCK
    warnings: List[str]
    citations: List[str]
    confidence: float

class AutoGate:
    def __init__(self, repo_root: Path, holo_adapter: HoloAdapter):
        self.repo_root = repo_root
        self.holo_adapter = holo_adapter
        
        # Initialize Qwen for semantic validation
        self.llm = None
        if LLM_AVAILABLE:
            try:
                config = QwenAdvisorConfig.from_env()
                self.llm = QwenInferenceEngine(
                    model_path=config.model_path,
                    max_tokens=config.max_tokens,
                    temperature=config.temperature,
                )
                logger.info("[AUTO-GATE] Qwen Inference Engine initialized")
            except Exception as e:
                logger.warning(f"[AUTO-GATE] Failed to init Qwen: {e}")

    def validate_plan(self, plan: Any) -> GateVerdict:
        """
        Validate a Qwen-generated coordination plan against HoloIndex docs.
        
        Args:
            plan: CoordinationPlan object (duck-typed)
            
        Returns:
            GateVerdict
        """
        start_time = time.time()
        logger.info(f"[AUTO-GATE] Validating plan: {plan.mission_type.value}")
        
        # 1. Extract Keywords for Search
        # We want to find "Laws" relevant to this mission
        keywords = self._extract_keywords(plan)
        query = f"protocol strategy rules for {' '.join(keywords)}"
        
        # 2. Retrieve Ground Truth (HoloIndex)
        # Search for docs (WSPs, Strategies)
        search_results = self.holo_adapter.search(query, limit=3, doc_type_filter="wsp")
        
        docs = []
        citations = []
        if search_results and "wsps" in search_results:
            for hit in search_results["wsps"]:
                title = hit.get("title", "Unknown Doc")
                summary = hit.get("summary", "")
                docs.append(f"Document: {title}\nSummary: {summary}")
                citations.append(title)

        # 3. Analyze Compliance (Qwen)
        # If no docs found, we can't strict check
        if not docs:
            return GateVerdict(
                status="PASS", 
                warnings=["[GATE] No specific protocols found for this mission type."],
                citations=[],
                confidence=0.5
            )

        # Prompt Qwen
        verdict = self._consult_compliance_oracle(plan, docs)
        
        duration = (time.time() - start_time) * 1000
        logger.info(f"[AUTO-GATE] Validation complete ({duration:.0f}ms): {verdict.status}")
        
        return verdict

    def _extract_keywords(self, plan: Any) -> List[str]:
        """Extract search keywords from plan."""
        keywords = set()
        # Mission type
        if hasattr(plan, 'mission_type'):
            keywords.add(str(plan.mission_type.name))
            keywords.add(str(plan.mission_type.value))
            
        # Phase descriptions
        if hasattr(plan, 'phases'):
            for phase in plan.phases[:2]: # Check first 2 phases
                desc = phase.get('description', '').lower()
                if 'reply' in desc: keywords.add('reply engagement')
                if 'comment' in desc: keywords.add('commenting')
                if 'deploy' in desc: keywords.add('deployment')
                if 'test' in desc: keywords.add('testing')
        
        return list(keywords)

    def _consult_compliance_oracle(self, plan: Any, docs: List[str]) -> GateVerdict:
        """Ask Qwen if the plan violates the docs."""
        if not self.llm:
            return GateVerdict("PASS", ["[GATE] LLM unavailable for check"], [], 0.0)

        # Construct Prompt
        plan_summary = f"Mission: {plan.mission_type.value}\n"
        for p in getattr(plan, 'phases', []):
            plan_summary += f"- Phase {p.get('phase')}: {p.get('description')}\n"

        docs_text = "\n\n".join(docs)
        
        prompt = f"""
You are the Compliance Officer (AutoGate). 
Verify if the Proposed Plan violates the Reference Protocols.

Reference Protocols (The Law):
{docs_text}

Proposed Plan:
{plan_summary}

Task:
Identify major violations (e.g., "Reply 100%" when protocol says "50%").
If VIOLATION found, return status BLOCK or WARN.
If Safe, return PASS.

Format:
STATUS: [PASS/WARN/BLOCK]
REASON: [Brief explanation]
"""
        
        try:
            response = self.llm.generate(prompt, max_tokens=100)
            
            # Simple parsing
            status = "PASS"
            warnings = []
            
            if "STATUS: BLOCK" in response:
                status = "BLOCK"
            elif "STATUS: WARN" in response:
                status = "WARN"
            elif "VIOLATION" in response:
                status = "WARN"

            # Extract reason
            lines = response.split('\n')
            for line in lines:
                if line.startswith("REASON:"):
                    warnings.append(line.replace("REASON:", "").strip())
            
            return GateVerdict(
                status=status,
                warnings=warnings,
                citations=[d.split('\n')[0] for d in docs], # Crude citation extraction
                confidence=0.9
            )

        except Exception as e:
            logger.error(f"[AUTO-GATE] Qwen check failed: {e}")
            return GateVerdict("PASS", ["[GATE] Validation error"], [], 0.0)
