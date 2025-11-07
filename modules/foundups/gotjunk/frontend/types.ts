
// Item ownership: who owns this item?
export type ItemOwnership = 'mine' | 'others';

// Item classification: how is this item being sold?
export type ItemClassification = 'free' | 'discount' | 'bid';

// Item status for MY items
export type MyItemStatus = 'draft' | 'listed' | 'sold' | 'auction';

// Item status when browsing OTHER people's items
export type BrowseStatus = 'browsing' | 'in_cart' | 'skipped';

// Combined status for internal tracking
export type ItemStatus = MyItemStatus | BrowseStatus;

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
  classification?: ItemClassification; // How the item is being sold (free/discount/bid)
  price?: number; // For selling items (auto-set based on classification)
  originalPrice?: number; // Detected price from Google Vision API (future)
  discountPercent?: number; // Discount percentage (75 or 50) - default 75
  bidDurationHours?: number; // Bid duration in hours (24, 48, or 72) - default 48
  description?: string; // Item description
  createdAt: number; // Timestamp
  userId?: string; // Who owns this item (for "others" items)
}
