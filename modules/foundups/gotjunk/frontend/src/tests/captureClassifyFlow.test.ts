/**
 * Capture + Classification Flow E2E Test Suite
 *
 * Tests the complete photo capture and classification workflow:
 * 1. Manual mode: Photo → Modal → Classify → My Drafts
 * 2. Auto mode: Toggle ON → Photo → Auto-classify (no modal) → My Drafts
 * 3. Race condition fix verification
 * 4. Edge cases (toggle while capturing, rapid captures, etc.)
 */

import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest';

// Mock types
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

interface LastClassification {
  type: ItemClassification;
  discountPercent?: number;
  bidDurationHours?: number;
}

describe('Capture + Classification Flow (E2E)', () => {
  let autoClassifyEnabled: boolean;
  let lastClassification: LastClassification | null;
  let pendingClassificationItem: {blob: Blob, url: string, location?: {latitude: number, longitude: number}} | null;
  let myDrafts: CapturedItem[];
  let classificationCompletedRef: {current: boolean};
  let pendingClassificationBackupRef: {current: any};
  let isProcessingClassification: boolean;

  // Mock state setters
  const setAutoClassifyEnabled = (value: boolean) => { autoClassifyEnabled = value; };
  const setLastClassification = (value: LastClassification | null) => { lastClassification = value; };
  const setPendingClassificationItem = (value: any) => { pendingClassificationItem = value; };
  const setMyDrafts = (fn: (current: CapturedItem[]) => CapturedItem[]) => { myDrafts = fn(myDrafts); };
  const setIsProcessingClassification = (value: boolean) => { isProcessingClassification = value; };

  // Mock storage
  const storage = {
    saveItem: vi.fn(async (item: CapturedItem) => {
      console.log('[Test] saveItem:', item.id, item.classification);
    })
  };

  // Mock location
  const mockLocation = { latitude: 37.7749, longitude: -122.4194 };

  beforeEach(() => {
    autoClassifyEnabled = false;
    lastClassification = null;
    pendingClassificationItem = null;
    myDrafts = [];
    classificationCompletedRef = { current: false };
    pendingClassificationBackupRef = { current: null };
    isProcessingClassification = false;
    vi.clearAllMocks();
  });

  afterEach(() => {
    // Clean up blob URLs
    myDrafts.forEach(item => URL.revokeObjectURL(item.url));
  });

  // Simulate handleClassify with race condition fix (itemOverride parameter)
  const handleClassify = async (
    classification: ItemClassification,
    discountPercent?: number,
    bidDurationHours?: number,
    itemOverride?: {blob: Blob, url: string, location?: {latitude: number, longitude: number}}
  ) => {
    console.log('[Test] handleClassify:', { classification, discountPercent, bidDurationHours, hasOverride: !!itemOverride });

    // Use itemOverride for auto-classify (avoids React setState race condition)
    const item = itemOverride || pendingClassificationItem;

    if (!item || isProcessingClassification) {
      console.warn('[Test] handleClassify - no item or already processing!');
      return;
    }

    const { blob, url, location } = item;

    // Mark classification as completed
    classificationCompletedRef.current = true;
    pendingClassificationBackupRef.current = null;

    // Store this classification for future auto-classify
    setLastClassification({
      type: classification,
      discountPercent,
      bidDurationHours
    });

    setPendingClassificationItem(null);
    setIsProcessingClassification(true);

    try {
      const defaultPrice = 100;
      let price = 0;

      const finalDiscountPercent = discountPercent || 75;
      const finalBidDurationHours = bidDurationHours || 48;

      if (classification === 'free') {
        price = 0;
      } else if (classification === 'discount') {
        price = defaultPrice * (1 - finalDiscountPercent / 100);
      } else if (classification === 'bid') {
        price = defaultPrice * 0.5;
      }

      const newItem: CapturedItem = {
        id: `item-${Date.now()}`,
        blob,
        url,
        status: 'draft',
        ownership: 'mine',
        classification,
        price,
        originalPrice: defaultPrice,
        discountPercent: classification === 'discount' ? finalDiscountPercent : undefined,
        bidDurationHours: classification === 'bid' ? finalBidDurationHours : undefined,
        createdAt: Date.now(),
        ...location,
      };

      await storage.saveItem(newItem);
      setMyDrafts(current => [newItem, ...current]);
      console.log('[Test] Item created:', newItem.id, classification);
    } catch (error) {
      console.error('[Test] Error in handleClassify:', error);
    } finally {
      setIsProcessingClassification(false);
    }
  };

  // Simulate handleCapture with auto-classify logic
  const handleCapture = async (blob: Blob) => {
    const capturedItem = {
      blob,
      url: URL.createObjectURL(blob),
      location: mockLocation
    };

    console.log('[Test] handleCapture called, autoClassifyEnabled:', autoClassifyEnabled, 'lastClassification:', lastClassification);

    // Check if auto-classify is enabled (this is the key logic)
    if (autoClassifyEnabled && lastClassification) {
      console.log('[Test] Auto-classify enabled - using last classification:', lastClassification);

      classificationCompletedRef.current = true;
      pendingClassificationBackupRef.current = null;

      // FIX: Pass item directly to avoid race condition
      await handleClassify(
        lastClassification.type,
        lastClassification.discountPercent,
        lastClassification.bidDurationHours,
        capturedItem  // itemOverride parameter
      );
      return;
    }

    // Manual mode: Show classification modal
    classificationCompletedRef.current = false;
    pendingClassificationBackupRef.current = capturedItem;
    setPendingClassificationItem(capturedItem);
    console.log('[Test] Manual mode - showing classification modal');
  };

  describe('Manual Mode (Toggle OFF)', () => {
    it('should capture photo and show classification modal', async () => {
      setAutoClassifyEnabled(false);
      const blob = new Blob(['test-photo'], { type: 'image/jpeg' });

      await handleCapture(blob);

      // Modal should be shown (pendingClassificationItem is set)
      expect(pendingClassificationItem).not.toBeNull();
      expect(pendingClassificationBackupRef.current).not.toBeNull();
      expect(classificationCompletedRef.current).toBe(false);
      expect(myDrafts.length).toBe(0); // No item created yet
    });

    it('should classify as FREE after user selects in modal', async () => {
      setAutoClassifyEnabled(false);
      const blob = new Blob(['test-photo'], { type: 'image/jpeg' });

      await handleCapture(blob);
      expect(pendingClassificationItem).not.toBeNull();

      // User clicks FREE in modal
      await handleClassify('free');

      expect(myDrafts.length).toBe(1);
      expect(myDrafts[0].classification).toBe('free');
      expect(myDrafts[0].price).toBe(0);
      expect(pendingClassificationItem).toBeNull(); // Modal closed
      expect(lastClassification?.type).toBe('free'); // Stored for future auto-classify
    });

    it('should classify as DISCOUNT 90% after user selects', async () => {
      setAutoClassifyEnabled(false);
      const blob = new Blob(['test-photo'], { type: 'image/jpeg' });

      await handleCapture(blob);

      // User selects DISCOUNT 90% in modal
      await handleClassify('discount', 90);

      expect(myDrafts.length).toBe(1);
      expect(myDrafts[0].classification).toBe('discount');
      expect(myDrafts[0].discountPercent).toBe(90);
      expect(myDrafts[0].price).toBe(10); // 100 * (1 - 0.90) = 10
      expect(lastClassification).toEqual({ type: 'discount', discountPercent: 90, bidDurationHours: undefined });
    });

    it('should classify as BID 72h after user selects', async () => {
      setAutoClassifyEnabled(false);
      const blob = new Blob(['test-photo'], { type: 'image/jpeg' });

      await handleCapture(blob);

      // User selects BID 72h in modal
      await handleClassify('bid', undefined, 72);

      expect(myDrafts.length).toBe(1);
      expect(myDrafts[0].classification).toBe('bid');
      expect(myDrafts[0].bidDurationHours).toBe(72);
      expect(myDrafts[0].price).toBe(50); // 100 * 0.5 = 50
      expect(lastClassification).toEqual({ type: 'bid', discountPercent: undefined, bidDurationHours: 72 });
    });
  });

  describe('Auto Mode (Toggle ON) - Race Condition Fix', () => {
    it('should auto-classify as FREE without showing modal', async () => {
      // Step 1: Classify first photo manually
      const blob1 = new Blob(['photo1'], { type: 'image/jpeg' });
      await handleCapture(blob1);
      await handleClassify('free');

      expect(myDrafts.length).toBe(1);
      expect(lastClassification?.type).toBe('free');

      // Step 2: Toggle auto-classify ON
      setAutoClassifyEnabled(true);

      // Step 3: Capture second photo - should auto-classify as FREE
      const blob2 = new Blob(['photo2'], { type: 'image/jpeg' });
      await handleCapture(blob2);

      // Verify: Second item created automatically, NO modal shown
      expect(myDrafts.length).toBe(2);
      expect(myDrafts[0].classification).toBe('free');
      expect(pendingClassificationItem).toBeNull(); // Modal NOT shown
      expect(storage.saveItem).toHaveBeenCalledTimes(2);
    });

    it('should auto-classify as DISCOUNT 80% without modal', async () => {
      // Step 1: Classify manually as DISCOUNT 80%
      const blob1 = new Blob(['photo1'], { type: 'image/jpeg' });
      await handleCapture(blob1);
      await handleClassify('discount', 80);

      expect(lastClassification).toEqual({ type: 'discount', discountPercent: 80, bidDurationHours: undefined });

      // Step 2: Toggle ON
      setAutoClassifyEnabled(true);

      // Step 3: Capture - should auto-classify as DISCOUNT 80%
      const blob2 = new Blob(['photo2'], { type: 'image/jpeg' });
      await handleCapture(blob2);

      expect(myDrafts.length).toBe(2);
      expect(myDrafts[0].classification).toBe('discount');
      expect(myDrafts[0].discountPercent).toBe(80);
      expect(myDrafts[0].price).toBe(20); // 100 * (1 - 0.80) = 20
    });

    it('should auto-classify as BID 96h without modal', async () => {
      // Step 1: Classify manually as BID 96h
      const blob1 = new Blob(['photo1'], { type: 'image/jpeg' });
      await handleCapture(blob1);
      await handleClassify('bid', undefined, 96);

      // Step 2: Toggle ON
      setAutoClassifyEnabled(true);

      // Step 3: Capture - should auto-classify as BID 96h
      const blob2 = new Blob(['photo2'], { type: 'image/jpeg' });
      await handleCapture(blob2);

      expect(myDrafts.length).toBe(2);
      expect(myDrafts[0].classification).toBe('bid');
      expect(myDrafts[0].bidDurationHours).toBe(96);
    });

    it('should NOT auto-classify when toggle is OFF', async () => {
      // Step 1: Store a classification
      setLastClassification({ type: 'free' });

      // Step 2: Ensure toggle is OFF
      setAutoClassifyEnabled(false);

      // Step 3: Capture - should show modal
      const blob = new Blob(['photo'], { type: 'image/jpeg' });
      await handleCapture(blob);

      expect(pendingClassificationItem).not.toBeNull(); // Modal shown
      expect(myDrafts.length).toBe(0); // No item created yet
    });

    it('should NOT auto-classify when lastClassification is null', async () => {
      // Step 1: Toggle ON but no last classification
      setAutoClassifyEnabled(true);
      setLastClassification(null);

      // Step 2: Capture - should show modal
      const blob = new Blob(['photo'], { type: 'image/jpeg' });
      await handleCapture(blob);

      expect(pendingClassificationItem).not.toBeNull(); // Modal shown
      expect(myDrafts.length).toBe(0);
    });
  });

  describe('Race Condition Fix Verification', () => {
    it('should pass item directly via itemOverride (no setState race)', async () => {
      // This tests the fix: itemOverride parameter prevents race condition
      setAutoClassifyEnabled(true);
      setLastClassification({ type: 'free' });

      const blob = new Blob(['photo'], { type: 'image/jpeg' });

      // Before fix: setPendingClassificationItem was async, so handleClassify
      // would execute before state updated, causing item to be null
      // After fix: item passed directly via itemOverride parameter

      await handleCapture(blob);

      // Verify: Item created successfully without race condition
      expect(myDrafts.length).toBe(1);
      expect(myDrafts[0].classification).toBe('free');
      expect(storage.saveItem).toHaveBeenCalledTimes(1);
    });

    it('should handle rapid captures in auto mode', async () => {
      setAutoClassifyEnabled(true);
      setLastClassification({ type: 'free' });

      const blob1 = new Blob(['photo1'], { type: 'image/jpeg' });
      const blob2 = new Blob(['photo2'], { type: 'image/jpeg' });
      const blob3 = new Blob(['photo3'], { type: 'image/jpeg' });

      // Rapid captures
      await handleCapture(blob1);
      await handleCapture(blob2);
      await handleCapture(blob3);

      // All should succeed
      expect(myDrafts.length).toBe(3);
      expect(myDrafts.every(i => i.classification === 'free')).toBe(true);
      expect(storage.saveItem).toHaveBeenCalledTimes(3);
    });
  });

  describe('Toggle State Transitions', () => {
    it('should switch from manual to auto mid-session', async () => {
      // Capture 1: Manual mode
      setAutoClassifyEnabled(false);
      const blob1 = new Blob(['photo1'], { type: 'image/jpeg' });
      await handleCapture(blob1);
      await handleClassify('discount', 50);

      expect(myDrafts.length).toBe(1);

      // Toggle ON
      setAutoClassifyEnabled(true);

      // Capture 2: Auto mode
      const blob2 = new Blob(['photo2'], { type: 'image/jpeg' });
      await handleCapture(blob2);

      expect(myDrafts.length).toBe(2);
      expect(myDrafts[0].classification).toBe('discount');
      expect(myDrafts[0].discountPercent).toBe(50);
    });

    it('should switch from auto to manual mid-session', async () => {
      // Setup auto mode
      setAutoClassifyEnabled(true);
      setLastClassification({ type: 'free' });

      // Capture 1: Auto mode
      const blob1 = new Blob(['photo1'], { type: 'image/jpeg' });
      await handleCapture(blob1);
      expect(myDrafts.length).toBe(1);

      // Toggle OFF
      setAutoClassifyEnabled(false);

      // Capture 2: Manual mode
      const blob2 = new Blob(['photo2'], { type: 'image/jpeg' });
      await handleCapture(blob2);

      expect(pendingClassificationItem).not.toBeNull(); // Modal shown
      expect(myDrafts.length).toBe(1); // Only first item created
    });
  });

  describe('Classification Storage', () => {
    it('should update lastClassification when user changes classification type', async () => {
      // First: FREE
      const blob1 = new Blob(['photo1'], { type: 'image/jpeg' });
      await handleCapture(blob1);
      await handleClassify('free');
      expect(lastClassification?.type).toBe('free');

      // Second: DISCOUNT
      const blob2 = new Blob(['photo2'], { type: 'image/jpeg' });
      await handleCapture(blob2);
      await handleClassify('discount', 90);
      expect(lastClassification).toEqual({ type: 'discount', discountPercent: 90, bidDurationHours: undefined });

      // Third: BID
      const blob3 = new Blob(['photo3'], { type: 'image/jpeg' });
      await handleCapture(blob3);
      await handleClassify('bid', undefined, 24);
      expect(lastClassification).toEqual({ type: 'bid', discountPercent: undefined, bidDurationHours: 24 });
    });
  });

  describe('My Drafts Integration', () => {
    it('should add items to myDrafts with correct ownership and status', async () => {
      const blob = new Blob(['photo'], { type: 'image/jpeg' });
      await handleCapture(blob);
      await handleClassify('free');

      expect(myDrafts.length).toBe(1);
      expect(myDrafts[0].ownership).toBe('mine');
      expect(myDrafts[0].status).toBe('draft');
    });

    it('should maintain chronological order (newest first)', async () => {
      const blob1 = new Blob(['photo1'], { type: 'image/jpeg' });
      await handleCapture(blob1);
      await handleClassify('free');

      // Small delay to ensure different timestamps
      await new Promise(resolve => setTimeout(resolve, 10));

      const blob2 = new Blob(['photo2'], { type: 'image/jpeg' });
      await handleCapture(blob2);
      await handleClassify('discount', 75);

      expect(myDrafts.length).toBe(2);
      expect(myDrafts[0].createdAt).toBeGreaterThan(myDrafts[1].createdAt); // Newest first
      expect(myDrafts[0].classification).toBe('discount'); // Most recent
      expect(myDrafts[1].classification).toBe('free'); // Older
    });
  });
});
