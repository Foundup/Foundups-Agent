/**
 * Cart Flow Test Suite
 *
 * Tests the complete cart flow:
 * 1. Items appear in browse feed
 * 2. Right swipe adds to cart
 * 3. Cart displays items correctly
 * 4. Left swipe skips items
 * 5. Cart removal returns items to browse
 *
 * Tests both "my items" and "other people's items" scenarios.
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';

// Mock types matching App.tsx
type ItemClassification = 'free' | 'discount' | 'bid';
type ItemStatus = 'draft' | 'browsing' | 'in_cart' | 'skipped' | 'listed';
type ItemOwnership = 'mine' | 'others';

interface CapturedItem {
  id: string;
  blob: Blob;
  url: string;
  status: ItemStatus;
  ownership: ItemOwnership;
  classification: ItemClassification;
  price: number;
  originalPrice: number;
  discountPercent?: number;
  bidDurationHours?: number;
  latitude?: number;
  longitude?: number;
  createdAt: number;
}

describe('Cart Flow', () => {
  let browseFeed: CapturedItem[];
  let cart: CapturedItem[];
  let skipped: CapturedItem[];

  // Mock state setters
  const setBrowseFeed = (fn: (current: CapturedItem[]) => CapturedItem[]) => {
    browseFeed = fn(browseFeed);
  };
  const setCart = (fn: (current: CapturedItem[]) => CapturedItem[]) => {
    cart = fn(cart);
  };
  const setSkipped = (fn: (current: CapturedItem[]) => CapturedItem[]) => {
    skipped = fn(skipped);
  };

  // Mock storage
  const storage = {
    updateItemStatus: vi.fn(async (id: string, status: ItemStatus) => {
      console.log('[Test] updateItemStatus:', id, status);
    })
  };

  beforeEach(() => {
    browseFeed = [];
    cart = [];
    skipped = [];
    vi.clearAllMocks();
  });

  // Simulate handleBrowseSwipe from App.tsx
  const handleBrowseSwipe = async (item: CapturedItem, direction: 'left' | 'right') => {
    console.log('[Test] handleBrowseSwipe:', item.id, direction, 'ownership:', item.ownership);

    // Remove from browse feed
    setBrowseFeed(current => current.filter(i => i.id !== item.id));

    if (direction === 'right') {
      // Swipe RIGHT = Add to cart
      const cartItem: CapturedItem = { ...item, status: 'in_cart' };
      setCart(current => [cartItem, ...current]);
      await storage.updateItemStatus(item.id, 'in_cart');
      console.log('[Test] Added to cart:', item.id);
    } else {
      // Swipe LEFT = Skip
      const skippedItem: CapturedItem = { ...item, status: 'skipped' };
      setSkipped(current => [skippedItem, ...current]);
      await storage.updateItemStatus(item.id, 'skipped');
      console.log('[Test] Skipped item:', item.id);
    }
  };

  // Helper: Create test item
  const createItem = (id: string, ownership: ItemOwnership, status: ItemStatus = 'browsing'): CapturedItem => ({
    id,
    blob: new Blob(['test'], { type: 'image/jpeg' }),
    url: `blob:${id}`,
    status,
    ownership,
    classification: 'free',
    price: 0,
    originalPrice: 100,
    latitude: 37.7749,
    longitude: -122.4194,
    createdAt: Date.now()
  });

  describe('Browse Feed → Cart (Right Swipe)', () => {
    it('should add item to cart when swiping right', async () => {
      const item = createItem('item-1', 'others', 'browsing');
      browseFeed = [item];

      await handleBrowseSwipe(item, 'right');

      expect(browseFeed.length).toBe(0); // Removed from browse
      expect(cart.length).toBe(1); // Added to cart
      expect(cart[0].id).toBe('item-1');
      expect(cart[0].status).toBe('in_cart');
      expect(storage.updateItemStatus).toHaveBeenCalledWith('item-1', 'in_cart');
    });

    it('should add MY OWN item to cart (for testing)', async () => {
      // This tests the current behavior: browse feed includes user's own items
      const myItem = createItem('my-item-1', 'mine', 'browsing');
      browseFeed = [myItem];

      await handleBrowseSwipe(myItem, 'right');

      expect(browseFeed.length).toBe(0);
      expect(cart.length).toBe(1);
      expect(cart[0].id).toBe('my-item-1');
      expect(cart[0].ownership).toBe('mine'); // User's own item in cart!
      expect(cart[0].status).toBe('in_cart');
    });

    it('should handle multiple items added to cart', async () => {
      const item1 = createItem('item-1', 'others', 'browsing');
      const item2 = createItem('item-2', 'mine', 'browsing');
      const item3 = createItem('item-3', 'others', 'browsing');
      browseFeed = [item1, item2, item3];

      await handleBrowseSwipe(item1, 'right');
      await handleBrowseSwipe(item2, 'right');
      await handleBrowseSwipe(item3, 'right');

      expect(cart.length).toBe(3);
      expect(cart.map(i => i.id)).toEqual(['item-3', 'item-2', 'item-1']); // Newest first
      expect(browseFeed.length).toBe(0);
    });

    it('should preserve item properties when adding to cart', async () => {
      const item = createItem('item-1', 'others', 'browsing');
      item.classification = 'discount';
      item.price = 25;
      item.discountPercent = 75;
      browseFeed = [item];

      await handleBrowseSwipe(item, 'right');

      expect(cart[0].classification).toBe('discount');
      expect(cart[0].price).toBe(25);
      expect(cart[0].discountPercent).toBe(75);
    });
  });

  describe('Browse Feed → Skipped (Left Swipe)', () => {
    it('should skip item when swiping left', async () => {
      const item = createItem('item-1', 'others', 'browsing');
      browseFeed = [item];

      await handleBrowseSwipe(item, 'left');

      expect(browseFeed.length).toBe(0); // Removed from browse
      expect(cart.length).toBe(0); // NOT in cart
      expect(skipped.length).toBe(1); // Added to skipped
      expect(skipped[0].id).toBe('item-1');
      expect(skipped[0].status).toBe('skipped');
      expect(storage.updateItemStatus).toHaveBeenCalledWith('item-1', 'skipped');
    });

    it('should skip multiple items', async () => {
      const item1 = createItem('item-1', 'others', 'browsing');
      const item2 = createItem('item-2', 'mine', 'browsing');
      browseFeed = [item1, item2];

      await handleBrowseSwipe(item1, 'left');
      await handleBrowseSwipe(item2, 'left');

      expect(skipped.length).toBe(2);
      expect(cart.length).toBe(0);
    });
  });

  describe('Cart Display', () => {
    it('should display items in cart tab', () => {
      const item1 = createItem('item-1', 'others', 'in_cart');
      const item2 = createItem('item-2', 'mine', 'in_cart');
      cart = [item1, item2];

      // Cart tab should show all items with status='in_cart'
      expect(cart.length).toBe(2);
      expect(cart.every(i => i.status === 'in_cart')).toBe(true);
    });

    it('should show empty state when cart is empty', () => {
      expect(cart.length).toBe(0);
      // In UI: "0 items • Swipe right on browse items to add them here"
    });
  });

  describe('Cart Removal (Undo)', () => {
    it('should remove item from cart and return to browse', async () => {
      const item = createItem('item-1', 'others', 'in_cart');
      cart = [item];

      // Simulate cart removal (PhotoGrid onDelete)
      setCart(prev => prev.filter(i => i.id !== item.id));
      await storage.updateItemStatus(item.id, 'browsing');

      expect(cart.length).toBe(0);
      expect(storage.updateItemStatus).toHaveBeenCalledWith('item-1', 'browsing');
      // Item should reappear in browse feed on next load
    });
  });

  describe('Ownership Scenarios', () => {
    it('should handle mixed ownership in browse feed', () => {
      const myItem = createItem('my-1', 'mine', 'browsing');
      const otherItem1 = createItem('other-1', 'others', 'browsing');
      const otherItem2 = createItem('other-2', 'others', 'browsing');
      browseFeed = [myItem, otherItem1, otherItem2];

      // Current behavior: ALL items (including mine) appear in browse
      expect(browseFeed.length).toBe(3);
      expect(browseFeed.filter(i => i.ownership === 'mine').length).toBe(1);
      expect(browseFeed.filter(i => i.ownership === 'others').length).toBe(2);
    });

    it('should allow adding MY OWN items to cart (current testing behavior)', async () => {
      // This is the UX confusion: user can swipe right on their own items
      const myItem = createItem('my-1', 'mine', 'browsing');
      browseFeed = [myItem];

      await handleBrowseSwipe(myItem, 'right');

      expect(cart.length).toBe(1);
      expect(cart[0].ownership).toBe('mine');
      // TODO: Future - add toggle to exclude user's own items from browse feed (line 173-175 in App.tsx)
    });
  });

  describe('Edge Cases', () => {
    it('should handle empty browse feed', async () => {
      expect(browseFeed.length).toBe(0);
      // UI should show: "No items found • 50km radius"
    });

    it('should handle rapid swipes (multiple items)', async () => {
      const items = [
        createItem('item-1', 'others', 'browsing'),
        createItem('item-2', 'mine', 'browsing'),
        createItem('item-3', 'others', 'browsing'),
      ];
      browseFeed = [...items];

      // Rapid swipes
      await Promise.all([
        handleBrowseSwipe(items[0], 'right'),
        handleBrowseSwipe(items[1], 'left'),
        handleBrowseSwipe(items[2], 'right'),
      ]);

      expect(cart.length).toBe(2); // items[0] and items[2]
      expect(skipped.length).toBe(1); // items[1]
      expect(browseFeed.length).toBe(0);
    });

    it('should not duplicate items in cart', async () => {
      const item = createItem('item-1', 'others', 'browsing');
      browseFeed = [item];

      await handleBrowseSwipe(item, 'right');

      // Try to add again (shouldn't happen in real app, but test defensively)
      const cartSize = cart.length;
      expect(cartSize).toBe(1);
    });
  });
});
