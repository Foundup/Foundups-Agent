Param(
    [string]$OverseerUrl = $env:HOLO_LLM_BASE_URL,
    [string]$OverseerKey = $env:HOLO_LLM_API_KEY,
    [string]$TarsUrl = $env:TARS_VLM_BASE_URL
)

# Defaults: Overseer (Qwen/Gemma) on 1235, TARS on 1234
if (-not $OverseerUrl) { $OverseerUrl = "http://127.0.0.1:1235/v1" }
if (-not $OverseerKey) { $OverseerKey = "lm-studio" }
if (-not $TarsUrl) { $TarsUrl = "http://127.0.0.1:1234/v1" }

$env:HOLO_LLM_BASE_URL = $OverseerUrl
$env:HOLO_LLM_API_KEY = $OverseerKey

function Test-Endpoint($url) {
    try {
        $probe = $url.TrimEnd('/') + "/models"
        $resp = Invoke-WebRequest -UseBasicParsing -Method Get -Uri $probe -TimeoutSec 5
        return $resp.StatusCode -lt 400
    } catch {
        return $false
    }
}

Write-Host "[CHECK] Overseer (Qwen/Gemma) at $OverseerUrl ..."
if (-not (Test-Endpoint $OverseerUrl)) {
    Write-Host "[FAIL] Overseer endpoint not reachable. Start LM Studio/Ollama on this URL and retry." -ForegroundColor Red
    exit 1
}

Write-Host "[CHECK] TARS (ui-tars-1.5-7b) at $TarsUrl ..."
if (-not (Test-Endpoint $TarsUrl)) {
    Write-Host "[WARN] TARS endpoint not reachable; UI actions may fail. Start LM Studio on this URL if needed." -ForegroundColor Yellow
}

if (-not (Test-Path "logs")) { New-Item -ItemType Directory -Path "logs" | Out-Null }

Write-Host "[HOLODAE] Starting monitor with overseer endpoint $OverseerUrl"
python holo_index.py --start-holodae 2>&1 | Tee-Object -FilePath "logs/holodae_launcher.log"
