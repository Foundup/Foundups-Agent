@echo off
echo Launching Edge with remote debugging for FoundUps (port 9223)...
echo.

REM Launch Edge with remote debugging
REM CRITICAL: Anti-backgrounding flags prevent JavaScript throttling when window not focused
REM FIX: --no-restore-session-state prevents Edge from restoring previous tabs after force-kill (2026-01-18)
start "" "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" --remote-debugging-port=9223 --user-data-dir="%LOCALAPPDATA%\Microsoft\Edge\User Data" --disable-backgrounding-occluded-windows --disable-renderer-backgrounding --disable-background-timer-throttling --no-restore-session-state "https://studio.youtube.com/channel/UCSNTUXjAgpd4sgWYP0xoJgw/videos/upload"

echo.
echo Edge is starting with remote debugging on port 9223...
echo Please wait 10 seconds for it to fully load...
timeout /t 10 /nobreak

echo.
echo Ready! You can now run FoundUps automation:
echo   - YouTube Indexing: main.py menu 1 option 8 then s3
echo   - Comment Engagement: python run_skill.py --browser-port 9223
