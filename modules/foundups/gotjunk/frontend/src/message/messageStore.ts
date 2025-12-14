/**
 * Message Store - Wave-Style Messaging System
 * 
 * WSP ARCHITECTURE NOTE (DO NOT REMOVE):
 * This store uses IndexedDB persistence via messageStorage.ts
 * AND Firestore cloud sync via messageSync.ts
 * 
 * Sprint M1: IndexedDB Persistence
 * - hydrate() loads from IndexedDB on app init
 * - saveThread() persists after mutations
 * - deleteThread() removes empty threads
 * 
 * Sprint M2: Firestore Cloud Sync (WSP AUDIT FIX)
 * - hydrateFromCloud() merges cloud threads with local
 * - syncThreadToCloud() pushes changes to cloud
 * - Enables cross-device messaging
 * 
 * See: ROADMAP.md "Wave-Style Messaging System" section
 */
import { Message, MessageContextRef, MessageThread, ThreadStatus } from "./types";
import * as storage from "./messageStorage";
import * as cloudSync from "./messageSync";

export interface MessageStore {
  getThread(context: MessageContextRef): MessageThread | null;
  getMessages(context: MessageContextRef): Message[];
  addMessage(
    msg: Omit<Message, 'id' | 'createdAt' | 'expiresAt'> & {
      id?: string;
      createdAt?: number;
    }
  ): Message;
  closeThread(context: MessageContextRef, reason: string): void;
  lockThread(context: MessageContextRef, reason: string): void;
  pruneExpired(now?: number): void;
}

const DEFAULT_LA_TTL_MS = 15 * 60 * 1000;

const contextKey = (ctx: MessageContextRef) => `${ctx.type}::${ctx.itemId ?? ''}::${ctx.alertId ?? ''}`;

export class InMemoryMessageStore implements MessageStore {
  private threads: Map<string, MessageThread> = new Map();
  private isHydrated: boolean = false;
  private isCloudHydrated: boolean = false;

  /**
   * WSP M1: Hydrate store from IndexedDB (call on app init)
   * DO NOT REMOVE - without this, messages are lost on page refresh
   */
  async hydrate(): Promise<void> {
    if (this.isHydrated) return;
    
    const loadedThreads = await storage.loadAllThreads();
    this.threads = loadedThreads;
    this.isHydrated = true;
    console.log(`[MessageStore] Hydrated from IndexedDB with ${this.threads.size} threads`);
  }

  /**
   * WSP AUDIT FIX: Hydrate from Firestore cloud (call after local hydrate)
   * Merges cloud threads with local - cloud wins for newer data
   * DO NOT REMOVE - without this, cross-device sync doesn't work
   */
  async hydrateFromCloud(): Promise<void> {
    if (this.isCloudHydrated) return;
    
    try {
      const cloudThreads = await cloudSync.fetchAllThreadsFromCloud();
      
      if (cloudThreads.size === 0) {
        console.log('[MessageStore] No cloud threads found');
        this.isCloudHydrated = true;
        return;
      }

      let merged = 0;
      let added = 0;

      for (const [key, cloudThread] of cloudThreads) {
        const localThread = this.threads.get(key);
        
        if (!localThread) {
          // Cloud thread doesn't exist locally - add it
          this.threads.set(key, cloudThread);
          storage.saveThread(key, cloudThread);
          added++;
        } else {
          // Both exist - merge messages (keep unique by ID)
          const localIds = new Set(localThread.messages.map(m => m.id));
          let hasNewMessages = false;
          
          for (const cloudMsg of cloudThread.messages) {
            if (!localIds.has(cloudMsg.id)) {
              localThread.messages.push(cloudMsg);
              hasNewMessages = true;
            }
          }
          
          // Update metadata if cloud is more recent
          if (cloudThread.metadata.closedAt && 
              (!localThread.metadata.closedAt || cloudThread.metadata.closedAt > localThread.metadata.closedAt)) {
            localThread.metadata = cloudThread.metadata;
            hasNewMessages = true;
          }
          
          if (hasNewMessages) {
            storage.saveThread(key, localThread);
            merged++;
          }
        }
      }

      this.isCloudHydrated = true;
      console.log(`[MessageStore] Cloud hydration complete: ${added} added, ${merged} merged`);
    } catch (error) {
      console.error('[MessageStore] Cloud hydration failed:', error);
      // Don't block on cloud failure - local data is still available
      this.isCloudHydrated = true;
    }
  }

