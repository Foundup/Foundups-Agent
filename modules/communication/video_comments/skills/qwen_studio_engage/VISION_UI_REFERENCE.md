# YouTube Studio UI Reference (Vision AI)

**Created from screenshots:** 2025-12-03
**Purpose:** Precise Vision descriptions for UI element targeting

---

## Comment Action Bar Layout

**Every comment has this action bar (left to right):**

```
[Reply] [0 replies ▼] [👍] [👎] [♡] [⋮]
```

### 1. Reply Button
- **Type**: Text button
- **Label**: "Reply"
- **State**: Gray text, no icon
- **Vision Description**: "gray 'Reply' text button to the left of '0 replies'"

### 2. Replies Counter
- **Type**: Dropdown button
- **Label**: "0 replies" (or "1 reply", "5 replies")
- **State**: Gray text with dropdown arrow
- **Vision Description**: "replies counter showing '0 replies' with dropdown arrow"

### 3. Like Button (Thumbs Up)
- **Type**: Icon button
- **Icon**: 👍 thumbs up
- **States**:
  - **Not engaged**: Gray outline icon
  - **Engaged**: Filled icon with number "1" (or count)
- **Vision Descriptions**:
  - Click: "gray thumbs up icon button in comment action bar"
  - Verify: "thumbs up icon showing number next to it" (when engaged)

### 4. Dislike Button (Thumbs Down)
- **Type**: Icon button
- **Icon**: 👎 thumbs down
- **State**: Always gray (no public count shown)
- **Vision Description**: "gray thumbs down icon button"

### 5. Creator Heart Button ❤️
- **Type**: Icon button
- **Icon**: ♡ heart outline
- **States**:
  - **Not engaged**: Gray outline heart
  - **Engaged**: **RED filled heart** (distinct from like)
- **Vision Descriptions**:
  - Click: "gray outlined heart icon button in comment action bar"
  - Verify: "red filled heart icon" (when engaged)
- **Note**: This is creator-specific! Only channel owner can give creator hearts.

### 6. More Options (3-dot menu)
- **Type**: Icon button
- **Icon**: ⋮ vertical three dots
- **State**: Gray
- **Vision Description**: "vertical three-dot menu button"

---

## Reply Workflow UI Elements

### When "Reply" is Clicked:

**New elements appear below the comment:**

```
[Channel Avatar] [Reply text box with placeholder]
                              [Cancel] [Reply]
```

### Reply Text Box
- **Type**: Text input
- **Placeholder**: Usually empty or shows typing
- **Location**: Appears directly below comment after clicking Reply
- **Vision Descriptions**:
  - Click: "reply text input box below the comment"
  - Type: "text input field for replying to comment"

### Cancel Button
- **Type**: Text button
- **Label**: "Cancel"
- **Location**: Bottom right of reply box (left of Reply button)
- **Vision Description**: "gray 'Cancel' text button at bottom right of reply box"

### Submit Reply Button
- **Type**: Text button (or filled button when text entered)
- **Label**: "Reply"
- **Location**: Bottom right of reply box (right of Cancel)
- **States**:
  - **Disabled**: Gray (no text entered)
  - **Enabled**: Blue/highlighted (text entered)
- **Vision Description**: "blue 'Reply' submit button at bottom right of reply text box"

---

## Visual State Indicators

### Like Engaged
**Before:**
```
Reply  0 replies ▼  👍  👎  ♡  ⋮
```

**After:**
```
Reply  0 replies ▼  👍1  👎  ♡  ⋮
```
- Thumbs up now shows count "1"
- Icon may be slightly filled/highlighted

### Creator Heart Engaged
**Before:**
```
Reply  0 replies ▼  👍  👎  ♡  ⋮
```

**After:**
```
Reply  0 replies ▼  👍  👎  ❤️  ⋮
```
- Heart changes from gray outline to **RED filled**
- Very distinct visual change

### Both Engaged (from screenshot 2)
```
Reply  0 replies ▼  👍1  👎  ❤️  ⋮
```
- Both thumbs up (with count) AND red heart visible
- User can give both on same comment!

