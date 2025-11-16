# GotJUNK? FoundUp - Development Roadmap

---

## 📖 Vision & Architecture

**CRITICAL**: Read the comprehensive vision documents before starting any Phase 3+ work:

- **[GJ_00_Vision.md](docs/vision/GJ_00_Vision.md)** - Overall system architecture (Stuff + Liberty Alert, Globs, Mesh+Cloud, Privacy)
- **[GJ_10_Chat_and_Message_System.md](docs/vision/GJ_10_Chat_and_Message_System.md)** - Ephemeral messaging & IRC channels
- **[GJ_20_Security_and_Identity.md](docs/vision/GJ_20_Security_and_Identity.md)** - Keys, trust tiers, anti-VPN verification
- **[GJ_30_Media_YouTube_Integration.md](docs/vision/GJ_30_Media_YouTube_Integration.md)** - Unlisted video storage for LA
- **[GJ_40_Glob_and_Data_Model.md](docs/vision/GJ_40_Glob_and_Data_Model.md)** - Data architecture & AI coordination
- **[GJ_50_AI_Voice_Assistant.md](docs/vision/GJ_50_AI_Voice_Assistant.md)** - 012 ↔ 0102 voice interface, WSP_77 local DAE

**For 0102/012 Context**: Each vision doc contains micro-sprints designed as WSP-compliant prompts. Copy relevant sections into your context when starting a new sprint.

---

## Phase 1: PoC + Liberty Alert Foundation (COMPLETE ✅)

**Status**: Deployed to Cloud Run via AI Studio
**Duration**: Initial build
**Goal**: Validate core concept - rapid photo capture with swipe organization

### Features Delivered

#### Core Infrastructure
- [x] Photo capture with camera API
- [x] Fullscreen tap-to-capture camera flow
- [x] Geolocation tagging (GPS coordinates)
- [x] 50km radius geo-filtering (glob system foundation)
- [x] Swipe interface (keep/delete)
- [x] Local storage (IndexedDB via localforage)
- [x] PWA manifest (installable app)
- [x] Service worker (offline support)
- [x] Video capture with countdown
- [x] Export functionality
- [x] Cloud Run deployment
- [x] AI Studio integration

#### Liberty Alert System (2025-11-16)
- [x] **16 Classification Types** across 4 pillars:
  - [x] Commerce (3): Free, Discount, Bid
  - [x] Share Economy (2): Share, Wanted
  - [x] Mutual Aid Food (6): Soup Kitchen, BBQ, Dry Food, Pick, Garden, Food (deprecated)
  - [x] Mutual Aid Shelter (3): Couch (1N), Camping (2N), Housing
  - [x] Emergency Alerts (2): ICE (60m), Police (5m)
- [x] **SOS Morse Code Unlock** (`... ___ ...`) - persistent via localStorage
- [x] **Classification Modal**:
  - [x] Regular camera: Free/Discount/Bid/Share/Wanted
  - [x] Liberty camera: Accordion menu (Alert!/Food!/Shelter!)
  - [x] Long-press to customize discount %, bid duration, stay limits, alert timers
- [x] **Time-Based Expiration**:
  - [x] AlertTimer for ICE/police with countdown
  - [x] StayLimit for couch/camping with night limits
- [x] **Complete Display Pipeline**:
  - [x] ClassificationBadge - All 16 types with emojis, time displays
  - [x] MapClusterMarker - Color-coded for all 16 types
  - [x] Dynamic filters in My Items & Browse tabs
  - [x] PhotoGrid with classification badges

### Technical Achievements
- React 19 + TypeScript foundation
- Vite build pipeline
- Framer Motion animations
- Gemini AI SDK integration
- Progressive Web App capabilities
- Haversine distance calculations

### Deployment
- ✅ Google AI Studio project created
- ✅ One-click Cloud Run deployment
- ✅ HTTPS endpoint active
- ✅ Auto-scaling configured

---

## Phase 2: UX Polish & Event Lifecycle (CURRENT 🚧)

**Status**: Ready to Resume
**Duration**: 1-2 weeks
**Goal**: Polish Liberty Alert UX, add scheduled events, auto-cleanup

**Current Build**: 473.48 kB (gzip: 142.18 kB)
**Last Update**: 2025-11-16 - All LA categories display correctly

### Completed in Phase 2
- [x] Persistent Liberty unlock (localStorage)
- [x] Dynamic filter dropdowns (My Items & Browse)
- [x] Fullscreen camera with tap-to-capture
- [x] Simplified nav bar layout (`[<] [>] ... [📷]`)
- [x] All 16 classification types working end-to-end

