# Golden Ticket Invite System - Technical Framework

**Status**: Planned (Phase 3: MVP)  
**WSP Compliance**: WSP 3, WSP 11, WSP 49, WSP 83, WSP 89  
**Universal**: All FoundUps will launch with this system  
**Purpose**: PWA-based geo-anchored invite system for exclusive, viral launch mechanics

## Overview

The Golden Ticket Invite System implements a geo-anchored, time-sensitive QR code invitation mechanism that creates scarcity and exclusivity through in-person sharing. This system leverages PWA capabilities to create a seamless, app-like experience that feels like a high-tech treasure hunt.

**Core Concept**: Each user receives a limited number of "golden tickets" (invite tokens) that can be shared via geo-anchored QR codes. Recipients must be physically present at the QR code generation location to redeem the invite, creating authentic, in-person connections.

## Architecture

### 1. Backend System Requirements

#### 1.1 User Profile & Token Management

**Database Schema** (Firestore/PostgreSQL):
```typescript
interface UserProfile {
  userId: string;                    // Unique user identifier
  inviteTokens: number;              // Current available invites (starts at 1)
  totalInvitesGranted: number;       // Lifetime invites granted
  invitesShared: number;             // Number of invites successfully redeemed
  createdAt: number;                  // Account creation timestamp
  inviteHistory: InviteRecord[];     // Track who invited whom
}

interface InviteRecord {
  inviteId: string;                  // Unique invite code/token
  generatedAt: number;               // Timestamp when QR code was created
  generatedLocation: GeoPoint;        // GPS coordinates where QR was generated
  redeemedAt?: number;               // Timestamp when redeemed (null if unused)
  redeemedBy?: string;               // UserId of recipient (null if unused)
  redeemedLocation?: GeoPoint;        // GPS coordinates where redeemed
  expiresAt: number;                  // Expiration timestamp (5 minutes from generation)
  status: 'active' | 'redeemed' | 'expired';
}
```

**Token Lifecycle**:
1. **Initial Grant**: New user receives 1 invite token (golden ticket)
2. **Successful Share**: When invite is redeemed, sharer receives +1 bonus token (viral reward)
3. **Maximum Cap**: Optional cap (e.g., 10 tokens max) to prevent abuse
4. **Token Expiration**: QR codes expire after 5 minutes (time-sensitive)

#### 1.2 Invite Code Generation

**Algorithm**:
```typescript
interface InviteCode {
  code: string;                       // Unique alphanumeric code (e.g., "GT-ABC123XYZ")
  qrData: string;                    // Full URL: `https://gotjunk.app/invite/GT-ABC123XYZ`
  geoAnchor: GeoPoint;                // Generation location (lat, lng)
  validRadius: number;                // 50 meters (configurable)
  expiresAt: number;                  // 5 minutes from generation
  generatedBy: string;                // UserId of sharer
}

function generateInviteCode(userId: string, location: GeoPoint): InviteCode {
  const code = `GT-${generateUniqueCode()}`; // Base64 or UUID-based
  const qrData = `${APP_URL}/invite/${code}`;
  const expiresAt = Date.now() + (5 * 60 * 1000); // 5 minutes
  
  return {
    code,
    qrData,
    geoAnchor: location,
    validRadius: 50, // meters
    expiresAt,
    generatedBy: userId
  };
}
```

**Security Considerations**:
- Codes must be cryptographically random (use crypto.randomUUID or similar)
- Rate limiting: Max 1 QR code per user per 30 seconds
- Server-side validation of all redemption attempts
- Audit logging for fraud detection

### 2. PWA Implementation

#### 2.1 Geo-Location Access

**Geolocation API Integration**:
```typescript
interface LocationService {
  getCurrentPosition(): Promise<GeoPoint>;
  watchPosition(callback: (location: GeoPoint) => void): number;
  clearWatch(watchId: number): void;
}

class PwaLocationService implements LocationService {
  async getCurrentPosition(): Promise<GeoPoint> {
    return new Promise((resolve, reject) => {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          resolve({
            latitude: position.coords.latitude,
            longitude: position.coords.longitude,
            accuracy: position.coords.accuracy,
            timestamp: position.timestamp
          });
        },
        (error) => reject(error),
        {
          enableHighAccuracy: true,
          timeout: 10000,
          maximumAge: 0 // Always get fresh location
        }
      );
    });
  }
}
```

**Permission Handling**:
- Request location permission on first QR generation attempt
- Show clear explanation: "We need your location to create geo-anchored invites"
- Fallback: If permission denied, show error with instructions

#### 2.2 Dynamic QR Code Generation

**QR Code Library** (qrcode.js or similar):
```typescript
import QRCode from 'qrcode';

