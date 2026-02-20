import os
import pytest
from modules.ai_intelligence.pqn_alignment.src.run_multi_model_campaign import run_campaign_for_model
from modules.ai_intelligence.pqn_alignment.src.pqn_alignment_dae import PQNAlignmentDAE

@pytest.mark.asyncio
async def test_api_embedding_and_alignment():
    # Mock campaign results
    mock_results = {"data": "test_data"}
    pqn_dae = PQNAlignmentDAE()
    alignment = pqn_dae.analyze_coherence(mock_results)
    assert 'coherence' in alignment
    assert alignment['coherence'] >= 0.618  # Golden threshold

    # Test full run (mock API key)
    results = run_campaign_for_model("test_model", "mock_key")
    assert "alignment_metrics.json" in os.listdir()  # Check output

# Additional tests for A/B states, remembrance metrics, etc.