---

## Vision Targeting Strategies

### Strategy 1: Like Only
```python
# Target the thumbs up icon
await router.execute(
    'click_element',
    {
        'description': 'gray thumbs up icon in the comment action bar, located between the replies counter and thumbs down icon',
        'target': 'thumbs up like button',
        'context': 'YouTube Studio comments page',
        'visual_cues': 'gray thumbs up icon, part of horizontal action bar below comment text'
    },
    driver=DriverType.VISION
)
```

### Strategy 2: Creator Heart Only
```python
# Target the heart icon
await router.execute(
    'click_element',
    {
        'description': 'gray outlined heart icon in the comment action bar, located between thumbs down and three-dot menu',
        'target': 'creator heart button',
        'context': 'YouTube Studio comments page',
        'visual_cues': 'outlined heart icon, will turn red when clicked'
    },
    driver=DriverType.VISION
)
```

### Strategy 3: Reply Workflow

**Step 1: Open Reply**
```python
await router.execute(
    'click_element',
    {
        'description': 'gray Reply text button at the start of the comment action bar',
        'target': 'Reply button',
        'context': 'YouTube Studio comment',
        'visual_cues': 'text reads "Reply", leftmost button in action bar'
    },
    driver=DriverType.VISION
)
```

**Step 2: Type in Reply Box**
```python
await router.execute(
    'type_text',
    {
        'text': 'Thanks for your comment! 🎌',
        'description': 'reply text input box that appeared below the comment',
        'target': 'reply input field',
        'context': 'expanded reply area below comment',
    },
    driver=DriverType.VISION
)
```

**Step 3: Submit Reply**
```python
await router.execute(
    'click_element',
    {
        'description': 'blue Reply button at bottom right of reply text box, next to Cancel button',
        'target': 'submit reply button',
        'context': 'reply submission area',
        'visual_cues': 'blue button labeled "Reply", enabled when text is entered'
    },
    driver=DriverType.VISION
)
```

---

## Verification Patterns

### Verify Like Successful
**Check if thumbs up icon now shows a number:**
```python
# After clicking like, verify engagement
result = await router.execute(
    'check_element_state',
    {
        'description': 'thumbs up icon now showing a number next to it',
        'expected_state': 'has visible number like "1"',
    },
    driver=DriverType.VISION
)
```

### Verify Creator Heart Successful
**Check if heart icon is now RED:**
```python
# After clicking heart, verify it turned red
result = await router.execute(
    'check_element_state',
    {
        'description': 'heart icon is now filled and red colored',
        'expected_state': 'red filled heart instead of gray outline',
    },
    driver=DriverType.VISION
)
```

### Verify Reply Posted
**Check if reply box closed and reply appears:**
```python
# After submitting reply
result = await router.execute(
    'check_element_state',
    {
        'description': 'reply text box has closed and new reply appears below original comment',
        'expected_state': 'reply submission complete, text box gone',
    },
    driver=DriverType.VISION
)
```

---

## Common Edge Cases

### Already Liked
- Thumbs up icon will already show a count
- **Detection**: Look for number next to thumbs up
- **Action**: Skip like action, proceed to next step

### Already Hearted
- Heart icon will be RED instead of gray
- **Detection**: Look for red filled heart
- **Action**: Skip heart action, proceed to next step

### Already Replied
- Replies counter will show "1 reply" or more
- **Detection**: Check replies counter text
- **Action**: May skip or add additional reply

### No Comments in Inbox
- Empty state with message
- **Detection**: No comment elements visible
- **Action**: Exit gracefully, log "no comments to process"

---

## Screenshot References

**Screenshot 1**: Clean state (no engagement)
- All action bar icons are gray
- No counts shown
- Heart is outline only

**Screenshot 2**: After engagement
- Thumbs up shows "1" count
- Heart is RED (filled)
- Reply text box is open with text typed
- Both like AND heart can be active simultaneously

---

**Maintained By:** 0102 Vision Integration Team
**Last Updated:** 2025-12-03
**Based On:** Actual YouTube Studio UI screenshots from Move2Japan channel
