param(
    [ValidateSet("prezi", "cursor", "all")]
    [string]$Scope = "all",
    [string]$TargetRoot = "G:\FoundupsData",
    [switch]$DryRun
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Test-IsJunction {
    param([string]$Path)
    if (-not (Test-Path -LiteralPath $Path)) { return $false }
    $item = Get-Item -LiteralPath $Path -Force
    return (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0)
}

function Get-DirSizeGb {
    param([string]$Path)
    if (-not (Test-Path -LiteralPath $Path)) { return 0.0 }
    $sum = (Get-ChildItem -LiteralPath $Path -Recurse -Force -ErrorAction SilentlyContinue | Measure-Object Length -Sum).Sum
    return [math]::Round(($sum / 1GB), 2)
}

function Move-WithJunction {
    param(
        [string]$Source,
        [string]$Destination,
        [string[]]$BlockIfRunning = @(),
        [string[]]$StopIfRunning = @()
    )

    if (-not (Test-Path -LiteralPath $Source)) {
        Write-Output "SKIP missing: $Source"
        return
    }

    if (Test-IsJunction -Path $Source) {
        Write-Output "SKIP already linked: $Source"
        return
    }

    foreach ($name in $BlockIfRunning) {
        if (Get-Process -Name $name -ErrorAction SilentlyContinue) {
            if ($DryRun) {
                Write-Output "BLOCKED (dry-run): process '$name' is running for $Source"
                return
            }
            throw "Blocked: process '$name' is running. Close it first, then retry."
        }
    }

    foreach ($name in $StopIfRunning) {
        Get-Process -Name $name -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
    }

    $srcSizeGb = Get-DirSizeGb -Path $Source
    Write-Output "MOVE $Source ($srcSizeGb GB) -> $Destination"

    if ($DryRun) {
        Write-Output "DRYRUN no changes for: $Source"
        return
    }

    New-Item -ItemType Directory -Path (Split-Path -Path $Destination -Parent) -Force | Out-Null
    New-Item -ItemType Directory -Path $Destination -Force | Out-Null

    & robocopy $Source $Destination /E /MOVE /COPY:DAT /DCOPY:T /R:1 /W:1 /XJ /NFL /NDL /NP | Out-Null
    $rc = $LASTEXITCODE
    if ($rc -ge 8) {
        throw "robocopy failed (exit=$rc) for $Source"
    }

    if (Test-Path -LiteralPath $Source) {
        # Source should be empty after /MOVE; if not, keep as-is and do not junction.
        $remaining = (Get-ChildItem -LiteralPath $Source -Force -ErrorAction SilentlyContinue | Measure-Object).Count
        if ($remaining -gt 0) {
            throw "Source not empty after move ($remaining items remain): $Source"
        }
        Remove-Item -LiteralPath $Source -Recurse -Force -ErrorAction SilentlyContinue
    }

    cmd /c "mklink /J `"$Source`" `"$Destination`"" | Out-Null
    if (-not (Test-IsJunction -Path $Source)) {
        throw "Failed to create junction: $Source -> $Destination"
    }

    Write-Output "OK linked: $Source -> $Destination"
}

if ($Scope -in @("prezi", "all")) {
    Move-WithJunction `
        -Source "C:\AppData\Roaming\Prezi" `
        -Destination (Join-Path $TargetRoot "AppData\Roaming\Prezi") `
        -StopIfRunning @("Prezi", "PreziVideo", "PreziCrashHandler", "PreziCrashHandler64")
}

if ($Scope -in @("cursor", "all")) {
    Move-WithJunction `
        -Source "C:\Users\user\AppData\Roaming\Cursor\User\globalStorage" `
        -Destination (Join-Path $TargetRoot "AppData\Roaming\Cursor\User\globalStorage") `
        -BlockIfRunning @("Cursor")
}

$freeC = [math]::Round(((Get-CimInstance Win32_LogicalDisk -Filter "DeviceID='C:'").FreeSpace / 1GB), 2)
$freeG = [math]::Round(((Get-CimInstance Win32_LogicalDisk -Filter "DeviceID='G:'").FreeSpace / 1GB), 2)
Write-Output "FREE C: ${freeC}GB"
Write-Output "FREE G: ${freeG}GB"
