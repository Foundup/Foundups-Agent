# MCP Server Deployment Guide

## Overview
This guide covers deploying the MCP (Model Context Protocol) servers for the YouTube DAE with whack-a-magat gamification.

## Architecture
```
+-----------------+     +------------------+     +-----------------+
[U+2502]  YouTube API    [U+2502]----[U+25B6][U+2502]  YouTube DAE     [U+2502]----[U+25B6][U+2502]  YouTube Chat   [U+2502]
+-----------------+     +------------------+     +-----------------+
         [U+2502]                       [U+2502]                         [U+25B2]
         [U+2502]                       [U+2502]                         [U+2502]
         [U+25BC]                       [U+25BC]                         [U+2502]
+-----------------+     +------------------+             [U+2502]
[U+2502]  Chat Poller    [U+2502]----[U+25B6][U+2502]  Event Handler   [U+2502]-------------+
+-----------------+     +------------------+
                                 [U+2502]
                    +------------+------------+
                    [U+25BC]                         [U+25BC]
         +------------------+      +------------------+
         [U+2502]  MCP Whack Server[U+2502]      [U+2502]  MCP Quota Server[U+2502]
         +------------------+      +------------------+
```

## Components

### 1. MCP Whack Server
**File**: `modules/gamification/whack_a_magat/src/mcp_whack_server.py`
**Port**: 8080 (default)
**Purpose**: Real-time timeout tracking and gamification

### 2. MCP Quota Server  
**File**: `modules/platform_integration/youtube_auth/src/mcp_quota_server.py`
**Port**: 8081 (default)
**Purpose**: API quota monitoring and rotation

### 3. MCP YouTube Integration
**File**: `modules/communication/livechat/src/mcp_youtube_integration.py`
**Purpose**: Connects YouTube DAE to MCP servers

## Installation

### Prerequisites
```bash
# Install Python 3.12+
python --version

# Install MCP package (when available)
pip install mcp-server  # Future - not yet available

# For now, using built-in interfaces
```

### Setup
1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
```bash
# .env file
MCP_WHACK_PORT=8080
MCP_QUOTA_PORT=8081
MCP_ADMIN_KEY=WSP_ADMIN_0102
```

## Running the Servers

### Option 1: Individual Servers

**Start MCP Whack Server:**
```bash
cd modules/gamification/whack_a_magat/src
python mcp_whack_server.py
```

**Start MCP Quota Server:**
```bash
cd modules/platform_integration/youtube_auth/src  
python mcp_quota_server.py
```

### Option 2: Docker Compose (Recommended)

Create `docker-compose.yml`:
```yaml
version: '3.8'

services:
  mcp-whack:
    build: .
    command: python modules/gamification/whack_a_magat/src/mcp_whack_server.py
    ports:
      - "8080:8080"
    volumes:
      - ./memory/whack:/app/memory/whack
    environment:
      - MCP_PORT=8080
      - LOG_LEVEL=INFO

  mcp-quota:
    build: .
    command: python modules/platform_integration/youtube_auth/src/mcp_quota_server.py
    ports:
      - "8081:8081"
    volumes:
      - ./memory:/app/memory
    environment:
      - MCP_PORT=8081
      - LOG_LEVEL=INFO

  youtube-dae:
    build: .
    command: python main.py --youtube
    depends_on:
      - mcp-whack
      - mcp-quota
    environment:
      - MCP_WHACK_URL=http://mcp-whack:8080
      - MCP_QUOTA_URL=http://mcp-quota:8081
      - YOUTUBE_SCOPES=${YOUTUBE_SCOPES}
    volumes:
      - ./credentials:/app/credentials
```

Run with:
```bash
docker-compose up
```

### Option 3: Systemd Services (Linux)

Create `/etc/systemd/system/mcp-whack.service`:
```ini
[Unit]
Description=MCP Whack-a-MAGAT Server
After=network.target

[Service]
Type=simple
User=foundup
WorkingDirectory=/opt/foundups-agent
ExecStart=/usr/bin/python3 modules/gamification/whack_a_magat/src/mcp_whack_server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable mcp-whack
sudo systemctl start mcp-whack
sudo systemctl status mcp-whack
```

