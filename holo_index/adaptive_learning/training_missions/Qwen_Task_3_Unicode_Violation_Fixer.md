# Qwen Task 3: Add Unicode Violation Fixer to Orchestrator

## Single Task Focus
Add autonomous Unicode violation detection and fixing to Qwen orchestrator

## Problem Context
Windows console (cp932) cannot encode emoji characters, causing:
```
UnicodeEncodeError: 'cp932' codec can't encode character '\u2705'
```

This is **pattern recognition** - perfect for Gemma + Qwen coordination.

## Execute These Steps (Validate After Each)

### Step 1: Create Gemma Pattern File
**File**: `holo_index/qwen_advisor/patterns/unicode_violations.json`
**Location**: New file

**Create**:
```json
{
  "emoji_replacements": {
    "[OK]": "[OK]",
    "[FAIL]": "[FAIL]",
    "[U+26A0]️": "[WARN]",
    "[REFRESH]": "[REFRESH]",
    "[PILL]": "[HEALTH]",
    "[AI]": "[BRAIN]",
    "[RULER]": "[SIZE]",
    "[BOX]": "[MODULE]",
    "[GHOST]": "[ORPHAN]",
    "[BOOKS]": "[DOCS]",
    "[TOOL]": "[FIX]",
    "[TARGET]": "[TARGET]",
    "[U+1F525]": "[HOT]",
    "⏭️": "[SKIP]",
    "[BOT]": "[BOT]",
    "[AI]": "[THINK]",
    "[BREAD]": "[BREADCRUMB]",
    "[NOTE]": "[COMPOSE]",
    "[DATA]": "[LEARN]",
    "[LINK]": "[LINK]",
    "🩺": "[CODEINDEX]",
    "[SEARCH]": "[SEARCH]",
    "[HANDSHAKE]": "[COLLAB]"
  },
  "violation_patterns": [
    "print\\([\"'][^\"']*[[OK][FAIL][U+26A0]️[REFRESH][PILL][AI][RULER][BOX][GHOST][BOOKS][TOOL][TARGET][U+1F525]⏭️[BOT][BREAD][NOTE][DATA][LINK]🩺[SEARCH][HANDSHAKE]]",
    "logger\\.(info|debug|error|warning)\\([\"'][^\"']*[[OK][FAIL][U+26A0]️[REFRESH][PILL][AI][RULER][BOX][GHOST][BOOKS][TOOL][TARGET][U+1F525]]",
    "return [\"'][^\"']*[[OK][FAIL][U+26A0]️[REFRESH][PILL][AI][RULER][BOX][GHOST][BOOKS][TOOL]]"
  ],
  "learning": {
    "last_updated": "2025-10-16",
    "fixes_applied": 0,
    "patterns_learned": 3
  }
}
```

**Validate**: Does file parse as JSON?
```bash
python -c "import json; print(json.load(open('holo_index/qwen_advisor/patterns/unicode_violations.json')))"
```

### Step 2: Create Unicode Fixer Module
**File**: `holo_index/qwen_advisor/unicode_fixer.py`
**Location**: New file

