#!/usr/bin/env bash
set -e
echo "Running WSP 87 navigation schema check..."
python -m tests.navigation.test_navigation_schema
