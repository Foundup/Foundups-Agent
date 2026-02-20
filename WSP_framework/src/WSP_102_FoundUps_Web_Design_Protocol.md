# WSP 102: FoundUps Web Design Protocol

**Version**: 1.0.0
**Status**: Active
**Created**: 2026-02-18
**Author**: 012 (canonical insight)

## 1. Purpose

Define standards for designing FoundUps web interfaces including landing pages, member areas, and authentication flows. Prioritizes user efficiency, mobile-first design, and regulatory compliance.

## 2. Click Economy (012 Principle)

> "You can rate a system by how many clicks it takes you to do something"

### 2.1 Grading Scale

| Grade | Clicks | Rating | Example |
|-------|--------|--------|---------|
| A | 1 | Excellent | Dashboard access when authenticated |
| B | 2 | Good | ENTER → Sign in → Member area |
| C | 3 | Acceptable | Requires justification |
| D/F | 4+ | Fail | Redesign required |

### 2.2 Target Grades by Action

| Action | Target | Max Clicks |
|--------|--------|------------|
| Sign up/Sign in | B | 2 |
| View dashboard | A | 1 |
| Launch FoundUP | B | 2 |
| Send invite | B | 2 |
| View wallet | B | 2 |

### 2.3 Implementation Pattern

Combine related actions into single screens:
- Disclaimer + Auth buttons on same modal
- Clicking sign-in = implicit confirmation of terms

## 3. Authentication Architecture

### 3.1 Dual-Layer Architecture

```
┌─────────────────────────────────────────────────────────┐
│  Auth Layer: CLERK                                       │
│  - OAuth providers (Google, LinkedIn, etc.)             │
│  - Session management                                    │
│  - User identity (clerk.user.id)                        │
│  - Why: Firebase OAuth was unreliable                   │
├─────────────────────────────────────────────────────────┤
│  Data Layer: FIREBASE FIRESTORE                          │
│  - User data (invites, UPS balance, etc.)               │
│  - FoundUp data                                          │
│  - Keyed by Clerk user ID                               │
│  - Why: Already deployed, reliable data storage         │
└─────────────────────────────────────────────────────────┘
```

### 3.2 The Curtain Pattern

Legal disclaimer (the "curtain") must appear BEFORE authentication:

```
Landing → ENTER → Disclaimer Modal (with embedded auth) → Sign in → Member Area
```

**Grade: B** (2 clicks to member area)

### 3.3 Embedded Auth Buttons

Auth buttons appear directly on disclaimer modal:
- "I Confirm — Sign in with Google"
- "I Confirm — Sign in with LinkedIn"
- Escape hatch: "I am an accredited investor"

Clicking sign-in button implicitly confirms:
- User is NOT accredited investor
- User is NOT company representative
- User agrees to Terms of Access and NDA

### 3.4 Auth Flow Implementation

```javascript
// Landing page: Clerk SDK loaded, disclaimer buttons trigger Clerk.openSignIn()
disclaimerSignInGoogle.addEventListener('click', async () => {
  await window.Clerk.openSignIn({
    afterSignInUrl: '/member/',
    afterSignUpUrl: '/member/'
  });
});

// Member page: Check Clerk auth, load Firestore data
const user = window.Clerk.user;
if (user) {
  await loadUserData(user.id, user);  // Firestore keyed by Clerk ID
} else {
  window.location.href = '/?signin=required';
}
```

### 3.5 Mobile Touch Targets

- Minimum button size: 44x44px (Apple HIG)
- Minimum spacing: 8px between targets
- Full-width buttons on mobile for easy thumb reach

## 4. Visual Design Standards

### 4.1 Color Palette

```css
--bg-primary: #08080f;      /* Dark background */
--accent: #7c5cfc;          /* Purple accent */
--accent-hover: #6b4ce0;    /* Purple hover */
--text-primary: #ffffff;    /* White text */
--text-dim: #9ca3af;        /* Gray text */
--border: rgba(255,255,255,0.1);
--card-bg: rgba(255,255,255,0.05);
```

