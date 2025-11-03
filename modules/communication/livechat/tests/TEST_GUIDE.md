# YouTube Agent System - Systematic Test Guide

## [TARGET] TEST PROTOCOL: PoC -> Prototype -> MVP

### Prerequisites
1. Bot must be running: `python main.py` -> Option 1
2. You must be in a live YouTube stream chat
3. Have mod permissions for full testing

---

## [CLIPBOARD] PHASE 1: PoC TESTING (Basic Functionality)

### 1.1 AUTO-CAPTURE TEST [OK]
**Test:** Send any message in chat
**Expected:** 
- Bot captures your user ID
- Assigns role (OWNER/MOD/MEMBER/USER)
- Gives XP bonus (Owner: 1000, Mod: 500, Member: 100)
**Commands to test:**
```
Regular message: "Hello"
Check capture: /score
```

### 1.2 BASIC COMMANDS TEST 
**Test these commands in chat:**
```
/score     -> Shows your XP and level
/rank      -> Shows your position on leaderboard  
/level     -> Shows progress bar to next level
/points    -> Shows point breakdown
/help      -> Shows available commands
```

### 1.3 WHACK-A-MAGA TEST [U+1F528]
**Test:** Send MAGA/Trump keywords
```
Test messages:
"MAGA 2024"
"Trump is great"
"I love Trump"
```
**Expected:**
- Bot detects MAGA keywords
- Sends troll response
- Issues 10-second timeout
- Awards points to moderator

### 1.4 MOD TIMEOUT SCORING
**As Moderator, test:**
```
/timeout @username 60     -> 60 second timeout
/timeout @username 300    -> 5 minute timeout
/timeout @username 600    -> 10 minute timeout
```
**Expected:**
- Timeout executed
- Points awarded based on duration
- Anti-gaming rules apply

### 1.5 EMOJI SEQUENCE TEST
**Test these sequences:**
```
[U+270A][U+270A][U+270A]     -> 000 consciousness (blocked)
[U+270A][U+270A][U+270B]     -> 001 emergence
[U+270A][U+270B][U+270B]     -> 011 formation
[U+270B][U+270B][U+270B]     -> 111 DAO (triggers response)
[U+270B][U+270B][U+1F590]️    -> 112 resonance
[U+270B][U+1F590]️[U+1F590]️   -> 122 yielding
[U+1F590]️[U+1F590]️[U+1F590]️  -> 222 full entanglement
```
**Expected:** BanterEngine responds based on consciousness level

---

## [CLIPBOARD] PHASE 2: PROTOTYPE TESTING (Enhanced Features)

### 2.1 RPG COMMANDS TEST
```
/stats        -> D&D character sheet
/class        -> View/choose character class
/achievements -> List earned achievements
/leaderboard  -> Top 10 players
/daily        -> Claim daily bonus
/quest        -> View daily quests
```

### 2.2 ACHIEVEMENT TRIGGERS
**Test these actions:**
- First timeout -> "First Blood" achievement
- 10 timeouts -> "Decimator" achievement  
- 5 timeouts in 60 seconds -> "Speed Demon"
- Help 2 members -> Helper achievement

### 2.3 ANTI-GAMING MECHANICS
**Test rapid timeouts:**
1. Timeout same user twice -> Reduced points
2. Spam 10-second timeouts -> No points after 5
3. Timeout 50+ users in one day -> Soft cap

### 2.4 DATABASE PERSISTENCE
1. Note your current XP: `/score`
2. Restart the bot (Ctrl+C, restart)
3. Check XP again: `/score`
**Expected:** XP persists across sessions

### 2.5 LEADERBOARD COMPETITION
```
/leaderboard      -> View top 10
/leaderboard 25   -> View top 25
```
**Test:** Multiple users gain XP, verify ranking updates

---

## [CLIPBOARD] PHASE 3: INTEGRATION TESTING

### 3.1 AUTO-MODERATION
**Test spam detection:**
```
Send 6 messages in 30 seconds
Send identical message 3 times
Use multiple MAGA keywords
```
**Expected:** Escalating timeouts

