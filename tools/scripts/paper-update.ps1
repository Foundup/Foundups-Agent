# Quick Paper Update Script
# Usage: .\paper-update.ps1

param(
    [string]$Message = "docs(paper): Minor edits and refinements to rESP paper"
)

Write-Host "[NOTE] Updating rESP paper..." -ForegroundColor Green
.\auto-pr.ps1 $Message
