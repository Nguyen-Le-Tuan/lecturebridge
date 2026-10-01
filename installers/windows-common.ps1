Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Invoke-Checked {
    param([string]$Executable, [string[]]$Arguments)
    & $Executable @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Command failed (exit $LASTEXITCODE): $Executable $($Arguments -join ' ')"
    }
}

function Get-VerifiedDownload {
    param([string]$Url, [string]$Destination, [string]$Sha256)
    Invoke-WebRequest -UseBasicParsing -Uri $Url -OutFile $Destination
    if ($Sha256 -and (Get-FileHash $Destination -Algorithm SHA256).Hash -ne $Sha256) {
        Remove-Item $Destination -Force
        throw "Download checksum mismatch. Retry setup; do not run the downloaded file."
    }
}

function Install-VCRuntime {
    $runtime = Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\VisualStudio\14.0\VC\Runtimes\x64" -ErrorAction SilentlyContinue
    if ($runtime -and $runtime.Installed -eq 1 -and ([version]$runtime.Version.TrimStart('v')) -ge [version]'14.40') {
        return
    }
    Write-Host "Installing the Microsoft Visual C++ x64 runtime. Windows may request administrator permission."
    $installer = Join-Path $ProjectDir ".tools\vc_redist.x64.exe"
    Get-VerifiedDownload -Url "https://aka.ms/vc14/vc_redist.x64.exe" -Destination $installer
    $signature = Get-AuthenticodeSignature $installer
    if ($signature.Status -ne 'Valid' -or $signature.SignerCertificate.Subject -notmatch 'O=Microsoft Corporation(?:,|$)') {
        Remove-Item $installer -Force
        throw "The Visual C++ installer does not have a valid Microsoft signature."
    }
    $process = Start-Process -FilePath $installer -ArgumentList '/install /passive /norestart' -Verb RunAs -Wait -PassThru
    if ($process.ExitCode -eq 3010) {
        throw "Windows requires a restart to finish installing Visual C++. Restart when convenient, then run Install.cmd again."
    }
    if ($process.ExitCode -ne 0) {
        throw "Visual C++ installation failed or was cancelled (exit $($process.ExitCode))."
    }
    Remove-Item $installer -Force
}
