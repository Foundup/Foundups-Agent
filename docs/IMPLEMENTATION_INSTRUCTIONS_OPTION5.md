# Fix AI Overseer Monitoring - Option 5 Implementation

## Current Problem
When user selects option 5 "Launch with AI Overseer Monitoring", they see:
```
[WARN] AI Overseer monitoring launch not yet implemented
  TODO: Integrate BashOutput for daemon monitoring
  TODO: Launch YouTube DAE + AI Overseer in parallel
```

## Solution (Replace Placeholder Code)

### Find this code block (around line 1110-1128 in your version):
```python
elif yt_choice == "5":
    # Launch YouTube DAE with AI Overseer monitoring
    print("\n[AI] Launching YouTube DAE with AI Overseer Monitoring")
    print("="*60)
    print("  Architecture: WSP 77 Agent Coordination")
    print("  Phase 1 (Gemma): Fast error detection (<100ms)")
    print("  Phase 2 (Qwen): Bug classification (200-500ms)")
    print("  Phase 3 (0102): Auto-fix or report (<2s)")
    print("  Phase 4: Learning pattern storage")
    print("="*60)
    print("\n  Monitoring:")
    print("    - Unicode errors (auto-fix)")
    print("    - OAuth revoked (auto-fix)")
    print("    - Duplicate posts (bug report)")
    print("    - API quota exhausted (auto-fix)")
    print("    - LiveChat connection errors (auto-fix)")
    print("="*60)

    # TODO: Implement actual daemon monitoring launch
    # This will require:
    # 1. Start YouTube daemon in background (asyncio task or subprocess)
    # 2. Get bash shell ID for monitoring
    # 3. Launch AI Overseer monitor_daemon() in parallel
    # 4. Coordinate both tasks

    print("\n[WARN] AI Overseer monitoring launch not yet implemented")
    print("  TODO: Integrate BashOutput for daemon monitoring")
    print("  TODO: Launch YouTube DAE + AI Overseer in parallel")
    print("\n  For now, you can:")
    print("    1. Launch YouTube DAE (option 1)")
    print("    2. Manually run AI Overseer monitoring")
    print("\n  Manual monitoring command:")
    print('    from modules.ai_intelligence.ai_overseer.src.ai_overseer import AIIntelligenceOverseer')
    print('    overseer = AIIntelligenceOverseer(Path("O:/Foundups-Agent"))')
    print('    overseer.monitor_daemon(bash_id="SHELL_ID", skill_path=Path("modules/communication/livechat/skills/youtube_daemon_monitor.json"))')

    input("\n[ENTER] Press Enter to return to menu...")
```

### Replace with this WORKING code:
```python
elif yt_choice == "5":
    # Launch YouTube DAE with AI Overseer monitoring
    print("\n[AI] Launching YouTube DAE with AI Overseer Monitoring")
    print("="*60)
    print("  Architecture: WSP 77 Agent Coordination")
    print("  Phase 1 (Gemma): Fast error detection (<100ms)")
    print("  Phase 2 (Qwen): Bug classification (200-500ms)")
    print("  Phase 3 (0102): Auto-fix or report (<2s)")
    print("  Phase 4: Learning pattern storage")
    print("="*60)
    print("\n  Monitoring:")
    print("    - Unicode errors (auto-fix)")
    print("    - OAuth revoked (auto-fix)")
    print("    - Duplicate posts (bug report)")
    print("    - API quota exhausted (auto-fix)")
    print("    - LiveChat connection errors (auto-fix)")
    print("="*60)

    try:
        # Simply launch monitor_youtube - it IS the YouTube daemon!
        # AI Overseer monitoring happens automatically via YouTubeDAEHeartbeat service
        print("\n[AI] Starting YouTube daemon with AI Overseer monitoring...")
        print("[INFO] Monitoring enabled via YouTubeDAEHeartbeat service\n")
        await monitor_youtube(disable_lock=False)

    except KeyboardInterrupt:
        print("\n[STOP] YouTube daemon stopped by user")
    except Exception as e:
        print(f"\n[ERROR] Failed to start YouTube daemon: {e}")
        logger.error(f"YouTube daemon error: {e}", exc_info=True)

    input("\n[ENTER] Press Enter to return to menu...")
```

## Why This Works

1. **`monitor_youtube()` IS the YouTube daemon** - same as option 1
2. **YouTubeDAEHeartbeat service** (in `modules/communication/livechat/src/youtube_dae_heartbeat.py`) already handles AI Overseer integration
3. **No BashOutput coordination needed** - monitoring is built into the daemon itself
4. **Clean and simple** - just launch the daemon, monitoring happens automatically

## Test After Fix

1. Restart main.py
2. Select option 1 -> 5
3. Should see: "Starting YouTube daemon with AI Overseer monitoring..."
4. Daemon launches and runs normally
5. AI Overseer monitors errors automatically in background

## Related Files
- AI Overseer: `modules/ai_intelligence/ai_overseer/src/ai_overseer.py`
- Heartbeat Service: `modules/communication/livechat/src/youtube_dae_heartbeat.py`
- Monitoring Skill: `modules/communication/livechat/skills/youtube_daemon_monitor.json`
