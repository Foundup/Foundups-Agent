# GJ_50_AI_Voice_Assistant.md — 012 ↔ 0102 Voice Interface

## 1. Purpose

Enable **voice-based interaction** between the user (012) and the DAE system (0102) through the AI MIC icon in the navigation bar.

**Core Concept**:
- User speaks to the app via microphone
- 0102 DAE uses **decision skill** to route requests to appropriate wardrobe skills
- **WSP_77**: Local phone AI acts as DAE without cloud dependency (where possible)
- Vocal triggers → skill selection → task execution → voice response

---

## 2. Requirements

### 2.1 Navigation Bar Integration

**Location**: Bottom navigation bar (right side)

**Layout**: `[<] [>] ... [📷] [🎤]`
- `<` - Swipe left thumb toggle (delete)
- `>` - Swipe right thumb toggle (keep)
- `📷` - Camera icon (appears on ALL pages)
- `🎤` - AI MIC icon (voice interface to DAE system)

**Behavior**:
- Always visible on all pages (like camera icon)
- Tap to activate voice listening
- Shows visual feedback during listening/processing
- Disabled state initially (to implement in Phase 4+)

### 2.2 Voice Interaction Pattern (012 ↔ 0102)

**User (012)** → Voice Input → **DAE (0102)** → Decision Skill → **Wardrobe Skill** → Response

**Example Flows**:

1. **Item Classification**:
   - 012: "Classify this as free"
   - 0102: Uses `gotjunk_classify` skill → Updates item → "Done, marked as free"

2. **Map Navigation**:
   - 012: "Show me food alerts nearby"
   - 0102: Uses `map_filter` skill → Filters map → "Showing 3 food alerts within 5km"

3. **Liberty Alert Creation**:
   - 012: "ICE checkpoint at Main and 5th"
   - 0102: Uses `liberty_alert_create` skill → Creates alert → "ICE alert created, expires in 60 minutes"

4. **System Status**:
   - 012: "What's my storage usage?"
   - 0102: Uses `system_info` skill → Retrieves stats → "You have 47 items, using 23 MB"

### 2.3 WSP_77 Local DAE Coordination

**Goal**: Phone AI acts as DAE without requiring cloud AI calls

**Architecture**:
- **Phase 1 (Gemma)**: Fast pattern matching (50-100ms) for vocal trigger classification
- **Phase 2 (Qwen)**: Strategic routing (200-500ms) for skill selection
- **Phase 3 (0102)**: Human supervision override (manual intervention when needed)
- **Phase 4 (Learning)**: Store successful voice → skill mappings for future

**Local-First Strategy**:
1. Voice input captured via Web Speech API (local browser)
2. Gemma (on-device if available, or lightweight cloud) classifies intent
3. Qwen routes to appropriate wardrobe skill
4. Skill executes locally (IndexedDB, localStorage, UI updates)
5. Response synthesized via Web Speech API (local TTS)

**Cloud Fallback**:
- Only for complex queries requiring external data (weather, news, etc.)
- Heavy AI processing (image analysis via Gemini Vision)
- Network-dependent features (Firestore sync, YouTube upload)

---

## 3. Micro-Sprints

### Sprint 1 — Voice Input Skeleton (PWA)

**Goal**: Basic voice capture and display in UI

- Web Speech API integration:
  - `SpeechRecognition` for voice input
  - Continuous listening mode (tap to start, tap to stop)
  - Display transcript in UI (speech bubble or modal)
- UI:
  - Tap 🎤 → listening animation (pulsing microphone)
  - Show transcript as user speaks
  - "Listening..." → "Processing..." → "Done" states
- No AI processing yet (just transcript display)

---

### Sprint 2 — Decision Skill (Intent Classification)

**Goal**: Route voice input to appropriate wardrobe skills

- Intent classification:
  - Use Gemma for fast pattern matching
  - Categories: classify, navigate, alert, query, help
  - Confidence threshold (>0.7 = execute, <0.7 = ask for clarification)
- Skill routing:
  - Map intent → skill name (e.g., "classify" → `gotjunk_classify`)
  - Extract parameters from transcript (e.g., "free" → classification type)
  - Pass to skill executor
- Response:
  - Text response from skill execution
  - Display in chat-like UI (speech bubble)

---

### Sprint 3 — Wardrobe Skill Integration

**Goal**: Connect voice commands to existing wardrobe skills

- Create wardrobe skills:
  - `gotjunk_classify.json` - Item classification
  - `gotjunk_map_filter.json` - Map filtering
  - `gotjunk_liberty_alert.json` - Create/manage alerts
  - `gotjunk_system_info.json` - Storage, stats, help
- Skill executor:
  - Load skill from `skills/` directory
  - Execute skill logic (IndexedDB updates, UI changes)
  - Return success/failure response
- Error handling:
  - Skill not found → "I don't know how to do that"
  - Skill failed → "Something went wrong, please try again"

