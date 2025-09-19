#!/usr/bin/env python3
"""
DAE-Specific Fingerprint Generator - WSP 86 Modular Implementation
Generates fingerprints per DAE to avoid 1MB+ central file

Each DAE maintains its own fingerprints in memory/DAE_FINGERPRINTS.json
Token reduction: 95% (from 35K to 1.5K per DAE operation)
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Set, Optional
from .module_fingerprint_generator import ModuleFingerprintGenerator

logger = logging.getLogger(__name__)

# DAE Domain Mappings
DAE_REGISTRY = {
    # Infrastructure DAEs
    "infrastructure_orchestration_dae": {
        "domain": "infrastructure",
        "primary_modules": ["wre_core", "dae_infrastructure", "shared_utilities"],
        "cross_domains": ["all"]  # Orchestrates everything
    },
    "compliance_quality_dae": {
        "domain": "infrastructure",
        "primary_modules": ["system_health_monitor", "wre_core/recursive_improvement"],
        "cross_domains": ["testing", "validation"]
    },
    "knowledge_learning_dae": {
        "domain": "infrastructure",
        "primary_modules": ["wre_core/memory", "dae_infrastructure/pattern_banks"],
        "cross_domains": ["ai_intelligence"]
    },
    "maintenance_operations_dae": {
        "domain": "infrastructure",
        "primary_modules": ["system_health_monitor", "shared_utilities"],
        "cross_domains": []
    },
    "documentation_registry_dae": {
        "domain": "infrastructure",
        "primary_modules": ["dae_infrastructure/docs"],
        "cross_domains": ["all"]  # Needs to see all for docs
    },

    # Platform Integration DAEs
    "youtube_dae": {
        "domain": "communication",  # Primary home
        "primary_modules": ["livechat"],
        "cross_domains": ["platform_integration/youtube_auth", "platform_integration/stream_resolver"]
    },
    "linkedin_dae": {
        "domain": "platform_integration",
        "primary_modules": ["linkedin_agent", "linkedin_scheduler"],
        "cross_domains": ["ai_intelligence/banter_engine"]
    },
    "x_twitter_dae": {
        "domain": "platform_integration",
        "primary_modules": ["x_twitter"],
        "cross_domains": ["ai_intelligence/banter_engine"]
    },

    # Other DAEs
    "gamification_dae": {
        "domain": "gamification",
        "primary_modules": ["whack_a_magat"],
        "cross_domains": ["communication"]
    }
}


class DAEFingerprintGenerator(ModuleFingerprintGenerator):
    """
    Generate fingerprints specific to each DAE cube.
    Stores in DAE's memory/ directory for fast access.
    """

    def __init__(self, dae_name: str, project_root: str = "."):
        """
        Initialize DAE-specific fingerprint generator.

        Args:
            dae_name: Name of the DAE (e.g., "youtube_dae")
            project_root: Root directory of project
        """
        super().__init__(project_root)

        if dae_name not in DAE_REGISTRY:
            raise ValueError(f"Unknown DAE: {dae_name}. Available: {list(DAE_REGISTRY.keys())}")

        self.dae_name = dae_name
        self.dae_config = DAE_REGISTRY[dae_name]
        self.dae_domain = self.dae_config["domain"]

        # Determine DAE memory location
        if dae_name == "youtube_dae":
            # Special case: YouTube DAE lives in communication/livechat
            self.memory_dir = self.project_root / "modules" / "communication" / "livechat" / "memory"
        elif "infrastructure" in self.dae_domain:
            self.memory_dir = self.project_root / "modules" / "infrastructure" / dae_name / "memory"
        else:
            primary = self.dae_config["primary_modules"][0]
            self.memory_dir = self.project_root / "modules" / self.dae_domain / primary / "memory"

        self.memory_dir.mkdir(parents=True, exist_ok=True)

        # Track what modules belong to this DAE
        self.dae_modules = set()
        self.cross_domain_modules = set()

    def scan_dae_modules(self):
        """
        Scan only modules relevant to this DAE.
        Much faster than scanning all 624 modules.
        """
        logger.info(f"Scanning modules for {self.dae_name}")

        # 1. Scan primary DAE modules
        for module_pattern in self.dae_config["primary_modules"]:
            self._scan_module_pattern(module_pattern, is_primary=True)

        # 2. Scan cross-domain dependencies
        for domain_pattern in self.dae_config.get("cross_domains", []):
            if domain_pattern == "all":
                # Special case for orchestration DAEs
                logger.info(f"{self.dae_name} requires all modules (orchestrator)")
                self._scan_all_modules()
                break
            else:
                self._scan_module_pattern(domain_pattern, is_primary=False)

        # 3. Find and scan imported dependencies
        self._scan_dependencies()

        # 4. Save DAE-specific fingerprints
        self._save_dae_fingerprints()

    def _scan_module_pattern(self, pattern: str, is_primary: bool = False):
        """Scan modules matching a pattern."""
        base_path = self.project_root / "modules"

        # Handle different pattern types
        if "/" in pattern:
            # Specific path like "platform_integration/youtube_auth"
            search_path = base_path / pattern
        else:
            # Module name within domain
            search_path = base_path / self.dae_domain / pattern

        if not search_path.exists():
            logger.warning(f"Path not found: {search_path}")
            return

        # Find Python files
        py_files = list(search_path.rglob("*.py"))
        logger.info(f"Found {len(py_files)} files in {pattern}")

        for py_file in py_files:
            # Skip tests and cache
            if "test" in py_file.name or "__pycache__" in str(py_file):
                continue

            fingerprint = self.scan_module(py_file)
            if fingerprint:
                self.fingerprints[str(py_file)] = fingerprint

                if is_primary:
                    self.dae_modules.add(str(py_file))
                else:
                    self.cross_domain_modules.add(str(py_file))

    def _scan_dependencies(self):
        """Scan for imported dependencies not yet fingerprinted."""
        dependencies_to_scan = set()

        for fp in self.fingerprints.values():
            for local_dep in fp.get("dependencies", {}).get("local", []):
                # Convert import to file path
                if local_dep.startswith("modules."):
                    dep_path = local_dep.replace(".", "/") + ".py"
                    dep_file = self.project_root / dep_path

                    if dep_file.exists() and str(dep_file) not in self.fingerprints:
                        dependencies_to_scan.add(dep_file)

        logger.info(f"Scanning {len(dependencies_to_scan)} additional dependencies")

        for dep_file in dependencies_to_scan:
            fingerprint = self.scan_module(dep_file)
            if fingerprint:
                self.fingerprints[str(dep_file)] = fingerprint
                self.cross_domain_modules.add(str(dep_file))

    def _scan_all_modules(self):
        """Scan all modules (for orchestration DAEs)."""
        modules_dir = self.project_root / "modules"
        py_files = list(modules_dir.rglob("*.py"))

        logger.info(f"Scanning all {len(py_files)} modules for orchestration DAE")

        for py_file in py_files:
            if "test" in py_file.name or "__pycache__" in str(py_file):
                continue

            fingerprint = self.scan_module(py_file)
            if fingerprint:
                self.fingerprints[str(py_file)] = fingerprint
                self.dae_modules.add(str(py_file))

    def _save_dae_fingerprints(self):
        """Save fingerprints to DAE memory directory."""
        output_file = self.memory_dir / "DAE_FINGERPRINTS.json"

        # Add DAE metadata
        dae_fingerprint_data = {
            "dae_name": self.dae_name,
            "dae_domain": self.dae_domain,
            "fingerprint_version": "2.0",
            "module_count": len(self.fingerprints),
            "primary_modules": len(self.dae_modules),
            "cross_domain_modules": len(self.cross_domain_modules),
            "generated_at": str(os.path.getmtime(__file__)),
            "modules": self.fingerprints
        }

        with open(output_file, 'w') as f:
            json.dump(dae_fingerprint_data, f, indent=2, default=str)

        logger.info(f"Saved {len(self.fingerprints)} fingerprints to {output_file}")

        # Print summary
        self._print_dae_summary()

    def _print_dae_summary(self):
        """Print DAE-specific summary."""
        print(f"\n{'='*60}")
        print(f"DAE FINGERPRINT SUMMARY: {self.dae_name}")
        print(f"{'='*60}")
        print(f"Domain: {self.dae_domain}")
        print(f"Primary modules: {len(self.dae_modules)}")
        print(f"Cross-domain modules: {len(self.cross_domain_modules)}")
        print(f"Total fingerprints: {len(self.fingerprints)}")

        # File size comparison
        output_file = self.memory_dir / "DAE_FINGERPRINTS.json"
        if output_file.exists():
            size_kb = output_file.stat().st_size / 1024
            print(f"Fingerprint file size: {size_kb:.1f} KB")

            # Token estimate (rough)
            token_estimate = int(size_kb * 30)  # ~30 tokens per KB
            print(f"Estimated tokens to load: {token_estimate:,}")

            # Compare to central file
            central_size = 1024  # 1MB central file
            reduction = (1 - size_kb/central_size) * 100
            print(f"Size reduction vs central: {reduction:.1f}%")

        print(f"Memory location: {self.memory_dir}")


def generate_all_dae_fingerprints():
    """Generate fingerprints for all registered DAEs."""
    for dae_name in DAE_REGISTRY:
        print(f"\n{'='*60}")
        print(f"Generating fingerprints for {dae_name}")
        print(f"{'='*60}")

        try:
            generator = DAEFingerprintGenerator(dae_name)
            generator.scan_dae_modules()
        except Exception as e:
            logger.error(f"Failed to generate fingerprints for {dae_name}: {e}")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Generate DAE-specific fingerprints")
    parser.add_argument("--dae", help="Specific DAE to generate fingerprints for")
    parser.add_argument("--all", action="store_true", help="Generate for all DAEs")
    parser.add_argument("--list", action="store_true", help="List available DAEs")

    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)

    if args.list:
        print("Available DAEs:")
        for dae_name, config in DAE_REGISTRY.items():
            print(f"  {dae_name} ({config['domain']})")

    elif args.all:
        generate_all_dae_fingerprints()

    elif args.dae:
        generator = DAEFingerprintGenerator(args.dae)
        generator.scan_dae_modules()

    else:
        print("Usage:")
        print("  Generate for specific DAE: python dae_fingerprint_generator.py --dae youtube_dae")
        print("  Generate for all DAEs: python dae_fingerprint_generator.py --all")
        print("  List available DAEs: python dae_fingerprint_generator.py --list")


if __name__ == "__main__":
    main()