# OAuth Client ID Configuration

## For Desktop App (Recommended for Bot)
**Application type:** Desktop app
- No URLs needed!
- Works with local authorization flow
- Best for bots and CLI tools

## For Web Application (If Required)

### Authorized JavaScript origins:
```
http://localhost
http://localhost:8080
http://localhost:8090
http://127.0.0.1:8080
```

### Authorized redirect URIs:
```
http://localhost:8080/
http://localhost:8080/oauth2callback
http://localhost:8090/
http://localhost/oauth2callback
http://127.0.0.1:8080/oauth2callback
urn:ietf:wg:oauth:2.0:oob
```

## Which to Choose?

**For this YouTube bot: Use "Desktop app"**
- Simpler setup
- No redirect URLs needed
- Works perfectly for automated bots

**Steps for Desktop App:**
1. Application type: **Desktop app**
2. Name: `foundups-agent5-bot`
3. Click Create
4. Download JSON
5. Done! No URLs needed

## If You Already Created Web App

You can either:
1. Delete it and create Desktop app instead (recommended)
2. Or add the localhost URLs above

The Desktop app is much simpler for bots!