### Priority Features (Next Up)

#### Event Lifecycle & Cleanup (P0)
- [ ] **Auto-Delete Expired Alerts**
  - [ ] Background job (60s interval) to remove expired items
  - [ ] Based on `alertTimer.expiresAt` for ICE/police
  - [ ] UI notification when alerts expire
  - [ ] Cleanup runs on app start + periodic

- [ ] **Scheduled Events UI**
  - [ ] Faded badges for future events (not yet started)
  - [ ] Display: "BBQ this Saturday 2pm" with date/time
  - [ ] "NOW" badge for events currently happening
  - [ ] Fade out after event completion
  - [ ] Event creation flow (date/time picker for food/shelter)

#### Map Improvements (P1)
- [ ] **Global Liberty Alert View**
  - [ ] Zoom to world map (level 2) when viewing all alerts
  - [ ] Larger Liberty statue markers (🗽) in global view
  - [ ] Swipe up gesture to return to home location
  - [ ] Pre-populated sample alerts at real conflict zones

- [ ] **Enhanced Clustering**
  - [ ] Alert priority indicators (red for ICE/police)
  - [ ] Category-specific marker shapes
  - [ ] Animated pulsing for recent alerts

### Security & Compliance (Design-Only checkpoint - 2025-11-15)
- [x] Documented future identity/encryption plan in `docs/SECURITY_IDENTITY.md` (on-device keypairs, FaceID + spoken passphrase gate, LA chat E2EE, later blockchain identity); design-only, no implementation in current sprints.
- [x] Added wardrobe skill `skills/gotjunk_audit.json` for audit-only runs; use AI_overseer/wardrobe to trigger reviews (no auto-fix).
- [ ] Implement identity/encryption hooks and LA chat E2EE (defer to Phase 3 - see GJ_20)

### Deferred to Phase 3 (AI Integration)

#### AI Integration (P0)
- [ ] Gemini Vision API for image analysis
- [ ] **AI-Powered Pricing Workflow** (Core Feature)
  - [ ] User snaps photo of item
  - [ ] Gemini Vision analyzes item (brand, condition, market value)
  - [ ] Three pricing options presented:
    - [ ] **FREE** - Give away (charity/friends)
    - [ ] **75% DISCOUNT** (default) - Quick sale price
    - [ ] **AUCTION** (default 75hr countdown) - Maximum value
  - [ ] AI suggests price based on:
    - [ ] Item category and condition
    - [ ] Local market data (if available)
    - [ ] Similar item comparisons
- [ ] **Voice Chat About Items**
  - [ ] User can talk to AI about item history/story
  - [ ] AI asks clarifying questions (age, condition, sentimental value)
  - [ ] Conversation influences pricing suggestion
  - [ ] Uses Gemini multimodal (voice + vision + text)
- [ ] Auto-categorization of captured items
  - [ ] Junk vs. Keep vs. Sell suggestions
  - [ ] Category labels (furniture, electronics, documents, etc.)
  - [ ] Confidence scores
- [ ] Smart batch operations
  - [ ] "Price all items" action
  - [ ] "Export sellable items" action
  - [ ] Category-based pricing profiles

#### Enhanced Export (P0)
- [ ] ZIP export with metadata JSON
- [ ] Include geolocation in export
- [ ] Timestamp and category data
- [ ] Optional image compression
- [ ] Export statistics (kept vs. deleted)

#### UX Improvements (P1)
- [ ] Undo swipe decision
- [ ] Batch selection mode
- [ ] Search/filter captured items
- [ ] Sort by date/location/category
- [ ] Gallery view enhancements
- [ ] Loading states and skeleton screens

#### Performance (P1)
- [ ] Image lazy loading optimization
- [ ] Virtual scrolling for large galleries
- [ ] Web Worker for heavy processing
- [ ] IndexedDB query optimization
- [ ] Reduce bundle size (tree shaking)

#### Testing (P2)
- [ ] E2E tests (Playwright)
- [ ] Unit tests for utilities
- [ ] Geolocation mocking for tests
- [ ] Camera API mocking for tests
- [ ] CI/CD pipeline

### Technical Debt
- [ ] Error boundary implementation
- [ ] Proper loading states
- [ ] Network error handling
- [ ] Storage quota monitoring
- [ ] Type safety improvements

### Deployment Updates
- [ ] Environment variable management
- [ ] Deployment automation script
- [ ] Cloud Run monitoring setup
- [ ] Performance metrics tracking

