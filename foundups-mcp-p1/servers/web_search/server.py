"""
Web Search MCP Server

Provides 0102 with web search capabilities for pattern recall from 0201 nonlocal space.
Primary: DuckDuckGo (zero-cost, no API key required)
Fallback: Google Custom Search (if GOOGLE_API_KEY and GOOGLE_CX configured)

WSP Compliance:
- WSP 50: Search before create (enables web research)
- WSP 84: Use existing infrastructure (FastMCP pattern from holo_index)
- WSP 96: MCP Governance (Phase 0.1 server)

Tools:
- web_search: General web search (10 results)
- web_search_news: News-focused search
- fetch_webpage: Fetch and parse webpage content
- google_search: Google Custom Search (requires API key)
"""

import logging
import os
from typing import Optional, List, Dict, Any

from mcp import FastMCP

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Initialize MCP server
mcp = FastMCP("Web Search")

# Lazy-loaded search clients
_ddg_search = None

# Search API configs (from environment)
GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
GOOGLE_CX = os.environ.get('GOOGLE_CX')  # Custom Search Engine ID
SERPER_API_KEY = os.environ.get('SERPER_API_KEY')  # Serper.dev - simpler, just one key


def get_ddg():
    """Get or create DuckDuckGo search instance."""
    global _ddg_search
    if _ddg_search is None:
        try:
            from duckduckgo_search import DDGS
            _ddg_search = DDGS()
            logger.info("DuckDuckGo search initialized")
        except ImportError as e:
            logger.error(f"Failed to import duckduckgo_search: {e}")
            raise ImportError(
                "duckduckgo-search not installed. Run: "
                "pip install duckduckgo-search"
            )
    return _ddg_search


def _serper_search_impl(query: str, max_results: int = 10) -> Dict[str, Any]:
    """Internal Serper.dev search implementation (Google results, simpler setup)."""
    if not SERPER_API_KEY:
        return {'error': 'Serper not configured. Set SERPER_API_KEY (get free key at serper.dev)'}
    
    try:
        import httpx
        
        response = httpx.post(
            "https://google.serper.dev/search",
            headers={"X-API-KEY": SERPER_API_KEY, "Content-Type": "application/json"},
            json={"q": query, "num": min(max_results, 10)},
            timeout=10.0
        )
        response.raise_for_status()
        data = response.json()
        
        results = []
        for item in data.get('organic', []):
            results.append({
                'title': item.get('title', ''),
                'url': item.get('link', ''),
                'snippet': item.get('snippet', '')
            })
        
        return {
            'query': query,
            'results': results,
            'result_count': len(results),
            'backend': 'serper'
        }
        
    except Exception as e:
        logger.error(f"Serper search failed: {e}")
        return {'error': str(e)}


def _google_search_impl(query: str, max_results: int = 10) -> Dict[str, Any]:
    """Internal Google Custom Search implementation."""
    if not GOOGLE_API_KEY or not GOOGLE_CX:
        return {
            'error': 'Google Custom Search not configured. Set GOOGLE_API_KEY and GOOGLE_CX environment variables.',
            'setup_guide': {
                'step1': 'Get API Key: https://console.cloud.google.com/apis/credentials',
                'step2': 'Enable Custom Search API in Google Cloud Console',
                'step3': 'Create Search Engine: https://programmablesearchengine.google.com/',
                'step4': 'Set env vars: GOOGLE_API_KEY=xxx GOOGLE_CX=yyy'
            }
        }
    
    try:
        import httpx
        
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            'key': GOOGLE_API_KEY,
            'cx': GOOGLE_CX,
            'q': query,
            'num': min(max_results, 10)  # Google API max is 10 per request
        }
        
        response = httpx.get(url, params=params, timeout=10.0)
        response.raise_for_status()
        data = response.json()
        
        results = []
        for item in data.get('items', []):
            results.append({
                'title': item.get('title', ''),
                'url': item.get('link', ''),
                'snippet': item.get('snippet', '')
            })
        
        return {
            'query': query,
            'results': results,
            'result_count': len(results),
            'backend': 'google'
        }
        
    except Exception as e:
        logger.error(f"Google search failed: {e}")
        return {'error': str(e)}


