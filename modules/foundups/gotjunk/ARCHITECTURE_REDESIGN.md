# GotJunk FoundUp - 3-Gallery Architecture Redesign

## Problem Statement
Current app shows camera as default screen, but users want to **browse nearby items first** (shopping experience), then optionally list their own items for sale.

## Solution: 3-Gallery System

### 1. Browse Gallery (DEFAULT SCREEN)
**Purpose**: Shopping experience - browse items from other users within 50km

**UI**:
- Tinder-style swipe cards showing items from OTHER users
- Swipe RIGHT → Add to Shopping Cart
- Swipe LEFT → Skip (mark as 'skipped')
- Nav buttons: `< Previous` | `Next >`
- Shows: Photo/video, price, distance, description

**Data**:
- Loads items where `ownership === 'others'` AND within 50km geo-fence
- Filters out `status === 'skipped'` items
- Sorts by distance (closest first)

**Flow**:
```
User opens app → Browse Gallery loads
→ Swipe right on couch → Added to Shopping Cart
→ Swipe left on chair → Skipped (won't show again)
→ Nav buttons to browse manually (< >)
```

---

### 2. My Items Gallery
**Purpose**: Manage items I'm selling

**UI**:
- Grid view of my listed items
- Camera FAB button (+) to add new items
- Each item shows: thumbnail, status badge (Listed/Sold/Auction), price
- Tap item → Edit details (price, description, status)
- Delete button

**Data**:
- Shows items where `ownership === 'mine'`
- Statuses: `draft`, `listed`, `sold`, `auction`

**Flow**:
```
Camera button → Take photo of couch
→ Set price ($50), description ("Blue couch, good condition")
→ Status: Listed
→ Appears on map for other users to browse
```

---

### 3. Shopping Cart Gallery
**Purpose**: Final review of items I want to buy/bid

**UI**:
- List view of items I swiped right
- Shows: thumbnail, price, distance, seller info
- Actions: Contact Seller | Place Bid | Remove from Cart
- Total price calculator (if buying multiple items)

**Data**:
- Shows items where `ownership === 'others'` AND `status === 'in_cart'`

**Flow**:
```
Review cart → Contact seller for couch
→ Place bid on auction chair
→ Remove lamp (changed mind)
```

---

## Map View Improvements

### Current Issues:
- ❌ No bottom nav bar visible
- ❌ No item thumbnails on markers
- ❌ Doesn't distinguish between my items vs cart items

### Fixes:
1. **Bottom Nav Bar**: Always visible in map view
2. **Marker Colors**:
   - 🟢 Green: Available items (others' items or my cart)
   - 🔴 Red: Sold items
   - 🟨 Gold: Auction items
   - 🔵 Blue: My listed items
3. **Marker Popups**: Show thumbnail image when clicked
4. **Filter Toggles**:
   - "Show My Items" checkbox
   - "Show Cart Items" checkbox
   - "Show All Nearby" checkbox

---

## State Management

### App.tsx State:
```typescript
const [myItems, setMyItems] = useState<CapturedItem[]>([]); // ownership='mine'
const [browseItems, setBrowseItems] = useState<CapturedItem[]>([]); // ownership='others', status!=='skipped'
const [cartItems, setCartItems] = useState<CapturedItem[]>([]); // ownership='others', status='in_cart'
const [currentView, setCurrentView] = useState<'browse' | 'my_items' | 'cart' | 'map'>('browse'); // DEFAULT: browse
```

### Data Flow:
1. **App Load**:
   - Fetch ALL items from IndexedDB
   - Filter by geo-fence (50km)
   - Separate into `myItems` (ownership='mine') and `browseItems` (ownership='others')
   - Extract `cartItems` from browseItems where status='in_cart'

2. **Camera Capture**:
   - Create new item with `ownership='mine'`, `status='draft'`
   - Add to `myItems` array
   - Save to IndexedDB
   - Show in My Items Gallery

3. **Swipe Right** (in Browse Gallery):
   - Update item `status='in_cart'`
   - Move from `browseItems` to `cartItems`
   - Save to IndexedDB

4. **Swipe Left** (in Browse Gallery):
   - Update item `status='skipped'`
   - Remove from `browseItems` (filtered out)
   - Save to IndexedDB

---

## Bottom Nav Bar Icons

```
[🏠 Browse] [🛒 Cart (badge)] [📦 My Items] [🗺️ Map]
```

**Badge**: Show count on Cart icon when items in cart

---

## Implementation Order

1. ✅ Update `types.ts` with new ItemStatus, ItemOwnership
2. ⏳ Create `BrowseGallery.tsx` component (Tinder swipe for shopping)
3. ⏳ Create `ShoppingCart.tsx` component (cart review)
4. ⏳ Update `BottomNavBar.tsx` to support 4 views + cart badge
5. ⏳ Update `App.tsx` state management (3 arrays: myItems, browseItems, cartItems)
6. ⏳ Update `PigeonMapView.tsx` to:
   - Show bottom nav bar
   - Add thumbnail popups on markers
   - Color-code markers by ownership/status
7. ⏳ Update `FullscreenGallery.tsx` to show "My Items" only
8. ⏳ Add mock data generator for testing (create 10-20 "others" items nearby)

---

## Testing Scenario

1. **User opens app** → See Browse Gallery with 15 nearby items
2. **Swipe right on 3 items** → Cart badge shows "3"
3. **Tap Cart icon** → See Shopping Cart with 3 items
4. **Tap "My Items"** → Empty (no items listed yet)
5. **Tap Camera (+) in My Items** → Take photo of couch
6. **Set price $50, description** → Mark as "Listed"
7. **Tap Map** → See:
   - Blue marker (my couch)
   - Green markers (3 cart items)
   - Green markers (12 browseable items)
8. **Click green marker** → See thumbnail popup with price
9. **Bottom nav visible** → Can switch views from map

---

## Key Improvements

✅ **Default screen**: Browse Gallery (shopping experience, not camera)
✅ **3 distinct galleries**: Browse, My Items, Shopping Cart
✅ **Map enhancements**: Bottom nav, thumbnails, color-coded markers
✅ **Tinder UX preserved**: Swipe right (add to cart) / left (skip)
✅ **Clear ownership**: My items vs Others' items
✅ **Shopping cart**: Review before contacting sellers
✅ **Geo-fencing**: Only show items within 50km

---

## Questions for User

1. Should Browse Gallery auto-advance after swipe, or stay on same item until manual nav?
2. Should "Contact Seller" open SMS, email, or in-app chat?
3. Should auction items have bid timer/countdown?
4. Should map show item thumbnails directly on markers, or only in popup?
