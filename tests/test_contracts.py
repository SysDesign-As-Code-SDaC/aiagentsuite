"""
Contract Tests for AI Agent Suite

Tests that components adhere to their defined interfaces and contracts.
Ensures compatibility between components and prevents breaking changes.
"""

import pytest
import pytest_asyncio
import asyncio
from typing import Dict, Any, List, Optional
from unittest.mock import Mock, AsyncMock
import json

from aiagentsuite.core import AIAgentSuite
from aiagentsuite.framework.manager import FrameworkManager
from aiagentsuite.protocols.executor import ProtocolExecutor, ProtocolExecutionStatus, ProtocolPhase
from aiagentsuite.memory_bank.manager import MemoryBank
from aiagentsuite.core.errors import AIAgentSuiteError, ValidationError
from aiagentsuite.core.security import SecurityContext, SecurityLevel, Permission
from aiagentsuite.core.config import ConfigurationManager
from aiagentsuite.core.cache import CacheManager


class TestContractFrameworkManager:
    """Test FrameworkManager contract compliance."""

    @pytest_asyncio.fixture
    async def framework_manager(self, tmp_path):
        manager = FrameworkManager(tmp_path)
        yield manager

    @pytest.mark.asyncio
    async def test_get_constitution_contract(self, framework_manager):
        """Test get_constitution method contract."""
        # Should return string or None
        result = await framework_manager.get_constitution()
        assert isinstance(result, (str, type(None)))

    @pytest.mark.asyncio
    async def test_get_principles_contract(self, framework_manager):
        """Test principles methods contract."""
        # get_all_principles should return dict
        all_principles = await framework_manager.get_all_principles()
        assert isinstance(all_principles, dict)

        # get_principle should work for existing and non-existing keys
        result = await framework_manager.get_principle("nonexistent")
        assert isinstance(result, str)  # Should return error message

    @pytest.mark.asyncio
    async def test_project_context_contract(self, framework_manager):
        """Test project context contract."""
        result = await framework_manager.get_project_context()
        assert isinstance(result, (str, type(None)))


class TestContractProtocolExecutor:
    """Test ProtocolExecutor contract compliance."""

    @pytest_asyncio.fixture
    async def protocol_executor(self, tmp_path):
        # Create a protocol file for testing
        protocols_dir = tmp_path / "protocols"
        protocols_dir.mkdir(parents=True)

        protocol_content = """# Test Protocol

## **Phase 1: Setup**
- Initialize test environment
- Validate inputs

## **Phase 2: Execute**
- Run main logic
- Check results

## **Phase 3: Cleanup**
- Clean up resources
- Generate report
"""

        protocol_file = protocols_dir / "Protocol_Test Protocol.md"
        protocol_file.write_text(protocol_content)

        executor = ProtocolExecutor(tmp_path)
        yield executor

    @pytest.mark.asyncio
    async def test_list_protocols_contract(self, protocol_executor):
        """Test list_protocols method contract."""
        result = await protocol_executor.list_protocols()
        assert isinstance(result, dict)

        # Each protocol entry should have required fields
        for protocol_name, protocol_info in result.items():
            assert isinstance(protocol_name, str)
            assert isinstance(protocol_info, dict)
            assert "name" in protocol_info
            assert "phases" in protocol_info
            assert "description" in protocol_info
            assert isinstance(protocol_info["phases"], int)
            assert isinstance(protocol_info["description"], str)

    @pytest.mark.asyncio
    async def test_execute_protocol_contract(self, protocol_executor):
        """Test execute_protocol method contract."""
        result = await protocol_executor.execute_protocol("Test Protocol", {"test": True})

        # Result should contain expected structure
        assert isinstance(result, dict)
        assert "protocol" in result
        assert "execution_id" in result
        assert "duration" in result
        assert "phases_completed" in result
        assert "total_phases" in result
        assert "phase_results" in result
        assert "context" in result
        assert "errors" in result

        # Protocol should match what was requested
        assert result["protocol"] == "Test Protocol"

        # Execution time should be reasonable
        assert result["duration"] >= 0

        # Context should be preserved
        assert result["context"]["test"] is True

    @pytest.mark.asyncio
    async def test_get_protocol_details_contract(self, protocol_executor):
        """Test get_protocol_details contract."""
        result = await protocol_executor.get_protocol_details("Test Protocol")

        if result:  # Protocol exists
            assert isinstance(result, dict)
            assert "name" in result
            assert "phases" in result
            assert "content" in result
            assert "metadata" in result

        # Should return None for non-existent protocol
        result = await protocol_executor.get_protocol_details("NonExistent Protocol")
        assert result is None


