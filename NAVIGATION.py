#!/usr/bin/env python3
"""
NAVIGATION.py - WSP 87 Code Navigation Protocol Implementation

This file maps problems to existing solutions to prevent vibecoding.
0102 agents MUST consult this file BEFORE creating any new code.

Status: ACTIVE - Fully functional with HoloIndex integration
Last Updated: 2025-11-30 - Expanded to include AI intelligence, infrastructure, and HoloDAE modules
WSP Compliance: WSP 87 (Code Navigation), WSP 50 (Pre-Action Verification)

COVERAGE:
- ✅ GotJunk FoundUp (classification, location, storage)
- ✅ AI Intelligence (telemetry monitoring, event processing)
- ✅ Infrastructure (WSP orchestration, MCP management, WRE skills)
- ✅ HoloDAE Coordination (Qwen/Gemma agents, autonomous refactoring)

ACHIEVEMENTS:
- ✅ Surgical debugging: 93% token reduction, 80% time savings vs grep
- ✅ Code extraction: Actual TypeScript snippets from .tsx files
- ✅ Module detection: Correctly identifies all major domains
- ✅ Expanded coverage: 10 → 40+ semantic mappings
"""

# === NEED_TO: Problem -> Solution Mapping ===
# Direct mapping of problems to existing code solutions
NEED_TO = {
    # GotJunk Classification Logic
    "handle item classification": "modules/foundups/gotjunk/frontend/App.tsx:handleClassify()",
    "prevent duplicate item creation": "modules/foundups/gotjunk/frontend/App.tsx:handleClassify() - race condition guards",
    "race condition in classification": "modules/foundups/gotjunk/frontend/App.tsx:handleClassify() - isProcessingClassification guard",
    "onClassify event handling": "modules/foundups/gotjunk/frontend/components/ClassificationModal.tsx:onClassify prop",
    "classification modal duplicate prevention": "modules/foundups/gotjunk/frontend/App.tsx:pendingClassificationItem state management",

    # Generic duplicate prevention (existing implementations)
    "duplicate item prevention": "modules/platform_integration/social_media_orchestrator/src/core/duplicate_prevention_manager.py",
    "social media duplicate posting": "modules/platform_integration/social_media_orchestrator/src/core/duplicate_prevention_manager.DuplicatePreventionManager.mark_as_posted()",

    # Other common patterns
    "user location detection": "modules/foundups/gotjunk/frontend/App.tsx:getCurrentPositionPromise()",
    "geolocation with fallback": "modules/foundups/gotjunk/frontend/App.tsx:initializeApp() - location handling",
    "react state race conditions": "modules/foundups/gotjunk/frontend/App.tsx:handleClassify() - immediate state clearing",

    # AI Intelligence & Monitoring
    "monitor telemetry from HoloDAE": "modules/ai_intelligence/ai_overseer/src/holo_telemetry_monitor.py:HoloTelemetryMonitor",
    "tail JSONL telemetry logs": "modules/ai_intelligence/ai_overseer/src/holo_telemetry_monitor.py:HoloTelemetryMonitor.tail_log()",
    "ai overseer coordinate mission": "modules/ai_intelligence/ai_overseer/src/ai_overseer.py:AIIntelligenceOverseer.coordinate_mission()",
    "ai overseer check false positive": "modules/ai_intelligence/ai_overseer/src/ai_overseer.py:AIIntelligenceOverseer._is_known_false_positive()",
    "ai overseer record false positive": "modules/ai_intelligence/ai_overseer/src/ai_overseer.py:AIIntelligenceOverseer.record_false_positive()",
    "ricDAE MCP integration": "modules/ai_intelligence/ric_dae/src/mcp_tools.py:ResearchIngestionMCP",

    # Infrastructure & Orchestration
    "wsp orchestration": "modules/infrastructure/wsp_orchestrator/src/wsp_orchestrator.py:WSPOrchestrator",
    "coordinate qwen and gemma agents": "modules/infrastructure/wsp_orchestrator/src/wsp_orchestrator.py:WSPOrchestrator.route_to_agent()",
    "mcp server management": "modules/infrastructure/mcp_manager/src/mcp_manager.py:MCPManager",
    "auto-start mcp servers": "modules/infrastructure/mcp_manager/src/mcp_manager.py:MCPManager.ensure_server_running()",
    "wre skills loading": "modules/infrastructure/wre_core/skillz/wre_skills_loader.py:WRESkillsLoader",
    "progressive disclosure for skills": "modules/infrastructure/wre_core/skillz/wre_skills_loader.py:WRESkillsLoader.load_skill_on_demand()",
    "skillz wardrobe": "modules/infrastructure/wre_core/skillz/wre_skills_loader.py:WRESkillsLoader - Wardrobe Skills = advanced prompting system (see WSP 96)",
    "wardrobe skills": "modules/infrastructure/wre_core/skillz/wre_skills_loader.py:WRESkillsLoader - Like clothing outfits the agent wears for specific tasks",
    "load skillz": "modules/infrastructure/wre_core/skillz/wre_skills_loader.py:WRESkillsLoader.load_skill_on_demand()",
    "wre skillz protocol": "WSP_framework/src/WSP_96_WRE_Skills_Wardrobe_Protocol.md - Micro Chain-of-Thought paradigm",

    # WSP Compliance & Pattern Memory
    "scan wsp violations": "modules/infrastructure/wsp_core/src/wsp_compliance_checker.py:WSPComplianceChecker.scan()",
    "check false positives": "modules/infrastructure/wsp_core/src/wsp_compliance_checker.py:WSPComplianceChecker._is_known_false_positive()",
    "pattern memory false positives": "modules/infrastructure/wre_core/src/pattern_memory.py:PatternMemory.is_false_positive()",
    "record learned false positive": "modules/infrastructure/wre_core/src/pattern_memory.py:PatternMemory.record_false_positive()",
    "github wsp automation": "modules/platform_integration/github_integration/src/wsp_automation.py:WSPAutomationManager",

    # HoloDAE Coordination
    "holodae query processing": "holo_index/qwen_advisor/holodae_coordinator.py:HoloDAECoordinator.handle_holoindex_request()",
    "holodae filter false positives": "holo_index/qwen_advisor/holodae_coordinator.py:HoloDAECoordinator._filter_false_positive_results()",
    "qwen strategic analysis": "holo_index/qwen_advisor/holodae_coordinator.py:HoloDAECoordinator.qwen_analyze_context()",
    "qwen autonomous refactoring": "holo_index/qwen_advisor/orchestration/autonomous_refactoring.py:AutonomousRefactoringOrchestrator",
    "gemma pattern validation": "holo_index/qwen_advisor/orchestration/autonomous_refactoring.py:AutonomousRefactoringOrchestrator.gemma_validate_patterns()",

    # Browser Automation & Vision (Sprint A1, V4 complete) - ENHANCED: Multi-tier vision with UI-TARS + Gemini
    "route browser action": "modules/infrastructure/browser_actions/src/action_router.py:ActionRouter.execute()",
    "check driver availability": "modules/infrastructure/browser_actions/src/action_router.py:ActionRouter._ensure_vision()",
    "classify action complexity": "modules/infrastructure/browser_actions/src/action_router.py:ActionRouter.get_driver_for_action()",
    "multi-tier vision routing": "modules/infrastructure/browser_actions/src/action_router.py:ActionRouter._ensure_vision() - Tier 1 UI-TARS → Tier 2 Gemini fallback",
    "initialize ui-tars bridge": "modules/infrastructure/browser_actions/src/action_router.py:ActionRouter._ensure_ui_tars() - Local vision on LM Studio port 1234",
    "initialize gemini vision": "modules/infrastructure/browser_actions/src/action_router.py:ActionRouter._ensure_gemini_vision() - Cloud vision fallback",
    "multi-driver support": "modules/infrastructure/browser_actions/src/action_router.py:DriverType - SELENIUM, TARS, GEMINI, VISION, PLAYWRIGHT",
    "ui-tars bridge connect": "modules/infrastructure/foundups_vision/src/ui_tars_bridge.py:UITarsBridge.connect()",
    "vision executor workflow": "modules/infrastructure/foundups_vision/src/vision_executor.py:VisionExecutor.execute_workflow()",

    # Browser Session Management (Sprint V4 - migrated to foundups_selenium)
    "get browser instance": "modules/infrastructure/foundups_selenium/src/browser_manager.py:BrowserManager.get_browser()",
    "reuse browser session": "modules/infrastructure/foundups_selenium/src/browser_manager.py:BrowserManager.get_browser()",
    "browser singleton manager": "modules/infrastructure/foundups_selenium/src/browser_manager.py:get_browser_manager()",
    "close browser session": "modules/infrastructure/foundups_selenium/src/browser_manager.py:BrowserManager.close_browser()",
    "chrome profile management": "modules/infrastructure/foundups_selenium/src/browser_manager.py:BrowserManager._create_chrome_browser()",
    "youtube browser profile": "modules/infrastructure/foundups_selenium/src/browser_manager.py:BrowserManager._create_chrome_browser() - youtube_move2japan profile",

    # DAE Dependency Launcher (auto-start Chrome + LM Studio)
    "ensure dae dependencies": "modules/infrastructure/dependency_launcher/src/dae_dependencies.py:ensure_dependencies()",
    "launch chrome debug port": "modules/infrastructure/dependency_launcher/src/dae_dependencies.py:launch_chrome()",
    "launch lm studio": "modules/infrastructure/dependency_launcher/src/dae_dependencies.py:launch_lm_studio()",
    "check dependency status": "modules/infrastructure/dependency_launcher/src/dae_dependencies.py:get_dependency_status()",
    "chrome debug port 9222": "modules/infrastructure/dependency_launcher/src/dae_dependencies.py:is_chrome_running()",
    "lm studio port 1234": "modules/infrastructure/dependency_launcher/src/dae_dependencies.py:is_lm_studio_running()",

    # Pattern Learning (Sprint V6)
    "action pattern learning": "modules/infrastructure/foundups_vision/src/action_pattern_learner.py:ActionPatternLearner",
    "pattern learner singleton": "modules/infrastructure/foundups_vision/src/action_pattern_learner.py:get_learner()",
    "record action success": "modules/infrastructure/foundups_vision/src/action_pattern_learner.py:ActionPatternLearner.record_success()",
    "record action failure": "modules/infrastructure/foundups_vision/src/action_pattern_learner.py:ActionPatternLearner.record_failure()",
    "adaptive retry strategy": "modules/infrastructure/foundups_vision/src/action_pattern_learner.py:ActionPatternLearner.get_retry_strategy()",
    "recommend driver": "modules/infrastructure/foundups_vision/src/action_pattern_learner.py:ActionPatternLearner.recommend_driver()",
    "ab test drivers": "modules/infrastructure/foundups_vision/src/action_pattern_learner.py:ActionPatternLearner.start_ab_test()",
    "pattern metrics": "modules/infrastructure/foundups_vision/src/action_pattern_learner.py:ActionPatternLearner.get_metrics()",
    "record human validation": "modules/infrastructure/foundups_vision/src/action_pattern_learner.py:ActionPatternLearner.record_human_validation()",
    "012 feedback recommendations": "modules/infrastructure/foundups_vision/src/action_pattern_learner.py:ActionPatternLearner.get_012_recommendations()",
    "pre action learning display": "modules/infrastructure/foundups_vision/src/action_pattern_learner.py:ActionPatternLearner.display_pre_learning()",
    "post action learning display": "modules/infrastructure/foundups_vision/src/action_pattern_learner.py:ActionPatternLearner.display_post_learning()",

    # Documentation & Architecture (NEW - 2025-12-03)
    "daemon architecture": "docs/DAEMON_ARCHITECTURE_MAP.md - Complete daemon inventory and event queue design",
    "event queue orchestration": "docs/DAEMON_ARCHITECTURE_MAP.md - Unified event queue architecture",
    "daemon coordination": "docs/DAEMON_ARCHITECTURE_MAP.md - Inter-daemon communication patterns",
    "holodae gitpushdae youtube daemons": "docs/DAEMON_ARCHITECTURE_MAP.md - All daemon capabilities mapped",
    "git push social media flow": "docs/GIT_SOCIAL_MEDIA_EVENT_DRIVEN_ARCHITECTURE.md - Event-driven posting architecture",
    "architecture documentation index": "docs/README.md - Central catalog of all architecture docs",
    "session reports": "docs/README.md - Completed work sessions and sprints",
    "vision automation sprints": "docs/VISION_AUTOMATION_SPRINT_MAP.md - Vision automation roadmap (A1-A5, V1-V6)",

    # Testing & Validation (NEW - 2025-12-05)
    "test youtube studio vision": "modules/communication/video_comments/skillz/qwen_studio_engage/tests/ - Vision automation test suite",
    "test qwen studio engage": "modules/communication/video_comments/skillz/qwen_studio_engage/tests/test_qwen_studio_engage.py - Full autonomous flow test",
    "test gemini vision": "modules/communication/video_comments/skillz/qwen_studio_engage/tests/test_gemini_simple.py - Gemini Vision button detection",

    # WRE Skills - Autonomous Engagement (NEW - 2025-12-05)
    "autonomous youtube engagement": "modules/communication/video_comments/skillz/qwen_studio_engage/ - Agentic Studio comment engagement",
    "youtube studio skillz": "modules/communication/video_comments/skillz/qwen_studio_engage/SKILL.md - Qwen+Gemma autonomous engagement",
    "studio comment like reply": "modules/communication/video_comments/skillz/qwen_studio_engage/executor.py - Vision-based engagement execution",
    "youtube studio ui reference": "modules/communication/video_comments/skillz/qwen_studio_engage/VISION_UI_REFERENCE.md - Precise Vision targeting",

    # YouTube Live Audio (Phase 1: Loopback, Phase 2: Archive) - NEW 2026-01-07
    "youtube live audio capture": "modules/platform_integration/youtube_live_audio/src/youtube_live_audio.py:SystemAudioCapture",
    "system audio loopback": "modules/platform_integration/youtube_live_audio/src/youtube_live_audio.py:SystemAudioCapture - WASAPI loopback capture",
    "youtube audio source": "modules/platform_integration/youtube_live_audio/src/youtube_live_audio.py:YouTubeLiveAudioSource",
    "stream audio chunks": "modules/platform_integration/youtube_live_audio/src/youtube_live_audio.py:YouTubeLiveAudioSource.stream_audio_chunks()",
    "video archive extractor": "modules/platform_integration/youtube_live_audio/src/youtube_live_audio.py:VideoArchiveExtractor",
    "list channel videos": "modules/platform_integration/youtube_live_audio/src/youtube_live_audio.py:VideoArchiveExtractor.list_channel_videos() - 0 API quota",
    "extract audio from video": "modules/platform_integration/youtube_live_audio/src/youtube_live_audio.py:VideoArchiveExtractor.extract_audio()",
    "stream video chunks": "modules/platform_integration/youtube_live_audio/src/youtube_live_audio.py:VideoArchiveExtractor.stream_video_chunks()",
    "audio chunk timestamp": "modules/platform_integration/youtube_live_audio/src/youtube_live_audio.py:AudioChunk.timestamp_ms - Video position for deep linking",

    # Voice Command Ingestion (STT + Batch Transcription) - NEW 2026-01-07
    "faster whisper stt": "modules/communication/voice_command_ingestion/src/voice_command_ingestion.py:FasterWhisperSTT",
    "transcribe audio whisper": "modules/communication/voice_command_ingestion/src/voice_command_ingestion.py:FasterWhisperSTT.transcribe()",
    "voice trigger detection": "modules/communication/voice_command_ingestion/src/voice_command_ingestion.py:TriggerDetector",
    "detect 0102 trigger": "modules/communication/voice_command_ingestion/src/voice_command_ingestion.py:TriggerDetector.detect() - Handles '0102' variations",
    "voice command ingestion": "modules/communication/voice_command_ingestion/src/voice_command_ingestion.py:VoiceCommandIngestion",
    "batch transcriber": "modules/communication/voice_command_ingestion/src/voice_command_ingestion.py:BatchTranscriber",
    "transcribe channel videos": "modules/communication/voice_command_ingestion/src/voice_command_ingestion.py:BatchTranscriber.transcribe_channel()",
    "transcript segment": "modules/communication/voice_command_ingestion/src/voice_command_ingestion.py:TranscriptSegment - video_id, timestamp, text, url",
    "save transcripts jsonl": "modules/communication/voice_command_ingestion/src/voice_command_ingestion.py:BatchTranscriber.save_transcripts_jsonl()",
    "what did 012 say": "modules/communication/voice_command_ingestion/src/voice_command_ingestion.py:TranscriptSegment.url - Deep link to exact video moment",

    # Transcript Index (Sprint 7-8) - Semantic Search for Digital Twin - NEW 2026-01-07
    "video transcript index": "modules/communication/voice_command_ingestion/src/transcript_index.py:VideoTranscriptIndex",
    "transcript semantic search": "modules/communication/voice_command_ingestion/src/transcript_index.py:VideoTranscriptIndex.search()",
    "index transcripts jsonl": "modules/communication/voice_command_ingestion/src/transcript_index.py:VideoTranscriptIndex.index_from_jsonl()",
    "search 012 transcripts": "modules/communication/voice_command_ingestion/src/transcript_index.py:search_012_transcripts() - MCP-compatible",
    "digital twin query": "modules/communication/voice_command_ingestion/src/transcript_index.py:search_012_transcripts() - What did 012 say about X?",

    # YouTube Channel Indexing (Menu Integration) - NEW 2026-01-08
    "youtube indexing": "modules/communication/voice_command_ingestion/scripts/index_channel.py:index_channel()",
    "index youtube channel": "modules/communication/voice_command_ingestion/scripts/index_channel.py:index_channel(channel_key, max_videos)",
    "index move2japan": "modules/communication/voice_command_ingestion/scripts/index_channel.py:index_channel('move2japan')",
    "index undaodu": "modules/communication/voice_command_ingestion/scripts/index_channel.py:index_channel('undaodu')",
    "index foundups": "modules/communication/voice_command_ingestion/scripts/index_channel.py:index_channel('foundups')",
    "youtube indexing menu": "modules/communication/voice_command_ingestion/scripts/index_channel.py:run_indexing_menu() - main.py option 1.8",
    "search video transcripts": "modules/communication/voice_command_ingestion/scripts/index_channel.py:search_transcripts(query)",
    # Video Indexer (Multimodal Content Intelligence) - NEW 2026-01-08
    "video indexer": "modules/ai_intelligence/video_indexer/src/video_indexer.py:VideoIndexer",
    "index video content": "modules/ai_intelligence/video_indexer/src/video_indexer.py:VideoIndexer.index_video()",
    "index channel videos": "modules/ai_intelligence/video_indexer/src/video_indexer.py:VideoIndexer.index_channel()",
    "search video content": "modules/ai_intelligence/video_indexer/src/video_indexer.py:VideoIndexer.search()",
    "audio analysis diarization": "modules/ai_intelligence/video_indexer/src/audio_analyzer.py:AudioAnalyzer",
    "extract video quotes": "modules/ai_intelligence/video_indexer/src/audio_analyzer.py:AudioAnalyzer.extract_quotes()",
    "identify video topics": "modules/ai_intelligence/video_indexer/src/audio_analyzer.py:AudioAnalyzer.identify_topics()",
    "visual frame analysis": "modules/ai_intelligence/video_indexer/src/visual_analyzer.py:VisualAnalyzer",
    "detect video shots": "modules/ai_intelligence/video_indexer/src/visual_analyzer.py:VisualAnalyzer.detect_shots()",
    "extract keyframes": "modules/ai_intelligence/video_indexer/src/visual_analyzer.py:VisualAnalyzer.extract_keyframes()",
    "multimodal alignment": "modules/ai_intelligence/video_indexer/src/multimodal_aligner.py:MultimodalAligner",
    "align audio visual moments": "modules/ai_intelligence/video_indexer/src/multimodal_aligner.py:MultimodalAligner.align_moments()",
    "detect video highlights": "modules/ai_intelligence/video_indexer/src/multimodal_aligner.py:MultimodalAligner.detect_highlights()",
    "generate clip candidates": "modules/ai_intelligence/video_indexer/src/clip_generator.py:ClipGenerator.generate_candidates()",
    "score viral potential": "modules/ai_intelligence/video_indexer/src/clip_generator.py:ClipGenerator._score_virality()",
    "video index storage": "modules/ai_intelligence/video_indexer/src/video_index_store.py:VideoIndexStore",
}

