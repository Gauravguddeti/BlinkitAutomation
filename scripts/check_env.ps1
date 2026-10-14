# check_env.ps1
# Pre-run environment validator for the Blinkit Grocery Assistant flow.
# Run this once before starting Power Automate Desktop to confirm everything is in place.
#
# Usage:
#   powershell -ExecutionPolicy Bypass -File check_env.ps1

Write-Host "`n=== Blinkit Assistant — Environment Check ===" -ForegroundColor Cyan

$ok = $true

# Python
try {
    $pyVer = & python --version 2>&1
    Write-Host "[OK] Python: $pyVer" -ForegroundColor Green
} catch {
    Write-Host "[WARN] Python not found — PowerShell fallback (send_email.ps1) will be used" -ForegroundColor Yellow
}

# Gmail credentials
if ($env:GMAIL_USER) {
    Write-Host "[OK] GMAIL_USER: $($env:GMAIL_USER)" -ForegroundColor Green
} else {
    Write-Host "[FAIL] GMAIL_USER is not set" -ForegroundColor Red; $ok = $false
}

if ($env:GMAIL_APP_PASSWORD) {
    Write-Host "[OK] GMAIL_APP_PASSWORD is set (length: $($env:GMAIL_APP_PASSWORD.Length))" -ForegroundColor Green
} else {
    Write-Host "[FAIL] GMAIL_APP_PASSWORD is not set" -ForegroundColor Red; $ok = $false
}

# Config files
$root     = Split-Path $PSScriptRoot -Parent
$settings = Join-Path $root "config\settings.json"
$items    = Join-Path $root "config\items.csv"

if (Test-Path $settings) {
    $s = Get-Content $settings | ConvertFrom-Json
    Write-Host "[OK] settings.json found" -ForegroundColor Green
    if ($s.delivery.address -match "YOUR") { Write-Host "[WARN] Address is still a placeholder" -ForegroundColor Yellow }
    if ($s.recipients.whatsapp_number -match "XXXX") { Write-Host "[WARN] WhatsApp number is still a placeholder" -ForegroundColor Yellow }
} else {
    Write-Host "[FAIL] config/settings.json not found" -ForegroundColor Red; $ok = $false
}

if (Test-Path $items) {
    Write-Host "[OK] config/items.csv found" -ForegroundColor Green
} else {
    Write-Host "[FAIL] config/items.csv not found" -ForegroundColor Red; $ok = $false
}

# Output directories
$outDir        = Join-Path $root "output"
$screenshotDir = Join-Path $outDir "screenshots"
foreach ($dir in @($outDir, $screenshotDir)) {
    if (-not (Test-Path $dir)) { New-Item -ItemType Directory -Path $dir | Out-Null }
    Write-Host "[OK] Directory ready: $dir" -ForegroundColor Green
}

Write-Host ""
if ($ok) {
    Write-Host "All checks passed. You can start the flow in PAD." -ForegroundColor Green
} else {
    Write-Host "One or more checks failed. Fix the issues above before running." -ForegroundColor Red
}
Write-Host ""
