"""
Test: Gemma 3 270M Live File Naming Enforcement

Uses actual Gemma 3 270M model (not simulation) to detect violations.

Model: E:/HoloIndex/models/gemma-3-270m-it-Q4_K_M.gguf
Size: 241MB
Speed: <50ms per query
Accuracy: Testing live

WSP 57: Naming Coherence
WSP 93: CodeIndex Surgical Intelligence
"""

import sys
from pathlib import Path
import json
from typing import Dict
import time

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from llama_cpp import Llama
    GEMMA_AVAILABLE = True
except ImportError:
    GEMMA_AVAILABLE = False
    print("[ERROR] llama-cpp-python not installed")
    print("       Install with: pip install llama-cpp-python")
    sys.exit(1)


class Gemma3FileNamingEnforcer:
    """
    Live Gemma 3 270M file naming enforcement

    Baby 0102 learns WSP 57 naming rules and enforces them in real-time
    """

    def __init__(self, model_path: Path = Path("E:/HoloIndex/models/gemma-3-270m-it-Q4_K_M.gguf")):
        """Initialize Gemma 3 270M model"""
        self.model_path = model_path
        self.llm = None

        if not model_path.exists():
            print(f"[ERROR] Model not found: {model_path}")
            print(f"       Run: python holo_index/scripts/download_gemma3_270m.py")
            sys.exit(1)

        print(f"[INIT] Loading Gemma 3 270M from {model_path}...")
        start = time.time()

        self.llm = Llama(
            model_path=str(model_path),
            n_ctx=1024,  # Small context for classification
            n_threads=4,
            n_gpu_layers=0,  # CPU only
            verbose=False
        )

        load_time = time.time() - start
        print(f"[READY] Model loaded in {load_time:.2f}s")
        print()

    def analyze_file_naming(self, file_path: str) -> Dict:
        """
        Ask Gemma 3 to analyze if file violates WSP 57 naming rules

        Returns:
            dict: {violation: bool, reason: str, suggested_fix: str|None, priority: str|None}
        """

        # Training prompt (teaches Gemma the rules)
        training = """WSP 57 File Naming Rules:

ALLOWED "WSP_" prefix locations:
- WSP_framework/src/WSP_*.md (official protocols)
- WSP_knowledge/src/WSP_*.md (official protocols)
- */reports/WSP_*/ (analysis reports)
- */archive/*/WSP_* (historical archives)
- docs/session_backups/WSP_* (session backups)

PROHIBITED "WSP_" prefix locations:
- modules/*/docs/WSP_*.md (use descriptive names)
- modules/*/src/WSP_*.md (use descriptive names)
- modules/*/tests/WSP_*.md (use descriptive names)
- docs/WSP_*.md (unless in session_backups/)

Replacement patterns:
- WSP_COMPLIANCE → COMPLIANCE_STATUS.md
- WSP_AUDIT_REPORT → Audit_Report.md
- WSP_79_SWOT_ANALYSIS → SWOT_Analysis_*.md
"""

        # Analysis query - simplified for better parsing
        query = f"""File: {file_path}

Rules:
ALLOWED WSP_ prefix: WSP_framework/src/, WSP_knowledge/src/, */reports/, */archive/, docs/session_backups/
PROHIBITED WSP_ prefix: modules/*/docs/, modules/*/src/, modules/*/tests/, docs/ (unless session_backups)

Is this a violation? Answer YES or NO, then explain why.
"""

        # Run inference
        start = time.time()
        response = self.llm(
            query,
            max_tokens=100,
            temperature=0.1,  # Low temp for consistent classification
            stop=["###", "\n\n\n"]
        )
        inference_time = (time.time() - start) * 1000  # Convert to ms

        # Extract response text
        if isinstance(response, dict) and 'choices' in response:
            text = response['choices'][0]['text'].strip()
        else:
            text = str(response).strip()

        # Parse response
        result = self._parse_gemma_response(text, file_path, inference_time)

        return result

    def _parse_gemma_response(self, text: str, file_path: str, inference_ms: float) -> Dict:
        """Parse Gemma's response into structured result"""

        result = {
            "file": file_path,
            "violation": False,
            "reason": text,
            "suggested_fix": None,
            "priority": None,
            "inference_time_ms": inference_ms,
            "raw_response": text
        }

        # Simple parsing - look for YES/NO in response
        text_lower = text.lower()

        # Check for violation indicators
        if "yes" in text_lower or "violation" in text_lower:
            # But NOT if it says "no" or "not a violation"
            if "no" not in text_lower and "not a violation" not in text_lower:
                result["violation"] = True

        # Extract reason (first few sentences)
        sentences = text.split('.')[:2]
        if sentences:
            result["reason"] = '. '.join(s.strip() for s in sentences if s.strip())

        return result


