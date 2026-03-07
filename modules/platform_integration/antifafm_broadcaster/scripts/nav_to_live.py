"""Simple navigation to YouTube Studio livestreaming."""
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

opts = Options()
opts.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
driver = webdriver.Chrome(options=opts)

print(f"[BEFORE] {driver.current_url}")

# Navigate directly to livestreaming page for antifaFM
live_url = "https://studio.youtube.com/channel/UCVSmg5aOhP4tnQ9KFUg97qA/livestreaming/stream"
print(f"[NAV] {live_url}")
driver.get(live_url)
time.sleep(3)

print(f"[AFTER] {driver.current_url}")
print(f"[TITLE] {driver.title}")
