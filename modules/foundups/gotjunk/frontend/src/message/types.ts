export type MessageContextType = 'item' | 'liberty';

export interface MessageContextRef {
  type: MessageContextType;
  itemId?: string;
  alertId?: string;
}

export interface BaseMessage {
  id: string;
  context: MessageContextRef;
  authorId: string;
  authorDisplayName?: string;
  text: string;
  createdAt: number;
}

export interface EphemeralMeta {
  ttlMs?: number;
  expiresAt?: number;
}

export interface Message extends BaseMessage, EphemeralMeta {}

export interface MessageThread {
  context: MessageContextRef;
  messages: Message[];
}
