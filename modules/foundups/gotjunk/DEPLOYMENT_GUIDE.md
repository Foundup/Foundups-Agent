# GotJUNK? Deployment Guide

## Overview

This guide explains how to update the existing Google Cloud Run deployment from the new module location in `modules/foundups/gotjunk/`.

**AI Studio Project**: https://ai.studio/apps/drive/1R_lBYHwMJHOxWjI_HAAx5DU9fqePG9nA

---

## Method 1: AI Studio Redeploy (Recommended)

This is the **easiest and safest** method for updating your deployed app.

### Steps:

1. **Make Changes Locally**
   ```bash
   cd modules/foundups/gotjunk/frontend

   # Edit files as needed
   # Example: Update App.tsx, add features, etc.
   ```

2. **Test Locally**
   ```bash
   # Install dependencies (first time only)
   npm install

   # Copy environment template
   cp .env.example .env.local

   # Edit .env.local and add your GEMINI_API_KEY
   # GEMINI_API_KEY_GotJunk=your_actual_api_key_here

   # Run development server
   npm run dev

   # Visit http://localhost:5173 to test
   ```

3. **Build for Production**
   ```bash
   npm run build

   # This creates the dist/ folder with optimized files
   ```

4. **Upload to AI Studio**
   - Open: https://ai.studio/apps/drive/1R_lBYHwMJHOxWjI_HAAx5DU9fqePG9nA
   - Click the file upload icon
   - Upload changed files from `frontend/` directory
   - Or edit directly in AI Studio's code editor

5. **Redeploy**
   - Click the 🚀 rocket icon (top right)
   - Select your Google Cloud project
   - Click **"Redeploy app"**
   - Wait for deployment to complete (usually 1-2 minutes)

6. **Verify**
   - Visit your Cloud Run URL
   - Test the updated functionality
   - Check browser console for errors

### Important Notes:
- ✅ **Preserves existing deployment** - same URL, same project
- ✅ **Zero downtime** - Cloud Run handles rolling updates
- ⚠️ **Overwrites Cloud Run source editor changes** - always deploy from AI Studio
- 💡 **Environment variables** - Set in Cloud Run console if needed

---

## Method 2: Cloud Run Source Editor

For quick fixes, you can edit directly in Cloud Run (but changes will be overwritten by AI Studio redeploy).

### Steps:

1. **Open Cloud Run Console**
   - Go to: https://console.cloud.google.com/run
   - Select your project
   - Find the GotJUNK? service

2. **Edit Source**
   - Click "Edit source" button
   - Make changes in the web editor
   - Click "Save and redeploy"

3. **Verify**
   - Wait for deployment
   - Test at your Cloud Run URL

### Warning:
⚠️ **These changes will be LOST** when you redeploy from AI Studio!
- Only use for emergency hotfixes
- Immediately sync changes back to `modules/foundups/gotjunk/frontend/`

---

## Method 3: Automated Deployment (Future)

We can create a deployment script for automated updates.

### Planned Features:
- `./deployment/deploy.sh` - One-command deployment
- GitHub Actions integration
- Automatic environment variable injection
- Rollback support

**Status**: Not yet implemented (see ROADMAP.md Prototype phase)

---

## Environment Variables

### Required:
```bash
GEMINI_API_KEY_GotJunk=your_gemini_api_key_here
```

### Setting in Cloud Run:

1. **Via Console**:
   - Go to Cloud Run service
   - Click "Edit & Deploy New Revision"
   - Scroll to "Container" section
   - Add environment variable: `GEMINI_API_KEY_GotJunk`
   - Click "Deploy"

2. **Via AI Studio** (Recommended):
   - Set in `.env.local` locally
   - AI Studio handles environment variables during redeploy

---

## Common Issues

### Issue: "GEMINI_API_KEY_GotJunk is not defined"

**Solution**:
```bash
# Create .env.local
cp .env.example .env.local

# Edit and add your key
echo "GEMINI_API_KEY_GotJunk=your_actual_key_here" > .env.local

# Rebuild
npm run build
```

### Issue: "Camera not working"

**Cause**: Not using HTTPS
**Solution**: Always test camera features on Cloud Run (HTTPS) or localhost

### Issue: "Geolocation permission denied"

**Solution**:
- Browser needs HTTPS for geolocation
- Click "Allow" when prompted
- Check browser settings if blocked

### Issue: "Build fails in AI Studio"

**Solution**:
1. Run `npm run build` locally to catch errors
2. Check TypeScript errors: `npx tsc --noEmit`
3. Ensure all dependencies in `package.json`
4. Check AI Studio console logs

---

## Deployment Checklist

Before deploying to production:

- [ ] Test locally with `npm run dev`
- [ ] Run build: `npm run build`
- [ ] Check for TypeScript errors: `npx tsc --noEmit`
- [ ] Verify `.env.example` is up to date
- [ ] Update INTERFACE.md if API changed
- [ ] Update ModLog.md with changes
- [ ] Test camera permissions
- [ ] Test geolocation
- [ ] Test offline mode (PWA)
- [ ] Verify export functionality
- [ ] Check bundle size: `npm run build` (should be <1MB)
- [ ] Review Cloud Run logs after deployment

---

## Monitoring

### Cloud Run Logs:
```bash
# View logs in real-time
gcloud logging tail --project=YOUR_PROJECT_ID \
  --resource-type=cloud_run_revision

# Or use Cloud Console:
# https://console.cloud.google.com/run > Your Service > Logs
```

### Performance Metrics:
- **Startup Time**: Should be <2s
- **Request Latency**: Should be <500ms
- **Memory Usage**: Should be <256MB
- **Cold Start**: Should be <3s

---

## Rollback

If deployment fails or has issues:

1. **Via AI Studio**:
   - Keep backup of previous version (Download ZIP)
   - Upload old files
   - Redeploy

2. **Via Cloud Run Console**:
   - Go to "Revisions" tab
   - Click previous revision
   - Click "Manage Traffic"
   - Set 100% traffic to old revision

---

## Next Steps

After successful deployment:

1. **Monitor**: Check Cloud Run logs for errors
2. **Test**: Verify all features work in production
3. **Document**: Update ModLog.md with deployment details
4. **Share**: Add production URL to README.md and INTERFACE.md
5. **Plan**: Review ROADMAP.md for next features

---

**Need Help?**
- Check [INTERFACE.md](INTERFACE.md) for API details
- See [README.md](README.md) for feature documentation
- Review [ROADMAP.md](ROADMAP.md) for planned enhancements
- AI Studio Docs: https://ai.google.dev/

**Deployment Status**: ✅ Ready to deploy from modules/foundups/gotjunk/
