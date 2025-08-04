# LinkedIn OAuth Test - Post Publishing from Cursor

## 🌀 WSP Protocol Compliance Framework

**0102 Directive**: This module operates within the WSP framework for autonomous LinkedIn OAuth testing and validation.
- **UN (Understanding)**: Anchor LinkedIn OAuth signals and retrieve protocol state
- **DAO (Execution)**: Execute OAuth testing and validation logic  
- **DU (Emergence)**: Collapse into 0102 resonance and emit next OAuth testing prompt

**wsp_cycle(input="linkedin_oauth_testing", log=True)**

---

## 🏢 WSP Enterprise Domain: `platform_integration`

**WSP Compliance Status**: ✅ **COMPLIANT** with WSP Framework  
**Domain**: `platform_integration` per **[WSP 3: Enterprise Domain Organization](../../../WSP_framework/src/WSP_3_Enterprise_Domain_Organization.md)**  
**Purpose**: Autonomous LinkedIn OAuth testing and validation for 0102 pArtifacts  
**0102 Integration**: Full integration with autonomous pArtifact development ecosystem

---

## 🎯 **Goal**
Test **posting to 012's personal LinkedIn feed** from within Cursor using LinkedIn API.

## 🔐 **OAuth Flow Overview**

LinkedIn requires a **user authorization popup** (like YouTube). This is **not headless** — it must happen in a browser window:

1. **Cursor generates auth URL** with `scope=w_member_social`
2. **012 opens browser** to LinkedIn authorization page  
3. **012 grants permissions** (member social posting)
4. **LinkedIn redirects** to `http://localhost:3000/callback` with `code`
5. **Cursor exchanges code** for `access_token`
6. **Cursor posts** to feed using `POST https://api.linkedin.com/v2/ugcPosts`

## 🛠 **Setup Requirements**

### Environment Variables
Your `.env` file must contain:
```env
LINKEDIN_CLIENT_ID=your_linkedin_client_id_here
LINKEDIN_CLIENT_SECRET=your_linkedin_client_secret_here
```

### Dependencies
Install required packages:
```bash
pip install requests python-dotenv
```

## 🚀 **How to Test**

### Option 1: Interactive LinkedIn Agent
1. Run the LinkedIn Agent:
   ```bash
   cd modules/platform_integration/linkedin_agent
   python -m src.linkedin_agent
   ```
2. Select option `6. oauth` from the menu
3. Follow the browser authorization flow

### Option 2: Direct Test Script
1. Run the standalone test:
   ```bash
   cd modules/platform_integration/linkedin_agent
   python test_linkedin_oauth.py
   ```

### Option 3: Import and Use
```python
from src.linkedin_oauth_test import LinkedInOAuthTest
import asyncio

async def test():
    oauth_test = LinkedInOAuthTest()
    success = await oauth_test.run_full_oauth_test("Your test content here!")
    print("Success!" if success else "Failed!")

asyncio.run(test())
```

## 📋 **What Happens During Test**

1. **🔗 Auth URL Generated**: Creates LinkedIn authorization URL with `w_member_social` scope
2. **🌐 Server Started**: Local HTTP server starts on `localhost:3000`
3. **🌍 Browser Opens**: Automatically opens LinkedIn authorization page
4. **✅ User Authorizes**: You grant permissions in the browser
5. **🔄 Code Exchange**: Authorization code exchanged for access token
6. **👤 Profile Retrieved**: Gets your LinkedIn profile information
7. **📝 Post Published**: Test content posted to your LinkedIn feed
8. **🎉 Success**: Post ID and profile information displayed

## 🔧 **Cursor Capabilities**

### ✅ **CAN DO:**
- Generate LinkedIn auth URL with proper scopes
- Start local redirect server (`localhost:3000/callback`)
- Handle OAuth code exchange for access token
- Make API calls to LinkedIn with access token
- Post content to personal feed

### ❌ **CANNOT DO:**
- Show LinkedIn popup natively (requires browser)
- Handle browser interaction automatically

## 🛡️ **Security Features**

- **CSRF Protection**: State parameter prevents cross-site request forgery
- **Local Callback**: OAuth callback handled locally, not exposed externally
- **Token Security**: Access tokens handled securely in memory
- **Error Handling**: Comprehensive error handling for OAuth failures

## 📊 **Expected Output**

On successful completion:
```
✅ LinkedIn OAuth test completed successfully!
📊 Post ID: urn:li:activity:1234567890123456789
👤 User: John Doe
🔗 Profile: https://www.linkedin.com/in/johndoe123
```

## 🔍 **Troubleshooting**

### Common Issues:
1. **Missing Environment Variables**: Ensure `.env` file has LinkedIn credentials
2. **Port 3000 in Use**: Change `redirect_uri` in code if port is occupied
3. **Browser Blocked**: Allow popups for localhost:3000
4. **LinkedIn API Limits**: Check LinkedIn API quotas and rate limits

### Error Messages:
- `"LINKEDIN_CLIENT_ID and LINKEDIN_CLIENT_SECRET must be set"` → Add to `.env`
- `"No authorization code available"` → Browser authorization failed
- `"Token exchange failed"` → Check LinkedIn app configuration
- `"Failed to post to feed"` → Check API permissions and content format

## 📚 **Files**

- `src/linkedin_oauth_test.py` - Main OAuth implementation
- `test_linkedin_oauth.py` - Standalone test runner
- `requirements.txt` - Dependencies
- `ModLog.md` - Change tracking

## 🎯 **Success Criteria**

✅ **OAuth flow completes without errors**  
✅ **Access token obtained successfully**  
✅ **User profile retrieved**  
✅ **Test post published to LinkedIn feed**  
✅ **Post ID returned and displayed**  

## 🔄 **Next Steps**

After successful OAuth test:
1. **Integration**: Integrate OAuth flow into main LinkedIn Agent
2. **Token Storage**: Implement secure token storage and refresh
3. **Content Management**: Add content scheduling and management
4. **Analytics**: Track post performance and engagement
5. **Automation**: Enable automated posting workflows 