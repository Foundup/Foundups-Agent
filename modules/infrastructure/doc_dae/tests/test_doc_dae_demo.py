"""
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
    print("\n🤖 Running autonomous organization (DRY RUN)...\n")
    result = dae.run_autonomous_organization(dry_run=True)

    # Show summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)

    analysis = result['analysis']
    plan = result['plan']

    print(f"\n📊 Files Analyzed: {analysis['total_files']}")
    print(f"   📄 Markdown docs: {analysis['markdown_docs']}")
    print(f"   📊 JSON data: {analysis['json_data']}")
    print(f"   ❓ Other: {analysis['other']}")

    print(f"\n📦 Movement Plan:")
    print(f"   📦 To Move: {plan['summary']['to_move']} files")
    print(f"   🗄️  To Archive: {plan['summary']['to_archive']} files")
    print(f"   ✅ To Keep: {plan['summary']['to_keep']} files")
    print(f"   ❓ Unmatched: {plan['summary']['unmatched']} files")

    # Show some examples
    print(f"\n📦 Example Moves (first 5):")
    for i, move in enumerate(plan['moves'][:5], 1):
        source_name = Path(move['source']).name
        module = move['module']
        print(f"   {i}. {source_name[:50]}... → {module}/docs/")

    print(f"\n🗄️  Example Archives (first 5):")
    for i, archive in enumerate(plan['archives'][:5], 1):
        source_name = Path(archive['source']).name
        reason = archive['reason']
        print(f"   {i}. {source_name[:50]}... ({reason})")

    print(f"\n✅ Example Keeps (first 5):")
    for i, keep in enumerate(plan['keeps'][:5], 1):
        path_name = Path(keep['path']).name
        reason = keep['reason']
        print(f"   {i}. {path_name[:50]}... ({reason})")

    print("\n" + "="*80)
    print("Training Opportunity:")
    print("  • Gemma: Fast classification (doc vs data, module extraction)")
    print("  • Qwen: Complex coordination (73 files → destinations)")
    print("  • Pattern memory: All decisions stored for future automation")
    print("="*80)

    print(f"\n💡 To execute for real:")
    print(f"   python main.py → option 13 → Execute (not dry-run)")

    return result


if __name__ == "__main__":
    demo_doc_organization()