### 3.2 GIFT/SUPERCHAT DETECTION
**Test:** Send Super Chat or gift membership
**Expected:** 
- Instant response
- Bonus XP for gifter
- Special acknowledgment

### 3.3 QUIZ SYSTEM
```
/quiz     -> Get fascism awareness question
/facts    -> Get 1933 parallel fact
/fscale   -> F-scale personality test
```

### 3.4 PARTY SYSTEM (Prototype)
```
/party create "Anti-Fascist Squad"
/party invite @username
/party raid
```

---

## [SEARCH] MONITORING & LOGS

### Check Live Logs
**Log Location:** `modules/communication/livechat/memory/chat_logs/live_chat_debug.log`

### Database Inspection
**Database:** `modules/communication/chat_rules/data/chat_rules.db`

**SQL Queries to check:**
```sql
-- View all captured users
SELECT * FROM moderators ORDER BY total_points DESC;

-- View timeout history
SELECT * FROM timeout_history ORDER BY timestamp DESC;

-- View achievements
SELECT * FROM achievements;

-- Check cooldowns
SELECT * FROM cooldowns WHERE expires_at > datetime('now');
```

### Error Patterns to Watch
1. **Unicode Errors** - Expected on Windows, bot continues
2. **Rate Limiting** - 60 requests/minute max
3. **Quota Exceeded** - Switches to next credential set
4. **Connection Timeouts** - Auto-reconnects

---

## [DATA] SUCCESS METRICS

### PoC Success [OK]
- [ ] Users auto-captured with roles
- [ ] Basic commands working (/score, /rank, etc.)
- [ ] MAGA detection and timeout working
- [ ] Points system tracking scores
- [ ] Database persisting data

### Prototype Success
- [ ] RPG leveling 1-100 working
- [ ] Achievements unlocking
- [ ] Anti-gaming rules enforced
- [ ] Leaderboard updating correctly
- [ ] Daily quests and bonuses

### Integration Success
- [ ] Multi-user coordination
- [ ] Spam protection active
- [ ] Emoji sequences trigger responses
- [ ] No critical errors in 30 minutes
- [ ] Session summary shows all captured users

---

## [U+1F41B] TROUBLESHOOTING

### Bot Not Responding
1. Check if live stream is active
2. Verify OAuth credentials valid
3. Check quota limits
4. Restart bot

### Commands Not Working
1. Ensure message starts with `/`
2. Check if you have required permissions
3. Verify database is not locked
4. Check for typos in command

### Points Not Awarded
1. Check anti-gaming cooldowns
2. Verify room activity > 30 msgs/5min
3. Check if target was already timed out
4. Ensure you're a moderator

### Database Issues
1. Delete `chat_rules.db` to reset
2. Check file permissions
3. Ensure SQLite3 installed
4. No other process locking DB

---

## [NOTE] TEST CHECKLIST

**PoC Features (Must Work):**
- [ ] Auto-capture users
- [ ] /score command
- [ ] /rank command  
- [ ] /level command
- [ ] MAGA timeout
- [ ] Point scoring
- [ ] Database saves

**Prototype Features (Should Work):**
- [ ] Character classes
- [ ] Achievements
- [ ] Daily bonuses
- [ ] Quests
- [ ] Anti-gaming
- [ ] Leaderboard

**MVP Features (Future):**
- [ ] Gemini AI integration
- [ ] Raid bosses
- [ ] PvP dueling
- [ ] Item shop
- [ ] Prestige system

---

## [ROCKET] QUICK TEST SEQUENCE

1. **Start bot:** `python main.py` -> 1
2. **In chat, type:**
   - "Hello" (captures you)
   - "/score" (shows XP)
   - "MAGA 2024" (triggers timeout)
   - "/rank" (shows position)
   - "[U+270B][U+270B][U+270B]" (emoji response)
   - "/stats" (character sheet)
   - "/daily" (bonus XP)
   - "/leaderboard" (top players)
3. **As mod:** "/timeout @troll 300"
4. **Check database:** Captured users and points
5. **Restart bot:** Data persists
6. **Session complete!**

---

**Testing Duration:** 15-30 minutes for full PoC
**Required:** YouTube channel with active chat
**Best Practice:** Test with 2-3 users for interaction