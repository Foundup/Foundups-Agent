import { MeshCore } from '../src/meshCore';
import { MeshPacket } from '../src/packet';

describe('MeshCore', () => {
  let meshCore: MeshCore;

  beforeEach(() => {
    meshCore = new MeshCore();
  });

  describe('peer management', () => {
    test('should add peer', () => {
      meshCore.addPeer('peer-1');
      expect(meshCore.listPeers()).toContain('peer-1');
    });

    test('should remove peer', () => {
      meshCore.addPeer('peer-1');
      meshCore.removePeer('peer-1');
      expect(meshCore.listPeers()).not.toContain('peer-1');
    });

    test('should list all peers', () => {
      meshCore.addPeer('peer-1');
      meshCore.addPeer('peer-2');
      const peers = meshCore.listPeers();
      expect(peers).toHaveLength(2);
      expect(peers).toContain('peer-1');
      expect(peers).toContain('peer-2');
    });
  });

  describe('online status', () => {
    test('should start offline', () => {
      expect(meshCore.isOnline).toBe(false);
    });

    test('should go online', () => {
      meshCore.goOnline();
      expect(meshCore.isOnline).toBe(true);
    });

    test('should go offline', () => {
      meshCore.goOnline();
      meshCore.goOffline();
      expect(meshCore.isOnline).toBe(false);
    });
  });

  describe('broadcast', () => {
    test('should accept packet', () => {
      const packet: MeshPacket = {
        id: 'test-uuid',
        type: 'alert',
        timestamp: Date.now(),
        payload: { message: 'test' }
      };
      
      expect(() => meshCore.broadcast(packet)).not.toThrow();
    });
  });

  describe('discoverPeers', () => {
    test('should return empty array initially', async () => {
      const peers = await meshCore.discoverPeers();
      expect(peers).toEqual([]);
    });
  });
});
