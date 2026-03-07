#!/usr/bin/env python3
"""Tests for LinkedIn group membership DAE helpers."""

import sqlite3
import tempfile


def _import_membership_symbols():
    from modules.platform_integration.linkedin_agent.skillz.openclaw_group_news import (
        GroupLanguageDetector,
        GroupMemberRequest,
        OpenClawGroupMembershipDAE,
        WelcomeMessageComposer,
    )

    return GroupLanguageDetector, GroupMemberRequest, OpenClawGroupMembershipDAE, WelcomeMessageComposer


def test_group_language_detection_scripts():
    GroupLanguageDetector, _, _, _ = _import_membership_symbols()

    assert GroupLanguageDetector.detect("\ubc15\ub3d9\ud658") == "ko"
    assert GroupLanguageDetector.detect("\u30c7\u30b8\u30e3\u30f3") == "ja"
    assert GroupLanguageDetector.detect("\u5f20\u4e09") == "zh"
    assert GroupLanguageDetector.detect("\u0414\u0435\u0458\u0430\u043d") == "sr"
    assert GroupLanguageDetector.detect("Dejan Djokic") == "en"


def test_parse_member_name_from_approve_label():
    _, _, OpenClawGroupMembershipDAE, _ = _import_membership_symbols()

    assert (
        OpenClawGroupMembershipDAE.parse_member_name_from_approve_label(
            "Approve request for Dejan Djokic"
        )
        == "Dejan Djokic"
    )
    assert (
        OpenClawGroupMembershipDAE.parse_member_name_from_approve_label(
            "Approve request for \ubc15\ub3d9\ud658"
        )
        == "\ubc15\ub3d9\ud658"
    )


def test_welcome_composer_fallback_localized():
    _, GroupMemberRequest, _, WelcomeMessageComposer = _import_membership_symbols()

    composer = WelcomeMessageComposer(prefer_ironclaw=False)

    english = composer.compose(
        GroupMemberRequest(name="Dejan", language="en")
    ).lower()
    assert "foundups.com" in english
    assert "roi" in english and "roc" in english

    korean = composer.compose(
        GroupMemberRequest(name="\ubc15\ub3d9\ud658", language="ko")
    )
    assert "foundups.com" in korean
    assert "roc" in korean.lower()


def test_group_action_log_table_writes():
    _, GroupMemberRequest, OpenClawGroupMembershipDAE, _ = _import_membership_symbols()

    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as handle:
        db_path = handle.name

    dae = OpenClawGroupMembershipDAE(db_path=db_path)
    member = GroupMemberRequest(
        name="Dejan Djokic",
        language="en",
        profile_url="https://linkedin.com/in/dejan",
    )
    dae._log_action(
        member=member,
        action_type="dry_run_preview",
        action_status="ok",
        message_preview="welcome Dejan...",
    )

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM agents_social_group_actions")
    count = cursor.fetchone()[0]
    conn.close()

    assert count == 1


def test_member_classifier_denies_no_image():
    _, GroupMemberRequest, OpenClawGroupMembershipDAE, _ = _import_membership_symbols()

    member = GroupMemberRequest(
        name="Nicodemme Jean-Baptiste",
        headline="Celebrity Phlebotomist",
        profile_url="https://www.linkedin.com/in/convelabs/",
        image_url="",
    )
    is_human, reason = OpenClawGroupMembershipDAE._classify_member_account(member)
    assert is_human is False
    assert reason == "no_image"


def test_member_classifier_denies_brand_admin():
    _, GroupMemberRequest, OpenClawGroupMembershipDAE, _ = _import_membership_symbols()

    member = GroupMemberRequest(
        name="Top Vietnam",
        headline="Administrator at TopVN",
        profile_url="https://www.linkedin.com/in/top-vietnam/",
        image_url="https://media.licdn.com/dms/image/profile-displayphoto.jpg",
    )
    is_human, reason = OpenClawGroupMembershipDAE._classify_member_account(member)
    assert is_human is False
    assert "headline_admin_role" in reason


def test_non_human_message_no_image_override():
    _, GroupMemberRequest, OpenClawGroupMembershipDAE, _ = _import_membership_symbols()

    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as handle:
        db_path = handle.name

    dae = OpenClawGroupMembershipDAE(db_path=db_path)
    member = GroupMemberRequest(name="No Avatar", classification_reason="no_image")
    message = dae._compose_non_human_message(member)
    assert message == "no image"
