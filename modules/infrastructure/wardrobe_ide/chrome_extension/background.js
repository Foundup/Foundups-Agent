// Wardrobe Recorder - Background Service Worker
// Handles extension icon clicks and widget activation

// Listen for extension icon clicks
chrome.action.onClicked.addListener((tab) => {
  // Toggle widget in the active tab
  chrome.tabs.sendMessage(tab.id, {action: 'toggleWidget'}, (response) => {
    if (chrome.runtime.lastError) {
      console.error('[WARDROBE] Error sending message:', chrome.runtime.lastError);
    } else {
      console.log('[WARDROBE] Widget toggled:', response?.status);
    }
  });
});

// Listen for installation
chrome.runtime.onInstalled.addListener(() => {
  console.log('[WARDROBE] Extension installed successfully');
  console.log('[WARDROBE] Click the extension icon on any page to start recording');
});

console.log('[WARDROBE] Background service worker initialized');
