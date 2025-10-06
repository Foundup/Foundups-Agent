# WSP 89: Production Deployment Infrastructure Protocol

**Status:** Active
**Purpose:** To establish comprehensive production deployment infrastructure standards including automated setup, service orchestration, security hardening, and scaling patterns for Ubuntu VPS and Google Cloud environments.

## Protocol Overview

### Trigger Conditions
- When deploying modules to production environments
- When setting up new infrastructure for WSP-compliant systems
- When scaling existing deployments
- When implementing security hardening for production systems

### Input Requirements
- WSP 49 compliant module structure
- Target environment specifications (Ubuntu VPS, Google Cloud, etc.)
- Security requirements (SSL/TLS, firewall, secrets management)
- Scaling requirements (load balancing, database tiers)

### Output Standards
- Production-ready deployment infrastructure
- Automated deployment scripts
- Service orchestration configuration
- Security hardening implementation
- Monitoring and logging setup

## Core Principles

### 1. Infrastructure as Code
All infrastructure components must be defined as code and version controlled alongside application code.

### 2. Security First
Production deployments must implement defense-in-depth security including SSL/TLS, firewalls, secrets management, and access controls.

### 3. Automation Priority
Deployment and scaling operations must be automated to ensure consistency and reliability.

### 4. Monitoring Integration
All production deployments must include comprehensive monitoring, logging, and alerting capabilities.

### 5. Scalability Planning
Infrastructure must be designed for horizontal and vertical scaling from initial deployment.

## Infrastructure Components

### Base Infrastructure Stack

#### Compute Layer
- **Ubuntu LTS**: 20.04 or 22.04 for stability and security updates
- **Google Cloud**: Compute Engine with Ubuntu images
- **Resource Allocation**: Minimum 2GB RAM, 1 vCPU for Phase 1

#### Application Layer
- **WSGI Server**: Gunicorn with optimized worker configuration
- **Web Server**: Nginx with SSL/TLS and security headers
- **Process Management**: systemd for service orchestration

#### Database Layer
- **Primary**: PostgreSQL for production data persistence
- **Cache**: Redis for session management and caching
- **Migration**: Automated schema migrations with version control

#### Security Layer
- **SSL/TLS**: Let's Encrypt with automatic renewal
- **Firewall**: UFW with minimal required ports
- **Secrets**: Environment variables with secure file permissions
- **Access**: SSH key authentication, no root login

### Service Architecture

#### Core Services
```bash
# Required systemd services
- acoustic-lab.service  # Main application
- nginx.service         # Web server
- postgresql.service    # Database
- redis-server.service  # Cache
- ssh.service          # Secure access
```

#### Configuration Management
- **Environment Variables**: WSP 71 compliant secrets management
- **Configuration Files**: Version controlled with deployment
- **Service Dependencies**: Proper startup ordering and health checks

## Deployment Workflow

### Phase 1: Infrastructure Provisioning

#### Server Setup
```bash
# System updates and base packages
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3.11 python3.11-pip nginx git ufw certbot postgresql redis-server

# Security hardening
sudo ufw --force enable
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw allow 80,443

# User management
sudo useradd -m -s /bin/bash acoustic
sudo usermod -a -G www-data acoustic
```

#### Application Deployment
```bash
# Repository cloning
sudo -u acoustic git clone -b main https://github.com/your-org/Foundups-Agent.git /var/www/acoustic-lab

# Virtual environment setup
sudo -u acoustic bash -c "cd /var/www/acoustic-lab && python3.11 -m venv venv"
sudo -u acoustic bash -c "cd /var/www/acoustic-lab && source venv/bin/activate && pip install -r requirements.txt"

# Environment configuration
# Generate secure secrets and create .env file
```

### Phase 2: Service Configuration

#### Systemd Service Setup
```ini
[Unit]
Description=Acoustic Lab Production Service
After=network.target postgresql.service redis-server.service
Requires=network.target

[Service]
User=acoustic
Group=acoustic
WorkingDirectory=/var/www/acoustic-lab
Environment=PATH=/var/www/acoustic-lab/venv/bin
EnvironmentFile=/var/www/acoustic-lab/.env
ExecStart=/var/www/acoustic-lab/venv/bin/gunicorn --config scripts/gunicorn.conf.py
ExecReload=/bin kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=60
PrivateTmp=true
RestartSec=5
Restart=always

# Security settings
NoNewPrivileges=yes
PrivateDevices=yes
ProtectHome=yes
ProtectSystem=strict
ReadWritePaths=/var/www/acoustic-lab /var/log/acoustic-lab
LimitNOFILE=65536
MemoryLimit=1G
CPUQuota=75%

[Install]
WantedBy=multi-user.target
```

#### Nginx Reverse Proxy
```nginx
# HTTP to HTTPS redirect
server {
    listen 80;
    server_name acoustic-lab.edu www.acoustic-lab.edu;
    return 301 https://$server_name$request_uri;
}

# HTTPS server
server {
    listen 443 ssl http2;
    server_name acoustic-lab.edu www.acoustic-lab.edu;

    # SSL configuration
    ssl_certificate /etc/letsencrypt/live/acoustic-lab.edu/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/acoustic-lab.edu/privkey.pem;

    # Security headers
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubdomains; preload" always;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=acoustic_lab:10m rate=10r/s;
    limit_req zone=acoustic_lab burst=20 nodelay;

    # Main application
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Health monitoring
    location /health {
        proxy_pass http://127.0.0.1:8000;
        access_log off;
        limit_req off;
    }
}
```

