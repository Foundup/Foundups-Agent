@echo off
REM Batch file to schedule automatic OAuth token refresh
REM This can be scheduled with Windows Task Scheduler to run daily

cd /d O:\Foundups-Agent
python modules\platform_integration\youtube_auth\scripts\auto_refresh_tokens.py

REM To schedule this with Windows Task Scheduler:
REM 1. Open Task Scheduler (taskschd.msc)
REM 2. Create Basic Task
REM 3. Name: "YouTube OAuth Token Refresh"
REM 4. Trigger: Daily at 12:00 AM
REM 5. Action: Start this batch file
REM 6. Set to run whether user is logged in or not