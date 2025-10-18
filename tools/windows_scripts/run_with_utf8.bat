@echo off
REM Run with UTF-8 encoding on Windows
REM This fixes emoji and special character display issues

REM Set console to UTF-8 code page
chcp 65001 >nul 2>&1

REM Set Python environment to UTF-8
set PYTHONIOENCODING=utf-8
set PYTHONLEGACYWINDOWSSTDIO=utf-8

REM Clear screen for clean start
cls

echo ========================================
echo 0102 FoundUps Agent - UTF-8 Mode
echo ========================================
echo.
echo Console set to UTF-8 (code page 65001)
echo Python encoding: UTF-8
echo.

REM Run main program with arguments
if "%1"=="" (
    REM No arguments - run interactive
    python main.py
) else (
    REM Pass all arguments to main.py
    python main.py %*
)