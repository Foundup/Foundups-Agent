@echo off
rem Navigate to project root (4 levels up from this batch file)
cd /d "%~dp0\..\..\..\..\..\"
set PYTHONIOENCODING=utf-8
set PYTHONUNBUFFERED=1
echo Starting WRE with UTF-8 encoding...
echo Current directory: %CD%
python -m modules.wre_core.src.main --directive "Test from batch script" --autonomous
echo.
echo Exit code: %ERRORLEVEL%
pause