interface QRCodeGenerator {
  generateQRCode(data: string): Promise<string>; // Returns data URL
  generateQRCodeBlob(data: string): Promise<Blob>; // Returns blob for download
}

class PwaQRCodeGenerator implements QRCodeGenerator {
  async generateQRCode(inviteCode: string): Promise<string> {
    const qrDataUrl = await QRCode.toDataURL(inviteCode, {
      width: 400,
      margin: 2,
      color: {
        dark: '#000000',
        light: '#FFFFFF'
      }
    });
    return qrDataUrl;
  }
}
```

**UI Component**:
```typescript
interface InviteQRPanelProps {
  inviteCode: InviteCode;
  onClose: () => void;
}

const InviteQRPanel: React.FC<InviteQRPanelProps> = ({ inviteCode, onClose }) => {
  const [qrDataUrl, setQrDataUrl] = useState<string>('');
  const [timeRemaining, setTimeRemaining] = useState<number>(300); // 5 minutes

  useEffect(() => {
    // Generate QR code
    QRCode.toDataURL(inviteCode.qrData).then(setQrDataUrl);
    
    // Countdown timer
    const interval = setInterval(() => {
      const remaining = Math.max(0, Math.floor((inviteCode.expiresAt - Date.now()) / 1000));
      setTimeRemaining(remaining);
      if (remaining === 0) {
        onClose(); // Auto-close when expired
      }
    }, 1000);

    return () => clearInterval(interval);
  }, [inviteCode]);

  return (
    <div className="invite-qr-panel">
      <h2>Share Your Golden Ticket</h2>
      <p>Valid for {timeRemaining}s • Within 50m of this location</p>
      <img src={qrDataUrl} alt="Invite QR Code" />
      <button onClick={onClose}>Close</button>
    </div>
  );
};
```

#### 2.3 QR Code Redemption Flow

**Recipient Experience**:
```typescript
interface InviteRedemptionService {
  scanQRCode(qrData: string): Promise<void>;
  validateInvite(code: string, location: GeoPoint): Promise<ValidationResult>;
  redeemInvite(code: string, userId: string): Promise<void>;
}

interface ValidationResult {
  valid: boolean;
  reason?: 'expired' | 'wrong_location' | 'already_redeemed' | 'invalid_code';
  distance?: number; // Meters from anchor point
}

class PwaInviteRedemptionService implements InviteRedemptionService {
  async validateInvite(code: string, location: GeoPoint): Promise<ValidationResult> {
    // Fetch invite record from backend
    const invite = await fetchInviteRecord(code);
    
    if (!invite) {
      return { valid: false, reason: 'invalid_code' };
    }
    
    if (invite.status === 'redeemed') {
      return { valid: false, reason: 'already_redeemed' };
    }
    
    if (Date.now() > invite.expiresAt) {
      return { valid: false, reason: 'expired' };
    }
    
    // Calculate distance from anchor point
    const distance = haversineDistance(
      location,
      invite.geoAnchor
    );
    
    if (distance > invite.validRadius) {
      return { valid: false, reason: 'wrong_location', distance };
    }
    
    return { valid: true, distance };
  }
  
  async redeemInvite(code: string, userId: string): Promise<void> {
    const location = await locationService.getCurrentPosition();
    const validation = await this.validateInvite(code, location);
    
    if (!validation.valid) {
      throw new Error(`Invite invalid: ${validation.reason}`);
    }
    
    // Backend API call to redeem
    await fetch('/api/invites/redeem', {
      method: 'POST',
      body: JSON.stringify({ code, userId, location })
    });
    
    // Grant new user access
    // Award bonus token to sharer (via push notification)
  }
}
```

**QR Code Scanning** (Camera API):
```typescript
// Use device camera to scan QR code
const scanQRCode = async (): Promise<string> => {
  const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' } });
  const video = document.createElement('video');
  video.srcObject = stream;
  video.play();
  
  // Use jsQR or similar library to detect QR code
  const qrCode = await detectQRCode(video);
  
  stream.getTracks().forEach(track => track.stop());
  return qrCode.data;
};
```

### 3. PWA Enhancements

#### 3.1 Offline Functionality (Service Worker)

**Caching Strategy**:
```typescript
// service-worker.js
const CACHE_NAME = 'gotjunk-invite-v1';
const INVITE_CACHE = 'invite-codes-v1';

