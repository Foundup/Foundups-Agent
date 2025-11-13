export interface MeshPeer {
  id: string;
  lastSeen: number;
  signalStrength?: number;   // future BLE/LoRa
}
