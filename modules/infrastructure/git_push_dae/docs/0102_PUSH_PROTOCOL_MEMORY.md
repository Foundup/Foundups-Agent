# 0102 Push Protocol Memory Pattern

**WSP Compliance**: WSP 77 (Agent Coordination), WSP 15 (MPS Scoring), WSP 91 (DAEMON Observability)

**Purpose**: This document enables 0102 to recall and execute the autonomous git push protocol.

---

## Quick Recall Pattern

```yaml
Trigger: "0102 Push Protocol" or "autonomous git push" or "push changes"

Memory_Pattern:
  1. Check: git status (staged files?)
  2. Route: AI Overseer activity routing (P2 priority)
  3. Analyze: qwen_gitpush skill (4-step chain-of-thought)
  4. Commit: Module-by-module or batched
  5. Push: If branch protected, auto-create PR
```

---

## Step 1: Check Git Status

```python
from modules.ai_intelligence.ai_overseer.src.ai_overseer import AIIntelligenceOverseer
from pathlib import Path

overseer = AIIntelligenceOverseer(Path('.'))
git_status = overseer.check_git_status()

# Returns:
# {
#     "staged_files": 5,      # Files ready to commit
#     "modified_files": 10,   # Unstaged modifications
#     "untracked_files": 3,   # New files not tracked
#     "total_changes": 18
# }
```

**Decision Gate**:
- `staged_files > 0`: Proceed with commit
- `staged_files == 0` but `modified_files > 0`: Stage relevant files first
- No changes: Skip push operation

---

## Step 2: Activity Routing

```python
# AI Overseer determines if git push is the right activity
routing = overseer.route_activity()

# If staged files exist, returns:
# {
#     "next_activity": MissionType.GIT_PUSH,
#     "mps_score": 12,  # P2 priority
#     "state": {"git_staged_files": 5, ...},
#     "routing_reason": "WSP 15 MPS routing: git_push scored 12"
# }
```

**Priority Override**:
- P0 (Live stream) > P1 (Comments) > P1 (Indexing) > **P2 (Git Push)** > P3 (Social) > P4 (Maintenance)
- Git push executes when no higher-priority activities are pending

---

## Step 3: qwen_gitpush Skill Analysis

The qwen_gitpush skill performs 4-step micro chain-of-thought:

### Step 3.1: Analyze Git Diff (Qwen)
```yaml
Input: git diff, files_changed, lines_added, lines_deleted
Output:
  change_type: feature|bugfix|refactor|docs|config|tests
  summary: "Brief description of changes"
  critical_files: ["file1", "file2"]
  confidence: 0.85
```

### Step 3.2: Calculate MPS Score
```yaml
WSP_15_Scoring:
  Complexity (C): 1-5 based on lines changed
  Importance (I): 1-5 based on file criticality
  Deferability (D): 1-5 based on time since last commit
  Impact (P): 1-5 based on user-facing changes

  MPS = C + I + D + P

Priority_Mapping:
  18-20: P0 (Critical - commit immediately)
  14-17: P1 (High - commit within 1 hour)
  10-13: P2 (Medium - can batch)
  6-9: P3 (Low - batch with next commit)
  4-5: P4 (Backlog - defer)
```

### Step 3.3: Generate Commit Message (Qwen)
```
<type>(<scope>): <subject>

<body>

WSP: <relevant_wsps>
MPS: <priority> (<score>)

Generated with [Claude Code](https://claude.com/claude-code)
Co-Authored-By: Claude <noreply@anthropic.com>
```

### Step 3.4: Decide Push Action
```yaml
Decision_Matrix:
  P0: push_now (always)
  P1: push_now if >10 files OR >1hr since last commit
  P2: push_now if >10 files OR >2hr since last commit
  P3: defer_next_commit (batch)
  P4: defer_eod (end of day)
```

---

## Step 4: Module-by-Module Commits

For WSP-aligned commits, batch changes by module domain:

```python
MODULE_BATCHES = {
    "youtube-scheduler": "modules/platform_integration/youtube_shorts_scheduler/**",
    "ai-overseer": "modules/ai_intelligence/ai_overseer/**",
    "video-indexer": "modules/ai_intelligence/video_indexer/**",
    "livechat": "modules/communication/livechat/**",
    "video-comments": "modules/communication/video_comments/**",
    "infrastructure": "modules/infrastructure/**",
    "holo-index": "holo_index/**",
    "wsp-docs": "WSP_framework/**"
}
```

