# GotJUNK? - Cloud Deployment Guide

## Prerequisites

1. **Google Cloud Project** with billing enabled
2. **GitHub Repository** connected to Cloud Build
3. **APIs Enabled**:
   - Cloud Build API
   - Cloud Run API
   - Container Registry API
   - Secret Manager API

## Setup Steps

### 1. Create Secret for Gemini API Key

```bash
# Create secret in Secret Manager
gcloud secrets create GEMINI_API_KEY_GOTJUNK \
  --data-file=- <<< "your-gemini-api-key-here"

# Grant Cloud Run access to the secret
gcloud secrets add-iam-policy-binding GEMINI_API_KEY_GOTJUNK \
  --member="serviceAccount:PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

### 2. Set Up Cloud Build Trigger

**Option A: Via gcloud CLI**
```bash
gcloud builds triggers create github \
  --name="gotjunk-deploy" \
  --repo-name="Foundups-Agent" \
  --repo-owner="YOUR_GITHUB_USERNAME" \
  --branch-pattern="^main$" \
  --build-config="modules/foundups/gotjunk/cloudbuild.yaml" \
  --included-files="modules/foundups/gotjunk/**"
```

**Option B: Via GCP Console**
1. Go to Cloud Build → Triggers
2. Click "Create Trigger"
3. Connect your GitHub repository
4. Configure:
   - Name: `gotjunk-deploy`
   - Event: Push to branch
   - Source: `^main$`
   - Build configuration: `modules/foundups/gotjunk/cloudbuild.yaml`
   - Included files filter: `modules/foundups/gotjunk/**`

### 3. Deploy

**Manual Deployment:**
```bash
# From repo root
gcloud builds submit \
  --config=modules/foundups/gotjunk/cloudbuild.yaml \
  .
```

**Automatic Deployment:**
```bash
# Commit and push changes
git add modules/foundups/gotjunk/
git commit -m "feat(gotjunk): Deploy to Cloud Run with mobile support"
git push origin main

# Cloud Build trigger will automatically deploy
```

### 4. Get Service URL

```bash
gcloud run services describe gotjunk \
  --region=us-west1 \
  --format='value(status.url)'
```

Example output: `https://gotjunk-XXXXXXXXXX-uw.a.run.app`

## Mobile Testing

### iOS Safari
1. Open Service URL on iPhone
2. Camera requires HTTPS ✓ (Cloud Run provides this)
3. Add to Home Screen for PWA experience:
   - Tap Share button
   - "Add to Home Screen"
   - Opens in standalone mode

### Android Chrome
1. Open Service URL on Android
2. Chrome will prompt to "Install App"
3. Camera permissions work out of the box

## Troubleshooting

### Build Fails
```bash
# Check build logs
gcloud builds list --limit=5

# View specific build
gcloud builds log BUILD_ID
```

### Deployment Fails
```bash
# Check Cloud Run service status
gcloud run services describe gotjunk --region=us-west1

# View logs
gcloud run services logs read gotjunk --region=us-west1
```

### Camera Not Working on iPhone
- **Cause**: App must be served over HTTPS
- **Solution**: Use Cloud Run URL (already HTTPS)
- **Verify**: Check console for `getUserMedia` errors

### IPFS Not Loading
- **Cause**: Helia initialization timeout
- **Solution**: Check browser console for errors
- **Note**: IPFS may be slower on mobile networks

## Production Checklist

- [ ] Secret Manager configured with API key
- [ ] Cloud Build trigger connected to GitHub
- [ ] First deployment successful
- [ ] HTTPS working (camera permissions)
- [ ] PWA manifest loading
- [ ] Add to Home Screen tested on iPhone
- [ ] Camera capture working on mobile
- [ ] IPFS upload working
- [ ] Geolocation 50km filter working
- [ ] Tab navigation + highlighting working

## Cost Estimate

- **Cloud Run**: ~$0.10/day (with min-instances=0)
- **Cloud Build**: $0.003/build-minute (~5min builds)
- **Container Registry**: ~$0.02/month storage
- **Total**: ~$3-5/month for light usage

## Environment Variables

Set via cloudbuild.yaml:
- `NODE_ENV=production` ✓
- `GEMINI_API_KEY_GOTJUNK` (from Secret Manager) ✓

## Next Steps

1. Deploy to Cloud Run
2. Test on iPhone Safari
3. Configure custom domain (optional)
4. Set up monitoring/alerts
5. Enable CDN for static assets (optional)
