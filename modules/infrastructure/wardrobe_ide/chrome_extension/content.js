// Wardrobe Recorder - Content Script
// Injects recording widget into any webpage

// Listen for messages from background script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'toggleWidget') {
    toggleWardrobeWidget();
    sendResponse({status: 'toggled'});
  }
});

// Toggle widget visibility
function toggleWardrobeWidget() {
  const existing = document.getElementById('wardrobe-widget');
  if (existing) {
    existing.remove();
    return;
  }

  injectWardrobeWidget();
}

// Inject the recording widget
function injectWardrobeWidget() {
  // Check if already exists
  if (document.getElementById('wardrobe-widget')) {
    return;
  }

  // Create widget container
  const widget = document.createElement('div');
  widget.id = 'wardrobe-widget';
  widget.style.cssText = `
    position: fixed;
    top: 20px;
    right: 20px;
    z-index: 2147483647;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 20px;
    border-radius: 12px;
    box-shadow: 0 8px 32px rgba(0,0,0,0.3);
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    min-width: 300px;
    pointer-events: auto;
  `;

  // Title
  const title = document.createElement('div');
  title.style.cssText = 'font-size: 16px; font-weight: bold; margin-bottom: 12px; display: flex; justify-content: space-between; align-items: center;';
  title.innerHTML = `
    <span>WARDROBE RECORDER</span>
    <span id="wardrobe-close" style="cursor: pointer; font-size: 20px;">&times;</span>
  `;
  widget.appendChild(title);

  // Close button handler
  setTimeout(() => {
    document.getElementById('wardrobe-close').onclick = () => widget.remove();
  }, 0);

  // Status and timer
  const statusContainer = document.createElement('div');
  statusContainer.style.cssText = 'margin-bottom: 12px;';

  const status = document.createElement('div');
  status.id = 'wardrobe-status';
  status.style.cssText = 'font-size: 14px; opacity: 0.9;';
  status.textContent = 'Ready to record';
  statusContainer.appendChild(status);

  const timer = document.createElement('div');
  timer.id = 'wardrobe-timer';
  timer.style.cssText = 'font-size: 18px; font-weight: bold; opacity: 1; display: none; margin-top: 8px; color: #fff; text-shadow: 0 0 10px rgba(255,255,255,0.5);';
  timer.textContent = 'Recording: 00:00';
  statusContainer.appendChild(timer);

  widget.appendChild(statusContainer);

  // Input: Skill Name (required)
  const nameLabel = document.createElement('div');
  nameLabel.style.cssText = 'font-size: 12px; margin-bottom: 4px; opacity: 0.9;';
  nameLabel.textContent = 'Skill Name (required):';
  widget.appendChild(nameLabel);

  const nameInput = document.createElement('input');
  nameInput.id = 'wardrobe-skill-name';
  nameInput.type = 'text';
  nameInput.placeholder = 'e.g., linkedin_reply_comment';

  // Auto-suggest skill name from page title
  const pageTitle = document.title.toLowerCase()
    .replace(/[^a-z0-9]+/g, '_')
    .replace(/^_+|_+$/g, '')
    .substring(0, 50);
  nameInput.value = pageTitle || 'skill_' + Date.now();

  nameInput.style.cssText = `
    width: 100%;
    padding: 8px;
    margin-bottom: 12px;
    border: 2px solid #48bb78;
    border-radius: 4px;
    font-size: 13px;
    box-sizing: border-box;
  `;
  widget.appendChild(nameInput);

  // Input: Tags (optional)
  const tagsLabel = document.createElement('div');
  tagsLabel.style.cssText = 'font-size: 12px; margin-bottom: 4px; opacity: 0.9;';
  tagsLabel.textContent = 'Tags (optional, comma-separated):';
  widget.appendChild(tagsLabel);

  const tagsInput = document.createElement('input');
  tagsInput.id = 'wardrobe-tags';
  tagsInput.type = 'text';
  tagsInput.placeholder = 'linkedin, comment, engagement';
  tagsInput.style.cssText = `
    width: 100%;
    padding: 8px;
    margin-bottom: 12px;
    border: none;
    border-radius: 4px;
    font-size: 13px;
    box-sizing: border-box;
  `;
  widget.appendChild(tagsInput);

  // Input: Notes (optional)
  const notesLabel = document.createElement('div');
  notesLabel.style.cssText = 'font-size: 12px; margin-bottom: 4px; opacity: 0.9;';
  notesLabel.textContent = 'Notes (optional):';
  widget.appendChild(notesLabel);

  const notesInput = document.createElement('textarea');
  notesInput.id = 'wardrobe-notes';
  notesInput.placeholder = 'Describe what this skill does...';
  notesInput.rows = 2;
  notesInput.style.cssText = `
    width: 100%;
    padding: 8px;
    margin-bottom: 12px;
    border: none;
    border-radius: 4px;
    font-size: 13px;
    resize: vertical;
    box-sizing: border-box;
  `;
  widget.appendChild(notesInput);

  // START button
  const startBtn = document.createElement('button');
  startBtn.id = 'wardrobe-start';
  startBtn.style.cssText = `
    width: 100%;
    padding: 12px;
    background: #48bb78;
    color: white;
    border: none;
    border-radius: 6px;
    font-size: 14px;
    font-weight: bold;
    cursor: pointer;
    margin-bottom: 8px;
    pointer-events: auto;
  `;
  startBtn.textContent = '> START RECORDING';
  startBtn.onclick = startRecording;
  widget.appendChild(startBtn);

  // Button container for STOP and START OVER
  const buttonContainer = document.createElement('div');
  buttonContainer.style.cssText = 'display: none;';
  buttonContainer.id = 'wardrobe-button-container';

  // STOP button
  const stopBtn = document.createElement('button');
  stopBtn.id = 'wardrobe-stop';
  stopBtn.style.cssText = `
    width: 100%;
    padding: 12px;
    background: #48bb78;
    color: white;
    border: none;
    border-radius: 6px;
    font-size: 14px;
    font-weight: bold;
    cursor: pointer;
    margin-bottom: 8px;
    pointer-events: auto;
  `;
  stopBtn.textContent = '[OK] STOP & SAVE';
  stopBtn.onclick = stopRecording;
  buttonContainer.appendChild(stopBtn);

  // START OVER button
  const resetBtn = document.createElement('button');
  resetBtn.id = 'wardrobe-reset';
  resetBtn.style.cssText = `
    width: 100%;
    padding: 12px;
    background: #f56565;
    color: white;
    border: none;
    border-radius: 6px;
    font-size: 14px;
    font-weight: bold;
    cursor: pointer;
    pointer-events: auto;
  `;
  resetBtn.textContent = '[X] START OVER';
  resetBtn.onclick = resetRecording;
  buttonContainer.appendChild(resetBtn);

  widget.appendChild(buttonContainer);

  // Step counter
  const counter = document.createElement('div');
  counter.id = 'wardrobe-counter';
  counter.style.cssText = 'font-size: 12px; margin-top: 8px; opacity: 0.8; display: none;';
  counter.innerHTML = 'Steps: <span id="step-count">0</span>';
  widget.appendChild(counter);

  // Action log
  const actionLog = document.createElement('div');
  actionLog.id = 'wardrobe-action-log';
  actionLog.style.cssText = `
    font-size: 11px;
    margin-top: 8px;
    padding: 8px;
    background: rgba(0,0,0,0.2);
    border-radius: 4px;
    max-height: 60px;
    overflow-y: auto;
    display: none;
  `;
  actionLog.textContent = 'No actions yet...';
  widget.appendChild(actionLog);

  // Add CSS animations
  const style = document.createElement('style');
  style.textContent = `
    @keyframes pulse {
      0%, 100% { opacity: 1; }
      50% { opacity: 0.5; }
    }
    @keyframes recording-pulse {
      0%, 100% {
        transform: scale(1);
        box-shadow: 0 8px 32px rgba(0,0,0,0.3), 0 0 0 0 rgba(252, 92, 125, 0.7);
      }
      50% {
        transform: scale(1.02);
        box-shadow: 0 8px 32px rgba(0,0,0,0.3), 0 0 0 10px rgba(252, 92, 125, 0);
      }
    }
  `;
  document.head.appendChild(style);

  document.body.appendChild(widget);

  // Initialize recording state
  window.__wardrobeState = {
    recording: false,
    steps: [],
    startTime: null,
    timerInterval: null,
    targetUrl: window.location.href
  };

  // Setup event listeners
  setupEventCapture();
}

