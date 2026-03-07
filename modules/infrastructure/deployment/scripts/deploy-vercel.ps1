# FoundUps Agent - Vercel Deployment Script
# Automates the deployment of FoundUps to Vercel cloud platform
# WSP Compliant: Located in modules/infrastructure/deployment/scripts/

Write-Host "[ROCKET] FoundUps Agent - Vercel Deployment Script" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host "WSP Location: modules/infrastructure/deployment/scripts/" -ForegroundColor Cyan
Write-Host "Note: Run this script from the project root directory" -ForegroundColor Yellow

# Check if Vercel CLI is installed
try {
    $vercelVersion = & vercel --version 2>$null
    Write-Host "[OK] Vercel CLI available: $vercelVersion" -ForegroundColor Green
} catch {
    Write-Host "[BOX] Installing Vercel CLI..." -ForegroundColor Yellow
    npm install -g vercel
}

# Check if user is logged in
try {
    $whoami = & vercel whoami 2>$null
    Write-Host "[OK] Logged in as: $whoami" -ForegroundColor Green
} catch {
    Write-Host "[U+1F510] Please login to Vercel:" -ForegroundColor Yellow
    & vercel login
}

# Check if already linked
if (Test-Path ".vercel") {
    Write-Host "[OK] Vercel project already linked" -ForegroundColor Green
} else {
    Write-Host "[LINK] Linking to Vercel project..." -ForegroundColor Yellow
    & vercel link
}

# Set production environment variables
Write-Host "[TOOL] Setting up environment variables..." -ForegroundColor Yellow
Write-Host "Enter values for environment variables (or press Enter for defaults):"

function Set-VercelEnvValue {
    param(
        [string]$Name,
        [string]$Value
    )
    foreach ($target in @("production", "preview")) {
        $Value | & vercel env add $Name $target 2>$null | Out-Null
    }
}

$localModelRoot = Read-Host "LOCAL_MODEL_ROOT (default: E:/LM_studio/models/local)"
if (-not $localModelRoot) { $localModelRoot = "E:/LM_studio/models/local" }
Set-VercelEnvValue -Name "LOCAL_MODEL_ROOT" -Value $localModelRoot

$triageDir = Read-Host "LOCAL_MODEL_TRIAGE_DIR (default: E:/LM_studio/models/local/gemma-270m)"
if (-not $triageDir) { $triageDir = "$localModelRoot/gemma-270m" }
Set-VercelEnvValue -Name "LOCAL_MODEL_TRIAGE_DIR" -Value $triageDir

$generalDir = Read-Host "LOCAL_MODEL_GENERAL_DIR (default: E:/LM_studio/models/local/qwen3-4b)"
if (-not $generalDir) { $generalDir = "$localModelRoot/qwen3-4b" }
Set-VercelEnvValue -Name "LOCAL_MODEL_GENERAL_DIR" -Value $generalDir

$codeDir = Read-Host "LOCAL_MODEL_CODE_DIR (default: E:/LM_studio/models/local/qwen-coder-7b)"
if (-not $codeDir) { $codeDir = "$localModelRoot/qwen-coder-7b" }
Set-VercelEnvValue -Name "LOCAL_MODEL_CODE_DIR" -Value $codeDir

# Legacy alias retained for compatibility with older workers.
Set-VercelEnvValue -Name "HOLO_QWEN_MODEL" -Value $codeDir

# HOLO_QWEN_MAX_TOKENS
$maxTokens = Read-Host "HOLO_QWEN_MAX_TOKENS (default: 512)"
if (-not $maxTokens) { $maxTokens = "512" }
Set-VercelEnvValue -Name "HOLO_QWEN_MAX_TOKENS" -Value $maxTokens

# HOLO_QWEN_TEMPERATURE
$temperature = Read-Host "HOLO_QWEN_TEMPERATURE (default: 0.2)"
if (-not $temperature) { $temperature = "0.2" }
Set-VercelEnvValue -Name "HOLO_QWEN_TEMPERATURE" -Value $temperature

# Deploy
Write-Host "[ROCKET] Deploying to production..." -ForegroundColor Green
& vercel --prod

Write-Host ""
Write-Host "[CELEBRATE] Deployment Complete!" -ForegroundColor Green
Write-Host "======================" -ForegroundColor Green
Write-Host "Your autonomous development platform is now live on Vercel!" -ForegroundColor Cyan
Write-Host ""
Write-Host "[U+1F310] API Endpoints:" -ForegroundColor Yellow
Write-Host "  - Health Check: https://your-app.vercel.app/api/health" -ForegroundColor White
Write-Host "  - System Status: https://your-app.vercel.app/api/status" -ForegroundColor White
Write-Host "  - HoloIndex Search: https://your-app.vercel.app/api/search?q=your+query" -ForegroundColor White
Write-Host ""
Write-Host "[TOOL] Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Visit your Vercel dashboard to monitor usage" -ForegroundColor White
Write-Host "  2. Set up custom domain (optional)" -ForegroundColor White
Write-Host "  3. Configure additional environment variables as needed" -ForegroundColor White
Write-Host "  4. Share the API endpoints with your autonomous agents!" -ForegroundColor White
Write-Host ""
Write-Host "[IDEA] Pro Tips:" -ForegroundColor Yellow
Write-Host "  - Free tier: 100GB bandwidth, 100 serverless invocations/month" -ForegroundColor White
Write-Host "  - Automatic scaling and global CDN included" -ForegroundColor White
Write-Host "  - HTTPS certificates are automatic" -ForegroundColor White
Write-Host ""
Write-Host "[TARGET] FoundUps is now globally accessible for autonomous development!" -ForegroundColor Green
