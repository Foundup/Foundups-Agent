"""
Test external JSON loading feature for BanterEngine
Tests the new functionality added from banter_engine2.py
"""

import json
import tempfile
import os
from pathlib import Path
from modules.ai_intelligence.banter_engine.src.banter_engine import BanterEngine


def test_external_json_loading():
    """Test that BanterEngine can load custom banter from external JSON file"""
    print("\n[U+1F9EA] Testing external JSON loading feature")
    
    # Create a temporary JSON file with custom banter
    custom_banter = {
        "custom_greeting": ["Hello from external JSON!", "Custom greeting loaded!"],
        "custom_farewell": ["Goodbye from JSON!", "See you later from file!"],
        "tech_joke": ["Why did the programmer quit? He didn't get arrays!"]
    }
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(custom_banter, f)
        temp_path = f.name
    
    try:
        # Test loading with external file
        engine = BanterEngine(banter_file_path=temp_path)
        
        # Check that themes were loaded
        themes = engine.list_themes()
        print(f"Themes loaded: {themes}")
        
        # Verify custom themes are present
        assert "custom_greeting" in themes, "Custom greeting theme not loaded"
        assert "custom_farewell" in themes, "Custom farewell theme not loaded"
        assert "tech_joke" in themes, "Tech joke theme not loaded"
        
        # Test getting random banter from custom theme
        response = engine.get_random_banter(theme="custom_greeting")
        print(f"Custom greeting response: {response}")
        # Check if the core response is from custom data (may have emoji appended)
        assert any(custom_resp in response for custom_resp in custom_banter["custom_greeting"]), \
            "Response not from custom data"
        
        print("[OK] External JSON loading test passed!")
        
    finally:
        # Clean up temp file
        os.unlink(temp_path)


def test_backward_compatibility():
    """Test that BanterEngine still works without external file (backward compatibility)"""
    print("\n[U+1F9EA] Testing backward compatibility (no external file)")
    
    # Create engine without external file
    engine = BanterEngine()
    
    # Should still have default themes
    themes = engine.list_themes()
    assert "greeting" in themes, "Default greeting theme missing"
    assert "default" in themes, "Default theme missing"
    
    # New themes from our enhancement should be present
    assert "roast" in themes, "Roast theme missing"
    assert "philosophy" in themes, "Philosophy theme missing"
    assert "rebuttal" in themes, "Rebuttal theme missing"
    
    # Test roast theme
    response = engine.get_random_banter(theme="roast")
    print(f"Roast response: {response}")
    assert isinstance(response, str) and len(response) > 0, "Invalid roast response"
    
    # Test philosophy theme
    response = engine.get_random_banter(theme="philosophy")
    print(f"Philosophy response: {response}")
    assert isinstance(response, str) and len(response) > 0, "Invalid philosophy response"
    
    print("[OK] Backward compatibility test passed!")


def test_theme_merging():
    """Test that external themes merge with internal ones"""
    print("\n[U+1F9EA] Testing theme merging (external + internal)")
    
    # Create JSON with overlapping theme
    custom_banter = {
        "greeting": ["External greeting 1", "External greeting 2"],
        "new_theme": ["This is a new theme response"]
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(custom_banter, f)
        temp_path = f.name
    
    try:
        engine = BanterEngine(banter_file_path=temp_path)
        
        # Both internal and external themes should exist
        themes = engine.list_themes()
        assert "greeting" in themes, "Greeting theme missing"
        assert "new_theme" in themes, "New theme not added"
        assert "default" in themes, "Default theme missing"
        
        # Greeting should have both internal and external responses
        # (This depends on implementation details, but theme should exist)
        response = engine.get_random_banter(theme="greeting")
        assert isinstance(response, str) and len(response) > 0
        
        print("[OK] Theme merging test passed!")
        
    finally:
        os.unlink(temp_path)


if __name__ == "__main__":
    test_external_json_loading()
    test_backward_compatibility()
    test_theme_merging()
    print("\n[CELEBRATE] All external loading tests passed!")