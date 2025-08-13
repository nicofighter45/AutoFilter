@echo off
set "PROXY_URL=http://11.56.30.169:3142"
REM Check if Python is installed
python --version >nul 2>&1
IF %ERRORLEVEL% EQU 0 (
    echo Python is installed.
    echo Upgrading to the latest version...
    python -m pip install --upgrade pip --proxy=http://11.56.30.169:3142 --trusted-host pypi.org --trusted-host files.pythonhost
    python -m pip install --upgrade python --proxy=http://11.56.30.169:3142 --trusted-host pypi.org --trusted-host files.pythonhost
) ELSE (
    echo Python is not installed.
    echo Downloading Python installer...
    
    curl -x %PROXY_URL% -o python-installer.exe https://www.python.org/ftp/python/3.12.3/python-3.12.3-amd64.exe 
    echo Running Python installer...
    start /wait python-installer.exe /quiet InstallAllUsers=1 PrependPath=1
    del python-installer.exe
    echo Python installation complete.
)

REM Cloning git repository
echo Cloning Git repository...
git --version >nul 2>&1
IF %ERRORLEVEL% EQU 0 (
    git config --global http.proxy %PROXY_URL%
    git clone https://github.com/nicofighter45/AutoFilter.git
) ELSE (
    echo Git is not installed.
    echo Downloading Git installer...
    curl -x %PROXY_URL% -o git-installer.exe https://github.com/git-for-windows/git/releases/download/v2.45.2.windows.1/Git-2.45.2-64-bit.exe
    echo Running Git installer...
    start /wait git-installer.exe /VERYSILENT /NORESTART
    del git-installer.exe
    echo Git installation complete.
    git config --global http.proxy %PROXY_URL%
    git clone https://github.com/nicofighter45/AutoFilter.git
)

cd AutoFilter

REM Create the shortcuts to the Destop
set "DESKTOP=%USERPROFILE%\Desktop"
set "SHORTCUT=%DESKTOP%\AutoFilter.lnk"
set "TARGET=%CD%\application\src\application.py"
powershell -Command "$s=(New-Object -COM WScript.Shell).CreateShortcut('%SHORTCUT%');$s.TargetPath='python';$s.Arguments='\"%TARGET%\"';$s.WorkingDirectory='%CD%\AutoFilter';$s.Save()"

set "SHORTCUT=%DESKTOP%\Tesseract.lnk"
set "TARGET=%CD%\application\ressources\tesseract-ocr-w64-setup-5.5.0.20241111.exe"
powershell -Command "$s=(New-Object -COM WScript.Shell).CreateShortcut('%SHORTCUT%');$s.TargetPath='%TARGET%\';$s.WorkingDirectory='%CD%\AutoFilter';$s.Save()"

set "SHORTCUT=%DESKTOP%\Auto Filter Configuration.lnk"
set "TARGET=%CD%\application\src\constants\"
powershell -Command "$s=(New-Object -COM WScript.Shell).CreateShortcut('%SHORTCUT%');$s.TargetPath='%TARGET%';$s.WorkingDirectory='%CD%\AutoFilter';$s.Save()"


REM Check if Tesseract is already installed
if exist "C:\Program Files\Tesseract-OCR\tesseract.exe" (
    echo Tesseract is already installed.
) else (
    echo Tesseract is not installed. Installing...
    set INSTALLER="%CD%\application\ressources\tesseract-ocr-w64-setup-5.5.0.20241111.exe"
    %INSTALLER% /S /v"/qn"
    setx /M PATH "%PATH%;C:\Program Files\Tesseract-OCR\tesseract.exe"
)

REM Launching main.py
cd AutoFilter
python main.py

pause

REM Delete this batch file
del "%~f0"