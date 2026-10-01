param(
    [ValidateSet('en', 'zh', 'zh-Hant', 'ja', 'ko')][string]$Language = '',
    [ValidateSet('auto', 'safe', 'cpu')][string]$Profile = 'auto',
    [switch]$NonInteractive
)
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$ProjectDir = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectDir
. "$PSScriptRoot\windows-common.ps1"
New-Item -ItemType Directory -Force -Path '.lecturebridge', '.tools' | Out-Null
$transcribing = $false
try {
    Start-Transcript -Path '.lecturebridge\setup.log' -Force | Out-Null
    $transcribing = $true
    if (-not [Environment]::Is64BitProcess -or $env:PROCESSOR_ARCHITECTURE -ne 'AMD64') {
        throw 'Use Windows 10/11 x86-64 and 64-bit PowerShell. ARM Windows is not supported.'
    }
    Set-Content '.lecturebridge\installing' 'Setup is in progress.'
    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
    $ProgressPreference = 'SilentlyContinue'
    $UvVersion = '0.12.13'
    $UvDir = Join-Path $ProjectDir ".tools\uv-$UvVersion"
    $UvExe = Join-Path $UvDir 'uv.exe'
    if (-not (Test-Path $UvExe)) {
        New-Item -ItemType Directory -Force -Path $UvDir | Out-Null
        $archive = Join-Path $UvDir 'uv.zip'
        Get-VerifiedDownload -Url "https://github.com/astral-sh/uv/releases/download/$UvVersion/uv-x86_64-pc-windows-msvc.zip" -Destination $archive -Sha256 'a86c9dc7bad9b03f388583b7187c05fe9951c2e0d392217e8fd43d97787f6ec2'
        Expand-Archive -Path $archive -DestinationPath $UvDir -Force
        if (-not (Test-Path $UvExe)) { throw 'uv.exe was missing from the verified archive.' }
        Remove-Item $archive -Force
    }
    Install-VCRuntime
    $env:UV_PYTHON_INSTALL_DIR = Join-Path $ProjectDir '.tools\python'
    $env:UV_PROJECT_ENVIRONMENT = Join-Path $ProjectDir '.venv'
    $env:UV_PYTHON_PREFERENCE = 'only-managed'
    $env:UV_PYTHON_NO_REGISTRY = '1'
    $env:PYTHONIOENCODING = 'utf-8'
    Invoke-Checked $UvExe @('python', 'install', '--no-bin', '--no-registry', '3.12')
    $PythonExe = Join-Path $ProjectDir '.venv\Scripts\python.exe'
    if (-not (Test-Path $PythonExe)) {
        Invoke-Checked $UvExe @('venv', '--python', '3.12', '.venv')
    }
    $planArgs = @('installers/setup.py', 'plan', '--profile', $Profile)
    if ($Language) { $planArgs += @('--language', $Language) }
    if ($NonInteractive) { $planArgs += '--non-interactive' }
    Invoke-Checked $PythonExe $planArgs
    $state = Get-Content '.lecturebridge\install.json' -Raw | ConvertFrom-Json
    $syncArgs = @('sync', '--locked', '--no-dev', '--python', '3.12')
    if ($state.windows_cuda) { $syncArgs += @('--extra', 'windows-cuda') }
    Invoke-Checked $UvExe $syncArgs
    Invoke-Checked $PythonExe @('installers/setup.py', 'complete')
    Remove-Item '.lecturebridge\installing'
    exit 0
} catch {
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host 'Setup did not complete. Review .lecturebridge\setup.log and rerun Install.cmd.'
    exit 1
} finally {
    if ($transcribing) { Stop-Transcript | Out-Null }
}
