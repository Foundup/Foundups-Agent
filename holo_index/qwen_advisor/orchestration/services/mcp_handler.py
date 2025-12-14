import datetime
from typing import Dict, List, Any, Optional

class MCPHandler:
    """
    Handles MCP tool calls, learning, and integration for HoloDAE.
    """

    def __init__(self, mcp_client=None, logger=None):
        self.mcp_client = mcp_client
        self.logger = logger
        self._mcp_learning_history = []

    def call_research_mcp_tools(self, query: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Call ricDAE MCP tools for research-augmented analysis
        """
        if not self.mcp_client:
            self._log("MCP-SKIP", "[LINK] MCP client not available")
            return []

        insights = []

        try:
            # Call literature_search for relevant queries
            if self._should_call_literature_search(query):
                self._log("MCP-TOOL", "[SEARCH] Calling literature_search MCP tool")
                search_results = self.mcp_client.literature_search(query, limit=5)
                if search_results:
                    insights.extend(search_results)
                    self._log("MCP-RESULT", f"[BOOKS] Found {len(search_results)} literature results")
                    self._record_mcp_tool_call("literature_search", query, len(search_results))

            # Call trend_digest for research queries
            if self._should_call_trend_digest(query, context):
                self._log("MCP-TOOL", "[UP] Calling trend_digest MCP tool")
                trend_results = self.mcp_client.trend_digest(days=7)
                if trend_results:
                    insights.extend(trend_results)
                    self._log("MCP-RESULT", f"[DATA] Found {len(trend_results)} trend insights")
                    self._record_mcp_tool_call("trend_digest", query, len(trend_results))

            # Call research_update to check for new research
            if self._should_call_research_update(query):
                self._log("MCP-TOOL", "🆕 Calling research_update MCP tool")
                update_results = self.mcp_client.research_update()
                if update_results:
                    insights.extend(update_results)
                    self._log("MCP-RESULT", f"[REFRESH] Found {len(update_results)} research updates")
                    self._record_mcp_tool_call("research_update", query, len(update_results))

        except Exception as e:
            self._log("MCP-ERROR", f"[LINK] MCP tool call failed: {e}")

        return insights

    def learn_from_mcp_usage(self, query: str, mcp_insights: List[Dict[str, Any]], context: Dict[str, Any]):
        """
        RECURSIVE LEARNING: Learn from successful MCP tool usage
        """
        try:
            learning_insights = {
                "query": query,
                "mcp_tools_used": [],
                "insights_found": len(mcp_insights),
                "tool_effectiveness": {},
                "query_patterns": self._extract_query_patterns(query),
                "timestamp": datetime.datetime.now().isoformat()
            }

            if self._should_call_literature_search(query):
                learning_insights["mcp_tools_used"].append("literature_search")
                literature_results = [i for i in mcp_insights if i.get("type") == "literature_result"]
                learning_insights["tool_effectiveness"]["literature_search"] = len(literature_results)

            if self._should_call_trend_digest(query, context):
                learning_insights["mcp_tools_used"].append("trend_digest")
                trend_results = [i for i in mcp_insights if i.get("type") == "trend_analysis"]
                learning_insights["tool_effectiveness"]["trend_digest"] = len(trend_results)

            if self._should_call_research_update(query):
                learning_insights["mcp_tools_used"].append("research_update")
                update_results = [i for i in mcp_insights if i.get("type") == "research_update"]
                learning_insights["tool_effectiveness"]["research_update"] = len(update_results)

            self._store_mcp_learning(learning_insights)
            self._log("MCP-LEARNING", f"[AI] Learned from {len(learning_insights['mcp_tools_used'])} MCP tools")

        except Exception as e:
            self._log("MCP-LEARNING-ERROR", f"Failed to learn from MCP usage: {e}")

    def _should_call_literature_search(self, query: str) -> bool:
        research_keywords = ['research', 'paper', 'study', 'neural', 'ai', 'ml', 'algorithm']
        return any(keyword in query.lower() for keyword in research_keywords)

    def _should_call_trend_digest(self, query: str, context: Dict[str, Any]) -> bool:
        trend_keywords = ['trend', 'latest', 'recent', 'new', 'update', 'progress']
        return any(keyword in query.lower() for keyword in trend_keywords)

    def _should_call_research_update(self, query: str) -> bool:
        update_keywords = ['update', 'new', 'latest', 'recent', 'fresh']
        return any(keyword in query.lower() for keyword in update_keywords)

    def _extract_query_patterns(self, query: str) -> List[str]:
        patterns = []
        query_lower = query.lower()
        if any(word in query_lower for word in ['research', 'paper', 'study']):
            patterns.append("academic_research")
        if any(word in query_lower for word in ['neural', 'ai', 'ml', 'algorithm']):
            patterns.append("ai_technology")
        if any(word in query_lower for word in ['trend', 'latest', 'recent']):
            patterns.append("current_trends")
        if any(word in query_lower for word in ['quantum', 'hybrid']):
            patterns.append("advanced_tech")
        return patterns

    def _store_mcp_learning(self, learning_insights: Dict[str, Any]):
        self._mcp_learning_history.append(learning_insights)
        if len(self._mcp_learning_history) > 100:
            self._mcp_learning_history = self._mcp_learning_history[-100:]

    def _record_mcp_tool_call(self, tool_name: str, query: str, result_count: int):
        # In a real implementation, this would callback to the coordinator
        pass

    def _log(self, tag: str, message: str):
        if self.logger:
            self.logger(tag, message)
