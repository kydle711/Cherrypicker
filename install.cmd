@echo off
setlocal

REM Set up variables
set "VENV_DIR=venv"
set "REQUIREMENTS=requirements.txt"
set "TASK_NAME=AutoDownloadChecklists"
set "CMD_SCRIPT=autorunchecklistdownloader.cmd"
set "MAIN_SCRIPT=main.py"
set "LAUNCHER_CMD=launch_autorun.cmd"
set "GUI_SCRIPT=gui.py"
set "VBS_SCRIPT=ChecklistDownloaderGui.vbs"
set "SHORTCUT_NAME=Cherrypicker.lnk"
set "ICON_FILE=assets\cherrypicker.ico"


REM Get current directory (trailing backslash removed)
set "CURRENT_DIR=%~dp0"
set "CURRENT_DIR=%CURRENT_DIR:~0,-1%"
set "DESKTOP=%USERPROFILE%\Desktop"

REM Step 1: Create virtual environment
where python >nul 2>&1 || (
  echo Python not found in PATH. Aborting.
  pause
  exit /b 1
)
echo Creating virtual environment...
python -m venv "%CURRENT_DIR%\%VENV_DIR%" || (
  echo Failed to create virtual environment.
  pause
  exit /b 1
)

REM Step 2: Activate venv and install requirements
echo Installing requirements...
call "%CURRENT_DIR%\%VENV_DIR%\Scripts\activate.bat"
pip install --upgrade pip
pip install -r "%CURRENT_DIR%\%REQUIREMENTS%"

REM Step 3: Create autorunchecklistdownloader.cmd
echo Creating %CMD_SCRIPT%...
echo @echo off > "%CURRENT_DIR%\%CMD_SCRIPT%"
echo "%CURRENT_DIR%\%VENV_DIR%\Scripts\python.exe" "%CURRENT_DIR%\%MAIN_SCRIPT%" >> "%CURRENT_DIR%\%CMD_SCRIPT%"

REM Step 3.5: Create launcher script to enforce correct working dir
echo Creating %LAUNCHER_CMD%...
echo @echo off > "%CURRENT_DIR%\%LAUNCHER_CMD%"
echo cd /d "%CURRENT_DIR%" >> "%CURRENT_DIR%\%LAUNCHER_CMD%"
echo call "%CMD_SCRIPT%" >> "%CURRENT_DIR%\%LAUNCHER_CMD%"

REM Step 4: Schedule daily task at 09:00 AM
echo Creating scheduled task '%TASK_NAME%'...
schtasks /create ^
 /tn "%TASK_NAME%" ^
 /tr "\"%CURRENT_DIR%\%LAUNCHER_CMD%\"" ^
 /sc daily ^
 /st 09:00 ^
 /rl highest ^
 /f

REM Step 5: Create VBS launcher for GUI
echo Creating VBS launcher...
echo Set oShell = CreateObject("WScript.Shell") > "%CURRENT_DIR%\%VBS_SCRIPT%"
echo oShell.CurrentDirectory = "%CURRENT_DIR%" >> "%CURRENT_DIR%\%VBS_SCRIPT%"
echo sPython = "%CURRENT_DIR%\%VENV_DIR%\Scripts\pythonw.exe" >> "%CURRENT_DIR%\%VBS_SCRIPT%"
echo sScript = "%CURRENT_DIR%\%GUI_SCRIPT%" >> "%CURRENT_DIR%\%VBS_SCRIPT%"
echo oShell.Run sPython ^& " " ^& sScript, 0, False >> "%CURRENT_DIR%\%VBS_SCRIPT%"

REM Step 6: Create desktop shortcut with custom icon
echo Creating desktop shortcut...

powershell -NoProfile -Command ^
 "$desktop  = [Environment]::GetFolderPath('Desktop');" ^
 "$target   = Join-Path '%CURRENT_DIR%' '%VBS_SCRIPT%';" ^
 "$iconPath = Join-Path '%CURRENT_DIR%' '%ICON_FILE%';" ^
 "$sc = (New-Object -COM WScript.Shell).CreateShortcut((Join-Path $desktop '%SHORTCUT_NAME%'));" ^
 "$sc.TargetPath       = $target;" ^
 "$sc.WorkingDirectory = '%CURRENT_DIR%';" ^
 "$sc.IconLocation     = $iconPath + ',0';" ^
 "$sc.Save()"

echo Done.
pause