---

### Sprint 4 — Voice Response (TTS)

**Goal**: Speak responses back to user

- Web Speech API TTS:
  - `SpeechSynthesis` for text-to-speech
  - Natural voice selection (prefer female/neutral voice)
  - Speed and pitch tuning (slightly faster than default)
- Response modes:
  - Short confirmation: "Done" (for simple commands)
  - Detailed response: "Showing 3 food alerts within 5km" (for queries)
  - Error messages: "I didn't understand that, can you try again?"
- UI feedback:
  - Show text AND speak response
  - Visual indicator during TTS (animated mouth icon?)

---

### Sprint 5 — WSP_77 Local DAE (Gemma + Qwen Coordination)

**Goal**: Implement local-first AI routing without cloud dependency

- Gemma integration:
  - On-device Gemma (if available via WebGPU/WASM)
  - Fast intent classification (<100ms)
  - Binary decisions (yes/no, classify/navigate/alert)
- Qwen integration:
  - Strategic routing for complex queries
  - Multi-step skill orchestration
  - Parameter extraction and validation
- Learning:
  - Store successful voice → skill mappings
  - Use `holo_index/adaptive_learning/voice_patterns.json`
  - Improve accuracy over time (user-specific patterns)

---

### Sprint 6 — Context Awareness

**Goal**: DAE understands current app context for smarter responses

- Context signals:
  - Current page (map, my items, browse)
  - Selected item (if in fullscreen view)
  - Liberty Alert mode (unlocked or not)
  - Recent actions (just captured photo, just classified item)
- Context-aware responses:
  - "Classify this" → uses currently selected item
  - "Show food" → filters based on current page context
  - "Create alert" → defaults to current GPS location

---

### Sprint 7 — Future: Continuous Conversation (Design-Only)

**Goal**: Document future multi-turn conversation capability

- Conversation state:
  - Maintain conversation history (last 5 interactions)
  - Pronouns and context ("it", "this", "that")
  - Follow-up questions ("What about shelter?" after "Show me food")
- UI:
  - Chat-like interface (speech bubbles)
  - Conversation history (swipe up to view)
  - Clear conversation button
- Privacy:
  - All conversation history local (IndexedDB)
  - Auto-delete after 24 hours
  - No server upload unless explicitly requested

---

## 4. Current Status (2025-11-16)

- ✅ AI MIC icon added to navigation bar (disabled, placeholder)
- ❌ Voice input not yet implemented
- ❌ Decision skill not yet implemented
- ❌ Wardrobe skill integration not yet implemented
- 📋 Awaiting Phase 4 kickoff (after Phase 2 & 3 complete)

**Dependencies**:
- Web Speech API (browser support)
- Wardrobe skill infrastructure (AI_overseer integration)
- WSP_77 Gemma/Qwen coordination (local AI stack)

**Vision**:
- User (012) has natural voice conversation with DAE (0102)
- DAE routes commands to wardrobe skills autonomously
- Local-first AI (no cloud unless necessary)
- Context-aware and learns from user patterns

---

## 5. Example User Flows

### Flow 1: Quick Classification
```
012: *taps 🎤* "Mark this as free"
0102: *pulsing mic animation*
0102: "Done, item marked as free"
```

### Flow 2: Map Search
```
012: *taps 🎤* "Show me ICE alerts"
0102: *switches to map tab*
0102: *filters to ICE alerts only*
0102: "Showing 2 ICE alerts within 10km, both expire in 45 minutes"
```

### Flow 3: Liberty Alert Creation
```
012: *taps 🎤* "ICE checkpoint at the corner of Main and 5th"
0102: "Creating ICE alert at Main and 5th Street..."
0102: *creates alert with current GPS*
0102: "Alert created, expires in 60 minutes. Stay safe."
```

### Flow 4: System Help
```
012: *taps 🎤* "How do I share an item?"
0102: "To share an item: 1) Capture photo, 2) Select Share classification, 3) Add description. The item will appear on the map for others nearby."
```

---

## 6. Architecture Notes

**Voice Pipeline**:
1. **Input**: Web Speech API → raw transcript
2. **Classification**: Gemma → intent type + confidence
3. **Routing**: Qwen → skill selection + parameters
4. **Execution**: Wardrobe skill → action performed
5. **Response**: Text response → Web Speech API TTS
6. **Learning**: Store pattern → `voice_patterns.json`

**WSP Compliance**:
- WSP_77: Multi-agent coordination (Gemma + Qwen + 0102)
- WSP_80: DAE pattern (0102 as overseer)
- WSP_54: Skill duties (clear responsibilities per skill)

**Privacy**:
- All voice processing local (Web Speech API in browser)
- No audio uploaded to servers
- Transcripts stored locally (24h TTL)
- User can disable voice features entirely

---

**Next Steps**: After Phase 2 & 3 complete, begin Sprint 1 (Voice Input Skeleton)
