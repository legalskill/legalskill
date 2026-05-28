# IMA Legal Consultation Expert - One-click install
param(
    [string]$SessionId = $env:WORKBUDDY_SESSION_ID
)

$ErrorActionPreference = "Stop"
$expertName = "tencent-ima-copilot-legal-consultation"
$targetDir = "$env:USERPROFILE\.workbuddy\plugins\marketplaces\my-experts\plugins\$expertName"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "=== IMA Legal Consultation Expert Install ===" -ForegroundColor Cyan

# Step 1: Copy
Write-Host "[1/3] Copy to $targetDir"
if (Test-Path $targetDir) {
    Remove-Item -Recurse -Force $targetDir
}
Copy-Item -Recurse -Force "$scriptDir" "$targetDir"
Write-Host "  OK"

# Step 2: Session ID
if (-not $SessionId) {
    $SessionId = [guid]::NewGuid().ToString()
    Write-Host "[2/3] Auto session-id: $SessionId"
} else {
    Write-Host "[2/3] session-id: $SessionId"
}

# Step 3: Register
Write-Host "[3/3] Register"
$registerScript = "$targetDir\scripts\register_expert.py"
$pythonExe = (Get-Command python3 -ErrorAction SilentlyContinue).Source
if (-not $pythonExe) { $pythonExe = (Get-Command python -ErrorAction SilentlyContinue).Source }
if (-not $pythonExe) {
    Write-Host "  ERROR: python3/python not found"
    exit 1
}
$env:PYTHONIOENCODING = "utf-8"
& $pythonExe $registerScript $targetDir --session-id $SessionId

$line = "=" * 40
Write-Host ""
Write-Host $line -ForegroundColor Green
Write-Host "  Install OK. Restart WorkBuddy to use." -ForegroundColor Green
Write-Host $line -ForegroundColor Green
