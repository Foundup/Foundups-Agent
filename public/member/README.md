# FoundUPS Member Area

**Status**: Layer 1 (Shell) Complete
**Location**: `public/member/`
**WSP Compliance**: WSP 49 (Structure), WSP 72 (Independence)

## Overview

The FoundUPS Member Area is the authenticated dashboard where users manage their:
- UPS token balance and staking
- FoundUp ventures (create, manage, contribute)
- OpenClaw agents (deploy, monitor, earn)
- Invite codes and referrals
- Account settings

## Architecture

The member area follows **Occam's Layered Architecture** — each section is an independent module that can be built/tested separately.

```
public/member/
├── index.html          # Shell + routing + auth state
├── css/
│   └── member.css      # Shared styles (dark theme, glassmorphism)
├── js/
│   ├── dashboard.js    # (Layer 2 - pending)
│   ├── wallet.js       # (Layer 3 - pending)
│   ├── foundups.js     # (Layer 4 - pending)
│   ├── agents.js       # (Layer 5 - pending)
│   └── marketplace.js  # (Layer 6 - pending)
└── README.md           # This file
```

## Layer Roadmap

| Layer | Module | Status | Description |
|-------|--------|--------|-------------|
| 1 | Shell | **Complete** | Auth state, navigation, routing |
| 2 | Dashboard | Placeholder | Overview, stats, activity feed |
| 3 | Wallet | Placeholder | UPS balance, staking, transactions |
| 4 | FoundUps | Placeholder | Create/manage/contribute |
| 5 | Agents | Placeholder | Deploy/monitor OpenClaw agents |
| 6 | Marketplace | Placeholder | Browse/join FoundUps |

## Dependencies

- **Firebase Auth** - User authentication
- **Firestore** - User data, FoundUps, transactions
- **Landing page** (`public/index.html`) - Signup flow

## Entry Points

1. **Direct Access**: `/member/` - Redirects to landing if not authenticated
2. **Post-Signup**: Landing page redirects here after successful signup
3. **Deep Links**: `/member/#wallet`, `/member/#foundups`, etc.

## Design Principles

1. **No God Modules** - Each section is independent
2. **Occam's Layered** - Build/test one layer at a time
3. **WSP 72 Compliance** - No cross-module dependencies
4. **Same Design Language** - Matches landing page (dark theme, glassmorphism)

## Firebase Collections

| Collection | Purpose |
|------------|---------|
| `users` | User profiles, inviteCodes, settings |
| `foundups` | FoundUp ventures |
| `transactions` | UPS/F_i transactions |
| `agents` | OpenClaw agent deployments |

## Next Steps

1. **Layer 2**: Implement dashboard with real data
2. **Layer 3**: Wallet module with UPS display
3. **Layer 4**: FoundUps CRUD operations
4. **Layer 5**: Agent deployment interface
5. **Layer 6**: Marketplace discovery

---

*Created 2026-02-18 | WSP 49 Compliant*
