#!/usr/bin/env python3
"""
Test core functionality of AI Agent Suite.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from aiagentsuite.core.suite import AIAgentSuite


async def test_core_functionality():
    """Test core functionality."""
    print("Testing AI Agent Suite core functionality...")
    
    try:
        # Initialize suite
        suite = AIAgentSuite()
        print("[SUCCESS] Suite initialized")
        
        # Initialize components
        await suite.initialize()
        print("[SUCCESS] Components initialized")
        
        # Test constitution
        constitution = await suite.get_constitution()
        assert constitution is not None
        print("[SUCCESS] Constitution retrieved")
        
        # Test protocols
        protocols = await suite.list_protocols()
        assert isinstance(protocols, dict)
        print("[SUCCESS] Protocols listed")
        
        # Test memory context
        context = await suite.get_memory_context("active")
        assert isinstance(context, dict)
        print("[SUCCESS] Memory context retrieved")
        
        # Test decision logging
        await suite.log_decision(
            "Test decision",
            "Testing the decision logging functionality",
            {"test": True}
        )
        print("[SUCCESS] Decision logged")
        
        print("\n[SUCCESS] All core functionality tests passed!")
        return True
        
    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
        return False


if __name__ == "__main__":
    success = asyncio.run(test_core_functionality())
    sys.exit(0 if success else 1)
