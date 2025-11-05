
// Item ownership: who owns this item?
export type ItemOwnership = 'mine' | 'others';

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
  price?: number; // For selling items
  description?: string; // Item description
  createdAt: number; // Timestamp
  userId?: string; // Who owns this item (for "others" items)
}
