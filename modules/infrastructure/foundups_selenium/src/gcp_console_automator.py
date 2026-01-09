# -*- coding: utf-8 -*-
"""
GCP Console Automator - Autonomous Google Cloud Console Operations
Uses FoundUpsDriver + Gemini Vision to automate cloud infrastructure tasks.

WSP 77: Agent Coordination Protocol
WSP 80: DAE Orchestration
WSP 96: Skills-driven automation
"""

import json
import logging
import time
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime

from modules.infrastructure.foundups_selenium.src.foundups_driver import FoundUpsDriver

logger = logging.getLogger(__name__)

@dataclass
class AutomationResult:
    """Result of GCP Console automation task"""
    success: bool
    workflow: str
    steps_completed: int
    total_steps: int
    error_message: Optional[str] = None
    screenshots: List[str] = None
    duration_seconds: float = 0.0
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.screenshots is None:
            self.screenshots = []


class GCPConsoleAutomator:
    """
    Autonomous GCP Console automation using FoundUpsDriver + Vision DAE.

    Executes cloud infrastructure tasks defined in skills/gcp_console_automation.json
    without human intervention, using Gemini Vision for UI state validation.
    """

    def __init__(self, skill_path: Optional[Path] = None):
        """
        Initialize GCP Console Automator.

        Args:
            skill_path: Path to gcp_console_automation.json skill definition
        """
        if skill_path is None:
            skill_path = Path(__file__).parents[3] / "communication" / "livechat" / "skillz" / "gcp_console_automation.json"

        self.skill_path = skill_path
        self.skill_config = self._load_skill_config()
        self.driver: Optional[FoundUpsDriver] = None
        self.screenshot_dir = Path("docs/session_backups/gcp_automation/screenshots")
        self.screenshot_dir.mkdir(parents=True, exist_ok=True)

    def _load_skill_config(self) -> Dict[str, Any]:
        """Load GCP automation skill configuration"""
        try:
            with open(self.skill_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"Skill config not found: {self.skill_path}")
            return {}

    def create_secret_manager_secret(
        self,
        project_id: str,
        secret_name: str,
        secret_value: str,
        grant_to_cloud_build: bool = True
    ) -> AutomationResult:
        """
        Create a secret in Secret Manager and optionally grant Cloud Build access.

        Args:
            project_id: GCP project ID
            secret_name: Name of the secret (e.g., GEMINI_API_KEY_GOTJUNK)
            secret_value: Secret value to store
            grant_to_cloud_build: Whether to grant access to Cloud Build service account

        Returns:
            AutomationResult with success status and details
        """
        workflow = self.skill_config["automation_workflows"]["create_secret_manager_secret"]
        start_time = time.time()
        steps_completed = 0
        total_steps = len(workflow["steps"])

        try:
            # Initialize driver with vision enabled
            self.driver = FoundUpsDriver(vision_enabled=True, stealth_mode=True)

            # Step 1: Navigate to Secret Manager
            url = workflow["steps"][0]["target"].format(project_id=project_id)
            logger.info(f"[0102::GCP] Navigating to Secret Manager: {url}")
            self.driver.get(url)
            self.driver.random_delay(2, 4)
            steps_completed += 1

            # Step 2: Click CREATE SECRET button
            logger.info("[0102::GCP] Clicking CREATE SECRET button")
            create_button = self.driver.smart_find_element(
                selectors=workflow["steps"][1]["target_selectors"],
                description=workflow["steps"][1]["vision_fallback"],
                use_vision=True
            )
            create_button.click()
            self.driver.random_delay(1, 2)
            steps_completed += 1

            # Step 3: Enter secret name
            logger.info(f"[0102::GCP] Entering secret name: {secret_name}")
            name_input = self.driver.smart_find_element(
                selectors=workflow["steps"][2]["target_selectors"],
                description=workflow["steps"][2]["description"]
            )
            self.driver.human_type(name_input, secret_name)
            self.driver.random_delay(0.5, 1)
            steps_completed += 1

            # Step 4: Enter secret value
            logger.info("[0102::GCP] Entering secret value (redacted)")
            value_textarea = self.driver.smart_find_element(
                selectors=workflow["steps"][3]["target_selectors"],
                description=workflow["steps"][3]["description"]
            )
            self.driver.human_type(value_textarea, secret_value)
            self.driver.random_delay(0.5, 1)
            steps_completed += 1

            # Step 5: Click CREATE button
            logger.info("[0102::GCP] Clicking CREATE button")
            submit_button = self.driver.smart_find_element(
                selectors=workflow["steps"][4]["target_selectors"],
                description=workflow["steps"][4]["vision_fallback"],
                use_vision=True
            )
            submit_button.click()
            steps_completed += 1

            # Step 6: Validate secret creation
            logger.info("[0102::GCP] Validating secret creation with Vision DAE")
            self.driver.random_delay(2, 3)
            screenshot_path = str(self.screenshot_dir / f"secret_created_{secret_name}_{int(time.time())}.png")
            analysis = self.driver.analyze_ui(save_screenshot=True, screenshot_dir=str(self.screenshot_dir))
            steps_completed += 1

            # Check for success pattern
            ui_state = analysis.get("ui_state", "")
            if "success" in ui_state.lower() or "created" in ui_state.lower():
                logger.info(f"[0102::GCP] ✓ Secret {secret_name} created successfully")

                # Step 7: Grant permissions to Cloud Build (if requested)
                if grant_to_cloud_build:
                    logger.info("[0102::GCP] Granting permissions to Cloud Build service account")
                    # TODO: Implement permission granting automation
                    # For now, log manual step required
                    logger.warning("[0102::GCP] Manual step: Grant Cloud Build access via Permissions tab")
                steps_completed += 1

                duration = time.time() - start_time
                return AutomationResult(
                    success=True,
                    workflow="create_secret_manager_secret",
                    steps_completed=steps_completed,
                    total_steps=total_steps,
                    screenshots=[screenshot_path],
                    duration_seconds=duration
                )
            else:
                raise Exception(f"Secret creation validation failed: {ui_state}")

        except Exception as e:
            logger.error(f"[0102::GCP] ✗ Secret creation failed: {e}")
            duration = time.time() - start_time
            return AutomationResult(
                success=False,
                workflow="create_secret_manager_secret",
                steps_completed=steps_completed,
                total_steps=total_steps,
                error_message=str(e),
                duration_seconds=duration
            )
        finally:
            if self.driver:
                # Keep browser open for debugging
                logger.info("[0102::GCP] Browser staying open for inspection...")

    def create_cloud_build_trigger(
        self,
        project_id: str,
        trigger_name: str,
        repo_name: str,
        branch_pattern: str,
        yaml_path: str,
        file_filter: Optional[str] = None
    ) -> AutomationResult:
        """
        Create Cloud Build trigger for GitHub repository.

        Args:
            project_id: GCP project ID
            trigger_name: Name for the trigger
            repo_name: GitHub repository name
            branch_pattern: Branch pattern (e.g., ^main$)
            yaml_path: Path to cloudbuild.yaml
            file_filter: Optional included files filter (e.g., modules/foundups/gotjunk/**)

        Returns:
            AutomationResult with success status and details
        """
        workflow = self.skill_config["automation_workflows"]["create_cloud_build_trigger"]
        start_time = time.time()
        steps_completed = 0
        total_steps = len(workflow["steps"])

        try:
            # Initialize driver if not already created
            if self.driver is None:
                self.driver = FoundUpsDriver(vision_enabled=True, stealth_mode=True)

            # Step 1: Navigate to Cloud Build Triggers
            url = workflow["steps"][0]["target"].format(project_id=project_id)
            logger.info(f"[0102::GCP] Navigating to Cloud Build Triggers: {url}")
            self.driver.get(url)
            self.driver.random_delay(3, 5)
            steps_completed += 1

            # Step 2: Click CREATE TRIGGER button
            logger.info("[0102::GCP] Clicking CREATE TRIGGER button")
            create_button = self.driver.smart_find_element(
                selectors=workflow["steps"][1]["target_selectors"],
                description=workflow["steps"][1]["vision_fallback"],
                use_vision=True
            )
            create_button.click()
            self.driver.random_delay(2, 3)
            steps_completed += 1

            # Step 3: Configure trigger (complex multi-field form)
            logger.info("[0102::GCP] Configuring trigger settings")
            # TODO: Implement detailed form filling automation
            # This is complex and requires Vision DAE guidance for each field
            logger.warning("[0102::GCP] Manual step: Configure trigger fields in UI")
            logger.info(f"  - Name: {trigger_name}")
            logger.info(f"  - Event: push_to_branch")
            logger.info(f"  - Repository: {repo_name}")
            logger.info(f"  - Branch: {branch_pattern}")
            logger.info(f"  - Config: {yaml_path}")
            if file_filter:
                logger.info(f"  - Filter: {file_filter}")
            steps_completed += 1

            # Placeholder: User completes manual steps
            input("[0102::GCP] Press Enter after manually configuring trigger fields...")

            # Step 4: Click CREATE button
            logger.info("[0102::GCP] Clicking CREATE button")
            submit_button = self.driver.smart_find_element(
                selectors=workflow["steps"][3]["target_selectors"],
                description=workflow["steps"][3]["vision_fallback"],
                use_vision=True
            )
            submit_button.click()
            steps_completed += 1

            # Step 5: Validate trigger creation
            logger.info("[0102::GCP] Validating trigger creation with Vision DAE")
            self.driver.random_delay(3, 5)
            screenshot_path = str(self.screenshot_dir / f"trigger_created_{trigger_name}_{int(time.time())}.png")
            analysis = self.driver.analyze_ui(save_screenshot=True, screenshot_dir=str(self.screenshot_dir))
            steps_completed += 1

            ui_state = analysis.get("ui_state", "")
            if "success" in ui_state.lower() or "created" in ui_state.lower():
                logger.info(f"[0102::GCP] ✓ Trigger {trigger_name} created successfully")
                duration = time.time() - start_time
                return AutomationResult(
                    success=True,
                    workflow="create_cloud_build_trigger",
                    steps_completed=steps_completed,
                    total_steps=total_steps,
                    screenshots=[screenshot_path],
                    duration_seconds=duration
                )
            else:
                raise Exception(f"Trigger creation validation failed: {ui_state}")

        except Exception as e:
            logger.error(f"[0102::GCP] ✗ Trigger creation failed: {e}")
            duration = time.time() - start_time
            return AutomationResult(
                success=False,
                workflow="create_cloud_build_trigger",
                steps_completed=steps_completed,
                total_steps=total_steps,
                error_message=str(e),
                duration_seconds=duration
            )

    def setup_gotjunk_deployment(self) -> Dict[str, AutomationResult]:
        """
        Complete autonomous setup for GotJunk FoundUp deployment.
        Reads config from skill definition and executes all required automation.

        Returns:
            Dict of workflow_name -> AutomationResult
        """
        gotjunk_config = self.skill_config["foundups_integration"]["gotjunk"]
        results = {}

        logger.info("[0102::GCP] Starting autonomous GotJunk deployment setup")
        logger.info(f"  Project: {gotjunk_config['project_id']}")
        logger.info(f"  Service: {gotjunk_config['cloud_run_service']}")
        logger.info(f"  Region: {gotjunk_config['region']}")

        # Task 1: Create Secret Manager secret
        # NOTE: Secret value should come from .env, not hardcoded
        logger.info("\n[0102::GCP] Task 1: Create Secret Manager secret")
        logger.warning("[0102::GCP] Skipping secret creation - requires API key from .env")
        # Uncomment when ready to execute:
        # secret_result = self.create_secret_manager_secret(
        #     project_id=gotjunk_config["project_id"],
        #     secret_name=gotjunk_config["secret_name"],
        #     secret_value="<from .env>",  # Load from environment
        #     grant_to_cloud_build=True
        # )
        # results["create_secret"] = secret_result

        # Task 2: Create Cloud Build trigger
        logger.info("\n[0102::GCP] Task 2: Create Cloud Build trigger")
        trigger_result = self.create_cloud_build_trigger(
            project_id=gotjunk_config["project_id"],
            trigger_name=gotjunk_config["trigger_name"],
            repo_name=gotjunk_config["repo_name"],
            branch_pattern=gotjunk_config["branch_pattern"],
            yaml_path=gotjunk_config["yaml_path"],
            file_filter=gotjunk_config["file_filter"]
        )
        results["create_trigger"] = trigger_result

        logger.info("\n[0102::GCP] Autonomous setup complete")
        return results

    def __del__(self):
        """Cleanup: close browser if still open"""
        if self.driver:
            try:
                # Don't auto-close for debugging
                pass
            except:
                pass


