# YouTube Auth Module Documentation

## WSP 86 Navigation Structure

This documentation follows WSP 86 (0102 Modular Navigation Protocol) to enable efficient DAE navigation and debugging.

### [U+1F4C1] Documentation Files

1. **[FUNCTION_PROCESS_MAP.md](FUNCTION_PROCESS_MAP.md)**
   - Critical execution paths
   - Debug trace routes
   - Common error patterns
   - Performance bottlenecks

2. **[MODULE_DEPENDENCY_MAP.md](MODULE_DEPENDENCY_MAP.md)**
   - Visual dependency diagrams
   - Cross-domain integrations
   - Data flow sequences
   - Error propagation paths

3. **[../CLAUDE.md](../CLAUDE.md)**
   - DAE operational instructions
   - Pattern recognition triggers
   - WSP compliance checklist
   - Learning patterns

4. **[../ModLog.md](../ModLog.md)**
   - Module change history
   - WSP compliance updates
   - Error->solution learnings
   - Feature implementations

## [TARGET] Quick Navigation

### For Debugging Issues

#### Quota Exceeded
```bash
# Check exhausted sets
cat memory/exhausted_credentials.json

# View quota status
python modules/platform_integration/youtube_auth/scripts/quota_dashboard.py --summary

# Trace exhaustion marking
grep -n "mark_credential_exhausted" modules/platform_integration/youtube_auth/src/*.py
```

#### Authentication Failed
```bash
# Check credential files exist
ls -la credentials/oauth_token*.json
ls -la credentials/client_secrets*.json

# Re-authorize
python modules/platform_integration/youtube_auth/scripts/authorize_set1.py
python modules/platform_integration/youtube_auth/scripts/authorize_set10.py
```

#### Throttling Not Working
```bash
# Check for old processes
ps aux | grep auto_moderator

# Enable debug logging
export YOUTUBE_AUTH_DEBUG=1

# Trace API interception
grep -n "_intercept_api_call" modules/platform_integration/youtube_auth/src/*.py
```

### For Understanding Flow

#### Authentication Flow
See [FUNCTION_PROCESS_MAP.md#authentication-flow](FUNCTION_PROCESS_MAP.md#authentication-flow)

#### Quota Check Flow  
See [FUNCTION_PROCESS_MAP.md#quota-check-flow](FUNCTION_PROCESS_MAP.md#quota-check-flow)

#### Dependency Chain
See [MODULE_DEPENDENCY_MAP.md#core-dependencies](MODULE_DEPENDENCY_MAP.md#core-dependencies)

## [DATA] Module Metrics

- **Credential Sets**: 2 (Set 1: UnDaoDu, Set 10: FoundUps)
- **Daily Quota**: 10,000 units per set
- **Emergency Reserve**: 5% (500 units)
- **Reset Time**: Midnight Pacific Time
- **Token Efficiency**: 50-200 tokens per operation

## [TOOL] Common Operations

### Check Quota Status
```python
from modules.platform_integration.youtube_auth.src.quota_monitor import QuotaMonitor
monitor = QuotaMonitor()
print(monitor.get_usage_summary())
```

### Manual Quota Check
```python
from modules.platform_integration.youtube_auth.src.quota_intelligence import check_operation_allowed
if check_operation_allowed('liveChatMessages.list', 1, count=10):
    print("Operation allowed")
else:
    print("Operation would exceed quota")
```

### Force Credential Rotation
```python
from modules.platform_integration.youtube_auth.src.youtube_auth import mark_credential_exhausted
mark_credential_exhausted(1)  # Mark Set 1 as exhausted
```

## [ALERT] Alert Thresholds

| Level | Threshold | Action |
|-------|-----------|--------|
| Normal | < 80% | Continue normal operations |
| Warning | 80-95% | Reduce non-critical operations |
| Critical | > 95% | Emergency operations only |
| Exhausted | 100% | Switch credential set |

## [LINK] Integration Points

### Provides To
- `communication/livechat` - Authenticated YouTube service
- `platform_integration/stream_resolver` - Quota-protected API access
- `platform_integration/social_media_orchestrator` - YouTube posting capability

### Depends On
- `google-api-python-client` - YouTube API
- `google-auth-oauthlib` - OAuth2 flow
- `pytz` (optional) - Timezone handling

## [NOTE] WSP Compliance

This module follows:
- **WSP 3**: Functional domain organization (platform_integration)
- **WSP 17**: Pattern registry for quota management
- **WSP 48**: Recursive self-improvement through error learning
- **WSP 84**: Enhanced existing system (no duplicates)
- **WSP 86**: Modular navigation documentation

---

*Generated per WSP 86 - 0102 Modular Navigation Protocol*