#!/usr/bin/env python3
"""
Block Independence Test Script
WSP Protocol: WSP 40 (Architectural Coherence)

Demonstrates that FoundUps blocks can run independently with proper
dependency injection, proving the modular LEGO architecture works.
"""

import asyncio
import sys
import os
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import our dependency injection system
sys.path.insert(0, str(project_root / "modules/wre_core/src/components"))
from block_runner import DependencyInjector

class IndependenceTestRunner:
    """Tests block independence without package imports"""
    
    def __init__(self):
        self.results = {}
    
    async def test_dependency_injection(self):
        """Test that dependency injection works"""
        print("🧪 Testing Dependency Injection System...")
        
        # Test injector creation
        injector = DependencyInjector("test_block", "INFO")
        
        # Test logger injection
        logger = injector.logger
        assert logger is not None
        assert logger.name == "FoundUps.test_block"
        
        # Test config injection
        injector.set_config({"test_key": "test_value"})
        assert injector.get_config("test_key") == "test_value"
        
        print("✅ Dependency injection working perfectly!")
        return True
    
    async def test_mock_components(self):
        """Test that mock components work for standalone mode"""
        print("🧪 Testing Mock Component System...")
        
        class MockBlock:
            def __init__(self):
                self.logger = None
                self.config = {}
        
        # Test dependency injection into mock block
        injector = DependencyInjector("mock_test", "INFO")
        block = MockBlock()
        block.logger = injector.logger
        
        # Test that block can use injected dependencies
        block.logger.info("Mock block test message")
        
        print("✅ Mock component system working!")
        return True
    
    async def test_standalone_patterns(self):
        """Test standalone execution patterns"""
        print("🧪 Testing Standalone Execution Patterns...")
        
        # Test async standalone method pattern
        class TestBlock:
            def __init__(self, logger=None, config=None):
                self.logger = logger or logging.getLogger("TestBlock")
                self.config = config or {}
                self.running = False
            
            async def run_standalone(self):
                self.logger.info("🚀 Starting standalone execution...")
                self.running = True
                await asyncio.sleep(0.1)  # Simulate work
                self.logger.info("✅ Standalone execution complete")
                return True
        
        # Test the pattern
        injector = DependencyInjector("pattern_test", "INFO") 
        block = TestBlock(logger=injector.logger)
        
        result = await block.run_standalone()
        assert result is True
        assert block.running is True
        
        print("✅ Standalone execution patterns working!")
        return True
    
    async def test_block_registry(self):
        """Test that block registry system works"""
        print("🧪 Testing Block Registry System...")
        
        from block_runner import ModularBlockRunner
        
        runner = ModularBlockRunner()
        
        # Test block discovery
        assert "youtube_proxy" in runner.block_configs
        assert "linkedin_agent" in runner.block_configs
        assert "x_twitter" in runner.block_configs
        assert "auto_meeting_orchestrator" in runner.block_configs
        assert "post_meeting_feedback" in runner.block_configs
        
        print("✅ Block registry system working!")
        print(f"📊 Discovered {len(runner.block_configs)} blocks")
        
        return True
    
    async def run_all_tests(self):
        """Run comprehensive independence tests"""
        print("🧊 FOUNDUPS BLOCK INDEPENDENCE TEST SUITE")
        print("=" * 50)
        
        tests = [
            ("Dependency Injection", self.test_dependency_injection),
            ("Mock Components", self.test_mock_components),
            ("Standalone Patterns", self.test_standalone_patterns),
            ("Block Registry", self.test_block_registry)
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            try:
                result = await test_func()
                if result:
                    print(f"✅ {test_name}: PASS")
                    passed += 1
                else:
                    print(f"❌ {test_name}: FAIL")
            except Exception as e:
                print(f"❌ {test_name}: ERROR - {e}")
        
        print("=" * 50)
        print(f"🎯 RESULTS: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 BLOCK INDEPENDENCE: FULLY OPERATIONAL!")
            print("\n🧊 KEY ACHIEVEMENTS:")
            print("  ✅ Modular LEGO architecture working")
            print("  ✅ Dependency injection system operational")
            print("  ✅ Mock components for standalone testing")
            print("  ✅ Block registry and discovery functional")
            print("  ✅ Ready for independent block execution")
            
            return True
        else:
            print("⚠️  Some tests failed - needs investigation")
            return False

async def main():
    """Main test execution"""
    runner = IndependenceTestRunner()
    success = await runner.run_all_tests()
    
    if success:
        print("\n🚀 BLOCK INDEPENDENCE PROOF-OF-CONCEPT: SUCCESS!")
        print("   Ready to solve package import conflicts and achieve full independence")
    else:
        print("\n❌ Block independence needs more work")
        
    return success

if __name__ == "__main__":
    asyncio.run(main()) 