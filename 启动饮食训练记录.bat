@echo off
setlocal
set "APP_DIR=%~dp0"
set "NODE_EXE="

where node.exe >nul 2>nul
if not errorlevel 1 set "NODE_EXE=node.exe"
if not defined NODE_EXE if exist "%ProgramFiles%\nodejs\node.exe" set "NODE_EXE=%ProgramFiles%\nodejs\node.exe"
if not defined NODE_EXE if exist "%LocalAppData%\Programs\nodejs\node.exe" set "NODE_EXE=%LocalAppData%\Programs\nodejs\node.exe"

if not defined NODE_EXE (
  echo Node.js was not found. Install Node.js and try again.
  pause
  exit /b 1
)

set "JOURNAL_APP_DIR=%APP_DIR%"
set "JOURNAL_NODE_EXE=%NODE_EXE%"
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -Command "$scriptPath = Join-Path $env:JOURNAL_APP_DIR ([string][char]0x542F + [char]0x52A8 + '.ps1'); & $scriptPath -AppDirectory $env:JOURNAL_APP_DIR -NodeExecutable $env:JOURNAL_NODE_EXE"
if errorlevel 1 (
  echo The local website could not be opened. Review the error above.
  pause
)
endlocal
