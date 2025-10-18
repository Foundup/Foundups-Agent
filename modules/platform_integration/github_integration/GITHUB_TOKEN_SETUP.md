# GitHub Token Setup Guide

**WSP Compliance**: Following WSP 71 (Secrets Management Protocol)

## [U+1F511] Creating Your GitHub Personal Access Token

### Step 1: Generate Token on GitHub
1. Go to [GitHub Settings > Developer settings > Personal access tokens > Tokens (classic)](https://github.com/settings/tokens)
2. Click **"Generate new token (classic)"**
3. Set **Name**: `FoundUps-Agent-Integration`
4. Set **Expiration**: 90 days (for security)
5. Select **Required Scopes**:
   - [OK] `repo` - Full repository access
   - [OK] `workflow` - GitHub Actions workflow access
   - [OK] `write:packages` - Package write access
   - [OK] `read:org` - Organization read access
   - [OK] `user:email` - User email access

### Step 2: Copy and Secure Token
1. **Copy the token** (it will only be shown once!)
2. **DO NOT** share or commit this token to git
3. **Store securely** in your password manager

### Step 3: Add Token to .env File
1. Open `O:\Foundups-Agent\.env`
2. Replace the empty `GITHUB_TOKEN=` line with:
   ```
   GITHUB_TOKEN=ghp_your_actual_token_here_1234567890
   ```
3. **Save the file**

### Step 4: Verify .env is in .gitignore
The `.env` file should already be in `.gitignore` to prevent token exposure:
```
# Environment variables
.env
.env.local
```

## [U+1F9EA] Testing the Integration

### Quick Health Check
```bash
cd O:\Foundups-Agent
python -c "import asyncio; from modules.platform_integration.github_integration.src.wre_integration import quick_health_check; print('[OK] Healthy' if asyncio.run(quick_health_check()) else '[FAIL] Issues found')"
```

### Full Integration Test
```bash
cd O:\Foundups-Agent\modules\platform_integration\github_integration
python src/wre_integration.py
```

This will:
- [OK] Test GitHub API authentication
- [OK] Check repository access
- [OK] Display rate limit status
- [OK] Show repository statistics

## [LOCK] Security Best Practices (WSP 71 Compliance)

### Token Security
- [OK] **Never commit tokens to git**
- [OK] **Use environment variables only**
- [OK] **Set reasonable expiration dates**
- [OK] **Monitor token usage in GitHub settings**
- [OK] **Rotate tokens regularly (every 90 days)**

### Access Control
- [OK] **Use minimum required scopes**
- [OK] **Limit to specific repositories if possible**
- [OK] **Monitor API usage and rate limits**
- [OK] **Revoke unused tokens immediately**

### Backup & Recovery
- [OK] **Document token creation process**
- [OK] **Have backup authentication methods**
- [OK] **Test token rotation procedures**
- [OK] **Monitor for token expiration**

## [ALERT] Troubleshooting

### Common Issues

#### Token Not Found
```
Error: No GitHub token provided
Solution: Check GITHUB_TOKEN in .env file
```

#### Invalid Token
```
Error: GitHub API error: Bad credentials
Solution: Generate new token with correct scopes
```

#### Rate Limit Exceeded
```
Error: GitHub API error: API rate limit exceeded  
Solution: Wait for reset (5000/hour limit) or use authenticated requests
```

#### Repository Access Denied
```
Error: GitHub API error: Not Found
Solution: Verify token has repo access and repository exists
```

### Debug Mode
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Run integration with debug logging
python modules/platform_integration/github_integration/src/wre_integration.py
```

## [OK] Verification Checklist

Before proceeding, verify:
- [ ] GitHub token generated with correct scopes
- [ ] Token added to .env file (never to git)
- [ ] .env file is in .gitignore
- [ ] Health check passes
- [ ] Repository access confirmed
- [ ] Rate limits are reasonable

## [REFRESH] WSP Protocol Compliance

### WSP 71: Secrets Management
- [OK] Environment variable storage
- [OK] No hardcoded secrets
- [OK] Secure token handling
- [OK] Access control documentation

### WSP 34: Git Operations Protocol
- [OK] GitHub integration with git operations
- [OK] Automated PR creation
- [OK] Repository management

### WSP 22: Documentation
- [OK] Complete setup documentation
- [OK] Security guidelines
- [OK] Troubleshooting guide

---

**Once your token is set up, run the health check to verify everything is working correctly!**