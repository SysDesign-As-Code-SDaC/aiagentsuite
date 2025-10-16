"""
Comprehensive unit tests for Protocol Executor functionality.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, mock_open
from pathlib import Path
import tempfile
import json

from aiagentsuite.protocols.executor import (
    ProtocolExecutor, ProtocolPhase, ProtocolExecutionContext,
    ProtocolExecutionStatus, ProtocolPhaseStatus, ProtocolDSLInterpreter
)


class TestProtocolPhase:
    """Test protocol phase functionality."""
    
    @pytest.fixture
    def mock_executor(self):
        """Create mock protocol executor."""
        return Mock()
    
    @pytest.fixture
    def sample_phase(self, mock_executor):
        """Create sample protocol phase."""
        return ProtocolPhase(
            number=1,
            title="Test Phase",
            content="This is a test phase with some actions:\n- [ ] Action 1\n- [ ] Action 2",
            executor=mock_executor
        )
    
    def test_phase_initialization(self, sample_phase):
        """Test protocol phase initialization."""
        assert sample_phase.number == 1
        assert sample_phase.title == "Test Phase"
        assert sample_phase.status == ProtocolPhaseStatus.PENDING
        assert sample_phase.result is None
        assert sample_phase.error is None
    
    def test_parse_actions(self, sample_phase):
        """Test action parsing from phase content."""
        actions = sample_phase._parse_actions()
        
        assert len(actions) >= 2
        assert "Action 1" in actions
        assert "Action 2" in actions
    
    def test_parse_actions_imperative(self, mock_executor):
        """Test parsing imperative actions."""
        phase = ProtocolPhase(
            number=1,
            title="Test Phase",
            content="Execute the following:\nImplement user authentication\nValidate input data",
            executor=mock_executor
        )
        
        actions = phase._parse_actions()
        assert len(actions) > 0
    
    @pytest.mark.asyncio
    async def test_execute_phase_success(self, sample_phase):
        """Test successful phase execution."""
        context = ProtocolExecutionContext(protocol_name="Test Protocol")
        
        with patch.object(sample_phase, '_execute_action', return_value={"status": "success"}):
            result = await sample_phase.execute(context)
        
        assert sample_phase.status == ProtocolPhaseStatus.COMPLETED
        assert result["status"] == "completed"
        assert result["phase"] == 1
        assert result["title"] == "Test Phase"
        assert "execution_time" in result
    
    @pytest.mark.asyncio
    async def test_execute_phase_failure(self, sample_phase):
        """Test phase execution failure."""
        context = ProtocolExecutionContext(protocol_name="Test Protocol")
        
        with patch.object(sample_phase, '_execute_action', side_effect=Exception("Test error")):
            with pytest.raises(Exception):
                await sample_phase.execute(context)
        
        assert sample_phase.status == ProtocolPhaseStatus.FAILED
        assert sample_phase.error == "Test error"
    
    @pytest.mark.asyncio
    async def test_execute_validation_action(self, sample_phase):
        """Test validation action execution."""
        context = ProtocolExecutionContext(protocol_name="Test Protocol")
        
        result = await sample_phase._execute_validation_action("Validate security compliance", context)
        
        assert result["action_type"] == "validation"
        assert "security_review" in result["checks_performed"]
        assert "Review OWASP Top 10 compliance" in result["recommendations"]
    
    @pytest.mark.asyncio
    async def test_execute_generation_action(self, sample_phase):
        """Test generation action execution."""
        context = ProtocolExecutionContext(protocol_name="Test Protocol")
        
        result = await sample_phase._execute_generation_action("Generate test files", context)
        
        assert result["action_type"] == "generation"
        assert "test_file.py" in result["files_created"]
        assert result["code_generated"] == 150
    
    @pytest.mark.asyncio
    async def test_execute_documentation_action(self, sample_phase):
        """Test documentation action execution."""
        context = ProtocolExecutionContext(protocol_name="Test Protocol")
        
        result = await sample_phase._execute_documentation_action("Document the API", context)
        
        assert result["action_type"] == "documentation"
        assert "Implementation Details" in result["sections_added"]
        assert result["word_count"] == 250
    
    @pytest.mark.asyncio
    async def test_execute_review_action(self, sample_phase):
        """Test review action execution."""
        context = ProtocolExecutionContext(protocol_name="Test Protocol")
        
        result = await sample_phase._execute_review_action("Review code quality", context)
        
        assert result["action_type"] == "review"
        assert "readability" in result["criteria_checked"]
        assert result["approval_status"] == "approved"
    
    @pytest.mark.asyncio
    async def test_execute_testing_action(self, sample_phase):
        """Test testing action execution."""
        context = ProtocolExecutionContext(protocol_name="Test Protocol")
        
        result = await sample_phase._execute_testing_action("Run unit tests", context)
        
        assert result["action_type"] == "testing"
        assert "unit_tests" in result["tests_executed"]
        assert result["pass_rate"] == 0.95
    
    @pytest.mark.asyncio
    async def test_execute_manual_action(self, sample_phase):
        """Test manual action execution."""
        context = ProtocolExecutionContext(protocol_name="Test Protocol")
        
        result = await sample_phase._execute_action("Manual action required", context)
        
        assert result["action_type"] == "manual"
        assert result["status"] == "marked_complete"
        assert "Manual action" in result["note"]


class TestProtocolExecutionContext:
    """Test protocol execution context."""
    
    def test_context_initialization(self):
        """Test execution context initialization."""
        context = ProtocolExecutionContext(protocol_name="Test Protocol")
        
        assert context.protocol_name == "Test Protocol"
        assert context.status == ProtocolExecutionStatus.PENDING
        assert context.current_phase == 0
        assert len(context.phases) == 0
        assert len(context.results) == 0
        assert len(context.errors) == 0
        assert context.execution_id.startswith("exec_")
    
    def test_duration_property(self):
        """Test duration calculation."""
        context = ProtocolExecutionContext(protocol_name="Test Protocol")
        
        # Duration should be small initially
        assert context.duration >= 0
        assert context.duration < 1.0  # Should be very small


class TestProtocolDSLInterpreter:
    """Test protocol DSL interpreter."""
    
    @pytest.fixture
    def mock_executor(self):
        """Create mock protocol executor."""
        return Mock()
    
    @pytest.fixture
    def dsl_interpreter(self, mock_executor):
        """Create DSL interpreter."""
        return ProtocolDSLInterpreter(mock_executor)
    
    def test_parse_dsl_commands(self, dsl_interpreter):
        """Test DSL command parsing."""
        dsl_content = """
        @validate {security_check}
        @generate {test_files}
        validate: Check input validation
        """
        
        commands = dsl_interpreter._parse_dsl_commands(dsl_content)
        
        assert len(commands) >= 2
        command_names = [cmd["command"] for cmd in commands]
        assert "validate" in command_names
        assert "generate" in command_names
    
    @pytest.mark.asyncio
    async def test_execute_dsl_command_validate(self, dsl_interpreter):
        """Test DSL validate command execution."""
        command = {"command": "validate", "args": "security_check"}
        context = {"project": "test"}
        
        result = await dsl_interpreter._execute_dsl_command(command, context)
        
        assert result["command"] == "validate"
        assert result["status"] == "success"
        assert "Validation executed" in result["result"]
    
    @pytest.mark.asyncio
    async def test_execute_dsl_command_generate(self, dsl_interpreter):
        """Test DSL generate command execution."""
        command = {"command": "generate", "args": "test_files"}
        context = {"project": "test"}
        
        result = await dsl_interpreter._execute_dsl_command(command, context)
        
        assert result["command"] == "generate"
        assert result["status"] == "success"
        assert "Code generated" in result["result"]
    
    @pytest.mark.asyncio
    async def test_execute_dsl_command_test(self, dsl_interpreter):
        """Test DSL test command execution."""
        command = {"command": "test", "args": "unit_tests"}
        context = {"project": "test"}
        
        result = await dsl_interpreter._execute_dsl_command(command, context)
        
        assert result["command"] == "test"
        assert result["status"] == "success"
        assert "Tests executed" in result["result"]
    
    @pytest.mark.asyncio
    async def test_execute_dsl_command_unknown(self, dsl_interpreter):
        """Test DSL unknown command execution."""
        command = {"command": "unknown", "args": "test"}
        context = {"project": "test"}
        
        result = await dsl_interpreter._execute_dsl_command(command, context)
        
        assert result["command"] == "unknown"
        assert result["status"] == "skipped"
        assert "Unknown command" in result["result"]
    
    @pytest.mark.asyncio
    async def test_parse_and_execute_dsl_success(self, dsl_interpreter):
        """Test successful DSL parsing and execution."""
        dsl_content = """
        @validate {security_check}
        @generate {test_files}
        """
        
        result = await dsl_interpreter.parse_and_execute_dsl(dsl_content, {"project": "test"})
        
        assert result["dsl_parsed"] is True
        assert result["commands_executed"] >= 2
        assert result["status"] == "completed"
        assert len(result["results"]) >= 2
    
    @pytest.mark.asyncio
    async def test_parse_and_execute_dsl_failure(self, dsl_interpreter):
        """Test DSL parsing and execution failure."""
        # Invalid DSL content that should cause parsing to fail
        dsl_content = "invalid dsl content"
        
        with patch.object(dsl_interpreter, '_parse_dsl_commands', side_effect=Exception("Parse error")):
            result = await dsl_interpreter.parse_and_execute_dsl(dsl_content, {"project": "test"})
        
        assert result["dsl_parsed"] is False
        assert result["status"] == "failed"
        assert "Parse error" in result["error"]


class TestProtocolExecutor:
    """Test protocol executor functionality."""
    
    @pytest.fixture
    def temp_workspace(self):
        """Create temporary workspace with protocol files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace_path = Path(temp_dir)
            
            # Create a sample protocol file
            protocol_content = """
# Test Protocol

**Objective**: To test protocol execution functionality.

Duration: 30 minutes
Complexity: Medium
Required Roles: Developer, Tester

## **Phase 1: Analysis**

- [ ] Analyze requirements
- [ ] Review existing code
- [ ] Identify potential issues

## **Phase 2: Implementation**

- [ ] Implement core functionality
- [ ] Add error handling
- [ ] Write unit tests

```dsl
@validate {security_check}
@generate {test_files}
```
"""
            
            protocol_file = workspace_path / "Protocol_ Test Protocol.md"
            protocol_file.write_text(protocol_content)
            
            yield workspace_path
    
    @pytest.fixture
    def executor(self, temp_workspace):
        """Create protocol executor with temporary workspace."""
        return ProtocolExecutor(temp_workspace)
    
    @pytest.mark.asyncio
    async def test_initialization(self, executor):
        """Test protocol executor initialization."""
        await executor.initialize()
        
        assert len(executor._protocols) == 1
        assert "Test Protocol" in executor._protocols
        assert executor._dsl_interpreter is not None
    
    @pytest.mark.asyncio
    async def test_load_protocols(self, executor):
        """Test protocol loading."""
        await executor._load_protocols()
        
        assert len(executor._protocols) == 1
        protocol = executor._protocols["Test Protocol"]
        assert protocol["name"] == "Test Protocol"
        assert len(protocol["phases"]) == 2
        assert len(protocol["dsl_blocks"]) == 1
    
    def test_extract_protocol_name(self, executor):
        """Test protocol name extraction."""
        name = executor._extract_protocol_name("Protocol_ Test Protocol.md")
        assert name == "Test Protocol"
        
        name = executor._extract_protocol_name("Protocol_Another_Test.md")
        assert name == "Another Test"
    
    def test_parse_protocol_phases(self, executor):
        """Test protocol phase parsing."""
        content = """
## **Phase 1: Analysis**
This is phase 1 content.

## **Phase 2: Implementation**
This is phase 2 content.
"""
        
        phases = executor._parse_protocol_phases(content)
        
        assert len(phases) == 2
        assert phases[0].number == 1
        assert phases[0].title == "Analysis"
        assert phases[1].number == 2
        assert phases[1].title == "Implementation"
    
    def test_extract_dsl_blocks(self, executor):
        """Test DSL block extraction."""
        content = """
Some content here.

```dsl
@validate {security_check}
@generate {test_files}
```

More content.

```dsl
@test {unit_tests}
```
"""
        
        dsl_blocks = executor._extract_dsl_blocks(content)
        
        assert len(dsl_blocks) == 2
        assert "@validate {security_check}" in dsl_blocks[0]
        assert "@test {unit_tests}" in dsl_blocks[1]
    
    def test_extract_metadata(self, executor):
        """Test metadata extraction."""
        content = """
Duration: 30 minutes
Complexity: Medium
Required Roles: Developer, Tester, Reviewer
"""
        
        metadata = executor._extract_metadata(content)
        
        assert metadata["estimated_duration"] == "30 minutes"
        assert metadata["complexity"] == "Medium"
        assert "Developer" in metadata["required_roles"]
        assert "Tester" in metadata["required_roles"]
        assert "Reviewer" in metadata["required_roles"]
    
    @pytest.mark.asyncio
    async def test_list_protocols(self, executor):
        """Test protocol listing."""
        await executor.initialize()
        protocols = await executor.list_protocols()
        
        assert len(protocols) == 1
        assert "Test Protocol" in protocols
        protocol_info = protocols["Test Protocol"]
        assert protocol_info["name"] == "Test Protocol"
        assert protocol_info["phases"] == 2
        assert protocol_info["dsl_support"] is True
    
    def test_extract_protocol_description(self, executor):
        """Test protocol description extraction."""
        content = """
# Test Protocol

**Objective**: This is a test protocol for validation.

## Phase 1: Analysis
Some content here.
"""
        
        description = executor._extract_protocol_description(content)
        assert description == "This is a test protocol for validation."
    
    @pytest.mark.asyncio
    async def test_execute_protocol_success(self, executor):
        """Test successful protocol execution."""
        await executor.initialize()
        
        context = {"project": "test", "environment": "development"}
        result = await executor.execute_protocol("Test Protocol", context)
        
        assert result["protocol"] == "Test Protocol"
        assert "execution_id" in result
        assert result["duration"] > 0
        assert result["phases_completed"] == 2
        assert result["total_phases"] == 2
        assert len(result["phase_results"]) == 2
        assert result["context"] == context
        assert len(result["errors"]) == 0
        assert "dsl_results" in result
    
    @pytest.mark.asyncio
    async def test_execute_protocol_not_found(self, executor):
        """Test protocol execution with non-existent protocol."""
        await executor.initialize()
        
        with pytest.raises(ValueError, match="Protocol 'Non-existent Protocol' not found"):
            await executor.execute_protocol("Non-existent Protocol", {})
    
    @pytest.mark.asyncio
    async def test_execute_protocol_phase_failure(self, executor):
        """Test protocol execution with phase failure."""
        await executor.initialize()
        
        # Mock a phase to fail
        protocol = executor._protocols["Test Protocol"]
        original_execute = protocol["phases"][0].execute
        
        async def failing_execute(context):
            raise Exception("Phase execution failed")
        
        protocol["phases"][0].execute = failing_execute
        
        try:
            result = await executor.execute_protocol("Test Protocol", {})
            
            # Should have errors and incomplete execution
            assert len(result["errors"]) > 0
            assert result["phases_completed"] < result["total_phases"]
        finally:
            # Restore original method
            protocol["phases"][0].execute = original_execute
    
    @pytest.mark.asyncio
    async def test_get_protocol_details(self, executor):
        """Test protocol details retrieval."""
        await executor.initialize()
        
        details = await executor.get_protocol_details("Test Protocol")
        
        assert details is not None
        assert details["name"] == "Test Protocol"
        assert len(details["phases"]) == 2
        assert details["dsl_support"] is True
        assert "content" in details
        assert "metadata" in details
    
    @pytest.mark.asyncio
    async def test_get_protocol_details_not_found(self, executor):
        """Test protocol details retrieval for non-existent protocol."""
        await executor.initialize()
        
        details = await executor.get_protocol_details("Non-existent Protocol")
        assert details is None
    
    @pytest.mark.asyncio
    async def test_get_active_executions(self, executor):
        """Test active executions retrieval."""
        await executor.initialize()
        
        # Start an execution
        context = {"project": "test"}
        execution_task = asyncio.create_task(
            executor.execute_protocol("Test Protocol", context)
        )
        
        # Give it a moment to start
        await asyncio.sleep(0.01)
        
        active_executions = await executor.get_active_executions()
        
        # The execution might complete very quickly, so we just check that the method works
        # and doesn't raise an exception
        assert isinstance(active_executions, dict)
        
        # Wait for execution to complete
        await execution_task
    
    @pytest.mark.asyncio
    async def test_cancel_execution(self, executor):
        """Test execution cancellation."""
        await executor.initialize()
        
        # Test cancellation with non-existent execution ID
        cancelled = await executor.cancel_execution("non-existent-id")
        assert cancelled is False
        
        # Test that the method doesn't raise exceptions
        assert isinstance(cancelled, bool)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
