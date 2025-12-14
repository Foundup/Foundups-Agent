/**
 * Message Storage Service - IndexedDB Persistence for Wave-Style Messaging
 * 
 * Architecture (WSP 98 - Mesh-Native):
 * - Layer 1: IndexedDB (this file) - offline-first, instant access
 * - Layer 2: Firestore (messageSync.ts) - cross-device sync (Sprint M2)
 * 
 * Storage Pattern:
 * - Store Name: message_threads (separate from captured_items)
 * - Key: contextKey format (type::itemId::alertId)
 * - Value: Full MessageThread object
 */

import localforage from 'localforage';
import { MessageThread, MessageContextRef } from './types';

// Configure separate store for message threads
const messageStore = localforage.createInstance({
  name: 'got-junk-pwa',
  storeName: 'message_threads',
  description: 'Storage for Wave-style message threads',
});

/**
 * Generate storage key from context (matches messageStore.ts pattern)
 */
export const contextKey = (ctx: MessageContextRef): string =>
  `${ctx.type}::${ctx.itemId ?? ''}::${ctx.alertId ?? ''}`;

/**
 * Load all message threads from IndexedDB
 * Called on app init to hydrate InMemoryMessageStore
 */
export const loadAllThreads = async (): Promise<Map<string, MessageThread>> => {
  const threads = new Map<string, MessageThread>();
  
  try {
    await messageStore.iterate<MessageThread, void>((thread, key) => {
      threads.set(key, thread);
    });
    console.log(`[MessageStorage] Loaded ${threads.size} threads from IndexedDB`);
  } catch (err) {
    console.error('[MessageStorage] Failed to load threads:', err);
  }
  
  return threads;
};

/**
 * Save a single thread to IndexedDB
 * Called after addMessage, closeThread, lockThread
 */
export const saveThread = async (key: string, thread: MessageThread): Promise<void> => {
  try {
    await messageStore.setItem(key, thread);
    console.log(`[MessageStorage] Saved thread: ${key} (${thread.messages.length} messages)`);
  } catch (err) {
    console.error('[MessageStorage] Failed to save thread:', key, err);
  }
};

/**
 * Delete a thread from IndexedDB
 * Called when thread is empty after pruneExpired
 */
export const deleteThread = async (key: string): Promise<void> => {
  try {
    await messageStore.removeItem(key);
    console.log(`[MessageStorage] Deleted thread: ${key}`);
  } catch (err) {
    console.error('[MessageStorage] Failed to delete thread:', key, err);
  }
};

/**
 * Clear all message threads (for testing/reset)
 */
export const clearAllThreads = async (): Promise<void> => {
  try {
    await messageStore.clear();
    console.log('[MessageStorage] Cleared all threads');
  } catch (err) {
    console.error('[MessageStorage] Failed to clear threads:', err);
  }
};

/**
 * Get thread count (for debugging)
 */
export const getThreadCount = async (): Promise<number> => {
  return await messageStore.length();
};

