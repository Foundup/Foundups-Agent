#!/usr/bin/env python3
"""
FoundUps SDK - Python Client for Autonomous Development Platform
================================================================

Easy-to-use Python SDK for integrating with FoundUps autonomous development platform.

Features:
- Semantic code search with HoloIndex
- AI-powered code analysis with Qwen
- Real-time development guidance
- WSP compliance checking
- Module health monitoring

Example:
    from foundups_sdk import FoundUpsClient

    client = FoundUpsClient("https://your-app.vercel.app")
    results = client.search("authentication patterns")
    analysis = client.analyze("implement user login")
"""



import requests
import json
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from urllib.parse import urljoin, urlencode


@dataclass
class SearchResult:
    """Represents a single search result from HoloIndex."""
    location: str
    similarity: float
    content: Optional[str] = None
    module: Optional[str] = None


@dataclass
class SearchResponse:
    """Complete search response from FoundUps."""
    query: str
    total_results: int
    code_results: List[SearchResult]
    wsp_results: List[SearchResult]
    timestamp: str


@dataclass
class AnalysisResult:
    """AI analysis result from Qwen orchestrator."""
    query: str
    analysis: Dict[str, Any]
    recommendations: List[str]
    wsp_guidance: List[str]
    timestamp: str


class FoundUpsClient:
    """
    Python SDK client for FoundUps autonomous development platform.

    Provides easy access to HoloIndex semantic search, Qwen AI analysis,
    and real-time development guidance.
    """

    def __init__(self, base_url: str, api_key: Optional[str] = None, timeout: int = 30):
        """
        Initialize FoundUps client.

        Args:
            base_url: Base URL of FoundUps deployment (e.g., "https://your-app.vercel.app")
            api_key: Optional API key for authenticated requests
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.timeout = timeout
        self.session = requests.Session()

        # Set default headers
        self.session.headers.update({
            'User-Agent': 'FoundUps-SDK/1.0.0',
            'Content-Type': 'application/json'
        })

        if api_key:
            self.session.headers['Authorization'] = f'Bearer {api_key}'

    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request to FoundUps API."""
        url = urljoin(self.base_url + '/', endpoint.lstrip('/'))

        try:
            response = self.session.request(method, url, timeout=self.timeout, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise FoundUpsError(f"API request failed: {e}")

    def health_check(self) -> Dict[str, Any]:
        """
        Check system health status.

        Returns:
            Dict containing health status information
        """
        return self._make_request('GET', '/api/health')

    def system_status(self) -> Dict[str, Any]:
        """
        Get detailed system status.

        Returns:
            Dict containing system status (HoloIndex, Qwen model, etc.)
        """
        return self._make_request('GET', '/api/status')

    def search(self, query: str, limit: int = 5, include_content: bool = False) -> SearchResponse:
        """
        Perform semantic search using HoloIndex.

        Args:
            query: Search query (e.g., "authentication patterns")
            limit: Maximum number of results per category
            include_content: Whether to include full content in results

        Returns:
            SearchResponse object with results
        """
        params = {
            'q': query,
            'limit': limit,
            'include_content': str(include_content).lower()
        }

        response = self._make_request('GET', f'/api/search?{urlencode(params)}')

        # Parse results into SearchResult objects
        code_results = []
        for hit in response.get('results', {}).get('code', []):
            code_results.append(SearchResult(
                location=hit.get('location', ''),
                similarity=float(hit.get('similarity', 0)),
                content=hit.get('content') if include_content else None
            ))

        wsp_results = []
        for hit in response.get('results', {}).get('wsps', []):
            wsp_results.append(SearchResult(
                location=hit.get('location', ''),
                similarity=float(hit.get('similarity', 0)),
                content=hit.get('content') if include_content else None
            ))

        return SearchResponse(
            query=response.get('query', query),
            total_results=response.get('total_found', 0),
            code_results=code_results,
            wsp_results=wsp_results,
            timestamp=response.get('timestamp', '')
        )

    def analyze(self, query: str, advisor: bool = True) -> AnalysisResult:
        """
        Perform AI-powered analysis using Qwen orchestrator.

        Args:
            query: Analysis query (e.g., "implement user login")
            advisor: Whether to include Qwen advisor guidance

        Returns:
            AnalysisResult object with AI analysis and recommendations
        """
        payload = {
            'query': query,
            'advisor': advisor
        }

        response = self._make_request('POST', '/api/holoindex', json=payload)

        return AnalysisResult(
            query=response.get('query', query),
            analysis=response.get('analysis', {}),
            recommendations=response.get('analysis', {}).get('recommendations', []),
            wsp_guidance=response.get('analysis', {}).get('wsp_guidance', []),
            timestamp=response.get('timestamp', '')
        )

    def check_module(self, module_name: str) -> Dict[str, Any]:
        """
        Check if a module exists and get its status.

        Args:
            module_name: Name of module to check

        Returns:
            Dict with module existence and status information
        """
        # This would typically be a dedicated endpoint
        # For now, we'll search for the module
        results = self.search(f"module:{module_name}", limit=1)
        return {
            'module_name': module_name,
            'exists': len(results.code_results) > 0,
            'results': results
        }

    def get_wsp_guidance(self, topic: str) -> List[str]:
        """
        Get WSP protocol guidance for a specific topic.

        Args:
            topic: Topic to get guidance for

        Returns:
            List of WSP guidance recommendations
        """
        results = self.search(f"WSP {topic}", limit=10)

        guidance = []
        for result in results.wsp_results[:5]:  # Top 5 WSP results
            if result.content:
                # Extract key guidance points
                lines = result.content.split('\n')
                guidance.extend([line.strip() for line in lines if line.strip().startswith('-')][:3])

        return list(set(guidance))  # Remove duplicates


class FoundUpsError(Exception):
    """Base exception for FoundUps SDK errors."""
    pass


# Convenience functions for quick usage
def quick_search(base_url: str, query: str, limit: int = 5) -> SearchResponse:
    """
    Quick search function without creating a client instance.

    Args:
        base_url: FoundUps API base URL
        query: Search query
        limit: Result limit

    Returns:
        SearchResponse object
    """
    client = FoundUpsClient(base_url)
    return client.search(query, limit)


def quick_analyze(base_url: str, query: str, advisor: bool = True) -> AnalysisResult:
    """
    Quick analysis function without creating a client instance.

    Args:
        base_url: FoundUps API base URL
        query: Analysis query
        advisor: Whether to include advisor guidance

    Returns:
        AnalysisResult object
    """
    client = FoundUpsClient(base_url)
    return client.analyze(query, advisor)


# CLI interface for the SDK
def main():
    """Command-line interface for FoundUps SDK."""
    import argparse

    parser = argparse.ArgumentParser(description="FoundUps SDK CLI")
    parser.add_argument('--url', required=True, help='FoundUps API base URL')
    parser.add_argument('--search', help='Search query')
    parser.add_argument('--analyze', help='Analysis query')
    parser.add_argument('--health', action='store_true', help='Check system health')
    parser.add_argument('--limit', type=int, default=5, help='Result limit')

    args = parser.parse_args()

    client = FoundUpsClient(args.url)

    try:
        if args.health:
            status = client.health_check()
            print(f"✅ System Health: {status}")

        elif args.search:
            results = client.search(args.search, args.limit)
            print(f"🔍 Search Results for '{args.search}':")
            print(f"   Total: {results.total_results} results")
            print(f"   Code hits: {len(results.code_results)}")
            print(f"   WSP hits: {len(results.wsp_results)}")

            if results.code_results:
                print("\n📝 Top Code Results:")
                for i, result in enumerate(results.code_results[:3], 1):
                    print(f"   {i}. {result.location} (similarity: {result.similarity})")

        elif args.analyze:
            analysis = client.analyze(args.analyze)
            print(f"🤖 AI Analysis for '{args.analyze}':")
            print(f"   Recommendations: {len(analysis.recommendations)}")
            print(f"   WSP Guidance: {len(analysis.wsp_guidance)}")

            if analysis.recommendations:
                print("\n💡 Key Recommendations:")
                for rec in analysis.recommendations[:3]:
                    print(f"   • {rec}")

        else:
            print("Use --search, --analyze, or --health")

    except FoundUpsError as e:
        print(f"❌ Error: {e}")
        exit(1)


if __name__ == '__main__':
    main()
