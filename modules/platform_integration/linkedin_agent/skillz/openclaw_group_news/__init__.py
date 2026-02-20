"""
OpenClaw Group News Skillz

Searches, rates, and posts OpenClaw news to LinkedIn Group.
Runs BEFORE comment engagement in the LinkedIn automation flow.

Usage:
    from modules.platform_integration.linkedin_agent.skillz.openclaw_group_news import (
        search_openclaw_news,
        NewsRelevanceRater,
        OpenClawGroupPoster,
        run_openclaw_news_flow
    )

    # Full flow
    result = run_openclaw_news_flow(dry_run=True)

    # Or manual steps
    news = search_openclaw_news(max_results=10)
    scored = [(item, NewsRelevanceRater.rate(item)) for item in news]
    poster = OpenClawGroupPoster()
    poster.post_to_group(scored[0][0])
"""

from .executor import (
    NewsItem,
    NewsRelevanceRater,
    OpenClawGroupPoster,
    search_openclaw_news,
    run_openclaw_news_flow,
    LINKEDIN_GROUP_ID,
    LINKEDIN_GROUP_URL,
    RELEVANCE_THRESHOLD,
)

__all__ = [
    "NewsItem",
    "NewsRelevanceRater",
    "OpenClawGroupPoster",
    "search_openclaw_news",
    "run_openclaw_news_flow",
    "LINKEDIN_GROUP_ID",
    "LINKEDIN_GROUP_URL",
    "RELEVANCE_THRESHOLD",
]
