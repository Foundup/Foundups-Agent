/**
 * IPFS Service using Helia (modern IPFS implementation)
 *
 * Purpose: Decentralized storage for GotJunk item photos/videos
 * Architecture: Helia + libp2p WebRTC for mesh networking
 */

import { createHelia } from 'helia';
import { unixfs } from '@helia/unixfs';
import { IDBBlockstore } from 'blockstore-idb';
import type { Helia } from 'helia';
import type { UnixFS } from '@helia/unixfs';

let heliaInstance: Helia | null = null;
let fs: UnixFS | null = null;

/**
 * Initialize Helia node (call once on app startup)
 */
export const initHelia = async (): Promise<void> => {
  if (heliaInstance) return;

  try {
    // Use IndexedDB for browser storage
    const blockstore = new IDBBlockstore('gotjunk-ipfs-blocks');
    await blockstore.open();

    // Create Helia instance with WebRTC for mesh networking
    heliaInstance = await createHelia({
      blockstore,
      // libp2p config for mesh networking
      libp2p: {
        addresses: {
          listen: [
            '/webrtc', // Enable WebRTC for P2P
          ]
        }
      }
    });

    // Initialize UnixFS (file system layer)
    fs = unixfs(heliaInstance);

    console.log('[IPFS] Helia node started:', heliaInstance.libp2p.peerId.toString());
  } catch (error) {
    console.error('[IPFS] Failed to initialize Helia:', error);
    throw error;
  }
};

/**
 * Upload item photo/video to IPFS
 * @returns IPFS CID (Content Identifier) - e.g., "bafybeigdyrzt5sfp7udm7hu76uh7y26nf3efuylqabf3oclgtqy55fbzdi"
 */
export const uploadToIPFS = async (blob: Blob): Promise<string> => {
  if (!fs) {
    await initHelia();
    if (!fs) throw new Error('Helia not initialized');
  }

  try {
    // Convert Blob to Uint8Array
    const arrayBuffer = await blob.arrayBuffer();
    const bytes = new Uint8Array(arrayBuffer);

    // Upload to IPFS (returns CID)
    const cid = await fs.addBytes(bytes);

    console.log('[IPFS] Uploaded file:', cid.toString());
    return cid.toString();
  } catch (error) {
    console.error('[IPFS] Upload failed:', error);
    throw error;
  }
};

/**
 * Download item photo/video from IPFS
 * @param cidString - IPFS CID from uploadToIPFS()
 * @returns Blob (can create URL with URL.createObjectURL)
 */
export const downloadFromIPFS = async (cidString: string): Promise<Blob> => {
  if (!fs) {
    await initHelia();
    if (!fs) throw new Error('Helia not initialized');
  }

  try {
    // Parse CID string
    const { CID } = await import('multiformats/cid');
    const cid = CID.parse(cidString);

    // Download from IPFS (try local first, then mesh peers, then global IPFS)
    const chunks: Uint8Array[] = [];
    for await (const chunk of fs.cat(cid)) {
      chunks.push(chunk);
    }

    // Combine chunks into single Blob
    const totalLength = chunks.reduce((acc, chunk) => acc + chunk.length, 0);
    const combined = new Uint8Array(totalLength);
    let offset = 0;
    for (const chunk of chunks) {
      combined.set(chunk, offset);
      offset += chunk.length;
    }

    console.log('[IPFS] Downloaded file:', cidString);
    return new Blob([combined]);
  } catch (error) {
    console.error('[IPFS] Download failed:', error);
    throw error;
  }
};

/**
 * Pin item to keep in local storage (earn storage rewards)
 */
export const pinItem = async (cidString: string): Promise<void> => {
  if (!heliaInstance) {
    await initHelia();
    if (!heliaInstance) throw new Error('Helia not initialized');
  }

  try {
    const { CID } = await import('multiformats/cid');
    const cid = CID.parse(cidString);

    await heliaInstance.pins.add(cid);
    console.log('[IPFS] Pinned:', cidString);
  } catch (error) {
    console.error('[IPFS] Pin failed:', error);
    throw error;
  }
};

/**
 * Get list of pinned items (for storage provider rewards)
 */
export const listPinnedItems = async (): Promise<string[]> => {
  if (!heliaInstance) {
    await initHelia();
    if (!heliaInstance) throw new Error('Helia not initialized');
  }

  const pinned: string[] = [];
  for await (const cid of heliaInstance.pins.ls()) {
    pinned.push(cid.toString());
  }
  return pinned;
};

/**
 * Get connected peer count (mesh network size)
 */
export const getPeerCount = (): number => {
  if (!heliaInstance) return 0;
  return heliaInstance.libp2p.getPeers().length;
};

/**
 * Cleanup on app shutdown
 */
export const stopHelia = async (): Promise<void> => {
  if (heliaInstance) {
    await heliaInstance.stop();
    heliaInstance = null;
    fs = null;
    console.log('[IPFS] Helia node stopped');
  }
};
