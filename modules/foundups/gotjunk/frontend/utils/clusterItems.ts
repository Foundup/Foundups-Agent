/**
 * Item Clustering Algorithm
 *
 * Groups items by location using simple distance-based clustering.
 * Items within CLUSTER_RADIUS (~100m) are grouped together.
 *
 * Algorithm:
 * 1. Sort items by latitude (for spatial locality)
 * 2. Iterate through items, assigning each to nearest cluster or creating new cluster
 * 3. Return array of clusters with center point and items
 */

import type { CapturedItem } from '../types';
import type { ItemCluster, ClusteredItem, ItemLocation } from '../components/MapClusterMarker';

// Cluster threshold: ~100m radius (0.001 degrees ≈ 111m at equator)
const CLUSTER_RADIUS = 0.001;

/**
 * Calculate distance between two lat/lon points (simple Euclidean for small distances)
 * For clustering, we don't need precise Haversine - fast approximation is fine
 */
function simpleDistance(lat1: number, lon1: number, lat2: number, lon2: number): number {
  const latDiff = lat1 - lat2;
  const lonDiff = lon1 - lon2;
  return Math.sqrt(latDiff * latDiff + lonDiff * lonDiff);
}

/**
 * Calculate center point of cluster (average lat/lon)
 */
function calculateCenter(items: ClusteredItem[]): ItemLocation {
  const sum = items.reduce(
    (acc, item) => ({
      latitude: acc.latitude + item.latitude,
      longitude: acc.longitude + item.longitude,
    }),
    { latitude: 0, longitude: 0 }
  );

  return {
    latitude: sum.latitude / items.length,
    longitude: sum.longitude / items.length,
  };
}

/**
 * Find nearest cluster for an item
 */
function findNearestCluster(
  item: ClusteredItem,
  clusters: ItemCluster[]
): ItemCluster | null {
  let nearestCluster: ItemCluster | null = null;
  let minDistance = CLUSTER_RADIUS;

  for (const cluster of clusters) {
    const distance = simpleDistance(
      item.latitude,
      item.longitude,
      cluster.location.latitude,
      cluster.location.longitude
    );

    if (distance < minDistance) {
      minDistance = distance;
      nearestCluster = cluster;
    }
  }

  return nearestCluster;
}

/**
 * Cluster items by location
 *
 * @param items - Array of CapturedItems with lat/lon
 * @returns Array of clusters with center point, items, and count
 */
export function clusterItemsByLocation(items: CapturedItem[]): ItemCluster[] {
  const clusters: ItemCluster[] = [];

  // Filter out items without valid lat/lon
  const validItems: ClusteredItem[] = items
    .filter((item) => typeof item.latitude === 'number' && typeof item.longitude === 'number')
    .map((item) => ({
      id: item.id,
      url: item.url,
      classification: item.classification || 'free',
      latitude: item.latitude!,
      longitude: item.longitude!,
    }));

  if (validItems.length === 0) {
    return [];
  }

  // Sort by latitude for spatial locality (improves clustering speed)
  validItems.sort((a, b) => a.latitude - b.latitude);

  // Assign each item to nearest cluster or create new cluster
  for (const item of validItems) {
    const nearestCluster = findNearestCluster(item, clusters);

    if (nearestCluster) {
      // Add to existing cluster
      nearestCluster.items.push(item);
      nearestCluster.count++;

      // Recalculate center point (moving average)
      nearestCluster.location = calculateCenter(nearestCluster.items);
    } else {
      // Create new cluster
      clusters.push({
        location: {
          latitude: item.latitude,
          longitude: item.longitude,
        },
        items: [item],
        count: 1,
      });
    }
  }

  console.log(`[GotJunk] Clustered ${validItems.length} items into ${clusters.length} clusters`);

  return clusters;
}

/**
 * Get all items within a cluster's radius
 * Used when user clicks a cluster marker to filter browse feed
 */
export function getItemsNearLocation(
  items: CapturedItem[],
  location: ItemLocation,
  radius: number = CLUSTER_RADIUS
): CapturedItem[] {
  return items.filter((item) => {
    if (typeof item.latitude !== 'number' || typeof item.longitude !== 'number') {
      return false;
    }

    const distance = simpleDistance(
      item.latitude,
      item.longitude,
      location.latitude,
      location.longitude
    );

    return distance <= radius;
  });
}

/**
 * Debug helper: Log cluster statistics
 */
export function logClusterStats(clusters: ItemCluster[]): void {
  console.log('[GotJunk] Cluster Statistics:');
  console.log(`  Total clusters: ${clusters.length}`);

  const itemCounts = clusters.map((c) => c.count);
  const minItems = Math.min(...itemCounts);
  const maxItems = Math.max(...itemCounts);
  const avgItems = (itemCounts.reduce((a, b) => a + b, 0) / clusters.length).toFixed(2);

  console.log(`  Items per cluster: min=${minItems}, max=${maxItems}, avg=${avgItems}`);

  // Show largest clusters
  const largestClusters = clusters
    .sort((a, b) => b.count - a.count)
    .slice(0, 5);

  console.log('  Largest clusters:');
  largestClusters.forEach((cluster, index) => {
    console.log(`    ${index + 1}. ${cluster.count} items at (${cluster.location.latitude.toFixed(4)}, ${cluster.location.longitude.toFixed(4)})`);
  });
}
