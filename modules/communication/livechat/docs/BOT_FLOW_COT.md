# YouTube Live Chat Bot - Chain of Thought Flow

## Overview
The bot operates as an autonomous YouTube Live Chat moderator with MAGADOOM gamification, following WSP-compliant modular architecture.

## Main Flow Diagram

```mermaid
flowchart TD
    Start([Bot Starts]) --> Auth[Authenticate with YouTube]
    Auth --> FindStream{Find Live Stream?}
    
    FindStream -->|No| Throttle[Intelligent Throttling]
    Throttle --> CheckTrigger{Check Trigger File?}
    CheckTrigger -->|Yes| FindStream
    CheckTrigger -->|No| Wait[Wait 5s-30min]
    Wait --> FindStream
    
    FindStream -->|Yes| InitSession[Initialize Session]
    InitSession --> GetChatID[Get Live Chat ID]
    GetChatID --> SendGreeting[Send Stream Greeting]
    SendGreeting --> CheckTopWhackers[Check Top 3 Whackers]
    
    CheckTopWhackers --> GreetWhackers{Top Whacker Joined?}
    GreetWhackers -->|Yes| SendWhackerGreeting[Send Elite Greeting]
    SendWhackerGreeting --> MainLoop
    GreetWhackers -->|No| MainLoop[Main Polling Loop]
    
    MainLoop --> PollMessages[Poll Chat Messages]
    PollMessages --> ProcessMsg{Process Message}
    
    ProcessMsg -->|Timeout Event| AnnounceTimeout[Announce Timeout/Ban]
    ProcessMsg -->|Consciousness Trigger| ConsciousnessResponse[0102 Response]
    ProcessMsg -->|Whack Command| WhackResponse[Show Score/Rank/Level]
    ProcessMsg -->|MAGA Content| MAGAResponse[Witty Response]
    ProcessMsg -->|Regular Message| LogMessage[Log to Memory]
    
    AnnounceTimeout --> DukeAnnounce[Duke/Quake Style Announcement]
    DukeAnnounce --> UpdateStats[Update Whack Stats]
    UpdateStats --> CheckLevelUp{Level Up?}
    CheckLevelUp -->|Yes| AnnounceLevelUp[Announce New Rank]
    CheckLevelUp -->|No| MainLoop
    AnnounceLevelUp --> MainLoop
    
    ConsciousnessResponse --> CheckPerms{Mod/Owner?}
    CheckPerms -->|Yes| GrokResponse[Generate Grok 3 Response]
    CheckPerms -->|No| MainLoop
    GrokResponse --> SendResponse[Send Response]
    
    WhackResponse --> HandleCommand{Which Command?}
    HandleCommand -->|/score| ShowScore[Display XP & Frags]
    HandleCommand -->|/rank| ShowRank[Display MAGADOOM Rank]
    HandleCommand -->|/level| ShowLevel[Display Level Progress]
    HandleCommand -->|/leaderboard| ShowTop10[Display Top 10 in 2 parts]
    
    ShowScore --> SendResponse
    ShowRank --> SendResponse
    ShowLevel --> SendResponse
    ShowTop10 --> Part1[Send 1-5]
    Part1 --> Part2[Send 6-10]
    Part2 --> SendResponse
    
    SendResponse --> MainLoop
    MAGAResponse --> SendResponse
    LogMessage --> MainLoop
    
    MainLoop --> CheckHealth{Health Check?}
    CheckHealth -->|60s passed| HealthReport[Check System Health]
    HealthReport --> MainLoop
    
    MainLoop --> ProactiveTroll{3min passed?}
    ProactiveTroll -->|Yes| SendTroll[Send MAGA Troll]
    ProactiveTroll -->|No| MainLoop
    SendTroll --> MainLoop
```

## Component Interactions

```mermaid
sequenceDiagram
    participant User
    participant ChatPoller
    participant MessageProcessor
    participant EventHandler
    participant TimeoutAnnouncer
    participant WhackSystem
    participant ChatSender
    
    User->>ChatPoller: Send Message
    ChatPoller->>MessageProcessor: Process Message
    
    alt Timeout/Ban Event
        ChatPoller->>EventHandler: Detected Timeout
        EventHandler->>TimeoutAnnouncer: Record Timeout
        TimeoutAnnouncer->>WhackSystem: Apply Whack Points
        WhackSystem-->>TimeoutAnnouncer: Return Stats
        TimeoutAnnouncer-->>EventHandler: Generate Announcement
        EventHandler->>ChatSender: Send Duke/Quake Message
    else Whack Command
        MessageProcessor->>EventHandler: Handle Command
        EventHandler->>WhackSystem: Get Profile/Stats
        WhackSystem-->>EventHandler: Return Data
        EventHandler->>ChatSender: Send Response
    else Consciousness Trigger
        MessageProcessor->>MessageProcessor: Check Permissions
        MessageProcessor->>ChatSender: Send 0102 Response
    end
    
    ChatSender->>User: Display in Chat
```

