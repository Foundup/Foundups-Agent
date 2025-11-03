# -*- coding: utf-8 -*-

"""
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

DocDAE Demo - Show Qwen/Gemma coordination in action
"""

import sys
import io
from pathlib import Path

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))

from modules.infrastructure.doc_dae.src.doc_dae import DocDAE


def demo_doc_organization():
    """Demo DocDAE - WSP 77 Training Mission"""
    print("="*80)
    print("DocDAE - Autonomous Documentation Organization")
    print("WSP 77 Training Mission: Qwen/Gemma Coordination")
    print("="*80)

    # Initialize
    dae = DocDAE()

    # Run analysis
    print("\n[BOT] Running autonomous organization (DRY RUN)...\n")
    result = dae.run_autonomous_organization(dry_run=True)

    # Show summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)

    analysis = result['analysis']
    plan = result['plan']

    print(f"\n[DATA] Files Analyzed: {analysis['total_files']}")
    print(f"   [U+1F4C4] Markdown docs: {analysis['markdown_docs']}")
    print(f"   [DATA] JSON data: {analysis['json_data']}")
    print(f"   [U+2753] Other: {analysis['other']}")

    print(f"\n[BOX] Movement Plan:")
    print(f"   [BOX] To Move: {plan['summary']['to_move']} files")
    print(f"   [U+1F5C4]️  To Archive: {plan['summary']['to_archive']} files")
    print(f"   [OK] To Keep: {plan['summary']['to_keep']} files")
    print(f"   [U+2753] Unmatched: {plan['summary']['unmatched']} files")

    # Show some examples
    print(f"\n[BOX] Example Moves (first 5):")
    for i, move in enumerate(plan['moves'][:5], 1):
        source_name = Path(move['source']).name
        module = move['module']
        print(f"   {i}. {source_name[:50]}... -> {module}/docs/")

    print(f"\n[U+1F5C4]️  Example Archives (first 5):")
    for i, archive in enumerate(plan['archives'][:5], 1):
        source_name = Path(archive['source']).name
        reason = archive['reason']
        print(f"   {i}. {source_name[:50]}... ({reason})")

    print(f"\n[OK] Example Keeps (first 5):")
    for i, keep in enumerate(plan['keeps'][:5], 1):
        path_name = Path(keep['path']).name
        reason = keep['reason']
        print(f"   {i}. {path_name[:50]}... ({reason})")

    print("\n" + "="*80)
    print("Training Opportunity:")
    print("  • Gemma: Fast classification (doc vs data, module extraction)")
    print("  • Qwen: Complex coordination (73 files -> destinations)")
    print("  • Pattern memory: All decisions stored for future automation")
    print("="*80)

    print(f"\n[IDEA] To execute for real:")
    print(f"   python main.py -> option 13 -> Execute (not dry-run)")

    return result


if __name__ == "__main__":
    demo_doc_organization()
