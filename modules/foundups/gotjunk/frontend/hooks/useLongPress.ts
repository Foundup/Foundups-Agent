import { useCallback, useRef } from 'react';

interface UseLongPressOptions {
  onLongPress: (event: PointerEvent | TouchEvent | MouseEvent) => void;
  onTap?: (event: PointerEvent | TouchEvent | MouseEvent) => void;
  threshold?: number; // ms before long-press fires (default 450ms)
  moveThreshold?: number; // px movement to cancel long-press (default 10px)
}

interface UseLongPressReturn {
  onPointerDown: (event: React.PointerEvent) => void;
  onPointerUp: (event: React.PointerEvent) => void;
  onPointerMove: (event: React.PointerEvent) => void;
  onPointerCancel: (event: React.PointerEvent) => void;
  onTouchStart: (event: React.TouchEvent) => void;
  onTouchEnd: (event: React.TouchEvent) => void;
  onTouchMove: (event: React.TouchEvent) => void;
  onTouchCancel: (event: React.TouchEvent) => void;
  onMouseDown: (event: React.MouseEvent) => void;
  onMouseUp: (event: React.MouseEvent) => void;
  onMouseMove: (event: React.MouseEvent) => void;
  onMouseLeave: (event: React.MouseEvent) => void;
}

/**
 * useLongPress Hook
 *
 * Robust long-press detection with iOS Safari compatibility
 * - Uses Pointer Events with fallback to Touch/Mouse
 * - Threshold: 450ms (configurable)
 * - Cancels on movement > 10px (configurable)
 * - Prevents iOS context menu
 * - Haptic feedback on trigger
 * - Mutually exclusive tap/long-press
 */
export function useLongPress({
  onLongPress,
  onTap,
  threshold = 450,
  moveThreshold = 10,
}: UseLongPressOptions): UseLongPressReturn {
  const timerRef = useRef<number | null>(null);
  const longPressTriggeredRef = useRef(false);
  const startPosRef = useRef<{ x: number; y: number } | null>(null);
  const lastLongPressTimeRef = useRef<number>(0);

  const clear = useCallback(() => {
    if (timerRef.current) {
      clearTimeout(timerRef.current);
      timerRef.current = null;
    }
  }, []);

  const triggerLongPress = useCallback((event: PointerEvent | TouchEvent | MouseEvent) => {
    const now = Date.now();

    // Debounce: ignore if triggered within 800ms
    if (now - lastLongPressTimeRef.current < 800) {
      return;
    }

    longPressTriggeredRef.current = true;
    lastLongPressTimeRef.current = now;

    // Haptic feedback (iOS Safari)
    if (navigator.vibrate) {
      navigator.vibrate(10); // Light impact
    }

    onLongPress(event);
    clear();
  }, [onLongPress, clear]);

  const handleStart = useCallback((clientX: number, clientY: number, event: PointerEvent | TouchEvent | MouseEvent) => {
    // Prevent iOS context menu
    event.preventDefault();

    longPressTriggeredRef.current = false;
    startPosRef.current = { x: clientX, y: clientY };

    clear();
    timerRef.current = window.setTimeout(() => {
      triggerLongPress(event);
    }, threshold);
  }, [threshold, triggerLongPress, clear]);

  const handleMove = useCallback((clientX: number, clientY: number) => {
    if (!startPosRef.current) return;

    const deltaX = Math.abs(clientX - startPosRef.current.x);
    const deltaY = Math.abs(clientY - startPosRef.current.y);

    // Cancel if moved too much
    if (deltaX > moveThreshold || deltaY > moveThreshold) {
      clear();
    }
  }, [moveThreshold, clear]);

  const handleEnd = useCallback((event: PointerEvent | TouchEvent | MouseEvent) => {
    clear();

    // Fire tap only if long-press wasn't triggered
    if (!longPressTriggeredRef.current && onTap) {
      onTap(event);
    }

    startPosRef.current = null;
  }, [onTap, clear]);

  const handleCancel = useCallback(() => {
    clear();
    longPressTriggeredRef.current = false;
    startPosRef.current = null;
  }, [clear]);

  // Pointer Events (preferred)
  const onPointerDown = useCallback((event: React.PointerEvent) => {
    handleStart(event.clientX, event.clientY, event.nativeEvent);
  }, [handleStart]);

  const onPointerMove = useCallback((event: React.PointerEvent) => {
    handleMove(event.clientX, event.clientY);
  }, [handleMove]);

  const onPointerUp = useCallback((event: React.PointerEvent) => {
    handleEnd(event.nativeEvent);
  }, [handleEnd]);

  const onPointerCancel = useCallback((event: React.PointerEvent) => {
    handleCancel();
  }, [handleCancel]);

  // Touch Events (iOS fallback)
  const onTouchStart = useCallback((event: React.TouchEvent) => {
    const touch = event.touches[0];
    handleStart(touch.clientX, touch.clientY, event.nativeEvent);
  }, [handleStart]);

  const onTouchMove = useCallback((event: React.TouchEvent) => {
    const touch = event.touches[0];
    handleMove(touch.clientX, touch.clientY);
  }, [handleMove]);

  const onTouchEnd = useCallback((event: React.TouchEvent) => {
    handleEnd(event.nativeEvent);
  }, [handleEnd]);

  const onTouchCancel = useCallback((event: React.TouchEvent) => {
    handleCancel();
  }, [handleCancel]);

  // Mouse Events (desktop fallback)
  const onMouseDown = useCallback((event: React.MouseEvent) => {
    handleStart(event.clientX, event.clientY, event.nativeEvent);
  }, [handleStart]);

  const onMouseMove = useCallback((event: React.MouseEvent) => {
    handleMove(event.clientX, event.clientY);
  }, [handleMove]);

  const onMouseUp = useCallback((event: React.MouseEvent) => {
    handleEnd(event.nativeEvent);
  }, [handleEnd]);

  const onMouseLeave = useCallback((event: React.MouseEvent) => {
    handleCancel();
  }, [handleCancel]);

  return {
    onPointerDown,
    onPointerUp,
    onPointerMove,
    onPointerCancel,
    onTouchStart,
    onTouchEnd,
    onTouchMove,
    onTouchCancel,
    onMouseDown,
    onMouseUp,
    onMouseMove,
    onMouseLeave,
  };
}