// Start recording
function startRecording() {
  const nameInput = document.getElementById('wardrobe-skill-name');
  const skillName = nameInput.value.trim();

  if (!skillName) {
    alert('Please enter a skill name before starting');
    nameInput.focus();
    return;
  }

  // Start recording
  window.__wardrobeState.recording = true;
  window.__wardrobeState.startTime = Date.now();
  window.__wardrobeState.steps = [];

  // Update UI
  const status = document.getElementById('wardrobe-status');
  status.textContent = '[REC] RECORDING...';
  status.style.animation = 'pulse 1s infinite';

  // Show timer
  const timer = document.getElementById('wardrobe-timer');
  timer.style.display = 'block';

  // Start timer countdown
  window.__wardrobeState.timerInterval = setInterval(updateTimer, 1000);

  // Change widget background
  document.getElementById('wardrobe-widget').style.background = 'linear-gradient(135deg, #fc5c7d 0%, #6a82fb 100%)';
  document.getElementById('wardrobe-widget').style.animation = 'recording-pulse 2s infinite';

  // Hide start button, show stop/reset buttons
  document.getElementById('wardrobe-start').style.display = 'none';
  document.getElementById('wardrobe-button-container').style.display = 'block';
  document.getElementById('wardrobe-counter').style.display = 'block';
  document.getElementById('wardrobe-action-log').style.display = 'block';

  // Disable inputs during recording
  nameInput.disabled = true;
  document.getElementById('wardrobe-tags').disabled = true;
  document.getElementById('wardrobe-notes').disabled = true;

  console.log('[WARDROBE] Recording started for skill:', skillName);
}

