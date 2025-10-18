#!/bin/bash

# WSP Step 3 Script: Per-Module Coverage Audit
# Ensures each FoundUps module meets the minimum test coverage threshold.

MODULES_DIR="modules"
MIN_COVERAGE=90 # Required minimum coverage percentage

echo "Starting Per-Module Coverage Audit (Threshold: ${MIN_COVERAGE}%)"
echo "=========================================================="

# Dynamically find module directories containing src/ and tests/
# Alternatively, use the original hardcoded list if preferred:
# for module_name in banter_engine livechat ...; do module_path="${MODULES_DIR}/${module_name}"; ... done

find "$MODULES_DIR" -maxdepth 1 -mindepth 1 -type d | while read -r module_path; do
  module_name=$(basename "$module_path")

  # Skip directories that don't look like valid modules
  if [ ! -d "${module_path}/src" ] || [ ! -d "${module_path}/tests" ]; then
    echo "--- Skipping ${module_name} (missing src/ or tests/) ---"
    continue
  fi
  # Add other skips if necessary (e.g., baseline copies, hidden dirs)
  if [[ "$module_name" == .* || "$module_name" == "__pycache__" || "$module_name" == *"clean"* ]]; then
       echo "--- Skipping known non-module: ${module_name} ---"
       continue
  fi


  echo # Blank line for separation
  echo "=== Auditing Coverage for: ${module_name} ==="

  pytest "${module_path}/tests/" \
    --cov="modules.${module_name}.src" \
    --cov-report=term-missing \
    --cov-fail-under=$MIN_COVERAGE

  # Check the exit code explicitly
  pytest_exit_code=$?
  if [ $pytest_exit_code -ne 0 ]; then
    echo "----------------------------------------------------------"
    echo "[FAIL] ERROR: Pytest failed for module '${module_name}' (Exit Code: ${pytest_exit_code})."
    echo "       Coverage likely below ${MIN_COVERAGE}% or tests failed."
    echo "       Fix the issues above and re-run the audit."
    echo "=========================================================="
    exit 1 # Exit the script immediately
  else
    echo "[OK] OK: Coverage check passed for ${module_name}."
    echo "----------------------------------------------------------"

  fi
done

# If the loop completes without exiting, all modules passed
echo # Blank line
echo "=========================================================="
echo "[CELEBRATE] SUCCESS: All checked modules meet the ${MIN_COVERAGE}% coverage threshold!"
echo "=========================================================="
exit 0 