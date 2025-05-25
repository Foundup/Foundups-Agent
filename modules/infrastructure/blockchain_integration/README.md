# Blockchain Module - Web3 Integration System

This module implements the blockchain integration for the FoundUps Agent, enabling token rewards, smart contract interactions, and decentralized storage.

## Architecture Overview

### Web3 Components
```
blockchain/
├── providers/           # Web3 Provider Interfaces
│   ├── ethereum/       # Ethereum Mainnet & Testnets
│   ├── polygon/        # Polygon PoS & zkEVM
│   ├── solana/         # Solana Integration
│   ├── arbitrum/       # Arbitrum One & Nova
│   ├── optimism/       # OP Mainnet
│   └── custom/         # Custom Chain Support
├── contracts/          # Smart Contract Interfaces
├── tokens/            # Token Management
├── rewards/           # Reward Distribution Logic
└── storage/           # Decentralized Storage
```

## Token System (UP$)

### Token Architecture
1. **FoundUps (UP$) Token**
   - ERC-20 Standard
   - Initial Supply: 100M
   - Distribution: Community-driven
   - Use Case: Engagement rewards, governance

2. **Experience Points (XP)**
   - Non-transferable points
   - Earned through participation
   - Levels system
   - Unlocks features

### Smart Contracts
```solidity
// FoundUps Token Contract
contract FoundUps is ERC20, Ownable {
    // Reward Mechanisms
    function rewardEngagement(address user, uint256 amount) external {
        require(isAuthorized(msg.sender), "Unauthorized");
        _mint(user, amount);
    }
    
    // Governance Features
    function propose(string calldata proposal) external {
        require(balanceOf(msg.sender) >= proposalThreshold, "Insufficient tokens");
        // Create proposal
    }
}
```

## Reward System

### Engagement Categories & Rewards

1. **Active Participation**
   - Chat engagement: 1-5 UP$
   - Quality responses: 5-20 UP$
   - Fallacy corrections: 10-30 UP$
   - Community help: 15-50 UP$

2. **Content Creation**
   - Original content: 50-200 UP$
   - Verified facts: 20-100 UP$
   - Tutorial creation: 100-500 UP$

### Distribution Logic
```python
class RewardDistributor:
    def calculate_reward(self, action_type, quality_score):
        return {
            "token_amount": float,    # UP$ tokens to award
            "xp_points": int,         # Experience points
            "multiplier": float,      # Based on user level
            "bonus": float           # Special event bonus
        }
```

## Transaction Management

### Gas Optimization
```python
class GasManager:
    def estimate_gas(self, transaction):
        return {
            "estimated_gas": Wei,
            "max_fee": Wei,
            "priority_fee": Wei,
            "optimal_timing": datetime
        }
```

### Batch Processing
```python
class RewardBatcher:
    def batch_rewards(self, rewards_list):
        """Batch multiple rewards into a single transaction"""
        return {
            "merkle_root": bytes32,
            "proof_data": List[bytes32],
            "total_tokens": int,
            "recipients": List[address]
        }
```

## Decentralized Storage

### IPFS Integration
- Chat history archival
- Content verification
- Proof of engagement
- Metadata storage

### Storage Process
```python
class IPFSManager:
    def store_data(self, data):
        return {
            "ipfs_hash": str,
            "timestamp": int,
            "size_bytes": int,
            "retrieval_url": str
        }
```

## Configuration

Required environment variables:
```env
# Network Configuration
ETH_NETWORK=mainnet
POLYGON_NETWORK=mainnet
ARBITRUM_NETWORK=mainnet

# Contract Addresses
UP$_TOKEN_ADDRESS=0x...
REWARDS_CONTRACT=0x...
GOVERNANCE_CONTRACT=0x...

# Web3 Providers
ETH_RPC_URL=https://...
POLYGON_RPC_URL=https://...
ARBITRUM_RPC_URL=https://...

# IPFS Configuration
IPFS_GATEWAY=https://ipfs.io
IPFS_API_KEY=...

# Private Keys (Deploy Only)
DEPLOY_PRIVATE_KEY=...  # Never in production
```

## Reward Distribution Flow

1. Action Detection
2. Quality Assessment
3. Reward Calculation
4. Gas Optimization
5. Transaction Execution
6. Verification & Logging

### Example Usage
```python
from blockchain.rewards import RewardManager
from blockchain.providers import Web3Provider

async def process_reward(user_action):
    # Initialize reward manager
    reward_mgr = RewardManager(Web3Provider())
    
    # Calculate and distribute reward
    tx = await reward_mgr.process_action(
        user=user_action.address,
        action_type=user_action.type,
        quality_score=user_action.score
    )
    
    return tx.hash
```

## Security & Compliance

- Multi-sig requirements
- Rate limiting
- Anti-spam measures
- KYC compliance (if required)
- Transaction monitoring
- Audit logging

## Future Enhancements

- Cross-chain integration
- Layer 2 scaling solutions
- DAO governance implementation
- NFT achievements
- Advanced tokenomics
- Automated market making

## Dependencies

```requirements
# Web3 Core
web3>=6.0.0
eth-account>=0.8.0
eth-typing>=3.0.0
eth-utils>=2.1.0

# Smart Contracts
solidity-parser>=0.1.0
py-solc-x>=1.1.0

# IPFS
ipfs-http-client>=1.0.0
multiformats>=0.2.0

# Utils
eth-brownie>=1.19.0
eth-ape>=0.6.0
```

See `ModLog.md` for version history and `coding_rules.json` for contribution guidelines.
