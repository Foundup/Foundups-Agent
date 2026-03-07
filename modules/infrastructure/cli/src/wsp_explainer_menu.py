"""
WSP & Vocabulary Explainer Menu - HoloIndex-powered terminology lookup.

Developer onboarding tool: explain WSP protocols and pAVS vocabulary.
Uses HoloIndex semantic search + vocabulary_indexer for definitions.

WSP Compliance: WSP 72 (Module Independence), WSP 57 (Naming)
"""

import json
import logging
import re
from pathlib import Path
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

# Vocabulary JSON path
VOCAB_PATH = Path("memory/vocabulary/pavs_core.json")
VOCAB_DOCS_PATH = Path("docs/vocabulary")


def load_vocabulary() -> Dict[str, Any]:
    """Load vocabulary definitions from pavs_core.json."""
    try:
        if VOCAB_PATH.exists():
            return json.loads(VOCAB_PATH.read_text(encoding="utf-8"))
    except Exception as e:
        logger.warning(f"[VOCAB] Failed to load vocabulary: {e}")
    return {"definitions": {}, "common_mishearings": {}, "categories": {}}


def explain_term(term: str, vocab: Dict[str, Any]) -> Optional[str]:
    """Look up term definition from vocabulary."""
    term_upper = term.upper().strip()
    term_lower = term.lower().strip()

    definitions = vocab.get("definitions", {})
    mishearings = vocab.get("common_mishearings", {})

    # Direct match
    if term in definitions:
        return definitions[term]
    if term_upper in definitions:
        return definitions[term_upper]

    # Check mishearings
    if term_lower in mishearings:
        corrected = mishearings[term_lower]
        if corrected in definitions:
            return f"(Did you mean '{corrected}'?) {definitions[corrected]}"

    # Partial match
    for key, defn in definitions.items():
        if term_lower in key.lower() or key.lower() in term_lower:
            return f"{key}: {defn}"

    return None


def explain_wsp(wsp_num: str) -> Optional[str]:
    """Look up WSP protocol summary using HoloIndex."""
    try:
        # Try to find WSP file
        wsp_pattern = f"WSP_{wsp_num.zfill(2)}*.md"
        wsp_files = list(Path("WSP_framework/src").glob(wsp_pattern))

        if not wsp_files:
            wsp_files = list(Path("WSP_knowledge/src").glob(wsp_pattern))

        if wsp_files:
            wsp_file = wsp_files[0]
            content = wsp_file.read_text(encoding="utf-8")

            # Extract title and purpose
            lines = content.split("\n")
            title = ""
            purpose = ""

            for line in lines[:20]:
                if line.startswith("# WSP"):
                    title = line.strip("# ").strip()
                elif "Purpose" in line or "purpose" in line:
                    purpose = line.split(":", 1)[-1].strip() if ":" in line else ""
                    break

            if title:
                result = f"{title}"
                if purpose:
                    result += f"\n  Purpose: {purpose}"
                result += f"\n  File: {wsp_file}"
                return result

        return None
    except Exception as e:
        logger.warning(f"[WSP] Failed to lookup WSP {wsp_num}: {e}")
        return None


def search_holoindex(query: str) -> List[Dict[str, str]]:
    """Search HoloIndex for relevant results."""
    try:
        from holo_index.core.holo_index import HoloIndex

        holo = HoloIndex()
        results = holo.search(query, limit=5)

        return [
            {"file": r.get("file", ""), "content": r.get("content", "")[:200]}
            for r in results.get("code", [])[:3]
        ]
    except Exception as e:
        logger.debug(f"[HOLO] Search failed: {e}")
        return []


