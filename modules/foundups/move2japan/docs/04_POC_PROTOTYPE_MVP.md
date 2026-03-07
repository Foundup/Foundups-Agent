# Move2Japan FoundUp — POC → Prototype → MVP (012 Architecture Vision)

_Source: 012 voice-mode conversation, captured 2026-03-07_

## Big Vision

A full relocation operating system for moving to Japan.

---

## Proof of Concept

**Question**: Will people engage with a staged, agent-led "move to Japan" journey?

**Build**:

- `!move2japan` trigger in live chat
- Agent responds with one next question
- Ask passport status
- Provide immediate guidance
- Offer signup link
- Store minimal memory
- Allow stakeholder to return and resume

**Success signals**:

- Trigger usage
- Clickthrough to signup
- Returning stakeholders
- Stakeholders advancing from passport unknown → passport in progress

---

## Prototype

**Question**: Can the system persist journeys and guide stakeholders through multiple base camps?

**Build**:

- Stakeholder accounts
- Roadmap engine
- Stage gating
- Dashboard
- Basic checklist system
- Memory across sessions
- Handbook/content hub
- Updates/news engine
- First premium upsell
- First job/location guidance flows

**Success signals**:

- Stage progression
- Dashboard engagement
- Email capture
- Repeat visits
- Premium interest

---

## MVP

**Question**: Will stakeholders pay for active execution help?

**Build**:

- Personal assistant tier
- Job guidance agent
- Location-fit agent
- Housing assist workflows
- Broker handoff
- Revenue tracking
- Human escalation
- Document/form support

**Success signals**:

- Paid conversions
- Completion to "ready to move"
- Successful partner handoffs
- Relocation outcomes
- Referral revenue

---

## Post-MVP Expansion

- City-specific onboarding
- Arrival concierge
- Tax/admin setup
- Language ramp plans
- Spouse/family flows
- School/kids flows
- Remote worker flow
- Entrepreneur visa flow
- Retirement flow
- Property purchase flow
- Settlement retention products

---

## Recommended Build Order

1. **Trigger handler** — `!move2japan` in live chat (BC0 skill)
2. **Memory schema** — Minimal stakeholder profile
3. **Stage engine** — Base camp state machine
4. **Minimal signup handoff** — movetojapan.info newsletter capture
5. **Passport-first journey** — BC0 → BC1 progression

> This gives a real POC while preserving the architecture for the full FoundUp. Without rewriting everything.
