"""
CLI Testing for AI Agent Suite

Comprehensive tests for command-line interface functionality.
"""

import pytest
from click.testing import CliRunner
from unittest.mock import patch, MagicMock, AsyncMock
from pathlib import Path
import json
import tempfile
import asyncio

from aiagentsuite.cli.main import main
from aiagentsuite.core.suite import AIAgentSuite


class TestCLI:
    """Test CLI commands and functionality."""

    @pytest.fixture
    def runner(self):
        """CLI runner fixture."""
        return CliRunner()

    @pytest.fixture
    def temp_workspace(self):
        """Create a temporary workspace for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)

            # Create basic framework structure
            framework_dir = workspace / "src" / "aiagentsuite" / "framework"
            framework_dir.mkdir(parents=True, exist_ok=True)

            # Create constitution file
            constitution_file = framework_dir / "data" / "MASTER AI AGENT CONSTITUTION.md"
            constitution_file.parent.mkdir(exist_ok=True)
            constitution_file.write_text("# Master AI Agent Constitution\n\nThis is the constitution.")

            # Create principles directory
            principles_dir = framework_dir / "principles"
            principles_dir.mkdir(exist_ok=True)

            # Create principle files
            (principles_dir / "Principle 1_ The VDE Core Philosophy.md").write_text("# Principle 1\nCore philosophy content.")
            (principles_dir / "Principle 2_ Branching and Commit Strategy.md").write_text("# Principle 2\nBranching strategy content.")

            yield workspace

    def test_main_command_help(self, runner):
        """Test main command help output."""
        result = runner.invoke(main, ['--help'])
        assert result.exit_code == 0
        assert "AI Agent Suite CLI" in result.output
        assert "--workspace" in result.output
        assert "init" in result.output
        assert "constitution" in result.output
        assert "protocols" in result.output

    @patch('aiagentsuite.cli.main.AIAgentSuite')
    def test_init_command_success(self, mock_suite_class, runner, temp_workspace):
        """Test successful initialization command."""
        # Mock the suite
        mock_suite = MagicMock()
        mock_suite.initialize = AsyncMock()
        mock_suite_class.return_value = mock_suite

        result = runner.invoke(main, ['--workspace', str(temp_workspace), 'init'])

        assert result.exit_code == 0
        assert "AI Agent Suite initialized successfully" in result.output
        mock_suite.initialize.assert_called_once()

    @patch('aiagentsuite.cli.main.AIAgentSuite')
    def test_init_command_failure(self, mock_suite_class, runner, temp_workspace):
        """Test initialization command failure."""
        # Mock the suite to raise an exception
        mock_suite = MagicMock()
        mock_suite.initialize = AsyncMock(side_effect=Exception("Init failed"))
        mock_suite_class.return_value = mock_suite

        result = runner.invoke(main, ['--workspace', str(temp_workspace), 'init'])

        assert result.exit_code == 1  # Click will exit with 1 on unhandled exceptions

    @patch('aiagentsuite.cli.main.AIAgentSuite')
    def test_constitution_command_success(self, mock_suite_class, runner, temp_workspace):
        """Test successful constitution display."""
        # Mock the suite
        mock_suite = MagicMock()
        mock_suite.initialize = AsyncMock()
        mock_suite.get_constitution = AsyncMock(return_value="Test Constitution Content")
        mock_suite_class.return_value = mock_suite

        result = runner.invoke(main, ['--workspace', str(temp_workspace), 'constitution'])

        assert result.exit_code == 0
        assert "Master AI Agent Constitution" in result.output
        assert "Test Constitution Content" in result.output
        mock_suite.get_constitution.assert_called_once()

    @patch('aiagentsuite.cli.main.AIAgentSuite')
    def test_protocols_command_success(self, mock_suite_class, runner, temp_workspace):
        """Test successful protocols listing."""
        # Mock protocols data
        mock_protocols = {
            "protocol1": {
                "phases": 3,
                "description": "Test protocol 1"
            },
            "protocol2": {
                "phases": 5,
                "description": "Test protocol 2"
            }
        }

        # Mock the suite
        mock_suite = MagicMock()
        mock_suite.initialize = AsyncMock()
        mock_suite.list_protocols = AsyncMock(return_value=mock_protocols)
        mock_suite_class.return_value = mock_suite

        result = runner.invoke(main, ['--workspace', str(temp_workspace), 'protocols'])

        assert result.exit_code == 0
        assert "Available Protocols" in result.output
        assert "protocol1" in result.output
        assert "protocol2" in result.output
        assert "3" in result.output  # phases
        assert "5" in result.output
        mock_suite.list_protocols.assert_called_once()

    @patch('aiagentsuite.cli.main.AIAgentSuite')
    def test_execute_command_success(self, mock_suite_class, runner, temp_workspace):
        """Test successful protocol execution."""
        # Mock execution result
        mock_result = {
            "protocol": "test_protocol",
            "execution_id": "exec_123",
            "duration": 2.5,
            "phases_completed": 3,
            "total_phases": 3,
            "errors": []
        }

        # Mock the suite
        mock_suite = MagicMock()
        mock_suite.initialize = AsyncMock()
        mock_suite.execute_protocol = AsyncMock(return_value=mock_result)
        mock_suite_class.return_value = mock_suite

        result = runner.invoke(main, ['--workspace', str(temp_workspace), 'execute', 'test_protocol'])

        assert result.exit_code == 0
        assert "Protocol Execution: test_protocol" in result.output
        assert "exec_123" in result.output
        assert "2.50s" in result.output
        assert "3/3" in result.output
        mock_suite.execute_protocol.assert_called_once_with('test_protocol', {})

    @patch('aiagentsuite.cli.main.AIAgentSuite')
    def test_execute_command_with_context(self, mock_suite_class, runner, temp_workspace):
        """Test protocol execution with JSON context."""
        # Create a temporary context file
        context_data = {"key": "value", "number": 42}
        context_file = temp_workspace / "context.json"
        context_file.write_text(json.dumps(context_data))

        mock_result = {
            "protocol": "test_protocol",
            "execution_id": "exec_123",
            "duration": 1.0,
            "phases_completed": 2,
            "total_phases": 2,
            "errors": []
        }

        # Mock the suite
        mock_suite = MagicMock()
        mock_suite.initialize = AsyncMock()
        mock_suite.execute_protocol = AsyncMock(return_value=mock_result)
        mock_suite_class.return_value = mock_suite

        result = runner.invoke(main, [
            '--workspace', str(temp_workspace),
            'execute', 'test_protocol',
            '--context', json.dumps(context_data)
        ])

        assert result.exit_code == 0
        mock_suite.execute_protocol.assert_called_once_with('test_protocol', context_data)

    @patch('aiagentsuite.cli.main.AIAgentSuite')
    def test_execute_command_failure(self, mock_suite_class, runner, temp_workspace):
        """Test protocol execution failure."""
        # Mock the suite to raise ValueError
        mock_suite = MagicMock()
        mock_suite.initialize = AsyncMock()
        mock_suite.execute_protocol = AsyncMock(side_effect=ValueError("Protocol not found"))
        mock_suite_class.return_value = mock_suite

        result = runner.invoke(main, ['--workspace', str(temp_workspace), 'execute', 'invalid_protocol'])

        assert result.exit_code == 0  # Click catches exceptions and displays them
        assert "Error: Protocol not found" in result.output

    @patch('aiagentsuite.cli.main.AIAgentSuite')
    def test_memory_command_success(self, mock_suite_class, runner, temp_workspace):
        """Test successful memory context display."""
        # Mock memory context
        mock_context = {
            "content": "Test memory content",
            "last_modified": "2025-01-15T10:30:00"
        }

        # Mock the suite
        mock_suite = MagicMock()
        mock_suite.initialize = AsyncMock()
        mock_suite.get_memory_context = AsyncMock(return_value=mock_context)
        mock_suite_class.return_value = mock_suite

        result = runner.invoke(main, ['--workspace', str(temp_workspace), 'memory', 'active'])

        assert result.exit_code == 0
        assert "Memory Context: Active" in result.output
        assert "Test memory content" in result.output
        assert "2025-01-15T10:30:00" in result.output
        mock_suite.get_memory_context.assert_called_once_with('active')

    def test_memory_command_invalid_type(self, runner, temp_workspace):
        """Test memory command with invalid context type."""
        result = runner.invoke(main, ['--workspace', str(temp_workspace), 'memory', 'invalid'])

        assert result.exit_code == 2  # Click validation error
        assert "Invalid value for" in result.output

    @patch('aiagentsuite.cli.main.AIAgentSuite')
    def test_log_decision_command_success(self, mock_suite_class, runner, temp_workspace):
        """Test successful decision logging."""
        # Mock the suite
        mock_suite = MagicMock()
        mock_suite.initialize = AsyncMock()
        mock_suite.log_decision = AsyncMock()
        mock_suite_class.return_value = mock_suite

        result = runner.invoke(main, [
            '--workspace', str(temp_workspace),
            'log-decision', 'Test Decision', 'Test Rationale'
        ])

        assert result.exit_code == 0
        assert "Decision logged: Test Decision" in result.output
        mock_suite.log_decision.assert_called_once_with('Test Decision', 'Test Rationale', {})

    @patch('aiagentsuite.cli.main.AIAgentSuite')
    def test_log_decision_command_with_context(self, mock_suite_class, runner, temp_workspace):
        """Test decision logging with JSON context."""
        context_data = {"component": "core", "priority": "high"}

        # Mock the suite
        mock_suite = MagicMock()
        mock_suite.initialize = AsyncMock()
        mock_suite.log_decision = AsyncMock()
        mock_suite_class.return_value = mock_suite

        result = runner.invoke(main, [
            '--workspace', str(temp_workspace),
            'log-decision', 'Test Decision', 'Test Rationale',
            '--context', json.dumps(context_data)
        ])

        assert result.exit_code == 0
        mock_suite.log_decision.assert_called_once_with('Test Decision', 'Test Rationale', context_data)

    def test_default_workspace(self, runner):
        """Test CLI with default workspace (current directory)."""
        result = runner.invoke(main, ['init'])

        # Should not fail due to workspace issues, but may fail due to missing framework files
        # The important thing is that the command structure works
        assert result.exit_code in [0, 1]  # Either success or expected failure

    @patch('aiagentsuite.cli.main.AIAgentSuite')
    def test_async_error_handling(self, mock_suite_class, runner, temp_workspace):
        """Test that async errors are properly handled."""
        # Mock the suite to raise an exception during async operation
        mock_suite = MagicMock()
        mock_suite.initialize = AsyncMock(side_effect=Exception("Async error"))
        mock_suite_class.return_value = mock_suite

        result = runner.invoke(main, ['--workspace', str(temp_workspace), 'init'])

        assert result.exit_code == 1  # Should exit with error code

    def test_command_validation(self, runner, temp_workspace):
        """Test command argument validation."""
        # Test missing required arguments
        result = runner.invoke(main, ['--workspace', str(temp_workspace), 'execute'])
        assert result.exit_code == 2  # Missing argument error

        result = runner.invoke(main, ['--workspace', str(temp_workspace), 'log-decision', 'decision'])
        assert result.exit_code == 2  # Missing rationale argument

        result = runner.invoke(main, ['--workspace', str(temp_workspace), 'memory'])
        assert result.exit_code == 2  # Missing context type argument