"""
Unit tests for Memory Bank functionality based on actual implementation.
"""

import pytest
import asyncio
from pathlib import Path
import tempfile

from aiagentsuite.memory_bank.manager import MemoryBank


class TestMemoryBank:
    """Test memory bank functionality."""
    
    @pytest.fixture
    def temp_workspace(self):
        """Create temporary workspace for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace_path = Path(temp_dir)
            yield workspace_path
    
    @pytest.fixture
    def memory_bank(self, temp_workspace):
        """Create memory bank with temporary workspace."""
        return MemoryBank(temp_workspace)
    
    @pytest.mark.asyncio
    async def test_initialization(self, memory_bank):
        """Test memory bank initialization."""
        await memory_bank.initialize()
        
        assert memory_bank.workspace_path is not None
        assert memory_bank.memory_dir.exists()
        assert memory_bank.active_context_file.exists()
        assert memory_bank.decision_log_file.exists()
        assert memory_bank.product_context_file.exists()
        assert memory_bank.progress_file.exists()
        assert memory_bank.project_brief_file.exists()
        assert memory_bank.system_patterns_file.exists()
    
    @pytest.mark.asyncio
    async def test_get_context_active(self, memory_bank):
        """Test getting active context."""
        await memory_bank.initialize()
        
        context = await memory_bank.get_context("active")
        
        assert context is not None
        assert isinstance(context, dict)
        assert "content" in context
        assert "last_modified" in context
    
    @pytest.mark.asyncio
    async def test_get_context_product(self, memory_bank):
        """Test getting product context."""
        await memory_bank.initialize()
        
        context = await memory_bank.get_context("product")
        
        assert context is not None
        assert isinstance(context, dict)
        assert "content" in context
        assert "last_modified" in context
    
    @pytest.mark.asyncio
    async def test_get_context_progress(self, memory_bank):
        """Test getting progress context."""
        await memory_bank.initialize()
        
        context = await memory_bank.get_context("progress")
        
        assert context is not None
        assert isinstance(context, dict)
        assert "content" in context
        assert "last_modified" in context
    
    @pytest.mark.asyncio
    async def test_get_context_project_brief(self, memory_bank):
        """Test getting project brief context."""
        await memory_bank.initialize()
        
        context = await memory_bank.get_context("project")
        
        assert context is not None
        assert isinstance(context, dict)
        assert "content" in context
        assert "last_modified" in context
    
    @pytest.mark.asyncio
    async def test_get_context_system_patterns(self, memory_bank):
        """Test getting system patterns context."""
        await memory_bank.initialize()
        
        context = await memory_bank.get_context("patterns")
        
        assert context is not None
        assert isinstance(context, dict)
        assert "content" in context
        assert "last_modified" in context
    
    @pytest.mark.asyncio
    async def test_get_context_invalid_type(self, memory_bank):
        """Test getting context with invalid type."""
        await memory_bank.initialize()
        
        with pytest.raises(ValueError, match="Unknown context type"):
            await memory_bank.get_context("invalid_type")
    
    @pytest.mark.asyncio
    async def test_update_context_active(self, memory_bank):
        """Test updating active context."""
        await memory_bank.initialize()
        
        new_data = {
            "content": "Updated active context for testing"
        }
        
        await memory_bank.update_context("active", new_data)
        
        retrieved_context = await memory_bank.get_context("active")
        assert "Updated active context for testing" in retrieved_context["content"]
    
    @pytest.mark.asyncio
    async def test_update_context_product(self, memory_bank):
        """Test updating product context."""
        await memory_bank.initialize()
        
        new_data = {
            "content": "Updated product context"
        }
        
        await memory_bank.update_context("product", new_data)
        
        retrieved_context = await memory_bank.get_context("product")
        assert "Updated product context" in retrieved_context["content"]
    
    @pytest.mark.asyncio
    async def test_update_context_invalid_type(self, memory_bank):
        """Test updating context with invalid type."""
        await memory_bank.initialize()
        
        new_data = {"content": "Test content"}
        
        with pytest.raises(ValueError, match="Unknown context type"):
            await memory_bank.update_context("invalid_type", new_data)
    
    @pytest.mark.asyncio
    async def test_log_decision(self, memory_bank):
        """Test logging a decision."""
        await memory_bank.initialize()
        
        decision = "Use FastAPI for backend API"
        rationale = "FastAPI provides excellent performance and automatic documentation"
        context = {"project": "test", "component": "backend"}
        
        await memory_bank.log_decision(decision, rationale, context)
        
        # Verify the decision was logged by checking the file content
        decision_content = memory_bank.decision_log_file.read_text()
        assert decision in decision_content
        assert rationale in decision_content
        assert "project" in decision_content
        assert "backend" in decision_content
    
    @pytest.mark.asyncio
    async def test_log_multiple_decisions(self, memory_bank):
        """Test logging multiple decisions."""
        await memory_bank.initialize()
        
        # Log first decision
        await memory_bank.log_decision(
            "Use PostgreSQL for database",
            "ACID compliance required",
            {"project": "test", "component": "database"}
        )
        
        # Log second decision
        await memory_bank.log_decision(
            "Use Docker for containerization",
            "Consistent deployment across environments",
            {"project": "test", "component": "deployment"}
        )
        
        # Verify both decisions were logged
        decision_content = memory_bank.decision_log_file.read_text()
        assert "PostgreSQL" in decision_content
        assert "Docker" in decision_content
        assert "ACID compliance" in decision_content
        assert "Consistent deployment" in decision_content
    
    @pytest.mark.asyncio
    async def test_get_all_contexts(self, memory_bank):
        """Test getting all contexts."""
        await memory_bank.initialize()
        
        # Update some contexts first
        await memory_bank.update_context("active", {
            "content": "Test active context"
        })
        
        await memory_bank.update_context("product", {
            "content": "Test product context"
        })
        
        all_contexts = await memory_bank.get_all_contexts()
        
        assert isinstance(all_contexts, dict)
        assert "active" in all_contexts
        assert "product" in all_contexts
        assert "progress" in all_contexts
        assert "project" in all_contexts
        assert "patterns" in all_contexts
        
        # Verify updated contexts
        assert "Test active context" in all_contexts["active"]["content"]
        assert "Test product context" in all_contexts["product"]["content"]
    
    @pytest.mark.asyncio
    async def test_context_persistence(self, memory_bank):
        """Test that context changes persist across instances."""
        await memory_bank.initialize()
        
        # Update context
        await memory_bank.update_context("active", {
            "content": "Persistent test context"
        })
        
        # Create new memory bank instance
        new_memory_bank = MemoryBank(memory_bank.workspace_path)
        await new_memory_bank.initialize()
        
        # Verify persistence
        context = await new_memory_bank.get_context("active")
        assert "Persistent test context" in context["content"]
    
    @pytest.mark.asyncio
    async def test_decision_log_persistence(self, memory_bank):
        """Test that decision log persists across instances."""
        await memory_bank.initialize()
        
        # Log a decision
        await memory_bank.log_decision(
            "Persistent decision",
            "Persistent rationale",
            {"persistence": "test"}
        )
        
        # Create new memory bank instance
        new_memory_bank = MemoryBank(memory_bank.workspace_path)
        await new_memory_bank.initialize()
        
        # Verify persistence
        decision_content = new_memory_bank.decision_log_file.read_text()
        assert "Persistent decision" in decision_content
        assert "Persistent rationale" in decision_content
        assert "persistence" in decision_content
    
    @pytest.mark.asyncio
    async def test_memory_file_creation(self, memory_bank):
        """Test that memory files are created with default content."""
        await memory_bank.initialize()
        
        # Check that all files exist and have content
        files_to_check = [
            memory_bank.active_context_file,
            memory_bank.decision_log_file,
            memory_bank.product_context_file,
            memory_bank.progress_file,
            memory_bank.project_brief_file,
            memory_bank.system_patterns_file
        ]
        
        for file_path in files_to_check:
            assert file_path.exists()
            content = file_path.read_text()
            assert len(content) > 0
            # Should have markdown headers
            assert content.startswith("#")
    
    @pytest.mark.asyncio
    async def test_concurrent_updates(self, memory_bank):
        """Test concurrent context updates."""
        await memory_bank.initialize()
        
        # Create multiple concurrent update tasks
        tasks = []
        for i in range(5):
            task = asyncio.create_task(
                memory_bank.update_context("active", {
                    "content": f"Concurrent update {i}"
                })
            )
            tasks.append(task)
        
        # Execute all updates concurrently
        await asyncio.gather(*tasks)
        
        # Verify one of the updates was applied
        context = await memory_bank.get_context("active")
        assert "Concurrent update" in context["content"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
