# SECURITY: Personal Data in Git History

## Problem
1728 browser profile files still exist in git history containing:
- Personal browsing data
- Session cookies  
- Cached credentials
- Browser preferences

## Why This Happened
- Browser profiles were committed in early development (d97fb4f1)
- We removed them from tracking (2735846b) but NOT from history
- `.gitignore` now blocks them, but history remains

## What Selenium Needs (Keep These Files Locally)
✅ KEEP these directories locally for posting to work:
- `modules/platform_integration/browser_profiles/` - LinkedIn/X sessions
- `modules/platform_integration/linkedin_agent/data/chrome_profile/` - LinkedIn auth
- `modules/platform_integration/x_twitter/data/chrome_profile_foundups/` - X/Twitter auth

These maintain login sessions so Selenium doesn't need to re-authenticate.

## What's Safe to Delete from Git History
❌ DELETE from git history (but keep locally):
- All browser cache files
- Session storage
- Cookies
- Service worker cache
- GPU cache
- All files matching:
  - `**/browser_profiles/**`
  - `**/chrome_profile/**`
  - `**/edge_profile/**`
  - `**/data/chrome_profile/**`

## Solutions

### Option 1: BFG Repo-Cleaner (Recommended)
```bash
# Download BFG: https://rtyley.github.io/bfg-repo-cleaner/
java -jar bfg.jar --delete-folders browser_profiles --no-blob-protection .
java -jar bfg.jar --delete-folders chrome_profile --no-blob-protection .
java -jar bfg.jar --delete-folders edge_profile --no-blob-protection .
git reflog expire --expire=now --all
git gc --prune=now --aggressive
git push --force
```

### Option 2: Git Filter-Branch (Manual)
```bash
git filter-branch --force --index-filter \
  'git rm -r --cached --ignore-unmatch modules/platform_integration/browser_profiles modules/platform_integration/*/data/*_profile*' \
  --prune-empty --tag-name-filter cat -- --all
git push --force
```

### Option 3: Fresh Repo (Nuclear Option)
1. Export clean code (without browser profiles)
2. Create new GitHub repo
3. Push clean history
4. Archive old repo

## Impact
- Rewrites git history (breaks collaborators)
- Requires force push
- Old clones will need re-cloning
- BUT removes all personal data from GitHub

## Immediate Action
1. Verified `.gitignore` blocks future commits ✅
2. Browser profiles removed from tracking ✅  
3. Files kept locally for Selenium ✅
4. Need to purge git history ⏳

## Rotation Fix Status
The OAuth credential rotation fix is ready but CAN'T be pushed until we:
1. Clean git history of large files (189MB)
2. Clean git history of personal browser data (1728 files)

Commits ready to push:
- c8f9c65d: FIX: Automatic credential rotation
- ae1a5261: Add 012.txt to .gitignore  
- 2735846b: Gitignore large files
