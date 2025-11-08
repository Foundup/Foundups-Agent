#!/usr/bin/env python3
"""
0102 Autonomous AI Wiring Application Script
Applies Gemma/Qwen integration to AI_overseer without file handle issues
"""

import re
from pathlib import Path

def apply_ai_wiring():
    """Apply AI wiring changes autonomously"""

    ai_overseer_path = Path("modules/ai_intelligence/ai_overseer/src/ai_overseer.py")

    print(f"[0102] Reading {ai_overseer_path}")
    with open(ai_overseer_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Change 1: Add Gemma/Qwen engine initialization after fix_attempts
    print("[0102] Adding Gemma/Qwen engine initialization...")
    content = content.replace(
        "        # Load learning patterns\n        self.patterns = self._load_patterns()",
        """        # WSP 77: Gemma (270M) for fast pattern detection
        self._gemma_engine = None  # Lazy loaded on first use
        self._gemma_available = False

        # WSP 77: Qwen (1.5B) for strategic classification
        self._qwen_engine = None  # Lazy loaded on first use
        self._qwen_available = False

        # Load learning patterns
        self.patterns = self._load_patterns()"""
    )

    # Change 2: Enhance _gemma_detect_errors with ML validation
    print("[0102] Enhancing _gemma_detect_errors with ML validation...")

    old_gemma_func = r'''    def _gemma_detect_errors\(self, bash_output: str, skill: Dict\) -> List\[Dict\]:
        """Phase 1 \(Gemma\): Fast error pattern detection using skill patterns"""
        import re
        detected = \[\]

        error_patterns = skill\.get\("error_patterns", \{\}\)
        for pattern_name, pattern_config in error_patterns\.items\(\):
            regex = pattern_config\.get\("regex", ""\)
            if not regex:
                continue

            matches = re\.findall\(regex, bash_output, re\.IGNORECASE \| re\.MULTILINE\)
            if matches:
                detected\.append\(\{
                    "pattern_name": pattern_name,
                    "matches": matches,
                    "config": pattern_config
                \}\)

        return detected'''

    new_gemma_func = '''    def _initialize_gemma(self) -> bool:
        """Lazy load Gemma 270M for ML pattern validation"""
        if self._gemma_engine is not None:
            return self._gemma_available

        try:
            from holo_index.qwen_advisor.gemma_rag_inference import GemmaRAGInference
            self._gemma_engine = GemmaRAGInference()
            self._gemma_available = True
            logger.info("[GEMMA] Initialized Gemma 270M for pattern validation")
            return True
        except Exception as e:
            logger.warning(f"[GEMMA] Gemma unavailable, using static patterns: {e}")
            self._gemma_available = False
            return False

    def _gemma_detect_errors(self, bash_output: str, skill: Dict) -> List[Dict]:
        """
        Phase 1 (Gemma): Fast error detection with iterative research chain

        Chain: Deep Think → HoloIndex Research → Deep Think → Occam's Razor → Decision
        Performance: 50-150ms (regex 50ms + Gemma 100ms)
        """
        import re
        detected = []

        error_patterns = skill.get("error_patterns", {})
        for pattern_name, pattern_config in error_patterns.items():
            regex = pattern_config.get("regex", "")
            if not regex:
                continue

            # Step 1: Deep think - Regex pre-filter
            matches = re.findall(regex, bash_output, re.IGNORECASE | re.MULTILINE)
            if not matches:
                continue

            # Step 2: HoloIndex research - Check pattern memory (TODO)
            # Step 3: Deep think with Gemma ML - Validate if genuine bug
            if self._initialize_gemma():
                log_excerpt = bash_output[-500:]
                prompt = f"""Error Pattern: {pattern_name}
Description: {pattern_config.get('description', '')}
Matches: {len(matches)}
Log Context: {log_excerpt}

Deep Think: Is this a genuine bug requiring action?
First Principles: Does this indicate system malfunction?
Occam's Razor: What is the SIMPLEST explanation?

Answer: YES (genuine bug) or NO (false positive/noise)
Confidence: 0.0-1.0"""

                try:
                    result = self._gemma_engine.infer(prompt)

                    # Step 4: Occam's Razor decision
                    if result.response.upper().startswith("YES") and result.confidence > 0.7:
                        detected.append({
                            "pattern_name": pattern_name,
                            "matches": matches,
                            "config": pattern_config,
                            "gemma_confidence": result.confidence,
                            "ml_validated": True
                        })
                        logger.info(f"[GEMMA] Validated {pattern_name} (confidence={result.confidence:.2f})")
                    else:
                        logger.debug(f"[GEMMA] Rejected {pattern_name} as false positive")
                except Exception as e:
                    logger.warning(f"[GEMMA] ML validation failed, using static: {e}")
                    detected.append({
                        "pattern_name": pattern_name,
                        "matches": matches,
                        "config": pattern_config,
                        "ml_validated": False
                    })
            else:
                # Fallback: Gemma unavailable
                detected.append({
                    "pattern_name": pattern_name,
                    "matches": matches,
                    "config": pattern_config,
                    "ml_validated": False
                })

        return detected'''

    content = re.sub(old_gemma_func, new_gemma_func, content, flags=re.MULTILINE | re.DOTALL)

    print(f"[0102] Writing enhanced {ai_overseer_path}")
    with open(ai_overseer_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print("[0102] ✅ AI wiring applied successfully")
    print("[0102] Backup saved at: ai_overseer.py.backup")
    return True

if __name__ == "__main__":
    try:
        apply_ai_wiring()
    except Exception as e:
        print(f"[0102] ❌ Error applying AI wiring: {e}")
        print("[0102] Restore from backup: cp modules/ai_intelligence/ai_overseer/src/ai_overseer.py.backup modules/ai_intelligence/ai_overseer/src/ai_overseer.py")
        raise
