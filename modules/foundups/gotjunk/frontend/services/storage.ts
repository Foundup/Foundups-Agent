/**
 * Storage Service - Local + Cloud Hybrid Storage
 * WSP 98: FoundUps Mesh-Native Architecture Protocol
 *
 * Architecture:
 * - Layer 1: IndexedDB (localforage) - offline-first, instant access
 * - Layer 2: Firestore (firestoreSync) - cross-device sync
 */

import localforage from 'localforage';
import { CapturedItem, ItemStatus } from '../types';
import { syncItemToCloud, fetchItemsFromCloud, getSyncStatus } from './firestoreSync';
import { MeshDaemon } from './meshDaemon';
import { getCurrentUserId } from './firebaseAuth'; // ✅ AUTH: Ensure userId is set

localforage.config({
    name: 'got-junk-pwa',
    storeName: 'captured_items',
    description: 'Storage for captured images and their status'
});

// StorableItem omits the URL, which is generated at runtime.
type StorableItem = Omit<CapturedItem, 'url'>;

export const saveItem = async (item: CapturedItem): Promise<void> => {
    const { url, ...storableItem } = item;

    // ============================================================================
    // FIREBASE AUTH PATTERN (ensure userId is set)
    // ============================================================================
    // ✅ Set userId from auth if missing (for items created before auth initialized)
    // This ensures cross-device sync works even if item was created during auth init
    // ============================================================================
    if (!storableItem.userId) {
        const currentUid = getCurrentUserId();
        if (currentUid) {
            storableItem.userId = currentUid;
            console.log('[Storage] ✅ Set userId from auth:', currentUid);
        }
    }

    const mediaType = item.blob.type.startsWith('video/') ? 'VIDEO' : 'PHOTO';
    console.log(`[Storage] Saving ${mediaType}:`, {
        id: item.id,
        blobSize: item.blob.size,
        blobType: item.blob.type,
        classification: item.classification,
        status: item.status,
        userId: storableItem.userId // Log userId for debugging
    });

    // Layer 1: Save to IndexedDB (immediate, offline-first)
    await localforage.setItem(item.id, storableItem);
    console.log(`[Storage] ✅ ${mediaType} saved to IndexedDB:`, item.id);

    // ============================================================================
    // SYNC TIMING PATTERN (for Wave Messaging Firestore integration)
    // ============================================================================
    // Layer 2: Sync to Cloud (async, non-blocking)
    // ✅ CORRECT: App.tsx calls initializeAuth() before loading items
    // By the time items are created/saved, auth is ready
    // If auth isn't ready (edge case), syncItemToCloud fails gracefully
    // TODO: Implement sync queue to retry failed syncs after auth completes
    // ============================================================================
    syncItemToCloud(item).catch(err =>
        console.log('[Storage] Cloud sync deferred:', err.message)
    );

    // Layer 3: Broadcast to Mesh (Local-First/Gossip)
    try {
        MeshDaemon.getInstance().broadcastItem(item);
    } catch (e) {
        console.warn('[Storage] Mesh broadcast failed:', e);
    }
};

export const updateItemStatus = async (id: string, status: ItemStatus): Promise<void> => {
    const item = await localforage.getItem<StorableItem>(id);
    if (item) {
        item.status = status;
        await localforage.setItem(id, item);
        
        // Broadcast status update to Mesh
        try {
            // We need to mock the URL/Blob since we don't have it here and don't need it for status update
            // Ideally MeshDaemon accepts a lighter type
            const meshItem = { ...item, url: '', blob: new Blob() } as CapturedItem;
            MeshDaemon.getInstance().broadcastItem(meshItem);
        } catch (e) {
            console.warn('[Storage] Mesh update failed:', e);
        }
    }
}

export const getAllItems = async (limit?: number, offset: number = 0): Promise<CapturedItem[]> => {
    const items: CapturedItem[] = [];

    // First pass: collect all items without creating ObjectURLs (fast)
    const storableItems: Array<{ key: string; value: StorableItem }> = [];
    await localforage.iterate((value: StorableItem, key: string) => {
        // Ensure status defaults to 'review' for legacy items that don't have it.
        if (!value.status) {
            value.status = 'review';
        }
        storableItems.push({ key, value });
    });

    // Sort by newest first (using ID timestamp)
    storableItems.sort((a, b) => {
        const timeA = parseInt(a.key.split('-')[1] || '0');
        const timeB = parseInt(b.key.split('-')[1] || '0');
        return timeB - timeA;
    });

    // Apply pagination and create ObjectURLs only for requested items (defers expensive blob operations)
    const paginatedItems = limit !== undefined
        ? storableItems.slice(offset, offset + limit)
        : storableItems.slice(offset);

    for (const { key, value } of paginatedItems) {
        // Defensive: Skip items with missing or invalid blobs (prevents white screen crash)
        if (!value.blob || !(value.blob instanceof Blob)) {
            console.warn('[Storage] Skipping item with missing blob:', key);
            continue;
        }

        try {
            const url = URL.createObjectURL(value.blob);
            items.push({ ...value, id: key, url });
        } catch (err) {
            console.error('[Storage] Failed to create URL for item:', key, err);
            // Skip corrupted items instead of crashing
        }
    }

    return items;
};

export const deleteItem = async (id: string): Promise<void> => {
    await localforage.removeItem(id);
};

/**
 * Get all items merged from local + cloud (cross-device sync)
 * Local items take priority (fresher data), cloud items fill gaps
 */
export const getAllItemsWithCloud = async (
    limitCount?: number,
    offset: number = 0
): Promise<CapturedItem[]> => {
    // Get local items first (offline-first)
    const localItems = await getAllItems(limitCount, offset);
    const localIds = new Set(localItems.map(item => item.id));

    // Fetch cloud items (async, may fail if offline/not configured)
    try {
        const cloudItems = await fetchItemsFromCloud(limitCount || 100);
        // Merge: add cloud items that aren't already local
        for (const cloudItem of cloudItems) {
            if (!localIds.has(cloudItem.id)) {
                localItems.push(cloudItem);
            }
        }
        console.log('[Storage] Merged', localItems.length, 'items (local + cloud)');
    } catch (err) {
        console.log('[Storage] Cloud fetch skipped (offline or not configured)');
    }

    // Sort merged items by createdAt (newest first)
    localItems.sort((a, b) => (b.createdAt || 0) - (a.createdAt || 0));

    return localItems;
};

/**
 * Get sync status (for UI indicators)
 */
export const getCloudSyncStatus = () => getSyncStatus();
