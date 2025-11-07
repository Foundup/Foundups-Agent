# ⚠️ CRITICAL: DO NOT REMOVE BottomNavBar.tsx ⚠️

This file contains the **CORE navigation and camera functionality** for GotJunk.

## What This Component Does

1. **Live Camera Preview** - Circular button with live video feed
2. **Photo/Video Capture** - Tap for photo, press & hold for video
3. **Swipe Navigation** - Left/right arrows for Tinder-style review
4. **Gallery Access** - Grid icon opens kept items gallery
5. **Map Access** - Map icon opens location view
6. **SOS Detection** - Liberty Alert easter egg (morse code on gallery icon)

## DO NOT:

- ❌ Delete this file
- ❌ Remove this component from App.tsx
- ❌ Replace with custom navigation
- ❌ Remove camera controls
- ❌ Remove swipe arrows

## If You Need to Add Navigation:

✅ **ADD** additional navigation ABOVE this component (e.g., top-right icons)
✅ **EXTEND** this component with new features
✅ Keep this component as the primary bottom nav bar

---

**Created**: 2025-11-03
**Reason**: Component was accidentally removed, causing app to lose all camera functionality