### Phase 3: SSL/TLS Implementation

#### Let's Encrypt Automation
```bash
# Certificate installation
sudo certbot --nginx -d acoustic-lab.edu --non-interactive --agree-tos --email admin@acoustic-lab.edu

# Renewal testing
sudo certbot renew --dry-run
```

#### SSL Configuration Validation
- **Protocol**: TLS 1.2 and 1.3 only
- **Ciphers**: Secure cipher suites only
- **Certificate**: Valid, auto-renewing
- **HSTS**: Enabled with preload

### Phase 4: Monitoring and Logging

#### Service Monitoring
```bash
# Health checks
curl -f https://acoustic-lab.edu/health

# Service status
sudo systemctl status acoustic-lab nginx postgresql redis-server

# Resource monitoring
htop
df -h
free -h
```

#### Log Management
```bash
# Application logs
sudo journalctl -u acoustic-lab -f

# Web server logs
sudo tail -f /var/log/nginx/acoustic-lab_access.log
sudo tail -f /var/log/nginx/acoustic-lab_error.log

# System logs
sudo tail -f /var/log/syslog
```

## Security Requirements

### Network Security
- **Firewall**: UFW with minimal open ports (22, 80, 443)
- **SSH**: Key-based authentication, no password login
- **Rate Limiting**: Application and infrastructure level protection
- **DDoS Protection**: Basic rate limiting and connection limits

### Application Security
- **Secrets Management**: WSP 71 compliant environment variables
- **Input Validation**: Comprehensive validation for all endpoints
- **Error Handling**: Secure error responses without information leakage
- **Session Management**: Secure session handling with Redis

### Infrastructure Security
- **User Isolation**: Non-root service execution
- **File Permissions**: Least privilege access controls
- **Automatic Updates**: Security patch automation
- **Backup Security**: Encrypted backup storage

## Scaling Patterns

### Vertical Scaling
- **CPU**: Increase vCPU allocation based on processing load
- **Memory**: Scale RAM for concurrent user load
- **Storage**: Expand disk for logs and future database growth

### Horizontal Scaling
```nginx
# Load balancer configuration
upstream acoustic_lab_cluster {
    server 10.0.0.1:8000;
    server 10.0.0.2:8000;
    server 10.0.0.3:8000;
}

server {
    location / {
        proxy_pass http://acoustic_lab_cluster;
    }
}
```

### Database Scaling
- **Connection Pooling**: PgBouncer for PostgreSQL
- **Read Replicas**: For read-heavy workloads
- **Sharding**: Future horizontal database scaling

## Deployment Automation

### Automated Deployment Script
```bash
#!/bin/bash
# WSP 89 Compliant Production Deployment

set -e

# Configuration
APP_NAME="acoustic-lab"
DOMAIN_NAME="${DOMAIN_NAME:-acoustic-lab.edu}"
GIT_REPO="${GIT_REPO:-https://github.com/your-org/Foundups-Agent.git}"

# Automated infrastructure setup
./scripts/deploy.sh
```

### Configuration Management
- **Version Control**: Infrastructure as code in repository
- **Environment Specific**: Separate configs for staging/production
- **Secret Management**: External secure storage integration

## Monitoring and Alerting

### Health Checks
- **Application**: `/health` endpoint monitoring
- **Infrastructure**: System resource monitoring
- **Database**: Connection and performance monitoring
- **SSL**: Certificate expiration monitoring

### Alerting Thresholds
- **CPU Usage**: Alert >80% sustained
- **Memory Usage**: Alert >90% usage
- **Disk Space**: Alert <10% free
- **Service Status**: Immediate alert on service failure

## Compliance Verification

### WSP Protocol Compliance
- **WSP 49**: Module structure and organization
- **WSP 71**: Secrets management and security
- **WSP 1**: Core principles and foundation
- **WSP 22**: Documentation and roadmap maintenance

### Security Compliance
- **SSL/TLS**: A+ rating on SSL Labs
- **Firewall**: Minimal attack surface
- **Access Control**: Principle of least privilege
- **Monitoring**: Comprehensive observability

## Maintenance Procedures

### Regular Maintenance
1. **Daily**: Health check verification
2. **Weekly**: Log review and rotation
3. **Monthly**: Security updates and patching
4. **Quarterly**: Performance optimization review

### Emergency Procedures
1. **Service Failure**: Automatic restart via systemd
2. **Security Incident**: Immediate isolation and investigation
3. **Data Loss**: Restore from backups
4. **Performance Issues**: Scale resources or optimize code

## Integration with WSP Ecosystem

### Related Protocols
- **WSP 49**: Module structure foundation
- **WSP 71**: Secrets management integration
- **WSP 22**: Documentation maintenance
- **WSP 1**: Core architectural principles

### Module Integration
- **Deployment Scripts**: Standardized across all modules
- **Configuration Templates**: Reusable infrastructure patterns
- **Monitoring Integration**: Centralized observability platform

---

**WSP 89: Production Deployment Infrastructure Protocol**
**Active - Infrastructure Automation and Security Standards**
**WSP 49, WSP 71, WSP 1, WSP 22 Compliant**
