@echo off
REM Launch Chrome with remote debugging for LinkedIn/X social media posting
REM Port 9223 (separate from comment engagement on 9222)

echo [OK] Launching Chrome for LinkedIn/X social media posting (port 9223)...

REM CRITICAL: Anti-backgrounding flags prevent JavaScript throttling when window not focused (2025-12-30)
start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" ^
  --remote-debugging-port=9223 ^
  --user-data-dir="%LOCALAPPDATA%\Google\Chrome\User Data\Social_Media_Profile" ^
  --disable-blink-features=AutomationControlled ^
  --disable-backgrounding-occluded-windows ^
  --disable-renderer-backgrounding ^
  --disable-background-timer-throttling ^
  --no-first-run ^
  --no-default-browser-check ^
  "https://linkedin.com/feed" "https://x.com/home"

echo [OK] Chrome launched on port 9223 for social media posting
echo [INFO] Comment engagement runs on port 9222 (separate instance)
echo [INFO] Both Chrome instances can run simultaneously
