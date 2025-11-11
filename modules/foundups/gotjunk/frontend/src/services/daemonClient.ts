/**
 * GotJunk DAEmon Client
 *
 * Browser-side action capture and event buffering for AI oversight.
 * Sends events to DAEmon server for pattern detection and intervention.
 *
 * Usage:
 *   const daemon = new GotJunkDAEmonClient(API_URL);
 *   daemon.captureAction('capture', { captureMode: 'photo', ... }, true);
 */

export type ActionType =
  | 'capture'
  | 'classify'
  | 'swipe'
  | 'toggle'
  | 'error'
  | 'navigation'
  | 'storage';

export interface ActionPayload {
  // Capture
  captureMode?: 'photo' | 'video';
  autoClassifyEnabled?: boolean;
  lastClassification?: { type: string; discountPercent?: number; bidDurationHours?: number } | null;
  durationMs?: number;

  // Classify
  mode?: 'manual' | 'auto';
  classification?: 'free' | 'discount' | 'bid';
  discountPercent?: number;
  bidDurationHours?: number;
  modalShown?: boolean;
  timeSinceCapture?: number;

  // Swipe
  tab?: 'browse' | 'myitems' | 'cart';
  direction?: 'left' | 'right';
  itemId?: string;
  itemOwnership?: 'mine' | 'others';
  itemClassification?: 'free' | 'discount' | 'bid';
  resultingStatus?: 'in_cart' | 'skipped' | 'listed' | 'deleted' | 'browsing';

  // Toggle
  toggle?: 'autoClassify' | 'captureMode' | 'liberty' | 'filter';
  from?: any;
  to?: any;
  triggeredBy?: 'user' | 'system';

  // Error
  source?: string;
  error?: string;
  stack?: string;
  context?: any;
  recoverable?: boolean;

  // Navigation
  fromTab?: string;
  toTab?: string;

  // Storage
  operation?: 'save' | 'update' | 'delete' | 'read';
  itemCount?: number;

  // Generic
  [key: string]: any;
}

export interface Event {
  type: ActionType;
  timestamp: number;
  sessionId: string;
  userId: string | null;
  payload: ActionPayload;
  success: boolean;
  error?: string;
}

export class GotJunkDAEmonClient {
  private eventBuffer: Event[] = [];
  private flushInterval: number = 10000; // 10 seconds
  private maxBufferSize: number = 100;
  private flushTimer?: number;
  private enabled: boolean = true;

  constructor(
    private apiUrl: string = '/api/daemon',
    private debugMode: boolean = true
  ) {
    this.startAutoFlush();
    this.log('[DAEmon] Client initialized', { apiUrl, debugMode });
  }

  /**
   * Capture a user action
   */
  captureAction(
    type: ActionType,
    payload: ActionPayload,
    success: boolean = true,
    error?: string
  ): void {
    if (!this.enabled) return;

    const event: Event = {
      type,
      timestamp: Date.now(),
      sessionId: this.getSessionId(),
      userId: this.getUserId(),
      payload,
      success,
      error
    };

    this.eventBuffer.push(event);
    this.log(`[DAEmon] ${type}`, { payload, success, error });

    // Flush immediately for errors or high-priority events
    if (!success || type === 'error') {
      this.flush();
    }

    // Flush if buffer is full
    if (this.eventBuffer.length >= this.maxBufferSize) {
      this.flush();
    }
  }

  /**
   * Batch send events to server
   */
  private async flush(): Promise<void> {
    if (this.eventBuffer.length === 0) return;

    const events = [...this.eventBuffer];
    this.eventBuffer = [];

    this.log('[DAEmon] Flushing events', { count: events.length });

    try {
      const response = await fetch(`${this.apiUrl}/events`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ events })
      });

      if (!response.ok) {
        throw new Error(`DAEmon server responded with ${response.status}`);
      }

      this.log('[DAEmon] Events sent successfully', { count: events.length });
    } catch (error) {
      console.error('[DAEmon] Flush failed:', error);

      // Re-add events to buffer (up to max size to avoid memory leak)
      const overflow = this.eventBuffer.length + events.length - this.maxBufferSize;
      if (overflow > 0) {
        // Drop oldest events if buffer would overflow
        this.eventBuffer = [...events.slice(overflow), ...this.eventBuffer];
        this.log('[DAEmon] Buffer overflow - dropped oldest events', { dropped: overflow });
      } else {
        this.eventBuffer.unshift(...events);
      }
    }
  }

  /**
   * Start automatic flushing timer
   */
  private startAutoFlush(): void {
    this.flushTimer = window.setInterval(() => this.flush(), this.flushInterval);
  }

  /**
   * Stop automatic flushing
   */
  stopAutoFlush(): void {
    if (this.flushTimer) {
      clearInterval(this.flushTimer);
      this.flushTimer = undefined;
    }
  }

  /**
   * Manually trigger flush
   */
  async forceFlush(): Promise<void> {
    await this.flush();
  }

  /**
   * Enable/disable event capture
   */
  setEnabled(enabled: boolean): void {
    this.enabled = enabled;
    this.log('[DAEmon] Enabled state changed', { enabled });
  }

  /**
   * Get current session ID (or create new one)
   */
  private getSessionId(): string {
    let sessionId = sessionStorage.getItem('gotjunk_session_id');

    if (!sessionId) {
      sessionId = this.generateSessionId();
      sessionStorage.setItem('gotjunk_session_id', sessionId);
      this.log('[DAEmon] New session created', { sessionId });
    }

    return sessionId;
  }

  /**
   * Get user ID if logged in
   */
  private getUserId(): string | null {
    return localStorage.getItem('gotjunk_user_id');
  }

  /**
   * Generate unique session ID
   */
  private generateSessionId(): string {
    return `session-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Debug logging
   */
  private log(message: string, data?: any): void {
    if (this.debugMode) {
      if (data) {
        console.log(message, data);
      } else {
        console.log(message);
      }
    }
  }

  /**
   * Get current buffer stats
   */
  getStats(): {
    bufferSize: number;
    sessionId: string;
    userId: string | null;
    enabled: boolean;
  } {
    return {
      bufferSize: this.eventBuffer.length,
      sessionId: this.getSessionId(),
      userId: this.getUserId(),
      enabled: this.enabled
    };
  }

  /**
   * Clear all buffered events (useful for testing)
   */
  clearBuffer(): void {
    this.eventBuffer = [];
    this.log('[DAEmon] Buffer cleared');
  }
}

// Export singleton instance for convenience
export const daemon = new GotJunkDAEmonClient(
  import.meta.env.VITE_DAEMON_API_URL || '/api/daemon',
  import.meta.env.DEV // Debug mode on in development
);