### 4.2 Typography

- Font: Geist Sans (primary), Geist Mono (code)
- Headings: Bold, high contrast
- Body: Regular weight, sufficient line height

### 4.3 Components

**Stat Cards**: Icon + Value + Label + Action Button
```html
<div class="stat-card">
  <span class="icon">💰</span>
  <div class="content">
    <div class="value">--</div>
    <div class="label">UPS Balance</div>
  </div>
  <button class="action">Wallet</button>
</div>
```

**Action Buttons**: Full-width on mobile, icon + label
```html
<button class="action-button">
  <span class="icon">🚀</span>
  <span class="label">Launch a FoundUP</span>
</button>
```

## 5. Regulatory Compliance

### 5.1 Required Disclaimers

Every auth flow must verify:
- User is NOT accredited investor (SEC definition)
- User is NOT company representative
- User agrees to Terms of Access
- User agrees to NDA

### 5.2 Legal Links

Required links on disclaimer:
- Terms of Access: `/legal/terms-of-access.html`
- NDA: `/legal/alpha-nda.html`

Links must be visible, clickable, and open in new tab.

## 6. Responsive Design

### 6.1 Breakpoints

```css
/* Mobile first */
@media (min-width: 768px) { /* Tablet */ }
@media (min-width: 1024px) { /* Desktop */ }
```

### 6.2 Grid Patterns

- Stats: 1 column mobile → 4 columns desktop
- Content: 1 column mobile → 2 columns desktop
- Full-width cards on mobile

## 7. Gate Template Architecture

All FoundUps use the same entry gate pattern. This is a **reusable template**.

### 7.1 Template Components

| Component | Purpose | Customizable |
|-----------|---------|--------------|
| Landing page | Hero, value prop, ENTER | Branding, copy |
| Disclaimer modal | Legal curtain | Requirements, jurisdiction |
| OAuth buttons | Auth via Clerk | Providers enabled |
| Member dashboard | User area | Features, data displayed |
| Legal pages | ToA, NDA | Entity, jurisdiction |

### 7.2 Template Variables (config.json)

```json
{
  "foundupId": "foundups-alpha",
  "name": "FoundUPS",
  "tagline": "Peer-to-Peer Autonomous Venture System",
  "colors": {
    "accent": "#7c5cfc",
    "background": "#08080f"
  },
  "legal": {
    "jurisdiction": "Fukui District Court, Japan",
    "entity": "Foundups G.K."
  },
  "disclaimers": [
    "Are NOT accredited investors (SEC definition)",
    "Are NOT company representatives"
  ],
  "oauth": {
    "clerk_publishable_key": "pk_test_...",
    "providers": ["google", "linkedin"]
  },
  "features": ["invites", "wallet", "agents", "foundups"]
}
```

### 7.3 Folder Structure

```
foundups-gate-template/
├── index.html              # Landing (uses config.json)
├── member/
│   ├── index.html          # Dashboard
│   └── css/member.css      # Member styles
├── legal/
│   ├── terms-of-access.html
│   └── alpha-nda.html
├── css/
│   └── styles.css          # Shared styles
├── config.json             # FoundUp-specific config
└── assets/
    ├── logo.svg
    └── favicon.ico
```

### 7.4 Deployment

Each FoundUp deploys to:
- Firebase Hosting (static files)
- Uses shared Clerk application (or own Clerk instance)
- Own Firestore project (data isolation)

```bash
# Deploy a new FoundUp
cp -r foundups-gate-template/ my-foundup/
# Edit config.json with FoundUp specifics
firebase deploy --only hosting
```

## 8. Testing Checklist

- [ ] Click count audit (target Grade B or better)
- [ ] Mobile touch target verification (44px minimum)
- [ ] Disclaimer visible before auth
- [ ] Legal links functional
- [ ] Auth flow completes in 2 clicks
- [ ] Responsive on mobile/tablet/desktop

---

*WSP 102: Every click costs trust. Spend wisely.*
