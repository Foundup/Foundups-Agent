# GotJunk Deployment Architecture

## Automatic Cloud Build Deployment

GotJunk uses **Google Cloud Build triggers** for fully automated deployment. No manual deployment required.

### How It Works

```
Developer → PR Merge → GitHub main → Cloud Build Trigger → Cloud Run
                                            ↓
                                      Build + Deploy
                                      (2-3 minutes)
```

### Deployment Flow

1. **Developer creates PR** with frontend changes
2. **PR merged to main branch** on GitHub
3. **Cloud Build trigger fires automatically** (within seconds)
4. **Cloud Build executes** [cloudbuild.yaml](../cloudbuild.yaml):
   - Builds Docker image from [Dockerfile](../frontend/Dockerfile)
   - Pushes image to Container Registry
   - Deploys to Cloud Run service `gotjunk`
5. **Live site updated** at https://gotjunk-56566376153.us-west1.run.app/

### Build Configuration

**File**: [modules/foundups/gotjunk/cloudbuild.yaml](../cloudbuild.yaml)

**Build Steps**:
```yaml
1. Docker build → gcr.io/gen-lang-client-0061781628/gotjunk:$COMMIT_SHA
2. Docker push → Container Registry
3. Deploy → Cloud Run (us-west1, 512Mi RAM, 1 CPU)
```

**Build Time**: ~2-3 minutes
- Docker build: ~1-1.5 min (Node 20 + Vite build)
- Push: ~30s
- Deploy: ~30s-1min (Cloud Run cold start)

### Docker Build

**Multi-stage Dockerfile**:
```dockerfile
Stage 1 (builder): Node 20 Alpine
  → npm ci (install deps)
  → npm run build (Vite production build)
  → Output: dist/ directory

Stage 2 (runtime): nginx Alpine
  → Copy dist/ → /usr/share/nginx/html
  → Configure nginx for SPA routing
  → Expose port 8080
  → Size: ~50MB (nginx + static assets)
```

### Cloud Run Configuration

```yaml
Service: gotjunk
Region: us-west1
URL: https://gotjunk-56566376153.us-west1.run.app/
Project: gen-lang-client-0061781628

Resources:
  Memory: 512Mi
  CPU: 1 vCPU
  Max instances: 10
  Min instances: 0 (scales to zero)

Port: 8080 (nginx)
Authentication: Allow unauthenticated

Secrets:
  GEMINI_API_KEY_GOTJUNK (from Secret Manager)

Environment:
  NODE_ENV=production
```

### Monitoring Deployment

**View Build History**:
https://console.cloud.google.com/cloud-build/builds?project=gen-lang-client-0061781628

**View Cloud Run Service**:
https://console.cloud.google.com/run/detail/us-west1/gotjunk/observability/metrics?project=gen-lang-client-0061781628

**Check Build Status**:
```bash
# List recent builds
gcloud builds list --project=gen-lang-client-0061781628 --limit=10

# View specific build
gcloud builds describe <BUILD_ID> --project=gen-lang-client-0061781628

# Stream logs
gcloud builds log <BUILD_ID> --project=gen-lang-client-0061781628 --stream
```

### Deployment Timeline

**Recent Deployments** (from Cloud Build history):

| Build ID | Commit | Status | Time | Duration |
|----------|--------|--------|------|----------|
| f0080ed3 | TBD | Running | 2:59 PM | In progress |
| 733dd5ed | 34d93b5 | ✅ Success | 7:27 AM | 2m 56s |
| 4e5bc79a | 34b3bd5 | ✅ Success | 7:27 AM | 2m 47s |
| f66b23bd | cf241c8 | ✅ Success | 12:01 AM | 2m 41s |

**Latest Deployed Commit**: `34d93b5` (PR #71 - Tutorial popup safe-area fix)

### Why Aren't My Changes Visible?

**Problem**: Merged PR to main, but live site doesn't show changes.

**Common Causes**:

1. **Build still running** (check Cloud Build console)
2. **Browser cache** (hard refresh: Cmd+Shift+R / Ctrl+Shift+R)
3. **Service Worker cache** (clear in DevTools → Application → Service Workers)
4. **CDN cache** (wait 5-10 minutes for edge propagation)

**How to Verify Deployment**:

```bash
# Check deployed commit SHA
curl -I https://gotjunk-56566376153.us-west1.run.app/ | grep x-cloud-trace-context

# Compare with GitHub main branch
git log origin/main --oneline -1
```

### Manual Deployment (Emergency Only)

If Cloud Build trigger fails, manual deployment is possible:

```bash
cd modules/foundups/gotjunk
bash deployment/deploy.sh
```

**Requirements**:
- gcloud CLI installed
- Authenticated: `gcloud auth login`
- Project set: `gcloud config set project gen-lang-client-0061781628`

### Trigger Configuration

**Trigger Name**: `gotjunk-main-trigger` (inferred from build history)

**Trigger Source**: GitHub repository `Foundup/Foundups-Agent`

**Trigger Event**: Push to `main` branch

**Included Files** (inferred):
- `modules/foundups/gotjunk/**`
- Triggers only on changes to GotJunk module

**Build Config**: `modules/foundups/gotjunk/cloudbuild.yaml`

### Troubleshooting

**Build Failed**:
1. Check build logs in Cloud Build console
2. Common issues:
   - TypeScript compilation errors
   - Vite build failures
   - Docker layer caching issues
   - Secret access errors

**Deployment Failed**:
1. Check Cloud Run service logs
2. Common issues:
   - Container crashes (check nginx config)
   - Port mismatch (must be 8080)
   - Memory limits exceeded
   - Secret mounting failures

**Site Not Updating**:
1. Clear browser cache (Cmd+Shift+R)
2. Check Cloud Build - build may still be running
3. Verify deployment: `gcloud run services describe gotjunk --region=us-west1 --project=gen-lang-client-0061781628`
4. Check latest revision deployed

### Best Practices

1. **Always test locally** before merging:
   ```bash
   cd modules/foundups/gotjunk/frontend
   npm run build
   npm run preview  # Test production build
   ```

2. **Monitor build after merge**:
   - Watch Cloud Build console for ~3 minutes
   - Verify build succeeds before testing live site

3. **Clear cache when testing**:
   - Hard refresh (Cmd+Shift+R)
   - Or use incognito mode

4. **Small PRs deploy faster**:
   - Docker layer caching works better
   - Faster npm install (fewer dep changes)

### Architecture Benefits

✅ **Zero manual deployment** - automatic on merge
✅ **Fast iteration** - 2-3 minute deploy time
✅ **Immutable deploys** - every commit gets unique image tag
✅ **Easy rollback** - redeploy previous image with one command
✅ **Cost efficient** - scales to zero when idle
✅ **Security** - secrets managed in Secret Manager, not code

### WSP Compliance

- **WSP 7**: Pre-commit validation (Cloud Build checks before deploy)
- **WSP 22**: Deployment documented (this file)
- **WSP 50**: Pre-action verification (build logs + Cloud Run metrics)
- **WSP 87**: Code navigation preserved (deployment doesn't block development)

---

**Live URL**: https://gotjunk-56566376153.us-west1.run.app/
**Build History**: https://console.cloud.google.com/cloud-build/builds?project=gen-lang-client-0061781628
**Cloud Run Console**: https://console.cloud.google.com/run/detail/us-west1/gotjunk?project=gen-lang-client-0061781628
