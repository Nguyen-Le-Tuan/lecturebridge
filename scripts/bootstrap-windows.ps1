$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$ProjectDir = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectDir

if (-not [Environment]::Is64BitOperatingSystem) {
    throw "LectureBridge supports 64-bit Windows only."
}

if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Host "uv was not found; installing it with Astral's official installer."
    Invoke-RestMethod https://astral.sh/uv/install.ps1 | Invoke-Expression
    $UvBin = Join-Path $env:USERPROFILE ".local\bin"
    if (Test-Path $UvBin) {
        $env:PATH = "$UvBin;$env:PATH"
    }
}

if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    throw "uv installation completed but uv is not available in this terminal. Open a new PowerShell window and run this script again."
}

$NvidiaSmi = Get-Command nvidia-smi -ErrorAction SilentlyContinue
if ($NvidiaSmi) {
    & $NvidiaSmi.Source --query-gpu=name,memory.total,driver_version --format=csv,noheader
} else {
    Write-Warning "nvidia-smi was not found. LectureBridge will use the CPU fallback."
}

$RequiredDlls = @("cublas64_12.dll", "cudnn64_9.dll", "cudnn_ops64_9.dll")
$PathDirectories = $env:PATH -split ";" | Where-Object { $_ }
$MissingDlls = foreach ($Dll in $RequiredDlls) {
    $Found = $false
    foreach ($Directory in $PathDirectories) {
        if (Test-Path (Join-Path $Directory $Dll)) {
            $Found = $true
            break
        }
    }
    if (-not $Found) { $Dll }
}
if ($NvidiaSmi -and $MissingDlls) {
    Write-Warning "NVIDIA GPU detected, but required CUDA DLLs are missing from PATH: $($MissingDlls -join ', '). Install CUDA 12 and cuDNN 9."
}

$VcRuntime = Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\VisualStudio\14.0\VC\Runtimes\x64" -ErrorAction SilentlyContinue
if (-not $VcRuntime -or -not $VcRuntime.Installed) {
    Write-Warning "Microsoft Visual C++ 2015-2022 x64 Redistributable was not detected. CTranslate2 may not load without it."
}

uv sync --locked
uv run lecturebridge-models download --model distil-large-v3.5

Write-Host ""
Write-Host "Running readiness checks. Tailscale must already be installed and signed in."
uv run lecturebridge-preflight --device auto
