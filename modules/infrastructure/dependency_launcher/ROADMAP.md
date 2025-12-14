# Dependency Launcher Module - ROADMAP

**Module:** infrastructure/dependency_launcher
**WSP Reference:** WSP 22 (Module Roadmap Protocol)

---

## Vision Statement

Provide zero-friction startup for YouTube DAE by automatically launching all required dependencies (Chrome, LM Studio) when the DAE starts.

---

## LLME Progression

| Level | Status | Description |
|-------|--------|-------------|
| A1 | ✅ | Chrome auto-launch with debug port |
| A2 | ✅ | LM Studio auto-launch (optional) |
| A3 | ✅ | Integration with auto_moderator_dae.py |
| **A4** | 🚧 | Health monitoring and auto-restart |
| A5 | 🔮 | Multi-dependency orchestration |

---

## Phase 1: Core Dependency Launch ✅ COMPLETE

**Objective:** Auto-launch Chrome and LM Studio

- [x] `launch_chrome()` - Debug port 9222, YouTube profile
- [x] `launch_lm_studio()` - Port 1234 for UI-TARS
- [x] Port availability checks
- [x] Timeout handling (30s Chrome, 120s LM Studio)

---

## Phase 2: DAE Integration ✅ COMPLETE

**Objective:** Integrate into YouTube DAE startup

- [x] Phase -2 in `auto_moderator_dae.py`
- [x] Graceful degradation if Chrome unavailable
- [x] Optional LM Studio (falls back to DOM-only)
- [x] NAVIGATION.py entries for HoloIndex

---

## Phase 3: Health Monitoring 📋 PLANNED

**Objective:** Monitor and auto-restart crashed dependencies

### 3.1 Health Checks
- [ ] Periodic Chrome port check
- [ ] LM Studio API health endpoint
- [ ] Selenium connection validation

### 3.2 Auto-Recovery
- [ ] Detect Chrome crash → restart
- [ ] Detect LM Studio timeout → restart
- [ ] Notification to DAE on recovery

---

## Phase 4: Multi-Dependency Orchestration 🔮 FUTURE

**Objective:** Support additional DAE dependencies

- [ ] Database connections
- [ ] API service health
- [ ] External tool integration
- [ ] Dependency graph management

---

## 0102 Directive

Dependencies are orchestrated, not installed. The system self-heals. ✊✋🖐️




