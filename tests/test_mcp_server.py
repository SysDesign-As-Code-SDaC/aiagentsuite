"""
Comprehensive unit tests for MCP Server functionality.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from pathlib import Path
import json

from aiagentsuite.mcp import (
    MCPServer, MCPContext, MCPTool, MCPResponse, MCPResource,
    ConstitutionToolHandler, ListProtocolsToolHandler, ExecuteProtocolToolHandler,
    MemoryContextToolHandler, LogDecisionToolHandler, FrameworkResourceProvider
)


class TestMCPTool:
    """Test MCP tool definitions."""
    
    def test_mcp_tool_creation(self):
        """Test MCP tool creation and serialization."""
        tool = MCPTool(
            name="test_tool",
            description="A test tool",
            input_schema={"type": "object", "properties": {"param": {"type": "string"}}}
        )
        
        assert tool.name == "test_tool"
        assert tool.description == "A test tool"
        assert tool.input_schema["type"] == "object"
        
        tool_dict = tool.to_dict()
        assert tool_dict["name"] == "test_tool"
        assert tool_dict["inputSchema"]["type"] == "object"


class TestMCPResponse:
    """Test MCP response handling."""
    
    def test_success_response(self):
        """Test successful MCP response."""
        content = [{"type": "text", "text": "Success"}]
        response = MCPResponse(content=content)
        
        assert response.content == content
        assert not response.is_error
        
        response_dict = response.to_dict()
        assert response_dict["content"] == content
        assert "isError" not in response_dict
    
    def test_error_response(self):
        """Test error MCP response."""
        content = [{"type": "text", "text": "Error occurred"}]
        response = MCPResponse(content=content, is_error=True)
        
        assert response.content == content
        assert response.is_error
        
        response_dict = response.to_dict()
        assert response_dict["content"] == content
        assert response_dict["isError"] is True


class TestMCPContext:
    """Test MCP context management."""
    
    def test_mcp_context_creation(self):
        """Test MCP context initialization."""
        workspace_path = Path("/test/workspace")
        framework_manager = Mock()
        memory_bank = Mock()
        protocol_executor = Mock()
        
        context = MCPContext(
            workspace_path=workspace_path,
            framework_manager=framework_manager,
            memory_bank=memory_bank,
            protocol_executor=protocol_executor
        )
        
        assert context.workspace_path == workspace_path
        assert context.framework == framework_manager
        assert context.memory_bank == memory_bank
        assert context.protocol_executor == protocol_executor


class TestConstitutionToolHandler:
    """Test constitution tool handler."""
    
    @pytest.fixture
    def mock_context(self):
        """Create mock MCP context."""
        context = Mock(spec=MCPContext)
        context.framework = AsyncMock()
        return context
    
    @pytest.mark.asyncio
    async def test_get_constitution_success(self, mock_context):
        """Test successful constitution retrieval."""
        mock_context.framework.get_constitution.return_value = "Test Constitution"
        
        handler = ConstitutionToolHandler(mock_context)
        response = await handler.execute({})
        
        assert not response.is_error
        assert len(response.content) == 1
        assert response.content[0]["type"] == "text"
        assert response.content[0]["text"] == "Test Constitution"
        mock_context.framework.get_constitution.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_constitution_error(self, mock_context):
        """Test constitution retrieval error handling."""
        mock_context.framework.get_constitution.side_effect = Exception("Test error")
        
        handler = ConstitutionToolHandler(mock_context)
        response = await handler.execute({})
        
        assert response.is_error
        assert len(response.content) == 1
        assert "Error retrieving constitution" in response.content[0]["text"]


class TestListProtocolsToolHandler:
    """Test list protocols tool handler."""
    
    @pytest.fixture
    def mock_context(self):
        """Create mock MCP context."""
        context = Mock(spec=MCPContext)
        context.protocol_executor = AsyncMock()
        return context
    
    @pytest.mark.asyncio
    async def test_list_protocols_success(self, mock_context):
        """Test successful protocol listing."""
        mock_protocols = {
            "Protocol 1": {"name": "Protocol 1", "phases": 3},
            "Protocol 2": {"name": "Protocol 2", "phases": 5}
        }
        mock_context.protocol_executor.list_protocols.return_value = mock_protocols
        
        handler = ListProtocolsToolHandler(mock_context)
        response = await handler.execute({})
        
        assert not response.is_error
        assert len(response.content) == 2
        assert response.content[0]["type"] == "text"
        assert "Protocol 1, Protocol 2" in response.content[0]["text"]
        assert response.content[1]["type"] == "json"
        assert response.content[1]["json"] == mock_protocols
    
    @pytest.mark.asyncio
    async def test_list_protocols_error(self, mock_context):
        """Test protocol listing error handling."""
        mock_context.protocol_executor.list_protocols.side_effect = Exception("Test error")
        
        handler = ListProtocolsToolHandler(mock_context)
        response = await handler.execute({})
        
        assert response.is_error
        assert "Error listing protocols" in response.content[0]["text"]


class TestExecuteProtocolToolHandler:
    """Test execute protocol tool handler."""
    
    @pytest.fixture
    def mock_context(self):
        """Create mock MCP context."""
        context = Mock(spec=MCPContext)
        context.protocol_executor = AsyncMock()
        return context
    
    @pytest.mark.asyncio
    async def test_execute_protocol_success(self, mock_context):
        """Test successful protocol execution."""
        mock_result = {
            "protocol": "Test Protocol",
            "execution_id": "exec_123",
            "duration": 1.5,
            "phases_completed": 3,
            "total_phases": 3
        }
        mock_context.protocol_executor.execute_protocol.return_value = mock_result
        
        handler = ExecuteProtocolToolHandler(mock_context)
        response = await handler.execute({
            "protocol_name": "Test Protocol",
            "context": {"param": "value"}
        })
        
        assert not response.is_error
        assert len(response.content) == 2
        assert "Successfully executed protocol" in response.content[0]["text"]
        assert response.content[1]["json"] == mock_result
        mock_context.protocol_executor.execute_protocol.assert_called_once_with(
            "Test Protocol", {"param": "value"}
        )
    
    @pytest.mark.asyncio
    async def test_execute_protocol_missing_name(self, mock_context):
        """Test protocol execution with missing protocol name."""
        handler = ExecuteProtocolToolHandler(mock_context)
        response = await handler.execute({})
        
        assert response.is_error
        assert "protocol_name is required" in response.content[0]["text"]
    
    @pytest.mark.asyncio
    async def test_execute_protocol_error(self, mock_context):
        """Test protocol execution error handling."""
        mock_context.protocol_executor.execute_protocol.side_effect = Exception("Test error")
        
        handler = ExecuteProtocolToolHandler(mock_context)
        response = await handler.execute({
            "protocol_name": "Test Protocol",
            "context": {}
        })
        
        assert response.is_error
        assert "Error executing protocol" in response.content[0]["text"]


class TestMemoryContextToolHandler:
    """Test memory context tool handler."""
    
    @pytest.fixture
    def mock_context(self):
        """Create mock MCP context."""
        context = Mock(spec=MCPContext)
        context.memory_bank = AsyncMock()
        return context
    
    @pytest.mark.asyncio
    async def test_get_memory_context_success(self, mock_context):
        """Test successful memory context retrieval."""
        mock_context_data = {
            "type": "active",
            "content": "Test content",
            "last_modified": "2023-01-01T00:00:00"
        }
        mock_context.memory_bank.get_context.return_value = mock_context_data
        
        handler = MemoryContextToolHandler(mock_context)
        response = await handler.execute({"context_type": "active"})
        
        assert not response.is_error
        assert len(response.content) == 2
        assert "Retrieved active context" in response.content[0]["text"]
        assert response.content[1]["json"] == mock_context_data
        mock_context.memory_bank.get_context.assert_called_once_with("active")
    
    @pytest.mark.asyncio
    async def test_get_memory_context_missing_type(self, mock_context):
        """Test memory context retrieval with missing context type."""
        handler = MemoryContextToolHandler(mock_context)
        response = await handler.execute({})
        
        assert response.is_error
        assert "context_type is required" in response.content[0]["text"]
    
    @pytest.mark.asyncio
    async def test_get_memory_context_invalid_type(self, mock_context):
        """Test memory context retrieval with invalid context type."""
        handler = MemoryContextToolHandler(mock_context)
        response = await handler.execute({"context_type": "invalid"})
        
        assert response.is_error
        assert "context_type must be one of" in response.content[0]["text"]
    
    @pytest.mark.asyncio
    async def test_get_memory_context_error(self, mock_context):
        """Test memory context retrieval error handling."""
        mock_context.memory_bank.get_context.side_effect = Exception("Test error")
        
        handler = MemoryContextToolHandler(mock_context)
        response = await handler.execute({"context_type": "active"})
        
        assert response.is_error
        assert "Error retrieving memory context" in response.content[0]["text"]


class TestLogDecisionToolHandler:
    """Test log decision tool handler."""
    
    @pytest.fixture
    def mock_context(self):
        """Create mock MCP context."""
        context = Mock(spec=MCPContext)
        context.memory_bank = AsyncMock()
        return context
    
    @pytest.mark.asyncio
    async def test_log_decision_success(self, mock_context):
        """Test successful decision logging."""
        handler = LogDecisionToolHandler(mock_context)
        response = await handler.execute({
            "decision": "Use JWT for authentication",
            "rationale": "Industry standard with good ecosystem support",
            "context": {"project": "test"}
        })
        
        assert not response.is_error
        assert "Successfully logged decision" in response.content[0]["text"]
        mock_context.memory_bank.log_decision.assert_called_once_with(
            "Use JWT for authentication",
            "Industry standard with good ecosystem support",
            {"project": "test"}
        )
    
    @pytest.mark.asyncio
    async def test_log_decision_missing_decision(self, mock_context):
        """Test decision logging with missing decision."""
        handler = LogDecisionToolHandler(mock_context)
        response = await handler.execute({
            "rationale": "Test rationale"
        })
        
        assert response.is_error
        assert "decision and rationale are required" in response.content[0]["text"]
    
    @pytest.mark.asyncio
    async def test_log_decision_missing_rationale(self, mock_context):
        """Test decision logging with missing rationale."""
        handler = LogDecisionToolHandler(mock_context)
        response = await handler.execute({
            "decision": "Test decision"
        })
        
        assert response.is_error
        assert "decision and rationale are required" in response.content[0]["text"]
    
    @pytest.mark.asyncio
    async def test_log_decision_error(self, mock_context):
        """Test decision logging error handling."""
        mock_context.memory_bank.log_decision.side_effect = Exception("Test error")
        
        handler = LogDecisionToolHandler(mock_context)
        response = await handler.execute({
            "decision": "Test decision",
            "rationale": "Test rationale"
        })
        
        assert response.is_error
        assert "Error logging decision" in response.content[0]["text"]


class TestFrameworkResourceProvider:
    """Test framework resource provider."""
    
    @pytest.fixture
    def mock_context(self):
        """Create mock MCP context."""
        context = Mock(spec=MCPContext)
        context.framework = AsyncMock()
        context.protocol_executor = AsyncMock()
        context.workspace_path = Path("/test/workspace")
        return context
    
    @pytest.mark.asyncio
    async def test_list_resources_success(self, mock_context):
        """Test successful resource listing."""
        mock_context.framework.get_all_principles.return_value = {
            "Core Philosophy": "Test principle"
        }
        mock_context.protocol_executor.list_protocols.return_value = {
            "Test Protocol": {"name": "Test Protocol"}
        }
        
        provider = FrameworkResourceProvider(mock_context)
        resources = await provider.list_resources()
        
        assert len(resources) >= 1  # At least constitution
        constitution_resource = next(r for r in resources if r.uri == "framework://constitution")
        assert constitution_resource.name == "AI Agent Constitution"
        assert constitution_resource.mime_type == "text/markdown"
    
    @pytest.mark.asyncio
    async def test_get_resource_constitution(self, mock_context):
        """Test constitution resource retrieval."""
        mock_context.framework.get_constitution.return_value = "Test Constitution"
        
        provider = FrameworkResourceProvider(mock_context)
        content = await provider.get_resource("framework://constitution")
        
        assert content is not None
        assert content.uri == "framework://constitution"
        assert content.mime_type == "text/markdown"
        assert content.text == "Test Constitution"
    
    @pytest.mark.asyncio
    async def test_get_resource_principle(self, mock_context):
        """Test principle resource retrieval."""
        mock_context.framework.get_principle.return_value = "Test Principle Content"
        
        provider = FrameworkResourceProvider(mock_context)
        content = await provider.get_resource("framework://principles/core_philosophy")
        
        assert content is not None
        assert content.uri == "framework://principles/core_philosophy"
        assert content.mime_type == "text/markdown"
        assert content.text == "Test Principle Content"
    
    @pytest.mark.asyncio
    async def test_get_resource_unknown(self, mock_context):
        """Test unknown resource retrieval."""
        provider = FrameworkResourceProvider(mock_context)
        content = await provider.get_resource("framework://unknown/resource")
        
        assert content is None


class TestMCPServer:
    """Test MCP server functionality."""
    
    @pytest.fixture
    def mock_context(self):
        """Create mock MCP context."""
        context = Mock(spec=MCPContext)
        context.framework = AsyncMock()
        context.memory_bank = AsyncMock()
        context.protocol_executor = AsyncMock()
        context.workspace_path = Path("/test/workspace")
        return context
    
    @pytest.fixture
    def mcp_server(self, mock_context):
        """Create MCP server instance."""
        return MCPServer(mock_context)
    
    @pytest.mark.asyncio
    async def test_server_initialization(self, mcp_server):
        """Test MCP server initialization."""
        await mcp_server.initialize()
        
        assert mcp_server._initialized
        assert len(mcp_server.tools) == 5
        assert "get_constitution" in mcp_server.tools
        assert "list_protocols" in mcp_server.tools
        assert "execute_protocol" in mcp_server.tools
        assert "get_memory_context" in mcp_server.tools
        assert "log_decision" in mcp_server.tools
        assert len(mcp_server.resource_providers) == 1
    
    def test_list_tools(self, mcp_server):
        """Test tool listing."""
        tools = mcp_server.list_tools()
        
        assert len(tools) == 5
        tool_names = [tool.name for tool in tools]
        assert "get_constitution" in tool_names
        assert "list_protocols" in tool_names
        assert "execute_protocol" in tool_names
        assert "get_memory_context" in tool_names
        assert "log_decision" in tool_names
    
    @pytest.mark.asyncio
    async def test_call_tool_success(self, mcp_server, mock_context):
        """Test successful tool call."""
        mock_context.framework.get_constitution.return_value = "Test Constitution"
        
        await mcp_server.initialize()
        response = await mcp_server.call_tool("get_constitution", {})
        
        assert not response.is_error
        assert len(response.content) == 1
        assert response.content[0]["text"] == "Test Constitution"
    
    @pytest.mark.asyncio
    async def test_call_tool_unknown(self, mcp_server):
        """Test unknown tool call."""
        await mcp_server.initialize()
        response = await mcp_server.call_tool("unknown_tool", {})
        
        assert response.is_error
        assert "Unknown tool" in response.content[0]["text"]
    
    @pytest.mark.asyncio
    async def test_call_tool_error(self, mcp_server, mock_context):
        """Test tool call error handling."""
        mock_context.framework.get_constitution.side_effect = Exception("Test error")
        
        await mcp_server.initialize()
        response = await mcp_server.call_tool("get_constitution", {})
        
        assert response.is_error
        assert "Error retrieving constitution" in response.content[0]["text"]
    
    @pytest.mark.asyncio
    async def test_list_resources(self, mcp_server, mock_context):
        """Test resource listing."""
        mock_context.framework.get_all_principles.return_value = {}
        mock_context.protocol_executor.list_protocols.return_value = {}
        
        await mcp_server.initialize()
        resources = await mcp_server.list_resources()
        
        assert len(resources) >= 1  # At least constitution
        constitution_resource = next(r for r in resources if r.uri == "framework://constitution")
        assert constitution_resource.name == "AI Agent Constitution"
    
    @pytest.mark.asyncio
    async def test_read_resource(self, mcp_server, mock_context):
        """Test resource reading."""
        mock_context.framework.get_constitution.return_value = "Test Constitution"
        
        await mcp_server.initialize()
        content = await mcp_server.read_resource("framework://constitution")
        
        assert content is not None
        assert content.text == "Test Constitution"
    
    @pytest.mark.asyncio
    async def test_read_resource_not_found(self, mcp_server):
        """Test reading non-existent resource."""
        await mcp_server.initialize()
        content = await mcp_server.read_resource("framework://unknown/resource")
        
        assert content is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