---

## Phase 3: Chat, Security, Media, Cloud (PLANNED 📋)

**Status**: Not Started
**Duration**: 4-6 weeks
**Goal**: Implement foundational security, ephemeral chat, video storage, and cloud backend

**CRITICAL**: Follow the micro-sprints defined in vision docs. Each sprint is designed as a WSP-compliant, standalone build task.

### 🔐 Security & Identity (GJ_20) — P0

**See**: [GJ_20_Security_and_Identity.md](docs/vision/GJ_20_Security_and_Identity.md) for detailed sprints

- [ ] **Sprint 1**: Local Keypair & QR Identity
  - [ ] WebCrypto Ed25519 keypair generation
  - [ ] Encrypted private key storage (IndexedDB)
  - [ ] QR code display of public key
  - [ ] "My ID" screen in UI

- [ ] **Sprint 2**: Trust Tier Management
  - [ ] TrustTier enum (Trusted/Known/New)
  - [ ] Local mapping: `{ [publicKey]: TrustTier }`
  - [ ] UI to set trust levels per contact
  - [ ] Badge display in future chat

- [ ] **Sprint 3**: Location Verification (Anti-VPN)
  - [ ] LocationProof data model
  - [ ] GPS + image capture flow
  - [ ] Backend AI verification endpoint
  - [ ] Signed proof storage for glob

- [ ] **Sprint 4**: Key Rotation & Backward Compatibility
  - [ ] Historical keys list
  - [ ] Message verification from old keys
  - [ ] Stable identity ID across rotations

- [ ] **Sprint 5**: Face + Passphrase (Design-Only)
  - [ ] WebAuthn/biometric documentation
  - [ ] LA unlock flow design
  - [ ] Graceful degradation plan

### 💬 Chat & Message System (GJ_10) — P0

**See**: [GJ_10_Chat_and_Message_System.md](docs/vision/GJ_10_Chat_and_Message_System.md) for detailed sprints

- [ ] **Sprint 1**: Local Per-Item Chat (Stuff Only)
  - [ ] Message/ItemChatThread data models
  - [ ] chatStorage wrapper (IndexedDB)
  - [ ] Simple chat UI for Stuff items
  - [ ] 7-day TTL + pruning

- [ ] **Sprint 2**: Extend to Liberty Alert (Open Bulletin)
  - [ ] LA-specific chat (ice/police/food/shelter)
  - [ ] Shorter TTL (1-72h based on category)
  - [ ] LA chat icon in full-screen image view

- [ ] **Sprint 3**: Trust Tiers in Chat
  - [ ] Trust tier badges (⭐/✅/👤)
  - [ ] senderTrustTier snapshot in messages
  - [ ] Display-only (no handshake yet)

- [ ] **Sprint 4**: Invite-Only LA IRC Channels
  - [ ] LAChannel data model
  - [ ] Create channel from LA full-screen
  - [ ] QR invite + local contact selection
  - [ ] Member-only message visibility

- [ ] **Sprint 5**: Ephemeral Cleanup & Mesh/Cloud Hooks
  - [ ] Background cleanup job
  - [ ] ChatTransport abstraction
  - [ ] Local transport implementation
  - [ ] Document future mesh/Firestore plug-ins

### 🎥 Media & YouTube Integration (GJ_30) — P1

**See**: [GJ_30_Media_YouTube_Integration.md](docs/vision/GJ_30_Media_YouTube_Integration.md) for detailed sprints

- [ ] **Sprint 1**: Backend Upload Skeleton
  - [ ] Cloud Function/Run endpoint
  - [ ] YouTube Data API integration
  - [ ] Unlisted video upload
  - [ ] Return youtubeVideoId

- [ ] **Sprint 2**: Frontend Video Capture
  - [ ] MediaRecorder in PWA
  - [ ] Review/confirm flow
  - [ ] Upload to GCS → backend

- [ ] **Sprint 3**: LA View + Playback
  - [ ] Add videoRef to LA items
  - [ ] Embedded YouTube player
  - [ ] No share/link exposure

- [ ] **Sprint 4**: AI Summaries & Moderation
  - [ ] Transcript/frame analysis
  - [ ] Category validation
  - [ ] Abuse detection

### ☁️ Glob & Cloud Backend (GJ_40) — P1

**See**: [GJ_40_Glob_and_Data_Model.md](docs/vision/GJ_40_Glob_and_Data_Model.md) for detailed sprints

