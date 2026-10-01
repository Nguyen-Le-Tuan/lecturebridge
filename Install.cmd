@echo off
setlocal
cd /d "%~dp0"
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0installers\setup-windows.ps1" %*
set "result=%ERRORLEVEL%"
if not "%result%"=="0" echo Setup failed. See .lecturebridge\setup.log for details.
pause
exit /b %result%
