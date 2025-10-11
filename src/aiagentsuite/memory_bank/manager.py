"""
Memory Bank Manager - Handles persistent context and decision logging
"""

import asyncio
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class MemoryBank:
    """
    Manages persistent memory for context, decisions, and progress tracking.
    """

    def __init__(self, workspace_path: Path):
        self.workspace_path = workspace_path
        self.memory_dir = workspace_path / "memory-bank"
        self.memory_dir.mkdir(exist_ok=True)

        # Memory file paths
        self.active_context_file = self.memory_dir / "activeContext.md"
        self.decision_log_file = self.memory_dir / "decisionLog.md"
        self.product_context_file = self.memory_dir / "productContext.md"
        self.progress_file = self.memory_dir / "progress.md"
        self.project_brief_file = self.memory_dir / "projectBrief.md"
        self.system_patterns_file = self.memory_dir / "systemPatterns.md"

    async def initialize(self) -> None:
        """Initialize memory bank by ensuring all memory files exist."""
        memory_files = [
            self.active_context_file,
            self.decision_log_file,
            self.product_context_file,
            self.progress_file,
            self.project_brief_file,
            self.system_patterns_file
        ]

        for memory_file in memory_files:
            if not memory_file.exists():
                await self._create_default_memory_file(memory_file)

        logger.info("Memory bank initialized")

    async def _create_default_memory_file(self, file_path: Path) -> None:
        """Create a default memory file with basic structure."""
        filename = file_path.stem

        defaults = {
            "activeContext": "# Active Context\n\n## Current Goals\n\n- Goal 1\n\n## Current Blockers\n\n- None yet",
            "decisionLog": "# Decision Log\n\n## Architectural Decisions\n\n### Decision 1\n- **Date**: TBD\n- **Decision**: TBD\n- **Rationale**: TBD\n- **Context**: TBD",
            "productContext": "# Product Context\n\n## Overview\n\nTBD",
            "progress": "# Progress\n\n## Completed Tasks\n\n- None yet\n\n## Current Tasks\n\n- None yet\n\n## Upcoming Tasks\n\n- None yet",
            "projectBrief": "# Project Brief\n\n## Objective\n\nTBD\n\n## Scope\n\nTBD\n\n## Timeline\n\nTBD",
            "systemPatterns": "# System Patterns\n\n## Architectural Patterns\n\nTBD\n\n## Design Patterns\n\nTBD"
        }

        default_content = defaults.get(filename, f"# {filename.title()}\n\nTBD")
        file_path.write_text(default_content, encoding='utf-8')
        logger.debug(f"Created default memory file: {file_path}")

    async def get_context(self, context_type: str) -> Dict[str, Any]:
        """Get memory context of specified type."""
        context_map = {
            "active": self.active_context_file,
            "decisions": self.decision_log_file,
            "product": self.product_context_file,
            "progress": self.progress_file,
            "project": self.project_brief_file,
            "patterns": self.system_patterns_file
        }

        if context_type not in context_map:
            raise ValueError(f"Unknown context type: {context_type}")

        file_path = context_map[context_type]
        if not file_path.exists():
            await self._create_default_memory_file(file_path)

        content = file_path.read_text(encoding='utf-8')
        return {
            "type": context_type,
            "content": content,
            "last_modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
        }

    async def update_context(self, context_type: str, data: Dict[str, Any]) -> None:
        """Update memory context."""
        context_map = {
            "active": self.active_context_file,
            "decisions": self.decision_log_file,
            "product": self.product_context_file,
            "progress": self.progress_file,
            "project": self.project_brief_file,
            "patterns": self.system_patterns_file
        }

        if context_type not in context_map:
            raise ValueError(f"Unknown context type: {context_type}")

        file_path = context_map[context_type]

        if "content" in data:
            # Direct content update
            file_path.write_text(data["content"], encoding='utf-8')
        elif "append" in data:
            # Append to existing content
            existing_content = file_path.read_text(encoding='utf-8') if file_path.exists() else ""
            new_content = existing_content + "\n\n" + data["append"]
            file_path.write_text(new_content, encoding='utf-8')

        logger.info(f"Updated {context_type} context")

    async def log_decision(self, decision: str, rationale: str, context: Dict[str, Any]) -> None:
        """Log an architectural or implementation decision."""
        timestamp = datetime.now().isoformat()

        decision_entry = f"""### {decision}
- **Date**: {timestamp}
- **Decision**: {decision}
- **Rationale**: {rationale}
- **Context**: {json.dumps(context, indent=2)}
"""

        await self.update_context("decisions", {"append": decision_entry})
        logger.info(f"Logged decision: {decision}")

    async def get_all_contexts(self) -> Dict[str, Dict[str, Any]]:
        """Get all memory contexts."""
        context_types = ["active", "decisions", "product", "progress", "project", "patterns"]
        contexts = {}

        for context_type in context_types:
            contexts[context_type] = await self.get_context(context_type)

        return contexts