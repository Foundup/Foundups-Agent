#!/usr/bin/env python3
"""Unit coverage for Git push branch-protection policy helpers."""

from __future__ import annotations

from modules.platform_integration.linkedin_agent.src.git_linkedin_bridge import GitLinkedInBridge


def test_branch_requires_pr_for_protected_branch_by_default() -> None:
    assert GitLinkedInBridge._branch_requires_pr("main", env={}) is True
    assert GitLinkedInBridge._branch_requires_pr("master", env={}) is True


def test_branch_requires_pr_can_allow_direct_protected_override() -> None:
    env = {"GIT_PUSH_DIRECT_PROTECTED": "1"}
    assert GitLinkedInBridge._branch_requires_pr("main", env=env) is False


def test_branch_requires_pr_global_flag_forces_pr_on_feature_branches() -> None:
    env = {"GIT_PUSH_REQUIRE_PR": "true"}
    assert GitLinkedInBridge._branch_requires_pr("feature/policy-check", env=env) is True


def test_release_branch_pattern_matching_defaults() -> None:
    assert GitLinkedInBridge._is_release_branch("main", env={}) is True
    assert GitLinkedInBridge._is_release_branch("release/2026-q1", env={}) is True
    assert GitLinkedInBridge._is_release_branch("hotfix/urgent", env={}) is True
    assert GitLinkedInBridge._is_release_branch("feature/prototype", env={}) is False


def test_release_branch_pattern_matching_custom_patterns() -> None:
    env = {"GIT_PUSH_RELEASE_BRANCH_PATTERNS": "prod,staging/*"}
    assert GitLinkedInBridge._is_release_branch("prod", env=env) is True
    assert GitLinkedInBridge._is_release_branch("staging/canary", env=env) is True
    assert GitLinkedInBridge._is_release_branch("main", env=env) is False
