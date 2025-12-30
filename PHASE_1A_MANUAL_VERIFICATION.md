# Sprint 1 Phase 1A: Manual DOM Coordinate Verification

## Context
Automated tests (Phase 1B) executed all 3 clicks successfully but account switch failed. This indicates DOM coordinates may need adjustment.

## Phase 1B Results
✅ Navigation to YouTube Studio working
✅ All 3 clicks executing (no errors)
✅ Training data recording (9 examples)
❌ Account switch not occurring (still on Move2Japan after clicks)

## Click Coordinates Attempted
```javascript
Step 1: Avatar Button → (378, 31) with ±8px variance
Step 2: Switch Menu → (299, 179) with ±8px variance
Step 3: UnDaoDu Account → (171, 168) with ±12px variance
```

## Manual Verification Steps

### 1. Open Chrome DevTools
1. Navigate to https://studio.youtube.com
2. Press F12 to open DevTools
3. Click Console tab

### 2. Verify Avatar Button
Run this in Console:
```javascript
// Get avatar button position
const avatar = document.querySelector('button[aria-label*="Account"], button[id*="avatar"], ytd-topbar-menu-button-renderer:last-child button');
if (avatar) {
    const rect = avatar.getBoundingClientRect();
    console.log('Avatar Button:');
    console.log('  Left:', rect.left, 'Top:', rect.top);
    console.log('  Width:', rect.width, 'Height:', rect.height);
    console.log('  Center X:', rect.left + rect.width/2);
    console.log('  Center Y:', rect.top + rect.height/2);
    avatar.style.outline = '3px solid red';
} else {
    console.log('Avatar button not found');
}
```

**Expected**: Avatar should have red outline
**Record**: Center X and Y coordinates

### 3. Click Avatar Manually
1. Click the avatar button (should have red outline)
2. Account menu should open

### 4. Verify "Switch Account" Menu Item
Run this in Console while menu is open:
```javascript
// Get switch account menu item
const switchItem = Array.from(document.querySelectorAll('a, button, tp-yt-paper-item'))
    .find(el => el.textContent.includes('Switch account') || el.textContent.includes('switch account'));

if (switchItem) {
    const rect = switchItem.getBoundingClientRect();
    console.log('Switch Account Item:');
    console.log('  Left:', rect.left, 'Top:', rect.top);
    console.log('  Width:', rect.width, 'Height:', rect.height);
    console.log('  Center X:', rect.left + rect.width/2);
    console.log('  Center Y:', rect.top + rect.height/2);
    switchItem.style.outline = '3px solid blue';
} else {
    console.log('Switch account item not found');
}
```

**Expected**: "Switch account" should have blue outline
**Record**: Center X and Y coordinates

### 5. Click "Switch Account" Manually
1. Click the "Switch account" item (blue outline)
2. Account list should open showing all 3 channels

### 6. Verify UnDaoDu Account Position
Run this in Console while account list is open:
```javascript
// Get all account items
const accounts = document.querySelectorAll('[role="menuitem"], ytd-account-item-renderer, tp-yt-paper-item');
console.log('Found', accounts.length, 'account items');

accounts.forEach((acc, idx) => {
    const rect = acc.getBoundingClientRect();
    const text = acc.textContent.trim().substring(0, 50);
    console.log(`Account ${idx}:`);
    console.log('  Text:', text);
    console.log('  Left:', rect.left, 'Top:', rect.top);
    console.log('  Center X:', rect.left + rect.width/2);
    console.log('  Center Y:', rect.top + rect.height/2);

    if (text.includes('UnDaoDu')) {
        acc.style.outline = '3px solid green';
        console.log('  ^^^ THIS IS UNDAODU');
    }
    if (text.includes('Move2Japan') || text.includes('MOVE2JAPAN')) {
        acc.style.outline = '3px solid yellow';
        console.log('  ^^^ THIS IS MOVE2JAPAN');
    }
    if (text.includes('FoundUps')) {
        acc.style.outline = '3px solid orange';
        console.log('  ^^^ THIS IS FOUNDUPS');
    }
});
```

**Expected**:
- Green outline on UnDaoDu
- Yellow outline on Move2Japan
- Orange outline on FoundUps (if visible)

**Record**: Center X and Y for each account

## Results to Provide

Fill in the verified coordinates:

```
Avatar Button:
  Current: (371, 28)
  Verified: (_____, _____)

Switch Account Menu:
  Current: (294, 184)
  Verified: (_____, _____)

UnDaoDu Account:
  Current: (178, 161)
  Verified: (_____, _____)

Move2Japan Account:
  Current: (178, 225)
  Verified: (_____, _____)

FoundUps Account:
  Current: (178, 289)
  Verified: (_____, _____)
```

## Next Steps After Verification

1. If coordinates differ significantly (>15px), update `youtube_studio.json`
2. Re-run Phase 1B automated test
3. If switch succeeds, proceed to Phase 1C (comment engagement integration)
4. If still failing, investigate UI changes or authentication state

## Notes

- All measurements should be done with browser at 100% zoom
- Window size should match typical usage (~1920x1080 or similar)
- Account menu must be logged into Move2Japan initially
- Screenshots of each step recommended for documentation