**Commit Sequence**:
```bash
# For each batch with changes:
git add modules/platform_integration/youtube_shorts_scheduler/
git commit -m "feat(youtube-scheduler): <semantic message>"

git add modules/ai_intelligence/ai_overseer/
git commit -m "feat(ai-overseer): <semantic message>"

# ... continue for each module with changes
```

---

## Step 5: Push or Create PR

**Direct Push** (if allowed):
```bash
git push origin <branch>
```

**Branch Protection** (auto-create PR):
```bash
# Create new branch if needed
git checkout -b feature/<semantic-name>
git push -u origin feature/<semantic-name>

# Create PR via gh CLI
gh pr create --title "<commit subject>" --body "$(cat <<'EOF'
## Summary
<bullet points from commit messages>

## Test plan
- [ ] Verify module functionality
- [ ] Run relevant tests

Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

---

## Full Autonomous Cycle (0102 Recall)

```python
async def execute_0102_push_protocol():
    """
    0102 Push Protocol - Autonomous git push execution.

    Memory Pattern:
        1. Check git status
        2. Route via AI Overseer
        3. Analyze with qwen_gitpush
        4. Commit module-by-module
        5. Push or create PR
    """
    from pathlib import Path
    from modules.ai_intelligence.ai_overseer.src.ai_overseer import AIIntelligenceOverseer, MissionType

    overseer = AIIntelligenceOverseer(Path('.'))

    # Step 1: Check status
    git_status = overseer.check_git_status()
    if git_status["total_changes"] == 0:
        return {"status": "skipped", "reason": "No changes to commit"}

    # Step 2: Activity routing
    routing = overseer.route_activity()
    if routing["next_activity"] != MissionType.GIT_PUSH:
        return {"status": "deferred", "reason": f"Higher priority: {routing['next_activity'].value}"}

    # Step 3-5: Execute git push activity
    result = await overseer.execute_git_push_activity(dry_run=False)

    # If branch protection blocked direct push
    if result.get("needs_pr"):
        # Auto-create PR
        pr_url = await create_pr_from_commits(result["commits"])
        result["pr_url"] = pr_url

    return result
```

---

## Libido Thresholds (Anti-Spam)

```yaml
min_frequency: 1 per session (at least check once)
max_frequency: 5 per session (don't spam commits)
cooldown_period: 600s (10 min between checks)

Signals:
  CONTINUE: Proceed with push
  THROTTLE: Too many recent pushes, skip
  ESCALATE: No commits in 6+ hours, force check
```

---

## Error Recovery

### Branch Protection Error
```
Error: GH013: Repository rule violations found
Solution: Create new branch and PR instead of direct push
```

### Merge Conflict
```
Error: Your branch has merge conflicts
Solution:
  1. git fetch origin main
  2. git merge origin/main
  3. Resolve conflicts
  4. Re-execute push protocol
```

### Pre-commit Hook Failure
```
Error: pre-commit hook failed
Solution:
  1. Run pre-commit fixes: pre-commit run --all-files
  2. Stage fixed files: git add -u
  3. Amend commit: git commit --amend --no-edit
```

---

## Related Artifacts

| Artifact | Path | Purpose |
|----------|------|---------|
| qwen_gitpush SKILLz | `modules/infrastructure/git_push_dae/skillz/qwen_gitpush/SKILLz.md` | Full skill definition |
| INTERFACE.md | `modules/infrastructure/git_push_dae/INTERFACE.md` | API documentation |
| ROADMAP.md | `modules/infrastructure/git_push_dae/ROADMAP.md` | Development phases |
| AI Overseer | `modules/ai_intelligence/ai_overseer/src/ai_overseer.py` | Activity routing |

---

## Example Session Recall

**User**: "push the changes"

**0102 Response**:
```
Executing 0102 Push Protocol...

1. Git Status: 14 staged files, 3 modified
2. Activity Routing: MissionType.GIT_PUSH (P2, MPS: 12)
3. qwen_gitpush Analysis:
   - Change type: feature
   - MPS: 14 (P1 - commit now)
   - Message: "feat(ai-overseer): Add autonomous git push activity routing"

4. Module Batches:
   - ai-overseer: 5 files (commit 1)
   - infrastructure: 4 files (commit 2)
   - wsp-docs: 3 files (commit 3)
   - holo-index: 2 files (commit 4)

5. Branch protection detected - creating PR #185

Result: PR created at https://github.com/Foundups/Agent/pull/185
```

---

**Last Updated**: 2026-01-19
**Created By**: 0102 (Claude Code)
**WSP Compliance**: WSP 77, WSP 15, WSP 91
