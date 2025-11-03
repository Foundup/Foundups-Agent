# Function Process Map - YouTube Auth Module

## Critical Execution Paths

| Function | Module | Calls | Dependencies | Common Issues |
|----------|--------|-------|--------------|---------------|
| get_authenticated_service() | youtube_auth.py | get_credentials_for_index(), mark_credential_exhausted() | quota_monitor.py, google.oauth2 | Exhausted sets not clearing at midnight |
| mark_credential_exhausted() | youtube_auth.py | File I/O to memory/exhausted_credentials.json | pathlib, json, pytz | pytz missing causes timezone fallback |
| can_perform_operation() | quota_intelligence.py | get_usage_summary(), _get_quota_suggestion() | quota_monitor.py | Emergency reserve calculations |
| MonitoredYouTubeService.__getattr__() | monitored_youtube_service.py | _intercept_api_call(), quota_intelligence.can_perform_operation() | quota_intelligence.py | Old processes bypass monitoring |
| get_usage_summary() | quota_monitor.py | _load_usage(), _check_reset() | json, datetime | Daily reset timing issues |
| _check_reset() | quota_monitor.py | _reset_daily_usage() | datetime, pytz | Timezone calculations for PT |
| plan_operation_batch() | quota_intelligence.py | can_perform_operation(), _get_priority_score() | None | Batch optimization logic |
| get_quota_dashboard() | quota_intelligence.py | get_usage_summary(), _generate_recommendations() | quota_monitor.py | Dashboard data aggregation |

## Debug Trace Routes

### Authentication Flow
**Path**: `get_authenticated_service()` -> credential selection -> exhaustion check -> service building
```
youtube_auth.py:36 (entry point)
  v
youtube_auth.py:72-86 (load exhausted sets from memory/exhausted_credentials.json)
  v
youtube_auth.py:87-112 (check midnight PT reset, clear if needed)
  v
youtube_auth.py:119-136 (determine credential sets to try)
  v
youtube_auth.py:138-224 (iterate sets, authenticate, handle exhaustion)
  v
monitored_youtube_service.py:17-20 (wrap service with monitoring)
```

### Quota Check Flow
**Path**: API call -> interception -> quota check -> allow/block decision
```
Any API call (e.g., liveChatMessages().list())
  v
monitored_youtube_service.py:123 (__getattr__ intercepts)
  v
monitored_youtube_service.py:130 (_intercept_api_call)
  v
quota_intelligence.py:63 (can_perform_operation)
  v
quota_monitor.py:250 (get_usage_summary for current state)
  v
quota_intelligence.py:98-176 (evaluate rules and limits)
  v
Return decision with suggestions
```

### Credential Exhaustion Flow
**Path**: Quota exceeded -> mark exhausted -> persist to disk -> prevent reuse
```
API returns quotaExceeded error
  v
youtube_auth.py:232 (mark_credential_exhausted called)
  v
youtube_auth.py:247-262 (load current exhausted data)
  v
youtube_auth.py:264 (add to exhausted_sets)
  v
youtube_auth.py:267-276 (calculate next midnight PT)
  v
youtube_auth.py:279-299 (save to memory/exhausted_credentials.json)
  v
youtube_auth.py:304 (update in-memory set)
```

### Quota Reset Flow
**Path**: Time check -> midnight detection -> clear exhausted -> reset counters
```
get_authenticated_service() called
  v
youtube_auth.py:87-100 (calculate current time in PT)
  v
youtube_auth.py:101 (check if past midnight)
  v
youtube_auth.py:102-103 (clear exhausted_sets if true)
  v
youtube_auth.py:106-112 (save reset state to disk)
  v
quota_monitor.py:211-229 (_check_reset for usage counters)
```

## Common Error Patterns

### pytz Module Missing
- **Symptom**: `No module named 'pytz'`
- **Location**: youtube_auth.py:62-65
- **Trace Path**: Import attempt -> ImportError -> Fallback to UTC-8
- **Solution**: Uses UTC-8 approximation (not perfect for DST)

### Throttling Bypass (2,343 calls)
- **Symptom**: API calls not being monitored/throttled
- **Location**: monitored_youtube_service.py:123-140
- **Trace Path**: Old process -> No MonitoredYouTubeService -> Direct API calls
- **Solution**: Kill old processes, ensure single instance

### False Quota Exhaustion
- **Symptom**: Valid credentials marked as exhausted
- **Location**: youtube_auth.py:206-212 (removed validation)
- **Trace Path**: Auth -> Validation test -> Quota consumed -> False exhaustion
- **Solution**: Skip validation during authentication

### Midnight Reset Failure
- **Symptom**: Exhausted sets not clearing after midnight PT
- **Location**: youtube_auth.py:87-112
- **Trace Path**: Time check -> Timezone calculation -> Reset logic
- **Solution**: Verify timezone handling and persistent state file

## Performance Bottlenecks

| Operation | Location | Cost | Optimization |
|-----------|----------|------|--------------|
| search.list | API call | 100 units | Use batch planning, defer if possible |
| liveChatMessages.insert | API call | 200 units | Queue and batch, use emergency override sparingly |
| Validation during auth | youtube_auth.py:206 | 1 unit per attempt | REMOVED - Skip validation |
| Quota dashboard generation | quota_intelligence.py:320 | Memory/CPU | Cache results for 60 seconds |

## Integration Points

### Incoming Dependencies
- **auto_moderator_dae.py** -> Requests authenticated service
- **livechat_core.py** -> Uses service for API calls
- **social_media_orchestrator** -> Needs YouTube API access

### Outgoing Dependencies
- **google.oauth2.credentials** -> OAuth handling
- **googleapiclient.discovery** -> API service building
- **memory/exhausted_credentials.json** -> Persistent state
- **memory/quota_usage.json** -> Usage tracking

## WSP 86 Navigation Commands

```bash
# Find specific function
grep -n "get_authenticated_service" modules/platform_integration/youtube_auth/src/*.py

# Trace quota flow
grep -n "can_perform_operation" modules/platform_integration/youtube_auth/src/*.py

# Debug exhaustion
cat memory/exhausted_credentials.json

# Check quota state
python modules/platform_integration/youtube_auth/scripts/quota_dashboard.py --summary
```