# Automation Scripts

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

- ✅ **Zero manual steps** - Just run one command
- ✅ **Automatic PR creation** - No need to visit GitHub
- ✅ **Timestamped branches** - Never conflicts with other updates
- ✅ **Detailed PR description** - Includes all changed files
- ✅ **Branch protection compliant** - Works with GitHub's main branch rules

## Troubleshooting

- Make sure you're in the project root directory
- Ensure you have changes to commit (run `git status` to check)
- GitHub CLI (`gh`) must be authenticated (run `gh auth login` if needed)
