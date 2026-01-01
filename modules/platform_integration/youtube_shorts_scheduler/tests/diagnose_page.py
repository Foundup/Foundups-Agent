"""Quick diagnostic script to check page state."""
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import json

options = Options()
options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
driver = webdriver.Chrome(options=options)

print(f"URL: {driver.current_url}")
print(f"Title: {driver.title}")

# Check VIDEO_TABLE selector
video_table = driver.execute_script("""
    const table = document.querySelector("table[aria-label='Video list']");
    if (table) {
        return {exists: true, visible: table.offsetParent !== null};
    }
    // Try ytcp-video-list instead
    const videoList = document.querySelector('ytcp-video-list');
    if (videoList) {
        return {exists: false, ytcpVideoList: true};
    }
    return {exists: false, ytcpVideoList: false};
""")
print(f"\nVIDEO_TABLE selector: {video_table}")

# Check for filter input
filter_info = driver.execute_script("""
    const result = {
        filterInput: null,
        ytcpChips: [],
        url: window.location.href
    };

    // Filter input
    const filterInput = document.querySelector("input[placeholder='Filter']");
    if (filterInput) {
        result.filterInput = {
            visible: filterInput.offsetParent !== null,
            placeholder: filterInput.placeholder
        };
    }

    // ytcp-chip elements
    const chips = document.querySelectorAll('ytcp-chip');
    for (let chip of chips) {
        result.ytcpChips.push({
            text: chip.textContent.trim().substring(0, 30),
            visible: chip.offsetParent !== null
        });
    }

    // Check for UNLISTED in any element
    const allText = document.body.innerText;
    result.hasUnlisted = allText.includes('Unlisted');

    // Check for video rows
    const videoRows = document.querySelectorAll('ytcp-video-row');
    result.videoRowCount = videoRows.length;

    return result;
""")

print(f"\nFilter Input: {filter_info.get('filterInput')}")
print(f"ytcp-chips: {filter_info.get('ytcpChips')}")
print(f"Has 'Unlisted' text: {filter_info.get('hasUnlisted')}")
print(f"Video row count: {filter_info.get('videoRowCount')}")

# Check URL for filter param
url = driver.current_url
print(f"\nURL has filter param: {'filter=' in url}")
print(f"URL has UNLISTED: {'UNLISTED' in url.upper()}")

# The filter is working if URL has UNLISTED param - we just need to update chip detection
if 'UNLISTED' in url.upper():
    print("\n[SUCCESS] URL-based filter IS applied!")
    print("The chip detection just needs to be updated to recognize the filter is active.")