// Cache QR generation logic
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll([
        '/invite-generator.js',
        '/qr-code-generator.js',
        '/location-service.js'
      ]);
    })
  );
});

// Offline QR generation
self.addEventListener('fetch', (event) => {
  if (event.request.url.includes('/api/invites/generate')) {
    event.respondWith(
      // Generate QR code offline, sync when online
      generateOfflineInvite(event.request).then((response) => {
        // Queue for sync when online
        queueForSync(event.request, response);
        return response;
      })
    );
  }
});
```

**Background Sync**:
```typescript
// Queue invite generation for sync when online
async function queueForSync(request: Request, response: Response) {
  const db = await openDB('invite-sync-queue');
  await db.add('pending-invites', {
    request: await request.clone().json(),
    response: await response.clone().json(),
    timestamp: Date.now()
  });
  
  // Register background sync
  if ('serviceWorker' in navigator && 'sync' in (self as any).registration) {
    await (self as any).registration.sync.register('sync-invites');
  }
}
```

#### 3.2 Add to Home Screen (Install Prompt)

**Web App Manifest**:
```json
{
  "name": "GotJunk? FoundUp",
  "short_name": "GotJunk",
  "description": "Golden Ticket Invite System",
  "start_url": "/invite",
  "display": "standalone",
  "background_color": "#000000",
  "theme_color": "#FFD700",
  "icons": [
    {
      "src": "/icon-192.png",
      "sizes": "192x192",
      "type": "image/png"
    },
    {
      "src": "/icon-512.png",
      "sizes": "512x512",
      "type": "image/png"
    }
  ],
  "share_target": {
    "action": "/invite/share",
    "method": "GET",
    "params": {
      "title": "title",
      "text": "text",
      "url": "url"
    }
  }
}
```

**Install Prompt**:
```typescript
let deferredPrompt: BeforeInstallPromptEvent | null = null;

window.addEventListener('beforeinstallprompt', (e) => {
  e.preventDefault();
  deferredPrompt = e;
  showInstallButton();
});

const handleInstallClick = async () => {
  if (!deferredPrompt) return;
  
  deferredPrompt.prompt();
  const { outcome } = await deferredPrompt.userChoice;
  
  if (outcome === 'accepted') {
    console.log('User installed PWA');
    // Track installation event
    analytics.track('pwa_installed');
  }
  
  deferredPrompt = null;
};
```

#### 3.3 Push Notifications (Viral Rewards)

**Service Worker Push Handler**:
```typescript
// service-worker.js
self.addEventListener('push', (event) => {
  const data = event.data?.json();
  
  if (data.type === 'invite_redeemed') {
    const options = {
      body: `🎉 ${data.recipientName} just joined via your QR code! You earned +1 invite token.`,
      icon: '/icon-192.png',
      badge: '/badge-72.png',
      tag: 'invite-redeemed',
      data: {
        url: '/invite?token=+1'
      },
      actions: [
        {
          action: 'view',
          title: 'View Invites'
        },
        {
          action: 'dismiss',
          title: 'Dismiss'
        }
      ]
    };
    
    event.waitUntil(
      self.registration.showNotification('Golden Ticket Redeemed!', options)
    );
  }
});

self.addEventListener('notificationclick', (event) => {
  event.notification.close();
  
  if (event.action === 'view') {
    event.waitUntil(
      clients.openWindow(event.notification.data.url)
    );
  }
});
```

**Backend Push Notification**:
```typescript
// When invite is redeemed
async function onInviteRedeemed(inviteCode: string, recipientId: string) {
  const invite = await getInviteRecord(inviteCode);
  const sharer = await getUserProfile(invite.generatedBy);
  
  // Award bonus token
  await updateUserProfile(invite.generatedBy, {
    inviteTokens: sharer.inviteTokens + 1,
    invitesShared: sharer.invitesShared + 1
  });
  
  // Send push notification
  await sendPushNotification(sharer.pushSubscription, {
    type: 'invite_redeemed',
    recipientName: await getUserDisplayName(recipientId),
    bonusTokens: 1
  });
}
```

### 4. Future Enhancements

#### 4.1 Augmented Reality (AR) Layer

**WebXR Integration** (Future):
```typescript
interface ARInviteSystem {
  detectARSupport(): boolean;
  launchARInvite(): Promise<void>;
  catchFloatingToken(): Promise<InviteToken>;
}

