# Compatibility entry point; all setup logic lives in installers/.
& "$PSScriptRoot\..\installers\setup-windows.ps1" @args
exit $LASTEXITCODE
