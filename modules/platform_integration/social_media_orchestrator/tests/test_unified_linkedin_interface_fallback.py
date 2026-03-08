import asyncio

from modules.platform_integration.social_media_orchestrator.src import unified_linkedin_interface as uli


def test_post_to_linkedin_uses_direct_fallback_when_fastmcp_missing(monkeypatch):
    interface = uli.UnifiedLinkedInInterface()
    request = uli.LinkedInPostRequest(
        content="Test content",
        content_type=uli.LinkedInContentType.GIT_COMMIT,
        company_page=uli.LinkedInCompanyPage.FOUNDUPS,
    )

    monkeypatch.setattr(uli, "_module_available", lambda name: False if name == "fastmcp" else True)
    monkeypatch.setattr(interface, "_post_direct_via_selenium", lambda req: (True, {"ui_state": "ok"}, None))
    monkeypatch.setattr(interface, "mark_as_posted", lambda request, success=True: None)

    result = asyncio.run(interface.post_to_linkedin(request))

    assert result.success is True
    assert result.company_page == uli.LinkedInCompanyPage.FOUNDUPS