**Create**:
```python
#!/usr/bin/env python3
"""
Unicode Violation Fixer - Gemma Pattern Matching

Detects and fixes Unicode/emoji violations in code that fails on Windows cp932.
Uses Gemma-style fast pattern matching with learned emoji mappings.

WSP Compliance: WSP 90 (UTF-8 Enforcement)
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Tuple


class UnicodeViolationFixer:
    """
    Gemma-style pattern matcher for Unicode violations

    Fast detection: Is there emoji in output code?
    Auto-fix: Replace with ASCII equivalent from pattern memory
    """

    def __init__(self):
        self.patterns_file = Path(__file__).parent / "patterns" / "unicode_violations.json"
        self.patterns = self._load_patterns()

    def _load_patterns(self) -> Dict:
        """Load emoji replacement patterns"""
        if self.patterns_file.exists():
            with open(self.patterns_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"emoji_replacements": {}, "violation_patterns": []}

    def detect_violations(self, file_path: str) -> List[Tuple[int, str]]:
        """
        Gemma fast pattern matching: Find lines with emoji in output

        Returns: List of (line_number, line_content) with violations
        """
        violations = []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            for i, line in enumerate(lines, 1):
                # Check against violation patterns
                for pattern in self.patterns['violation_patterns']:
                    if re.search(pattern, line):
                        violations.append((i, line.strip()))
                        break

        except Exception:
            pass

        return violations

    def fix_file(self, file_path: str) -> Dict:
        """
        Auto-fix Unicode violations in file

        Returns: Results dict with fixes applied
        """
        violations = self.detect_violations(file_path)

        if not violations:
            return {"fixed": False, "reason": "No violations found"}

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Apply replacements
            fixed_content = content
            replacements_made = 0

            for emoji, replacement in self.patterns['emoji_replacements'].items():
                if emoji in fixed_content:
                    fixed_content = fixed_content.replace(emoji, replacement)
                    replacements_made += 1

            # Write back
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(fixed_content)

            # Update learning
            self.patterns['learning']['fixes_applied'] += 1
            self._save_patterns()

            return {
                "fixed": True,
                "violations_found": len(violations),
                "replacements_made": replacements_made,
                "file": file_path
            }

        except Exception as e:
            return {"fixed": False, "error": str(e)}

    def _save_patterns(self):
        """Save updated patterns (learning)"""
        with open(self.patterns_file, 'w', encoding='utf-8') as f:
            json.dump(self.patterns, f, indent=2, ensure_ascii=False)
```

**Validate**: Does module import?
```bash
python -c "from holo_index.qwen_advisor.unicode_fixer import UnicodeViolationFixer; print('Import OK')"
```

### Step 3: Add to Orchestrator
**File**: `holo_index/qwen_advisor/orchestration/qwen_orchestrator.py`

**Add import** (around line 47):
```python
# Unicode Violation Fixer
try:
    from ..unicode_fixer import UnicodeViolationFixer
    UNICODE_FIXER_AVAILABLE = True
except ImportError:
    UNICODE_FIXER_AVAILABLE = False
    UnicodeViolationFixer = None
```

**Add to COMPONENT_META** (around line 56):
```python
COMPONENT_META = {
    ...existing entries...
    'unicode_violation_fixer': ('[TOOL]', 'Unicode Violation Fixer'),
}
```

**Add method to QwenOrchestrator class** (at end):
```python
def fix_unicode_violations(self, file_paths: List[str]) -> Dict:
    """
    Autonomous Unicode violation fixing

    Uses Gemma pattern matching to detect and fix emoji in output code
    """
    if not UNICODE_FIXER_AVAILABLE:
        return {"error": "Unicode fixer not available"}

    fixer = UnicodeViolationFixer()
    results = []

    for file_path in file_paths:
        result = fixer.fix_file(file_path)
        if result.get('fixed'):
            results.append(result)

    return {
        "files_processed": len(file_paths),
        "files_fixed": len(results),
        "results": results
    }
```

**Validate**: Does orchestrator still import?
```bash
python -c "from holo_index.qwen_advisor.orchestration.qwen_orchestrator import QwenOrchestrator; print('Import OK')"
```

## Success Criteria
- [OK] Pattern file created and valid JSON
- [OK] Unicode fixer module imports correctly
- [OK] Integrated into qwen_orchestrator
- [OK] Method callable from orchestrator
- [OK] No breaking changes

## Submission
After completing all 3 steps and validating each:
- Report: "Task 3 complete - Unicode fixer integrated"
- Show test results
- Ready for 0102 review

## Time Estimate
8 minutes

## If Anything Fails
- Stop immediately
- Report failure with error message
- Wait for 0102 direction
- Do NOT proceed to next step
