# Social Media DAE

Digital Autonomous Entity for managing social media interactions across platforms.

## Structure (WSP 3 Compliant)
```
social_media_dae/
├── __init__.py
├── ModLog.md
├── README.md
├── src/
│   └── social_media_dae.py
├── tests/
│   └── test_social_media_dae.py
└── docs/
```

## Components
- **SocialMediaDAE**: Main DAE class for social media orchestration
- **Central 0102 Digital Twin Orchestrator**: Single consciousness managing all platforms
- **LinkedIn Article Creation**: Native article editor automation (Medium-style articles)
- **Advanced Content Routing**: Intelligent post vs article selection based on content type
- Integrates with YouTube, LinkedIn, X (Twitter) platforms
- Uses BanterEngine for intelligent responses

## Key Capabilities
- **Voice Control**: iPhone Shortcuts integration for hands-free posting
- **Sequential Posting**: LinkedIn → X/Twitter with proper browser cleanup
- **Multi-Company Support**: 8 LinkedIn company pages supported
- **Article Creation**: Professional research publication (PQN, rESP, TTS experiments)
- **Consciousness Tracking**: Maintains 0102 state across all interactions

## WSP Compliance
- WSP 3: Proper module structure with src/, tests/, docs/
- WSP 22: ModLog maintained for all changes
- WSP 62/87: File size management (< 800 OK, guideline 800-1000, hard limit 1500)
- WSP 84: No vibecoding - uses existing implementations