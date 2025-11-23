#!/bin/bash
# Firebase Setup Script for GotJunk Cross-Device Sync
# WSP 98: FoundUps Mesh-Native Architecture Protocol - Layer 2
#
# Prerequisites:
#   - Firebase CLI installed: npm install -g firebase-tools
#   - Authenticated: firebase login
#   - gcloud authenticated: gcloud auth login
#
# Usage: ./setup_firebase.sh

set -e

PROJECT_ID="gen-lang-client-0061781628"
APP_NAME="GotJunk PWA"

echo "========================================"
echo "Firebase Setup for GotJunk"
echo "Project: $PROJECT_ID"
echo "========================================"

# Check if Firebase CLI is installed
if ! command -v firebase &> /dev/null; then
    echo "Firebase CLI not found. Installing..."
    npm install -g firebase-tools
fi

# Login to Firebase (if not already)
echo ""
echo "Step 1: Checking Firebase authentication..."
firebase login --no-localhost || echo "Already logged in"

# Set project
echo ""
echo "Step 2: Setting Firebase project..."
firebase use $PROJECT_ID

# Check if web app exists, if not create one
echo ""
echo "Step 3: Checking/Creating Firebase Web App..."
EXISTING_APPS=$(firebase apps:list --project=$PROJECT_ID 2>/dev/null || echo "")

if echo "$EXISTING_APPS" | grep -q "WEB"; then
    echo "Web app already exists."
else
    echo "Creating new Firebase Web App..."
    firebase apps:create WEB "$APP_NAME" --project=$PROJECT_ID
fi

# Get SDK config
echo ""
echo "Step 4: Getting Firebase SDK Config..."
echo ""
echo "========================================"
echo "FIREBASE WEB CONFIG (copy these to .env):"
echo "========================================"
firebase apps:sdkconfig WEB --project=$PROJECT_ID

echo ""
echo "========================================"
echo "Copy the values above to your .env file:"
echo "  VITE_FIREBASE_API_KEY=<apiKey>"
echo "  VITE_FIREBASE_APP_ID=<appId>"
echo "  VITE_FIREBASE_SENDER_ID=<messagingSenderId>"
echo "========================================"

# Deploy Firestore rules
echo ""
echo "Step 5: Deploying Firestore Security Rules..."
cd "$(dirname "$0")/.."
firebase deploy --only firestore:rules --project=$PROJECT_ID

# Deploy Storage rules
echo ""
echo "Step 6: Deploying Storage Security Rules..."
firebase deploy --only storage:rules --project=$PROJECT_ID

# Create Firestore indexes
echo ""
echo "Step 7: Creating Firestore Indexes..."
firebase deploy --only firestore:indexes --project=$PROJECT_ID

echo ""
echo "========================================"
echo "Firebase Setup Complete!"
echo ""
echo "Next steps:"
echo "1. Copy the Firebase config to Cloud Run env vars"
echo "2. Test cross-device sync on multiple phones"
echo "========================================"
