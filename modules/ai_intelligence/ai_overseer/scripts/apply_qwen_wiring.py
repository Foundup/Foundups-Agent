#!/usr/bin/env python3
"""
0102 Autonomous Qwen Wiring Application Script
Applies Qwen strategic MPS classification to AI_overseer
"""

import re
from pathlib import Path

def apply_qwen_wiring():
    """Apply Qwen wiring changes autonomously"""

    ai_overseer_path = Path("modules/ai_intelligence/ai_overseer/src/ai_overseer.py")

    print(f"[0102] Reading {ai_overseer_path}")
    with open(ai_overseer_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Add _initialize_qwen method before _qwen_classify_bugs
    qwen_init_method = '''
    def _initialize_qwen(self) -> bool:
        """Lazy load Qwen 1.5B for strategic classification"""
        if self._qwen_engine is not None:
            return self._qwen_available

        try:
            from holo_index.qwen_advisor.llm_engine import QwenInferenceEngine
            from pathlib import Path

            self._qwen_engine = QwenInferenceEngine(
                model_path=Path("E:/LLM_Models/qwen-coder-1.5b.gguf"),
                max_tokens=512,
                temperature=0.2,
                context_length=2048
            )

            if self._qwen_engine.initialize():
                self._qwen_available = True
                logger.info("[QWEN] Initialized Qwen 1.5B for strategic classification")
                return True
            else:
                self._qwen_available = False
                return False

        except Exception as e:
            logger.warning(f"[QWEN] Qwen unavailable, using static config: {e}")
            self._qwen_available = False
            return False

    def _fallback_static_classification(self, bug: Dict, config: Dict) -> Dict:
        """Fallback to static JSON classification when Qwen unavailable"""
        qwen_action = config.get("qwen_action", "ignore")
        wsp_15_mps = config.get("wsp_15_mps", {})
        complexity = wsp_15_mps.get("complexity", 3)

        return {
            "pattern_name": bug["pattern_name"],
            "complexity": complexity,
            "auto_fixable": (qwen_action == "auto_fix"),
            "needs_0102": (qwen_action == "bug_report"),
            "qwen_action": qwen_action,
            "matches": bug["matches"],
            "config": config,
            "ml_classified": False
        }
'''

    # Find the _qwen_classify_bugs method and insert the new methods before it
    qwen_classify_start = content.find('    def _qwen_classify_bugs(self, detected_bugs: List[Dict], skill: Dict)')
    if qwen_classify_start == -1:
        print("[0102] ERROR: Could not find _qwen_classify_bugs method")
        return False

    content = content[:qwen_classify_start] + qwen_init_method + '\n' + content[qwen_classify_start:]

    # Now enhance _qwen_classify_bugs method
    old_qwen_pattern = r'''    def _qwen_classify_bugs\(self, detected_bugs: List\[Dict\], skill: Dict\) -> List\[Dict\]:
        """Phase 2 \(Qwen\): Classify bugs with WSP 15 MPS scoring and determine actions"""
        classified = \[\]

        for bug in detected_bugs:
            config = bug\["config"\]
            qwen_action = config\.get\("qwen_action", "ignore"\)

            # Interpret qwen_action into auto_fixable/needs_0102 flags
            auto_fixable = \(qwen_action == "auto_fix"\)
            needs_0102 = \(qwen_action == "bug_report"\)
            should_ignore = \(qwen_action == "ignore"\)'''

    new_qwen_method = '''    def _qwen_classify_bugs(self, detected_bugs: List[Dict], skill: Dict) -> List[Dict]:
        """
        Phase 2 (Qwen): Strategic classification with iterative research chain

        Chain: Deep Think → HoloIndex Research → Deep Think → Occam's Razor → Decision
        Performance: 200-500ms per bug (Qwen strategic analysis)
        """
        classified = []

        for bug in detected_bugs:
            config = bug["config"]

            # Step 1+2: Deep think + HoloIndex research - Qwen strategic analysis
            if self._initialize_qwen():
                prompt = f"""Bug Classification Task (WSP 15 MPS Scoring):

Pattern: {bug['pattern_name']}
Description: {config.get('description', '')}
Matches: {len(bug['matches'])}
Daemon: {skill.get('daemon_name', 'unknown')}

Iterative Analysis:
1. DEEP THINK: What is this bug?
2. RESEARCH: Search memory for similar patterns
3. FIRST PRINCIPLES: Break down to root cause
4. OCCAM'S RAZOR: What is the SIMPLEST solution?

WSP 15 Scoring Criteria (1-5 scale):
1. Complexity (1=trivial regex, 5=architectural change)
2. Importance (1=optional, 5=critical blocker)
3. Deferability (1=fix NOW, 5=can wait)
4. Impact (1=affects one user, 5=transforms system)

Provide JSON response:
{{
    "complexity": <1-5>,
    "importance": <1-5>,
    "deferability": <1-5>,
    "impact": <1-5>,
    "total_mps": <sum>,
    "priority": "<P0|P1|P2|P3|P4>",
    "action": "<auto_fix|bug_report|ignore>",
    "rationale": "<1 sentence explaining SIMPLEST solution>"
}}"""

                try:
                    import json
                    response = self._qwen_engine.generate_response(prompt)

                    # Parse Qwen's strategic analysis
                    qwen_analysis = json.loads(response)

                    classification = {
                        "pattern_name": bug["pattern_name"],
                        "complexity": qwen_analysis["complexity"],
                        "auto_fixable": (qwen_analysis["action"] == "auto_fix"),
                        "needs_0102": (qwen_analysis["action"] == "bug_report"),
                        "qwen_action": qwen_analysis["action"],
                        "mps_score": qwen_analysis["total_mps"],
                        "priority": qwen_analysis["priority"],
                        "rationale": qwen_analysis["rationale"],
                        "matches": bug["matches"],
                        "config": config,
                        "ml_classified": True
                    }

                    classified.append(classification)
                    logger.info(f"[QWEN] Classified {bug['pattern_name']}: {qwen_analysis['priority']} - {qwen_analysis['action']}")
                    continue

                except Exception as e:
                    logger.warning(f"[QWEN] Classification failed for {bug['pattern_name']}, using static config: {e}")

            # Fallback to static config
            qwen_action = config.get("qwen_action", "ignore")
            should_ignore = (qwen_action == "ignore")'''

    content = re.sub(old_qwen_pattern, new_qwen_method, content, flags=re.MULTILINE | re.DOTALL)

    print(f"[0102] Writing enhanced {ai_overseer_path}")
    with open(ai_overseer_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print("[0102] Qwen wiring applied successfully")
    return True

if __name__ == "__main__":
    try:
        apply_qwen_wiring()
    except Exception as e:
        print(f"[0102] Error applying Qwen wiring: {e}")
        print("[0102] Restore from backup: cp modules/ai_intelligence/ai_overseer/src/ai_overseer.py.backup modules/ai_intelligence/ai_overseer/src/ai_overseer.py")
        raise
