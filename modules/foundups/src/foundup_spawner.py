#!/usr/bin/env python3
"""
FoundUp Spawner - Instance Creation System
==========================================

Creates new FoundUp instances following WSP-defined protocols.

This module handles the technical instantiation of FoundUps but does NOT
define what a FoundUp is - that definition lives in WSP_appendices APPENDIX_J.md.
"""

import os
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, Any

class FoundUpSpawner:
    """
    Spawns new FoundUp instances based on WSP-defined protocols.
    
    This is the execution layer - the actual definitions and governance
    rules for FoundUps are sourced from WSP framework.
    """
    
    def __init__(self, foundups_root: Optional[str] = None):
        """Initialize spawner with FoundUps root directory."""
        self.foundups_root = Path(foundups_root or "modules/foundups")
        self.wsp_source = "WSP_framework"  # Source of truth for protocols
    
    def spawn_foundup(self, name: str, founder: str, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Spawn a new FoundUp instance.
        
        Args:
            name: FoundUp name (should start with @)
            founder: Founder identifier
            config: Optional additional configuration
            
        Returns:
            Dict containing spawn result and instance info
        """
        # Ensure name follows @name convention
        if not name.startswith('@'):
            name = f"@{name}"
        
        instance_path = self.foundups_root / name
        
        # Check if already exists
        if instance_path.exists():
            return {
                "status": "error",
                "message": f"FoundUp {name} already exists",
                "path": str(instance_path)
            }
        
        # Create instance structure
        try:
            self._create_instance_structure(instance_path, name, founder, config or {})
            
            return {
                "status": "success",
                "message": f"FoundUp {name} spawned successfully",
                "path": str(instance_path),
                "founder": founder,
                "created_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "error", 
                "message": f"Failed to spawn FoundUp {name}: {e}",
                "path": str(instance_path)
            }
    
    def _create_instance_structure(self, instance_path: Path, name: str, founder: str, config: Dict[str, Any]):
        """Create the directory structure for a new FoundUp instance."""
        # Create main directory
        instance_path.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        (instance_path / "assets").mkdir(exist_ok=True)
        (instance_path / "logs").mkdir(exist_ok=True)
        (instance_path / "configs").mkdir(exist_ok=True)
        
        # Create foundup.json configuration
        foundup_config = {
            "name": name,
            "founder": founder,
            "created_at": datetime.now().isoformat(),
            "wsp_compliance": "active",
            "cabr_protocol": "enabled",  # CABR logic comes from WSP
            "status": "active",
            "version": "1.0.0",
            **config
        }
        
        with open(instance_path / "foundup.json", 'w') as f:
            json.dump(foundup_config, f, indent=2)
        
        # Create instance README
        readme_content = f"""# {name} - FoundUp Instance

## Instance Information
- **Founder**: {founder}
- **Created**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **WSP Compliance**: Active
- **Status**: Active

## WSP Integration
This FoundUp instance operates under WSP governance:
- **Protocol Source**: WSP_framework
- **CABR Logic**: Implemented per WSP_framework/cabr_protocol.md
- **Governance**: Follows WSP_framework/governance.md

## Structure
```
{name}/
├── foundup.json        # Instance configuration
├── cabr_loop.py        # CABR execution (WSP-compliant)
├── mod_log.db          # Instance logging
├── assets/             # FoundUp-specific assets
├── logs/               # Runtime logs
└── configs/            # Additional configurations
```

## Usage
This is an individual FoundUp instance. Core definitions and protocols
are managed by the WSP framework, not within this instance.
"""
        
        with open(instance_path / "README.md", 'w') as f:
            f.write(readme_content)
        
        # Create CABR loop implementation (references WSP)
        cabr_content = f'''#!/usr/bin/env python3
"""
{name} - CABR Loop Implementation
===============================

Instance-specific CABR execution following WSP_framework protocols.
Core CABR logic and definitions are sourced from WSP, not defined here.
"""

import sys
import os
from pathlib import Path

# Add WSP to path for protocol access
sys.path.append(str(Path(__file__).parent.parent.parent.parent / "WSP_framework"))

class CABRLoop:
    """
    CABR loop implementation for {name}.
    
    Executes CABR protocol as defined in WSP_framework, customized
    for this specific FoundUp instance.
    """
    
    def __init__(self):
        self.instance_name = "{name}"
        self.founder = "{founder}"
        self.wsp_source = "WSP_framework/cabr_protocol.md"
    
    def run_cabr_cycle(self):
        """Execute one CABR cycle per WSP protocol."""
        # Implementation follows WSP_framework/cabr_protocol.md
        print(f"🔄 CABR Cycle for {{self.instance_name}}")
        print(f"📋 Protocol Source: {{self.wsp_source}}")
        
        # Actual CABR logic would be implemented here
        # following WSP_framework specifications
        pass

if __name__ == "__main__":
    cabr = CABRLoop()
    cabr.run_cabr_cycle()
'''
        
        with open(instance_path / "cabr_loop.py", 'w') as f:
            f.write(cabr_content)
        
        print(f"✅ Created FoundUp instance: {name}")
        print(f"📁 Location: {instance_path}")
        print(f"👤 Founder: {founder}")

def main():
    """CLI interface for spawning FoundUps."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Spawn new FoundUp instances")
    parser.add_argument("--name", required=True, help="FoundUp name (e.g., @innovate)")
    parser.add_argument("--founder", required=True, help="Founder identifier")
    parser.add_argument("--config", help="Additional config as JSON string")
    
    args = parser.parse_args()
    
    spawner = FoundUpSpawner()
    
    config = {}
    if args.config:
        config = json.loads(args.config)
    
    result = spawner.spawn_foundup(args.name, args.founder, config)
    
    print(f"Status: {result['status']}")
    print(f"Message: {result['message']}")
    if result['status'] == 'success':
        print(f"Path: {result['path']}")

if __name__ == "__main__":
    main() 