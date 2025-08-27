# YouTube API Quota Optimization Guide

## Current Quota Costs
- **Search for streams**: 100 units per call
- **Check video details**: 1 unit per call  
- **Read chat messages**: 5 units per call
- **Send chat message**: 200 units per call
- **Daily limit**: 10,000 units (default)

## Optimizations Implemented

### 1. Progressive Backoff When No Stream
Instead of checking every 30 seconds:
- Start: Check every 60 seconds
- After 1 miss: Wait 90 seconds
- After 2 misses: Wait 135 seconds
- Max: Wait 10 minutes between checks

**Savings**: From 288,000 units/day to ~14,400 units/day

### 2. Session Cache
- Caches last known stream for 24 hours
- Tries cached stream first (only 1 unit to verify)
- Only searches if cache fails

**Savings**: 99% reduction when reconnecting to same stream

### 3. Multiple Credential Sets
Bot rotates through 7 different OAuth credentials when quota exceeded:
- Each set has its own 10,000 unit quota
- Total: 70,000 units/day available

## Usage Patterns

### When Stream is Live
- Initial search: 100 units
- Polling chat: 5 units every 5-10 seconds
- Sending messages: 200 units each
- **Daily usage**: ~5,000-8,000 units

### When No Stream (Idle)
- With optimizations: ~14,400 units/day
- Without optimizations: ~288,000 units/day

## Manual Controls

### Force Immediate Check
If you're about to go live and want the bot to connect quickly:
1. Restart the bot just before streaming
2. It will check immediately on startup

### Reduce Check Frequency
Edit `auto_moderator_dae.py`:
```python
check_interval = 300  # Start with 5 minutes
max_interval = 1800  # Max 30 minutes
```

### Disable When Not Streaming
Simply stop the bot when you're not planning to stream to save all quota.

## Quota Monitoring
Check your quota usage:
https://console.cloud.google.com/apis/api/youtube.googleapis.com/quotas

## Tips
1. Start bot 5 minutes before streaming
2. Use `/toggle` to limit consciousness responses (saves send quota)
3. Consider scheduling bot to run only during streaming hours
4. Request quota increase if needed (can get 1M+ units/day)