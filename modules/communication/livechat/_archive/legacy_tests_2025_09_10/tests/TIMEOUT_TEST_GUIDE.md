# Mod Timeout Testing Guide

## Test Setup
1. Bot must be running: `python main.py` → Option 1
2. You must be a MOD or OWNER in the stream
3. Have some test users ready to timeout

## Test Commands

### Basic Timeout Tests

#### Test 1: Simple Timeout
**As a MOD, type:**
```
/timeout @testuser
```
**Expected:** 
- User gets 60 second timeout (default)
- Bot responds with points earned
- Database records the action

#### Test 2: Custom Duration
**Try these durations:**
```
/timeout @user1 10      # 10 seconds (minimal)
/timeout @user2 60      # 1 minute
/timeout @user3 300     # 5 minutes  
/timeout @user4 600     # 10 minutes
/timeout @user5 3600    # 1 hour
/timeout @user6 86400   # 24 hours (max)
```
**Expected:** Different point values based on severity

#### Test 3: Timeout with Reason
```
/timeout @troll 300 Spamming MAGA propaganda
```
**Expected:** Timeout with reason logged

## Anti-Gaming Tests

### Test 4: Repeat Timeouts (Same User)
**Timeout same user multiple times:**
```
/timeout @repeatoffender 60
(wait 5 seconds)
/timeout @repeatoffender 60
```
**Expected:** 
- Second timeout gives reduced/no points
- Anti-gaming message appears

### Test 5: Spam Prevention
**Rapidly timeout 5+ different users with 10-second timeouts:**
```
/timeout @user1 10
/timeout @user2 10
/timeout @user3 10
/timeout @user4 10
/timeout @user5 10
/timeout @user6 10
```
**Expected:** After 5 timeouts, no more points for 10-second timeouts

### Test 6: Daily Limit
**Try to timeout 50+ users in one session**
**Expected:** Soft cap activates, reduced points after threshold

## Database Verification

### Check Your Stats
```
/score      # Your total XP
/points     # Point breakdown
```

### Check Timeout History
The database tracks:
- Total timeouts issued
- Points earned
- Timeout duration distribution
- Anti-gaming penalties applied

## Point Values (No Gaming)

| Duration | Points | Use Case |
|----------|--------|----------|
| 10 sec   | 5      | Warning |
| 60 sec   | 10     | Minor violation |
| 5 min    | 25     | Moderate violation |
| 10 min   | 50     | Serious violation |
| 1 hour   | 100    | Major violation |
| 24 hours | 200    | Ban-level violation |

## Success Metrics

✅ **PoC Success:**
- [ ] Basic timeout command works
- [ ] Points are awarded
- [ ] Database saves timeout history

✅ **Anti-Gaming Success:**
- [ ] Repeat timeouts detected
- [ ] Spam prevention active
- [ ] Daily limits enforced
- [ ] Cooldowns working

## Troubleshooting

**"Unknown command: /timeout"**
- You're not a mod/owner
- Use !timeout instead

**No points awarded:**
- Check anti-gaming cooldowns
- User might be recently timed out
- Daily limit might be reached

**Bot not responding:**
- Ensure you're a mod/owner
- Check if bot is still running
- Verify livestream is active