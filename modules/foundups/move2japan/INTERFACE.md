# Move2Japan FoundUp — INTERFACE.md (WSP 11 Contract Memory)

## Core Modules

### A. Intent Capture Module

- **Inputs**: Live chat trigger (`!move2japan`), site CTA, lead forms, newsletter signup
- **Outputs**: Stakeholder record, source attribution, initial stage = Intent

### B. Stakeholder Memory Module

- **Purpose**: Cross-channel identity resolution, resumable conversations, agent-readable summaries
- **Stores**: Chat identity, email, progress stage, key answers, preferences, urgency, premium status

### C. Roadmap Engine

- **Purpose**: Stage-gated progression with unlock logic
- **Controls**: Base camp progression, checklist state, prerequisite gates, unlock conditions, reminders

### D. Conversation Orchestrator

- **Purpose**: Determines next question, routing (chat vs site), signup timing, upsell timing, human escalation

### E. Knowledge Engine

- **Purpose**: Structured content for visa, passport, jobs, housing, city selection, documents, policy updates
- **Requirements**: Freshness review, source traceability, admin update workflow

### F. Dream Life Discovery Module

- **Purpose**: Translate abstract desire into concrete relocation path
- **Outputs**: Recommended regions, migration path, job/housing strategy

### G. Job Pathway Module

- **Purpose**: Income viability — education, language, industry, remote compatibility, sponsorship likelihood

### H. Housing Module

- **Purpose**: First landing housing → ideal housing → search aggregation → partner referrals

### I. Form/Document Automation Module (Premium)

- **Purpose**: Prefill applications, translate fields, generate checklists, draft Japanese emails

### J. News & Policy Update Module

- **Purpose**: Internal Substack — visa changes, policy shifts, work trends, housing news

### K. Monetization Module

- **Supports**: Free, premium, concierge, referral revenue, brokerage commission, partner commissions

### L. Analytics Module

- **Measures**: Trigger volume, signup conversion, stage completion, drop-off, premium conversion, time-to-progress

---

## State Model

Canonical stakeholder states (ordered progression):

```
Intent → Passport → Pathway Discovery → Income Plan → Visa Plan
  → Location Plan → Housing Plan → Document Prep → Ready to Move
  → In Japan → Settling In
```

---

## Stakeholder Profile Schema

| Field               | Type    | Description                                                  |
| ------------------- | ------- | ------------------------------------------------------------ |
| `stakeholder_id`    | string  | Unique identifier                                            |
| `source_channel`    | enum    | youtube_chat, web, email, referral                           |
| `chat_handle`       | string  | YouTube/platform handle                                      |
| `email`             | string  | Contact email                                                |
| `current_stage`     | enum    | State model value                                            |
| `passport_status`   | enum    | yes, no, expired, in_progress, unknown                       |
| `move_timeline`     | enum    | exploring, 12_24_months, 12_months, 6_months, asap           |
| `urgency_level`     | enum    | explorer, planner, serious, imminent, urgent                 |
| `move_reason`       | string  | work, student, spouse, entrepreneur, remote, retiree, escape |
| `employment_status` | string  | Current employment situation                                 |
| `language_level`    | string  | Japanese proficiency                                         |
| `target_region`     | string  | Preferred region in Japan                                    |
| `premium_interest`  | boolean | Has expressed premium interest                               |
| `notes_summary`     | text    | Agent-generated summary                                      |

---

## Gating Logic

| Condition                  | System Behavior                                      |
| -------------------------- | ---------------------------------------------------- |
| No passport                | Emphasize passport workflow, defer downstream stages |
| No income plan             | Do not over-focus on housing purchase                |
| No timeline                | Prioritize readiness clarification                   |
| High urgency               | Switch to fast-track guidance                        |
| High intent + high ability | Offer personal assistant tier                        |

---

## Base Camp 0 Routing Matrix

| Timeframe | Passport | Route                                   |
| --------- | -------- | --------------------------------------- |
| exploring | no       | passport-first + newsletter             |
| exploring | yes      | route to discovery later                |
| 1–2 years | no       | passport-first + low-pressure nurture   |
| 1–2 years | yes      | pathway discovery queue                 |
| 12 months | no       | passport-first + stronger CTA           |
| 12 months | yes      | next skill                              |
| 6 months  | no       | passport-first urgent tone              |
| 6 months  | yes      | fast-track next skill                   |
| ASAP      | no       | urgent passport-first + reality framing |
| ASAP      | yes      | fast-track next skill + PWA CTA         |

---

## Skill Handoff Model

| Skill                      | ID  | Responsibility                  |
| -------------------------- | --- | ------------------------------- |
| BC0_IntentAndPassportSkill | 0   | Triage, urgency, passport gate  |
| BC1_PassportSkill          | 1   | Passport acquisition guidance   |
| BC2_PathwayDiscoverySkill  | 2   | Migration pathway determination |
| BC3_WorkIncomeSkill        | 3   | Economic viability assessment   |
| BC4_VisaPlanningSkill      | 4   | Visa pathway selection          |
| BC5_LocationFitSkill       | 5   | Location matching               |
| BC6_HousingSkill           | 6   | Housing pathway                 |
| BC7_DocumentExecutionSkill | 7   | Paperwork and forms             |
