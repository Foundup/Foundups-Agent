#!/bin/bash
# Auto PR Creation Script for rESP Paper Updates
# Usage: ./auto-pr.sh "Commit message"

set -e  # Exit on any error

# Check if commit message is provided
if [ $# -eq 0 ]; then
    echo "❌ Error: Please provide a commit message"
    echo "Usage: ./auto-pr.sh \"Your commit message\""
    exit 1
fi

COMMIT_MESSAGE="$1"

echo "🚀 Starting automated PR workflow..."

# Check if we're in the right directory
if [ ! -d ".git" ]; then
    echo "❌ Error: Not in a git repository"
    exit 1
fi

# Check for uncommitted changes
if [ -z "$(git status --porcelain)" ]; then
    echo "ℹ️  No changes to commit"
    exit 0
fi

# Generate branch name with timestamp
BRANCH_NAME="paper-update-$(date +%Y%m%d-%H%M%S)"
PR_TITLE="Paper Update: $(date +%Y-%m-%d)"
PR_BODY="Automated paper update with the following changes:

**Commit Message:** $COMMIT_MESSAGE

**Files Changed:**
$(git status --porcelain | sed 's/^/- /')

**Changes:**
- Minor edits and improvements to rESP paper
- Content refinements and updates
- Documentation enhancements

🤖 This PR was created automatically via the auto-pr script."

echo "📝 Creating branch: $BRANCH_NAME"
git checkout -b "$BRANCH_NAME"

echo "📦 Staging all changes..."
git add .

echo "💾 Committing changes..."
git commit -m "$COMMIT_MESSAGE"

echo "⬆️  Pushing to remote..."
git push -u origin "$BRANCH_NAME"

echo "🔄 Creating pull request..."
gh pr create \
    --title "$PR_TITLE" \
    --body "$PR_BODY" \
    --head "$BRANCH_NAME" \
    --base "main"

echo "✅ PR created successfully!"
echo "🔗 Check your PR at: https://github.com/Foundup/Foundups-Agent/pulls"

# Optional: Switch back to main
echo "🔄 Switching back to main branch..."
git checkout main
