@echo off
setlocal

REM ───────────────────────────────────────────────────────────────
REM  Config – keep in sync with install.cmd
REM ───────────────────────────────────────────────────────────────
set "VENV_DIR=venv"
set "TASK_NAME=AutoDownloadChecklists"
set "CMD_SCRIPT=autorunchecklistdownloader.cmd"
set "LAUNCHER_CMD=launch_autorun.cmd"
set "VBS_SCRIPT=ChecklistDownloaderGui.vbs"
set "SHORTCUT_NAME=Checklist Downloader.lnk"

REM Current project directory (no trailing backslash trim needed here)
set "CURRENT_DIR=%~dp0"
set "DESKTOP=%USERPROFILE%\Desktop"

echo =============================================================
echo  Checklist‑Downloader –  Uninstaller
echo =============================================================
echo This will remove:
echo   - Scheduled Task  :  %TASK_NAME%
echo   - Virtual-env     :  %VENV_DIR%
echo   - Launcher files  :  %CMD_SCRIPT%, %LAUNCHER_CMD%, %VBS_SCRIPT%
echo   - Desktop shortcut:  %SHORTCUT_NAME%
echo.
set /p "_confirm=Type YES and press <Enter> to proceed: "
if /i not "%_confirm%"=="YES" (
    echo Aborted.
    goto :eof
)

REM ───────────────────────────────────────────────────────────────
REM 1) Delete Scheduled Task (ignore error if it’s already gone)
REM ───────────────────────────────────────────────────────────────
echo Removing scheduled task...
schtasks /delete /tn "%TASK_NAME%" /f >nul 2>&1

REM ───────────────────────────────────────────────────────────────
REM 2) Delete desktop shortcut
REM ───────────────────────────────────────────────────────────────
echo Deleting desktop shortcut...
del "%DESKTOP%\%SHORTCUT_NAME%"  >nul 2>&1

REM ───────────────────────────────────────────────────────────────
REM 3) Delete launcher / helper files
REM ───────────────────────────────────────────────────────────────
echo Deleting helper scripts...
for %%F in ("%CMD_SCRIPT%" "%LAUNCHER_CMD%" "%VBS_SCRIPT%") do (
    if exist "%%~fF" del "%%~fF"
)

REM ───────────────────────────────────────────────────────────────
REM 4) Remove virtual environment
REM ───────────────────────────────────────────────────────────────
echo Removing virtual environment...
rmdir /s /q "%VENV_DIR%" 2>nul

echo.
echo Cleanup complete.
pause
