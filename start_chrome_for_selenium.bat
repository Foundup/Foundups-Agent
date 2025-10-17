@echo off
REM Start Chrome with remote debugging for Selenium to connect
REM This allows Selenium to reuse the browser window instead of opening new ones

echo Starting Chrome with remote debugging enabled...
echo This browser window can be reused by Selenium
echo.

REM Use the same profile as Selenium
set PROFILE_DIR=O:\Foundups-Agent\modules\platform_integration\x_twitter\data\chrome_profile_foundups

REM Start Chrome with debugging port
start chrome.exe ^
  --remote-debugging-port=9222 ^
  --user-data-dir="%PROFILE_DIR%" ^
  --profile-directory=Default ^
  --disable-blink-features=AutomationControlled ^
  --window-size=1920,1080 ^
  https://x.com/home

echo.
echo Chrome started with debugging on port 9222
echo Selenium can now connect to this window
echo.
echo DO NOT CLOSE THIS TERMINAL while using Selenium
pause