# === MODULE_GRAPH: Module Relationships ===
MODULE_GRAPH = {
    "entry_points": {
        "gotjunk_main": "modules/foundups/gotjunk/frontend/App.tsx",
        "classification_flow": "modules/foundups/gotjunk/frontend/components/ClassificationModal.tsx",
        "ai_overseer": "modules/ai_intelligence/ai_overseer/src/ai_overseer.py",
        "holo_telemetry": "modules/ai_intelligence/ai_overseer/src/holo_telemetry_monitor.py",
        "holodae_coordinator": "holo_index/qwen_advisor/holodae_coordinator.py",
        "wsp_orchestrator": "modules/infrastructure/wsp_orchestrator/src/wsp_orchestrator.py",
    },

    "core_flows": [
        # GotJunk flows
        ("capture_photo", "modules/foundups/gotjunk/frontend/App.tsx:handleCapture()"),
        ("show_classification_modal", "modules/foundups/gotjunk/frontend/components/ClassificationModal.tsx"),
        ("handle_classification", "modules/foundups/gotjunk/frontend/App.tsx:handleClassify()"),
        ("save_to_storage", "modules/foundups/gotjunk/frontend/services/storage.ts"),

        # AI Intelligence flows
        ("tail_telemetry", "modules/ai_intelligence/ai_overseer/src/holo_telemetry_monitor.py:tail_log()"),
        ("process_ai_event", "modules/ai_intelligence/ai_overseer/src/ai_overseer.py:process_event()"),
        ("queue_event", "modules/ai_intelligence/ai_overseer/src/ai_overseer.py:queue_event()"),

        # HoloDAE coordination flows
        ("handle_holoindex_request", "holo_index/qwen_advisor/holodae_coordinator.py:handle_holoindex_request()"),
        ("qwen_analyze", "holo_index/qwen_advisor/holodae_coordinator.py:qwen_analyze_context()"),
        ("autonomous_refactor", "holo_index/qwen_advisor/orchestration/autonomous_refactoring.py"),

        # Infrastructure flows
        ("route_to_agent", "modules/infrastructure/wsp_orchestrator/src/wsp_orchestrator.py:route_to_agent()"),
        ("ensure_mcp_server", "modules/infrastructure/mcp_manager/src/mcp_manager.py:ensure_server_running()"),
        ("load_skill_on_demand", "modules/infrastructure/wre_core/skillz/wre_skills_loader.py:load_skill_on_demand()"),
    ],

    "module_relationships": {
        # GotJunk relationships
        "App.tsx": ["ClassificationModal.tsx", "storage.ts", "useViewport.ts"],
        "ClassificationModal.tsx": ["types.ts", "ActionSheetDiscount.tsx", "ActionSheetBid.tsx"],

        # AI Intelligence relationships
        "ai_overseer.py": ["holo_telemetry_monitor.py", "event_processor.py"],
        "holo_telemetry_monitor.py": ["ai_overseer.py"],

        # HoloDAE relationships
        "holodae_coordinator.py": ["pid_detective.py", "mcp_integration.py", "telemetry_formatter.py", "module_metrics.py", "monitoring_loop.py"],

        # Infrastructure relationships
        "wsp_orchestrator.py": ["mcp_manager.py", "wre_core"],
        "mcp_manager.py": ["mcp_servers"],
    }
}

