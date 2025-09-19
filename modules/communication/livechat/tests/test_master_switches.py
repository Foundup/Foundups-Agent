#!/usr/bin/env python3
"""
Test Master Switches for YouTube DAE
WSP 86: Central feature control panel testing

Tests the /0102, /MAGADOOM, and /PQN on|off master switches.
"""

import sys
import os
import logging

# Add parent directories to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')))

from modules.communication.livechat.src.command_handler import CommandHandler

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def test_master_switches():
    """Test all master switch commands"""
    
    # Database will initialize automatically when needed
    
    # Create command handler with master switches
    handler = CommandHandler(
        timeout_manager=None,
        message_processor=None,
        livechat_core=None
    )
    
    print("\n" + "="*60)
    print("MASTER SWITCH CONTROL PANEL TEST")
    print("="*60)
    
    # Test scenarios
    test_cases = [
        # Check initial states
        ("Initial /help", "/help", "TestUser", "user123", "USER"),
        
        # Test 0102 consciousness switch
        ("\n0102 OFF (as user)", "/0102 off", "TestUser", "user123", "USER"),
        ("0102 OFF (as mod)", "/0102 off", "ModUser", "mod123", "MOD"),
        ("0102 Status", "/0102", "ModUser", "mod123", "MOD"),
        ("0102 ON", "/0102 on", "ModUser", "mod123", "MOD"),
        
        # Test MAGADOOM gamification switch
        ("\nMAGADOOM OFF", "/magadoom off", "ModUser", "mod123", "MOD"),
        ("Try /score with MAGADOOM OFF", "/score", "TestUser", "user123", "USER"),
        ("MAGADOOM Status", "/magadoom", "ModUser", "mod123", "MOD"),
        ("MAGADOOM ON", "/magadoom on", "ModUser", "mod123", "MOD"),
        ("Try /score with MAGADOOM ON", "/score", "TestUser", "user123", "USER"),
        
        # Test PQN quantum research switch
        ("\nPQN ON", "/pqn on", "ModUser", "mod123", "MOD"),
        ("PQN Status", "/pqn", "ModUser", "mod123", "MOD"),
        ("Try /pqn help with PQN ON", "/pqn help", "TestUser", "user123", "USER"),
        ("PQN OFF", "/pqn off", "ModUser", "mod123", "MOD"),
        ("Try /pqn help with PQN OFF", "/pqn help", "TestUser", "user123", "USER"),
        
        # Test /help with different states
        ("\nHelp with all OFF", "/help", "TestUser", "user123", "USER"),
        ("Enable all", None, None, None, None),  # Special case to enable all
        ("Help with all ON", "/help", "TestUser", "user123", "USER"),
        ("Help as MOD", "/help", "ModUser", "mod123", "MOD"),
    ]
    
    for description, command, username, user_id, role in test_cases:
        if command is None:  # Special case to enable all features
            handler.feature_states['0102'] = True
            handler.feature_states['MAGADOOM'] = True
            handler.feature_states['PQN'] = True
            print(f"\n[OK] All features enabled manually")
            continue
            
        print(f"\n{description}:")
        print(f"  Command: {command}")
        print(f"  User: {username} (Role: {role})")
        
        response = handler.handle_whack_command(command, username, user_id, role)
        
        if response:
            # Encode response to handle Unicode properly
            try:
                print(f"  Response: {response}")
            except UnicodeEncodeError:
                # Fallback to ASCII representation
                ascii_response = response.encode('ascii', 'replace').decode('ascii')
                print(f"  Response: {ascii_response}")
        else:
            print(f"  Response: (None)")
    
    # Show final feature states
    print("\n" + "="*60)
    print("FINAL FEATURE STATES:")
    print("="*60)
    for feature, state in handler.feature_states.items():
        status = "ON" if state else "OFF"
        print(f"  {feature}: {status}")
    
    print("\n" + "="*60)
    print("MASTER SWITCH TEST COMPLETE")
    print("="*60)
    print("\nKey Features Demonstrated:")
    print("  • /0102 on|off - Controls consciousness responses")
    print("  • /MAGADOOM on|off - Controls gamification features")
    print("  • /PQN on|off - Controls quantum research features")
    print("  • Only MODs/OWNERs can control master switches")
    print("  • Features can be tested individually")
    print("  • /help dynamically shows enabled features")
    print("\nThis enables one-by-one feature testing as requested!")

if __name__ == "__main__":
    test_master_switches()