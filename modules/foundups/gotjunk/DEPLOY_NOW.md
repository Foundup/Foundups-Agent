# GotJunk Deployment - Quick Start

## ✅ PR #13 Merged Successfully!
https://github.com/FOUNDUPS/Foundups-Agent/pull/13

All code is now in main branch and ready to deploy to Google Cloud Run.

---

## OPTION 1: Deploy from Your Local Machine (Recommended)

### Step 1: Install Google Cloud SDK (if not installed)

**Windows:**
```powershell
# Download and run installer
https://dl.google.com/dl/cloudsdk/channels/rapid/GoogleCloudSDKInstaller.exe
```

**Mac:**
```bash
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
```

### Step 2: Authenticate

```bash
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

### Step 3: Pull Latest Code

```bash
git checkout main
git pull origin main
```

### Step 4: Deploy to Cloud Run

```bash
cd O:/Foundups-Agent

# Deploy (this will build and deploy in one command)
gcloud builds submit \
  --config=modules/foundups/gotjunk/cloudbuild.yaml \
  .
```

**Build Time**: ~5-7 minutes
**What happens:**
1. Builds Docker image with Vite production build
2. Pushes to Container Registry
3. Deploys to Cloud Run (region: us-west1)

### Step 5: Get Your App URL

```bash
gcloud run services describe gotjunk \
  --region=us-west1 \
  --format='value(status.url)'
```

Example output: `https://gotjunk-XXXXXXXXXX-uw.a.run.app`

---

## OPTION 2: Deploy from Google Cloud Shell (Browser-Based)

### Step 1: Open Cloud Shell
https://console.cloud.google.com/cloudshell/editor

### Step 2: Clone Repo

```bash
git clone https://github.com/FOUNDUPS/Foundups-Agent.git
cd Foundups-Agent
git checkout main
```

### Step 3: Deploy

```bash
gcloud builds submit \
  --config=modules/foundups/gotjunk/cloudbuild.yaml \
  .
```

### Step 4: Get URL

```bash
gcloud run services describe gotjunk \
  --region=us-west1 \
  --format='value(status.url)'
```

---

## OPTION 3: Set Up Automated Deployment (Future Pushes)

This will automatically deploy when you push to main.

```bash
# Create Cloud Build trigger
gcloud builds triggers create github \
  --name="gotjunk-auto-deploy" \
  --repo-name="Foundups-Agent" \
  --repo-owner="Foundup" \
  --branch-pattern="^main$" \
  --build-config="modules/foundups/gotjunk/cloudbuild.yaml" \
  --included-files="modules/foundups/gotjunk/**"
```

Now every `git push origin main` with GotJunk changes will automatically deploy!

---

## SECRET MANAGER SETUP (If First Deploy)

If this is your first deployment, create the Gemini API key secret:

```bash
# Create secret
echo "YOUR_GEMINI_API_KEY_HERE" | gcloud secrets create GEMINI_API_KEY_GOTJUNK --data-file=-

# Grant Cloud Run access
PROJECT_NUM=$(gcloud projects describe $(gcloud config get-value project) --format='value(projectNumber)')
gcloud secrets add-iam-policy-binding GEMINI_API_KEY_GOTJUNK \
  --member="serviceAccount:${PROJECT_NUM}-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

---

## TEST ON IPHONE

### Step 1: Open Safari on iPhone
Navigate to your Cloud Run URL: `https://gotjunk-XXXXXXXXXX-uw.a.run.app`

### Step 2: Grant Permissions
- **Camera**: Tap "Allow" when prompted (HTTPS required ✓)
- **Location**: Tap "Allow" for 50km filtering

### Step 3: Add to Home Screen (PWA)
1. Tap **Share** button (square with arrow)
2. Scroll down → Tap **"Add to Home Screen"**
3. Tap **"Add"**
4. App opens in standalone mode!

### Step 4: Test Features
- [ ] Camera works (back camera)
- [ ] Photo capture
- [ ] Swipe up (keep) → Item uploaded to IPFS
- [ ] Tab 1 (Browse) highlights when clicked
- [ ] Tab 2 (Map) shows your location
- [ ] Tab 3 (My Items) shows captured photos
- [ ] Tab 4 (Cart) ready for browsing

---

## TROUBLESHOOTING

### Build Fails

```bash
# View build logs
gcloud builds list --limit=5

# View specific build
gcloud builds log BUILD_ID
```

### Deployment Fails

```bash
# Check service status
gcloud run services describe gotjunk --region=us-west1

# View runtime logs
gcloud run services logs read gotjunk --region=us-west1
```

### Camera Not Working on iPhone
- **Cause**: Not HTTPS
- **Solution**: Use Cloud Run URL (already HTTPS)
- **Check**: Safari address bar should show 🔒

---

## WHAT'S DEPLOYED

### Architecture
- ✅ 4-tab navigation (Browse, Map, My Items, Cart)
- ✅ State bucket separation (my items ≠ others' items)
- ✅ Icon highlighting (active tab glows blue)
- ✅ IPFS integration (Helia for decentralized storage)

### Mobile Support
- ✅ iOS Safari camera access
- ✅ PWA manifest for home screen install
- ✅ Geolocation with 50km filtering
- ✅ Responsive design

### Infrastructure
- ✅ Docker multi-stage build
- ✅ nginx serving Vite production build
- ✅ Auto-scaling Cloud Run (min=0, max=10)
- ✅ Secret Manager for API keys

---

## COST ESTIMATE

- **Cloud Run**: ~$0.10/day (scales to zero)
- **Container Registry**: ~$0.02/month
- **Total**: ~$3-5/month light usage

---

## NEXT STEPS

1. **Deploy**: Run `gcloud builds submit --config=modules/foundups/gotjunk/cloudbuild.yaml .`
2. **Get URL**: Run `gcloud run services describe gotjunk --region=us-west1 --format='value(status.url)'`
3. **Test**: Open URL on iPhone Safari
4. **Report**: Let me know if it works!

---

**READY TO DEPLOY!** 🚀

Choose Option 1 (local machine) or Option 2 (Cloud Shell) and follow the steps above.
