# FoundUps Crypto Wallet Architecture (Testnet)

**Integration**: GotJunk purchase flow
**Environment**: Testnet (safe testing with no real funds)
**User Experience**: Fiat-first (hide crypto complexity)

---

## Overview

GotJunk integrates with FoundUps crypto wallet to enable seamless purchases. Users see familiar **fiat currency (USD)** prices, while the platform handles blockchain transactions transparently in the background.

### Key Principles

1. **User-Friendly**: No crypto knowledge required
2. **Fiat-First**: Prices displayed in USD, not crypto
3. **Testnet**: Safe testing environment with $1,000 test balance
4. **Transparent**: Users don't need to understand blockchain mechanics

---

## User Flow

### Purchase Journey

```
User browses item → Swipe right on cart item → Purchase modal shows:

┌─────────────────────────────────┐
│     Purchase Item?              │
├─────────────────────────────────┤
│  [Item Preview Image]           │
│                                 │
│  Type: 50% OFF                  │
│  Original: $10.00               │
│  Price: $5.00                   │
│                                 │
│  💰 FoundUps Wallet (Testnet)  │
│     Balance: $1,000.00          │
│                                 │
│  [Cancel]  [Confirm Purchase]   │
└─────────────────────────────────┘
```

### What Users See

- **Item preview** (from cart)
- **Classification type** (Free, Discount %, Bid)
- **Price in USD** (calculated from discount or bid)
- **Wallet balance in USD** ($1,000 testnet)
- **Simple Confirm/Cancel** buttons

### What Users DON'T See

- Private keys
- Blockchain addresses
- Gas fees
- Transaction hashes
- Crypto token names
- Wallet seed phrases

---

## Technical Architecture

### Components

#### 1. PurchaseModal Component
**Location**: `modules/foundups/gotjunk/frontend/components/PurchaseModal.tsx`

**Responsibilities**:
- Display item preview
- Show price in USD
- Display wallet balance
- Handle purchase confirmation
- Trigger wallet transaction

**Current State**: ✅ Implemented (placeholder wallet display)

#### 2. Wallet Service (TODO)
**Location**: `modules/foundups/gotjunk/frontend/services/walletService.ts`

**Responsibilities**:
```typescript
interface WalletService {
  // Get wallet balance in USD
  getBalance(): Promise<number>;

  // Execute purchase transaction
  purchase(itemId: string, priceUSD: number): Promise<{
    success: boolean;
    transactionId?: string;
    error?: string;
  }>;

  // Get transaction history
  getTransactionHistory(): Promise<Transaction[]>;

  // Convert crypto to fiat (real-time rates)
  convertToUSD(cryptoAmount: number, token: string): Promise<number>;
}
```

**Integration**: Connects to FoundUps blockchain testnet

#### 3. Blockchain Backend (TODO)
**Location**: `modules/foundups/gotjunk/backend/wallet/`

**Responsibilities**:
- Manage user wallet addresses
- Sign and broadcast transactions
- Track balances
- Handle testnet faucet (free test tokens)
- Convert between crypto and fiat

---

## Testnet Configuration

### Test Environment

| Property | Value |
|----------|-------|
| Network | FoundUps Testnet |
| Initial Balance | $1,000 USD (test tokens) |
| Token Type | TBD (e.g., USDC-test, FUSD) |
| Transaction Fee | Free (covered by testnet) |
| Reset Period | Manual (via admin panel) |

### Testnet Features

1. **Free Test Tokens**: Users get $1,000 on signup
2. **No Real Money**: All transactions use test currency
3. **Unlimited Testing**: Balances can be reset
4. **Fast Confirmations**: Testnet blocks confirm quickly
5. **Safe Experimentation**: No financial risk

---

## Price Calculation

### Classification Types

#### 1. Free Items
```typescript
classification: 'free'
price: $0.00
walletCharge: $0.00
```

#### 2. Discount Items
```typescript
classification: 'discount'
discountPercent: 25 | 50 | 75
originalPrice: $10.00 (placeholder)
price: originalPrice * (1 - discountPercent / 100)

Example: 50% OFF
  Original: $10.00
  Discount: 50%
  Final Price: $5.00
```

#### 3. Bid Items (Auction)
```typescript
classification: 'bid'
bidDurationHours: 24 | 48 | 72
startingBid: TBD
currentBid: Highest bid
price: currentBid + minIncrement
```

---

## Security Considerations

### Wallet Security

1. **Key Management**: Private keys stored server-side (not in browser)
2. **Authentication**: User login required for transactions
3. **Rate Limiting**: Prevent rapid-fire purchases
4. **Balance Validation**: Check balance before transaction
5. **Transaction Signing**: Server-side signing for security