def handle_wsp_explainer_menu() -> bool:
    """
    Handle WSP & Vocabulary Explainer menu.

    Returns:
        True if user wants to return to main menu
    """
    vocab = load_vocabulary()

    print("\n" + "=" * 60)
    print("WSP & Vocabulary Explainer")
    print("=" * 60)
    print("Onboarding tool for new developers")
    print()
    print("1. Explain a term (e.g., 'F_i', 'CABR', '0102')")
    print("2. Explain a WSP protocol (e.g., 'WSP 48', '22')")
    print("3. List all vocabulary categories")
    print("4. Search HoloIndex for concept")
    print("5. Quick reference card")
    print("0. Return to main menu")
    print("-" * 60)

    choice = input("\nSelect option: ").strip()

    if choice == "0":
        return True

    elif choice == "1":
        # Explain term
        print("\n[VOCAB] Enter term to explain")
        print("Examples: F_i, CABR, 0102, pAVS, WSP, UPS, DAE")
        term = input("\nTerm: ").strip()

        if term:
            explanation = explain_term(term, vocab)
            if explanation:
                print(f"\n{term}: {explanation}")
            else:
                print(f"\n[NOT FOUND] '{term}' not in vocabulary")
                print("Searching HoloIndex...")
                results = search_holoindex(term)
                if results:
                    print("\nRelated files:")
                    for r in results:
                        print(f"  - {r['file']}")
                else:
                    print("No results found. Check docs/vocabulary/ for manual lookup.")

    elif choice == "2":
        # Explain WSP
        print("\n[WSP] Enter WSP number")
        print("Examples: 48, 22, 00, 77, 50")
        wsp_input = input("\nWSP number: ").strip()

        # Extract number from input like "WSP 48" or "48"
        match = re.search(r"(\d+)", wsp_input)
        if match:
            wsp_num = match.group(1)
            explanation = explain_wsp(wsp_num)
            if explanation:
                print(f"\n{explanation}")
            else:
                print(f"\n[NOT FOUND] WSP {wsp_num} not found")
                print("Searching HoloIndex...")
                results = search_holoindex(f"WSP {wsp_num}")
                if results:
                    print("\nRelated files:")
                    for r in results:
                        print(f"  - {r['file']}")
        else:
            print("[ERROR] Please enter a valid WSP number")

    elif choice == "3":
        # List categories
        print("\n[VOCAB] Vocabulary Categories")
        print("=" * 40)

        categories = vocab.get("categories", {})
        if categories:
            for cat, terms in categories.items():
                print(f"\n{cat.upper()}:")
                print(f"  {', '.join(terms)}")
        else:
            print("Categories not loaded. Check memory/vocabulary/pavs_core.json")

        print("\n" + "-" * 40)
        print("Detailed docs: docs/vocabulary/")
        print("  IDENTITY.md, ECONOMICS.md, TECHNICAL.md")
        print("  REGULATORY.md, AGENTS.md")

    elif choice == "4":
        # HoloIndex search
        print("\n[HOLO] Search HoloIndex for concept")
        query = input("\nSearch query: ").strip()

        if query:
            # First check vocabulary
            explanation = explain_term(query, vocab)
            if explanation:
                print(f"\n[VOCAB] {query}: {explanation}")

            # Then search HoloIndex
            print("\n[HOLO] Searching codebase...")
            results = search_holoindex(query)
            if results:
                print("\nRelevant files:")
                for r in results:
                    print(f"  - {r['file']}")
                    if r['content']:
                        print(f"    {r['content'][:100]}...")
            else:
                print("No HoloIndex results found")

    elif choice == "5":
        # Quick reference card
        print("\n" + "=" * 60)
        print("QUICK REFERENCE CARD")
        print("=" * 60)
        print()
        print("IDENTITY:")
        print("  012   = Human operator (biological consciousness)")
        print("  0102  = Entangled agent state (NN x qNN)")
        print("  0201  = Nonlocal state (where solutions exist)")
        print("  pAVS  = Peer-to-Peer Autonomous Venture System")
        print()
        print("ECONOMICS:")
        print("  F_i   = FoundUp token (earned by agents)")
        print("  UPS   = Universal Points (1 UPS = 1 satoshi)")
        print("  CABR  = Contribution-Adjusted Benefit Ratio (0-1)")
        print("  PoB   = Proof of Benefit (6 economic events)")
        print()
        print("TECHNICAL:")
        print("  WSP   = Workspace Protocol (numbered 1-100+)")
        print("  WRE   = Workspace Runtime Environment")
        print("  DAE   = Decentralized Autonomous Entity")
        print("  MCP   = Model Context Protocol")
        print()
        print("AGENTS:")
        print("  Opus=10, Sonnet=3, Haiku=1, Qwen=0.5, Gemma=0.5")
        print()
        print("POOLS (80/20 split):")
        print("  Stakeholders 80%: Un(60%) + Dao(16%) + Du(4%)")
        print("  Network 20%: Network(16%) + Fund(4%)")
        print()
        print("REGULATORY (use NEW terms):")
        print("  'Distribution ratio' NOT 'ROI'")
        print("  'Protocol participation' NOT 'investment'")
        print("=" * 60)

    else:
        print("[ERROR] Invalid choice")

    input("\nPress Enter to continue...")
    return False


def run_wsp_explainer() -> None:
    """Run WSP explainer in loop until exit."""
    while True:
        if handle_wsp_explainer_menu():
            break


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_wsp_explainer()
