"""
Smoke: Visibility dialog -> schedule inputs presence (NO SAVE).

Purpose (0102-first):
- Verify current YouTube Studio variant exposes schedule date/time inputs
  after opening the visibility dialog.
- Avoids clicking Done/Save.

Run:
  python -m modules.platform_integration.youtube_shorts_scheduler.tests.debug.smoke_schedule_inputs
"""

import os
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from modules.platform_integration.youtube_shorts_scheduler.src.dom_automation import YouTubeStudioDOM


def main() -> int:
    channel_id = os.getenv("CHANNEL_ID", "UC-LSSlOZwpGIRIYihaz8zCw")
    port = int(os.getenv("CHROME_PORT", "9222"))

    opts = Options()
    opts.add_experimental_option("debuggerAddress", f"127.0.0.1:{port}")
    d = webdriver.Chrome(options=opts)
    dom = YouTubeStudioDOM(d)

    ok = dom.navigate_to_shorts_with_fallback(channel_id, "UNLISTED")
    vid = dom.click_first_video_edit_button()
    time.sleep(1)

    print(f"[SMOKE] unlisted_ok={ok} video_id={vid}")

    dom.open_visibility_dialog()
    print("[SMOKE] visibility dialog opened")

    # Some Studio variants require selecting Public before schedule inputs appear.
    try:
        pub = WebDriverWait(d, 3).until(
            EC.element_to_be_clickable((By.XPATH, "//tp-yt-paper-radio-button[@name='PUBLIC']"))
        )
        pub.click()
        time.sleep(0.4)
        print("[SMOKE] public selected")
    except Exception:
        print("[SMOKE] public not clicked (not required or not found)")

    # Expand schedule section if needed.
    try:
        sc = d.find_element(By.ID, "second-container")
        d.execute_script("arguments[0].scrollIntoView({block:'center'});", sc)
        d.execute_script("arguments[0].click();", sc)
        time.sleep(0.6)
        print("[SMOKE] schedule container clicked")
    except Exception as exc:
        print(f"[SMOKE] schedule container not clicked: {exc}")

    # Current variant: date is a trigger + popup input; time is an input under time-of-day-container.
    date_trigger_ok = False
    date_picker_input_ok = False
    time_input_ok = False
    try:
        WebDriverWait(d, 4).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, dom.selectors.DATE_TRIGGER_CSS))
        )
        date_trigger_ok = True
    except Exception:
        pass
    try:
        WebDriverWait(d, 4).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, dom.selectors.TIME_OF_DAY_INPUT_CSS))
        )
        time_input_ok = True
    except Exception:
        pass

    # Click date trigger to open date picker popup input (NO typing, NO save).
    if date_trigger_ok:
        try:
            d.find_element(By.CSS_SELECTOR, dom.selectors.DATE_TRIGGER_CSS).click()
            time.sleep(0.4)
            WebDriverWait(d, 4).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, dom.selectors.DATE_PICKER_INPUT_CSS))
            )
            date_picker_input_ok = True
        except Exception:
            date_picker_input_ok = False

    print(
        "[SMOKE] "
        f"date_trigger_present={date_trigger_ok} "
        f"date_picker_input_present={date_picker_input_ok} "
        f"time_input_present={time_input_ok}"
    )

    if not (date_trigger_ok and time_input_ok):
        # Emit a small diagnostic payload: visible inputs and likely schedule-related text.
        try:
            inputs = d.execute_script(
                """
                const els = Array.from(document.querySelectorAll('input, textarea'));
                const visible = els.filter(e => e && e.offsetParent !== null);
                return visible.slice(0, 40).map(e => ({
                  tag: e.tagName,
                  type: e.getAttribute('type') || '',
                  aria: e.getAttribute('aria-label') || '',
                  placeholder: e.getAttribute('placeholder') || '',
                  value: (e.value || '').slice(0, 80),
                  id: e.id || '',
                  name: e.getAttribute('name') || ''
                }));
                """
            )
            print("[SMOKE][DIAG] visible_inputs=", inputs)
        except Exception as exc:
            print(f"[SMOKE][DIAG] input scan failed: {exc}")

        try:
            sched_text = d.execute_script(
                """
                const sc = document.querySelector('#second-container');
                if (!sc) return null;
                return (sc.textContent || '').trim().replace(/\\s+/g,' ').slice(0, 300);
                """
            )
            print("[SMOKE][DIAG] schedule_container_text=", sched_text)
        except Exception:
            pass

    # Close dialog without saving.
    try:
        d.find_element(By.TAG_NAME, "body").send_keys("\u001b")
    except Exception:
        pass

    return 0 if (ok and vid and date_trigger_ok and date_picker_input_ok and time_input_ok) else 1


if __name__ == "__main__":
    raise SystemExit(main())

