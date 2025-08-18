"""Tests for blockchain_integration module"""

import pytest
import sys
from pathlib import Path

# Add src to path for imports
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from blockchain_integration import BlockchainIntegration


class TestBlockchainIntegration:
    def test_initialization(self):
        """Test blockchain initialization."""
        blockchain = BlockchainIntegration()
        assert len(blockchain.blocks) == 1  # Genesis block
        assert blockchain.blocks[0]["index"] == 0
        assert blockchain.blocks[0]["previous_hash"] == "0"
    
    def test_create_transaction(self):
        """Test transaction creation."""
        blockchain = BlockchainIntegration()
        result = blockchain.create_transaction("test_transaction", {"data": "test"}, "WSP_TEST")
        
        assert result["status"] == "success"
        assert "transaction_id" in result
        assert len(blockchain.transaction_pool) == 1
    
    def test_wsp_token_creation(self):
        """Test WSP token creation."""
        blockchain = BlockchainIntegration()
        result = blockchain.create_wsp_token("test_module", "infrastructure", 0.95)
        
        assert result["status"] == "success"
        assert "token_id" in result
        assert result["token_data"]["compliance_score"] == 0.95
    
    def test_blockchain_stats(self):
        """Test blockchain statistics."""
        blockchain = BlockchainIntegration()
        blockchain.create_wsp_token("test_module", "infrastructure", 0.90)
        
        stats = blockchain.get_blockchain_stats()
        
        assert stats["status"] == "success"
        assert stats["blockchain_stats"]["total_blocks"] == 1
        assert stats["blockchain_stats"]["wsp_tokens_issued"] == 1 