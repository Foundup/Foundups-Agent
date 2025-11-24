import { useState, useRef, useCallback } from 'react';

export interface SOSDetectorOptions {
    onSOSDetected: () => void;
    tapThreshold?: number; // ms to distinguish tap vs press (default 300ms)
    resetTimeout?: number; // ms to reset pattern (default 3000ms after last input)
}

export function useSOSDetector({
    onSOSDetected,
    tapThreshold = 300, // < 300ms = Dot (S), > 300ms = Dash (L)
    resetTimeout = 3000
}: SOSDetectorOptions) {
    // Use Ref for internal pattern state to avoid re-renders on every tap
    // We only expose patternLength for UI feedback
    const patternRef = useRef<string[]>([]);
    const [patternLength, setPatternLength] = useState(0);
    
    const startTimeRef = useRef<number>(0);
    // Use number type for browser compatibility (NodeJS.Timeout is for backend)
    const timeoutRef = useRef<number | null>(null);

    const handlePressStart = useCallback(() => {
        startTimeRef.current = Date.now();
        
        // Clear reset timeout while user is interacting
        if (timeoutRef.current) {
            clearTimeout(timeoutRef.current);
            timeoutRef.current = null;
        }
    }, []);

    const handlePressEnd = useCallback(() => {
        const duration = Date.now() - startTimeRef.current;
        
        // Ignore extremely short accidental touches (< 50ms)
        if (duration < 50) return;

        const type = duration < tapThreshold ? 'S' : 'L'; // Short (Dot) vs Long (Dash)
        
        // Update internal ref state
        const currentPattern = patternRef.current;
        const newPattern = [...currentPattern, type];
        
        // Keep only last 9 inputs (max length of SOS pattern)
        if (newPattern.length > 9) {
            newPattern.shift();
        }
        
        patternRef.current = newPattern;
        setPatternLength(newPattern.length); // Trigger re-render for visual feedback

        console.log('[SOS Detector] Pattern:', newPattern.join(' '));

        // Check for SOS: S S S L L L S S S
        const sequence = newPattern.join('');
        if (sequence === 'SSSLLLSSS') {
            console.log('🗽 SOS PATTERN CONFIRMED');
            onSOSDetected();
            // Reset after success
            patternRef.current = [];
            setPatternLength(0);
            return;
        }

        // Set timeout to reset pattern if user stops typing
        timeoutRef.current = window.setTimeout(() => {
            patternRef.current = [];
            setPatternLength(0);
            console.log('[SOS Detector] Pattern reset due to inactivity');
        }, resetTimeout);

    }, [tapThreshold, resetTimeout, onSOSDetected]);

    return {
        patternLength,
        handlers: {
            onPointerDown: handlePressStart,
            onPointerUp: handlePressEnd,
            onPointerLeave: handlePressEnd, // Handle finger sliding off
            // Touch fallback
            onTouchStart: handlePressStart,
            onTouchEnd: handlePressEnd,
            onMouseDown: handlePressStart,
            onMouseUp: handlePressEnd
        }
    };
}
