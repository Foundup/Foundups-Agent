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

### Refactored Modular Architecture (V021)
The module has been refactored from a monolithic 996-line file into focused, single-responsibility components:

**Core Components** (in `src/core/`):
- `DuplicatePreventionManager`: Duplicate detection with enhanced logging and database persistence
- `LiveStatusVerifier`: Stream status verification with 5-minute caching to reduce API calls
- `ChannelConfigurationManager`: Channel configuration and platform account mapping
- `PlatformPostingService`: Platform-specific posting (LinkedIn + X/Twitter) with browser configuration
- `RefactoredPostingOrchestrator`: Clean coordinator that uses all core components

**Migration Support**:
- `orchestrator_migration.py`: Backward compatibility bridge (drop-in replacement)
- Migration bridge ensures zero breaking changes to existing code

**Legacy Components** (being phased out):
- `SimplePostingOrchestrator`: Original monolithic implementation (996 lines)
- Will be removed once migration is complete

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

### New Refactored API (Recommended)
```python
from modules.platform_integration.social_media_orchestrator.src.refactored_posting_orchestrator import get_orchestrator

# Get orchestrator instance
orchestrator = get_orchestrator()

# Handle stream detection event
result = orchestrator.handle_stream_detected(
    video_id='VIDEO_123',
    title='My Live Stream',
    url='https://youtube.com/watch?v=VIDEO_123',
    channel_name='@FoundUps'
)
```

### Migration Bridge (Zero Changes Needed)
```python
from modules.platform_integration.social_media_orchestrator.src.orchestrator_migration import handle_stream_detected

# Drop-in replacement - no code changes needed!
result = handle_stream_detected('VIDEO_123', 'My Live Stream', 'https://youtube.com/...', '@FoundUps')
```

### Individual Core Components
```python
from modules.platform_integration.social_media_orchestrator.src.core import (
    DuplicatePreventionManager,
    PlatformPostingService,
    ChannelConfigurationManager
)

# Use components independently
duplicate_mgr = DuplicatePreventionManager()
posting_service = PlatformPostingService()
```

## Refactoring Benefits (V021)

### Before vs After
- **Before**: 996 lines in single monolithic file
- **After**: 1,539 lines across 6 focused modules (better organized + enhanced docs/logging)

### Architecture Improvements
- ✅ **Single Responsibility**: Each module has one clear purpose
- ✅ **Testability**: Easy to write focused unit tests (23+ tests created)
- ✅ **Maintainability**: Changes isolated to specific modules
- ✅ **Reusability**: Components work independently
- ✅ **Debugging**: Issues traced to specific modules
- ✅ **Performance**: 5-minute caching reduces API calls
- ✅ **Browser Config**: Edge for @Foundups, Chrome for @GeozeAi
- ✅ **Migration**: Zero breaking changes with migration bridge

### Enhanced Features
- Duplicate prevention with visual logging indicators
- Live status verification with intelligent caching
- Channel configuration with JSON persistence
- Platform-specific posting with proper browser assignment
- Comprehensive error handling and validation

## WSP Compliance

- **WSP 3**: Proper domain placement in platform_integration
- **WSP 11**: Complete interface documentation
- **WSP 22**: Comprehensive ModLog maintenance
- **WSP 49**: Full directory structure compliance
- **WSP 50**: Pre-action verification in all operations
- **WSP 72**: Block independence achieved through modularization
- **WSP 87**: HoloIndex navigation entries for all components