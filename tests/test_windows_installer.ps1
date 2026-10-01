# Run on Windows CI using Windows PowerShell 5.1; no downloads or model execution.
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$ProjectDir = Split-Path -Parent $PSScriptRoot
. "$ProjectDir\installers\windows-common.ps1"

$rejected = $false
try { Invoke-Checked $env:ComSpec @('/c', 'exit 7') } catch { $rejected = $true }
if (-not $rejected) { throw 'Native process failures must stop setup.' }
Invoke-Checked $env:ComSpec @('/c', 'exit 0')

$temporary = Join-Path ([IO.Path]::GetTempPath()) ([guid]::NewGuid().ToString())
New-Item -ItemType Directory $temporary | Out-Null
try {
    # Replace the network call with a tiny local payload.
    function Invoke-WebRequest {
        param([switch]$UseBasicParsing, [string]$Uri, [string]$OutFile)
        [IO.File]::WriteAllText($OutFile, 'fixture')
    }
    $download = Join-Path $temporary 'download'
    $rejected = $false
    try { Get-VerifiedDownload 'https://example.invalid/fixture' $download ('0' * 64) } catch { $rejected = $true }
    if (-not $rejected -or (Test-Path $download)) { throw 'Checksum mismatch must delete the download and abort.' }
    [IO.File]::WriteAllText($download, 'fixture')
    $hash = (Get-FileHash $download -Algorithm SHA256).Hash
    Get-VerifiedDownload 'https://example.invalid/fixture' $download $hash
    if (-not (Test-Path $download)) { throw 'Verified payload missing.' }
    Write-Host 'Windows installer failure/checksum tests passed (no network or inference).'
} finally {
    Remove-Item $temporary -Recurse -Force
}
