@echo off
echo Launching Chrome with remote debugging for YouTube Live Chat...
echo.

REM Kill any existing Chrome processes
taskkill /F /IM chrome.exe /T >nul 2>&1

REM Wait a moment
timeout /t 2 /nobreak >nul

REM Launch Chrome with remote debugging on port 9223 (separate from Studio instance)
REM Opens to @Move2Japan live stream (auto-redirects to current live if streaming)
REM CRITICAL: Anti-backgrounding flags prevent JavaScript throttling when window not focused (2025-12-30)
REM FIX: --no-restore-session-state prevents Chrome from restoring previous tabs after force-kill (2026-01-18)
echo Launching Chrome on port 9223 for live chat monitoring (anti-backgrounding enabled)...
start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9223 --user-data-dir="O:/Foundups-Agent/modules/platform_integration/youtube_auth/data/chrome_profile_move2japan" --disable-backgrounding-occluded-windows --disable-renderer-backgrounding --disable-background-timer-throttling --no-restore-session-state "https://www.youtube.com/@Move2Japan/live"

echo.
echo Chrome launched with remote debugging on port 9223
echo URL: https://www.youtube.com/@Move2Japan/live
echo.
echo If Move2Japan is live, you'll see the stream with live chat iframe.
echo If not live, page will show channel videos.
echo.
echo This instance is for:
echo - !party reactions (party_reactor.py)
echo - Future: Direct chat injection with UI-TARS
echo.
echo Press any key when ready...
pause >nul
