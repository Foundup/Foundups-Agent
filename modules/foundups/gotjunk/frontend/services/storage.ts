
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

export const getAllItems = async (): Promise<CapturedItem[]> => {
    const items: CapturedItem[] = [];
    await localforage.iterate((value: StorableItem, key: string) => {
        // Ensure status defaults to 'review' for legacy items that don't have it.
        if (!value.status) {
            value.status = 'review';
        }
        const url = URL.createObjectURL(value.blob);
        items.push({ ...value, id: key, url });
    });
    // Sort by newest first
    return items.sort((a, b) => {
      const timeA = parseInt(a.id.split('-')[1] || '0');
      const timeB = parseInt(b.id.split('-')[1] || '0');
      return timeB - timeA;
    });
};

export const deleteItem = async (id: string): Promise<void> => {
    await localforage.removeItem(id);
};
