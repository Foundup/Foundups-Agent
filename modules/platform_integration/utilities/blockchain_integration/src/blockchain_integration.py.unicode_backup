# Blockchain Integration Module
# WSP Integration: Decentralized infrastructure and token management

import json
import time
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid

class BlockchainIntegration:
    def __init__(self):
        """Initialize blockchain integration for decentralized infrastructure."""
        self.project_root = Path(__file__).resolve().parent.parent.parent.parent.parent
        self.blockchain_data = self.project_root / "modules" / "blockchain"
        self.transaction_pool = []
        self.blocks = []
        self.wsp_tokens = {}
        
        # Initialize genesis block
        self._create_genesis_block()
        
        print("Blockchain Integration initialized for decentralized WSP infrastructure.")

    def _create_genesis_block(self):
        """Create the genesis block for WSP blockchain."""
        genesis_block = {
            "index": 0,
            "timestamp": datetime.now().isoformat(),
            "transactions": [{
                "type": "genesis",
                "data": "WSP Framework Genesis Block",
                "wsp_compliance": "WSP_CORE"
            }],
            "previous_hash": "0",
            "nonce": 0,
            "hash": ""
        }
        
        # Calculate genesis hash
        genesis_block["hash"] = self._calculate_hash(genesis_block)
        self.blocks.append(genesis_block)

    def _calculate_hash(self, block: Dict) -> str:
        """Calculate SHA-256 hash for a block."""
        block_string = json.dumps({
            "index": block["index"],
            "timestamp": block["timestamp"], 
            "transactions": block["transactions"],
            "previous_hash": block["previous_hash"],
            "nonce": block["nonce"]
        }, sort_keys=True)
        
        return hashlib.sha256(block_string.encode()).hexdigest()

    def create_transaction(self, transaction_type: str, data: Dict, wsp_protocol: str = "") -> Dict:
        """
        Create a new transaction for the WSP blockchain.
        
        Args:
            transaction_type: Type of transaction (module_creation, compliance_check, etc.)
            data: Transaction data
            wsp_protocol: Associated WSP protocol reference
            
        Returns:
            Dict with transaction details
        """
        transaction = {
            "id": str(uuid.uuid4()),
            "type": transaction_type,
            "timestamp": datetime.now().isoformat(),
            "data": data,
            "wsp_protocol": wsp_protocol,
            "status": "pending"
        }
        
        self.transaction_pool.append(transaction)
        
        print(f"📝 Created transaction: {transaction_type} ({transaction['id'][:8]}...)")
        
        return {
            "status": "success",
            "transaction_id": transaction["id"],
            "transaction": transaction
        }

    def mine_block(self, difficulty: int = 2) -> Dict:
        """
        Mine a new block with pending transactions.
        
        Args:
            difficulty: Mining difficulty (number of leading zeros required)
            
        Returns:
            Dict with mining results
        """
        if not self.transaction_pool:
            return {
                "status": "error",
                "message": "No pending transactions to mine"
            }
        
        print(f"⛏️  Mining new block with {len(self.transaction_pool)} transactions...")
        
        # Create new block
        new_block = {
            "index": len(self.blocks),
            "timestamp": datetime.now().isoformat(),
            "transactions": self.transaction_pool.copy(),
            "previous_hash": self.blocks[-1]["hash"],
            "nonce": 0,
            "hash": ""
        }
        
        # Mine the block (find valid nonce)
        target = "0" * difficulty
        start_time = time.time()
        
        while True:
            new_block["hash"] = self._calculate_hash(new_block)
            
            if new_block["hash"].startswith(target):
                mining_time = time.time() - start_time
                print(f"✅ Block mined! Hash: {new_block['hash'][:16]}... (took {mining_time:.2f}s)")
                break
            
            new_block["nonce"] += 1
        
        # Add block to chain
        self.blocks.append(new_block)
        
        # Clear transaction pool
        mined_transactions = len(self.transaction_pool)
        self.transaction_pool.clear()
        
        return {
            "status": "success",
            "block_index": new_block["index"],
            "block_hash": new_block["hash"],
            "transactions_mined": mined_transactions,
            "mining_time": mining_time,
            "nonce": new_block["nonce"]
        }

    def validate_chain(self) -> Dict:
        """Validate the entire blockchain for integrity."""
        print("🔍 Validating blockchain integrity...")
        
        validation_results = {
            "valid": True,
            "errors": [],
            "blocks_validated": 0,
            "total_transactions": 0
        }
        
        for i in range(1, len(self.blocks)):
            current_block = self.blocks[i]
            previous_block = self.blocks[i - 1]
            
            validation_results["blocks_validated"] += 1
            validation_results["total_transactions"] += len(current_block["transactions"])
            
            # Validate current block hash
            calculated_hash = self._calculate_hash(current_block)
            if current_block["hash"] != calculated_hash:
                validation_results["valid"] = False
                validation_results["errors"].append(f"Block {i}: Invalid hash")
            
            # Validate previous hash reference
            if current_block["previous_hash"] != previous_block["hash"]:
                validation_results["valid"] = False
                validation_results["errors"].append(f"Block {i}: Invalid previous hash reference")
        
        status = "valid" if validation_results["valid"] else "invalid"
        print(f"{'✅' if validation_results['valid'] else '❌'} Blockchain validation: {status}")
        
        return {
            "status": "success",
            "blockchain_status": status,
            "validation": validation_results
        }

    def create_wsp_token(self, module_name: str, domain: str, compliance_score: float) -> Dict:
        """
        Create a WSP compliance token for a module.
        
        Args:
            module_name: Name of the module
            domain: Module domain
            compliance_score: WSP compliance score (0.0-1.0)
            
        Returns:
            Dict with token creation results
        """
        token_id = f"WSP_{domain}_{module_name}_{int(time.time())}"
        
        token_data = {
            "token_id": token_id,
            "module": f"{domain}/{module_name}",
            "compliance_score": compliance_score,
            "created": datetime.now().isoformat(),
            "wsp_protocols": ["WSP_49", "WSP_60"],  # Default compliance
            "status": "active"
        }
        
        # Store token
        self.wsp_tokens[token_id] = token_data
        
        # Create blockchain transaction
        transaction_result = self.create_transaction(
            "wsp_token_creation",
            token_data,
            "WSP_TOKENIZATION"
        )
        
        print(f"🪙 Created WSP token: {token_id} (score: {compliance_score})")
        
        return {
            "status": "success",
            "token_id": token_id,
            "token_data": token_data,
            "transaction_id": transaction_result["transaction_id"]
        }

    def get_module_tokens(self, module_path: str) -> Dict:
        """Get all WSP tokens for a specific module."""
        module_tokens = {}
        
        for token_id, token_data in self.wsp_tokens.items():
            if token_data["module"] == module_path:
                module_tokens[token_id] = token_data
        
        return {
            "status": "success",
            "module": module_path,
            "tokens": module_tokens,
            "token_count": len(module_tokens)
        }

    def get_blockchain_stats(self) -> Dict:
        """Get comprehensive blockchain statistics."""
        total_transactions = sum(len(block["transactions"]) for block in self.blocks)
        
        # Calculate compliance distribution
        compliance_scores = []
        for token_data in self.wsp_tokens.values():
            compliance_scores.append(token_data["compliance_score"])
        
        avg_compliance = sum(compliance_scores) / len(compliance_scores) if compliance_scores else 0
        
        return {
            "status": "success",
            "blockchain_stats": {
                "total_blocks": len(self.blocks),
                "total_transactions": total_transactions,
                "pending_transactions": len(self.transaction_pool),
                "wsp_tokens_issued": len(self.wsp_tokens),
                "average_compliance_score": round(avg_compliance, 3),
                "genesis_timestamp": self.blocks[0]["timestamp"] if self.blocks else None,
                "latest_block_hash": self.blocks[-1]["hash"][:16] + "..." if self.blocks else None
            }
        }

    def export_blockchain(self) -> Dict:
        """Export blockchain data for backup or analysis."""
        blockchain_export = {
            "export_timestamp": datetime.now().isoformat(),
            "blockchain_version": "WSP_1.0",
            "blocks": self.blocks,
            "wsp_tokens": self.wsp_tokens,
            "pending_transactions": self.transaction_pool
        }
        
        # Save to file
        export_file = self.blockchain_data / f"blockchain_export_{int(time.time())}.json"
        
        # Ensure directory exists
        export_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(export_file, 'w', encoding="utf-8") as f:
            json.dump(blockchain_export, f, indent=2)
        
        return {
            "status": "success",
            "export_file": str(export_file),
            "blocks_exported": len(self.blocks),
            "tokens_exported": len(self.wsp_tokens),
            "export_size": export_file.stat().st_size if export_file.exists() else 0
        }

    def import_blockchain(self, import_file: Path) -> Dict:
        """Import blockchain data from file."""
        if not import_file.exists():
            return {
                "status": "error",
                "message": f"Import file not found: {import_file}"
            }
        
        try:
            with open(import_file, 'r', encoding="utf-8") as f:
                blockchain_data = json.load(f)
            
            self.blocks = blockchain_data.get("blocks", [])
            self.wsp_tokens = blockchain_data.get("wsp_tokens", {})
            self.transaction_pool = blockchain_data.get("pending_transactions", [])
            
            return {
                "status": "success",
                "blocks_imported": len(self.blocks),
                "tokens_imported": len(self.wsp_tokens),
                "pending_transactions": len(self.transaction_pool)
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Import failed: {str(e)}"
            }

    def create_smart_contract(self, contract_name: str, contract_code: str, wsp_integration: str) -> Dict:
        """
        Create a smart contract for WSP protocol automation.
        
        Args:
            contract_name: Name of the smart contract
            contract_code: Contract logic/code
            wsp_integration: WSP protocol integration details
            
        Returns:
            Dict with contract creation results
        """
        contract_id = f"CONTRACT_{contract_name}_{int(time.time())}"
        
        contract_data = {
            "contract_id": contract_id,
            "name": contract_name,
            "code": contract_code,
            "wsp_integration": wsp_integration,
            "created": datetime.now().isoformat(),
            "status": "deployed",
            "executions": 0
        }
        
        # Create deployment transaction
        transaction_result = self.create_transaction(
            "smart_contract_deployment",
            contract_data,
            wsp_integration
        )
        
        print(f"📜 Deployed smart contract: {contract_name} ({contract_id})")
        
        return {
            "status": "success",
            "contract_id": contract_id,
            "contract_data": contract_data,
            "deployment_transaction": transaction_result["transaction_id"]
        } 