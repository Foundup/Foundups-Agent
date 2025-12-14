/**
 * Message Module - Wave-Style Messaging System
 * 
 * Public API for GotJunk messaging functionality.
 * All messaging logic contained in this module to prevent code balloon.
 * 
 * Usage:
 *   import { messageStore, MessageContextRef, Message } from '../src/message';
 *   
 *   // On app init - hydrate from IndexedDB then cloud
 *   await messageStore.hydrate();         // Local first (fast)
 *   await messageStore.hydrateFromCloud(); // Cloud merge (cross-device)
 *   
 *   // Add message
 *   messageStore.addMessage({ context, authorId, text });
 * 
 * WSP AUDIT: Auth is required for cloud writes (syncThreadToCloud)
 */

// Types
export type {
  MessageContextType,
  MessageContextRef,
  BaseMessage,
  EphemeralMeta,
  Message,
  ThreadStatus,
  ThreadMetadata,
  MessageThread,
} from './types';

// Store
export { messageStore, InMemoryMessageStore } from './messageStore';
export type { MessageStore } from './messageStore';

// Storage (for advanced use cases)
export {
  loadAllThreads,
  saveThread,
  deleteThread,
  clearAllThreads,
  getThreadCount,
  contextKey,
} from './messageStorage';

// Geohash utilities (for Liberty Alert context)
export { encodeGeohash, generateLibertyAlertId } from './geohash';

// Cloud Sync (Sprint M2 + WSP AUDIT FIX)
export {
  syncThreadToCloud,
  deleteThreadFromCloud,
  fetchThreadFromCloud,
  fetchThreadsForItem,
  fetchAllThreadsFromCloud,
  subscribeToThread,
  subscribeToAllThreads,
  isMessageSyncConfigured,
} from './messageSync';

