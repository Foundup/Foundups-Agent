# Billing Account Limit - Workarounds

## Problem
- Google limits projects per billing account (usually 5-10)
- You've reached the maximum
- foundups-agent5 can't be added to billing

## Solutions

### Option 1: Remove Billing from Unused Project
1. Go to Billing → My Projects
2. Find a project you're not using (maybe an old one)
3. Click "⋮" menu → "Disable billing"
4. Now add foundups-agent5 to billing

### Option 2: Use Without Billing (10K quota)
- foundups-agent5 still gets 10,000 daily quota
- With conservative polling (30-120 sec), runs 50+ hours
- Add it as Set 5 with free quota

### Option 3: Check Exhausted Projects
Your existing projects might have quota if you:
1. Request quota increase (10K → 1M)
2. Or wait for midnight PT reset
3. Projects with billing but stuck at 10K need manual increase

### Option 4: Create Second Billing Account
1. Go to Billing → Manage billing accounts
2. Create new billing account
3. Add payment method
4. Link foundups-agent5 to new billing

## Current Setup Recommendation

Since you have client_secret5.json ready:

1. **Use it with 10K free quota for now**
2. **Add to .env:**
```env
# Set 5 - foundups-agent5 (free tier 10K)
GOOGLE_CLIENT_SECRETS_FILE_5=credentials/client_secret5.json
OAUTH_TOKEN_FILE_5=credentials/oauth_token5.json
```

3. **It still helps!**
- Extra 10K quota daily
- Total: 40K (Sets 1-4) + 10K (Set 5) = 50K
- Can run 10+ days with conservative polling!

## Priority Actions

1. ✅ Add Set 5 even without billing (extra 10K helps!)
2. 📝 Request quota increases on Sets 2,3,4 (billing-enabled)
3. ⏰ Wait for midnight PT for quota reset
4. 🔄 Consider removing billing from unused projects

## Remember
Even 10K free quota = 50+ hours runtime with new polling!