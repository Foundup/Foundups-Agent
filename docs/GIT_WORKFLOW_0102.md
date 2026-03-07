# Git Workflow for 0102 Agents

**Last Updated**: 2026-03-06

## Dual-Remote Setup

| Remote | Repository | Purpose |
|--------|------------|---------|
| `origin` | github.com/FOUNDUPS/Foundups-Agent | Primary (org repo) |
| `backup` | github.com/Foundup/Foundups-Agent | Mirror (personal) |

**Rule**: Always push to BOTH remotes after commits.

## Quick Commands

```bash
# Push current branch to both remotes
git sync-both

# Push main branch to both remotes
git sync-main

# Alternative (same as sync-both)
git pushall

# Short status
git sts

# List worktrees
git wts
```

## Branch vs Worktree

### Branch
- A pointer to a commit in git history
- Lightweight - just a 41-byte file
- Can exist without being checked out
- Multiple branches can point to same commit

### Worktree
- A physical directory with checked-out files
- Each worktree has exactly ONE branch (or detached HEAD)
- Allows working on multiple branches simultaneously
- **CRITICAL**: Never run 2 agents in the same worktree

## Worktree Architecture

```
O:/Foundups-Agent/                    # Main sandbox (dirty work)
  .worktrees/0102-clean-main/         # Clean integration worktree
```

### Sandbox Worktree (Main)
- Path: `O:/Foundups-Agent`
- Purpose: Active development, experimentation
- State: May have uncommitted changes
- Agents: Primary 0102 agent operates here

### Clean Integration Worktree
- Path: `O:/Foundups-Agent/.worktrees/0102-clean-main`
- Purpose: Clean builds, integration testing
- State: Always matches origin/main
- Agents: CI/CD or verification agents

## Critical Rule: One Agent Per Worktree

```
WRONG:  Agent-A in O:/Foundups-Agent
        Agent-B in O:/Foundups-Agent   <-- CONFLICT!

RIGHT:  Agent-A in O:/Foundups-Agent
        Agent-B in .worktrees/0102-clean-main
```

**Why?** Concurrent git operations in same worktree cause:
- Index corruption
- Lost commits
- Merge conflicts
- File state inconsistencies

## Daily Workflow

### Morning Sync
```bash
# Fetch latest from both remotes
git fetch --all

# Check status
git sts
```

### Before Committing
```bash
# Stage specific files (not "git add .")
git add path/to/specific/file.py

# Verify what's staged
git diff --cached --stat

# Commit with descriptive message
git commit -m "feat(module): description

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

### After Committing
```bash
# Push to BOTH remotes
git sync-both
```

### Switching Context
```bash
# If you need to work on a different branch
# Use a worktree instead of switching in place:
git worktree add .worktrees/feature-x feature-x

# When done, remove the worktree
git worktree remove .worktrees/feature-x
```

## Handling Dirty State

### Legitimate Dirty Files
- Module source code changes
- Documentation updates
- Test additions

### Should Never Be Dirty
- `node_modules/` (in .gitignore)
- `.env` files (in .gitignore)
- `__pycache__/` (in .gitignore)
- `.venv/` (in .gitignore)

### If node_modules Shows Dirty
```bash
# This means it was tracked before - remove from index
git rm -r --cached node_modules
git commit -m "chore(git): remove node_modules from tracking"
```

## Commit Isolation Strategy

**Rule**: Each commit should contain ONE logical change.

```bash
# WRONG: Bundle everything
git add .
git commit -m "various updates"

# RIGHT: Isolate changes
git add modules/ai_intelligence/ai_overseer/src/*.py
git commit -m "feat(ai_overseer): add daemon monitoring"

git add WSP_framework/src/WSP_*.md
git commit -m "docs(wsp): update protocol definitions"
```

## Emergency Commands (Use With Caution)

These require explicit 012 approval:

```bash
# Discard ALL local changes (DESTRUCTIVE)
# git reset --hard origin/main

# Force push (DANGEROUS - overwrites remote)
# git push --force origin main

# Delete a worktree forcefully
# git worktree remove --force .worktrees/name
```

---

*This workflow optimized for single-operator multi-agent development.*