# === PROBLEMS: Common Issues & Solutions ===
PROBLEMS = {
    "duplicate_classification_calls": {
        "symptoms": "Items created multiple times, race conditions",
        "debug": "Check isProcessingClassification flag and pendingClassificationItem state",
        "solution": "Use immediate state clearing + processing guard in handleClassify()",
        "location": "modules/foundups/gotjunk/frontend/App.tsx:handleClassify()"
    },

    "missing_location_data": {
        "symptoms": "Items saved without GPS coordinates",
        "debug": "Check navigator.geolocation permissions and error handling",
        "solution": "Use getCurrentPositionPromise() with proper fallbacks",
        "location": "modules/foundups/gotjunk/frontend/App.tsx:getCurrentPositionPromise()"
    }
}

# === DANGER: Areas Requiring Caution ===
DANGER = {
    "modules/foundups/gotjunk/frontend/App.tsx:handleClassify()": "Race condition prone - always check isProcessingClassification before processing",
    "modules/foundups/gotjunk/frontend/App.tsx:pendingClassificationItem": "Must be cleared immediately to prevent duplicate processing",
}

# === DATABASES: Data Storage Locations ===
DATABASES = {
    "gotjunk_items": "IndexedDB via modules/foundups/gotjunk/frontend/services/storage.ts",
    "user_preferences": "localStorage in ClassificationModal.tsx",
}

# === COMMANDS: Operational Commands ===
COMMANDS = {
    "search_code": "python holo_index.py --search 'query'",
    "index_navigation": "python holo_index.py --index-code",
}
