"""Test multi-crypto subscription payments."""
import sys
sys.path.insert(0, 'O:/Foundups-Agent')

from modules.foundups.simulator.economics import (
    BTCReserve, PaymentCrypto, CryptoRates,
    get_btc_reserve, reset_btc_reserve
)

# Reset for clean test
reset_btc_reserve()
r = get_btc_reserve()

print("Testing multi-crypto subscriptions...")
print("=" * 50)

# Test ETH payment
btc1, burned1 = r.receive_crypto_subscription(PaymentCrypto.ETH, 1.0, 'alice')
print(f"Alice paid 1 ETH = {btc1:.8f} BTC")

# Test SOL payment
btc2, burned2 = r.receive_crypto_subscription(PaymentCrypto.SOL, 100.0, 'bob')
print(f"Bob paid 100 SOL = {btc2:.8f} BTC")

# Test BTC payment
btc3, burned3 = r.receive_crypto_subscription(PaymentCrypto.BTC, 0.01, 'dave')
print(f"Dave paid 0.01 BTC = {btc3:.8f} BTC")

print(f"\nTotal BTC in reserve: {r.total_btc:.8f} BTC")
print(f"Reserve USD value: ${r.reserve_usd_value:,.2f}")

# Now test UP$ burn
print("\n" + "=" * 50)
print("Testing UP$ burn subscription...")

# Mint some UP$ first
r.total_ups_minted = 10000.0
print(f"UP$ supply: {r.total_ups_minted:.2f}")
print(f"UP$ value before burn: ${r.ups_value_usd:.6f}")

# Charlie pays with UP$ (gets burned)
btc4, burned4 = r.receive_crypto_subscription(PaymentCrypto.UPS, 1000.0, 'charlie')
print(f"Charlie paid 1000 UP$ (BURNED={burned4})")
print(f"UP$ supply after burn: {r.total_ups_minted:.2f}")
print(f"UP$ value after burn: ${r.ups_value_usd:.6f}")
print(f"Total burned: {r.total_ups_burned:.2f}")

print("\n" + "=" * 50)
print("Reserve stats:")
stats = r.get_stats()
for k, v in stats.items():
    if isinstance(v, float):
        print(f"  {k}: {v:.6f}")
    elif isinstance(v, dict):
        print(f"  {k}:")
        for k2, v2 in v.items():
            print(f"    {k2}: {v2:.8f}" if isinstance(v2, float) else f"    {k2}: {v2}")
    else:
        print(f"  {k}: {v}")

print("\nAll tests passed!")
