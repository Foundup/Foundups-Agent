"""Check stream page and click Go Live."""
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

opts = Options()
opts.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
driver = webdriver.Chrome(options=opts)

print(f"[URL] {driver.current_url}")

# Find buttons on livestreaming page
print("\n=== BUTTONS ===")
buttons = driver.execute_script("""
    const results = [];
    document.querySelectorAll('button, ytcp-button, [role="button"]').forEach(btn => {
        const text = (btn.textContent || '').trim();
        if (btn.offsetParent !== null && text) {
            results.push({text: text.substring(0, 50), tag: btn.tagName, disabled: btn.disabled});
        }
    });
    return results;
""")
for btn in buttons[:20]:
    print(f"  {btn}")

# Click GO LIVE button
print("\n=== CLICKING GO LIVE ===")
result = driver.execute_script("""
    const buttons = document.querySelectorAll('button, ytcp-button');
    for (const btn of buttons) {
        const text = (btn.textContent || '').toLowerCase().trim();
        if (text === 'go live' || text.includes('go live')) {
            if (!btn.disabled) {
                btn.click();
                return {clicked: true, text: btn.textContent.trim()};
            } else {
                return {clicked: false, reason: 'button is disabled', text: btn.textContent.trim()};
            }
        }
    }
    return {clicked: false, reason: 'button not found'};
""")
print(f"  {result}")

if result.get('clicked'):
    time.sleep(3)
    print(f"\n[NEW URL] {driver.current_url}")
