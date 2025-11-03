# -*- coding: utf-8 -*-
from __future__ import annotations

import sys
import io



from typing import Any, Dict, List


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

def build_compliance_prompt(query: str, code_hits: List[Dict[str, Any]], wsp_hits: List[Dict[str, Any]]) -> str:
    """Construct the base prompt for Qwen compliance advisor.

    The prompt summarises retrieved code (NEED_TO) and WSP guidance so the
    LLM can recommend next steps without hallucinating new modules (WSP 17 & 87).
    """

    def format_hits(prefix: str, hits: List[Dict[str, Any]]) -> str:
        if not hits:
            return f"No {prefix} results found."
        lines = []
        for item in hits[:5]:
            if item is None:  # Skip None entries
                continue
            summary = item.get("need") or item.get("summary") or item.get("title")
            location = item.get("location") or item.get("path")
            lines.append(f"- {summary} ({location})")
        return "\n".join(lines) if lines else f"No valid {prefix} results found."

    code_section = format_hits("code", code_hits)
    wsp_section = format_hits("WSP", wsp_hits)

    prompt = (
        "You are the HoloIndex WSP compliance advisor.\n"
        "User query: {query}\n\n"
        "Relevant code navigation entries:\n{code}\n\n"
        "Relevant WSP protocols:\n{wsp}\n\n"
        "Provide: (1) immediate reminders, (2) WSP checks to confirm, (3) TODO list before coding."
    ).format(query=query, code=code_section, wsp=wsp_section)

    return prompt
