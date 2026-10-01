@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Run Install.cmd first.
  pause
  exit /b 1
)
set "PYTHONIOENCODING=utf-8"
".venv\Scripts\python.exe" installers\setup.py launch %*
set "result=%ERRORLEVEL%"
pause
exit /b %result%
