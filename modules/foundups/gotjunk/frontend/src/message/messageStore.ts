import { Message, MessageContextRef, MessageThread } from "./types";

export interface MessageStore {
  getThread(context: MessageContextRef): MessageThread | null;
  getMessages(context: MessageContextRef): Message[];
  addMessage(
    msg: Omit<Message, 'id' | 'createdAt' | 'expiresAt'> & {
      id?: string;
      createdAt?: number;
    }
  ): Message;
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

    const key = contextKey(fullMsg.context);
    const thread = this.threads.get(key);

    if (!thread) {
      this.threads.set(key, {
        context: fullMsg.context,
        messages: [fullMsg],
      });
    } else {
      thread.messages.push(fullMsg);
    }

    return fullMsg;
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
