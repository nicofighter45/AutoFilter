@echo off
cls
set /p userInput=Enter the libraries: 
pip install %userInput% --proxy=http://11.56.30.169:3142 --trusted-host pypi.org --trusted-host files.pythonhost
if %errorlevel% neq 0 (
    echo Installation failed. Please check the library names and your proxy settings.
) else (
    echo Installation successful.
)
pause
