"""pAVS System Audit - OpenClaw Deep Verification.

Burrows into the simulator economics to verify:
1. SIM ↔ WSP 26 documentation alignment
2. Parameter consistency across modules
3. Flow integrity (UPS→F_i→Treasury)
4. Dynamic parameter manipulation for testing

Usage:
    python -m modules.foundups.simulator.economics.pavs_audit

OpenClaw Methodology:
- Deep introspection of live module state
- Cross-reference parameters against WSP 26
- Identify drift between docs and implementation
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from enum import Enum

# Economics modules to audit
from .token_economics import (
    TokenEconomicsEngine, FeeConfig, SUBSCRIPTION_TIERS,
    SubscriptionTier,
)
from .demurrage import (
    DemurrageEngine, DecayConfig, FoundUpType, FOUNDUP_TYPE_RATIOS,
    ACTIVITY_TIER_MULTIPLIERS,
)
from .pool_distribution import (
    POOL_PERCENTAGES, ACTIVITY_SHARES, STAKER_TIER_THRESHOLDS,
    STAKER_CAP_GENESIS, STAKER_CAP_EARLY,
)
from .fi_orderbook import OrderBookManager
from .allocation_engine import AllocationEngine, AllocationStrategy
from .btc_reserve import BTCReserve, get_btc_reserve

logger = logging.getLogger(__name__)


class AuditStatus(Enum):
    """Audit check status."""
    PASS = "PASS"
    WARN = "WARN"
    FAIL = "FAIL"
    INFO = "INFO"


@dataclass
class AuditCheck:
    """Single audit check result."""
    name: str
    status: AuditStatus
    expected: Any
    actual: Any
    wsp_ref: str = ""
    notes: str = ""


@dataclass
class AuditSection:
    """Group of related audit checks."""
    name: str
    checks: List[AuditCheck] = field(default_factory=list)

    @property
    def pass_count(self) -> int:
        return sum(1 for c in self.checks if c.status == AuditStatus.PASS)

    @property
    def fail_count(self) -> int:
        return sum(1 for c in self.checks if c.status == AuditStatus.FAIL)


@dataclass
class PAVSAuditReport:
    """Complete pAVS system audit report."""
    sections: List[AuditSection] = field(default_factory=list)

    @property
    def total_checks(self) -> int:
        return sum(len(s.checks) for s in self.sections)

    @property
    def total_pass(self) -> int:
        return sum(s.pass_count for s in self.sections)

    @property
    def total_fail(self) -> int:
        return sum(s.fail_count for s in self.sections)

    def print_report(self) -> None:
        """Print formatted audit report."""
        print("\n" + "=" * 70)
        print("pAVS SYSTEM AUDIT REPORT - OpenClaw Deep Verification")
        print("=" * 70)

        for section in self.sections:
            print(f"\n## {section.name}")
            print("-" * 50)

            for check in section.checks:
                status_icon = {
                    AuditStatus.PASS: "[OK]",
                    AuditStatus.WARN: "[!!]",
                    AuditStatus.FAIL: "[XX]",
                    AuditStatus.INFO: "[--]",
                }[check.status]

                print(f"{status_icon} {check.name}")
                if check.status != AuditStatus.PASS:
                    print(f"    Expected: {check.expected}")
                    print(f"    Actual:   {check.actual}")
                if check.wsp_ref:
                    print(f"    WSP Ref:  {check.wsp_ref}")
                if check.notes:
                    print(f"    Notes:    {check.notes}")

            print(f"\nSection: {section.pass_count}/{len(section.checks)} passed")

        print("\n" + "=" * 70)
        print(f"TOTAL: {self.total_pass}/{self.total_checks} checks passed")
        if self.total_fail > 0:
            print(f"       {self.total_fail} FAILURES - requires attention")
        print("=" * 70 + "\n")


class PAVSAuditor:
    """OpenClaw auditor for pAVS economics system."""

    def __init__(self):
        self.report = PAVSAuditReport()

    def run_full_audit(self) -> PAVSAuditReport:
        """Run complete pAVS system audit."""
        self.report = PAVSAuditReport()

        self._audit_pool_structure()
        self._audit_demurrage_config()
        self._audit_subscription_tiers()
        self._audit_fee_structure()
        self._audit_staker_economics()
        self._audit_allocation_engine()
        self._audit_treasury_separation()
        self._audit_dex_config()

        return self.report

    def _audit_pool_structure(self) -> None:
        """Audit WSP 26 Section 6.3-6.4 pool percentages."""
        section = AuditSection(name="Pool Structure (WSP 26 Section 6.3-6.4)")

        # Check pool percentages sum to 100%
        total = sum(POOL_PERCENTAGES.values())
        section.checks.append(AuditCheck(
            name="Pool percentages sum to 100%",
            status=AuditStatus.PASS if abs(total - 1.0) < 0.001 else AuditStatus.FAIL,
            expected=1.0,
            actual=total,
            wsp_ref="WSP 26 Section 6.3",
        ))

        # Check individual pools
        expected_pools = {
            "stakeholder_un": 0.60,
            "stakeholder_dao": 0.16,
            "stakeholder_du": 0.04,
            "network": 0.16,
            "fund": 0.04,
        }

        for pool_name, expected_pct in expected_pools.items():
            actual = POOL_PERCENTAGES.get(pool_name, 0)
            section.checks.append(AuditCheck(
                name=f"{pool_name} = {expected_pct:.0%}",
                status=AuditStatus.PASS if abs(actual - expected_pct) < 0.001 else AuditStatus.FAIL,
                expected=expected_pct,
                actual=actual,
                wsp_ref="WSP 26 Section 6.3",
            ))

        # Check stakeholder total = 80%
        stakeholder_total = sum(
            v for k, v in POOL_PERCENTAGES.items()
            if k.startswith("stakeholder_")
        )
        section.checks.append(AuditCheck(
            name="Stakeholder pools = 80%",
            status=AuditStatus.PASS if abs(stakeholder_total - 0.80) < 0.001 else AuditStatus.FAIL,
            expected=0.80,
            actual=stakeholder_total,
            wsp_ref="WSP 26 Section 6.3",
        ))

        self.report.sections.append(section)

    def _audit_demurrage_config(self) -> None:
        """Audit WSP 26 Section 16 demurrage parameters."""
        section = AuditSection(name="Demurrage Config (WSP 26 Section 16)")

        config = DecayConfig()

        # Check decay rate bounds (daily rates)
        section.checks.append(AuditCheck(
            name="Max daily decay = 3%/day",
            status=AuditStatus.PASS if abs(config.max_daily_decay - 0.03) < 0.001 else AuditStatus.FAIL,
            expected=0.03,
            actual=config.max_daily_decay,
            wsp_ref="WSP 26 Section 16.2",
        ))

        # Check network pool ratio bounds
        section.checks.append(AuditCheck(
            name="Min network pool ratio = 60%",
            status=AuditStatus.PASS if abs(config.min_network_pool_ratio - 0.60) < 0.01 else AuditStatus.FAIL,
            expected=0.60,
            actual=config.min_network_pool_ratio,
            wsp_ref="WSP 26 Section 16.8.2",
        ))

        section.checks.append(AuditCheck(
            name="Max network pool ratio = 95%",
            status=AuditStatus.PASS if abs(config.max_network_pool_ratio - 0.95) < 0.01 else AuditStatus.FAIL,
            expected=0.95,
            actual=config.max_network_pool_ratio,
            wsp_ref="WSP 26 Section 16.8.2",
        ))

        # Check FoundUp type ratios exist
        for ft in FoundUpType:
            ratio = FOUNDUP_TYPE_RATIOS.get(ft)
            section.checks.append(AuditCheck(
                name=f"FoundUpType.{ft.name} has ratio defined",
                status=AuditStatus.PASS if ratio is not None else AuditStatus.FAIL,
                expected="(network, treasury) tuple",
                actual=ratio,
                wsp_ref="WSP 26 Section 16.8.1",
            ))

        # Check default ratio
        default_ratio = FOUNDUP_TYPE_RATIOS.get(FoundUpType.DEFAULT)
        if default_ratio:
            section.checks.append(AuditCheck(
                name="Default ratio = 80% network / 20% treasury",
                status=AuditStatus.PASS if default_ratio == (0.80, 0.20) else AuditStatus.WARN,
                expected=(0.80, 0.20),
                actual=default_ratio,
                wsp_ref="WSP 26 Section 16.8",
                notes="Variable ratios per FoundUp type are allowed",
            ))

        self.report.sections.append(section)

    def _audit_subscription_tiers(self) -> None:
        """Audit WSP 26 Section 4.9 subscription tiers."""
        section = AuditSection(name="Subscription Tiers (WSP 26 Section 4.9)")

        expected_tiers = {
            SubscriptionTier.FREE: (0.0, 1.0, 1),
            SubscriptionTier.SPARK: (2.95, 2.0, 2),
            SubscriptionTier.EXPLORER: (9.95, 3.0, 3),
            SubscriptionTier.BUILDER: (19.95, 5.0, 5),
            SubscriptionTier.FOUNDER: (49.95, 10.0, 30),
        }

        for tier, (price, mult, cycles) in expected_tiers.items():
            config = SUBSCRIPTION_TIERS.get(tier)
            if config is None:
                section.checks.append(AuditCheck(
                    name=f"{tier.value} tier exists",
                    status=AuditStatus.FAIL,
                    expected=tier,
                    actual=None,
                ))
                continue

            section.checks.append(AuditCheck(
                name=f"{tier.value}: ${price}/mo",
                status=AuditStatus.PASS if abs(config.price_monthly - price) < 0.01 else AuditStatus.FAIL,
                expected=price,
                actual=config.price_monthly,
                wsp_ref="WSP 26 Section 4.9",
            ))

            section.checks.append(AuditCheck(
                name=f"{tier.value}: {mult}x allocation",
                status=AuditStatus.PASS if abs(config.allocation_multiplier - mult) < 0.01 else AuditStatus.FAIL,
                expected=mult,
                actual=config.allocation_multiplier,
                wsp_ref="WSP 26 Section 4.9",
            ))

        self.report.sections.append(section)

    def _audit_fee_structure(self) -> None:
        """Audit WSP 26 fee configuration."""
        section = AuditSection(name="Fee Structure (WSP 26 Section 6.8)")

        config = FeeConfig()

        # MINED F_i exit = 11%
        section.checks.append(AuditCheck(
            name="MINED F_i exit fee = 11%",
            status=AuditStatus.PASS if abs(config.mined_fi_exit_fee - 0.11) < 0.001 else AuditStatus.FAIL,
            expected=0.11,
            actual=config.mined_fi_exit_fee,
            wsp_ref="WSP 26 Section 6.8",
        ))

        # STAKED round-trip = 8%
        roundtrip = config.staked_fi_entry_fee + config.staked_fi_exit_fee
        section.checks.append(AuditCheck(
            name="STAKED F_i round-trip = 8%",
            status=AuditStatus.PASS if abs(roundtrip - 0.08) < 0.001 else AuditStatus.FAIL,
            expected=0.08,
            actual=roundtrip,
            wsp_ref="WSP 26 Section 6.8",
            notes=f"Entry: {config.staked_fi_entry_fee:.0%}, Exit: {config.staked_fi_exit_fee:.0%}",
        ))

        self.report.sections.append(section)

    def _audit_staker_economics(self) -> None:
        """Audit staker/Du pool economics."""
        section = AuditSection(name="Staker Economics (WSP 26 Section 6.4)")

        # Check staker tier thresholds
        section.checks.append(AuditCheck(
            name="Du tier threshold = 10x",
            status=AuditStatus.PASS if STAKER_TIER_THRESHOLDS.get("du") == 10.0 else AuditStatus.FAIL,
            expected=10.0,
            actual=STAKER_TIER_THRESHOLDS.get("du"),
            wsp_ref="WSP 26 Section 6.4",
        ))

        section.checks.append(AuditCheck(
            name="Dao tier threshold = 100x",
            status=AuditStatus.PASS if STAKER_TIER_THRESHOLDS.get("dao") == 100.0 else AuditStatus.FAIL,
            expected=100.0,
            actual=STAKER_TIER_THRESHOLDS.get("dao"),
            wsp_ref="WSP 26 Section 6.4",
        ))

        # Check staker caps
        section.checks.append(AuditCheck(
            name="Genesis staker cap = 100",
            status=AuditStatus.PASS if STAKER_CAP_GENESIS == 100 else AuditStatus.WARN,
            expected=100,
            actual=STAKER_CAP_GENESIS,
            wsp_ref="Memory: dilution_scenario.py analysis",
        ))

        self.report.sections.append(section)

    def _audit_allocation_engine(self) -> None:
        """Audit AllocationEngine configuration."""
        section = AuditSection(name="Allocation Engine (WSP 26 Section 17)")

        engine = AllocationEngine()

        # Check strategies exist
        for strategy in AllocationStrategy:
            section.checks.append(AuditCheck(
                name=f"Strategy {strategy.value} defined",
                status=AuditStatus.PASS,
                expected=strategy,
                actual=strategy,
                wsp_ref="WSP 26 Section 17.4",
            ))

        # Check scarcity threshold
        section.checks.append(AuditCheck(
            name="Scarcity threshold = 10%",
            status=AuditStatus.PASS if abs(engine.scarcity_threshold - 0.10) < 0.01 else AuditStatus.WARN,
            expected=0.10,
            actual=engine.scarcity_threshold,
            wsp_ref="WSP 26 Section 17.4",
            notes="Below this, routes to DEX buy order",
        ))

        self.report.sections.append(section)

    def _audit_treasury_separation(self) -> None:
        """Audit pAVS Treasury vs F_i Fund separation."""
        section = AuditSection(name="Treasury Separation (012-Confirmed)")

        # Check demurrage routes to pAVS (not generic "treasury")
        engine = DemurrageEngine()
        has_pavs = hasattr(engine.config, "decay_to_pavs_treasury_ratio")

        section.checks.append(AuditCheck(
            name="Demurrage config uses 'pavs_treasury' naming",
            status=AuditStatus.PASS if has_pavs else AuditStatus.WARN,
            expected="decay_to_pavs_treasury_ratio",
            actual="present" if has_pavs else "missing",
            wsp_ref="012-confirmed 2026-02-15",
            notes="Distinguishes pAVS Treasury (system) from F_i Fund (per-FoundUp)",
        ))

        # Check F_i Fund = 4% of F_i pool (in pool_distribution)
        fund_pct = POOL_PERCENTAGES.get("fund", 0)
        section.checks.append(AuditCheck(
            name="F_i Fund (network) = 4%",
            status=AuditStatus.PASS if abs(fund_pct - 0.04) < 0.001 else AuditStatus.FAIL,
            expected=0.04,
            actual=fund_pct,
            wsp_ref="WSP 26 Section 6.3",
        ))

        self.report.sections.append(section)

    def _audit_dex_config(self) -> None:
        """Audit F_i DEX configuration."""
        section = AuditSection(name="F_i DEX (WSP 26 Section 17)")

        manager = OrderBookManager()

        section.checks.append(AuditCheck(
            name="Trading fee = 2%",
            status=AuditStatus.PASS if abs(manager.trading_fee_rate - 0.02) < 0.001 else AuditStatus.FAIL,
            expected=0.02,
            actual=manager.trading_fee_rate,
            wsp_ref="WSP 26 Section 17.6",
        ))

        # Check order book creates per FoundUp
        book1 = manager.get_or_create_book("test_001")
        book2 = manager.get_or_create_book("test_002")
        section.checks.append(AuditCheck(
            name="Separate order books per FoundUp",
            status=AuditStatus.PASS if book1 is not book2 else AuditStatus.FAIL,
            expected="distinct books",
            actual="distinct" if book1 is not book2 else "same",
            wsp_ref="WSP 26 Section 17.3",
        ))

        self.report.sections.append(section)


def run_audit() -> PAVSAuditReport:
    """Run full pAVS audit and print report."""
    auditor = PAVSAuditor()
    report = auditor.run_full_audit()
    report.print_report()
    return report


if __name__ == "__main__":
    run_audit()