- [ ] **Sprint 1**: Glob ID + Local Filtering
  - [ ] Formalize globId (geohash+radius)
  - [ ] Tag items with globId
  - [ ] Client-side filtering

- [ ] **Sprint 2**: Firestore Skeleton
  - [ ] Firestore collections: `globs/{globId}/items`, `/alerts`
  - [ ] uploadItemMetadata() function
  - [ ] listenToGlobItems() realtime listener

- [ ] **Sprint 3**: Alert Storage & TTL
  - [ ] Store alerts with expiresAt
  - [ ] Cloud Function for cleanup
  - [ ] Client respects server TTL

- [ ] **Sprint 4**: AI Coordination Hooks
  - [ ] globs/{globId}/stats document
  - [ ] AI-computed needs (food/shelter/ICE)
  - [ ] Display "High food need" overlays

### 🎤 AI Voice Assistant (GJ_50) — P1

**See**: [GJ_50_AI_Voice_Assistant.md](docs/vision/GJ_50_AI_Voice_Assistant.md) for detailed sprints

**Nav Bar Layout**: `[<] [>] ... [📷] [🎤]`
- Camera icon (📷) - Always visible on all pages
- AI MIC icon (🎤) - Voice interface to DAE system (012 ↔ 0102)

**Core Concept**: User (012) speaks to DAE (0102) → Decision skill routes to wardrobe skill → Task executed → Voice response

- [ ] **Sprint 1**: Voice Input Skeleton (PWA)
  - [ ] Web Speech API integration (SpeechRecognition)
  - [ ] Tap 🎤 → listening animation
  - [ ] Display transcript in UI
  - [ ] No AI processing yet (just transcript)

- [ ] **Sprint 2**: Decision Skill (Intent Classification)
  - [ ] Gemma for fast pattern matching
  - [ ] Intent categories (classify, navigate, alert, query, help)
  - [ ] Route intent → wardrobe skill
  - [ ] Text response from skill execution

- [ ] **Sprint 3**: Wardrobe Skill Integration
  - [ ] Create skills: gotjunk_classify, gotjunk_map_filter, gotjunk_liberty_alert, gotjunk_system_info
  - [ ] Skill executor (load, execute, return response)
  - [ ] Error handling (skill not found, execution failed)

- [ ] **Sprint 4**: Voice Response (TTS)
  - [ ] Web Speech API TTS (SpeechSynthesis)
  - [ ] Natural voice selection
  - [ ] Show text AND speak response
  - [ ] Visual indicator during TTS

- [ ] **Sprint 5**: WSP_77 Local DAE (Gemma + Qwen)
  - [ ] Gemma on-device (WebGPU/WASM) for fast intent classification
  - [ ] Qwen strategic routing for complex queries
  - [ ] Store successful voice → skill mappings
  - [ ] Local-first (cloud only for heavy processing)

- [ ] **Sprint 6**: Context Awareness
  - [ ] Understand current page (map, my items, browse)
  - [ ] Use selected item for "classify this"
  - [ ] Default to current GPS for "create alert"
  - [ ] Context-aware responses

- [ ] **Sprint 7**: Continuous Conversation (Design-Only)
  - [ ] Conversation history (last 5 interactions)
  - [ ] Pronouns and follow-up questions
  - [ ] Chat-like UI (speech bubbles)
  - [ ] 24h auto-delete (privacy)

### 🌐 Core Mesh Network Integration (P2 - Deferred)

#### Decentralized Emergency Mesh (Mesh Alert v2.0)
- [ ] **Hybrid Network Architecture**
  - [ ] Internet mode: Normal cloud sync via backend
  - [ ] Mesh mode: BLE/WiFi Direct peer-to-peer when offline
  - [ ] Automatic mode switching based on connectivity
  - [ ] Seamless user experience (no UI changes)

- [ ] **Mesh-Compatible Alert Packets**
  - [ ] Small encrypted packets (<1KB) for mesh transmission
  - [ ] Structure: `{type, gps, timestamp, expires, id, signature}`
  - [ ] No photos in mesh mode (deferred to cloud sync)
  - [ ] TTL-based propagation (ICE: 5min, Food: 48hrs, Tools: 7 days)

- [ ] **Liberty Alert Mesh Categories**
  - [ ] 🧊 ICE Raids (always mesh)
  - [ ] 🚓 Police Activity (always mesh)  
  - [ ] 🍞 Food Needs (mesh optional)
  - [ ] 🏠 Shelter Requests (mesh optional)
  - [ ] 🔍 Wanted Items (mesh optional)
  - [ ] 🔄 Tool Sharing (mesh optional)

