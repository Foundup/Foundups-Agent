# Move2Japan FoundUp — Funnel Architecture (012 Architecture Vision)

_Source: 012 voice-mode conversation, captured 2026-03-07_

## Dual-Surface Funnel Architecture

The system uses two different domains for two different purposes.

---

### movetojapan.info — Public Funnel

**Purpose**: Low-friction entry + marketing surface

**Functions**:

- Newsletter signup
- Relocation updates
- Policy alerts
- Educational articles
- Landing page for chat referrals
- Lead capture

**Tone**: Low commitment.

**Example chat line**:

> If you'd like updates and relocation tips, you can join the Move2Japan newsletter here: **movetojapan.info**

---

### movetojapan.foundups.com — Stakeholder PWA

**Purpose**: Stakeholder operating system

**Functions**:

- Account system
- Roadmap dashboard
- Base camp progression
- Checklists
- Agent memory
- Job/location discovery
- Premium tiers
- Personal relocation assistant
- Housing integrations
- Partner referrals

**Type**: Progressive Web App (PWA)

**Gating**: Part of `foundups.com` architecture. WSP membership gated via `foundups.com`. Participants need an **invite key** obtainable through the livechat framework.

---

## Funnel Progression

```
YouTube Chat
    ↓
Base Camp 0 (intent + urgency + passport)
    ↓
Newsletter capture (optional) — movetojapan.info
    ↓
Stakeholder signup — movetojapan.foundups.com
    ↓
Roadmap progression
    ↓
Premium tiers
    ↓
Relocation execution
```

---

## Chat Soft-Sell Script

```
If you'd like me to keep track of your move plan,
you can create a roadmap account here:
movetojapan.foundups.com

Or if you just want updates and relocation news,
join the newsletter here:
movetojapan.info
```

---

## Why Two Surfaces

This separation prevents friction.

| Domain                   | Role                                 |
| ------------------------ | ------------------------------------ |
| movetojapan.info         | Marketing + newsletter (low barrier) |
| movetojapan.foundups.com | Product platform (deeper commitment) |

**Benefits**:

- Lower signup resistance
- Higher email capture
- Cleaner PWA architecture
- Scalable marketing surface
- Invite key gating through foundups.com framework
