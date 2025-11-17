import { Message, MessageContextRef, MessageThread, ThreadStatus } from "./types";

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
      this.threads.set(key, {
        context: fullMsg.context,
        messages: [fullMsg],
        metadata: {
          status: 'active',
        },
      });
    } else {
      thread.messages.push(fullMsg);
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
      } else {
        thread.messages = remaining;
      }
    }
  }
}

export const messageStore = new InMemoryMessageStore();
