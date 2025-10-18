# Cross-Module Development Tools

## [CLIPBOARD] WSP 85 Root Directory Protection Compliance

**This directory contains ONLY cross-module development utilities.** All module-specific scripts have been moved to their proper locations per WSP 85:

- **Communication scripts** -> `modules/communication/{module}/scripts/`
- **Infrastructure scripts** -> `modules/infrastructure/{module}/scripts/`
- **Platform scripts** -> `modules/platform_integration/{module}/scripts/`

## [U+1F5D1]️ SCRIPTS_CATALOG.md Removal

**The SCRIPTS_CATALOG.md file has been removed** as it was counterproductive for 0102 semantic search:

### **Why Removed:**
- **Static vs Dynamic**: HoloIndex provides dynamic semantic search - no need for static catalogs
- **Maintenance Burden**: Every script move required catalog updates (violates WSP principles)
- **Redundant**: HoloIndex already catalogs and finds all scripts semantically
- **Misleading**: Listed scripts that moved or don't exist

### **How 0102 Finds Scripts Now:**
```bash
# Semantic search directly through HoloIndex
python holo_index.py --search "capture stream logs"
python holo_index.py --search "feed scripts to holoindex"
python holo_index.py --search "test breadcrumb integration"
```

**Result**: Scripts are found regardless of location, eliminating maintenance overhead.

## Paper Update Workflow

### Quick Update (Recommended)
```powershell
.\scripts\paper-update.ps1
```

### Custom Message Update
```powershell
.\scripts\auto-pr.ps1 "Your custom commit message"
```

## What These Scripts Do

1. **Create timestamped branch** - `paper-update-YYYYMMDD-HHMMSS`
2. **Stage all changes** - Adds all modified files
3. **Commit with message** - Uses your provided message
4. **Push to remote** - Creates remote branch
5. **Create Pull Request** - Automatically opens PR on GitHub
6. **Return to main** - Switches back to main branch

## Examples

```powershell
# Quick paper update with default message
.\scripts\paper-update.ps1

# Custom message for specific changes
.\scripts\auto-pr.ps1 "feat(paper): Add new section on quantum coherence analysis"

# Major revision
.\scripts\auto-pr.ps1 "feat(paper): Major rewrite - Bell State framework implementation"
```

## Benefits

- [OK] **Zero manual steps** - Just run one command
- [OK] **Automatic PR creation** - No need to visit GitHub
- [OK] **Timestamped branches** - Never conflicts with other updates
- [OK] **Detailed PR description** - Includes all changed files
- [OK] **Branch protection compliant** - Works with GitHub's main branch rules

## Troubleshooting

- Make sure you're in the project root directory
- Ensure you have changes to commit (run `git status` to check)
- GitHub CLI (`gh`) must be authenticated (run `gh auth login` if needed)
