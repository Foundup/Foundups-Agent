# FoundUps Agent Roadmap

This roadmap tracks project phases, development cycles, and future planning for FoundUps Agent under the Windsurf modular development model.

## Status Ledger
- ✅ Complete
- 🔄 In Progress
- ⏳ Planned
- ⚠️ Deprecated
- 🧬 LLME Target: [ABC] (Can be used for roadmap items)

## Development Phases

### ✅ Proof of Concept (0.0.x) - Target LLME: ~000-111
- [x] Connect to YouTube livestream
- [x] Authenticate via OAuth
- [x] Send greeting message on join
- [x] Log chat messages per user

### 🔄 Prototype (0.1.x - 0.9.x) - Target LLME: ~110-122
- [x] StreamResolver module for dynamic video ID
- [x] Modular chat processor with LLM hooks
- [x] AI response and moderation module
- [x] Prompt-throttle logic by channel activity
- [x] ModLog updater
- [x] ESM (Emoji Sentiment Mapper) foundation (incl. 111-333 triad mapping)
- [ ] LLM Integration Layer (Core interfaces/plumbing)
- [x] Windsurf Protocol (WSP) development framework (incl. FMAS Compatibility)
- [ ] Agent personality framework

### 🔄 LLM Core Systems (High Priority) - Current LLME: [XYZ], Target LLME: [ABC]
- [ ] Small LLM Integration (GPT)
- [ ] LLM Router System (Perplexity/Gemini/LLama/Claude etc rotation)
- [ ] LLM Integration (Claude)
- [ ] LLM Router Intelligence Algorithm
- [ ] LLM Input/Output Validation

### 🔄 LLM Infrastructure (Medium Priority)
- [ ] LLM Prompt Management System
- [ ] LLM Response Cache System
- [ ] LLM Rate Limiter System
- [ ] LLM Error Recovery System
- [ ] LLM Security & Privacy System

### 🔄 LLM Optimization (Lower Priority)
- [ ] LLM Cost Management Algorithm
- [ ] LLM Fallback System Algorithm
- [ ] LLM Quality Metrics System
- [ ] LLM Performance Analytics
- [ ] LLM Integration Testing Framework
- [ ] LLM A/B Testing System

### ⏳ Minimum Viable Product (1.0.x+) - Target LLME: ~112-222
- [ ] Make bot publicly usable by other YouTubers
- [ ] Website with user onboarding (landing page + auth)
- [ ] Cloud deployment and user instance spin-up
- [ ] Bot tokenization and usage metering
- [ ] Admin dashboard for managing streams
- [ ] AI persona config for streamers
- [ ] Payment/paywall system

## TODO List
*Use `[+todo]` or `[+WSP]` commit convention prefix or add manually here.*

### Memory System Audit (Refactor & Optimize)
**Priority:** [PriorityScore] - **LLME Target:** [ABC]
- [ ] Review chatlogs in memory folders
- [ ] Identify redundant information logs and remove them.
- [ ] compare o://foundups-agent-clean2 to current o://foundups-agent
- [ ] Implement chosen optimizations.
- [ ] Add detailed logging for memory allocation/deallocation events.
- [ ] Update relevant documentation.

## 🧩 MVP Release Phases

### ⏳ Tier 1 — Blockchain Foundation (DAE) (Domain: Blockchain)
- [ ] Blockchain integration module toggle via `.env`
- [ ] Token drop + reward logic (cross-domain with Gamification)
- [ ] Wallet generation for viewers
- [ ] Token reclaim + decay logic

### ⏳ Tier 2 — DAO Evolution (Domain: Blockchain)
- [ ] Token governance structure
- [ ] Voting logic for protocol decisions
- [ ] DAO treasury and fund routing

### 🔄 Gamification Layer (Domain: Gamification)
- [ ] Ledger module for tracking user interactions (points, achievements) (was: Blockchain Ledger)
- [ ] User points system
- [ ] Achievement tracking
- [ ] Reward distribution (integrates with Blockchain for token rewards)
- [ ] Historical data analysis for engagement metrics

### ⏳ Tier 3 — FoundUps Platform (Domain: FoundUps)
- [ ] Framework for onboarding individual FoundUp entities (e.g., JOSI, EDGWIT)
- [ ] Standardized APIs for FoundUp project interaction with core agent services
- [ ] Discovery and management features for multiple FoundUp projects

## Version Guide
### Development Phases (Correlated with WSP 9 & LLME Scores):
- #### POC (0.0.x): Initial development and proof of concept
  - Expected LLME Range: 000-111
  - 0.0.1: First working version
  - 0.0.2-0.0.9: POC improvements and fixes
- #### Prototype (0.1.x - 0.9.x): Feature development and testing
  - Expected LLME Range: 110-122
  - 0.1.x: Basic feature set
  - 0.2.x-0.9.x: Feature expansion and refinement
- #### MVP (1.0.x+): Production-ready releases
  - Expected LLME Range: 112-222
  - 1.0.0: First stable release
  - 1.x.x: Production updates and improvements 