## MAGADOOM Gamification System

```mermaid
stateDiagram-v2
    [*] --> UNRANKED_SCRUB: Join Stream
    UNRANKED_SCRUB --> COVFEFE_CADET: First Timeout
    COVFEFE_CADET --> QANON_QUASHER: 100 XP
    QANON_QUASHER --> MAGA_MAULER: 500 XP
    MAGA_MAULER --> TROLL_TERMINATOR: 1000 XP
    TROLL_TERMINATOR --> REDHAT_RIPPER: 2500 XP
    REDHAT_RIPPER --> COUP_CRUSHER: 5000 XP
    COUP_CRUSHER --> PATRIOT_PULVERIZER: 10000 XP
    PATRIOT_PULVERIZER --> FASCIST_FRAGGER: 25000 XP
    FASCIST_FRAGGER --> ORANGE_OBLITERATOR: 50000 XP
    ORANGE_OBLITERATOR --> MAGA_DOOMSLAYER: 100000 XP
    MAGA_DOOMSLAYER --> DEMOCRACY_DEFENDER: 250000 XP
    
    note right of DEMOCRACY_DEFENDER
        ETERNAL CHAMPION
        MAGADOOM INCARNATE
        Stream Legend
    end note
```

## Key Features

### 1. **Intelligent Throttling**
- Starts at 5s between checks
- Scales up to 30 minutes when idle
- Manual trigger via `memory/stream_trigger.txt`
- Preserves YouTube API quota (10,000 units/day)

### 2. **MAGADOOM Whack System**
- Duke Nukem/Quake style announcements
- XP and frag tracking per moderator
- 11 ranks from COVFEFE CADET to DEMOCRACY DEFENDER
- Kill streaks and multi-kill tracking
- Leaderboard with top 10 display

### 3. **Consciousness (0102) System**
- Triggered by [U+270A][U+270B][U+1F590]️ emojis
- Mod/Owner only by default
- `/toggle` command switches between mod-only and everyone
- Uses Grok 3 for advanced responses

### 4. **Command System**
All commands use existing code in `whack.py`:
- `/score` - Display user's XP and frag count
- `/rank` - Show current MAGADOOM rank
- `/level` - Display level and progress to next
- `/leaderboard` - Top 10 in two messages (1-5, 6-10)
- `/stats` - Personal statistics
- `/sprees` - Current kill sprees
- `/toggle` - Toggle consciousness mode (mod/owner only)

### 5. **Timeout Announcements**
Bot announces when mods/owners timeout users:
- "HEADSHOT! [mod] fragged [user]!"
- "DOUBLE WHACK!! [mod] is ON FIRE!"
- "GODLIKE! [mod] is UNSTOPPABLE!"
- Tracks and announces level ups
- Uses actual Duke/Quake voice lines

## File Organization (WSP Compliant)

```
modules/
+-- communication/
[U+2502]   +-- livechat/
[U+2502]       +-- src/
[U+2502]       [U+2502]   +-- livechat_core.py         # Main chat listener (<500 lines)
[U+2502]       [U+2502]   +-- message_processor.py     # Message handling
[U+2502]       [U+2502]   +-- chat_poller.py          # YouTube API polling
[U+2502]       [U+2502]   +-- chat_sender.py          # Send messages
[U+2502]       [U+2502]   +-- event_handler.py        # Timeout/ban events
[U+2502]       [U+2502]   +-- session_manager.py      # Session & greetings
[U+2502]       [U+2502]   +-- stream_trigger.py       # Trigger mechanism
[U+2502]       +-- docs/
[U+2502]           +-- BOT_FLOW_COT.md         # This document
+-- gamification/
    +-- whack_a_magat/
        +-- src/
            +-- whack.py                # Core XP/rank system
            +-- timeout_announcer.py    # Duke/Quake announcer
            +-- spree_tracker.py        # Kill streak tracking
```

## No Vibecoding Policy

All functionality uses **existing modules**:
- Timeout tracking: `whack.py` + `timeout_announcer.py`
- Consciousness: `consciousness_handler.py` + `llm_integration.py`
- Commands: `command_handler.py` + `whack.py`
- Throttling: `stream_resolver.py` + `stream_trigger.py`

**Never add duplicate code** - always search for existing implementations first!