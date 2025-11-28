/**
 * CartCountdown Component - 5-Minute Cart Reservation Timer
 * WSP 98: FoundUps Mesh-Native Architecture Protocol - Cart Timeout System
 *
 * Purpose: Display countdown timer for cart reservations in fullscreen view
 * Pattern: Updates every second using useEffect interval
 *
 * Features:
 * - MM:SS format display
 * - Color changes: green (>3min) → yellow (1-3min) → red (<1min)
 * - Auto-hides when no reservation or expired
 */

import React, { useState, useEffect } from 'react';
import { CapturedItem } from '../types';
import { getReservationTimeRemaining, formatTimeRemaining } from '../services/cartReservation';

interface CartCountdownProps {
  item: CapturedItem;
  onExpired?: () => void; // Optional callback when timer expires
}

export const CartCountdown: React.FC<CartCountdownProps> = ({ item, onExpired }) => {
  const [secondsRemaining, setSecondsRemaining] = useState<number>(0);

  useEffect(() => {
    // Initial calculation
    const remaining = getReservationTimeRemaining(item);
    setSecondsRemaining(remaining);

    // Update every second
    const interval = setInterval(() => {
      const newRemaining = getReservationTimeRemaining(item);
      setSecondsRemaining(newRemaining);

      // Trigger expiration callback when timer hits 0
      if (newRemaining === 0 && remaining > 0) {
        onExpired?.();
      }
    }, 1000);

    return () => clearInterval(interval);
  }, [item, onExpired]);

  // Hide countdown if no reservation or already expired
  if (!item.cartReservation || secondsRemaining === 0) {
    return null;
  }

  // Color coding based on time remaining
  const getColor = (): string => {
    if (secondsRemaining > 180) return '#10b981'; // green (>3min)
    if (secondsRemaining > 60) return '#f59e0b'; // yellow (1-3min)
    return '#ef4444'; // red (<1min)
  };

  const timeDisplay = formatTimeRemaining(secondsRemaining);
  const color = getColor();

  return (
    <div
      style={{
        position: 'absolute',
        top: '20px',
        right: '20px',
        backgroundColor: 'rgba(0, 0, 0, 0.7)',
        color: color,
        padding: '8px 16px',
        borderRadius: '8px',
        fontSize: '18px',
        fontWeight: 'bold',
        fontFamily: 'monospace',
        zIndex: 1000,
        boxShadow: '0 2px 8px rgba(0, 0, 0, 0.3)',
      }}
    >
      {timeDisplay}
    </div>
  );
};
