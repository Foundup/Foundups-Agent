# FoundUps Agent - Vercel Deployment Script
# Automates the deployment of FoundUps to Vercel cloud platform
# WSP Compliant: Located in modules/infrastructure/deployment/scripts/

Write-Host "🚀 FoundUps Agent - Vercel Deployment Script" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host "WSP Location: modules/infrastructure/deployment/scripts/" -ForegroundColor Cyan
Write-Host "Note: Run this script from the project root directory" -ForegroundColor Yellow

# Check if Vercel CLI is installed
try {
    $vercelVersion = & vercel --version 2>$null
    Write-Host "✅ Vercel CLI available: $vercelVersion" -ForegroundColor Green
} catch {
    Write-Host "📦 Installing Vercel CLI..." -ForegroundColor Yellow
    npm install -g vercel
}

# Check if user is logged in
try {
    $whoami = & vercel whoami 2>$null
    Write-Host "✅ Logged in as: $whoami" -ForegroundColor Green
} catch {
    Write-Host "🔐 Please login to Vercel:" -ForegroundColor Yellow
    & vercel login
}

# Check if already linked
if (Test-Path ".vercel") {
    Write-Host "✅ Vercel project already linked" -ForegroundColor Green
} else {
    Write-Host "🔗 Linking to Vercel project..." -ForegroundColor Yellow
    & vercel link
}

# Set production environment variables
Write-Host "🔧 Setting up environment variables..." -ForegroundColor Yellow
Write-Host "Enter values for environment variables (or press Enter for defaults):"

# HOLO_QWEN_MODEL
$modelPath = Read-Host "HOLO_QWEN_MODEL (default: E:/HoloIndex/models/qwen-coder-1.5b.gguf)"
if (-not $modelPath) { $modelPath = "E:/HoloIndex/models/qwen-coder-1.5b.gguf" }
& vercel env add HOLO_QWEN_MODEL production 2>$null
& vercel env add HOLO_QWEN_MODEL preview 2>$null

# HOLO_QWEN_MAX_TOKENS
$maxTokens = Read-Host "HOLO_QWEN_MAX_TOKENS (default: 512)"
if (-not $maxTokens) { $maxTokens = "512" }
& vercel env add HOLO_QWEN_MAX_TOKENS production 2>$null
& vercel env add HOLO_QWEN_MAX_TOKENS preview 2>$null

# HOLO_QWEN_TEMPERATURE
$temperature = Read-Host "HOLO_QWEN_TEMPERATURE (default: 0.2)"
if (-not $temperature) { $temperature = "0.2" }
& vercel env add HOLO_QWEN_TEMPERATURE production 2>$null
& vercel env add HOLO_QWEN_TEMPERATURE preview 2>$null

# Deploy
Write-Host "🚀 Deploying to production..." -ForegroundColor Green
& vercel --prod

Write-Host ""
Write-Host "🎉 Deployment Complete!" -ForegroundColor Green
Write-Host "======================" -ForegroundColor Green
Write-Host "Your autonomous development platform is now live on Vercel!" -ForegroundColor Cyan
Write-Host ""
Write-Host "🌐 API Endpoints:" -ForegroundColor Yellow
Write-Host "  - Health Check: https://your-app.vercel.app/api/health" -ForegroundColor White
Write-Host "  - System Status: https://your-app.vercel.app/api/status" -ForegroundColor White
Write-Host "  - HoloIndex Search: https://your-app.vercel.app/api/search?q=your+query" -ForegroundColor White
Write-Host ""
Write-Host "🔧 Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Visit your Vercel dashboard to monitor usage" -ForegroundColor White
Write-Host "  2. Set up custom domain (optional)" -ForegroundColor White
Write-Host "  3. Configure additional environment variables as needed" -ForegroundColor White
Write-Host "  4. Share the API endpoints with your autonomous agents!" -ForegroundColor White
Write-Host ""
Write-Host "💡 Pro Tips:" -ForegroundColor Yellow
Write-Host "  - Free tier: 100GB bandwidth, 100 serverless invocations/month" -ForegroundColor White
Write-Host "  - Automatic scaling and global CDN included" -ForegroundColor White
Write-Host "  - HTTPS certificates are automatic" -ForegroundColor White
Write-Host ""
Write-Host "🎯 FoundUps is now globally accessible for autonomous development!" -ForegroundColor Green
