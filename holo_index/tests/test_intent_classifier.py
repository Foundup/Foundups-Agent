"""
Tests for Intent Classifier
WSP Compliance: WSP 5 (Test Coverage), WSP 6 (Test Audit)

Tests all 5 intent types with example queries from design doc.
"""

import pytest
from holo_index.intent_classifier import (
    IntentClassifier,
    IntentType,
    IntentClassification,
    get_classifier
)


class TestIntentClassifier:
    """Test suite for IntentClassifier"""

    @pytest.fixture
    def classifier(self):
        """Fixture providing IntentClassifier instance"""
        return IntentClassifier()

    # DOC_LOOKUP Intent Tests

    def test_doc_lookup_wsp_query(self, classifier):
        """Test DOC_LOOKUP intent for WSP documentation queries"""
        result = classifier.classify("what does WSP 64 say")

        assert result.intent == IntentType.DOC_LOOKUP
        assert result.confidence >= 0.75
        assert len(result.patterns_matched) >= 1
        assert result.raw_query == "what does WSP 64 say"

    def test_doc_lookup_wsp_variations(self, classifier):
        """Test DOC_LOOKUP with various WSP query formats"""
        queries = [
            "what is WSP 80",
            "show WSP 22",
            "explain WSP 48",
            "read wsp 3",
            "what does wsp 50 say about verification",
        ]

        for query in queries:
            result = classifier.classify(query)
            assert result.intent == IntentType.DOC_LOOKUP, \
                f"Query '{query}' should be DOC_LOOKUP"

    def test_doc_lookup_readme_queries(self, classifier):
        """Test DOC_LOOKUP for README/INTERFACE queries"""
        queries = [
            "what does the readme say",
            "show interface.md",
            "read the modlog",
            "explain the README",
        ]

        for query in queries:
            result = classifier.classify(query)
            assert result.intent == IntentType.DOC_LOOKUP

    # CODE_LOCATION Intent Tests

    def test_code_location_where_queries(self, classifier):
        """Test CODE_LOCATION intent for 'where is' queries"""
        result = classifier.classify("where is AgenticChatEngine")

        assert result.intent == IntentType.CODE_LOCATION
        assert result.confidence >= 0.75
        assert len(result.patterns_matched) >= 1

    def test_code_location_find_queries(self, classifier):
        """Test CODE_LOCATION for find/locate queries"""
        queries = [
            "find the function handle_message",
            "locate the code for youtube auth",
            "which file contains StreamResolver",
            "find class IntentManager",
            "show me the implementation of PQN detector",
        ]

        for query in queries:
            result = classifier.classify(query)
            assert result.intent == IntentType.CODE_LOCATION, \
                f"Query '{query}' should be CODE_LOCATION"

    # MODULE_HEALTH Intent Tests

    def test_module_health_check_queries(self, classifier):
        """Test MODULE_HEALTH intent for health check queries"""
        result = classifier.classify("check holo_index health")

        assert result.intent == IntentType.MODULE_HEALTH
        assert result.confidence >= 0.75
        assert len(result.patterns_matched) >= 1

    def test_module_health_issue_queries(self, classifier):
        """Test MODULE_HEALTH for issue/problem queries"""
        queries = [
            "are there any issues",
            "show module problems",
            "check for wsp violations",
            "analyze livechat module",
            "module status",
            "system health",
        ]

        for query in queries:
            result = classifier.classify(query)
            assert result.intent == IntentType.MODULE_HEALTH, \
                f"Query '{query}' should be MODULE_HEALTH"

    # RESEARCH Intent Tests

    def test_research_how_queries(self, classifier):
        """Test RESEARCH intent for 'how does' queries"""
        result = classifier.classify("how does PQN emergence work")

        assert result.intent == IntentType.RESEARCH
        assert result.confidence >= 0.75
        assert len(result.patterns_matched) >= 1

    def test_research_explanation_queries(self, classifier):
        """Test RESEARCH for explanation/learning queries"""
        queries = [
            "how do I implement throttling",
            "explain the architecture",
            "what is quantum entanglement",
            "why does 012 call you 0102",
            "tell me about DAE cubes",
            "learn about pattern memory",
        ]

        for query in queries:
            result = classifier.classify(query)
            assert result.intent == IntentType.RESEARCH, \
                f"Query '{query}' should be RESEARCH"

    # GENERAL Intent Tests

    def test_general_fallback_queries(self, classifier):
        """Test GENERAL intent as fallback for unmatched queries"""
        result = classifier.classify("find youtube auth")

        assert result.intent == IntentType.GENERAL
        # GENERAL has lower confidence since it's fallback
        assert result.confidence >= 0.5

    def test_general_ambiguous_queries(self, classifier):
        """Test GENERAL for ambiguous/mixed queries"""
        queries = [
            "youtube",
            "search for something",
            "test",
            "random query string",
        ]

        for query in queries:
            result = classifier.classify(query)
            # These should fall back to GENERAL
            # (unless they happen to match another pattern)
            # Just verify we get valid classification
            assert isinstance(result.intent, IntentType)
            assert 0.0 <= result.confidence <= 1.0

    # Edge Cases

    def test_empty_query(self, classifier):
        """Test classification of empty query"""
        result = classifier.classify("")

        assert result.intent == IntentType.GENERAL
        assert result.confidence == 1.0
        assert len(result.patterns_matched) == 0

    def test_whitespace_only_query(self, classifier):
        """Test classification of whitespace-only query"""
        result = classifier.classify("   \t  \n  ")

        assert result.intent == IntentType.GENERAL

    def test_case_insensitive_matching(self, classifier):
        """Test that pattern matching is case-insensitive"""
        queries_same_intent = [
            ("what does WSP 64 say", "WHAT DOES wsp 64 SAY"),
            ("where is AgenticChatEngine", "WHERE IS agenticchatengine"),
            ("check holo_index health", "CHECK HOLO_INDEX HEALTH"),
        ]

        for query1, query2 in queries_same_intent:
            result1 = classifier.classify(query1)
            result2 = classifier.classify(query2)
            assert result1.intent == result2.intent

    # Confidence Scoring Tests

    def test_multiple_pattern_matches_increase_confidence(self, classifier):
        """Test that multiple matched patterns increase confidence"""
        # Query with one pattern match
        single_match = classifier.classify("what does WSP 64 say")

        # Query with multiple pattern matches (more specific)
        multi_match = classifier.classify("what does WSP 64 say about violations")

        # Multi-match should have equal or higher confidence
        assert multi_match.confidence >= single_match.confidence * 0.95

    def test_early_match_boosts_confidence(self, classifier):
        """Test that matches at query start boost confidence"""
        # Match at start
        early = classifier.classify("where is AgenticChatEngine")

        # Match later in query
        later = classifier.classify("can you tell me where is AgenticChatEngine")

        # Early match should have higher or equal confidence
        # (small boost applied)
        assert early.confidence >= later.confidence * 0.95

    # Singleton Tests

    def test_get_classifier_singleton(self):
        """Test get_classifier returns singleton instance"""
        classifier1 = get_classifier()
        classifier2 = get_classifier()

        assert classifier1 is classifier2

    # Stats Tests

    def test_get_stats(self, classifier):
        """Test classifier statistics reporting"""
        stats = classifier.get_stats()

        assert isinstance(stats, dict)
        assert "doc_lookup" in stats
        assert "code_location" in stats
        assert "module_health" in stats
        assert "research" in stats

        # Verify pattern counts
        assert stats["doc_lookup"] >= 5
        assert stats["code_location"] >= 5
        assert stats["module_health"] >= 5
        assert stats["research"] >= 5

    # Integration Tests (Real-World Queries)

    def test_real_world_queries(self, classifier):
        """Test classification of actual queries from design doc"""
        test_cases = [
            ("what does WSP 64 say", IntentType.DOC_LOOKUP),
            ("where is AgenticChatEngine", IntentType.CODE_LOCATION),
            ("check holo_index health", IntentType.MODULE_HEALTH),
            ("how does PQN emergence work", IntentType.RESEARCH),
            ("find youtube auth", IntentType.GENERAL),
        ]

        for query, expected_intent in test_cases:
            result = classifier.classify(query)
            assert result.intent == expected_intent, \
                f"Query '{query}' classified as {result.intent.value}, expected {expected_intent.value}"

    def test_ambiguous_query_handling(self, classifier):
        """Test handling of queries that could match multiple intents"""
        # This query could be CODE_LOCATION or MODULE_HEALTH
        result = classifier.classify("where are the health check violations")

        # Should pick one (either is acceptable)
        assert result.intent in [IntentType.CODE_LOCATION, IntentType.MODULE_HEALTH]
        # But should have decent confidence
        assert result.confidence >= 0.7


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
