import { CapturedItem } from '../types';

/**
 * MeshDaemon - The Bridge between Local Data and the Mesh
 * WSP 98: FoundUps Mesh-Native Architecture
 *
 * STUB VERSION: Full mesh implementation coming in Phase 2
 * Currently logs intent but doesn't actually broadcast over mesh
 */
export class MeshDaemon {
  private static instance: MeshDaemon;
  private isRunning: boolean = false;

  private constructor() {
    console.log('[MeshDaemon] Stub initialized (full mesh coming in Phase 2)');
  }

  public static getInstance(): MeshDaemon {
    if (!MeshDaemon.instance) {
      MeshDaemon.instance = new MeshDaemon();
    }
    return MeshDaemon.instance;
  }

  public start(): void {
    if (this.isRunning) return;
    this.isRunning = true;
    console.log('[MeshDaemon] Stub service started');
  }

  public stop(): void {
    this.isRunning = false;
    console.log('[MeshDaemon] Stub service stopped');
  }

  /**
   * Broadcast a new GotJunk item to the mesh
   * STUB: Logs intent but doesn't actually broadcast
   */
  public broadcastItem(item: CapturedItem): void {
    console.log('[MeshDaemon] Would broadcast item (stub):', item.id);
    // Full mesh broadcasting coming in Phase 2
  }
}
