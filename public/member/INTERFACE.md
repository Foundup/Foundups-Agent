# Member Area Interface

**Module**: `public/member/`
**Version**: 1.0.0 (Layer 1 - Shell)

## Public Interface

### Entry URL
```
/member/
```

### Auth Requirements
- Firebase Auth user session required
- Redirects to `/?signin=required` if not authenticated

### Navigation Sections

| Hash | Section | Status |
|------|---------|--------|
| `#dashboard` | Overview dashboard | Shell |
| `#wallet` | UPS/F_i wallet | Placeholder |
| `#foundups` | FoundUp management | Placeholder |
| `#marketplace` | FoundUp discovery | Placeholder |
| `#agents` | OpenClaw agents | Placeholder |
| `#profile` | Account settings | Shell |

### JavaScript API

```javascript
// Navigation (internal)
window.location.hash = '#wallet';

// Copy invite code
window.copyCode(code: string): Promise<void>
```

### Firebase Integration

**Auth State Listener**:
```javascript
onAuthStateChanged(auth, (user) => {
  if (user) {
    // Show member area
    // Load user data from Firestore
  } else {
    // Redirect to landing
  }
});
```

**User Document Schema**:
```typescript
interface UserDoc {
  displayName: string;
  email: string;
  username: string;
  inviteCodes: string[];
  createdAt: Timestamp;
  updatedAt: Timestamp;
  // Future: upsBalance, foundups[], agents[]
}
```

### CSS Variables

The member area uses the same design tokens as the landing page:

```css
--bg: #08080f;
--bg-card: rgba(14, 14, 28, 0.8);
--accent: #7c5cfc;
--cyan: #00e5d0;
--gold: #f5a623;
--pink: #ff4ea0;
--red: #ff2d2d;
```

## Internal Interfaces (Future Modules)

### Dashboard Module (Layer 2)
```javascript
// dashboard.js
export async function loadDashboard(uid: string): Promise<void>
export async function loadActivityFeed(uid: string): Promise<Activity[]>
```

### Wallet Module (Layer 3)
```javascript
// wallet.js
export async function getUPSBalance(uid: string): Promise<number>
export async function getStakedPositions(uid: string): Promise<StakePosition[]>
export async function getTransactionHistory(uid: string): Promise<Transaction[]>
```

### FoundUps Module (Layer 4)
```javascript
// foundups.js
export async function createFoundUp(data: FoundUpInput): Promise<FoundUp>
export async function getMyFoundUps(uid: string): Promise<FoundUp[]>
export async function contributeToFoundUp(foundupId: string, amount: number): Promise<void>
```

### Agents Module (Layer 5)
```javascript
// agents.js
export async function deployAgent(config: AgentConfig): Promise<Agent>
export async function getMyAgents(uid: string): Promise<Agent[]>
export async function getAgentEarnings(agentId: string): Promise<Earnings>
```

### Marketplace Module (Layer 6)
```javascript
// marketplace.js
export async function browseFoundUps(filters: SearchFilters): Promise<FoundUp[]>
export async function joinFoundUp(foundupId: string): Promise<void>
export async function stakeInFoundUp(foundupId: string, amount: number): Promise<void>
```

---

*WSP 11 Compliant | Last Updated: 2026-02-18*
