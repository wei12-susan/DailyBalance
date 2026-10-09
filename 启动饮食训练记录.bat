@echo off
setlocal
set "APP_DIR=%~dp0"
set "NODE_EXE="

where node.exe >nul 2>nul
if not errorlevel 1 set "NODE_EXE=node.exe"
if not defined NODE_EXE if exist "%ProgramFiles%\nodejs\node.exe" set "NODE_EXE=%ProgramFiles%\nodejs\node.exe"
if not defined NODE_EXE if exist "%LocalAppData%\Programs\nodejs\node.exe" set "NODE_EXE=%LocalAppData%\Programs\nodejs\node.exe"

if not defined NODE_EXE (
  echo 未找到 Node.js。当前本地网页服务需要 Node.js。
  echo 请把此提示发给我，我会提供不依赖 Node.js 的版本。
  pause
  exit /b 1
)

powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%APP_DIR%启动.ps1" -AppDirectory "%APP_DIR%" -NodeExecutable "%NODE_EXE%"
if errorlevel 1 (
  echo 网页启动失败，请把上方错误提示发给我。
  pause
)
endlocal
