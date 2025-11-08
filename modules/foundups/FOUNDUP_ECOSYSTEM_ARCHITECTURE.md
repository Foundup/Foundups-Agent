# GotJunk FoundUp Ecosystem - 3-App Architecture

## WSP 3 Compliance: Independent FoundUp Modules

Following WSP 3 domain organization, GotJunk should be **3 separate FoundUp PWAs** that share data but operate independently.

---

## FoundUp 1: `gotjunk` (Seller App - EXISTS)
**Current module**: `modules/foundups/gotjunk/`

**Purpose**: List and manage items you're selling

**Features**:
- Camera to photograph junk items
- Set price, description, status (Listed/Sold/Auction)
- View my listings gallery
- Edit/delete my items
- Map view showing where my items are visible to buyers
- Liberty Alert integration (easter egg)

**Default Screen**: Camera view → Capture items to sell

**User Flow**:
```
1. Open GotJunk Seller app
2. Take photo of couch
3. Set price ($50), description
4. Mark as "Listed"
5. Item appears on map for browsers
```

**Navigation**:
- Camera 📷
- My Listings 📦
- Map 🗺️ (shows my items)

---

## FoundUp 2: `gotjunk_browse` (Buyer/Browser App - NEW)
**New module**: `modules/foundups/gotjunk_browse/`

**Purpose**: Browse and discover junk items from sellers within 50km

**Features**:
- **DEFAULT SCREEN**: Tinder-style swipe interface
- Browse items from other sellers (geo-fenced 50km)
- Swipe RIGHT → Add to cart (opens gotjunk_cart app)
- Swipe LEFT → Skip item
- Nav buttons: < Previous | Next >
- Map view showing all nearby items
- Filter by price, distance, category

**Default Screen**: Swipe Gallery → Browse items from sellers

**User Flow**:
```
1. Open GotJunk Browse app (DEFAULT APP for shoppers)
2. See 15 nearby items in Tinder swipe view
3. Swipe RIGHT on couch → "Added to cart" → Deep link to gotjunk_cart
4. Swipe LEFT on chair → Skipped
5. Tap Map icon → See all items on map with thumbnails
```

**Navigation**:
- Browse (Swipe) 🏠 (default)
- Map 🗺️ (browse mode - shows all items)
- Cart 🛒 (deep links to gotjunk_cart app)

**Data Source**:
- Fetches items where `ownership='others'` from shared IndexedDB
- Filters by 50km geo-fence
- Excludes items with `status='skipped'` by current user

---

## FoundUp 3: `gotjunk_cart` (Shopping Cart App - NEW)
**New module**: `modules/foundups/gotjunk_cart/`

**Purpose**: Review and purchase items in shopping cart

**Features**:
- List view of items added from Browse app
- Show thumbnail, price, distance, seller info
- Actions:
  - Contact Seller (SMS/Email)
  - Place Bid (for auction items)
  - Remove from cart
- Total price calculator
- Map view showing cart items only

**Default Screen**: Cart List → Review items to buy

**User Flow**:
```
1. User swipes RIGHT in gotjunk_browse → Redirected to gotjunk_cart
2. See cart with 3 items ($50 couch, $20 lamp, $100 table)
3. Total: $170
4. Tap "Contact Seller" on couch → Opens SMS to seller
5. Tap "Remove" on lamp → Back to 2 items
6. Tap Map → See cart items on map
```

**Navigation**:
- Cart List 🛒 (default)
- Map 🗺️ (cart mode - shows cart items only)
- Back to Browse 🏠 (deep link to gotjunk_browse)

**Data Source**:
- Fetches items where `ownership='others'` AND `status='in_cart'` AND `userId='current_user'`
- Stores cart state in shared IndexedDB

---

## Shared Infrastructure

### IndexedDB Schema (Shared across all 3 apps)

**Database**: `gotjunk_db`

**Object Store**: `items`

```typescript
interface GotJunkItem {
  id: string;                    // Unique item ID
  blob: Blob;                    // Image/video blob
  url: string;                   // Blob URL
  latitude: number;              // GPS coordinates
  longitude: number;
  ownership: 'mine' | 'others';  // Who owns this item
  userId: string;                // Owner's user ID

  // For SELLERS (gotjunk app)
  status: 'draft' | 'listed' | 'sold' | 'auction'; // My item status
  price: number;                 // Selling price
  description: string;           // Item description

  // For BUYERS (gotjunk_browse/gotjunk_cart apps)
  browseStatus: 'browsing' | 'in_cart' | 'skipped'; // Buyer's action
  buyerId?: string;              // User who added to cart

  createdAt: number;             // Timestamp
  updatedAt: number;
}
```

### Deep Linking (Communication between apps)

**From gotjunk_browse → gotjunk_cart**:
```
Swipe RIGHT on item
→ Update item: browseStatus='in_cart', buyerId='user123'
→ Save to IndexedDB
→ window.location.href = '/gotjunk_cart?added=item-id-123'
```

**From gotjunk_cart → gotjunk_browse**:
```
Remove item from cart
→ Update item: browseStatus='browsing', buyerId=null
→ Save to IndexedDB
→ window.location.href = '/gotjunk_browse'
```

