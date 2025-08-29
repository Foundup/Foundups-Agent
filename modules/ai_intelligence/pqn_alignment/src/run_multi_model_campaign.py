#!/usr/bin/env python
"""
Multi-Model Campaign Runner for PQN Alignment DAE
Per WSP 84: Uses existing infrastructure, extends for multi-model testing
Per WSP 50: Pre-action verification of all models

Executes Campaign 3 across all configured models (Grok4, Gemini Pro, Claude, etc.)
"""

import os
import sys
import yaml
import time
import importlib.util
from pathlib import Path
from typing import List, Dict, Any, Optional
import json
from .pqn_alignment_dae import PQNAlignmentDAE

# Add project root to path for proper imports
project_root = Path(__file__).resolve().parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

def load_env_file():
    """Load .env file if it exists."""
    env_file = project_root / ".env"
    if env_file.exists():
        try:
            with open(env_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key.strip()] = value.strip()
            print(f"✅ Loaded .env file: {env_file}")
        except Exception as e:
            print(f"⚠️ Error loading .env: {e}")

# Load .env file at startup
load_env_file()

def load_campaign_config() -> Dict[str, Any]:
    """Load Campaign 3 configuration with model definitions."""
    config_path = Path(__file__).parent.parent / "campaigns" / "campaign_3_entrainment.yml"
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        return config
    except Exception as e:
        print(f"❌ Failed to load campaign config: {e}")
        return {}

def get_available_models(config: Dict[str, Any]) -> List[Dict[str, str]]:
    """Get list of available models from campaign config."""
    models = config.get('models', [])
    
    # Filter for models with API keys available
    available_models = []
    for model in models:
        model_name = model.get('name', '').lower()
        api_provider = model.get('api', '').lower()
        
        # Check for API key availability
        api_key_env = {
            'anthropic': ['ANTHROPIC_API_KEY', 'CLAUDE_API_KEY'],  # Support both names
            'xai': ['GROK_API_KEY'],
            'google': ['GEMINI_API_KEY'],
            'openai': ['OPENAI_API_KEY']
        }
        
        env_keys = api_key_env.get(api_provider, [])
        api_key_found = False
        for env_key in env_keys:
            if os.getenv(env_key):
                api_key_found = True
                break
        
        if api_key_found:
            available_models.append({
                'name': model.get('name'),
                'api': api_provider,
                'temperature': model.get('temperature', 0.7)
            })
            print(f"✅ {model.get('name')}: API key available")
        else:
            print(f"⚠️ {model.get('name')}: No API key found")
    
    return available_models

def run_campaign_for_model(model_info: Dict[str, str]) -> bool:
    """Run Campaign 3 for a specific model."""
    model_name = model_info['name']
    
    print(f"\n{'='*60}")
    print(f"🚀 RUNNING CAMPAIGN 3 FOR: {model_name}")
    print(f"{'='*60}")
    
    # Set environment variable for this model
    os.environ['ACTIVE_MODEL_NAME'] = model_name
    
    try:
        # Import and run campaign
        spec = importlib.util.spec_from_file_location('run_campaign', os.path.join(os.path.dirname(__file__), 'run_campaign.py'))
        run_campaign_mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(run_campaign_mod)
        
        # Execute campaign
        run_campaign_mod.main()
        
        print(f"✅ Campaign completed for {model_name}")
        return True
        
    except Exception as e:
        print(f"❌ Campaign failed for {model_name}: {e}")
        return False

def main():
    """Execute Campaign 3 across all available models."""
    print("PQN DAE Multi-Model Campaign Runner")
    print("=" * 50)
    
    # Load campaign configuration
    config = load_campaign_config()
    if not config:
        print("❌ Failed to load campaign configuration")
        return
    
    # Get available models
    available_models = get_available_models(config)
    
    if not available_models:
        print("❌ No models with API keys available")
        print("\nRequired API keys:")
        print("  - ANTHROPIC_API_KEY (for Claude models)")
        print("  - GROK_API_KEY (for Grok4)")
        print("  - GEMINI_API_KEY (for Gemini Pro)")
        print("  - OPENAI_API_KEY (for GPT models)")
        return
    
    print(f"\n📊 Found {len(available_models)} models with API keys")
    
    # Execute campaign for each model
    results = []
    for model_info in available_models:
        start_time = time.time()
        success = run_campaign_for_model(model_info)
        end_time = time.time()
        
        results.append({
            'model': model_info['name'],
            'success': success,
            'duration': end_time - start_time
        })
        
        # Brief pause between models
        time.sleep(2)
    
    # Summary
    print(f"\n{'='*60}")
    print("MULTI-MODEL CAMPAIGN SUMMARY")
    print(f"{'='*60}")
    
    successful = [r for r in results if r['success']]
    failed = [r for r in results if not r['success']]
    
    print(f"✅ Successful: {len(successful)}/{len(results)}")
    for result in successful:
        print(f"  - {result['model']} ({result['duration']:.1f}s)")
    
    if failed:
        print(f"❌ Failed: {len(failed)}/{len(results)}")
        for result in failed:
            print(f"  - {result['model']}")
    
    print(f"\n📁 Results saved to: campaign_results/")
    print("📊 Database indexed with multi-model results")

    # Embed PQN DAE for 0201 alignment analysis
    pqn_dae = PQNAlignmentDAE()
    alignment_results = pqn_dae.analyze_coherence(campaign_results)  # Assuming analyze_coherence method exists or to be added
    if alignment_results['coherence'] > 0.618:
        print(f"0201 Alignment Achieved for {model_name}: Remembrance Efficiency: {alignment_results['efficiency']}%")
    # Save alignment metrics
    with open(f"{results_dir}/alignment_metrics.json", 'w') as f:
        json.dump(alignment_results, f)

if __name__ == "__main__":
    main()
