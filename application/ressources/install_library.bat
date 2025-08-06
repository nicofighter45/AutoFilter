@echo off
cls
set /p userInput=Enter the libraries: 
pip install %userInput% --proxy proxy_amer.safran:9009
if %errorlevel% neq 0 (
    echo Installation failed. Please check the library names and your proxy settings.
) else (
    echo Installation successful.
)
pause