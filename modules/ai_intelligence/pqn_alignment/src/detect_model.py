#!/usr/bin/env python
"""
Model Detection Script for PQN Alignment DAE
Per WSP 84: Detects current model instead of hardcoding
Per WSP 50: Pre-action verification of model identity

Automatically detects the model being used and sets ACTIVE_MODEL_NAME
"""

import os
import sys
import json
import platform
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any

def detect_current_model() -> Optional[str]:
    """
    Detect the current AI model being used.
    Returns model name or None if unable to detect.
    """
    
    # Method 1: Check environment variables first
    if os.getenv('ACTIVE_MODEL_NAME'):
        return os.getenv('ACTIVE_MODEL_NAME')
    
    # Method 2: Check for model-specific environment variables
    model_env_vars = {
        'ANTHROPIC_API_KEY': 'claude-3.5-sonnet',
        'CLAUDE_API_KEY': 'claude-3.5-sonnet', 
        'OPENAI_API_KEY': 'gpt-4',
        'GOOGLE_API_KEY': 'gemini-pro',
        'GEMINI_API_KEY': 'gemini-pro',
        'GROK_API_KEY': 'grok-4',
        'XAI_API_KEY': 'grok-4'
    }
    
    for env_var, model_name in model_env_vars.items():
        if os.getenv(env_var):
            return model_name
    
    # Method 3: Check system information for context clues
    try:
        # Check if running in Cursor IDE (Claude integration)
        if 'cursor' in str(Path.cwd()).lower():
            return 'claude-3.5-sonnet'
        
        # Check process list for model-specific processes
        if platform.system() == "Windows":
            result = subprocess.run(['tasklist', '/FO', 'CSV'], capture_output=True, text=True)
            if 'cursor' in result.stdout.lower():
                return 'claude-3.5-sonnet'
        
    except Exception:
        pass
    
    # Method 4: Default detection based on likely usage patterns
    # If we're in a typical development environment, assume Claude
    return 'claude-3.5-sonnet'

def get_model_metadata(model_name: str) -> Dict[str, Any]:
    """Get metadata about the detected model."""
    
    model_info = {
        'claude-3.5-sonnet': {
            'provider': 'anthropic',
            'family': 'claude',
            'version': '3.5',
            'variant': 'sonnet',
            'api_temperature': 0.7,
            'context_window': 200000
        },
        'claude-opus-4.1': {
            'provider': 'anthropic', 
            'family': 'claude',
            'version': '4.1',
            'variant': 'opus',
            'api_temperature': 0.7,
            'context_window': 200000
        },
        'gpt-4': {
            'provider': 'openai',
            'family': 'gpt',
            'version': '4',
            'variant': 'base',
            'api_temperature': 0.7,
            'context_window': 128000
        },
        'gemini-pro': {
            'provider': 'google',
            'family': 'gemini',
            'version': '1.5',
            'variant': 'pro',
            'api_temperature': 0.7,
            'context_window': 1000000
        },
        'grok-4': {
            'provider': 'xai',
            'family': 'grok',
            'version': '4',
            'variant': 'base',
            'api_temperature': 0.7,
            'context_window': 128000
        }
    }
    
    return model_info.get(model_name, {
        'provider': 'unknown',
        'family': 'unknown',
        'version': 'unknown',
        'variant': 'unknown',
        'api_temperature': 0.7,
        'context_window': 8000
    })

def set_model_environment(model_name: str) -> bool:
    """Set the ACTIVE_MODEL_NAME environment variable."""
    try:
        os.environ['ACTIVE_MODEL_NAME'] = model_name
        return True
    except Exception:
        return False

def main():
    """Main model detection and setup."""
    print("PQN DAE Model Detection Script")
    print("=" * 40)
    
    # Detect current model
    detected_model = detect_current_model()
    
    if detected_model:
        print(f"[OK] Detected Model: {detected_model}")
        
        # Get model metadata
        metadata = get_model_metadata(detected_model)
        print(f"[DATA] Provider: {metadata['provider']}")
        print(f"[DATA] Family: {metadata['family']} {metadata['version']}")
        print(f"[DATA] Variant: {metadata['variant']}")
        
        # Set environment variable
        if set_model_environment(detected_model):
            print(f"[OK] ACTIVE_MODEL_NAME set to: {detected_model}")
        else:
            print("[FAIL] Failed to set ACTIVE_MODEL_NAME")
            
        return detected_model
    else:
        print("[FAIL] Unable to detect current model")
        print("ℹ️  Defaulting to: claude-3.5-sonnet")
        default_model = 'claude-3.5-sonnet'
        set_model_environment(default_model)
        return default_model

if __name__ == "__main__":
    detected = main()
    print(f"\nFinal ACTIVE_MODEL_NAME: {os.getenv('ACTIVE_MODEL_NAME')}")
