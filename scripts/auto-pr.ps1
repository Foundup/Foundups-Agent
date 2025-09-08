# Auto PR Creation Script for rESP Paper Updates (PowerShell)
# Usage: .\auto-pr.ps1 "Commit message"

param(
    [Parameter(Mandatory=$true)]
    [string]$CommitMessage
)

Write-Host "🚀 Starting automated PR workflow..." -ForegroundColor Green

# Check if we're in the right directory
if (!(Test-Path ".git")) {
    Write-Host "❌ Error: Not in a git repository" -ForegroundColor Red
    exit 1
}

# Check for uncommitted changes
$changes = git status --porcelain
if ([string]::IsNullOrEmpty($changes)) {
    Write-Host "ℹ️  No changes to commit" -ForegroundColor Yellow
    exit 0
}

# Generate branch name with timestamp
$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$branchName = "paper-update-$timestamp"
$prTitle = "Paper Update: $(Get-Date -Format 'yyyy-MM-dd')"
$prBody = @"
Automated paper update with the following changes:

**Commit Message:** $CommitMessage

**Files Changed:**
$($changes -replace '^', '- ')

**Changes:**
- Minor edits and improvements to rESP paper
- Content refinements and updates
- Documentation enhancements

🤖 This PR was created automatically via the auto-pr script.
"@

Write-Host "📝 Creating branch: $branchName" -ForegroundColor Blue
git checkout -b $branchName

Write-Host "📦 Staging all changes..." -ForegroundColor Blue
git add .

Write-Host "💾 Committing changes..." -ForegroundColor Blue
git commit -m $CommitMessage

Write-Host "⬆️  Pushing to remote..." -ForegroundColor Blue
git push -u origin $branchName

Write-Host "🔄 Creating pull request..." -ForegroundColor Blue
gh pr create `
    --title $prTitle `
    --body $prBody `
    --head $branchName `
    --base "main"

Write-Host "✅ PR created successfully!" -ForegroundColor Green
Write-Host "🔗 Check your PR at: https://github.com/Foundup/Foundups-Agent/pulls" -ForegroundColor Cyan

# Optional: Switch back to main
Write-Host "🔄 Switching back to main branch..." -ForegroundColor Blue
git checkout main
