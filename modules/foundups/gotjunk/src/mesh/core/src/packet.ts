export interface MeshPacket {
  id: string;                // uuid
  type: string;              // 'alert' | 'share' | 'sync' etc.
  timestamp: number;         // Date.now()
  payload: Record<string, any>;
}