// Update timer
function updateTimer() {
  if (!window.__wardrobeState.recording) return;

  const elapsed = Math.floor((Date.now() - window.__wardrobeState.startTime) / 1000);
  const minutes = String(Math.floor(elapsed / 60)).padStart(2, '0');
  const seconds = String(elapsed % 60).padStart(2, '0');

  document.getElementById('wardrobe-timer').textContent = `Recording: ${minutes}:${seconds}`;
}

// Stop recording
function stopRecording() {
  window.__wardrobeState.recording = false;

  // Stop timer
  if (window.__wardrobeState.timerInterval) {
    clearInterval(window.__wardrobeState.timerInterval);
  }

  // Get metadata
  const skillName = document.getElementById('wardrobe-skill-name').value.trim();
  const tags = document.getElementById('wardrobe-tags').value.split(',').map(t => t.trim()).filter(t => t);
  const notes = document.getElementById('wardrobe-notes').value.trim();

  // Create skill object
  const skill = {
    name: skillName,
    backend: 'chrome_extension',
    steps: window.__wardrobeState.steps,
    created_at: new Date().toISOString(),
    meta: {
      target_url: window.__wardrobeState.targetUrl,
      tags: tags,
      notes: notes,
      step_count: window.__wardrobeState.steps.length,
      recorded_with: 'wardrobe_chrome_extension'
    }
  };

  // Save to local storage
  chrome.storage.local.get(['skills'], (result) => {
    const skills = result.skills || [];
    skills.push(skill);
    chrome.storage.local.set({skills}, () => {
      console.log('[WARDROBE] Skill saved:', skillName);
    });
  });

  // Download as JSON file to Wardrobe skills store
  // NOTE: Chrome extensions can't write directly to O:\, so we save with instruction filename
  const blob = new Blob([JSON.stringify(skill, null, 2)], {type: 'application/json'});
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');

  // Filename includes path instruction for 0102
  const filename = `MOVE_TO_SKILLS_STORE__${skillName.replace(/[^a-z0-9]/gi, '_').toLowerCase()}.json`;
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);

  // Update UI - Change to GREEN for success
  const status = document.getElementById('wardrobe-status');
  status.textContent = `[OK] Saved ${window.__wardrobeState.steps.length} steps as "${skillName}"`;
  status.style.animation = '';

  document.getElementById('wardrobe-timer').style.display = 'none';
  document.getElementById('wardrobe-button-container').style.display = 'none';

  // SUCCESS STATE: Green background
  const widget = document.getElementById('wardrobe-widget');
  widget.style.background = 'linear-gradient(135deg, #48bb78 0%, #38a169 100%)';
  widget.style.animation = '';

  // After 3 seconds, fade back to purple (ready state)
  setTimeout(() => {
    widget.style.transition = 'background 1s ease';
    widget.style.background = 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';
    status.textContent = 'Ready to record';

    // Re-enable inputs and show start button
    document.getElementById('wardrobe-skill-name').disabled = false;
    document.getElementById('wardrobe-tags').disabled = false;
    document.getElementById('wardrobe-notes').disabled = false;
    document.getElementById('wardrobe-start').style.display = 'block';
    document.getElementById('wardrobe-counter').style.display = 'none';
    document.getElementById('wardrobe-action-log').style.display = 'none';
  }, 3000);

  console.log('[WARDROBE] Recording stopped. Steps:', window.__wardrobeState.steps.length);
}

// Reset recording (start over)
function resetRecording() {
  // Stop timer
  if (window.__wardrobeState.timerInterval) {
    clearInterval(window.__wardrobeState.timerInterval);
  }

  // Reset state
  window.__wardrobeState.recording = false;
  window.__wardrobeState.steps = [];
  window.__wardrobeState.startTime = null;

  // Update UI - back to ready state
  const status = document.getElementById('wardrobe-status');
  status.textContent = 'Ready to record';
  status.style.animation = '';

  const widget = document.getElementById('wardrobe-widget');
  widget.style.background = 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';
  widget.style.animation = '';

  // Hide timer and buttons
  document.getElementById('wardrobe-timer').style.display = 'none';
  document.getElementById('wardrobe-button-container').style.display = 'none';

  // Show start button
  document.getElementById('wardrobe-start').style.display = 'block';

  // Hide counter and action log
  document.getElementById('wardrobe-counter').style.display = 'none';
  document.getElementById('wardrobe-action-log').style.display = 'none';

  // Re-enable inputs
  document.getElementById('wardrobe-skill-name').disabled = false;
  document.getElementById('wardrobe-tags').disabled = false;
  document.getElementById('wardrobe-notes').disabled = false;

  // Reset counter
  document.getElementById('step-count').textContent = '0';

  console.log('[WARDROBE] Recording reset - ready to start over');
}

