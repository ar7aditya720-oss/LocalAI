@echo off
chcp 65001 > nul

:: Launch browser watcher in background - it polls /api/health before opening
start "" /B python "%~dp0browser_watcher.py"

:: Run the server in this terminal (all logs visible here)
python "%~dp0localai.py" %*
