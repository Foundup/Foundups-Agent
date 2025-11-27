
// Item ownership: who owns this item?
export type ItemOwnership = 'mine' | 'others';

// ============================================================================
// MEMBER CATEGORY SYSTEM - Moderation Roles
// ============================================================================
export type MemberCategory = 'regular' | 'trusted';

// Moderation permissions by member category:
// - regular: Can moderate GotJunk items (5 vote threshold)
// - trusted: Can moderate Liberty Alert items (10 vote threshold)

// ============================================================================
// CLASSIFICATION SYSTEM - 16 Types Across 4 Pillars
// ============================================================================
// Commerce: 3 types
// Share Economy: 2 types
// Mutual Aid: 9 types (5 food + 3 shelter + 1 deprecated)
// Alerts: 2 types

// Commerce (3 types) - Selling items for money or giving away
export type CommerceClassification = 'free' | 'discount' | 'bid';

// Share Economy (2 types) - Lending/borrowing tools and items
export type ShareClassification = 'share' | 'wanted';

// Mutual Aid (9 types) - Emergency community support (Maslow's hierarchy)
// Food subcategories (5): soup_kitchen, bbq, dry_food, pick, garden
// Shelter subcategories (3): couch, camping, housing
// Note: 'food' is deprecated - use specific subcategories
export type MutualAidClassification =
  | 'food' // @deprecated Use specific food subcategories
  | 'soup_kitchen'
  | 'bbq'
  | 'dry_food'
  | 'pick'
  | 'garden'
  | 'couch'
  | 'camping'
  | 'housing';

// Alerts (2 types) - Time-sensitive emergency alerts with countdown timers
export type AlertClassification = 'ice' | 'police';

// Combined classification (16 total types)
export type ItemClassification =
  | CommerceClassification
  | ShareClassification
  | MutualAidClassification
  | AlertClassification;

// Item status for MY items
export type MyItemStatus = 'draft' | 'listed' | 'sold' | 'auction';

// Item status when browsing OTHER people's items
export type BrowseStatus = 'browsing' | 'in_cart' | 'skipped';

// Combined status for internal tracking
export type ItemStatus = MyItemStatus | BrowseStatus;

// ============================================================================
// ALERT TIMER SYSTEM - Time-Sensitive Emergency Alerts
// ============================================================================

export interface AlertTimer {
  startTime: number; // Timestamp when alert was created
  duration: number; // Duration in milliseconds
  expiresAt: number; // Calculated expiration timestamp
  isPermanent?: boolean; // For ICE facilities (never expires)
}

// Timer Defaults:
// - Police alerts: 5 minutes (300000ms)
// - ICE alerts: Longer timer (configurable, e.g., 60 minutes = 3600000ms)
// - ICE facilities: Permanent (isPermanent: true, duration ignored)

// ============================================================================
// STAY LIMIT SYSTEM - Mutual Aid Housing Restrictions
// ============================================================================

export interface StayLimit {
  maxNights: number; // 1 for couch, 2 for camping, unlimited for housing
  checkIn?: number; // Timestamp when guest checked in
  checkOut?: number; // Timestamp when guest checked out
}

// Stay Limit Rules:
// - Couch: 1 night max
// - Camping: 2 nights max
// - Housing: No limit (maxNights: Infinity)

// ============================================================================
// SHARE ECONOMY STATUS - Item Lending/Borrowing Tracking
// ============================================================================

export type ShareStatus = 'available' | 'lent' | 'leased' | 'returned';

// Share Status Lifecycle:
// - available: Item is ready to be shared
// - lent: Item is currently lent out (GPS tracking active)
// - leased: Item is on a timed lease (paid rental)
// - returned: Item was returned by borrower

export interface CapturedItem {
  id: string;
  blob: Blob;
  url: string;
  blobUrl?: string; // For IndexedDB storage
  ipfsCid?: string; // IPFS Content Identifier (decentralized storage)
  latitude?: number;
  longitude?: number;
  status: ItemStatus;
  ownership: ItemOwnership; // Track if this is my item or someone else's
  classification?: ItemClassification; // How the item is classified (11 types across 4 pillars)

  // ============================================================================
  // COMMERCE FIELDS (free, discount, bid)
  // ============================================================================
  price?: number; // For selling items (auto-set based on classification)
  originalPrice?: number; // Detected price from Google Vision API (future)
  discountPercent?: number; // Discount percentage (75 or 50) - default 75
  bidDurationHours?: number; // Bid duration in hours (24, 48, or 72) - default 48

  // ============================================================================
  // SHARE ECONOMY FIELDS (share, wanted)
  // ============================================================================
  shareStatus?: ShareStatus; // Tracking for lent/borrowed items
  leaseDuration?: number; // Days for lease (if leased vs lent)
  trackingEnabled?: boolean; // GPS tracking for lent items

  // ============================================================================
  // MUTUAL AID FIELDS (food, couch, camping, housing)
  // ============================================================================
  stayLimit?: StayLimit; // Max nights for couch (1) and camping (2)

  // ============================================================================
  // ALERT FIELDS (ice, police)
  // ============================================================================
  alertTimer?: AlertTimer; // Countdown timer for time-sensitive alerts
  alertStatus?: 'active' | 'ongoing' | 'safe' | 'expired'; // Alert lifecycle status

  // ============================================================================
  // COMMUNITY MODERATION FIELDS
  // ============================================================================
  reportCount?: number; // How many users reported this item
  moderationVotes?: {
    keep: string[];    // User IDs who voted to keep
    remove: string[];  // User IDs who voted to remove
  };
  moderationStatus?: 'pending' | 'cleared' | 'hidden'; // Moderation lifecycle
  reportedBy?: string[]; // User IDs who reported (prevent duplicate reports)
  contentWarning?: boolean; // Auto-set for ice/police (graphic crisis content)
  moderationThreshold?: number; // Votes needed to hide: 5 (GotJunk) or 10 (LA trusted only)

  // ============================================================================
  // LEGACY/METADATA FIELDS
  // ============================================================================
  description?: string; // Item description
  createdAt: number; // Timestamp
  userId?: string; // Who owns this item (for "others" items)

  // DEPRECATED - Will be removed in future version
  // Use classification === 'ice' | 'police' instead
  libertyAlert?: boolean; // @deprecated Use classification-based filtering
  libertyRegion?: string; // Which Liberty region (optional metadata)
}