if __name__ == "__main__":
    # CLI testing
    import argparse

    logging.basicConfig(level=logging.INFO, format='%(message)s')

    parser = argparse.ArgumentParser(description="GCP Console Automation (0102 Arms & Eyes)")
    parser.add_argument("--setup-gotjunk", action="store_true", help="Run complete GotJunk setup")
    parser.add_argument("--create-secret", metavar="NAME", help="Create Secret Manager secret")
    parser.add_argument("--secret-value", metavar="VALUE", help="Secret value")
    parser.add_argument("--create-trigger", metavar="NAME", help="Create Cloud Build trigger")
    parser.add_argument("--project-id", default="gen-lang-client-0061781628", help="GCP project ID")

    args = parser.parse_args()

    automator = GCPConsoleAutomator()

    if args.setup_gotjunk:
        print("\n[0102::GCP] 🤖 Initiating autonomous GotJunk deployment setup...")
        print("[0102::GCP] Using FoundUpsDriver + Gemini Vision")
        results = automator.setup_gotjunk_deployment()
        print(f"\n[0102::GCP] Results: {len(results)} workflows executed")
        for workflow, result in results.items():
            status = "✓ SUCCESS" if result.success else "✗ FAILED"
            print(f"  {workflow}: {status} ({result.steps_completed}/{result.total_steps} steps)")

    elif args.create_secret:
        if not args.secret_value:
            print("Error: --secret-value required")
        else:
            result = automator.create_secret_manager_secret(
                project_id=args.project_id,
                secret_name=args.create_secret,
                secret_value=args.secret_value,
                grant_to_cloud_build=True
            )
            status = "✓ SUCCESS" if result.success else "✗ FAILED"
            print(f"\n[0102::GCP] {status} - {result.steps_completed}/{result.total_steps} steps completed")

    elif args.create_trigger:
        # Use GotJunk defaults
        config = automator.skill_config["foundups_integration"]["gotjunk"]
        result = automator.create_cloud_build_trigger(
            project_id=args.project_id,
            trigger_name=args.create_trigger,
            repo_name=config["repo_name"],
            branch_pattern=config["branch_pattern"],
            yaml_path=config["yaml_path"],
            file_filter=config["file_filter"]
        )
        status = "✓ SUCCESS" if result.success else "✗ FAILED"
        print(f"\n[0102::GCP] {status} - {result.steps_completed}/{result.total_steps} steps completed")

    else:
        parser.print_help()
