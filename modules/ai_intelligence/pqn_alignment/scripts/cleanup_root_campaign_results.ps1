# WSP 85 Compliance: Remove root campaign_results/ directory
# All campaign results are now in modules/ai_intelligence/pqn_alignment/campaign_results/

Write-Host "[WSP 85] Removing root campaign_results/ directory (violates WSP 85 Root Directory Protection)" -ForegroundColor Yellow
Write-Host "  All campaign results are safely stored in module location:" -ForegroundColor Cyan
Write-Host "  modules/ai_intelligence/pqn_alignment/campaign_results/" -ForegroundColor Cyan
Write-Host ""

$confirm = Read-Host "Delete root campaign_results/ directory? (y/N)"
if ($confirm -eq 'y' -or $confirm -eq 'Y') {
    if (Test-Path "campaign_results") {
        Remove-Item -Recurse -Force "campaign_results"
        Write-Host "[OK] Root campaign_results/ removed - WSP 85 compliance restored" -ForegroundColor Green
    } else {
        Write-Host "[OK] Root campaign_results/ already removed" -ForegroundColor Green
    }
} else {
    Write-Host "[SKIP] Deletion cancelled" -ForegroundColor Yellow
}



