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

### Cloud Build Trigger Not Activating

**Problem**: PR merged to main, but Cloud Build didn't trigger automatically.

**Investigation Steps**:

1. **Check Cloud Build Trigger Configuration**:
   ```bash
   # Via GCP Console (recommended)
   https://console.cloud.google.com/cloud-build/triggers?project=gen-lang-client-0061781628

   # Verify trigger: gotjunk-deploy-trigger
   # - Branch pattern: ^main$
   # - File filter: modules/foundups/gotjunk/**
   # - Status: Enabled
   ```

2. **Check Recent Build History**:
   ```bash
   # Via GCP Console
   https://console.cloud.google.com/cloud-build/builds?project=gen-lang-client-0061781628

   # Look for builds triggered by recent commits
   # Status: SUCCESS / FAILURE / QUEUED / WORKING
   ```

3. **Verify Git Commit Matches Trigger Pattern**:
   ```bash
   # Check recent commits to main branch
   git log origin/main --oneline -5

   # Verify changed files match trigger filter
   git show <commit-hash> --stat | grep "modules/foundups/gotjunk/"

   # Example:
   git show 72359a04 --stat | grep "modules/foundups/gotjunk/"
   # Should show: modules/foundups/gotjunk/frontend/App.tsx
   ```

4. **Check GitHub Webhook Connection**:
   ```bash
   # Via GCP Console
   https://console.cloud.google.com/cloud-build/connections?project=gen-lang-client-0061781628

   # Verify connection: foundups-agent-github
   # Status: Connected
   ```

5. **Investigate Build Logs** (if build ran but failed):
   ```bash
   # Via GCP Console - click on failed build
   https://console.cloud.google.com/cloud-build/builds?project=gen-lang-client-0061781628

   # Common issues:
   # - npm install failed (dependency error)
   # - npm run build failed (TypeScript errors)
   # - gcloud run deploy failed (permission error)
   # - Secret Manager access denied
   ```

**Solutions**:

- **Trigger Not Enabled**: Enable in Cloud Build Triggers console
- **Branch Pattern Mismatch**: Trigger watches `^main$`, verify PR merged to `main` (not a feature branch)
- **File Filter Mismatch**: Trigger watches `modules/foundups/gotjunk/**`, verify changed files match
- **Webhook Not Firing**: Reconnect GitHub in Cloud Build Connections
- **First-Time Setup - MOST COMMON**: Manual trigger activation required (see below)

### First-Time Trigger Activation via 0102 Automation

**0102 Autonomous Trigger Activation** (WSP 77 + WSP 96):

```python
# Execute via 0102 GCP Console Automator
from modules.infrastructure.foundups_selenium.src.gcp_console_automator import GCPConsoleAutomator

automator = GCPConsoleAutomator()

# Complete autonomous setup (creates trigger if missing, runs first build)
results = automator.setup_gotjunk_deployment()

# 0102 navigates GCP Console using Vision DAE + FoundUpsDriver:
# - Verifies trigger exists and is enabled
# - Clicks "RUN" button on gotjunk-deploy-trigger
# - Selects branch: main
# - Monitors build logs for SUCCESS/FAILURE
# - Verifies deployment at production URL

for workflow, result in results.items():
    print(f"{workflow}: {'✓' if result.success else '✗'} ({result.duration_seconds:.1f}s)")
```

**Note**: `run_cloud_build_trigger()` method not yet implemented in automator. Current implementation uses `setup_gotjunk_deployment()` which handles full infrastructure setup. Add dedicated trigger execution method for future optimization.

**What 0102 Automates**:
1. ✓ Navigate to Cloud Build Triggers console
2. ✓ Verify trigger exists and is enabled
3. ✓ Click "RUN" button using Vision DAE
4. ✓ Select branch: `main`
5. ✓ Click "RUN TRIGGER" button
6. ✓ Monitor build logs for SUCCESS/FAILURE
7. ✓ Verify deployment at production URL
8. ✓ Notify via YouTube Live Chat when complete

**Root Cause**: Previous session used semi-automated setup script ([gcp_console_automator.py:265](../../infrastructure/foundups_selenium/src/gcp_console_automator.py#L265)) which requires human completion of trigger form fields. The trigger may exist but was never fully activated.

**Manual Fallback** (if 0102 automation unavailable):
1. Go to: https://console.cloud.google.com/cloud-build/triggers?project=gen-lang-client-0061781628
2. Click on `gotjunk-deploy-trigger`
3. Click **"RUN"** button → Select branch: `main` → Click "RUN TRIGGER"
4. Monitor: https://console.cloud.google.com/cloud-build/builds?project=gen-lang-client-0061781628
5. Verify: https://gotjunk-56566376153.us-west1.run.app

**0102 Monitoring** (continuous):
```bash
# Use gcp_console_automation skill to monitor builds automatically
# Skill: modules/communication/livechat/skills/gcp_console_automation.json
# Action: monitor_cloud_build
# Notification: YouTube Live Chat when deployment succeeds/fails
```

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
