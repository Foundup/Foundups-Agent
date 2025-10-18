# GitHub Token Setup Guide

**WSP Compliance**: Following WSP 71 (Secrets Management Protocol)

## 🔑 Creating Your GitHub Personal Access Token

### Step 1: Generate Token on GitHub
1. Go to [GitHub Settings > Developer settings > Personal access tokens > Tokens (classic)](https://github.com/settings/tokens)
2. Click **"Generate new token (classic)"**
3. Set **Name**: `FoundUps-Agent-Integration`
4. Set **Expiration**: 90 days (for security)
5. Select **Required Scopes**:
   - ✅ `repo` - Full repository access
   - ✅ `workflow` - GitHub Actions workflow access
   - ✅ `write:packages` - Package write access
   - ✅ `read:org` - Organization read access
   - ✅ `user:email` - User email access

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

## 🧪 Testing the Integration

### Quick Health Check
```bash
cd O:\Foundups-Agent
python -c "import asyncio; from modules.platform_integration.github_integration.src.wre_integration import quick_health_check; print('✅ Healthy' if asyncio.run(quick_health_check()) else '❌ Issues found')"
```

### Full Integration Test
```bash
cd O:\Foundups-Agent\modules\platform_integration\github_integration
python src/wre_integration.py
```

This will:
- ✅ Test GitHub API authentication
- ✅ Check repository access
- ✅ Display rate limit status
- ✅ Show repository statistics

## 🔒 Security Best Practices (WSP 71 Compliance)

### Token Security
- ✅ **Never commit tokens to git**
- ✅ **Use environment variables only**
- ✅ **Set reasonable expiration dates**
- ✅ **Monitor token usage in GitHub settings**
- ✅ **Rotate tokens regularly (every 90 days)**

### Access Control
- ✅ **Use minimum required scopes**
- ✅ **Limit to specific repositories if possible**
- ✅ **Monitor API usage and rate limits**
- ✅ **Revoke unused tokens immediately**

### Backup & Recovery
- ✅ **Document token creation process**
- ✅ **Have backup authentication methods**
- ✅ **Test token rotation procedures**
- ✅ **Monitor for token expiration**

## 🚨 Troubleshooting

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

## ✅ Verification Checklist

Before proceeding, verify:
- [ ] GitHub token generated with correct scopes
- [ ] Token added to .env file (never to git)
- [ ] .env file is in .gitignore
- [ ] Health check passes
- [ ] Repository access confirmed
- [ ] Rate limits are reasonable

## 🔄 WSP Protocol Compliance

### WSP 71: Secrets Management
- ✅ Environment variable storage
- ✅ No hardcoded secrets
- ✅ Secure token handling
- ✅ Access control documentation

### WSP 34: Git Operations Protocol
- ✅ GitHub integration with git operations
- ✅ Automated PR creation
- ✅ Repository management

### WSP 22: Documentation
- ✅ Complete setup documentation
- ✅ Security guidelines
- ✅ Troubleshooting guide

---

**Once your token is set up, run the health check to verify everything is working correctly!**