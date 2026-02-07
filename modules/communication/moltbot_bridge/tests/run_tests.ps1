#!/usr/bin/env pwsh
# Deterministic test runner for moltbot_bridge tests.
# - Forces local venv python
# - Disables third-party pytest plugin auto-discovery
# - Hard CI gate: fails build if security/boundary tests fail (WSP 95/71)

param(
    [string[]]$PytestArgs = @("-q"),
    [switch]$SkipSecurityGate
)

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Resolve-Path (Join-Path $scriptDir "..\..\..\..")
$venvPython = Join-Path $repoRoot ".venv\Scripts\python.exe"

if (-not (Test-Path $venvPython)) {
    throw "Local venv python not found: $venvPython"
}

$previousAutoload = [Environment]::GetEnvironmentVariable("PYTEST_DISABLE_PLUGIN_AUTOLOAD", "Process")
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = "1"

# Hard CI gate tests (WSP 95/71)
$securityGateTests = @(
    "test_skill_boundary_policy.py",
    "test_skill_safety_guard.py",
    "test_hardening_tranche.py"
)

Push-Location $repoRoot
try {
    # Step 1: Run security gate tests first (hard fail)
    if (-not $SkipSecurityGate) {
        Write-Host "[CI-GATE] Running security gate tests..." -ForegroundColor Cyan
        foreach ($testFile in $securityGateTests) {
            $testPath = "modules/communication/moltbot_bridge/tests/$testFile"
            if (Test-Path $testPath) {
                & $venvPython -m pytest $testPath -q
                if ($LASTEXITCODE -ne 0) {
                    Write-Host "[CI-GATE] FAILED: $testFile" -ForegroundColor Red
                    Write-Host "[CI-GATE] Build blocked by security gate (WSP 95/71)" -ForegroundColor Red
                    exit 1
                }
                Write-Host "[CI-GATE] PASSED: $testFile" -ForegroundColor Green
            }
        }
        Write-Host "[CI-GATE] All security gate tests passed" -ForegroundColor Green
    }

    # Step 2: Run full test suite
    Write-Host "[TEST] Running full test suite..." -ForegroundColor Cyan
    & $venvPython -m pytest "modules/communication/moltbot_bridge/tests" @PytestArgs
    exit $LASTEXITCODE
}
finally {
    if ($null -eq $previousAutoload) {
        Remove-Item Env:PYTEST_DISABLE_PLUGIN_AUTOLOAD -ErrorAction SilentlyContinue
    } else {
        $env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = $previousAutoload
    }
    Pop-Location
}
