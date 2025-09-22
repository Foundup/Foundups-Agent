# NAVIGATION Coverage Log

| Need | Location | Last Verified | Owner |
|------|----------|---------------|-------|
| monitor youtube stream | python main.py --youtube | 2025-09-19 | 0102 Ops |
| find active stream | modules.communication.livechat.src.auto_moderator_dae.find_livestream() | 2025-09-19 | Livechat Cube |
| send chat message | modules.communication.livechat.src.chat_sender.ChatSender.send_message() | 2025-09-19 | Livechat Cube |
| process chat message | modules.communication.livechat.src.message_processor.MessageProcessor.process_message() | 2025-09-19 | Livechat Cube |
| handle consciousness trigger | modules.communication.livechat.src.consciousness_handler.ConsciousnessHandler | 2025-09-19 | Livechat Cube |
| post to linkedin/twitter | modules.platform_integration.social_media_orchestrator.src.simple_posting_orchestrator.handle_stream_detected() | 2025-09-19 | Platform Integration |
| check if already posted | modules.platform_integration.social_media_orchestrator.src.simple_posting_orchestrator.check_if_already_posted() | 2025-09-19 | Platform Integration |
| check youtube quota | modules.platform_integration.youtube_auth.src.quota_monitor.QuotaMonitor | 2025-09-19 | Platform Integration |
| throttle api calls | modules.communication.livechat.src.intelligent_throttle_manager.IntelligentThrottleManager | 2025-09-19 | Infra Ops |
| get player stats | modules.gamification.whack_a_magat.src.player_manager.PlayerManager.get_stats() | 2025-09-19 | Gamification |
| handle timeout | modules.gamification.whack_a_magat.src.timeout_announcer.TimeoutAnnouncer | 2025-09-19 | Gamification |
| monitor pqn consciousness | modules.ai_intelligence.pqn_alignment.src.pqn_research_dae_orchestrator.PQNResearchDAEOrchestrator | 2025-09-19 | PQN Lab |
| broadcast pqn to chat | modules.ai_intelligence.pqn_alignment.src.pqn_chat_broadcaster.PQNChatBroadcaster | 2025-09-19 | PQN Lab |
| route wre plugins | modules.infrastructure.wre_core.wre_master_orchestrator.src.wre_master_orchestrator.WREMasterOrchestrator.execute() | 2025-09-19 | WRE Core |
| recall pattern memory | modules.infrastructure.wre_core.wre_master_orchestrator.src.wre_master_orchestrator.PatternMemory.get() | 2025-09-19 | WRE Core |
| run navigation audit | NAVIGATION_COVERAGE.md -> update and commit | 2025-09-19 | DocumentationAgent |
| validate navigation schema | python -m tests.navigation.test_navigation_schema | 2025-09-19 | Test Harness |
| boot auto moderator dae | modules.communication.livechat.src.auto_moderator_dae.AutoModeratorDAE.run | 2025-09-19 | Livechat Cube |
| poll chat messages | modules.communication.livechat.src.chat_poller.ChatPoller.poll_messages | 2025-09-19 | Livechat Cube |
| send throttled chat reply | modules.communication.livechat.src.livechat_core.LiveChatCore.send_chat_message | 2025-09-19 | Livechat Cube |
| process slash command | modules.communication.livechat.src.command_handler.CommandHandler.handle_whack_command | 2025-09-19 | Gamification |
| adjust throttle window | modules.communication.livechat.src.intelligent_throttle_manager.IntelligentThrottleManager.calculate_adaptive_delay | 2025-09-19 | Infra Ops |
| drive agentic engagement | modules.communication.livechat.src.agentic_chat_engine.AgenticChatEngine.generate_agentic_response | 2025-09-19 | Livechat Cube |
| manage chat memory | modules.communication.livechat.src.chat_memory_manager.ChatMemoryManager.store_message | 2025-09-19 | Livechat Cube |
| generate greeting | modules.communication.livechat.src.greeting_generator.GreetingGenerator.generate_greeting | 2025-09-19 | Livechat Cube |
| call grok integration | modules.communication.livechat.src.llm_integration.GrokIntegration.creative_response | 2025-09-19 | Livechat Cube |
| fallback fact response | modules.communication.livechat.src.llm_bypass_engine.LLMBypassEngine.process_input | 2025-09-19 | Livechat Cube |
| analyze moderation stats | modules.communication.livechat.src.moderation_stats.ModerationStats.record_violation | 2025-09-19 | Livechat Cube |
| adjust quota polling | modules.communication.livechat.src.quota_aware_poller.QuotaAwarePoller.calculate_optimal_interval | 2025-09-19 | Livechat Cube |
| trigger stream handshake | modules.communication.livechat.src.stream_trigger.StreamTrigger.create_trigger_instructions | 2025-09-19 | Livechat Cube |
| integrate mcp youtube | modules.communication.livechat.src.mcp_youtube_integration.MCPYouTubeIntegration.connect_all | 2025-09-19 | Livechat Cube |

| git linkedin bridge | modules.platform_integration.linkedin_agent.src.git_linkedin_bridge.GitLinkedInBridge | 2025-09-19 | Platform Integration |
| git push and post | main.py --git (Push to Git and post to LinkedIn/Twitter) | 2025-09-19 | Platform Integration |
| post to linkedin | modules.platform_integration.social_media_orchestrator.src.simple_posting_orchestrator.handle_stream_detected() | 2025-09-19 | Platform Integration |
