@echo off
REM GotJUNK? Cloud Run Deployment Script (Windows)
REM Deploys to: https://gotjunk-56566376153.us-west1.run.app

echo.
echo 🚀 GotJUNK? Cloud Run Deployment
echo ==================================
echo.

REM Configuration
set PROJECT_ID=gen-lang-client-0061781628
set SERVICE_NAME=gotjunk
set REGION=us-west1
set CLOUD_RUN_URL=https://gotjunk-56566376153.us-west1.run.app

REM Navigate to frontend directory
set SCRIPT_DIR=%~dp0
set FRONTEND_DIR=%SCRIPT_DIR%..\frontend

echo 📂 Frontend directory: %FRONTEND_DIR%
echo 🔧 Project ID: %PROJECT_ID%
echo 📍 Region: %REGION%
echo 🌐 Service: %SERVICE_NAME%
echo.

REM Check if gcloud is installed
where gcloud >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo ❌ ERROR: gcloud CLI not found
    echo.
    echo Install gcloud CLI:
    echo   https://cloud.google.com/sdk/docs/install
    echo.
    exit /b 1
)

REM Set project
echo 🔑 Setting project: %PROJECT_ID%
gcloud config set project %PROJECT_ID%

REM Build frontend
echo.
echo 🔨 Building frontend...
cd /d "%FRONTEND_DIR%"
call npm run build

if not exist "dist" (
    echo ❌ ERROR: Build failed - dist directory not found
    exit /b 1
)

echo ✅ Build successful

REM Deploy to Cloud Run
echo.
echo 🚀 Deploying to Cloud Run...
echo    Service: %SERVICE_NAME%
echo    Region: %REGION%
echo.

gcloud run deploy %SERVICE_NAME% ^
  --source . ^
  --region %REGION% ^
  --platform managed ^
  --allow-unauthenticated ^
  --set-env-vars "GEMINI_API_KEY_GotJunk=%GEMINI_API_KEY_GotJunk%"

if %ERRORLEVEL% equ 0 (
    echo.
    echo ✅ Deployment successful!
    echo.
    echo 🌐 Your app is live at:
    echo    %CLOUD_RUN_URL%
    echo.
    echo 📊 View logs and metrics:
    echo    https://console.cloud.google.com/run/detail/%REGION%/%SERVICE_NAME%/observability/metrics?project=%PROJECT_ID%
    echo.
) else (
    echo.
    echo ❌ Deployment failed
    exit /b 1
)
