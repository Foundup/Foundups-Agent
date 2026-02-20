@echo off
REM Kill all Chrome processes
echo Closing all Chrome instances...
taskkill /F /IM chrome.exe /T 2>nul

REM Wait for processes to close
timeout /t 2 /nobreak >nul

REM Launch Chrome with remote debugging
REM CRITICAL: Anti-backgrounding flags prevent JavaScript throttling when window not focused (2025-12-30)
REM FIX: --no-restore-session-state prevents Chrome from restoring previous tabs after force-kill (2026-01-18)
echo Launching Chrome with remote debugging on port 9222 (anti-backgrounding enabled)...
start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="O:/Foundups-Agent/modules/platform_integration/youtube_auth/data/chrome_profile_move2japan" --disable-backgrounding-occluded-windows --disable-renderer-backgrounding --disable-background-timer-throttling --no-restore-session-state "https://studio.youtube.com/channel/UC-LSSlOZwpGIRIYihaz8zCw/comments/inbox"

echo.
echo Chrome launched with remote debugging on port 9222
echo Navigate to YouTube Studio comments page if not already there
echo.
echo Press any key when ready to run the test...
pause >nul