- [ ] **Neighborhood Mesh Mode**
  - [ ] Auto-activation when internet weakens
  - [ ] 10-150m radius local propagation
  - [ ] Visual overlay: "🟢 Local Mesh Active"
  - [ ] Map zooms to 2-5 block region
  - [ ] Mutual aid prioritization in offline mode

#### Enhanced Liberty Alert System
- [ ] **Mesh Broadcasting**
  - [ ] WebRTC P2P mesh for alert propagation
  - [ ] Peer discovery and connection management
  - [ ] Alert deduplication across mesh
  - [ ] Anonymous broadcasting (no user IDs)

- [ ] **Emergency Response Features**
  - [ ] Offline map with cached tiles
  - [ ] Emergency contact sharing via mesh
  - [ ] Resource coordination (food, shelter, tools)
  - [ ] Real-time peer count display

### User Features

#### Authentication & Cloud Sync (P0)
- [ ] User authentication (Firebase Auth or Supabase)
- [ ] Cloud storage integration
- [ ] Multi-device sync with conflict resolution
- [ ] Cross-device geofencing
- [ ] Mesh-to-cloud synchronization when online

#### Advanced AI Integration (P1)
- [ ] **AI-Powered Mesh Optimization**
  - [ ] Smart routing for mesh packets
  - [ ] Predictive offline mode activation
  - [ ] Optimal peer selection for relay
  - [ ] Battery-aware mesh participation

- [ ] **Natural Language Processing**
  - [ ] Voice commands for emergency alerts
  - [ ] "Show me food near me" (works offline)
  - [ ] "Broadcast shelter needed" (mesh mode)
  - [ ] Multi-language support for diverse communities

#### Collaboration & Community (P1)
- [ ] **Mesh-Based Sharing**
  - [ ] Share captures with nearby users
  - [ ] Collaborative organization in local mesh
  - [ ] Public/private capture modes
  - [ ] Community verification system

- [ ] **Resource Economy**
  - [ ] FoundUps wallet integration (testnet)
  - [ ] Fiat-first pricing (hide crypto complexity)
  - [ ] Local economy mesh transactions
  - [ ] Barter system for mutual aid

### Platform Features

#### Mesh Network Infrastructure (P0)
- [ ] **Decentralized Architecture**
  - [ ] BLE/WiFi Direct mesh implementation
  - [ ] Automatic peer discovery
  - [ ] Mesh health monitoring
  - [ ] Fallback to cloud when mesh unavailable

- [ ] **Security & Privacy**
  - [ ] End-to-end encryption for mesh packets
  - [ ] Anonymous broadcasting system
  - [ ] Zero-knowledge location sharing
  - [ ] Privacy-preserving peer discovery

#### Admin & Analytics (P1)
- [ ] Mesh network health dashboard
- [ ] Usage statistics (anonymized)
- [ ] Error tracking with mesh-specific metrics
- [ ] A/B testing for mesh features
- [ ] Community impact metrics

#### Infrastructure (P1)
- [ ] Database migration (PostgreSQL)
- [ ] Redis caching for mesh state
- [ ] CDN for static assets
- [ ] Rate limiting for mesh broadcasts
- [ ] API versioning for mesh endpoints

### Quality Assurance
- [ ] **Mesh Testing**
  - [ ] Offline functionality testing
  - [ ] Mesh network stress testing
  - [ ] Cross-device synchronization testing
  - [ ] Battery usage optimization
  - [ ] Privacy compliance testing

- [ ] **Security Audit**
  - [ ] Mesh packet security review
  - [ ] Anonymous broadcasting verification
  - [ ] End-to-end encryption validation
  - [ ] GDPR compliance for mesh data
  - [ ] Community safety review

### Deployment
- [ ] Production-grade Cloud Run config
- [ ] Multi-region deployment for mesh redundancy
- [ ] Disaster recovery with mesh fallback
- [ ] Automated backups including mesh state
- [ ] Blue-green deployments for zero downtime

---

## Phase 4: Mesh-First FoundUp (FUTURE 🚀)

**Goal**: World's first decentralized mesh mutual-aid + share economy platform

### Revolutionary Features
- [ ] **Civic Mesh Network**
  - [ ] Disaster-resilient emergency alerts
  - [ ] Censorship-resistant communication
  - [ ] ISP-independent local economy
  - [ ] Trustless peer verification

- [ ] **Community Governance**
  - [ ] Mesh-based voting systems
  - [ ] Community moderation
  - [ ] Resource allocation algorithms
  - [ ] Impact measurement tools

