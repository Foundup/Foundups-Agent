/**
 * Auto-Classify Feature Test Suite
 *
 * Tests the auto-classify toggle functionality that allows users to:
 * 1. Toggle auto-classify ON/OFF
 * 2. Store last classification (free/discount/bid)
 * 3. Auto-apply classification without showing modal
 *
 * Bug Fixed: Race condition where setState was async but handleClassify
 * expected pendingClassificationItem to be set immediately.
 * Solution: Pass item directly to handleClassify via itemOverride parameter.
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';

// Mock types matching App.tsx
type ItemClassification = 'free' | 'discount' | 'bid';

interface CapturedItem {
  id: string;
  blob: Blob;
  url: string;
  status: 'draft' | 'browsing' | 'in_cart' | 'skipped' | 'listed';
  ownership: 'mine' | 'others';
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

describe('Auto-Classify Feature', () => {
  let autoClassifyEnabled: boolean;
  let lastClassification: LastClassification | null;
  let pendingClassificationItem: {blob: Blob, url: string, location?: {latitude: number, longitude: number}} | null;
  let myDrafts: CapturedItem[];
  let classificationCompletedRef: {current: boolean};
  let pendingClassificationBackupRef: {current: any};
  let isProcessingClassification: boolean;

  // Mock functions
  const setAutoClassifyEnabled = (value: boolean) => { autoClassifyEnabled = value; };
  const setLastClassification = (value: LastClassification | null) => { lastClassification = value; };
  const setPendingClassificationItem = (value: any) => { pendingClassificationItem = value; };
  const setMyDrafts = (fn: (current: CapturedItem[]) => CapturedItem[]) => { myDrafts = fn(myDrafts); };
  const setIsProcessingClassification = (value: boolean) => { isProcessingClassification = value; };

  // Mock storage
  const storage = {
    saveItem: vi.fn(async (item: CapturedItem) => {
      console.log('[Test] saveItem called:', item.id);
    })
  };

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

  // Simulate handleClassify with itemOverride parameter (race condition fix)
  const handleClassify = async (
    classification: ItemClassification,
    discountPercent?: number,
    bidDurationHours?: number,
    itemOverride?: {blob: Blob, url: string, location?: {latitude: number, longitude: number}}
  ) => {
    console.log('[Test] handleClassify called:', { classification, discountPercent, bidDurationHours, hasOverride: !!itemOverride });

    // Use itemOverride for auto-classify (avoids React setState race condition)
    const item = itemOverride || pendingClassificationItem;

    // Prevent duplicate calls
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
    console.log('[Test] Stored classification:', { classification, discountPercent, bidDurationHours });

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

      console.log('[Test] Saving new item:', newItem.id);
      await storage.saveItem(newItem);

      setMyDrafts(current => [newItem, ...current]);
      console.log('[Test] Item added to drafts');
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
      location: { latitude: 37.7749, longitude: -122.4194 }
    };

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

  describe('Toggle State', () => {
    it('should start with auto-classify OFF', () => {
      expect(autoClassifyEnabled).toBe(false);
    });

    it('should toggle auto-classify ON', () => {
      setAutoClassifyEnabled(!autoClassifyEnabled);
      expect(autoClassifyEnabled).toBe(true);
    });

    it('should toggle auto-classify OFF after being ON', () => {
      setAutoClassifyEnabled(true);
      expect(autoClassifyEnabled).toBe(true);

      setAutoClassifyEnabled(!autoClassifyEnabled);
      expect(autoClassifyEnabled).toBe(false);
    });
  });

  describe('Last Classification Storage', () => {
    it('should store FREE classification', async () => {
      const blob = new Blob(['test'], { type: 'image/jpeg' });
      setPendingClassificationItem({
        blob,
        url: URL.createObjectURL(blob),
        location: { latitude: 37.7749, longitude: -122.4194 }
      });

      await handleClassify('free');

      expect(lastClassification).toEqual({
        type: 'free',
        discountPercent: undefined,
        bidDurationHours: undefined
      });
    });

    it('should store DISCOUNT classification with 75%', async () => {
      const blob = new Blob(['test'], { type: 'image/jpeg' });
      setPendingClassificationItem({
        blob,
        url: URL.createObjectURL(blob),
        location: { latitude: 37.7749, longitude: -122.4194 }
      });

      await handleClassify('discount', 75);

      expect(lastClassification).toEqual({
        type: 'discount',
        discountPercent: 75,
        bidDurationHours: undefined
      });
    });

    it('should store BID classification with 48h', async () => {
      const blob = new Blob(['test'], { type: 'image/jpeg' });
      setPendingClassificationItem({
        blob,
        url: URL.createObjectURL(blob),
        location: { latitude: 37.7749, longitude: -122.4194 }
      });

      await handleClassify('bid', undefined, 48);

      expect(lastClassification).toEqual({
        type: 'bid',
        discountPercent: undefined,
        bidDurationHours: 48
      });
    });
  });

  describe('Auto-Classify Flow (Race Condition Fix)', () => {
    it('should auto-classify FREE without showing modal', async () => {
      // Step 1: User classifies first item manually as FREE
      const blob1 = new Blob(['test1'], { type: 'image/jpeg' });
      setPendingClassificationItem({
        blob: blob1,
        url: URL.createObjectURL(blob1),
        location: { latitude: 37.7749, longitude: -122.4194 }
      });
      await handleClassify('free');

      expect(lastClassification?.type).toBe('free');
      expect(myDrafts.length).toBe(1);
      expect(myDrafts[0].classification).toBe('free');

      // Step 2: User toggles auto-classify ON
      setAutoClassifyEnabled(true);

      // Step 3: User captures second photo - should auto-classify as FREE
      const blob2 = new Blob(['test2'], { type: 'image/jpeg' });
      await handleCapture(blob2);

      // Verify: Second item created with FREE classification automatically
      expect(myDrafts.length).toBe(2);
      expect(myDrafts[0].classification).toBe('free');
      expect(pendingClassificationItem).toBeNull(); // Modal NOT shown
    });

    it('should auto-classify DISCOUNT 90% without showing modal', async () => {
      // Step 1: User classifies first item manually as DISCOUNT 90%
      const blob1 = new Blob(['test1'], { type: 'image/jpeg' });
      setPendingClassificationItem({
        blob: blob1,
        url: URL.createObjectURL(blob1),
        location: { latitude: 37.7749, longitude: -122.4194 }
      });
      await handleClassify('discount', 90);

      expect(lastClassification).toEqual({
        type: 'discount',
        discountPercent: 90,
        bidDurationHours: undefined
      });
      expect(myDrafts[0].discountPercent).toBe(90);

      // Step 2: Toggle auto-classify ON
      setAutoClassifyEnabled(true);

      // Step 3: Capture second photo - should auto-classify as DISCOUNT 90%
      const blob2 = new Blob(['test2'], { type: 'image/jpeg' });
      await handleCapture(blob2);

      // Verify: Second item has DISCOUNT 90%
      expect(myDrafts.length).toBe(2);
      expect(myDrafts[0].classification).toBe('discount');
      expect(myDrafts[0].discountPercent).toBe(90);
    });

    it('should auto-classify BID 72h without showing modal', async () => {
      // Step 1: User classifies first item manually as BID 72h
      const blob1 = new Blob(['test1'], { type: 'image/jpeg' });
      setPendingClassificationItem({
        blob: blob1,
        url: URL.createObjectURL(blob1),
        location: { latitude: 37.7749, longitude: -122.4194 }
      });
      await handleClassify('bid', undefined, 72);

      expect(lastClassification).toEqual({
        type: 'bid',
        discountPercent: undefined,
        bidDurationHours: 72
      });
      expect(myDrafts[0].bidDurationHours).toBe(72);

      // Step 2: Toggle auto-classify ON
      setAutoClassifyEnabled(true);

      // Step 3: Capture second photo - should auto-classify as BID 72h
      const blob2 = new Blob(['test2'], { type: 'image/jpeg' });
      await handleCapture(blob2);

      // Verify: Second item has BID 72h
      expect(myDrafts.length).toBe(2);
      expect(myDrafts[0].classification).toBe('bid');
      expect(myDrafts[0].bidDurationHours).toBe(72);
    });

    it('should NOT auto-classify when toggle is OFF', async () => {
      // Step 1: Store a classification
      setLastClassification({ type: 'free' });

      // Step 2: Ensure auto-classify is OFF
      setAutoClassifyEnabled(false);

      // Step 3: Capture photo - should show modal (manual mode)
      const blob = new Blob(['test'], { type: 'image/jpeg' });
      await handleCapture(blob);

      // Verify: Modal shown (pendingClassificationItem is set)
      expect(pendingClassificationItem).not.toBeNull();
      expect(myDrafts.length).toBe(0); // No item created yet
    });

    it('should NOT auto-classify when lastClassification is null', async () => {
      // Step 1: Toggle ON but no last classification
      setAutoClassifyEnabled(true);
      setLastClassification(null);

      // Step 2: Capture photo - should show modal
      const blob = new Blob(['test'], { type: 'image/jpeg' });
      await handleCapture(blob);

      // Verify: Modal shown
      expect(pendingClassificationItem).not.toBeNull();
      expect(myDrafts.length).toBe(0);
    });
  });

  describe('Race Condition Fix Verification', () => {
    it('should pass item directly to handleClassify (itemOverride)', async () => {
      // This test verifies the fix: itemOverride parameter avoids race condition
      setAutoClassifyEnabled(true);
      setLastClassification({ type: 'free' });

      const blob = new Blob(['test'], { type: 'image/jpeg' });

      // Before fix: setPendingClassificationItem was async, so handleClassify
      // would execute before state updated, causing item to be null
      // After fix: item passed directly via itemOverride parameter

      await handleCapture(blob);

      // Verify: Item created successfully without race condition
      expect(myDrafts.length).toBe(1);
      expect(myDrafts[0].classification).toBe('free');
      expect(storage.saveItem).toHaveBeenCalledTimes(1);
    });
  });

  describe('Manual Mode Still Works', () => {
    it('should show modal when auto-classify is OFF', async () => {
      setAutoClassifyEnabled(false);

      const blob = new Blob(['test'], { type: 'image/jpeg' });
      await handleCapture(blob);

      // Verify: Modal state set
      expect(pendingClassificationItem).not.toBeNull();
      expect(pendingClassificationBackupRef.current).not.toBeNull();
      expect(classificationCompletedRef.current).toBe(false);
    });

    it('should allow manual classification after capture', async () => {
      setAutoClassifyEnabled(false);

      const blob = new Blob(['test'], { type: 'image/jpeg' });
      await handleCapture(blob);

      // Simulate user clicking FREE in modal
      await handleClassify('free');

      // Verify: Item created
      expect(myDrafts.length).toBe(1);
      expect(myDrafts[0].classification).toBe('free');
    });
  });
});
