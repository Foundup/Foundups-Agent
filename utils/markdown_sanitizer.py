"""
Markdown Sanitizer

Normalizes a small set of Unicode markdown glyphs to ASCII-safe equivalents.
This is intended for generated summaries and training artifacts that need to
remain readable on Windows terminals and log sinks.
"""

from __future__ import annotations

from typing import Any


TRANSLATION_TABLE = str.maketrans(
    {
        "\u2192": "-->",   # right arrow
        "\u2190": "<--",   # left arrow
        "\u2014": "--",    # em dash
        "\u2013": "-",     # en dash
        "\u2b50": "[*]",   # star
        "\u2705": "[OK]",  # check
    }
)


def sanitize_markdown_text(text: str) -> str:
    """Convert a small set of problematic glyphs to ASCII-safe forms."""
    if not isinstance(text, str):
        return text
    return text.translate(TRANSLATION_TABLE)


def sanitize_markdown_object(value: Any) -> Any:
    """Recursively sanitize strings in basic Python containers."""
    if isinstance(value, str):
        return sanitize_markdown_text(value)
    if isinstance(value, dict):
        return {key: sanitize_markdown_object(item) for key, item in value.items()}
    if isinstance(value, list):
        return [sanitize_markdown_object(item) for item in value]
    if isinstance(value, tuple):
        return tuple(sanitize_markdown_object(item) for item in value)
    return value
