import { MeshPacket } from './packet';
import { MeshPeer } from './peer';

export class MeshCore {
  peers: Set<string> = new Set();
  isOnline: boolean = false;

  constructor() {
    this.peers = new Set();
    this.isOnline = false;
  }

  goOnline(): void {
    this.isOnline = true;
  }

  goOffline(): void {
    this.isOnline = false;
  }

  addPeer(peerId: string): void {
    this.peers.add(peerId);
  }

  removePeer(peerId: string): void {
    this.peers.delete(peerId);
  }

  listPeers(): string[] {
    return Array.from(this.peers);
  }

  broadcast(packet: MeshPacket): void {
    // Sprint 2 will implement BLE broadcast
    // Sprint 3 will implement emergency broadcast
    console.log('Broadcasting packet:', packet);
  }

  async discoverPeers(): Promise<string[]> {
    // Sprint 2 will implement BLE discovery
    // Sprint 3 will implement emergency peer discovery
    return [];
  }
}
