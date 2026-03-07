# WSP Module Placement Decision Matrix

## [U+1F3AF] Quick Decision Tree

```
Is it about...
[U+2502]
[U+251C][U+2500] Points/XP/Levels/Games?
[U+2502]  [U+2514][U+2500] YES -> modules/gamification/[game_name]/src/
[U+2502]
[U+251C][U+2500] Chat moderation/filtering?
[U+2502]  [U+2514][U+2500] YES -> modules/communication/chat_rules/src/
[U+2502]
[U+251C][U+2500] YouTube Live Chat API?
[U+2502]  [U+2514][U+2500] YES -> modules/communication/livechat/src/
[U+2502]
[U+251C][U+2500] AI/LLM responses?
[U+2502]  [U+2514][U+2500] YES -> modules/ai_intelligence/[model_name]/src/
[U+2502]
[U+251C][U+2500] OAuth/External APIs?
[U+2502]  [U+2514][U+2500] YES -> modules/platform_integration/[platform_name]/src/
[U+2502]
[U+2514][U+2500] Still unsure?
   [U+2514][U+2500] Ask: "What is the PRIMARY PURPOSE?"
      [U+2514][U+2500] That determines the domain!
```

## [U+1F4CA] Decision Matrix Table

| Feature | Domain | Block | Example Path |
|---------|--------|-------|--------------|
| **XP/Points System** | gamification | [game_name] | `gamification/whack_a_magat/src/whack.py` |
| **Leveling/Ranks** | gamification | rpg_system | `gamification/rpg_system/src/leveling.py` |
| **Game Commands** | gamification | [game_name] | `gamification/whack_a_magat/src/commands.py` |
| **Leaderboards** | gamification | [game_name] | `gamification/whack_a_magat/src/leaderboard.py` |
| **Timeout Tracking** | gamification | whack_a_magat | `gamification/whack_a_magat/src/timeout_tracker.py` |
| **Game Announcements** | gamification | [game_name] | `gamification/whack_a_magat/src/announcer.py` |
| **Chat Filtering** | communication | chat_rules | `communication/chat_rules/src/filter.py` |
| **Spam Detection** | communication | chat_rules | `communication/chat_rules/src/spam_detector.py` |
| **Bad Words** | communication | chat_rules | `communication/chat_rules/src/profanity_filter.py` |
| **Rate Limiting** | communication | chat_rules | `communication/chat_rules/src/rate_limiter.py` |
| **YouTube Polling** | communication | livechat | `communication/livechat/src/chat_poller.py` |
| **Chat Sending** | communication | livechat | `communication/livechat/src/chat_sender.py` |
| **Message Processing** | communication | livechat | `communication/livechat/src/message_processor.py` |
| **Banter Responses** | ai_intelligence | banter_engine | `ai_intelligence/banter_engine/src/banter.py` |
| **LLM Integration** | ai_intelligence | llm_interface | `ai_intelligence/llm_interface/src/connector.py` |
| **YouTube Auth** | platform_integration | youtube_auth | `platform_integration/youtube_auth/src/oauth.py` |
| **Twitter API** | platform_integration | twitter_api | `platform_integration/twitter_api/src/client.py` |

## [WARNING][U+FE0F] Common Confusion Points

### "But it's used in chat!"
**WRONG THINKING:** "Game commands are used in chat, so they go in chat_rules"
**CORRECT THINKING:** "Game commands are GAMING features, they go in gamification"

### "But it processes timeouts!"
**WRONG THINKING:** "Timeout handler goes with moderation"
**CORRECT THINKING:** "Timeout for POINTS goes in gamification, timeout for RULES goes in chat_rules"

### "But they work together!"
**WRONG THINKING:** "Keep related code in the same place"
**CORRECT THINKING:** "Separate by domain, connect via imports"

## [U+1F6AB] Red Flags - You're Doing It Wrong!

1. File contains "XP" or "points" -> Should be in `gamification/`
2. File contains "level" or "rank" -> Should be in `gamification/`
3. File contains "game" in name -> Should be in `gamification/`
4. File contains "leaderboard" -> Should be in `gamification/`
5. File handles YouTube API -> Should be in `livechat/`
6. File does AI responses -> Should be in `ai_intelligence/`

## [U+2705] Examples of CORRECT Placement

### Scenario 1: Timeout Points System
```
Feature: Award points when moderator times out a user
Domain: gamification (it's about points!)
Block: whack_a_magat (specific game)
File: modules/gamification/whack_a_magat/src/timeout_tracker.py
```

### Scenario 2: Chat Command Handler
```
Feature: Process /score, /level, /rank commands
Domain: gamification (these are game commands!)
Block: whack_a_magat (specific to this game)
File: modules/gamification/whack_a_magat/src/game_commands.py
```

### Scenario 3: Profanity Filter
```
Feature: Filter bad words from chat
Domain: communication (it's about chat moderation)
Block: chat_rules (rule enforcement)
File: modules/communication/chat_rules/src/profanity_filter.py
```

### Scenario 4: Send Chat Message
```
Feature: Send message to YouTube Live Chat
Domain: communication (it's about chat interaction)
Block: livechat (YouTube-specific)
File: modules/communication/livechat/src/chat_sender.py
```

## [U+1F4DD] Before Creating ANY Module:

1. **What is the PRIMARY PURPOSE?**
   - Gaming? -> gamification
   - Chat moderation? -> chat_rules
   - YouTube interaction? -> livechat
   - AI/LLM? -> ai_intelligence
   - External API? -> platform_integration

2. **Does it already exist?**
   ```bash
   grep -r "similar_functionality" modules/
   ```

3. **Is there a similar module in the right place?**
   ```bash
   ls modules/gamification/*/src/
   ```

4. **Will it be over 500 lines?**
   - If yes, plan to split it NOW

## [U+1F525] The Golden Rule:

**DOMAIN DETERMINES LOCATION, NOT USAGE!**

A game feature used in chat still goes in gamification.
A chat feature that awards points still has points logic in gamification.
Keep domains pure, use imports to connect.

---

*Use this matrix EVERY TIME before creating a module. No exceptions.*