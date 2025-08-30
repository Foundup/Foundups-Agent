# LinkedIn Authorization - Step by Step Instructions

## What's Happening:
Chrome just opened with the LinkedIn authorization page.

## Step-by-Step Instructions:

### 1. SIGN IN TO LINKEDIN
- Enter your LinkedIn email and password
- Click "Sign in"

### 2. AUTHORIZE THE APP
You'll see a page that says something like:
```
FoundUps-Agent is requesting access to your LinkedIn account

This will allow FoundUps-Agent to:
• Create, modify, and delete posts, comments, and reactions
• Retrieve your basic profile

[Allow]  [Deny]
```

**Click the "Allow" button**

### 3. YOU'LL GET AN ERROR PAGE
After clicking Allow, you'll see:
```
This site can't be reached
localhost refused to connect.
```

**THIS ERROR IS NORMAL AND EXPECTED!**

### 4. LOOK AT THE URL
In your browser's address bar, you'll see something like:
```
http://localhost:3000/callback?code=AQTh3K9Xu7RmC8N...&state=0102
```

### 5. COPY THE ENTIRE URL
- Click in the address bar
- Select all (Ctrl+A)
- Copy (Ctrl+C)
- Come back here and paste it

## Example of What to Copy:
The full URL from your browser, like:
```
http://localhost:3000/callback?code=AQTh3K9Xu7RmC8NvT5y2JKLMopqrstuvwxyz1234567890abcdefghijk&state=0102
```

## What I Need:
Either:
- The FULL URL (recommended)
- OR just the code part: `AQTh3K9Xu7RmC8NvT5y2JKLMopqrstuvwxyz1234567890abcdefghijk`

## Common Issues:

### "The redirect_uri does not match"
- This means we're using the wrong port
- We fixed this - now using port 3000

### "Invalid client_id"
- We fixed this - removed the extra ^ character

### Don't see an Allow button?
- Make sure you're signed into LinkedIn
- Try refreshing the page
- Check if you already authorized before (might auto-redirect)

## Ready?
1. Chrome is open with the authorization page
2. Sign in to LinkedIn
3. Click "Allow"
4. Copy the URL from the error page
5. Paste it here