class TestContractMemoryBank:
    """Test MemoryBank contract compliance."""

    @pytest_asyncio.fixture
    async def memory_bank(self, tmp_path):
        bank = MemoryBank(tmp_path)
        yield bank

    @pytest.mark.asyncio
    async def test_get_context_contract(self, memory_bank):
        """Test get_context method contract."""
        result = await memory_bank.get_context("active")
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_update_context_contract(self, memory_bank):
        """Test update_context method contract."""
        test_data = {"key": "value", "timestamp": "test"}

        # Should not raise exception
        await memory_bank.update_context("active", test_data)

        # Should be able to retrieve updated data
        result = await memory_bank.get_context("active")
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_log_decision_contract(self, memory_bank):
        """Test log_decision method contract."""
        # Should not raise exception
        await memory_bank.log_decision(
            "Test decision",
            "Rationale for test decision",
            {"component": "test"}
        )


class TestContractSecurityManager:
    """Test security manager contract compliance."""

    @pytest_asyncio.fixture
    async def security_manager(self):
        from aiagentsuite.core.security import SecurityManager
        manager = SecurityManager()
        yield manager

    @pytest.mark.asyncio
    async def test_secure_operation_contract(self, security_manager):
        """Test secure_operation decorator contract."""
        context = SecurityContext(
            user=Mock(),
            security_level=SecurityLevel.INTERNAL
        )

        # Create a test function with the decorator
        decorated_func = security_manager.secure_operation(
            permission=Permission.PROTOCOL_EXECUTE,
            security_level=SecurityLevel.INTERNAL
        )(lambda: "success")

        # Function should be callable
        assert callable(decorated_func)

    @pytest.mark.asyncio
    async def test_create_user_contract(self, security_manager):
        """Test create_user method contract."""
        user = security_manager.create_user(
            "testuser",
            "test@example.com",
            "password123",
            ["developer"]
        )

        # User object should have required attributes
        assert hasattr(user, 'user_id')
        assert hasattr(user, 'username')
        assert hasattr(user, 'email')
        assert hasattr(user, 'roles')
        assert hasattr(user, 'is_active')
        assert user.username == "testuser"
        assert user.email == "test@example.com"

    @pytest.mark.asyncio
    async def test_validate_input_contract(self, security_manager):
        """Test validate_input method contract."""
        # Should validate string inputs
        result = await security_manager.validate_input("test input", "test_operation")
        assert isinstance(result, str)

        # Should validate dict inputs
        result = await security_manager.validate_input({"key": "value"}, "test_operation")
        assert isinstance(result, dict)
        assert result.get("key") == "value"


class TestContractCacheManager:
    """Test cache manager contract compliance."""

    @pytest_asyncio.fixture
    async def cache_manager(self):
        from aiagentsuite.core.cache import CacheManager
        manager = CacheManager()
        await manager.initialize()
        yield manager

    @pytest.mark.asyncio
    async def test_cache_operations_contract(self, cache_manager):
        """Test basic cache operations contract."""
        # Should be able to set and get values
        success = await cache_manager.get_cache("framework").set("test_key", "test_value", 60)
        assert isinstance(success, bool)

        value = await cache_manager.get_cache("framework").get("test_key")
        assert value == "test_value"

        # Should be able to delete values
        deleted = await cache_manager.get_cache("framework").delete("test_key")
        assert isinstance(deleted, bool)

    @pytest.mark.asyncio
    async def test_get_cache_stats_contract(self, cache_manager):
        """Test cache stats contract."""
        stats = await cache_manager.get_cache_stats()
        assert isinstance(stats, dict)

        # Stats should contain expected cache types
        expected_caches = ["framework", "protocol", "memory", "conversation"]
        for cache_name in expected_caches:
            assert cache_name in stats


class TestContractConfigurationManager:
    """Test configuration manager contract compliance."""

    @pytest_asyncio.fixture
    async def config_manager(self):
        from aiagentsuite.core.config import ConfigurationManager
        manager = ConfigurationManager()
        yield manager

    @pytest.mark.asyncio
    async def test_get_value_contract(self, config_manager):
        """Test get_value method contract."""
        # Should return any type or None
        result = await config_manager.get_value("nonexistent_key")
        assert result is None  # Non-existent keys should return None

    @pytest.mark.asyncio
    async def test_set_value_contract(self, config_manager):
        """Test set_value method contract."""
        # Should return boolean indicating success
        success = await config_manager.set_value("test_key", "test_value")
        assert isinstance(success, bool)

    @pytest.mark.asyncio
    async def test_environment_info_contract(self, config_manager):
        """Test environment info structure."""
        info = await config_manager.get_environment_info()
        assert isinstance(info, dict)
        assert "environment" in info
        assert "debug" in info
        assert "version" in info
        assert "components" in info


