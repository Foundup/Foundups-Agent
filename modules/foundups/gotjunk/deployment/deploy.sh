#!/bin/bash
# GotJUNK? Cloud Run Deployment Script
# Deploys to: https://gotjunk-56566376153.us-west1.run.app

set -e

echo "🚀 GotJUNK? Cloud Run Deployment"
echo "=================================="
echo ""

# Configuration
PROJECT_ID="gen-lang-client-0061781628"
SERVICE_NAME="gotjunk"
REGION="us-west1"
CLOUD_RUN_URL="https://gotjunk-56566376153.us-west1.run.app"

# Navigate to frontend directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FRONTEND_DIR="$SCRIPT_DIR/../frontend"

echo "📂 Frontend directory: $FRONTEND_DIR"
echo "🔧 Project ID: $PROJECT_ID"
echo "📍 Region: $REGION"
echo "🌐 Service: $SERVICE_NAME"
echo ""

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ ERROR: gcloud CLI not found"
    echo ""
    echo "Install gcloud CLI:"
    echo "  https://cloud.google.com/sdk/docs/install"
    echo ""
    exit 1
fi

# Check if authenticated
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" &> /dev/null; then
    echo "⚠️  Not authenticated with gcloud"
    echo "Running: gcloud auth login"
    gcloud auth login
fi

# Set project
echo "🔑 Setting project: $PROJECT_ID"
gcloud config set project $PROJECT_ID

# Build frontend
echo ""
echo "🔨 Building frontend..."
cd "$FRONTEND_DIR"
npm run build

if [ ! -d "dist" ]; then
    echo "❌ ERROR: Build failed - dist/ directory not found"
    exit 1
fi

echo "✅ Build successful"

# Deploy to Cloud Run
echo ""
echo "🚀 Deploying to Cloud Run..."
echo "   Service: $SERVICE_NAME"
echo "   Region: $REGION"
echo ""

gcloud run deploy $SERVICE_NAME \
  --source . \
  --region $REGION \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars "GEMINI_API_KEY_GotJunk=$GEMINI_API_KEY_GotJunk"

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Deployment successful!"
    echo ""
    echo "🌐 Your app is live at:"
    echo "   $CLOUD_RUN_URL"
    echo ""
    echo "📊 View logs and metrics:"
    echo "   https://console.cloud.google.com/run/detail/$REGION/$SERVICE_NAME/observability/metrics?project=$PROJECT_ID"
    echo ""
else
    echo ""
    echo "❌ Deployment failed"
    exit 1
fi
