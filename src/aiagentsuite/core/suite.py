"""
AI Agent Suite Core Implementation
"""

from typing import Dict, Any, Optional
from pathlib import Path
import logging

from ..framework.manager import FrameworkManager
from ..protocols.executor import ProtocolExecutor
from ..memory_bank.manager import MemoryBank

logger = logging.getLogger(__name__)


class AIAgentSuite:
    """
    Main AI Agent Suite class providing unified access to all framework components.
    """

    def __init__(self, workspace_path: Optional[str] = None):
        """
        Initialize the AI Agent Suite.

        Args:
            workspace_path: Path to the workspace containing framework files.
                           Defaults to current directory.
        """
        self.workspace_path = Path(workspace_path or ".")
        self.framework = FrameworkManager(self.workspace_path)
        self.protocols = ProtocolExecutor(self.workspace_path)
        self.memory_bank = MemoryBank(self.workspace_path)

        logger.info("AI Agent Suite initialized")

    async def initialize(self) -> None:
        """Initialize all framework components."""
        await self.framework.initialize()
        await self.memory_bank.initialize()
        logger.info("AI Agent Suite components initialized")

    async def get_constitution(self) -> str:
        """Get the master AI agent constitution."""
        return await self.framework.get_constitution()

    async def list_protocols(self) -> Dict[str, Any]:
        """List all available protocols."""
        return await self.protocols.list_protocols()

    async def execute_protocol(self, protocol_name: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a specific protocol with given context."""
        return await self.protocols.execute_protocol(protocol_name, context)

    async def get_memory_context(self, context_type: str) -> Dict[str, Any]:
        """Get memory bank context of specified type."""
        return await self.memory_bank.get_context(context_type)

    async def update_memory_context(self, context_type: str, data: Dict[str, Any]) -> None:
        """Update memory bank context."""
        await self.memory_bank.update_context(context_type, data)

    async def log_decision(self, decision: str, rationale: str, context: Dict[str, Any]) -> None:
        """Log an architectural or implementation decision."""
        await self.memory_bank.log_decision(decision, rationale, context)