- [ ] **Global Mesh Federation**
  - [ ] Inter-city mesh networks
  - [ ] Cross-border mutual aid
  - [ ] International emergency response
  - [ ] Global resource sharing

---

## Future Enhancements (Backlog)

### Advanced Features
- [ ] AR preview mode (place furniture in room)
- [ ] ML model fine-tuning on user data
- [ ] Voice commands
- [ ] OCR for text extraction
- [ ] Barcode/QR code scanning
- [ ] Integration with donation platforms

### Platform Expansion
- [ ] Native mobile apps (React Native)
- [ ] Browser extension
- [ ] Desktop app (Electron)
- [ ] API for third-party integrations
- [ ] Webhook support

### AI Enhancements
- [ ] Custom AI models per user
- [ ] Sentiment analysis
- [ ] Predictive organization
- [ ] Automated workflows
- [ ] Smart reminders

---

## WSP Compliance Roadmap

### PoC → Prototype
- [x] WSP 3: Domain organization
- [x] WSP 49: Module structure
- [x] WSP 22: Documentation
- [ ] WSP 5: Test coverage ≥90%
- [ ] WSP 6: Test audit reports

### Prototype → MVP
- [ ] WSP 11: Interface protocol
- [ ] WSP 71: Secrets management
- [ ] WSP 89: Production deployment
- [ ] WSP 60: Module memory
- [ ] WSP 91: Observability

### MVP → Production
- [ ] WSP 78: Database scaling
- [ ] WSP 68: Build scalability
- [ ] WSP 59: Distributed development
- [ ] WSP 42: Universal platform protocol

---

## Metrics & Success Criteria

### PoC Success (ACHIEVED ✅)
- ✅ App deployable to Cloud Run
- ✅ Core swipe interface functional
- ✅ Geo-filtering accurate
- ✅ PWA installable on mobile
- ✅ <2s page load time

### Prototype Success (In Progress)
- [x] All 16 classification types working (100% coverage)
- [x] Liberty Alert unlock persistent
- [x] Complete display pipeline (badges, map, filters)
- [ ] Scheduled events lifecycle (Phase 2 next up)
- [ ] Auto-delete expired alerts (Phase 2 next up)
- [ ] Test coverage >70%
- [ ] <1.5s page load time (currently 473 kB gzipped: 142 kB)
- [ ] 10+ beta users with positive feedback

### MVP Success (Planned)
- [ ] 100+ active users
- [ ] Cloud sync 99.9% uptime
- [ ] Test coverage >90%
- [ ] <1s page load time
- [ ] <1% error rate
- [ ] Positive revenue from premium tier

---

## 📊 Current Status (2025-11-16)

**Current Phase**: Phase 2 - UX Polish & Event Lifecycle 🚧

**What Just Shipped** (Phase 1 Complete):
- ✅ All 16 classification types working end-to-end
- ✅ Liberty Alert unlock (SOS morse code, persistent)
- ✅ Complete camera → classification → storage → display pipeline
- ✅ ClassificationBadge with all 16 types + emojis
- ✅ MapClusterMarker color-coded for all types
- ✅ Dynamic filters in My Items & Browse
- ✅ Time-based expiration (AlertTimer, StayLimit)
- ✅ Build: 473.48 kB (gzip: 142.18 kB)

**Next Up** (Phase 2 Resume):
1. Auto-delete expired alerts (background cleanup job)
2. Scheduled events UI (faded badges, date/time picker)
3. Event lifecycle (before/during/after states)
4. Global Liberty Alert map view (zoom to world map)

**0102 Next Task**: Resume Phase 2 - see Priority Features section above

**Vision Docs Ready for Phase 3+**:
- [GJ_00_Vision.md](docs/vision/GJ_00_Vision.md) - Read this first!
- [GJ_10](docs/vision/GJ_10_Chat_and_Message_System.md), [GJ_20](docs/vision/GJ_20_Security_and_Identity.md), [GJ_30](docs/vision/GJ_30_Media_YouTube_Integration.md), [GJ_40](docs/vision/GJ_40_Glob_and_Data_Model.md), [GJ_50](docs/vision/GJ_50_AI_Voice_Assistant.md) - Micro-sprints ready

**WSP Compliance**: Following WSP_00, WSP_3, WSP_49, WSP_22. All sprints designed as WSP-compliant prompts.

---

For detailed implementation, see [README.md](README.md) and [INTERFACE.md](INTERFACE.md).
