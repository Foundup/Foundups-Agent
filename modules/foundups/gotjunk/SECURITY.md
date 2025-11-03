# GotJUNK? Security Guidelines

## API Key Management

### ❌ NEVER DO THIS:
- ❌ Commit `.env.local` to git
- ❌ Hardcode API keys in source code
- ❌ Share API keys in chat logs or screenshots
- ❌ Display API keys in documentation
- ❌ Store API keys in markdown files

### ✅ ALWAYS DO THIS:
- ✅ Use `.env.local` for local development (gitignored)
- ✅ Use environment variables in production
- ✅ Keep API keys in secure credential management systems
- ✅ Rotate API keys if exposed
- ✅ Use `.env.example` with placeholder values only

## Setting Up API Keys (Secure Method)

### Local Development:
```bash
# 1. Copy template
cp .env.example .env.local

# 2. Edit .env.local and add your key
# GEMINI_API_KEY=your_actual_key_here

# 3. Verify .gitignore includes *.local
cat .gitignore | grep "*.local"
```

### Cloud Run Deployment:
```bash
# Set via Cloud Run console:
# 1. Go to Cloud Run service
# 2. Edit & Deploy New Revision
# 3. Variables & Secrets tab
# 4. Add: GEMINI_API_KEY = your_actual_key

# Or via gcloud CLI:
gcloud run services update gotjunk \
  --update-env-vars GEMINI_API_KEY=your_actual_key
```

### AI Studio Deployment:
- AI Studio handles secrets automatically
- Set in AI Studio project settings
- Never commit to version control

## What's Protected

### Gitignored Files:
```
*.local           # All .env.local files
.env             # Environment files
dist/            # Build output
node_modules/    # Dependencies
```

### Secret Detection:
If you accidentally commit a secret:
1. **Immediately rotate** the API key
2. Revoke the old key at https://ai.google.dev/
3. Generate a new key
4. Update Cloud Run environment variables
5. Use `git filter-branch` or BFG Repo-Cleaner to remove from history

## API Key Rotation

If your API key is exposed:

1. **Revoke old key**:
   - Go to https://ai.google.dev/
   - Find the exposed key
   - Click "Revoke"

2. **Generate new key**:
   - Create new API key
   - Download securely

3. **Update everywhere**:
   - Local `.env.local`
   - Cloud Run environment variables
   - AI Studio project settings

4. **Clean git history** (if committed):
   ```bash
   # Install BFG Repo-Cleaner
   # Remove sensitive data from history
   bfg --replace-text sensitive.txt
   ```

## Conversation Logs

**WARNING**: This conversation may contain exposed API keys in earlier messages.

**Action Required**:
- Clear conversation history if API key was displayed
- Rotate the exposed key immediately
- Do not share conversation logs

## Cloud Run Security

### Environment Variables:
- Set via Cloud Run console (not in code)
- Use Secret Manager for production
- Enable VPC for private APIs

### IAM Permissions:
- Restrict who can view/edit environment variables
- Use service accounts with minimal permissions
- Enable Cloud Run authentication

## Monitoring

### Check for exposed secrets:
```bash
# Scan codebase for potential leaks
grep -r "AIza" . --exclude-dir=node_modules
grep -r "GEMINI_API_KEY.*AIza" . --exclude-dir=node_modules
```

### Use secret scanners:
- GitHub Secret Scanning (if using GitHub)
- GitGuardian
- TruffleHog

## WSP Compliance

**WSP 71: Secrets Management Protocol**
- All secrets must be externalized
- No hardcoded credentials
- Use secure credential stores
- Audit secret access

## Contact

If you discover a security issue:
1. Do NOT create a public issue
2. Rotate any exposed credentials immediately
3. Document the incident internally
4. Review and update security practices

---

**Last Updated**: GotJUNK? module integration
**Security Status**: ✅ No secrets in version control