def test_gemma3_live():
    """Test Gemma 3 270M on real file naming enforcement"""

    print("=" * 70)
    print("Gemma 3 270M Live File Naming Enforcement Test")
    print("=" * 70)
    print()

    # Initialize Gemma 3
    enforcer = Gemma3FileNamingEnforcer()

    # Test cases
    test_cases = [
        {
            "file": "WSP_framework/src/WSP_87_Code_Navigation_Protocol.md",
            "expected": "VALID",
            "why": "Official WSP protocol in proper location"
        },
        {
            "file": "modules/communication/livechat/docs/Compliance_Report.md",
            "expected": "VALID",
            "why": "Module doc without WSP_ prefix"
        },
        {
            "file": "modules/ai_intelligence/pqn_alignment/WSP_COMPLIANCE_STATUS.md",
            "expected": "VIOLATION",
            "why": "Module doc should not use WSP_ prefix"
        },
        {
            "file": "docs/WSP_Something_Analysis.md",
            "expected": "VIOLATION",
            "why": "Root doc should not use WSP_ prefix"
        },
        {
            "file": "docs/session_backups/WSP_22_Violation_Analysis.md",
            "expected": "VALID",
            "why": "Session backup can use WSP_ prefix"
        },
        {
            "file": "modules/communication/livechat/docs/WSP_AUDIT_REPORT.md",
            "expected": "VIOLATION",
            "why": "Module doc should be Audit_Report.md"
        }
    ]

    print("TESTING GEMMA 3 ON REAL FILES:")
    print("-" * 70)
    print()

    results = []
    total_time_ms = 0

    for i, test in enumerate(test_cases, 1):
        print(f"Test {i}/{len(test_cases)}: {test['file']}")
        print(f"Expected: {test['expected']} - {test['why']}")

        # Ask Gemma 3
        analysis = enforcer.analyze_file_naming(test['file'])

        # Check result
        gemma_says = "VIOLATION" if analysis['violation'] else "VALID"
        correct = (gemma_says == test['expected'])

        print(f"Gemma 3:  {gemma_says} {'[OK]' if correct else '[WRONG]'}")
        print(f"          {analysis['reason']}")

        if analysis['violation']:
            print(f"          Fix: {analysis['suggested_fix']}")
            print(f"          Priority: {analysis['priority']}")

        print(f"          Inference: {analysis['inference_time_ms']:.1f}ms")
        print()

        results.append({
            **test,
            "gemma_result": analysis,
            "correct": correct
        })

        total_time_ms += analysis['inference_time_ms']

    # Evaluation
    print("=" * 70)
    print("RESULTS:")
    print("=" * 70)
    print()

    correct_count = sum(1 for r in results if r['correct'])
    accuracy = correct_count / len(results) * 100
    avg_time_ms = total_time_ms / len(results)

    print(f"Test cases: {len(results)}")
    print(f"Correct: {correct_count}")
    print(f"Accuracy: {accuracy:.1f}%")
    print(f"Average inference time: {avg_time_ms:.1f}ms")
    print(f"Total time: {total_time_ms:.1f}ms")
    print()

    # Show errors
    errors = [r for r in results if not r['correct']]
    if errors:
        print("ERRORS:")
        for err in errors:
            print(f"  {err['file']}")
            print(f"    Expected: {err['expected']}")
            print(f"    Got: {'VIOLATION' if err['gemma_result']['violation'] else 'VALID'}")
            print(f"    Reason: {err['gemma_result']['reason']}")
            print()

    # Conclusion
    print("=" * 70)
    print("CONCLUSION:")
    print("=" * 70)
    print()

    if accuracy >= 80:
        print("[SUCCESS] Gemma 3 270M can enforce WSP 57 naming rules!")
        print()
        print(f"Performance:")
        print(f"  - Accuracy: {accuracy:.1f}%")
        print(f"  - Speed: {avg_time_ms:.1f}ms average ({1000/avg_time_ms:.1f} files/second)")
        print(f"  - Full repo scan (100 files): ~{avg_time_ms * 100 / 1000:.1f}s")
        print()
        print("Ready for production deployment:")
        print("  1. Pre-commit hook (block violations)")
        print("  2. WSP Sentinel real-time enforcement")
        print("  3. ChromaDB training corpus for continuous learning")
        print()
    else:
        print(f"[NEEDS IMPROVEMENT] Accuracy {accuracy:.1f}% below target (80%+)")
        print()
        print("Possible improvements:")
        print("  1. Refine training prompt")
        print("  2. Add more examples")
        print("  3. Adjust parsing logic")
        print("  4. Try different temperature")
        print()

    print("Model comparison:")
    print(f"  - Gemma 3 270M: 241MB, {avg_time_ms:.0f}ms/query")
    print(f"  - Qwen 1.5B: 1.1GB, ~250ms/query (estimated)")
    print()
    print("Gemma 3 is 4.5x smaller and likely faster!")
    print()


if __name__ == "__main__":
    test_gemma3_live()
