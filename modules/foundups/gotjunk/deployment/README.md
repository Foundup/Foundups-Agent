# GotJUNK? Deployment Scripts

## Deployed Service

**Live URL**: https://gotjunk-56566376153.us-west1.run.app
**Console**: https://console.cloud.google.com/run/detail/us-west1/gotjunk/observability/metrics?project=gen-lang-client-0061781628

**Project**: `gen-lang-client-0061781628`
**Service**: `gotjunk`
**Region**: `us-west1`

---

## Prerequisites

### 1. Install Google Cloud CLI

**Windows**:
1. Download: https://cloud.google.com/sdk/docs/install
2. Run installer
3. Restart terminal after installation

**Or via Chocolatey**:
```powershell
choco install gcloudsdk
```

**Verify Installation**:
```bash
gcloud --version
```

### 2. Authenticate

```bash
gcloud auth login
```

This opens your browser to sign in with your Google account.

### 3. Set Environment Variable

**Windows (PowerShell)**:
```powershell
$env:GEMINI_API_KEY_GotJunk="your_actual_api_key_here"
```

**Windows (CMD)**:
```cmd
set GEMINI_API_KEY_GotJunk=your_actual_api_key_here
```

**Linux/Mac**:
```bash
export GEMINI_API_KEY_GotJunk="your_actual_api_key_here"
```

---

## Deployment Methods

### Method 1: Automated Script (Recommended)

**Windows**:
```bash
cd modules/foundups/gotjunk/deployment
./deploy.bat
```

**Linux/Mac**:
```bash
cd modules/foundups/gotjunk/deployment
chmod +x deploy.sh
./deploy.sh
```

**What it does**:
1. ✅ Builds frontend (`npm run build`)
2. ✅ Deploys to Cloud Run
3. ✅ Sets environment variables
4. ✅ Shows deployment URL

### Method 2: Manual Deployment

```bash
# Navigate to frontend
cd modules/foundups/gotjunk/frontend

# Build
npm run build

# Deploy
gcloud run deploy gotjunk \
  --source . \
  --region us-west1 \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars "GEMINI_API_KEY_GotJunk=$GEMINI_API_KEY_GotJunk" \
  --project gen-lang-client-0061781628
```

### Method 3: Via AI Studio (Original Method)

1. Open: https://ai.studio/apps/drive/1R_lBYHwMJHOxWjI_HAAx5DU9fqePG9nA
2. Upload updated files
3. Click 🚀 "Redeploy app"

---

## Deployment Checklist

Before deploying:

- [ ] Test locally: `npm run dev`
- [ ] Build succeeds: `npm run build`
- [ ] No TypeScript errors: `npx tsc --noEmit`
- [ ] Environment variable set: `echo $GEMINI_API_KEY_GotJunk` (should not be empty)
- [ ] gcloud authenticated: `gcloud auth list`
- [ ] Correct project: `gcloud config get-value project` (should be gen-lang-client-0061781628)

---

## Post-Deployment

### Verify Deployment

**Check Service Status**:
```bash
gcloud run services describe gotjunk --region us-west1 --platform managed
```

**View Logs**:
```bash
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=gotjunk" --limit 50
```

**Test URL**:
```bash
curl https://gotjunk-56566376153.us-west1.run.app
```

### Monitor

**Cloud Console**:
- Metrics: https://console.cloud.google.com/run/detail/us-west1/gotjunk/observability/metrics?project=gen-lang-client-0061781628
- Logs: https://console.cloud.google.com/run/detail/us-west1/gotjunk/logs?project=gen-lang-client-0061781628

**Key Metrics**:
- Request count
- Latency (should be <500ms)
- Error rate (should be <1%)
- Memory usage
- CPU utilization

---

## Troubleshooting

### Error: "gcloud: command not found"

**Solution**: Install Google Cloud CLI (see Prerequisites)

### Error: "Permission denied"

**Solution**:
```bash
gcloud auth login
gcloud config set project gen-lang-client-0061781628
```

### Error: "Build failed"

**Solution**:
```bash
cd modules/foundups/gotjunk/frontend
rm -rf node_modules package-lock.json
npm install
npm run build
```

### Error: "Environment variable not set"

**Solution**:
```bash
# Verify it's set
echo $GEMINI_API_KEY_GotJunk

# Set it again
export GEMINI_API_KEY_GotJunk="your_key_here"
```

### Error: "Service already exists"

This is **expected** - gcloud will update the existing service. The URL stays the same.

---

## Rollback

If deployment fails or has issues:

**Via Console**:
1. Go to: https://console.cloud.google.com/run/detail/us-west1/gotjunk/revisions?project=gen-lang-client-0061781628
2. Click previous revision
3. Click "Manage Traffic"
4. Set 100% to old revision

**Via CLI**:
```bash
# List revisions
gcloud run revisions list --service gotjunk --region us-west1

# Route traffic to specific revision
gcloud run services update-traffic gotjunk \
  --to-revisions REVISION_NAME=100 \
  --region us-west1
```

---

## CI/CD Integration (Future)

For automated deployments on git push, see:
- GitHub Actions: `.github/workflows/deploy-gotjunk.yml` (to be created)
- Cloud Build: `cloudbuild.yaml` (to be created)

---

**Need Help?**
- Cloud Run Docs: https://cloud.google.com/run/docs
- gcloud CLI Reference: https://cloud.google.com/sdk/gcloud/reference/run
- Support: Check logs in Cloud Console first
