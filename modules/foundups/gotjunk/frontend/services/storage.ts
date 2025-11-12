
import localforage from 'localforage';
import { CapturedItem, ItemStatus } from '../types';

localforage.config({
    name: 'got-junk-pwa',
    storeName: 'captured_items',
    description: 'Storage for captured images and their status'
});

// StorableItem omits the URL, which is generated at runtime.
type StorableItem = Omit<CapturedItem, 'url'>;

export const saveItem = async (item: CapturedItem): Promise<void> => {
    const { url, ...storableItem } = item;
    await localforage.setItem(item.id, storableItem);
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
