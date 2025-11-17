# Message Board Architecture

## MB-1: Core Store (Complete)
- `messageStore.ts`: In-memory store with TTL + context keys
- Context types: `item` threads (itemId) and `liberty` threads (alertId)
- Default TTL: 15 minutes for Liberty messages, persistent for GotJunk items
- `Message`, `MessageThread` types defined in `types/messages.ts`

## MB-2: UI Wiring (Complete)
- PhotoCard `+` opens fullscreen; ItemReviewer `MessageBoardIcon` toggles `MessageThreadPanel`
- `MessageThreadPanel.tsx`: bottom drawer showing newest message on top
- Local send box writes to `messageStore` (Occam PoC, no backend yet)
- Panel metadata shows classification + price/discount info
- Panel triggered from browse, my items, and cart ItemReviewers
- Keyboard accessibility: Escape to close, Enter to send
- Auto-scroll to newest message

## MB-2.5: Thread Lifecycle Management (Complete)

### Messages vs Threads
- **Individual messages** expire per TTL (15min for Liberty, none for items)
- **Thread container** persists as long as item/alert exists
- Thread status: `'active'` | `'closed'` | `'locked'`

### Closed Threads (GotJunk Items Sold/Picked-Up)
- **Status**: `'closed'`
- **UI**: "🔒 SOLD / READ-ONLY" banner with reason
- **Behavior**: No new posts allowed, history visible until item rolls out
- **API**: `messageStore.closeThread(context, reason)`
- **Example**: Item sold → thread shows banner, input disabled

### Locked Threads (Liberty Alerts Expired)
- **Status**: `'locked'`
- **UI**: "🔒 LOCKED" banner with reason
- **Behavior**: No new posts, existing messages kept for TTL window
- **API**: `messageStore.lockThread(context, reason)`
- **Example**: Alert timer expires → thread locks, messages expire after 15min

### Geo-Fencing (Liberty Alerts)
- **Canonical alertId**: geohash (5-char, ~5km bucket) + alert type
- **Example**: `"u8g2b-ice"` (Donetsk, Ukraine + ICE alert)
- **Behavior**: All captures in same geo bucket attach to same thread
- **Geohash Utility**: `generateLibertyAlertId(lat, lon, type, precision=5)`
- **Precision Levels**:
  - 4 chars: ~20km x 20km (city-level)
  - 5 chars: ~5km x 5km (neighborhood-level, default)
  - 6 chars: ~1km x 1km (block-level)

### Error Handling
- `addMessage()` throws error if thread is closed/locked
- MessageThreadPanel catches error and displays in UI
- Input field disabled when thread is read-only

## Usage
1. Double-tap or `+` to open fullscreen item
2. Tap chat icon → `MessageThreadPanel` slides up
3. Messages stored via `messageStore.addMessage` (throws error if thread closed/locked)
4. Latest messages pinned at top, input at bottom
5. Sold items show read-only banner, block new posts
6. Liberty Alerts auto-expire → thread locks → messages TTL out

## Roadmap
- MB-3: Mesh packet transport (BLE/WebRTC)
- MB-4: Waze-style threaded replies (comment-on-comment)
- MB-5: Trust tiers + encrypted delivery
