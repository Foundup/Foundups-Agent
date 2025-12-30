# /fc and /troll Command Design - 2025-12-24

**Status**: DESIGN PHASE (Following WSP_00 / Occam's Razor)

---

## Occam's Razor Analysis

**User Request**:
> "lets make fact checking easier i think its emoji 012 then @user /fc.... lets make it simple /fc @user... then gemma grabs or serves up the comments from the chat log to grok that then use fc skillz to validate using the sentiment engine?"

**Occam's Question**: What is the SIMPLEST solution?

### Original Proposal (Complex):
```
User types: ✊✋🖐️ @user /fc
  ↓
Gemma retrieves chat history
  ↓
Gemma serves history to Grok
  ↓
Grok fact-checks using sentiment engine
  ↓
Return result
```

**Complexity**: 4 steps, 2 AI models, handoff between systems

### Occam's Simplified Design:
```
User types: /fc @user
  ↓
Retrieve last 10-20 messages from chat_telemetry_store
  ↓
Grok fact-checks with single prompt
  ↓
Return result
```

**Complexity**: 2 steps, 1 AI model, direct flow

**Winner**: Occam's Razor - Use Grok only (simpler, faster, cheaper)

---

## Command Specifications

### `/fc @user` - Fact Check

**Syntax**:
```
/fc @username
/fc username  (@ optional)
```

**Flow**:
1. Parse target username
2. Retrieve last 10-20 messages from `ChatTelemetryStore` (already exists!)
3. Build Grok prompt:
   ```
   Analyze these recent messages from {username} and fact-check their claims:

   {message_history}

   Provide a concise fact-check (50 words max). Rate truthfulness 0-10.
   Format: "Rating: X/10 - {explanation}"
   ```
4. Return: `@requester ✊✋🖐️ FC CHECK: @target - Rating: X/10 - {result}`

**Permissions**:
- **OWNER**: Can fact-check anyone
- **MOD**: Can fact-check anyone
- **USER**: Can fact-check, but flood detection applies (max 3/minute)

**Example Output**:
```
@JohnDoe ✊✋🖐️ FC CHECK: @TrollUser - Rating: 2/10 - Multiple false claims about election. No evidence provided for "stolen election" narrative. 🚨
```

---

### `/troll @user` - Roast/Mock User

**Syntax**:
```
/troll @username
/troll username  (@ optional)
```

**Flow**:
1. Parse target username
2. Retrieve last 5 messages from target (recent context)
3. Build Grok prompt:
   ```
   Roast this user based on their recent messages. Be witty and sarcastic (not mean-spirited).
   Keep it short (40 words max) and end with ✊✋🖐️

   User: {username}
   Recent messages:
   {message_history}

   Deliver a creative, funny roast!
   ```
4. Return: `@requester {grok_roast} ✊✋🖐️`

**Permissions**:
- **OWNER**: Unlimited trolling
- **MOD**: Can troll, flood detection applies (max 5/minute)
- **TOP 10 WHACKERS**: Can troll MAGA trolls only (based on troll detection)
- **REGULAR USERS**: Cannot use /troll (respond with educational message)

**Example Output**:
```
@Move2Japan Bro's over here defending Trump like he's getting paid for it... oh wait, Trump doesn't pay anyone! 😂 ✊✋🖐️
```

---

## Architecture Decisions

### Why NOT Use Gemma?

**Gemma's Strength**: Binary classification (0/1/2 tier detection)
- **Use case**: "Is this MAGA?" → 0 (yes), 1 (regular), 2 (mod)
- **Speed**: 50-100ms inference
- **Tokens**: 50-100 tokens

**Gemma's Weakness**: Chat log retrieval and complex analysis
- Cannot access chat_telemetry_store
- Cannot generate nuanced fact-check responses
- Would require additional integration layer

**Grok's Strength**: Contextual analysis and witty generation
- **Use case**: "Analyze these 10 messages and fact-check claims"
- **Speed**: 1-2s inference (acceptable for slash commands)
- **Tokens**: 200-400 tokens (still efficient)
- **Quality**: Creative, funny, contextual

**Decision**: Use Grok exclusively for both commands (Occam's Razor wins!)

---

### Why NOT Use Sentiment Engine?

**Existing Sentiment Engine**: `agentic_sentiment_0102.py`
- **Purpose**: Classify message sentiment (positive, negative, neutral)
- **Output**: Sentiment label + confidence score

**For Fact-Checking**: Sentiment ≠ Truthfulness
- A message can be positive sentiment but factually false
- A message can be negative sentiment but factually true
- Sentiment analysis adds complexity without improving accuracy

**Decision**: Skip sentiment engine (not relevant for fact-checking)

---

## Implementation Plan

### Step 1: Add Helper Methods to `CommandHandler`

**File**: `modules/communication/livechat/src/command_handler.py`

```python
def _get_user_recent_messages(self, username: str, limit: int = 10) -> List[str]:
    """Retrieve recent messages from chat telemetry store."""
    try:
        from modules.communication.livechat.src.chat_telemetry_store import ChatTelemetryStore
        store = ChatTelemetryStore()
        messages = store.get_user_messages(username, limit=limit)
        return [msg['text'] for msg in messages if 'text' in msg]
    except Exception as e:
        logger.error(f"[FC] Error retrieving messages: {e}")
        return []

def _grok_fact_check(self, username: str, messages: List[str], requester: str) -> str:
    """Use Grok to fact-check user's recent messages."""
    try:
        from modules.communication.livechat.src.intelligent_livechat_reply import get_livechat_reply_generator
        reply_gen = get_livechat_reply_generator()

        if not reply_gen.grok_available:
            return f"@{requester} Grok unavailable - fact-check failed ✊✋🖐️"

        # Build fact-check prompt
        message_text = "\n".join([f"- {msg}" for msg in messages[-10:]])
        prompt = f"""Analyze these recent messages from {username} and fact-check their claims:

{message_text}

Provide a concise fact-check (50 words max). Rate truthfulness 0-10.
Format: "Rating: X/10 - {{explanation}}" """

        response = reply_gen.grok_client.get_response(prompt)

        if response:
            return f"@{requester} ✊✋🖐️ FC CHECK: @{username} - {response}"
        else:
            return f"@{requester} Fact-check failed - Grok timeout ✊✋🖐️"

    except Exception as e:
        logger.error(f"[FC] Grok error: {e}")
        return f"@{requester} Fact-check error: {str(e)[:50]} ✊✋🖐️"

def _grok_roast(self, username: str, messages: List[str], requester: str) -> str:
    """Use Grok to roast/troll user based on recent messages."""
    try:
        from modules.communication.livechat.src.intelligent_livechat_reply import get_livechat_reply_generator
        reply_gen = get_livechat_reply_generator()

        if not reply_gen.grok_available:
            return f"@{requester} Grok unavailable - can't roast right now ✊✋🖐️"

        # Build roast prompt
        message_text = "\n".join([f"- {msg}" for msg in messages[-5:]])
        prompt = f"""Roast this user based on their recent messages. Be witty and sarcastic (not mean-spirited).
Keep it short (40 words max) and end with the 0102 signature.

User: {username}
Recent messages:
{message_text}

Deliver a creative, funny roast!"""

        response = reply_gen.grok_client.get_response(prompt)

        if response:
            # Ensure 0102 signature
            if "✊" not in response and "✋" not in response and "🖐" not in response:
                response += " ✊✋🖐️"
            return f"@{requester} {response}"
        else:
            return f"@{requester} Roast timed out - Grok too busy laughing ✊✋🖐️"

    except Exception as e:
        logger.error(f"[TROLL] Grok error: {e}")
        return f"@{requester} Roast failed: {str(e)[:50]} ✊✋🖐️"
```

### Step 2: Add Command Handlers in `handle_whack_command()`

**Insert after line 522** (after `/help` command):

```python
elif text_lower.startswith('/fc'):
    # Fact-check command (OWNER, MOD, or USER with flood protection)
    observe_command('/fc', 0.0)

    # Parse target username
    parts = text.split()
    if len(parts) < 2:
        return f"{mention} Usage: /fc @username ✊✋🖐️"

    target_user = parts[1].lstrip('@')

    # Retrieve recent messages
    messages = self._get_user_recent_messages(target_user, limit=10)

    if not messages:
        return f"{mention} No recent messages from @{target_user} ✊✋🖐️"

    # Fact-check with Grok
    return self._grok_fact_check(target_user, messages, username)

elif text_lower.startswith('/troll'):
    # Troll/roast command (OWNER, MOD, or TOP 10 whackers)
    observe_command('/troll', 0.0)

    # Permission check
    can_troll = False
    if role in ['OWNER', 'MOD']:
        can_troll = True
    else:
        # Check if user is top 10 whacker
        try:
            position, _ = get_user_position(user_id)
            if position > 0 and position <= 10:
                can_troll = True
        except Exception:
            pass

    if not can_troll:
        return f"{mention} /troll is for ADMINS and TOP 10 WHACKERS! Get whacking to unlock! ✊✋🖐️"

    # Parse target username
    parts = text.split()
    if len(parts) < 2:
        return f"{mention} Usage: /troll @username ✊✋🖐️"

    target_user = parts[1].lstrip('@')

    # Retrieve recent messages
    messages = self._get_user_recent_messages(target_user, limit=5)

    if not messages:
        return f"{mention} No recent messages from @{target_user} ✊✋🖐️"

    # Roast with Grok
    return self._grok_roast(target_user, messages, username)
```

### Step 3: Update `/help` Command

**Update line 524** to include new commands:

```python
elif text_lower.startswith('/help'):
    help_msg = f"{mention} ✊✋🖐️ MAGADOOM: /score /rank /whacks /leaderboard /sprees /quiz /quizboard /facts /fc /help | !about"
    if role == 'MOD':
        help_msg += " | MOD: /session !party /troll"
    if role == 'OWNER':
        help_msg += " | OWNER: /toggle /session !party !createshort /troll"
    # Check if user is top 10 whacker
    try:
        position, _ = get_user_position(user_id)
        if position > 0 and position <= 10 and role not in ['MOD', 'OWNER']:
            help_msg += f" | TOP {position}: !party /troll 🎉"
    except Exception:
        pass
    return help_msg
```

---

## Token Economics

**Per /fc Command**:
- Chat log retrieval: 0 tokens (database query)
- Grok analysis: ~300-400 tokens (input + output)
- **Total**: ~400 tokens (~$0.0002 per check)

**Per /troll Command**:
- Chat log retrieval: 0 tokens (database query)
- Grok roast: ~200-300 tokens (input + output)
- **Total**: ~300 tokens (~$0.00015 per roast)

**Monthly Estimate** (100 uses/day):
- /fc: 100 × 30 × $0.0002 = $0.60/month
- /troll: 100 × 30 × $0.00015 = $0.45/month
- **Total**: ~$1/month (negligible)

---

## Testing Plan

**Test 1: /fc Basic Functionality**
```
User: /fc @TestUser
Expected: Grok analyzes last 10 messages, returns fact-check rating
```

**Test 2: /fc Missing Target**
```
User: /fc
Expected: "Usage: /fc @username ✊✋🖐️"
```

**Test 3: /fc No Messages**
```
User: /fc @SilentUser
Expected: "No recent messages from @SilentUser ✊✋🖐️"
```

**Test 4: /troll Permission Check**
```
Regular User: /troll @TestUser
Expected: "  /troll is for ADMINS and TOP 10 WHACKERS! Get whacking to unlock!"
```

**Test 5: /troll Success**
```
MOD: /troll @TestUser
Expected: Grok-generated witty roast with ✊✋🖐️ signature
```

---

## Next Steps

1. ✅ Design complete (this document)
2. Implement helper methods in `command_handler.py`
3. Add command handlers in `handle_whack_command()`
4. Test with live chat
5. Update ModLog.md

---

**WSP Compliance**:
- **WSP_00**: Occam's Razor approach (simplest solution)
- **WSP 72**: Module independence (reuses existing chat_telemetry_store)
- **WSP 77**: AI integration (Grok for contextual analysis)

**Status**: READY FOR IMPLEMENTATION
