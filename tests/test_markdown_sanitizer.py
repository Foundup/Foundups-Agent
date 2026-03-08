from utils.markdown_sanitizer import sanitize_markdown_object, sanitize_markdown_text


def test_sanitize_markdown_text_replaces_known_glyphs():
    raw = "A → B ← C — D – E ⭐ ✅"
    assert sanitize_markdown_text(raw) == "A --> B <-- C -- D - E [*] [OK]"


def test_sanitize_markdown_object_recurses_through_containers():
    value = {
        "title": "Plan → Walkthrough",
        "items": ["⭐", ("✅", "A — B")],
    }

    assert sanitize_markdown_object(value) == {
        "title": "Plan --> Walkthrough",
        "items": ["[*]", ("[OK]", "A -- B")],
    }
