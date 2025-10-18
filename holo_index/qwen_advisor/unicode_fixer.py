#!/usr/bin/env python3
"""
Unicode Violation Fixer - Gemma Pattern Matching

Detects and fixes Unicode/emoji violations in code that fails on Windows cp932.
Uses Gemma-style fast pattern matching with learned emoji mappings.

WSP Compliance: WSP 90 (UTF-8 Enforcement)
"""

# === UTF-8 ENFORCEMENT (WSP 90) ===
import sys
import io
if __name__ == '__main__' and sys.platform.startswith('win'):
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except (OSError, ValueError):
        # Ignore if stdout/stderr already wrapped or closed
        pass
# === END UTF-8 ENFORCEMENT ===


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
