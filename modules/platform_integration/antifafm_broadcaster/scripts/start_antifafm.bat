@echo off
REM antifaFM Broadcaster - Windows Startup Script
REM Add to Task Scheduler for auto-start on boot

cd /d O:\Foundups-Agent
python modules\platform_integration\antifafm_broadcaster\scripts\launch.py

pause
