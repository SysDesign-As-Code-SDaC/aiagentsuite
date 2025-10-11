"""
AI Agent Suite MCP Extension Components

Provides Model Context Protocol (MCP) server tools for programmatic framework access.
Implements the bridge between MCP clients and Python framework components.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass
import asyncio
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class MCPTool:
    """Represents an MCP tool definition."""
    name: str
    description: str
    input_schema: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": self.input_schema
        }


@dataclass
class MCPResponse:
    """Represents an MCP tool response."""
    content: List[Dict[str, Any]]
    is_error: bool = False

    def to_dict(self) -> Dict[str, Any]:
        result = {"content": self.content}
        if self.is_error:
            result["isError"] = True
        return result


@dataclass
class MCPResource:
    """Represents an MCP resource."""
    uri: str
    name: str
    description: str
    mime_type: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "uri": self.uri,
            "name": self.name,
            "description": self.description,
            "mimeType": self.mime_type
        }


@dataclass
class MCPResourceContent:
    """Represents MCP resource content."""
    uri: str
    mime_type: str
    text: Optional[str] = None
    blob: Optional[bytes] = None

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "uri": self.uri,
            "mimeType": self.mime_type
        }
        if self.text is not None:
            result["text"] = self.text
        if self.blob is not None:
            result["blob"] = self.blob.hex()
        return result


class MCPContext:
    """Context information for MCP operations."""

    def __init__(
        self,
        workspace_path: Path,
        framework_manager: Any,  # Forward reference to avoid circular imports
        memory_bank: Any,  # Forward reference to avoid circular imports
        protocol_executor: Any  # Forward reference to avoid circular imports
    ):
        self.workspace_path = workspace_path
        self.framework = framework_manager
        self.memory_bank = memory_bank
        self.protocol_executor = protocol_executor


class MCPToolHandler(ABC):
    """Abstract base class for MCP tool handlers."""

    def __init__(self, context: MCPContext):
        self.context = context

    @abstractmethod
    async def execute(self, arguments: Dict[str, Any]) -> MCPResponse:
        """Execute the tool with given arguments."""
        pass


class ConstitutionToolHandler(MCPToolHandler):
    """Handles the get_constitution tool."""

    async def execute(self, arguments: Dict[str, Any]) -> MCPResponse:
        """Get the master AI agent constitution."""
        try:
            constitution = await self.context.framework.get_constitution()
            return MCPResponse(content=[
                {
                    "type": "text",
                    "text": constitution
                }
            ])
        except Exception as e:
            logger.error(f"Failed to get constitution: {e}")
            return MCPResponse(
                content=[{
                    "type": "text",
                    "text": f"Error retrieving constitution: {str(e)}"
                }],
                is_error=True
            )


class ListProtocolsToolHandler(MCPToolHandler):
    """Handles the list_protocols tool."""

    async def execute(self, arguments: Dict[str, Any]) -> MCPResponse:
        """List all available protocols."""
        try:
            protocols = await self.context.protocol_executor.list_protocols()
            return MCPResponse(content=[
                {
                    "type": "text",
                    "text": f"Available protocols: {', '.join(protocols.keys())}"
                },
                {
                    "type": "json",
                    "json": protocols
                }
            ])
        except Exception as e:
            logger.error(f"Failed to list protocols: {e}")
            return MCPResponse(
                content=[{
                    "type": "text",
                    "text": f"Error listing protocols: {str(e)}"
                }],
                is_error=True
            )


class ExecuteProtocolToolHandler(MCPToolHandler):
    """Handles the execute_protocol tool."""

    async def execute(self, arguments: Dict[str, Any]) -> MCPResponse:
        """Execute a specific protocol with context."""
        try:
            protocol_name = arguments.get("protocol_name")
            if not protocol_name:
                return MCPResponse(
                    content=[{
                        "type": "text",
                        "text": "Error: protocol_name is required"
                    }],
                    is_error=True
                )

            context = arguments.get("context", {})
            result = await self.context.protocol_executor.execute_protocol(
                protocol_name, context
            )

            return MCPResponse(content=[
                {
                    "type": "text",
                    "text": f"Successfully executed protocol: {protocol_name}"
                },
                {
                    "type": "json",
                    "json": result
                }
            ])
        except Exception as e:
            logger.error(f"Failed to execute protocol: {e}")
            return MCPResponse(
                content=[{
                    "type": "text",
                    "text": f"Error executing protocol: {str(e)}"
                }],
                is_error=True
            )


class MemoryContextToolHandler(MCPToolHandler):
    """Handles the get_memory_context tool."""

    async def execute(self, arguments: Dict[str, Any]) -> MCPResponse:
        """Get memory bank context of specified type."""
        try:
            context_type = arguments.get("context_type")
            if not context_type:
                return MCPResponse(
                    content=[{
                        "type": "text",
                        "text": "Error: context_type is required"
                    }],
                    is_error=True
                )

            valid_types = ["active", "decisions", "product", "progress", "project", "patterns"]
            if context_type not in valid_types:
                return MCPResponse(
                    content=[{
                        "type": "text",
                        "text": f"Error: context_type must be one of: {', '.join(valid_types)}"
                    }],
                    is_error=True
                )

            context_data = await self.context.memory_bank.get_context(context_type)

            return MCPResponse(content=[
                {
                    "type": "text",
                    "text": f"Retrieved {context_type} context"
                },
                {
                    "type": "json",
                    "json": context_data
                }
            ])
        except Exception as e:
            logger.error(f"Failed to get memory context: {e}")
            return MCPResponse(
                content=[{
                    "type": "text",
                    "text": f"Error retrieving memory context: {str(e)}"
                }],
                is_error=True
            )


class LogDecisionToolHandler(MCPToolHandler):
    """Handles the log_decision tool."""

    async def execute(self, arguments: Dict[str, Any]) -> MCPResponse:
        """Log an architectural or implementation decision."""
        try:
            decision = arguments.get("decision")
            rationale = arguments.get("rationale")
            context = arguments.get("context", {})

            if not decision or not rationale:
                return MCPResponse(
                    content=[{
                        "type": "text",
                        "text": "Error: decision and rationale are required"
                    }],
                    is_error=True
                )

            await self.context.memory_bank.log_decision(decision, rationale, context)

            return MCPResponse(content=[
                {
                    "type": "text",
                    "text": f"Successfully logged decision: {decision}"
                }
            ])
        except Exception as e:
            logger.error(f"Failed to log decision: {e}")
            return MCPResponse(
                content=[{
                    "type": "text",
                    "text": f"Error logging decision: {str(e)}"
                }],
                is_error=True
            )


class MCPResourceProvider(ABC):
    """Abstract base class for MCP resource providers."""

    def __init__(self, context: MCPContext):
        self.context = context

    @abstractmethod
    async def list_resources(self) -> List[MCPResource]:
        """List available resources."""
        pass

    @abstractmethod
    async def get_resource(self, uri: str) -> Optional[MCPResourceContent]:
        """Get resource content by URI."""
        pass


class FrameworkResourceProvider(MCPResourceProvider):
    """Provides framework-related resources."""

    async def list_resources(self) -> List[MCPResource]:
        """List framework-related resources."""
        resources = []

        # Constitution resource
        resources.append(MCPResource(
            uri="framework://constitution",
            name="AI Agent Constitution",
            description="Master AI agent constitution document",
            mime_type="text/markdown"
        ))

        # Principles resources
        try:
            principles = await self.context.framework.get_all_principles()
            for name in principles.keys():
                resources.append(MCPResource(
                    uri=f"framework://principles/{name.lower().replace(' ', '_')}",
                    name=f"Principle: {name}",
                    description=f"VDE principle: {name}",
                    mime_type="text/markdown"
                ))
        except Exception as e:
            logger.warning(f"Failed to get principles for resources: {e}")

        # Protocol resources
        try:
            protocols = await self.context.protocol_executor.list_protocols()
            for name in protocols.keys():
                resources.append(MCPResource(
                    uri=f"framework://protocols/{name.lower().replace(' ', '_')}",
                    name=f"Protocol: {name}",
                    description=f"VDE protocol: {name}",
                    mime_type="text/markdown"
                ))
        except Exception as e:
            logger.warning(f"Failed to get protocols for resources: {e}")

        return resources

    async def get_resource(self, uri: str) -> Optional[MCPResourceContent]:
        """Get framework resource content."""
        try:
            if uri == "framework://constitution":
                constitution = await self.context.framework.get_constitution()
                return MCPResourceContent(
                    uri=uri,
                    mime_type="text/markdown",
                    text=constitution
                )

            elif uri.startswith("framework://principles/"):
                principle_name = uri.split("/")[-1].replace("_", " ").title()
                content = await self.context.framework.get_principle(principle_name)
                return MCPResourceContent(
                    uri=uri,
                    mime_type="text/markdown",
                    text=content
                )

            elif uri.startswith("framework://protocols/"):
                protocol_name = uri.split("/")[-1].replace("_", " ").title()
                # Load protocol content from file system
                protocols_path = self.context.workspace_path / "protocols" / "data"
                protocol_file = None

                # Find matching protocol file
                for file_path in protocols_path.glob("*.md"):
                    if protocol_name.lower() in file_path.name.lower():
                        protocol_file = file_path
                        break

                if protocol_file and protocol_file.exists():
                    content = protocol_file.read_text()
                    return MCPResourceContent(
                        uri=uri,
                        mime_type="text/markdown",
                        text=content
                    )

            return None

        except Exception as e:
            logger.error(f"Failed to get resource {uri}: {e}")
            return None


class MCPServer:
    """AI Agent Suite MCP Server implementation."""

    def __init__(self, context: MCPContext):
        self.context = context
        self.tools: Dict[str, MCPToolHandler] = {}
        self.resource_providers: List[MCPResourceProvider] = []
        self._initialized = False

    async def initialize(self) -> None:
        """Initialize the MCP server."""
        if self._initialized:
            return

        # Register tool handlers
        self.tools["get_constitution"] = ConstitutionToolHandler(self.context)
        self.tools["list_protocols"] = ListProtocolsToolHandler(self.context)
        self.tools["execute_protocol"] = ExecuteProtocolToolHandler(self.context)
        self.tools["get_memory_context"] = MemoryContextToolHandler(self.context)
        self.tools["log_decision"] = LogDecisionToolHandler(self.context)

        # Register resource providers
        self.resource_providers.append(FrameworkResourceProvider(self.context))

        self._initialized = True
        logger.info("MCP Server initialized")

    def list_tools(self) -> List[MCPTool]:
        """List available MCP tools."""
        return [
            MCPTool(
                name="get_constitution",
                description="Get the master AI agent constitution",
                input_schema={"type": "object", "properties": {}}
            ),
            MCPTool(
                name="list_protocols",
                description="List all available protocols",
                input_schema={"type": "object", "properties": {}}
            ),
            MCPTool(
                name="execute_protocol",
                description="Execute a specific protocol with context",
                input_schema={
                    "type": "object",
                    "properties": {
                        "protocol_name": {"type": "string"},
                        "context": {"type": "object"}
                    },
                    "required": ["protocol_name"]
                }
            ),
            MCPTool(
                name="get_memory_context",
                description="Get memory bank context",
                input_schema={
                    "type": "object",
                    "properties": {
                        "context_type": {
                            "type": "string",
                            "enum": ["active", "decisions", "product", "progress", "project", "patterns"]
                        }
                    },
                    "required": ["context_type"]
                }
            ),
            MCPTool(
                name="log_decision",
                description="Log an architectural decision",
                input_schema={
                    "type": "object",
                    "properties": {
                        "decision": {"type": "string"},
                        "rationale": {"type": "string"},
                        "context": {"type": "object"}
                    },
                    "required": ["decision", "rationale"]
                }
            )
        ]

    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> MCPResponse:
        """Call an MCP tool by name."""
        if not self._initialized:
            await self.initialize()

        handler = self.tools.get(name)
        if not handler:
            return MCPResponse(
                content=[{
                    "type": "text",
                    "text": f"Unknown tool: {name}"
                }],
                is_error=True
            )

        try:
            return await handler.execute(arguments)
        except Exception as e:
            logger.error(f"Tool execution failed for {name}: {e}")
            return MCPResponse(
                content=[{
                    "type": "text",
                    "text": f"Tool execution failed: {str(e)}"
                }],
                is_error=True
            )

    async def list_resources(self) -> List[MCPResource]:
        """List all available resources."""
        if not self._initialized:
            await self.initialize()

        all_resources = []
        for provider in self.resource_providers:
            try:
                resources = await provider.list_resources()
                all_resources.extend(resources)
            except Exception as e:
                logger.warning(f"Failed to get resources from provider: {e}")

        return all_resources

    async def read_resource(self, uri: str) -> Optional[MCPResourceContent]:
        """Read resource content by URI."""
        if not self._initialized:
            await self.initialize()

        for provider in self.resource_providers:
            try:
                content = await provider.get_resource(uri)
                if content:
                    return content
            except Exception as e:
                logger.warning(f"Failed to read resource from provider: {e}")

        return None


__all__ = [
    "MCPTool",
    "MCPResponse",
    "MCPResource",
    "MCPResourceContent",
    "MCPContext",
    "MCPToolHandler",
    "ConstitutionToolHandler",
    "ListProtocolsToolHandler",
    "ExecuteProtocolToolHandler",
    "MemoryContextToolHandler",
    "LogDecisionToolHandler",
    "MCPResourceProvider",
    "FrameworkResourceProvider",
    "MCPServer"
]
