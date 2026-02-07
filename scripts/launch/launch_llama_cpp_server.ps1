$ErrorActionPreference = "Stop"

$envFile = "o:\Foundups-Agent\.env"
function Get-EnvValue([string]$key) {
  if (-not (Test-Path $envFile)) { return $null }
  $match = Select-String -Path $envFile -Pattern ("^" + [regex]::Escape($key) + "=") | Select-Object -First 1
  if ($match) {
    $value = $match.Line.Substring($key.Length + 1).Trim()
    return $value.Trim('"')
  }
  return $null
}

$modelPath = $env:LLAMA_CPP_MODEL_PATH
if ([string]::IsNullOrWhiteSpace($modelPath)) { $modelPath = Get-EnvValue "LLAMA_CPP_MODEL_PATH" }
if ([string]::IsNullOrWhiteSpace($modelPath)) {
  $modelPath = "E:\HoloIndex\models\qwen-coder-1.5b.gguf"
}

$bindHost = $env:LLAMA_CPP_HOST
if ([string]::IsNullOrWhiteSpace($bindHost)) { $bindHost = Get-EnvValue "LLAMA_CPP_HOST" }
if ([string]::IsNullOrWhiteSpace($bindHost)) { $bindHost = "127.0.0.1" }

$port = $env:LLAMA_CPP_PORT
if ([string]::IsNullOrWhiteSpace($port)) { $port = Get-EnvValue "LLAMA_CPP_PORT" }
if ([string]::IsNullOrWhiteSpace($port)) { $port = "1234" }

$python = $env:LLAMA_CPP_PYTHON
if ([string]::IsNullOrWhiteSpace($python)) { $python = Get-EnvValue "LLAMA_CPP_PYTHON" }
if ([string]::IsNullOrWhiteSpace($python)) { $python = "o:\Foundups-Agent\.venv\Scripts\python.exe" }

if (-not (Test-Path $modelPath)) {
  Write-Error "LLAMA_CPP_MODEL_PATH not found: $modelPath"
  exit 2
}

if (-not (Test-Path $python)) {
  Write-Error "Python not found: $python"
  exit 3
}

$debug = $env:LLAMA_CPP_DEBUG
if ($debug -eq "1") {
  Write-Output "DEBUG modelPath=$modelPath host=$bindHost port=$port python=$python"
}

# Check if server already listening
$client = New-Object System.Net.Sockets.TcpClient
$iar = $client.BeginConnect($bindHost, [int]$port, $null, $null)
$ok = $iar.AsyncWaitHandle.WaitOne(300)
if ($ok -and $client.Connected) {
  $client.EndConnect($iar)
  $client.Close()
  try {
    Invoke-RestMethod -Uri ("http://{0}:{1}/v1/models" -f $bindHost, $port) -Method Get -TimeoutSec 2 | Out-Null
    Write-Output "ALREADY_RUNNING"
    exit 0
  } catch {
    # Port open but not the expected server, continue to start
  }
} else {
  $client.Close()
}

$args = @("-m", "llama_cpp.server", "--model", $modelPath, "--host", $bindHost, "--port", $port)

$nCtx = $env:LLAMA_CPP_N_CTX
if ([string]::IsNullOrWhiteSpace($nCtx)) { $nCtx = Get-EnvValue "LLAMA_CPP_N_CTX" }
if (-not [string]::IsNullOrWhiteSpace($nCtx)) { $args += @("--n_ctx", $nCtx) }

$nGpu = $env:LLAMA_CPP_N_GPU_LAYERS
if ([string]::IsNullOrWhiteSpace($nGpu)) { $nGpu = Get-EnvValue "LLAMA_CPP_N_GPU_LAYERS" }
if (-not [string]::IsNullOrWhiteSpace($nGpu)) { $args += @("--n_gpu_layers", $nGpu) }

$threads = $env:LLAMA_CPP_THREADS
if ([string]::IsNullOrWhiteSpace($threads)) { $threads = Get-EnvValue "LLAMA_CPP_THREADS" }
if (-not [string]::IsNullOrWhiteSpace($threads)) { $args += @("--threads", $threads) }

Start-Process -FilePath $python -ArgumentList $args -WorkingDirectory (Split-Path $modelPath) -WindowStyle Hidden
Write-Output "STARTED"
