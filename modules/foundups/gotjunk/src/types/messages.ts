// modules/foundups/gotjunk/src/types/messages.ts
// WSP-3 Message Board – Sprint MB-1
// Pure types only, no UI, no networking

export type MessageContextType = 'item' | 'liberty';

export interface MessageContextRef {
  type: MessageContextType;
  // For generic GotJunk item chat
  itemId?: string;
  // For Liberty Alert chat
  alertId?: string;
}

export interface BaseMessage {
  id: string;
  context: MessageContextRef;
  authorId: string;             // future: tie to user identity / trust level
  authorDisplayName?: string;
  text: string;
  createdAt: number;            // timestamp in ms
}

export interface EphemeralMeta {
  ttlMs?: number;               // time-to-live in ms
  expiresAt?: number;           // absolute expiry timestamp
}

export interface Message extends BaseMessage, EphemeralMeta {
  // FUTURE SECURITY HOOKS (documented, NOT implemented here):
  // encryptedPayload?: string;
  // signature?: string;
  // publicKeyId?: string;
}

export interface MessageThread {
  context: MessageContextRef;
  messages: Message[];
}
