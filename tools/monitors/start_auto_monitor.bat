@echo off
REM Automatic Stream Monitor Launcher for Windows
REM Runs the monitor continuously in the background

echo ========================================
echo  FOUNDUPS AUTO STREAM MONITOR
echo ========================================
echo.
echo Starting automatic monitoring...
echo Press Ctrl+C to stop
echo.

REM Set Python encoding
set PYTHONIOENCODING=utf-8

REM Run the monitor
python auto_stream_monitor.py

REM If it crashes, restart after 10 seconds
if %errorlevel% neq 0 (
    echo.
    echo Monitor crashed! Restarting in 10 seconds...
    timeout /t 10 /nobreak > nul
    goto :restart
)

:restart
echo Restarting monitor...
python auto_stream_monitor.py
goto :restart