  /** Check if store has been hydrated from IndexedDB */
  get hydrated(): boolean {
    return this.isHydrated;
  }

  /** Check if store has been hydrated from cloud */
  get cloudHydrated(): boolean {
    return this.isCloudHydrated;
  }

  getThread(context: MessageContextRef): MessageThread | null {
    const key = contextKey(context);
    return this.threads.get(key) ?? null;
  }

  getMessages(context: MessageContextRef): Message[] {
    const thread = this.getThread(context);
    if (!thread) return [];
    return [...thread.messages].sort((a, b) => b.createdAt - a.createdAt);
  }

  addMessage(
    msg: Omit<Message, 'id' | 'createdAt' | 'expiresAt'> & {
      id?: string;
      createdAt?: number;
    }
  ): Message {
    const now = Date.now();
    const key = contextKey(msg.context);
    const thread = this.threads.get(key);

    // Check if thread is closed or locked
    if (thread && (thread.metadata.status === 'closed' || thread.metadata.status === 'locked')) {
      throw new Error(`Cannot post to ${thread.metadata.status} thread (reason: ${thread.metadata.closedReason})`);
    }

    const id = msg.id ?? `msg_${now}_${Math.random().toString(36).slice(2)}`;
    const createdAt = msg.createdAt ?? now;

    let ttlMs = msg.ttlMs;
    if (!ttlMs && msg.context.type === 'liberty') {
      ttlMs = DEFAULT_LA_TTL_MS;
    }

    const expiresAt = ttlMs != null ? createdAt + ttlMs : undefined;

    const fullMsg: Message = {
      ...msg,
      id,
      createdAt,
      ttlMs,
      expiresAt,
    };

    if (!thread) {
      // Create new thread with active status
      const newThread: MessageThread = {
        context: fullMsg.context,
        messages: [fullMsg],
        metadata: {
          status: 'active',
        },
      };
      this.threads.set(key, newThread);
      // WSP M1: Persist to IndexedDB (DO NOT REMOVE)
      storage.saveThread(key, newThread);
      // WSP M2: Sync to Firestore (DO NOT REMOVE)
      cloudSync.syncThreadToCloud(key, newThread);
    } else {
      thread.messages.push(fullMsg);
      // WSP M1: Persist updated thread (DO NOT REMOVE)
      storage.saveThread(key, thread);
      // WSP M2: Sync to Firestore (DO NOT REMOVE)
      cloudSync.syncThreadToCloud(key, thread);
    }

    return fullMsg;
  }

  closeThread(context: MessageContextRef, reason: string): void {
    const key = contextKey(context);
    const thread = this.threads.get(key);
    if (thread) {
      thread.metadata = {
        status: 'closed',
        closedAt: Date.now(),
        closedReason: reason,
      };
      // WSP M1: Persist closed state (DO NOT REMOVE)
      storage.saveThread(key, thread);
      // WSP M2: Sync to Firestore (DO NOT REMOVE)
      cloudSync.syncThreadToCloud(key, thread);
    }
  }

  lockThread(context: MessageContextRef, reason: string): void {
    const key = contextKey(context);
    const thread = this.threads.get(key);
    if (thread) {
      thread.metadata = {
        status: 'locked',
        closedAt: Date.now(),
        closedReason: reason,
      };
      // WSP M1: Persist locked state (DO NOT REMOVE)
      storage.saveThread(key, thread);
      // WSP M2: Sync to Firestore (DO NOT REMOVE)
      cloudSync.syncThreadToCloud(key, thread);
    }
  }

  pruneExpired(now: number = Date.now()): void {
    for (const [key, thread] of this.threads.entries()) {
      const remaining = thread.messages.filter((m) => {
        if (m.expiresAt == null) return true;
        return m.expiresAt > now;
      });

      if (remaining.length === 0) {
        this.threads.delete(key);
        // WSP M1: Delete empty thread from IndexedDB (DO NOT REMOVE)
        storage.deleteThread(key);
        // WSP M2: Delete from Firestore (DO NOT REMOVE)
        cloudSync.deleteThreadFromCloud(key);
      } else if (remaining.length !== thread.messages.length) {
        thread.messages = remaining;
        // WSP M1: Persist pruned thread (DO NOT REMOVE)
        storage.saveThread(key, thread);
        // WSP M2: Sync pruned thread to Firestore (DO NOT REMOVE)
        cloudSync.syncThreadToCloud(key, thread);
      }
    }
  }
}

export const messageStore = new InMemoryMessageStore();