@mcp.tool()
def web_search(
    query: str,
    max_results: int = 10,
    region: str = "wt-wt",
    use_google: bool = False
) -> Dict[str, Any]:
    """
    Search the web using DuckDuckGo (default) or Google (if configured).

    Args:
        query: Search query (e.g., "PQN consciousness research 2025")
        max_results: Maximum number of results (default: 10, max: 25)
        region: Region code (default: "wt-wt" for worldwide)
        use_google: Use Google Custom Search instead of DuckDuckGo (requires API key)

    Returns:
        {
            'query': str,
            'results': [{'title': str, 'url': str, 'snippet': str}],
            'result_count': int,
            'backend': str  # 'duckduckgo' or 'google'
        }

    Example:
        web_search(query="quantum neural networks consciousness", max_results=5)
        web_search(query="latest AI research", use_google=True)
    """
    logger.info(f"Web search: '{query}' (max_results={max_results}, use_google={use_google})")

    # Try Google if requested and configured
    if use_google:
        result = _google_search_impl(query, max_results)
        if 'error' not in result:
            return result
        # Fall through to DuckDuckGo if Google fails
        logger.warning(f"Google search failed, falling back to DuckDuckGo: {result.get('error')}")

    try:
        ddg = get_ddg()
        max_results = min(max_results, 25)  # Cap at 25

        results = list(ddg.text(
            keywords=query,
            region=region,
            max_results=max_results
        ))

        formatted_results = [
            {
                'title': r.get('title', ''),
                'url': r.get('href', r.get('link', '')),
                'snippet': r.get('body', r.get('snippet', ''))
            }
            for r in results
        ]

        logger.info(f"Found {len(formatted_results)} results for '{query}'")

        return {
            'query': query,
            'results': formatted_results,
            'result_count': len(formatted_results),
            'backend': 'duckduckgo'
        }

    except Exception as e:
        logger.error(f"Web search failed: {e}")
        return {
            'query': query,
            'results': [],
            'result_count': 0,
            'error': str(e)
        }


@mcp.tool()
def serper_search(
    query: str,
    max_results: int = 10
) -> Dict[str, Any]:
    """
    Search using Serper.dev API (Google results, simpler than Custom Search).
    
    Requires: SERPER_API_KEY environment variable
    
    Get free API key (2,500 queries/month free):
    1. Go to https://serper.dev
    2. Sign up and copy API key
    3. Add to .env: SERPER_API_KEY=your_key

    Args:
        query: Search query
        max_results: Maximum results (max: 10)

    Returns:
        {'query': str, 'results': [...], 'result_count': int, 'backend': 'serper'}
    """
    logger.info(f"Serper search: '{query}' (max_results={max_results})")
    return _serper_search_impl(query, max_results)


@mcp.tool()
def google_search(
    query: str,
    max_results: int = 10
) -> Dict[str, Any]:
    """
    Search using Google Custom Search API.
    
    Requires environment variables:
    - GOOGLE_API_KEY: Your Google Cloud API key
    - GOOGLE_CX: Your Programmable Search Engine ID
    
    Setup:
    1. Get API Key: https://console.cloud.google.com/apis/credentials
    2. Enable "Custom Search API" in APIs & Services
    3. Create Search Engine: https://programmablesearchengine.google.com/
    4. Set env vars in .cursor/mcp.json or shell

    Args:
        query: Search query
        max_results: Maximum results (max: 10 per Google API limits)

    Returns:
        {'query': str, 'results': [...], 'result_count': int, 'backend': 'google'}
        
    Cost: 100 free/day, then $5 per 1000 queries
    """
    logger.info(f"Google search: '{query}' (max_results={max_results})")
    return _google_search_impl(query, max_results)


