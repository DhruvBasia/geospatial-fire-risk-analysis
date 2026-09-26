@echo off
echo Starting Seelampur Fire Risk Map...
echo.
python -m http.server 8000 --directory "%~dp0"
pause
