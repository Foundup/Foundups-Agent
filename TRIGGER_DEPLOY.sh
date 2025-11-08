#!/bin/bash
# Manual deployment trigger for GotJunk
# This forces Cloud Build to use the latest main branch code

echo "🚀 Triggering GotJunk deployment to Cloud Run..."
echo "Current commit: $(git rev-parse HEAD)"
echo ""

# Deploy using Cloud Build
gcloud builds submit \
  --config=modules/foundups/gotjunk/cloudbuild.yaml \
  --substitutions=COMMIT_SHA=$(git rev-parse --short HEAD) \
  .

echo ""
echo "✅ Build submitted!"
echo "Monitor at: https://console.cloud.google.com/cloud-build/builds"
echo ""
echo "Once complete, check: https://gotjunk.foundups.com/"
