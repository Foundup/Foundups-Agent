"""
Skills Store - Local library of Wardrobe Skills

Manages storage and retrieval of recorded browser interaction skills.
Uses JSON files for persistence with an index for fast lookups.
"""
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Optional

from .skill import WardrobeSkill
from .config import SKILLS_DIR, SKILLS_INDEX_PATH


def _slugify(name: str) -> str:
    """
    Convert skill name to a filesystem-safe slug.

    Args:
        name: Original skill name (e.g. "YT Like and Reply")

    Returns:
        Slugified name (e.g. "yt_like_and_reply")
    """
    # Lowercase, replace spaces/special chars with underscore
    slug = re.sub(r'[^\w\s-]', '', name.lower())
    slug = re.sub(r'[-\s]+', '_', slug)
    return slug.strip('_')


def _load_index() -> dict:
    """Load the skills index from disk."""
    if SKILLS_INDEX_PATH.exists():
        with open(SKILLS_INDEX_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"skills": []}


def _save_index(index: dict) -> None:
    """Save the skills index to disk."""
    with open(SKILLS_INDEX_PATH, 'w', encoding='utf-8') as f:
        json.dump(index, f, indent=2, ensure_ascii=False)


def save_skill(skill: WardrobeSkill) -> Path:
    """
    Save a skill to the library.

    Args:
        skill: The WardrobeSkill to save

    Returns:
        Path to the saved skill file

    Note:
        Updates the skills index atomically.
    """
    # Generate filename
    slug = _slugify(skill.name)
    filename = f"{slug}.{skill.backend}.json"
    filepath = SKILLS_DIR / filename

    # Save skill file
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(skill.to_dict(), f, indent=2, ensure_ascii=False)

    # Update index
    index = _load_index()

    # Remove existing entry with same name+backend (update case)
    index["skills"] = [
        s for s in index["skills"]
        if not (s["name"] == skill.name and s["backend"] == skill.backend)
    ]

    # Add new entry
    index["skills"].append({
        "name": skill.name,
        "backend": skill.backend,
        "created_at": skill.created_at.isoformat(),
        "meta": skill.meta,
        "filename": filename
    })

    _save_index(index)

    print(f"[SKILLS-STORE] Saved skill '{skill.name}' to {filepath}")
    return filepath


def load_skill(name: str, backend: Optional[str] = None) -> Optional[WardrobeSkill]:
    """
    Load a skill from the library.

    Args:
        name: Skill name
        backend: Optional backend filter (if multiple skills with same name)

    Returns:
        WardrobeSkill if found, None otherwise
    """
    index = _load_index()

    # Find matching skill in index
    matches = [
        s for s in index["skills"]
        if s["name"] == name and (backend is None or s["backend"] == backend)
    ]

    if not matches:
        print(f"[SKILLS-STORE] Skill '{name}' not found")
        return None

    if len(matches) > 1 and backend is None:
        print(f"[SKILLS-STORE] Multiple skills named '{name}' found. Specify backend.")
        print(f"  Available backends: {[s['backend'] for s in matches]}")
        return None

    # Load skill file
    skill_entry = matches[0]
    filepath = SKILLS_DIR / skill_entry["filename"]

    if not filepath.exists():
        print(f"[SKILLS-STORE] Skill file missing: {filepath}")
        return None

    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    skill = WardrobeSkill.from_dict(data)
    print(f"[SKILLS-STORE] Loaded skill '{skill.name}' from {filepath}")
    return skill


def list_skills(filter_backend: Optional[str] = None) -> list[WardrobeSkill]:
    """
    List all skills in the library.

    Args:
        filter_backend: Optional backend filter

    Returns:
        List of WardrobeSkills
    """
    index = _load_index()

    skills_list = []
    for entry in index["skills"]:
        if filter_backend and entry["backend"] != filter_backend:
            continue

        # Load full skill
        skill = load_skill(entry["name"], entry["backend"])
        if skill:
            skills_list.append(skill)

    return skills_list


def delete_skill(name: str, backend: Optional[str] = None) -> bool:
    """
    Delete a skill from the library.

    Args:
        name: Skill name
        backend: Optional backend filter

    Returns:
        True if deleted, False if not found

    TODO: Implement when needed
    """
    raise NotImplementedError("Delete functionality not yet implemented")


def import_skill_file(
    file_path: str | Path,
    backend_override: Optional[str] = None,
    name_override: Optional[str] = None,
) -> WardrobeSkill:
    """
    Import a skill JSON file (e.g., from the Chrome extension) into the skills store.

    Args:
        file_path: Path to the JSON skill file
        backend_override: Optional backend to force (useful to map chrome_extension → selenium)
        name_override: Optional new name for the skill

    Returns:
        The imported WardrobeSkill

    Notes:
        - If backend is "chrome_extension", it is mapped to "selenium" by default.
        - Adds metadata: source_file, recorded_with, and step_count (if missing).
    """
    src = Path(file_path)
    if not src.exists():
        raise FileNotFoundError(f"Skill file not found: {src}")

    with open(src, "r", encoding="utf-8") as f:
        data = json.load(f)

    original_backend = data.get("backend", "playwright")
    backend = backend_override or (
        "selenium" if original_backend == "chrome_extension" else original_backend
    )

    name = name_override or data.get("name") or src.stem
    steps = data.get("steps", [])
    created_at = data.get("created_at") or datetime.utcnow().isoformat()
    meta = data.get("meta") or {}
    meta.setdefault("target_url", data.get("meta", {}).get("target_url", ""))
    meta.setdefault("tags", data.get("meta", {}).get("tags", []))
    meta.setdefault("notes", data.get("meta", {}).get("notes", ""))
    meta.setdefault("step_count", len(steps))
    meta.setdefault("recorded_with", original_backend)
    meta["source_file"] = str(src)

    normalized = {
        "name": name,
        "backend": backend,
        "steps": steps,
        "created_at": created_at,
        "meta": meta,
    }

    skill = WardrobeSkill.from_dict(normalized)
    save_skill(skill)
    return skill


# TODO: Future enhancements
# - Search skills by tags (skill.meta["tags"])
# - Filter by domain (skill.meta["domain"])
# - Export/import skill libraries
# - Skill versioning (track multiple versions of same skill)
# - Integration with higher-level "Wardrobe Skills" registry