**From gotjunk → Map** (show my items):
```
User taps Map in Seller app
→ Open map filtered by ownership='mine'
```

**From gotjunk_browse → Map** (show all items):
```
User taps Map in Browse app
→ Open map showing all items where ownership='others' AND within 50km
```

---

## Module Structure (WSP 49 Compliance)

### modules/foundups/gotjunk/ (EXISTS - Seller App)
```
modules/foundups/gotjunk/
├── README.md           # Seller app documentation
├── INTERFACE.md        # Public API for deep linking
├── ModLog.md           # Change history
├── frontend/           # React PWA
│   ├── components/     # Camera, MyListings, MapView
│   ├── services/       # IndexedDB storage
│   └── App.tsx         # Main app (camera default screen)
├── backend/            # FastAPI (optional - for Liberty Alert)
└── requirements.txt
```

### modules/foundups/gotjunk_browse/ (NEW - Browse/Shopping App)
```
modules/foundups/gotjunk_browse/
├── README.md           # Browser app documentation
├── INTERFACE.md        # Public API for deep linking
├── ModLog.md           # Change history
├── frontend/           # React PWA
│   ├── components/     # SwipeGallery, BrowseMap, ItemCard
│   ├── services/       # IndexedDB storage (shared with gotjunk)
│   └── App.tsx         # Main app (swipe gallery default screen)
└── package.json
```

### modules/foundups/gotjunk_cart/ (NEW - Shopping Cart App)
```
modules/foundups/gotjunk_cart/
├── README.md           # Cart app documentation
├── INTERFACE.md        # Public API for deep linking
├── ModLog.md           # Change history
├── frontend/           # React PWA
│   ├── components/     # CartList, CartMap, ContactSeller
│   ├── services/       # IndexedDB storage (shared with gotjunk)
│   └── App.tsx         # Main app (cart list default screen)
└── package.json
```

---

## User Journeys

### Journey 1: Seller Lists Item
1. Open **gotjunk** (seller app)
2. Take photo with camera
3. Set price, description
4. Mark as "Listed"
5. Item saved to IndexedDB with `ownership='mine'`
6. Item appears on map for browsers

### Journey 2: Buyer Browses & Purchases
1. Open **gotjunk_browse** (browser app) ← **DEFAULT APP**
2. Swipe through 15 nearby items
3. Swipe RIGHT on couch → Redirected to **gotjunk_cart**
4. Review cart, tap "Contact Seller"
5. SMS opens to seller's number
6. Purchase completed offline

### Journey 3: Map Exploration
1. Open **gotjunk_browse** (browser app)
2. Tap Map icon
3. See all nearby items on map with thumbnails
4. Click green marker → See item photo, price
5. Swipe map to different area → Load more items
6. Tap item → Add to cart → Redirect to **gotjunk_cart**

---

## Implementation Priority

### Phase 1: Fix Current gotjunk App (Seller App)
1. Keep camera as default screen (correct for sellers)
2. Add bottom nav to map view
3. Add thumbnails on map markers
4. Rename "Gallery" to "My Listings"

### Phase 2: Create gotjunk_browse (Browser App)
1. Create new module: `modules/foundups/gotjunk_browse/`
2. Copy boilerplate from gotjunk
3. Replace camera with Swipe Gallery component
4. Implement Tinder swipe UI (use existing ItemReviewer as base)
5. Add deep link to gotjunk_cart on swipe right
6. Add map view showing all items

### Phase 3: Create gotjunk_cart (Cart App)
1. Create new module: `modules/foundups/gotjunk_cart/`
2. Create Cart List component
3. Implement Contact Seller (SMS/Email)
4. Add "Place Bid" for auction items
5. Add map view showing cart items only
6. Deep link back to gotjunk_browse

### Phase 4: IndexedDB Shared Storage
1. Update schema to support both ownership modes
2. Add buyerId and browseStatus fields
3. Implement cross-app data sync

---

## Benefits of 3-App Architecture

✅ **WSP 3 Compliance**: Each FoundUp is independent module
✅ **Clear separation of concerns**: Sell vs Browse vs Cart
✅ **Standalone apps**: Each PWA works independently
✅ **Easier testing**: Test seller flow vs buyer flow separately
✅ **Better UX**: Each app has focused default screen
✅ **Scalability**: Can add more FoundUps (e.g., gotjunk_auction, gotjunk_delivery)
✅ **Deep linking**: Apps communicate via URLs + shared IndexedDB

---

## Questions for User

1. Should we proceed with 3-app architecture, or keep everything in gotjunk app?
2. For now, should we focus on improving the current gotjunk (seller) app first?
3. Or should we create gotjunk_browse (browser) app next, since that's the primary use case?
4. Should the 3 apps have different domain names or shared URL with routes?
   - Option A: `gotjunk.app`, `browse.gotjunk.app`, `cart.gotjunk.app`
   - Option B: `gotjunk.app/sell`, `gotjunk.app/browse`, `gotjunk.app/cart`