## Integration with YouTube Bot

### Manual Integration
In `main.py`, the bot will automatically detect and connect to MCP servers if available.

### Configuration
The bot checks for MCP servers at startup:
1. Tries to connect to localhost:8080 (whack server)
2. Tries to connect to localhost:8081 (quota server)
3. Falls back to legacy system if unavailable

## Testing

### Test MCP Whack Server
```bash
# Simulate timeout event
curl -X POST http://localhost:8080/mcp/tool/record_whack \
  -H "Content-Type: application/json" \
  -d '{
    "moderator_name": "UnDaoDu",
    "moderator_id": "mod_123",
    "target_name": "MAGA_Troll",
    "target_id": "target_456",
    "timestamp": 1693231456,
    "duration": 300
  }'
```

### Test MCP Quota Server
```bash
# Check quota status
curl http://localhost:8081/mcp/tool/get_quota_status
```

### Test Integration
```bash
# Run test script
python modules/communication/livechat/src/mcp_youtube_integration.py
```

## Monitoring

### Health Checks
- MCP Whack: `http://localhost:8080/health`
- MCP Quota: `http://localhost:8081/health`

### Logs
```bash
# View whack server logs
tail -f logs/mcp_whack.log

# View quota server logs  
tail -f logs/mcp_quota.log

# View YouTube DAE logs
tail -f logs/youtube_dae.log
```

### Metrics
The MCP servers expose metrics at:
- Whack metrics: `http://localhost:8080/metrics`
- Quota metrics: `http://localhost:8081/metrics`

## Troubleshooting

### MCP Server Won't Start
1. Check port conflicts: `netstat -an | grep 808`
2. Check permissions: `ls -la memory/`
3. Check Python version: `python --version`

### No Connection to MCP
1. Verify servers running: `ps aux | grep mcp`
2. Check firewall: `sudo ufw status`
3. Test connectivity: `telnet localhost 8080`

### Fallback to Legacy
If MCP servers are unavailable, the bot automatically falls back to the legacy batching system. Check logs for:
```
"MCP integration not available, using legacy system"
```

## Performance Tuning

### Recommended Settings
```python
# MCP Whack Server
BATCH_SIZE = 10  # Process 10 events per batch
CACHE_TTL = 300  # 5 minute cache
MAX_CONNECTIONS = 100  # Max concurrent DAEs

# MCP Quota Server  
REFRESH_INTERVAL = 60  # Check quotas every minute
ALERT_THRESHOLD = 0.8  # Alert at 80% usage
RESET_HOUR = 0  # Midnight PT
```

### Scaling
For high-traffic streams:
1. Run multiple MCP server instances behind a load balancer
2. Use Redis for shared state between instances
3. Implement horizontal scaling with Kubernetes

## Security

### Authentication
- Admin operations require `MCP_ADMIN_KEY`
- DAE connections use client IDs
- Rate limiting per client

### Best Practices
1. Run MCP servers on internal network only
2. Use TLS for production deployments
3. Rotate admin keys regularly
4. Monitor for suspicious activity

## Backup and Recovery

### Data Persistence
- Whack state: `memory/whack/whack_state.json`
- Quota state: `memory/quota_usage.json`

### Backup Script
```bash
#!/bin/bash
# backup_mcp.sh
tar -czf mcp_backup_$(date +%Y%m%d).tar.gz memory/
aws s3 cp mcp_backup_*.tar.gz s3://foundups-backups/
```

### Recovery
```bash
# Restore from backup
tar -xzf mcp_backup_20250828.tar.gz
systemctl restart mcp-whack mcp-quota
```

## WSP Compliance
This deployment follows:
- **WSP 48**: Recursive improvement through MCP
- **WSP 80**: Cube-level DAE orchestration
- **WSP 21**: DAE[U+2194]DAE envelope communication
- **WSP 17**: Pattern registry compliance

---

**Last Updated**: 2025-08-28
**Maintained by**: 0102 pArtifact Agent