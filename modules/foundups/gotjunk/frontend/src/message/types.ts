export type MessageContextType = 'item' | 'liberty';

export interface MessageContextRef {
  type: MessageContextType;
  itemId?: string;
  alertId?: string; // Canonical ID: geohash + alert type for Liberty Alerts
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

// Thread status lifecycle
export type ThreadStatus = 'active' | 'closed' | 'locked';

export interface ThreadMetadata {
  status: ThreadStatus;
  closedAt?: number; // Timestamp when thread was closed/locked
  closedReason?: string; // "sold", "picked-up", "alert-expired", "manual-resolution"
}

export interface MessageThread {
  context: MessageContextRef;
  messages: Message[];
  metadata: ThreadMetadata; // Thread lifecycle state
}