// Setup event capture
function setupEventCapture() {
  // Helper: Generate CSS selector (prioritize stable, specific selectors)
  function getSelector(element) {
    // Priority 1: ID (most specific)
    if (element.id && element.id.length > 0) {
      return '#' + element.id;
    }

    // Priority 2: aria-label (stable across sessions, descriptive)
    if (element.hasAttribute('aria-label')) {
      const label = element.getAttribute('aria-label');
      const tag = element.tagName.toLowerCase();
      // Include tag for specificity: button[aria-label="..."]
      return `${tag}[aria-label="${label}"]`;
    }

    // Priority 3: name attribute (common for inputs/buttons)
    if (element.hasAttribute('name') && element.name) {
      const tag = element.tagName.toLowerCase();
      return `${tag}[name="${element.name}"]`;
    }

    // Priority 4: data-* attributes (stable custom attributes)
    for (let attr of element.attributes) {
      if (attr.name.startsWith('data-') && attr.value) {
        const tag = element.tagName.toLowerCase();
        return `${tag}[${attr.name}="${attr.value}"]`;
      }
    }

    // Priority 5: type + tag (for inputs)
    if (element.hasAttribute('type')) {
      const tag = element.tagName.toLowerCase();
      const type = element.getAttribute('type');
      return `${tag}[type="${type}"]`;
    }

    // Priority 6: Tag + first stable class (avoid dynamic classes)
    let selector = element.tagName.toLowerCase();
    if (element.className && typeof element.className === 'string') {
      const classes = element.className.split(' ')
        .filter(c => c && c.length > 0 && !c.match(/^(ng-|mdc-|mat-)/)); // Skip framework classes
      if (classes.length > 0) {
        selector += '.' + classes[0]; // Use first stable class only
      }
    }

    // Last resort: just tag (will likely need manual editing)
    return selector;
  }

  // Capture clicks
  document.addEventListener('click', (e) => {
    if (!window.__wardrobeState.recording) return;
    if (e.target.closest('#wardrobe-widget')) return; // Ignore widget clicks

    const selector = getSelector(e.target);
    const timestamp = (Date.now() - window.__wardrobeState.startTime) / 1000;

    const step = {
      action: 'click',
      selector: selector,
      timestamp: timestamp,
      target_tag: e.target.tagName,
      target_text: e.target.textContent?.substring(0, 50) || '',
      target_aria_label: e.target.getAttribute('aria-label') || ''
    };

    window.__wardrobeState.steps.push(step);

    // Update counter
    document.getElementById('step-count').textContent = window.__wardrobeState.steps.length;

    // Update action log
    const actionLog = document.getElementById('wardrobe-action-log');
    actionLog.textContent = `Last: click ${selector}`;

    console.log('[WARDROBE] Captured click:', selector);
  }, true);

  // Capture typing (debounced - only captures final value after user stops typing)
  const typingTimeouts = new Map();

  document.addEventListener('input', (e) => {
    if (!window.__wardrobeState.recording) return;
    if (e.target.closest('#wardrobe-widget')) return;

    if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
      const selector = getSelector(e.target);
      const element = e.target;

      // Clear previous timeout for this element
      if (typingTimeouts.has(element)) {
        clearTimeout(typingTimeouts.get(element));
      }

      // Set new timeout - only record after 1 second of no typing
      const timeout = setTimeout(() => {
        const timestamp = (Date.now() - window.__wardrobeState.startTime) / 1000;

        const step = {
          action: 'type',
          selector: selector,
          text: element.value,
          timestamp: timestamp
        };

        window.__wardrobeState.steps.push(step);

        // Update counter
        document.getElementById('step-count').textContent = window.__wardrobeState.steps.length;

        // Update action log
        const actionLog = document.getElementById('wardrobe-action-log');
        actionLog.textContent = `Last: type "${element.value.substring(0, 20)}..."`;

        console.log('[WARDROBE] Captured input:', selector, element.value);

        typingTimeouts.delete(element);
      }, 1000); // Wait 1 second after last keystroke

      typingTimeouts.set(element, timeout);
    }
  }, true);
}

console.log('[WARDROBE] Content script loaded. Click extension icon to activate.');
