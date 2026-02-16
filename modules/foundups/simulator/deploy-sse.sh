#!/bin/bash
# Deploy SSE Server to Cloud Run
#
# Prerequisites:
#   - gcloud CLI installed and authenticated
#   - Firebase project: foundupscom
#
# Usage:
#   ./deploy-sse.sh

set -e

PROJECT_ID="gen-lang-client-0061781628"
SERVICE_NAME="sse-foundups"
REGION="us-central1"

echo "Deploying SSE Server to Cloud Run..."
echo "Project: $PROJECT_ID"
echo "Service: $SERVICE_NAME"
echo "Region: $REGION"

# Navigate to simulator directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Deploy to Cloud Run
gcloud run deploy $SERVICE_NAME \
    --source . \
    --project $PROJECT_ID \
    --region $REGION \
    --platform managed \
    --allow-unauthenticated \
    --port 8080 \
    --memory 256Mi \
    --min-instances 0 \
    --max-instances 2 \
    --timeout 300s \
    --set-env-vars "PYTHONUNBUFFERED=1"

# Get service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME \
    --project $PROJECT_ID \
    --region $REGION \
    --format "value(status.url)")

echo ""
echo "Deployment complete!"
echo "Service URL: $SERVICE_URL"
echo ""
echo "SSE endpoint: $SERVICE_URL/api/sim-events"
echo "Health check: $SERVICE_URL/api/health"
echo ""
echo "To test locally with this endpoint:"
echo "  https://foundups.com/?sse=1&sse_url=$SERVICE_URL/api/sim-events"
echo ""
echo "Firebase Hosting will proxy /api/sim-events to this Cloud Run service."