@mcp.tool()
def web_search_news(
    query: str,
    max_results: int = 10,
    timelimit: str = "w"
) -> Dict[str, Any]:
    """
    Search news articles using DuckDuckGo.

    Args:
        query: News search query
        max_results: Maximum number of results (default: 10, max: 25)
        timelimit: Time limit - "d" (day), "w" (week), "m" (month)

    Returns:
        {
            'query': str,
            'results': [
                {
                    'title': str,
                    'url': str,
                    'snippet': str,
                    'date': str,
                    'source': str
                }
            ],
            'result_count': int
        }

    Example:
        web_search_news(query="AI consciousness breakthrough", timelimit="w")
    """
    logger.info(f"News search: '{query}' (timelimit={timelimit})")

    try:
        ddg = get_ddg()
        max_results = min(max_results, 25)

        results = list(ddg.news(
            keywords=query,
            timelimit=timelimit,
            max_results=max_results
        ))

        formatted_results = [
            {
                'title': r.get('title', ''),
                'url': r.get('url', r.get('link', '')),
                'snippet': r.get('body', ''),
                'date': r.get('date', ''),
                'source': r.get('source', '')
            }
            for r in results
        ]

        logger.info(f"Found {len(formatted_results)} news results for '{query}'")

        return {
            'query': query,
            'results': formatted_results,
            'result_count': len(formatted_results)
        }

    except Exception as e:
        logger.error(f"News search failed: {e}")
        return {
            'query': query,
            'results': [],
            'result_count': 0,
            'error': str(e)
        }


@mcp.tool()
def fetch_webpage(
    url: str,
    max_length: int = 5000
) -> Dict[str, Any]:
    """
    Fetch and parse webpage content.

    Args:
        url: URL to fetch
        max_length: Maximum content length to return (default: 5000 chars)

    Returns:
        {
            'url': str,
            'title': str,
            'content': str,
            'content_length': int,
            'truncated': bool
        }

    Example:
        fetch_webpage(url="https://example.com/article")
    """
    logger.info(f"Fetching webpage: {url}")

    try:
        import httpx
        from bs4 import BeautifulSoup

        # Fetch with timeout
        response = httpx.get(
            url,
            timeout=10.0,
            follow_redirects=True,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        )
        response.raise_for_status()

        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract title
        title = soup.title.string if soup.title else ''

        # Remove script and style elements
        for script in soup(['script', 'style', 'nav', 'footer', 'header']):
            script.decompose()

        # Get text content
        text = soup.get_text(separator='\n', strip=True)

        # Clean up whitespace
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        content = '\n'.join(lines)

        # Truncate if needed
        truncated = len(content) > max_length
        if truncated:
            content = content[:max_length] + '...'

        logger.info(f"Fetched {len(content)} chars from {url}")

        return {
            'url': url,
            'title': title,
            'content': content,
            'content_length': len(content),
            'truncated': truncated
        }

    except ImportError as e:
        logger.error(f"Missing dependency: {e}")
        return {
            'url': url,
            'error': f"Missing dependency: {e}. Run: pip install httpx beautifulsoup4"
        }
    except Exception as e:
        logger.error(f"Failed to fetch {url}: {e}")
        return {
            'url': url,
            'error': str(e)
        }


@mcp.tool()
def get_search_status() -> Dict[str, Any]:
    """
    Check which search backends are available.
    
    Returns:
        {
            'duckduckgo': bool,
            'google': bool,
            'google_config': {'api_key_set': bool, 'cx_set': bool}
        }
    """
    return {
        'duckduckgo': True,  # Always available (no config needed)
        'serper': bool(SERPER_API_KEY),  # Recommended - simpler setup
        'google': bool(GOOGLE_API_KEY and GOOGLE_CX),
        'config': {
            'serper_key_set': bool(SERPER_API_KEY),
            'google_api_key_set': bool(GOOGLE_API_KEY),
            'google_cx_set': bool(GOOGLE_CX)
        }
    }


if __name__ == "__main__":
    logger.info("Starting Web Search MCP Server...")
    logger.info("Tools: web_search, serper_search, google_search, web_search_news, fetch_webpage, get_search_status")
    logger.info("Primary: DuckDuckGo (zero-cost)")
    logger.info(f"Serper: {'Configured' if SERPER_API_KEY else 'Not configured (recommended - get key at serper.dev)'}")
    logger.info(f"Google: {'Configured' if GOOGLE_API_KEY and GOOGLE_CX else 'Not configured'}")
    mcp.run()

