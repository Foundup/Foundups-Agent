/**
 * Cart Reservation Service - Multi-Device Cart Coordination
 * WSP 98: FoundUps Mesh-Native Architecture Protocol - Cart Timeout System
 *
 * Purpose: Coordinate cart reservations across multiple devices using Firestore
 * Pattern: Follows existing service structure (firebaseAuth, firestoreSync)
 *
 * Architecture:
 * - 5-minute reservation window when item added to cart
 * - Firestore sync for cross-device coordination
 * - Automatic expiration and return to browse feed
 *
 * Usage:
 * import { createCartReservation, isReservedByOthers } from './cartReservation';
 */

import { CapturedItem, CartReservation } from '../types';
import { getCurrentUserId } from './firebaseAuth';
import { updateCartReservation } from './firestoreSync';

// Cart reservation duration: 5 minutes (300000ms)
export const CART_RESERVATION_DURATION = 5 * 60 * 1000; // 300000ms

/**
 * Create a cart reservation for an item
 * @param itemId - The item ID to reserve
 * @returns CartReservation object with timestamps
 */
export const createCartReservation = (itemId: string): CartReservation | null => {
  const uid = getCurrentUserId();
  if (!uid) {
    console.warn('[CartReservation] Cannot create reservation - no auth user');
    return null;
  }

  const now = Date.now();
  const reservation: CartReservation = {
    reservedBy: uid,
    reservedAt: now,
    expiresAt: now + CART_RESERVATION_DURATION,
  };

  console.log('[CartReservation] Created reservation:', itemId, `expires in ${CART_RESERVATION_DURATION / 1000}s`);
  return reservation;
};

/**
 * Sync cart reservation to Firestore
 * @param itemId - The item ID
 * @param reservation - Reservation data (or null to clear)
 * @returns Promise<boolean> - true if sync successful
 */
export const syncReservationToFirestore = async (
  itemId: string,
  reservation: CartReservation | null
): Promise<boolean> => {
  return updateCartReservation(itemId, reservation);
};

/**
 * Check if an item is reserved by another user
 * @param item - The item to check
 * @param currentUid - Current user UID (optional, uses getCurrentUserId if not provided)
 * @returns boolean - true if reserved by someone else
 */
export const isReservedByOthers = (item: CapturedItem, currentUid?: string): boolean => {
  const uid = currentUid || getCurrentUserId();
  if (!uid || !item.cartReservation) return false;

  const now = Date.now();
  const { reservedBy, expiresAt } = item.cartReservation;

  // Check if reservation is still valid AND not by current user
  const isValid = expiresAt > now;
  const isByOthers = reservedBy !== uid;

  return isValid && isByOthers;
};

/**
 * Check if an item's reservation has expired
 * @param item - The item to check
 * @returns boolean - true if reservation exists and is expired
 */
export const isReservationExpired = (item: CapturedItem): boolean => {
  if (!item.cartReservation) return false;

  const now = Date.now();
  return item.cartReservation.expiresAt <= now;
};

/**
 * Get all expired cart items (for cleanup)
 * @param cartItems - Array of cart items
 * @returns Array of expired items
 */
export const getExpiredCartItems = (cartItems: CapturedItem[]): CapturedItem[] => {
  return cartItems.filter(isReservationExpired);
};

/**
 * Calculate time remaining for a reservation (in seconds)
 * @param item - The item with reservation
 * @returns number - Seconds remaining (0 if expired or no reservation)
 */
export const getReservationTimeRemaining = (item: CapturedItem): number => {
  if (!item.cartReservation) return 0;

  const now = Date.now();
  const remaining = item.cartReservation.expiresAt - now;

  return Math.max(0, Math.floor(remaining / 1000)); // Return seconds
};

/**
 * Filter browse feed to exclude items reserved by others
 * @param items - Array of items to filter
 * @param currentUid - Current user UID (optional)
 * @returns Filtered array excluding reserved items
 */
export const filterReservedItems = (items: CapturedItem[], currentUid?: string): CapturedItem[] => {
  return items.filter(item => !isReservedByOthers(item, currentUid));
};

/**
 * Format time remaining as MM:SS
 * @param seconds - Seconds remaining
 * @returns Formatted string "MM:SS"
 */
export const formatTimeRemaining = (seconds: number): string => {
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${mins}:${secs.toString().padStart(2, '0')}`;
};
