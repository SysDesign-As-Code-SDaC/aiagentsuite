"""
Tests for AI Agent Suite Framework Manager
"""

import pytest
import asyncio
from pathlib import Path
from unittest.mock import patch, mock_open

from aiagentsuite.framework.manager import FrameworkManager


class TestFrameworkManager:
    """Test cases for FrameworkManager."""

    @pytest.fixture
    def workspace_path(self, tmp_path):
        """Create a temporary workspace path."""
        return tmp_path

    @pytest.fixture
    def framework_manager(self, workspace_path):
        """Create a FrameworkManager instance."""
        return FrameworkManager(workspace_path)

    def test_initialization(self, framework_manager):
        """Test that FrameworkManager initializes correctly."""
        assert framework_manager._constitution is None
        assert framework_manager._principles == {}
        assert framework_manager._project_context is None

    @pytest.mark.asyncio
    async def test_load_constitution_success(self, framework_manager, workspace_path):
        """Test successful constitution loading."""
        constitution_content = "# Master Constitution\n\nTest content"
        constitution_file = workspace_path / "MASTER AI AGENT CONSTITUTION.md"
        constitution_file.write_text(constitution_content)

        await framework_manager._load_constitution()

        assert framework_manager._constitution == constitution_content

    @pytest.mark.asyncio
    async def test_load_constitution_missing_file(self, framework_manager):
        """Test constitution loading when file doesn't exist."""
        await framework_manager._load_constitution()

        assert framework_manager._constitution is None

    @pytest.mark.asyncio
    async def test_get_constitution_with_cache(self, framework_manager):
        """Test getting constitution from cache."""
        expected_content = "Cached constitution"
        framework_manager._constitution = expected_content

        result = await framework_manager.get_constitution()

        assert result == expected_content

    @pytest.mark.asyncio
    async def test_get_constitution_without_cache(self, framework_manager, workspace_path):
        """Test getting constitution by loading from file."""
        constitution_content = "Loaded constitution"
        constitution_file = workspace_path / "MASTER AI AGENT CONSTITUTION.md"
        constitution_file.write_text(constitution_content)

        result = await framework_manager.get_constitution()

        assert result == constitution_content

    @pytest.mark.asyncio
    async def test_load_principles(self, framework_manager, workspace_path):
        """Test loading VDE principles."""
        principle_files = {
            "Principle 1_ The VDE Core Philosophy.md": "Core philosophy content",
            "Principle 2_ Branching and Commit Strategy.md": "Branching strategy content",
            "Principle 3_ YAGNI (You Ain't Gonna Need It).md": "YAGNI content"
        }

        for filename, content in principle_files.items():
            principle_file = workspace_path / filename
            principle_file.write_text(content)

        await framework_manager._load_principles()

        assert len(framework_manager._principles) == 3

    @pytest.mark.asyncio
    async def test_get_principle(self, framework_manager):
        """Test getting a specific principle."""
        principles = {
            "Core Philosophy": "Philosophy content",
            "Branching Strategy": "Strategy content"
        }
        framework_manager._principles = principles

        result = await framework_manager.get_principle("Core Philosophy")
        assert result == "Philosophy content"

    @pytest.mark.asyncio
    async def test_get_all_principles(self, framework_manager):
        """Test getting all principles."""
        principles = {"Principle 1": "Content 1", "Principle 2": "Content 2"}
        framework_manager._principles = principles

        result = await framework_manager.get_all_principles()
        assert result == principles

    @pytest.mark.asyncio
    async def test_load_project_context(self, framework_manager, workspace_path):
        """Test loading project context."""
        context_content = "# Project Context\n\nTest context"
        context_file = workspace_path / "Project Context.md"
        context_file.write_text(context_content)

        await framework_manager._load_project_context()

        assert framework_manager._project_context == context_content

    @pytest.mark.asyncio
    async def test_get_project_context(self, framework_manager, workspace_path):
        """Test getting project context."""
        context_content = "Project context content"
        context_file = workspace_path / "Project Context.md"
        context_file.write_text(context_content)

        result = await framework_manager.get_project_context()

        assert result == context_content

        result = framework_manager.get_constitution()

        assert result == expected_content

    @pytest.mark.asyncio
    async def test_get_constitution_without_cache(self, framework_manager, workspace_path):
        """Test getting constitution by loading from file."""
        constitution_content = "Loaded constitution"
        constitution_file = workspace_path / "MASTER AI AGENT CONSTITUTION.md"
        constitution_file.write_text(constitution_content)

        result = await framework_manager.get_constitution()

        assert result == constitution_content
        assert framework_manager._constitution == constitution_content

    @pytest.mark.asyncio
    async def test_load_principles(self, framework_manager, workspace_path):
        """Test loading VDE principles."""
        principle_files = {
            "Principle 1_ The VDE Core Philosophy.md": "Core philosophy content",
            "Principle 2_ Branching and Commit Strategy.md": "Branching strategy content",
            "Principle 3_ YAGNI (You Ain't Gonna Need It).md": "YAGNI content"
        }

        for filename, content in principle_files.items():
            principle_file = workspace_path / filename
            principle_file.write_text(content)

        await framework_manager._load_principles()

        assert len(framework_manager._principles) == 3
        assert "Core Philosophy" in framework_manager._principles
        assert "Branching Strategy" in framework_manager._principles
        assert "YAGNI" in framework_manager._principles

    @pytest.mark.asyncio
    async def test_get_principle(self, framework_manager):
        """Test getting a specific principle."""
        principles = {
            "Core Philosophy": "Philosophy content",
            "Branching Strategy": "Strategy content"
        }
        framework_manager._principles = principles

        result = await framework_manager.get_principle("Core Philosophy")
        assert result == "Philosophy content"

        result = await framework_manager.get_principle("Nonexistent Principle")
        assert result == "Principle 'Nonexistent Principle' not found"

    @pytest.mark.asyncio
    async def test_get_all_principles(self, framework_manager):
        """Test getting all principles."""
        principles = {"Principle 1": "Content 1", "Principle 2": "Content 2"}
        framework_manager._principles = principles

        result = await framework_manager.get_all_principles()
        assert result == principles

    @pytest.mark.asyncio
    async def test_load_project_context(self, framework_manager, workspace_path):
        """Test loading project context."""
        context_content = "# Project Context\n\nTest context"
        context_file = workspace_path / "Project Context.md"
        context_file.write_text(context_content)

        await framework_manager._load_project_context()

        assert framework_manager._project_context == context_content

    @pytest.mark.asyncio
    async def test_get_project_context(self, framework_manager, workspace_path):
        """Test getting project context."""
        context_content = "Project context content"
        context_file = workspace_path / "Project Context.md"
        context_file.write_text(context_content)

        result = await framework_manager.get_project_context()

        assert result == context_content
        assert framework_manager._project_context == context_content