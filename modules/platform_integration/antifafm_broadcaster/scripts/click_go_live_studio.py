"""Click Go Live button on YouTube Studio livestreaming page."""
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

opts = Options()
opts.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
driver = webdriver.Chrome(options=opts)

print(f"[URL] {driver.current_url}")
print(f"[TITLE] {driver.title}")

# Look for buttons on the page
print("\n=== BUTTONS ON PAGE ===")
buttons = driver.execute_script("""
    const results = [];
    document.querySelectorAll('button, ytcp-button, [role="button"]').forEach(btn => {
        const text = (btn.textContent || '').trim();
        const label = btn.getAttribute('aria-label') || '';
        const id = btn.id || '';
        if (btn.offsetParent !== null && (text || label)) {
            results.push({
                tag: btn.tagName,
                text: text.substring(0, 50),
                label: label.substring(0, 50),
                id: id,
                disabled: btn.disabled || btn.getAttribute('disabled') !== null
            });
        }
    });
    return results;
""")

for btn in buttons[:20]:
    print(f"  {btn}")

# Try to click Go Live / Stream button
print("\n=== CLICKING GO LIVE ===")
click_result = driver.execute_script("""
    const buttons = document.querySelectorAll('button, ytcp-button, [role="button"]');
    for (const btn of buttons) {
        const text = (btn.textContent || '').toLowerCase().trim();
        const label = (btn.getAttribute('aria-label') || '').toLowerCase();

        // Look for: "go live", "stream", "start stream", "create stream"
        if (text.includes('go live') || text === 'stream' ||
            text.includes('start stream') || text.includes('create stream') ||
            label.includes('go live') || label.includes('stream')) {

            if (!btn.disabled && btn.offsetParent !== null) {
                btn.click();
                return {clicked: true, text: btn.textContent.trim().substring(0, 40)};
            }
        }
    }
    return {clicked: false};
""")
print(f"  Result: {click_result}")

if click_result.get('clicked'):
    time.sleep(2)
    print(f"\n[NEW URL] {driver.current_url}")
