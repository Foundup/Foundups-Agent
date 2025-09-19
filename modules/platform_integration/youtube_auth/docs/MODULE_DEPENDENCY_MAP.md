# Module Dependency Map - YouTube Auth

## Core Dependencies

```mermaid
flowchart TD
    YTA[youtube_auth.py] --> QM[quota_monitor.py]
    YTA --> MYS[monitored_youtube_service.py]
    MYS --> QI[quota_intelligence.py]
    QI --> QM
    
    YTA --> GOA[google.oauth2]
    YTA --> GAD[googleapiclient.discovery]
    
    QM --> MEM1[memory/quota_usage.json]
    YTA --> MEM2[memory/exhausted_credentials.json]
    
    QI --> PYTZ[pytz - optional]
    YTA --> PYTZ
    
    DASH[quota_dashboard.py] --> QI
    DASH --> QM
```

## Module Relationships

### Internal Module Dependencies
| Module | Depends On | Purpose |
|--------|------------|---------|
| youtube_auth.py | quota_monitor.py | Track quota usage and exhaustion |
| youtube_auth.py | monitored_youtube_service.py | Wrap service with monitoring |
| monitored_youtube_service.py | quota_intelligence.py | Pre-call quota checking |
| quota_intelligence.py | quota_monitor.py | Get usage summaries |
| quota_dashboard.py | quota_intelligence.py | Display intelligent metrics |
| quota_dashboard.py | quota_monitor.py | Access raw usage data |

### External Library Dependencies
| Module | External Library | Purpose | Required |
|--------|-----------------|---------|----------|
| youtube_auth.py | google.oauth2.credentials | OAuth2 credential handling | Yes |
| youtube_auth.py | google_auth_oauthlib.flow | OAuth2 flow management | Yes |
| youtube_auth.py | googleapiclient.discovery | Build YouTube API service | Yes |
| youtube_auth.py | pytz | Pacific timezone handling | No (fallback exists) |
| quota_intelligence.py | pytz | Timezone calculations | No (fallback exists) |
| All modules | python-dotenv | Environment variable loading | Yes |

## Cross-Domain Dependencies

| Local Module | External Domain | External Module | Integration Type |
|--------------|-----------------|-----------------|------------------|
| youtube_auth.py | communication/livechat | auto_moderator_dae.py | Provides authenticated service |
| monitored_youtube_service.py | communication/livechat | livechat_core.py | Monitors API calls |
| quota_intelligence.py | infrastructure/shared_utilities | single_instance.py | Process management |
| youtube_auth.py | platform_integration/stream_resolver | stream_resolver.py | Shares credentials |

## File System Dependencies

```mermaid
flowchart LR
    YTA[youtube_auth.py] --> ENV[.env file]
    YTA --> CS1[credentials/client_secrets_1.json]
    YTA --> CS10[credentials/client_secrets_10.json]
    YTA --> OT1[credentials/oauth_token_1.json]
    YTA --> OT10[credentials/oauth_token_10.json]
    
    YTA --> EXH[memory/exhausted_credentials.json]
    QM[quota_monitor.py] --> QU[memory/quota_usage.json]
    
    DASH[quota_dashboard.py] --> QU
    DASH --> EXH
```

### Configuration Files
- **.env**: Contains credential file paths and scopes
  - `GOOGLE_CLIENT_SECRETS_FILE_1`
  - `GOOGLE_CLIENT_SECRETS_FILE_10`
  - `OAUTH_TOKEN_FILE_1`
  - `OAUTH_TOKEN_FILE_10`
  - `YOUTUBE_SCOPES`

### Credential Files
- **credentials/client_secrets_*.json**: OAuth2 client configuration
- **credentials/oauth_token_*.json**: Stored authentication tokens

### State Files
- **memory/exhausted_credentials.json**: Tracks exhausted credential sets
- **memory/quota_usage.json**: Tracks daily quota consumption

## Data Flow

```mermaid
sequenceDiagram
    participant DAE as YouTube DAE
    participant YTA as youtube_auth
    participant MYS as MonitoredService
    participant QI as QuotaIntelligence
    participant QM as QuotaMonitor
    participant API as YouTube API
    
    DAE->>YTA: get_authenticated_service()
    YTA->>YTA: Check exhausted sets
    YTA->>YTA: Check midnight reset
    YTA->>API: Build service
    YTA->>MYS: Wrap with monitoring
    
    DAE->>MYS: API call (e.g., list())
    MYS->>QI: can_perform_operation()
    QI->>QM: get_usage_summary()
    QM-->>QI: Usage data
    QI-->>MYS: Allow/Block decision
    
    alt Allowed
        MYS->>API: Execute call
        API-->>MYS: Response
        MYS->>QM: Record usage
    else Blocked
        MYS-->>DAE: QuotaExceeded error
        DAE->>YTA: mark_credential_exhausted()
    end
```

## Error Propagation

```mermaid
flowchart TD
    API[YouTube API Error] --> MYS[MonitoredYouTubeService]
    MYS --> |quotaExceeded| YTA[youtube_auth]
    YTA --> |mark_exhausted| MEM[memory/exhausted_credentials.json]
    
    MYS --> |other errors| DAE[YouTube DAE]
    DAE --> |retry logic| YTA
    
    PYTZ[pytz ImportError] --> |fallback| UTC8[UTC-8 Approximation]
    
    AUTH[Auth Refresh Failed] --> |new OAuth flow| FLOW[OAuth2 Browser Flow]
```

## Module Evolution Path

### Current State (v1.0.0)
- Quota intelligence with pre-call checking
- Dual credential set support (1, 10)
- Timezone-aware reset with fallback
- Persistent exhaustion tracking

### Next Phase (v1.1.0)
- Machine learning for usage prediction
- Cross-platform quota sharing
- Advanced batch optimization
- GUI dashboard interface

### Future Vision (v2.0.0)
- Distributed quota management
- Multi-account federation
- Automatic quota purchasing
- Self-healing credential rotation