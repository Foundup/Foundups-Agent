# Social Media Orchestrator

**Domain**: platform_integration  
**Classification**: Social Media Orchestration Service  
**WSP Compliance**: WSP 3, WSP 11, WSP 22, WSP 49

## Purpose

Unified orchestration layer for social media platforms (X/Twitter and LinkedIn) that eliminates redundancy and provides a cohesive interface for cross-platform content management, OAuth coordination, and scheduling.

## Key Features

- **Unified OAuth Management**: Single coordinator for all platform authentication
- **Cross-Platform Content Distribution**: Consistent content formatting across platforms
- **Intelligent Scheduling**: Advanced scheduling engine with platform-specific optimizations
- **Natural Language Understanding**: 0102 understands commands like "post in 2 hours" (NEW)
- **Human Scheduling Interface**: 012 can schedule posts for future execution (NEW)
- **Anti-Detection Posting**: Browser automation with human-like behavior
- **Platform Adapters**: Clean abstraction layer for platform-specific implementations
- **WSP Compliance**: Full adherence to WSP standards for modular architecture

## Architecture

### Core Components
- `SocialMediaOrchestrator`: Main orchestration service
- `OAuthCoordinator`: Unified authentication management
- `ContentOrchestrator`: Content generation and formatting
- `SchedulingEngine`: Advanced post scheduling
- `TwitterAdapter`/`LinkedInAdapter`: Platform-specific implementations
- `AutonomousActionScheduler`: Natural language command understanding (0102)
- `HumanSchedulingInterface`: Human-friendly scheduling interface (012)
- `SimplePostingOrchestrator`: Sequential anti-detection posting

### Integration Points
- X/Twitter module: `modules/platform_integration/x_twitter/`
- LinkedIn modules: Replaces fragmented linkedin_agent, linkedin_scheduler, linkedin_proxy
- AI Intelligence: Content generation via banter_engine
- Infrastructure: OAuth management, logging, compliance

## Dependencies

- Python 3.8+
- asyncio support
- Platform-specific APIs (tweepy, linkedin-api)
- WRE integration for autonomous operations

## Usage

```python
from modules.platform_integration.social_media_orchestrator import SocialMediaOrchestrator

# Initialize orchestrator
orchestrator = SocialMediaOrchestrator()

# Authenticate platforms
await orchestrator.authenticate_platform('twitter', credentials)
await orchestrator.authenticate_platform('linkedin', credentials)

# Post to multiple platforms
await orchestrator.post_content("Hello from FoundUps!", ['twitter', 'linkedin'])
```

## WSP Compliance

- **WSP 3**: Proper domain placement in platform_integration
- **WSP 11**: Complete interface documentation
- **WSP 22**: Comprehensive ModLog maintenance
- **WSP 49**: Full directory structure compliance