### Testnet Safety

- ⚠️ **Never use real private keys** on testnet
- ⚠️ **Keep testnet separate** from mainnet infrastructure
- ⚠️ **Clear labels**: Always show "Testnet" badge
- ⚠️ **No real funds**: Testnet tokens have no value

---

## Implementation Phases

### Phase 1: Frontend Integration ✅
- [x] PurchaseModal component
- [x] Fiat price display
- [x] Testnet balance placeholder ($1,000)
- [x] Purchase confirmation flow

### Phase 2: Wallet Service (TODO)
- [ ] Create `walletService.ts`
- [ ] Implement `getBalance()` API
- [ ] Implement `purchase()` API
- [ ] Add transaction history
- [ ] Integrate with PurchaseModal

### Phase 3: Backend Wallet (TODO)
- [ ] Set up FoundUps testnet node
- [ ] Create wallet management API
- [ ] Implement transaction signing
- [ ] Add balance tracking
- [ ] Deploy testnet faucet

### Phase 4: Real-Time Conversion (TODO)
- [ ] Integrate crypto price feeds
- [ ] Convert testnet tokens to USD equivalent
- [ ] Update balance display dynamically
- [ ] Handle rate fluctuations

### Phase 5: Mainnet Preparation (Future)
- [ ] Security audit
- [ ] Mainnet wallet creation
- [ ] Real money testing (small amounts)
- [ ] Regulatory compliance check
- [ ] User education materials

---

## API Endpoints (Backend TODO)

### Wallet Management

```typescript
// Get user wallet balance
GET /api/wallet/balance
Response: {
  balanceUSD: 1000.00,
  balanceCrypto: 1000.0, // testnet tokens
  currency: "FUSD-test"
}

// Purchase item
POST /api/wallet/purchase
Body: {
  itemId: "item-123",
  priceUSD: 5.00
}
Response: {
  success: true,
  transactionId: "tx-abc123",
  newBalance: 995.00
}

// Get transaction history
GET /api/wallet/transactions
Response: {
  transactions: [
    {
      id: "tx-abc123",
      type: "purchase",
      itemId: "item-123",
      amount: -5.00,
      timestamp: 1699564800000,
      status: "confirmed"
    }
  ]
}

// Request testnet tokens (faucet)
POST /api/wallet/faucet
Response: {
  success: true,
  amount: 1000.00,
  newBalance: 1000.00
}
```

---

## User Education

### In-App Messaging

**On First Purchase**:
> 💰 **Your FoundUps Wallet**
>
> Your wallet has $1,000 in test funds. This is a safe testing environment - no real money is used.
>
> All prices are shown in USD for your convenience. Behind the scenes, we handle the blockchain magic!

**On Low Balance**:
> ⚠️ **Low Balance**
>
> Your test balance is running low. Need more test funds? [Request Refill]

**On Successful Purchase**:
> ✅ **Purchase Complete!**
>
> Item added to your collection. New balance: $995.00

---

## Conversion to Real Money (Future)

When moving from testnet to mainnet:

1. **Wallet Migration**: Generate real wallet for user
2. **KYC Compliance**: Verify user identity (if required by law)
3. **Fiat On-Ramp**: Allow credit card → crypto conversion
4. **Transaction Fees**: Display gas fees transparently
5. **User Agreement**: Terms of service for financial transactions

---

## Monitoring & Analytics

### Metrics to Track

- **Purchase Volume**: USD value of testnet purchases
- **Wallet Balances**: Average user balance over time
- **Transaction Success Rate**: % of successful purchases
- **Price Points**: Most common purchase amounts
- **User Confusion**: Support tickets about wallet

### Observability

- Log all wallet transactions (testnet only)
- Monitor balance inconsistencies
- Track failed purchases
- Alert on unusual activity

---

## Related Documentation

- [GotJunk DAEmon Architecture](GOTJUNK_DAEMON_ARCHITECTURE.md) - AI oversight system
- [ModLog.md](ModLog.md) - Development changelog
- [README.md](README.md) - GotJunk overview

---

## TODO: Next Steps

1. **Create `walletService.ts`** - Frontend wallet integration
2. **Design backend API** - Wallet management endpoints
3. **Set up testnet node** - FoundUps blockchain testnet
4. **Implement faucet** - $1,000 test token distribution
5. **Add transaction history UI** - Show past purchases
6. **Test purchase flow end-to-end** - Verify blockchain integration

---

**Status**: Phase 1 Complete (Frontend), Phase 2 Pending (Wallet Service)
**Last Updated**: 2025-11-12
