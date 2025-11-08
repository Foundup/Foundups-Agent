# Force GotJunk Rebuild - No Cloning Needed!

## ✅ EASIEST METHOD: GCP Console Manual Trigger

You already have Cloud Build triggers set up. Just manually re-trigger it!

### Step 1: Open Cloud Build Triggers
```
https://console.cloud.google.com/cloud-build/triggers
```

### Step 2: Find Your GotJunk Trigger
Look for trigger named:
- `gotjunk-deploy`
- `gotjunk-deploy-trigger`
- Or similar name with "gotjunk" in it

### Step 3: Click "RUN" Button
1. Click the **RUN** button (▶️ icon) next to the trigger
2. Confirm branch: `main`
3. Click **"RUN TRIGGER"**

### Step 4: Monitor Build
```
https://console.cloud.google.com/cloud-build/builds
```
- Watch live logs
- Build time: ~5-7 minutes
- Look for "SUCCESS" status

### Step 5: Verify Deployment
Once build succeeds, open: https://gotjunk.foundups.com/

**Check for:**
- 4 icons in bottom nav (Grid, Pin, Home, Cart)
- Blue highlight on active tab
- Console log: `[GotJunk] IPFS initialized`

---

## 🔧 ALTERNATIVE: Force Rebuild with Dummy Commit

If manual trigger doesn't work, make a tiny commit to force rebuild:

```bash
cd O:/Foundups-Agent

# Add empty line to trigger rebuild
echo "" >> modules/foundups/gotjunk/frontend/.env.example

# Commit and push
git add modules/foundups/gotjunk/frontend/.env.example
git commit -m "chore(gotjunk): force rebuild"
git push origin main
```

This will auto-trigger Cloud Build with the latest code.

---

## 📊 WHY THIS WORKS

Your Cloud Build trigger is configured to:
- ✅ Watch `main` branch
- ✅ Filter for `modules/foundups/gotjunk/**` changes
- ✅ Run `cloudbuild.yaml` automatically

When you manually trigger or push, it:
1. Pulls latest code from GitHub main branch
2. Builds fresh Docker image (no cache)
3. Deploys to Cloud Run
4. Updates https://gotjunk.foundups.com/

---

## ⚠️ CACHE ISSUE FIX

If the build still shows old code, add `--no-cache` flag:

1. Edit your Cloud Build trigger in GCP Console
2. Add substitution variable: `_NO_CACHE=true`
3. Or manually run with Cloud Shell (see below)

---

## 🌐 CLOUD SHELL OPTION (Minimal Upload)

If you prefer Cloud Shell, only upload the cloudbuild.yaml:

```bash
# In Cloud Shell
cat > cloudbuild.yaml << 'EOF'
# Paste contents of modules/foundups/gotjunk/cloudbuild.yaml here
EOF

# Submit build (points to GitHub repo, no cloning needed)
gcloud builds submit --config=cloudbuild.yaml \
  --substitutions=REPO_NAME=Foundups-Agent,BRANCH_NAME=main,COMMIT_SHA=$(git ls-remote https://github.com/Foundup/Foundups-Agent.git refs/heads/main | cut -f1) \
  --no-source
```

But honestly, **just use the GCP Console RUN button** - it's the easiest!

---

## ✅ RECOMMENDED: GCP Console Manual Trigger

**Total steps:**
1. Open https://console.cloud.google.com/cloud-build/triggers
2. Click RUN button on gotjunk trigger
3. Wait 5-7 minutes
4. Test https://gotjunk.foundups.com/

**No cloning, no installing, no uploading!** 🎉
