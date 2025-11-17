/**
 * Simple geohash implementation for Liberty Alert geo-fencing
 *
 * Precision levels:
 * - 4 chars: ~20km x 20km (city-level bucketing)
 * - 5 chars: ~5km x 5km (neighborhood-level)
 * - 6 chars: ~1km x 1km (block-level)
 */

const BASE32 = '0123456789bcdefghjkmnpqrstuvwxyz';

export function encodeGeohash(
  latitude: number,
  longitude: number,
  precision: number = 5
): string {
  let geohash = '';
  let even = true;
  let bit = 0;
  let ch = 0;

  let latMin = -90.0;
  let latMax = 90.0;
  let lonMin = -180.0;
  let lonMax = 180.0;

  while (geohash.length < precision) {
    if (even) {
      const mid = (lonMin + lonMax) / 2;
      if (longitude > mid) {
        ch |= (1 << (4 - bit));
        lonMin = mid;
      } else {
        lonMax = mid;
      }
    } else {
      const mid = (latMin + latMax) / 2;
      if (latitude > mid) {
        ch |= (1 << (4 - bit));
        latMin = mid;
      } else {
        latMax = mid;
      }
    }

    even = !even;

    if (bit < 4) {
      bit++;
    } else {
      geohash += BASE32[ch];
      bit = 0;
      ch = 0;
    }
  }

  return geohash;
}

/**
 * Generate canonical Liberty Alert ID from geohash + alert type
 *
 * Examples:
 * - encodeGeohash(48.0159, 37.8028, 5) + "-ice" => "u8g2b-ice" (Donetsk, Ukraine)
 * - encodeGeohash(31.5, 34.4, 5) + "-ice" => "sv94x-ice" (Gaza)
 */
export function generateLibertyAlertId(
  latitude: number,
  longitude: number,
  alertType: string,
  precision: number = 5
): string {
  const geohash = encodeGeohash(latitude, longitude, precision);
  return `${geohash}-${alertType}`;
}
