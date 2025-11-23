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

localforage.config({
    name: 'got-junk-pwa',
    storeName: 'captured_items',
    description: 'Storage for captured images and their status'
});

// StorableItem omits the URL, which is generated at runtime.
type StorableItem = Omit<CapturedItem, 'url'>;

export const saveItem = async (item: CapturedItem): Promise<void> => {
    const { url, ...storableItem } = item;
    // Layer 1: Save to IndexedDB (immediate, offline-first)
    await localforage.setItem(item.id, storableItem);
    // Layer 2: Sync to Firestore (async, non-blocking)
    syncItemToCloud(item).catch(err =>
        console.log('[Storage] Cloud sync deferred:', err.message)
    );
};

export const updateItemStatus = async (id: string, status: ItemStatus): Promise<void> => {
    const item = await localforage.getItem<StorableItem>(id);
    if (item) {
        item.status = status;
        await localforage.setItem(id, item);
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
        const url = URL.createObjectURL(value.blob);
        items.push({ ...value, id: key, url });
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
