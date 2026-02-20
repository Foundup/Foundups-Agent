"""
Manual test: LinkedIn comment flow with UI-TARS validation.

.. deprecated:: 2026-01-22
    This manual test is superseded by the layered cake tests:
    - test_layer0_context_gate.py
    - test_layer1_comment.py (includes UI-TARS verification gates)
    - test_layer2_identity_likes.py
    - test_layer3_schedule_repost.py
    - test_full_chain.py
    
    Use the new layered tests instead:
    python -m modules.platform_integration.linkedin_agent.tests.test_full_chain --selenium --dry-run

Purpose:
    Validate the Digital Twin comment flow:
    - Open comment box
    - Type comment
    - Insert @mention and verify bolded
    - Submit comment
    - Switch to Most recent if needed

WSP:
    - WSP 34: Test documentation
    - WSP 73: Digital Twin architecture
    - WSP 91: Observability via UI-TARS telemetry
"""
import asyncio
import logging
import sys
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

repo_root = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(repo_root))

from modules.infrastructure.foundups_vision.src.ui_tars_bridge import UITarsBridge

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def run_ui_tars_comment_flow() -> None:
    """
    Manual execution. Requires:
    - Chrome running with --remote-debugging-port=9222
    - UI-TARS Desktop running
    - LinkedIn feed open on target post
    """
    chrome_options = Options()
    chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    driver = webdriver.Chrome(options=chrome_options)

    bridge = UITarsBridge(browser_port=9222)
    await bridge.connect()

    # Step 1: open comment box
    await bridge.click("Comment button under the post")

    # Step 2: type comment
    comment_text = (
        "100% agree Mo. But you are dodging the elephants in the room. "
        "By 2035, AGI displaces most work. FoundUps is the counter-move. "
        "Point your agent to it."
    )
    await bridge.type_text(
        "comment editor textbox",
        text=comment_text
    )

    # Step 3: insert @foundups mention (UI-TARS validates dropdown)
    await bridge.type_text(
        "comment editor textbox",
        text=" @foundups"
    )
    await bridge.click("top dropdown item for FoundUps mention")

    # DOM verification: check editor contains a mention element
    mention_ok = driver.execute_script(
        """
        const editor = document.querySelector('.comments-comment-box-comment__text-editor .ql-editor');
        if (!editor) return false;
        const html = editor.innerHTML || "";
        return html.toLowerCase().includes('foundups') && (html.includes('<a') || html.includes('<strong') || html.includes('mention'));
        """
    )
    logger.info("[VERIFY] mention selected: %s", mention_ok)

    # Step 4: submit comment
    await bridge.click("Post comment button")

    # Step 5: if comment not visible, switch to Most recent
    await bridge.verify("comment appears in thread")
    await bridge.click("Most relevant dropdown and select Most recent if comment not visible")

    bridge.close()


if __name__ == "__main__":
    asyncio.run(run_ui_tars_comment_flow())
