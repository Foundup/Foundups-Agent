
import { MeshCore } from '@mesh/core/src/meshCore';
import { MeshPacket } from '@mesh/core/src/packet';
import { CapturedItem } from '../types';

/**
 * MeshDaemon - The Bridge between Local Data and the Mesh
 * WSP 98: FoundUps Mesh-Native Architecture
 */
export class MeshDaemon {
  private static instance: MeshDaemon;
  private mesh: MeshCore;
  private isRunning: boolean = false;

  private constructor() {
    // Initialize with a random device ID (in prod, persist this in localStorage)
    const deviceId = localStorage.getItem('gotjunk_device_id') || crypto.randomUUID();
    localStorage.setItem('gotjunk_device_id', deviceId);
    
    this.mesh = new MeshCore(deviceId);
    this.setupPacketHandlers();
  }

  public static getInstance(): MeshDaemon {
    if (!MeshDaemon.instance) {
      MeshDaemon.instance = new MeshDaemon();
    }
    return MeshDaemon.instance;
  }

  public start(): void {
    if (this.isRunning) return;
    
    this.mesh.goOnline();
    this.isRunning = true;
    console.log('[MeshDaemon] Service started');
    
    // In MVP, we mock peer discovery
    this.mesh.addPeer('mock-peer-1');
  }

  public stop(): void {
    this.mesh.goOffline();
    this.isRunning = false;
    console.log('[MeshDaemon] Service stopped');
  }

  /**
   * Broadcast a new GotJunk item to the mesh
   */
  public broadcastItem(item: CapturedItem): void {
    if (!this.isRunning) {
      console.warn('[MeshDaemon] Cannot broadcast: Service not running');
      return;
    }

    console.log('[MeshDaemon] Broadcasting item:', item.id);
    
    this.mesh.createAndBroadcast('gotjunk.new_item', {
      id: item.id,
      status: item.status,
      lat: item.latitude,
      lng: item.longitude,
      // Note: We don't send the blob over mesh yet (too big)
      // We send metadata so peers know it exists
    });
  }

  private setupPacketHandlers(): void {
    this.mesh.setPacketHandler((packet: MeshPacket) => {
      console.log('[MeshDaemon] Received packet:', packet);
      
      switch (packet.type) {
        case 'gotjunk.new_item':
          this.handleNewItem(packet);
          break;
        case 'liberty.alert':
          this.handleLibertyAlert(packet);
          break;
        default:
          console.log('[MeshDaemon] Unknown packet type:', packet.type);
      }
    });
  }

  private handleNewItem(packet: MeshPacket): void {
    // TODO: Check if we have this item in IndexedDB
    // If not, mark it as "known remote item"
    console.log('[MeshDaemon] Saw remote item:', packet.payload.id);
  }

  private handleLibertyAlert(packet: MeshPacket): void {
    // High priority alert!
    console.warn('[MeshDaemon] LIBERTY ALERT RECEIVED:', packet.payload);
    // TODO: Trigger UI notification
  }
}