class WebXRInviteSystem implements ARInviteSystem {
  async launchARInvite(): Promise<void> {
    const session = await navigator.xr?.requestSession('immersive-ar');
    // Render floating golden ticket token in AR space
    // User must "catch" token with camera before sharing
  }
}
```

**AR Token Rendering**:
- Use WebXR API to render 3D golden ticket in AR space
- User must physically move phone to "catch" token
- Adds gamification and exclusivity
- Requires WebXR-capable device (future enhancement)

### 5. Technical Framework (Universal for All FoundUps)

#### 5.1 Shared Components

**Invite System Module** (`modules/infrastructure/invite_system/`):
```
modules/infrastructure/invite_system/
├── README.md
├── INTERFACE.md
├── ROADMAP.md
├── ModLog.md
├── src/
│   ├── inviteStore.ts          # Token management
│   ├── qrGenerator.ts          # QR code generation
│   ├── locationService.ts      # Geolocation handling
│   ├── redemptionService.ts    # Invite validation/redeem
│   └── pushNotificationService.ts
├── tests/
│   └── README.md
└── memory/
    └── README.md
```

**Shared Interfaces**:
```typescript
// Universal invite system interface
export interface InviteSystem {
  generateInvite(userId: string, location: GeoPoint): Promise<InviteCode>;
  validateInvite(code: string, location: GeoPoint): Promise<ValidationResult>;
  redeemInvite(code: string, userId: string): Promise<void>;
  getUserInviteTokens(userId: string): Promise<number>;
  getInviteHistory(userId: string): Promise<InviteRecord[]>;
}

// Each FoundUp implements this interface
export class GotJunkInviteSystem implements InviteSystem {
  // GotJunk-specific implementation
}
```

#### 5.2 Configuration

**Environment Variables**:
```typescript
interface InviteSystemConfig {
  APP_URL: string;                    // Base URL for invite links
  QR_VALIDITY_MINUTES: number;        // Default: 5
  GEO_RADIUS_METERS: number;          // Default: 50
  INITIAL_TOKENS: number;             // Default: 1
  BONUS_TOKENS_PER_REDEEM: number;    // Default: 1
  MAX_TOKENS: number;                 // Default: 10 (optional cap)
  PUSH_NOTIFICATIONS_ENABLED: boolean; // Default: true
}
```

### 6. Security & Fraud Prevention

#### 6.1 Validation Rules

1. **Time Validation**: Server-side timestamp check (prevent clock manipulation)
2. **Location Validation**: Haversine distance calculation (prevent GPS spoofing)
3. **Rate Limiting**: Max 1 QR generation per 30 seconds per user
4. **Code Uniqueness**: Cryptographically secure random code generation
5. **Audit Logging**: All invite operations logged for fraud detection

#### 6.2 Anti-Abuse Measures

- **IP-based rate limiting**: Prevent automated redemption
- **Device fingerprinting**: Track suspicious patterns
- **Geographic anomaly detection**: Flag impossible location jumps
- **Token cap enforcement**: Prevent unlimited token accumulation

### 7. Analytics & Metrics

**Key Metrics**:
- Invite generation rate
- Redemption rate (successful vs expired)
- Average distance between generation and redemption
- Viral coefficient (invites shared per user)
- PWA installation rate
- Push notification engagement

### 8. WSP Compliance

**WSP Protocols Applied**:
- **WSP 3**: Enterprise domain organization (infrastructure/invite_system)
- **WSP 11**: Interface protocol (shared InviteSystem interface)
- **WSP 49**: Module structure (README, INTERFACE, ModLog, tests)
- **WSP 83**: Documentation tree attachment (this doc referenced in ROADMAP)
- **WSP 89**: Production deployment (PWA deployment strategy)

### 9. Implementation Phases

**Phase 1: Core System** (MVP)
- [ ] Backend invite token management
- [ ] QR code generation (geo-anchored)
- [ ] QR code redemption (location validation)
- [ ] Basic PWA manifest

**Phase 2: PWA Enhancements**
- [ ] Service worker offline support
- [ ] Install prompt integration
- [ ] Push notifications for viral rewards
- [ ] Background sync for offline invites

**Phase 3: Advanced Features**
- [ ] AR token catching (WebXR)
- [ ] Advanced analytics dashboard
- [ ] Fraud detection system
- [ ] Multi-FoundUp shared module

### 10. References

- **ROADMAP.md**: Phase 3 MVP feature
- **INTERFACE.md**: API specifications
- **ModLog.md**: Implementation tracking
- **WSP 83**: Documentation tree attachment
- **WSP 89**: Production deployment protocol

---

**Status**: Technical framework complete. Ready for implementation in Phase 3 MVP.  
**Universal**: This system will be implemented across all FoundUps for consistent launch mechanics.

