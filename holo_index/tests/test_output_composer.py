"""
Tests for Output Composer
WSP Compliance: WSP 5 (Test Coverage), WSP 6 (Test Audit)

Tests structured output composition and alert deduplication.
"""

import pytest
from holo_index.output_composer import (
    OutputComposer,
    ComposedOutput,
    get_composer
)
from holo_index.intent_classifier import IntentType


class TestOutputComposer:
    """Test suite for OutputComposer"""

    @pytest.fixture
    def composer(self):
        """Fixture providing OutputComposer instance"""
        return OutputComposer()

    @pytest.fixture
    def sample_findings(self):
        """Sample findings from component execution"""
        return """[HOLODAE-INTELLIGENCE] Data-driven analysis
[SEMANTIC] 10 files across 3 modules
[HEALTH][VIOLATION] holo_index/docs missing INTERFACE.md (WSP 22)
[HEALTH][OK] modules/communication/livechat documentation complete
[SIZE][WARNING] FOUND large file modules\\communication\\livechat\\src\\livechat_core.py (1097 lines)
[MODULE][FOUND] modules/communication/livechat contains 159 python files with 65 tests
[PATTERN] Found documentation gap in holo_index/docs: INTERFACE.md
WSP 64: Violation Prevention Protocol
Purpose: Establish systematic checks to prevent WSP violations
Key Protocols: Pre-Action Verification, WSP Master Index consultation"""

    @pytest.fixture
    def sample_alerts(self):
        """Sample alert list with duplicates"""
        alerts = []
        # 87 identical ModLog warnings
        for i in range(87):
            alerts.append(f"WSP_framework\\src\\ModLog.md older than document")
        # 5 orphan file warnings
        for i in range(5):
            alerts.append(f"modules\\test_file_{i}.py lacks matching tests")
        # 1 critical violation
        alerts.append("VIOLATION: Missing required documentation")
        return alerts

    # Composition Tests

    def test_compose_doc_lookup_intent(self, composer, sample_findings):
        """Test composition for DOC_LOOKUP intent"""
        result = composer.compose(
            intent=IntentType.DOC_LOOKUP,
            findings=sample_findings,
            query="what does WSP 64 say"
        )

        assert isinstance(result, ComposedOutput)
        assert "[INTENT: DOC_LOOKUP]" in result.full_output
        assert "[FINDINGS]" in result.full_output
        # Should filter out noise like [SEMANTIC], [SIZE]
        assert "[SEMANTIC]" not in result.findings_section
        assert "WSP 64" in result.findings_section

    def test_compose_code_location_intent(self, composer, sample_findings):
        """Test composition for CODE_LOCATION intent"""
        result = composer.compose(
            intent=IntentType.CODE_LOCATION,
            findings=sample_findings,
            query="where is AgenticChatEngine"
        )

        assert "[INTENT: CODE_LOCATION]" in result.full_output
        assert "[FINDINGS]" in result.full_output
        # Should focus on file locations
        assert "modules/communication/livechat" in result.findings_section or "files" in result.findings_section.lower()

    def test_compose_module_health_intent(self, composer, sample_findings):
        """Test composition for MODULE_HEALTH intent"""
        result = composer.compose(
            intent=IntentType.MODULE_HEALTH,
            findings=sample_findings,
            query="check holo_index health"
        )

        assert "[INTENT: MODULE_HEALTH]" in result.full_output
        assert "[FINDINGS]" in result.full_output
        # Should include health violations
        assert "VIOLATION" in result.findings_section or "missing" in result.findings_section.lower()

    def test_compose_research_intent_with_mcp(self, composer, sample_findings):
        """Test composition for RESEARCH intent with MCP results"""
        mcp_results = "Found 3 relevant papers on quantum neural networks"

        result = composer.compose(
            intent=IntentType.RESEARCH,
            findings=sample_findings,
            mcp_results=mcp_results,
            query="how does PQN emergence work"
        )

        assert "[INTENT: RESEARCH]" in result.full_output
        assert "[FINDINGS]" in result.full_output
        assert "[MCP RESEARCH]" in result.full_output
        assert "quantum neural networks" in result.mcp_section

    def test_compose_general_intent(self, composer, sample_findings):
        """Test composition for GENERAL intent"""
        result = composer.compose(
            intent=IntentType.GENERAL,
            findings=sample_findings,
            query="find youtube auth"
        )

        assert "[INTENT: GENERAL]" in result.full_output
        assert "[FINDINGS]" in result.full_output

    # Alert Deduplication Tests

    def test_deduplicate_alerts(self, composer, sample_alerts):
        """Test alert deduplication reduces 87 warnings to 1 line"""
        deduplicated = composer._deduplicate_alerts(sample_alerts)

        # Should have 3 summary lines (ModLog, orphans, violation)
        lines = deduplicated.split('\n')
        assert len(lines) <= 5  # Much less than 93 original alerts

        # Should contain summary for ModLog warnings
        assert any("87" in line for line in lines)
        assert any("ModLog" in line for line in lines)

    def test_deduplicate_single_alert(self, composer):
        """Test single alert is shown as-is"""
        alerts = ["Single warning message"]
        deduplicated = composer._deduplicate_alerts(alerts)

        assert "Single warning message" in deduplicated

    def test_deduplicate_empty_alerts(self, composer):
        """Test empty alerts list returns 'No alerts'"""
        deduplicated = composer._deduplicate_alerts([])
        assert "No alerts" in deduplicated

    def test_deduplicate_multiple_types(self, composer):
        """Test deduplication groups by alert type"""
        alerts = [
            "ModLog.md older than document",
            "ModLog.md older than document",
            "ModLog.md older than document",
            "Missing INTERFACE.md",
            "Missing README.md",
        ]

        deduplicated = composer._deduplicate_alerts(alerts)
        lines = deduplicated.split('\n')

        # Should have 2 groups: ModLog (3x) and Missing (2x)
        assert len(lines) == 2
        assert any("3" in line for line in lines)
        assert any("2" in line for line in lines)

    # Alert Extraction Tests

    def test_extract_alert_type_modlog(self, composer):
        """Test extracting ModLog alert type"""
        alert = "WSP_framework\\src\\ModLog.md older than document"
        alert_type = composer._extract_alert_type(alert)

        assert "ModLog outdated" in alert_type

    def test_extract_alert_type_missing_file(self, composer):
        """Test extracting missing file alert type"""
        alert = "holo_index/docs missing INTERFACE.md"
        alert_type = composer._extract_alert_type(alert)

        assert "missing" in alert_type.lower()

    def test_extract_alert_type_large_file(self, composer):
        """Test extracting large file alert type"""
        alert = "Large implementation file detected: modules\\livechat\\src\\livechat_core.py"
        alert_type = composer._extract_alert_type(alert)

        assert "Large file" in alert_type

    # Section Building Tests

    def test_build_intent_section(self, composer):
        """Test intent section includes description"""
        section = composer._build_intent_section(IntentType.DOC_LOOKUP, "what does WSP 64 say")

        assert "[INTENT: DOC_LOOKUP]" in section
        assert "Documentation lookup" in section or "docs" in section.lower()

    def test_build_alerts_section_suppresses_for_focused_intents(self, composer, sample_alerts):
        """Test alerts are suppressed for DOC_LOOKUP and CODE_LOCATION"""
        # DOC_LOOKUP should suppress non-critical alerts
        section = composer._build_alerts_section(sample_alerts, IntentType.DOC_LOOKUP)

        # Should only show critical alerts or "No critical issues"
        assert "No critical issues" in section or "VIOLATION" in section
        # Should NOT show all 87 ModLog warnings
        assert section.count("ModLog") <= 1  # Summary or suppressed

    def test_build_alerts_section_shows_for_health_intent(self, composer, sample_alerts):
        """Test alerts are shown for MODULE_HEALTH intent"""
        section = composer._build_alerts_section(sample_alerts, IntentType.MODULE_HEALTH)

        # Should include deduplicated alerts
        assert "87" in section or "ModLog" in section

    def test_mcp_section_only_for_research(self, composer):
        """Test MCP section is only included for RESEARCH intent"""
        mcp_results = "Research results here"

        # RESEARCH intent - should include MCP
        result_research = composer.compose(
            intent=IntentType.RESEARCH,
            findings="Some findings",
            mcp_results=mcp_results
        )
        assert result_research.mcp_section is not None
        assert "[MCP RESEARCH]" in result_research.full_output

        # DOC_LOOKUP intent - should NOT include MCP
        result_doc = composer.compose(
            intent=IntentType.DOC_LOOKUP,
            findings="Some findings",
            mcp_results=mcp_results
        )
        assert result_doc.mcp_section is None
        assert "[MCP RESEARCH]" not in result_doc.full_output

    # Content Extraction Tests

    def test_extract_documentation_content(self, composer, sample_findings):
        """Test documentation content extraction"""
        content = composer._extract_documentation_content(sample_findings)

        # Should include WSP content
        assert "WSP 64" in content
        # Should exclude noise
        assert "[SEMANTIC]" not in content
        assert "[SIZE][WARNING]" not in content

    def test_extract_file_locations(self, composer, sample_findings):
        """Test file location extraction"""
        content = composer._extract_file_locations(sample_findings)

        # Should include module paths
        assert "modules/communication" in content or "livechat" in content

    def test_extract_health_findings(self, composer, sample_findings):
        """Test health findings extraction"""
        content = composer._extract_health_findings(sample_findings)

        # Should include violations
        assert "VIOLATION" in content or "missing" in content

    # Integration Tests

    def test_real_world_doc_lookup_query(self, composer):
        """Test real-world DOC_LOOKUP composition"""
        findings = """[HEALTH][VIOLATION] holo_index/docs missing INTERFACE.md
WSP 64: Violation Prevention Protocol
Purpose: Establish systematic checks to prevent WSP violations before they occur
Key Protocols:
1. Pre-Action Verification (WSP 50 integration)
2. WSP Master Index consultation before new WSP creation"""

        alerts = ["ModLog outdated"] * 87 + ["Missing doc"] * 5

        result = composer.compose(
            intent=IntentType.DOC_LOOKUP,
            findings=findings,
            alerts=alerts,
            query="what does WSP 64 say"
        )

        # Verify structured output
        assert "[INTENT: DOC_LOOKUP]" in result.full_output
        assert "WSP 64" in result.full_output
        assert "[ALERTS]" in result.full_output

        # Verify deduplication
        alert_section_lines = result.alerts_section.split('\n') if result.alerts_section else []
        assert len(alert_section_lines) < 10  # Much less than 92 original alerts

    def test_token_efficiency_improvement(self, composer, sample_findings, sample_alerts):
        """Test that composed output is significantly shorter"""
        # Simulate unstructured output (all findings + all alerts)
        unstructured_length = len(sample_findings) + sum(len(a) for a in sample_alerts)

        # Compose structured output
        result = composer.compose(
            intent=IntentType.DOC_LOOKUP,
            findings=sample_findings,
            alerts=sample_alerts
        )

        structured_length = len(result.full_output)

        # Structured output should be significantly shorter
        reduction = (unstructured_length - structured_length) / unstructured_length
        assert reduction > 0.5  # At least 50% reduction

    # Singleton Tests

    def test_get_composer_singleton(self):
        """Test get_composer returns singleton instance"""
        composer1 = get_composer()
        composer2 = get_composer()

        assert composer1 is composer2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