class TestContractObservabilityManager:
    """Test observability manager contract compliance."""

    @pytest_asyncio.fixture
    async def observability_manager(self):
        from aiagentsuite.core.observability import ObservabilityManager
        manager = ObservabilityManager()
        yield manager

    @pytest.mark.asyncio
    async def test_health_check_contract(self, observability_manager):
        """Test health check contract."""
        health = await observability_manager.get_health_status()
        assert isinstance(health, dict)
        assert "status" in health
        assert "healthy_components" in health
        assert "total_components" in health

    @pytest.mark.asyncio
    async def test_run_health_checks_contract(self, observability_manager):
        """Test run_health_checks contract."""
        results = await observability_manager.run_health_checks()
        assert isinstance(results, list)

        for result in results:
            assert hasattr(result, 'name')
            assert hasattr(result, 'status')
            assert hasattr(result, 'message')
            assert hasattr(result, 'is_healthy')

    @pytest.mark.asyncio
    async def test_instrument_function_contract(self, observability_manager):
        """Test instrument_function decorator contract."""
        @observability_manager.instrument_function("test_function")
        async def test_func():
            return "success"

        # Should be callable and return expected result
        result = await test_func()
        assert result == "success"


class TestComponentIntegrationContracts:
    """Test integration contracts between components."""

    @pytest_asyncio.fixture
    async def ai_agent_suite(self, tmp_path):
        """Create a fully initialized AI Agent Suite."""
        suite = AIAgentSuite(tmp_path)
        await suite.initialize()
        yield suite

    @pytest.mark.asyncio
    async def test_suite_core_contract(self, ai_agent_suite):
        """Test core AIAgentSuite contract."""
        # Should have all expected methods
        assert hasattr(ai_agent_suite, 'get_constitution')
        assert hasattr(ai_agent_suite, 'list_protocols')
        assert hasattr(ai_agent_suite, 'execute_protocol')
        assert hasattr(ai_agent_suite, 'get_memory_context')
        assert hasattr(ai_agent_suite, 'log_decision')

        # Methods should be callable
        assert callable(ai_agent_suite.get_constitution)
        assert callable(ai_agent_suite.list_protocols)
        assert callable(ai_agent_suite.execute_protocol)
        assert callable(ai_agent_suite.get_memory_context)
        assert callable(ai_agent_suite.log_decision)

    @pytest.mark.asyncio
    async def test_integration_constitution_flow(self, ai_agent_suite):
        """Test constitution retrieval integration."""
        constitution = await ai_agent_suite.get_constitution()
        assert isinstance(constitution, (str, type(None)))

    @pytest.mark.asyncio
    async def test_integration_protocol_flow(self, ai_agent_suite):
        """Test protocol operations integration."""
        protocols = await ai_agent_suite.list_protocols()
        assert isinstance(protocols, dict)

        # If protocols exist, test execution
        if protocols:
            protocol_name = next(iter(protocols.keys()))
            result = await ai_agent_suite.execute_protocol(protocol_name, {"test": True})
            assert isinstance(result, dict)
            assert "protocol" in result

    @pytest.mark.asyncio
    async def test_integration_memory_flow(self, ai_agent_suite):
        """Test memory operations integration."""
        # Test getting context
        context = await ai_agent_suite.get_memory_context("active")
        assert isinstance(context, dict)

        # Test logging decision
        await ai_agent_suite.log_decision(
            "Integration test decision",
            "Testing memory bank integration",
            {"component": "test_suite"}
        )

    @pytest.mark.asyncio
    async def test_error_handling_contract(self, ai_agent_suite):
        """Test error handling across component integration."""
        # Invalid protocol should raise appropriate error
        with pytest.raises((AIAgentSuiteError, ValueError)):
            await ai_agent_suite.execute_protocol("NonExistent Protocol", {})

        # Invalid context should be handled gracefully
        try:
            await ai_agent_suite.get_memory_context("invalid_context")
        except Exception as e:
            # Should be a controlled error, not a system crash
            assert isinstance(e, (AIAgentSuiteError, ValueError, KeyError))


class TestPerformanceContracts:
    """Test performance-related contracts."""

    @pytest.mark.asyncio
    async def test_async_performance_contract(self):
        """Test that async operations complete within reasonable time."""
        import time

        start_time = time.time()
        suite = AIAgentSuite(".")
        await suite.initialize()
        init_time = time.time() - start_time

        # Initialization should complete in reasonable time (< 5 seconds)
        assert init_time < 5.0, f"Initialization too slow: {init_time:.2f}s"

        # Basic operations should also be reasonably fast
        start_time = time.time()
        await suite.list_protocols()
        list_time = time.time() - start_time
        assert list_time < 1.0, f"Protocol listing too slow: {list_time:.2f}s"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
