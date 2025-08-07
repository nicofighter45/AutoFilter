@echo off
REM Check if Python is installed
python --version >nul 2>&1
IF %ERRORLEVEL% EQU 0 (
    echo Python is installed.
    echo Upgrading to the latest version...
    python -m pip install --upgrade pip
    python -m pip install --upgrade python
) ELSE (
    echo Python is not installed.
    echo Downloading Python installer...
    curl -o python-installer.exe https://www.python.org/ftp/python/3.12.3/python-3.12.3-amd64.exe
    echo Running Python installer...
    start /wait python-installer.exe /quiet InstallAllUsers=1 PrependPath=1
    del python-installer.exe
    echo Python installation complete.
)

REM Cloning git repository
echo Cloning Git repository...
git --version >nul 2>&1
IF %ERRORLEVEL% EQU 0 (
    git clone https://github.com/nicofighter45/AutoFilter.git
) ELSE (
    echo Git is not installed.
    echo Downloading Git installer...
    curl -o git-installer.exe https://github.com/git-for-windows/git/releases/download/v2.45.2.windows.1/Git-2.45.2-64-bit.exe
    echo Running Git installer...
    start /wait git-installer.exe /VERYSILENT /NORESTART
    del git-installer.exe
    echo Git installation complete.
    git clone https://github.com/nicofighter45/AutoFilter.git
)
REM Create shortcut to main.py on Desktop
set "DESKTOP=%USERPROFILE%\Desktop"
set "SHORTCUT=%DESKTOP%\AutoFilter.lnk"
set "TARGET=%CD%\AutoFilter\main.py"

REM Use PowerShell to create the shortcut
powershell -Command "$s=(New-Object -COM WScript.Shell).CreateShortcut('%SHORTCUT%');$s.TargetPath='python';$s.Arguments='\"%TARGET%\"';$s.WorkingDirectory='%CD%\AutoFilter';$s.Save()"
REM Launching main.py
cd AutoFilter
python main.py
