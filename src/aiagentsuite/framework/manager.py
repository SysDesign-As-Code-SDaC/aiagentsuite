"""
Framework Manager - Handles framework components and constitution
"""

import asyncio
from pathlib import Path
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class FrameworkManager:
    """
    Manages framework components including constitution, principles, and project context.
    """

    def __init__(self, workspace_path: Path):
        self.workspace_path = workspace_path
        self._constitution: Optional[str] = None
        self._principles: Dict[str, str] = {}
        self._project_context: Optional[str] = None

    async def initialize(self) -> None:
        """Initialize framework components by loading all documents."""
        await asyncio.gather(
            self._load_constitution(),
            self._load_principles(),
            self._load_project_context()
        )
        logger.info("Framework components loaded")

    async def _load_constitution(self) -> None:
        """Load the master AI agent constitution."""
        constitution_path = self.workspace_path / "MASTER AI AGENT CONSTITUTION.md"
        if constitution_path.exists():
            self._constitution = constitution_path.read_text(encoding='utf-8')
            logger.debug("Constitution loaded")
        else:
            logger.warning(f"Constitution not found at {constitution_path}")

    async def _load_principles(self) -> None:
        """Load all VDE principles."""
        principles_dir = self.workspace_path
        principle_files = [
            "Principle 1_ The VDE Core Philosophy.md",
            "Principle 2_ Branching and Commit Strategy.md",
            "Principle 3_ YAGNI (You Ain't Gonna Need It).md"
        ]

        for principle_file in principle_files:
            principle_path = principles_dir / principle_file
            if principle_path.exists():
                # Extract principle name from filename
                if "Core Philosophy" in principle_file:
                    principle_name = "Core Philosophy"
                elif "Branching and Commit Strategy" in principle_file:
                    principle_name = "Branching Strategy"
                elif "YAGNI" in principle_file:
                    principle_name = "YAGNI"
                else:
                    principle_name = principle_file.split("_")[0] + " " + principle_file.split("_")[1].split()[0]

                self._principles[principle_name] = principle_path.read_text(encoding='utf-8')
                logger.debug(f"Principle loaded: {principle_name}")

    async def _load_project_context(self) -> None:
        """Load project context."""
        context_path = self.workspace_path / "Project Context.md"
        if context_path.exists():
            self._project_context = context_path.read_text(encoding='utf-8')
            logger.debug("Project context loaded")
        else:
            logger.warning(f"Project context not found at {context_path}")

    async def get_constitution(self) -> str:
        """Get the master AI agent constitution."""
        if self._constitution is None:
            await self._load_constitution()
        return self._constitution or "Constitution not available"

    async def get_principle(self, principle_name: str) -> str:
        """Get a specific VDE principle."""
        if not self._principles:
            await self._load_principles()
        return self._principles.get(principle_name, f"Principle '{principle_name}' not found")

    async def get_all_principles(self) -> Dict[str, str]:
        """Get all VDE principles."""
        if not self._principles:
            await self._load_principles()
        return self._principles

    async def get_project_context(self) -> str:
        """Get project context."""
        if self._project_context is None:
            await self._load_project_context()
        return self._project_context or "Project context not available"