@echo off
echo Launching Chrome with remote debugging for YouTube Studio...
echo.

REM Kill any existing Chrome processes
taskkill /F /IM chrome.exe /T >nul 2>&1

REM Wait a moment
timeout /t 2 /nobreak >nul

REM Launch Chrome with remote debugging
REM CRITICAL: Anti-backgrounding flags prevent JavaScript throttling when window not focused (2025-12-30)
start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="%LOCALAPPDATA%\Google\Chrome\User Data" --disable-backgrounding-occluded-windows --disable-renderer-backgrounding --disable-background-timer-throttling "https://studio.youtube.com/channel/UC-LSSlOZwpGIRIYihaz8zCw/comments/inbox?filter=%%5B%%7B%%22isDisabled%%22%%3Afalse%%2C%%22isPinned%%22%%3Atrue%%2C%%22name%%22%%3A%%22SORT_BY%%22%%2C%%22value%%22%%3A%%22SORT_BY_MOST_RELEVANT%%22%%7D%%2C%%7B%%22name%%22%%3A%%22ENGAGED_STATUS%%22%%2C%%22value%%22%%3A%%5B%%22COMMENT_CATEGORY_NOT_ENGAGED%%22%%5D%%7D%%2C%%7B%%22name%%22%%3A%%22PARENT_ENTITY_CONTENT_TYPE%%22%%2C%%22value%%22%%3A%%5B%%22PARENT_ENTITY_CONTENT_TYPE_WATCH%%22%%2C%%22PARENT_ENTITY_CONTENT_TYPE_SHORT%%22%%2C%%22PARENT_ENTITY_CONTENT_TYPE_CREATOR_POST%%22%%5D%%7D%%5D"

echo.
echo Chrome is starting with remote debugging on port 9222...
echo Please wait 10 seconds for it to fully load...
timeout /t 10 /nobreak

echo.
echo Ready! You can now run the autonomous engagement script.
