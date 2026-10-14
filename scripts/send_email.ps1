# send_email.ps1
# PowerShell alternative to send_email.py for machines without Python.
# Credentials are read from environment variables — never from files.
#
# Usage (via PAD "Run PowerShell script" action):
#   powershell -ExecutionPolicy Bypass -File send_email.ps1 `
#              -To "recipient@example.com" -Subject "Subject" -BodyFile "path\to\body.txt"

param(
    [Parameter(Mandatory)][string]$To,
    [Parameter(Mandatory)][string]$Subject,
    [Parameter(Mandatory)][string]$BodyFile
)

$user     = $env:GMAIL_USER
$password = ($env:GMAIL_APP_PASSWORD -replace ' ', '')

if (-not $user -or -not $password) {
    Write-Output "ERROR: GMAIL_USER or GMAIL_APP_PASSWORD environment variable is not set."
    exit 1
}

if (-not (Test-Path $BodyFile)) {
    Write-Output "ERROR: Body file not found: $BodyFile"
    exit 1
}

$body      = Get-Content -Path $BodyFile -Raw -Encoding UTF8
$securePw  = ConvertTo-SecureString $password -AsPlainText -Force
$cred      = New-Object System.Management.Automation.PSCredential($user, $securePw)

try {
    Send-MailMessage `
        -SmtpServer "smtp.gmail.com" `
        -Port 587 `
        -UseSsl `
        -Credential $cred `
        -From $user `
        -To $To `
        -Subject $Subject `
        -Body $body `
        -Encoding UTF8

    Write-Output "EMAIL_SENT=true TO=$To"
    exit 0
}
catch {
    Write-Output "ERROR: $_"
    exit 1
}
