# Message Board Architecture

## MB-1  ECore Store (Complete)
- `messageStore.ts`: In-memory store with TTL + context keys
- Context types: `item` threads (itemId) and `liberty` threads (alertId)
- Default TTL: 15 minutes for Liberty messages, persistent for GotJunk items
- `Message`, `MessageThread` types defined in `types/messages.ts`

## MB-2  EUI Wiring (Current)
- PhotoCard `+` opens fullscreen; ItemReviewer `MessageBoardIcon` toggles `MessageThreadPanel`
- `MessageThreadPanel.tsx`: bottom drawer showing newest message on top
- Local send box writes to `messageStore` (Occam PoC, no backend yet)
- Panel metadata shows classification + price/discount info
- Panel triggered from browse, my items, and cart ItemReviewers

## Usage
1. Double-tap or `+` to open fullscreen item
2. Tap chat icon ↁE`MessageThreadPanel` slides up
3. Messages stored via `messageStore.addMessage` using `MessageContextRef`
4. Latest messages pinned at top, input at bottom

## Roadmap
- MB-3: Mesh packet transport (BLE/WebRTC)
- MB-4: Waze-style threaded replies (comment-on-comment)
- MB-5: Trust tiers + encrypted delivery
