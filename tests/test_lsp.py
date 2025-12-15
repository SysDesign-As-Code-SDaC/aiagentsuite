"""
Comprehensive test suite for LSP module components.

Tests cover all LSP providers, data classes, and integration scenarios.
"""

import pytest
import pytest_asyncio
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from pathlib import Path
from typing import Dict, List, Any

from aiagentsuite.lsp import (
    LSPContext,
    LSPPosition,
    LSPRange,
    Diagnostic,
    CompletionItem,
    CodeAction,
    Hover,
    CompletionProvider,
    DiagnosticProvider,
    CodeActionProvider,
    HoverProvider
)


class TestLSPDataClasses:
    """Test LSP data classes and their serialization."""

    def test_lsp_position_creation(self):
        """Test LSPPosition dataclass creation and serialization."""
        pos = LSPPosition(line=10, character=5)
        assert pos.line == 10
        assert pos.character == 5

        expected_dict = {"line": 10, "character": 5}
        assert pos.to_dict() == expected_dict

    def test_lsp_range_creation(self):
        """Test LSPRange dataclass creation and serialization."""
        start = LSPPosition(line=1, character=0)
        end = LSPPosition(line=1, character=10)
        range_obj = LSPRange(start=start, end=end)

        assert range_obj.start == start
        assert range_obj.end == end

        expected_dict = {
            "start": {"line": 1, "character": 0},
            "end": {"line": 1, "character": 10}
        }
        assert range_obj.to_dict() == expected_dict

    def test_diagnostic_creation_minimal(self):
        """Test Diagnostic creation with minimal required fields."""
        range_obj = LSPRange(
            start=LSPPosition(line=1, character=0),
            end=LSPPosition(line=1, character=5)
        )
        diagnostic = Diagnostic(
            range=range_obj,
            severity=1,
            source="test",
            message="Test error"
        )

        assert diagnostic.range == range_obj
        assert diagnostic.severity == 1
        assert diagnostic.source == "test"
        assert diagnostic.message == "Test error"
        assert diagnostic.code is None
        assert diagnostic.related_information is None

    def test_diagnostic_creation_full(self):
        """Test Diagnostic creation with all fields."""
        range_obj = LSPRange(
            start=LSPPosition(line=1, character=0),
            end=LSPPosition(line=1, character=5)
        )
        diagnostic = Diagnostic(
            range=range_obj,
            severity=2,
            source="aiagentsuite",
            message="Security issue detected",
            code="SECURITY_SECRET",
            related_information=[{"message": "Related info"}]
        )

        result = diagnostic.to_dict()
        assert result["range"]["start"]["line"] == 1
        assert result["severity"] == 2
        assert result["source"] == "aiagentsuite"
        assert result["message"] == "Security issue detected"
        assert result["code"] == "SECURITY_SECRET"
        assert result["relatedInformation"] == [{"message": "Related info"}]

    def test_completion_item_creation_minimal(self):
        """Test CompletionItem creation with minimal fields."""
        item = CompletionItem(
            label="test()",
            kind=2,
            detail="Test function"
        )

        assert item.label == "test()"
        assert item.kind == 2
        assert item.detail == "Test function"
        assert item.documentation is None
        assert item.insert_text is None

    def test_completion_item_creation_full(self):
        """Test CompletionItem creation with all fields."""
        item = CompletionItem(
            label="getConstitution()",
            kind=2,
            detail="AI Agent Suite",
            documentation="Get the master AI agent constitution",
            insert_text="getConstitution()"
        )

        result = item.to_dict()
        assert result["label"] == "getConstitution()"
        assert result["kind"] == 2
        assert result["detail"] == "AI Agent Suite"
        assert result["documentation"] == "Get the master AI agent constitution"
        assert result["insertText"] == "getConstitution()"

    def test_code_action_creation_minimal(self):
        """Test CodeAction creation with minimal fields."""
        action = CodeAction(
            title="Execute Protocol",
            kind="refactor.execute"
        )

        assert action.title == "Execute Protocol"
        assert action.kind == "refactor.execute"
        assert action.diagnostics is None
        assert action.edit is None
        assert action.command is None

    def test_code_action_creation_full(self):
        """Test CodeAction creation with all fields."""
        diagnostics = [Diagnostic(
            range=LSPRange(LSPPosition(1, 0), LSPPosition(1, 5)),
            severity=1,
            source="test",
            message="Test diagnostic"
        )]
        action = CodeAction(
            title="Fix Issue",
            kind="quickfix",
            diagnostics=diagnostics,
            edit={"changes": {}},
            command={"title": "Fix", "command": "test.fix"}
        )

        result = action.to_dict()
        assert result["title"] == "Fix Issue"
        assert result["kind"] == "quickfix"
        assert len(result["diagnostics"]) == 1
        assert result["edit"] == {"changes": {}}
        assert result["command"] == {"title": "Fix", "command": "test.fix"}

    def test_hover_creation_minimal(self):
        """Test Hover creation with minimal fields."""
        hover = Hover(contents="Simple hover text")

        assert hover.contents == "Simple hover text"
        assert hover.range is None

        result = hover.to_dict()
        assert result["contents"] == "Simple hover text"
        assert "range" not in result

    def test_hover_creation_full(self):
        """Test Hover creation with all fields."""
        range_obj = LSPRange(LSPPosition(1, 0), LSPPosition(1, 10))
        hover = Hover(
            contents={"kind": "markdown", "value": "**bold** text"},
            range=range_obj
        )

        result = hover.to_dict()
        assert result["contents"]["kind"] == "markdown"
        assert result["contents"]["value"] == "**bold** text"
        assert result["range"]["start"]["line"] == 1


class TestLSPContext:
    """Test LSPContext class functionality."""

    def test_lsp_context_creation(self):
        """Test LSPContext initialization."""
        workspace_path = Path("/test/workspace")
        framework_manager = MagicMock()
        memory_bank = MagicMock()
        protocol_executor = MagicMock()

        context = LSPContext(
            workspace_path=workspace_path,
            framework_manager=framework_manager,
            memory_bank=memory_bank,
            protocol_executor=protocol_executor
        )

        assert context.workspace_path == workspace_path
        assert context.framework == framework_manager
        assert context.memory_bank == memory_bank
        assert context.protocol_executor == protocol_executor


@pytest_asyncio.fixture
async def mock_lsp_context():
    """Create a mock LSP context for testing."""
    workspace_path = Path("/test/workspace")
    framework_manager = AsyncMock()
    memory_bank = AsyncMock()
    protocol_executor = AsyncMock()

    # Mock protocol executor list_protocols method
    protocol_executor.list_protocols.return_value = {
        "Security Audit": {"description": "Security protocol"},
        "CodeReview": {"description": "Review protocol"}
    }

    context = LSPContext(
        workspace_path=workspace_path,
        framework_manager=framework_manager,
        memory_bank=memory_bank,
        protocol_executor=protocol_executor
    )

    return context


class TestCompletionProvider:
    """Test CompletionProvider functionality."""

    @pytest.mark.asyncio
    async def test_completion_provider_initialization(self, mock_lsp_context):
        """Test CompletionProvider initialization."""
        provider = CompletionProvider(mock_lsp_context)
        await provider.initialize()

        assert provider.context == mock_lsp_context

    @pytest.mark.asyncio
    async def test_get_completions_basic(self, mock_lsp_context):
        """Test basic completion generation."""
        provider = CompletionProvider(mock_lsp_context)
        await provider.initialize()

        position = LSPPosition(line=1, character=10)
        completions = await provider.get_completions(
            uri="file:///test.py",
            position=position,
            document_content="def test():\n    "
        )

        # Should have framework function completions
        assert len(completions) >= 5  # At least the basic framework functions

        # Check for specific completions
        labels = [c.label for c in completions]
        assert "getConstitution()" in labels
        assert "executeProtocol()" in labels
        assert "logDecision()" in labels

    @pytest.mark.asyncio
    async def test_get_completions_with_protocols(self, mock_lsp_context):
        """Test completion generation with protocol suggestions."""
        provider = CompletionProvider(mock_lsp_context)
        await provider.initialize()

        position = LSPPosition(line=1, character=10)
        completions = await provider.get_completions(
            uri="file:///test.py",
            position=position,
            document_content="def test():\n    "
        )

        # Should include protocol-specific completions
        labels = [c.label for c in completions]
        assert "executeProtocol('Security Audit')" in labels
        assert "executeProtocol('CodeReview')" in labels

    @pytest.mark.asyncio
    async def test_get_completions_function_definition_context(self, mock_lsp_context):
        """Test completions in function definition context."""
        provider = CompletionProvider(mock_lsp_context)
        await provider.initialize()

        position = LSPPosition(line=0, character=4)  # In "def " context
        completions = await provider.get_completions(
            uri="file:///test.py",
            position=position,
            document_content="def "
        )

        # Should include VDE decorator suggestion
        labels = [c.label for c in completions]
        assert "vde_compliant" in labels

    @pytest.mark.asyncio
    async def test_get_completions_protocol_error_handling(self, mock_lsp_context):
        """Test completion generation handles protocol errors gracefully."""
        # Make protocol executor fail
        mock_lsp_context.protocol_executor.list_protocols.side_effect = Exception("Test error")

        provider = CompletionProvider(mock_lsp_context)
        await provider.initialize()

        position = LSPPosition(line=1, character=10)
        completions = await provider.get_completions(
            uri="file:///test.py",
            position=position,
            document_content="def test():\n    "
        )

        # Should still return basic completions despite protocol error
        assert len(completions) >= 5

    def test_is_function_definition_detection(self, mock_lsp_context):
        """Test function definition context detection."""
        provider = CompletionProvider(mock_lsp_context)

        # Test various contexts
        assert provider._is_function_definition("def test_function():", LSPPosition(0, 10))
        assert provider._is_function_definition("@decorator\ndef test():", LSPPosition(1, 5))
        assert not provider._is_function_definition("    return x", LSPPosition(0, 5))
        assert not provider._is_function_definition("class Test:", LSPPosition(0, 5))


class TestDiagnosticProvider:
    """Test DiagnosticProvider functionality."""

    @pytest.mark.asyncio
    async def test_diagnostic_provider_initialization(self, mock_lsp_context):
        """Test DiagnosticProvider initialization."""
        provider = DiagnosticProvider(mock_lsp_context)
        await provider.initialize()

        assert provider.context == mock_lsp_context

    @pytest.mark.asyncio
    async def test_get_diagnostics_empty_file(self, mock_lsp_context):
        """Test diagnostics for empty file."""
        provider = DiagnosticProvider(mock_lsp_context)
        await provider.initialize()

        diagnostics = await provider.get_diagnostics(
            uri="file:///test.py",
            document_content=""
        )

        assert diagnostics == []

    @pytest.mark.asyncio
    async def test_get_diagnostics_security_issues(self, mock_lsp_context):
        """Test detection of security issues."""
        provider = DiagnosticProvider(mock_lsp_context)
        await provider.initialize()

        content = """\
def test():
    password = "secret123"
    api_key = "key123"
    token = "token123"
"""

        diagnostics = await provider.get_diagnostics(
            uri="file:///test.py",
            document_content=content
        )

        # Should detect multiple security issues
        security_diagnostics = [d for d in diagnostics if d.code == "SECURITY_SECRET"]
        assert len(security_diagnostics) == 3

        for diagnostic in security_diagnostics:
            assert diagnostic.severity == 1  # Error
            assert diagnostic.source == "aiagentsuite"

    @pytest.mark.asyncio
    async def test_get_diagnostics_error_handling(self, mock_lsp_context):
        """Test detection of missing error handling."""
        provider = DiagnosticProvider(mock_lsp_context)
        await provider.initialize()

        content = """\
def test():
    open("file.txt")
    requests.get("http://api.com")
    subprocess.run(["ls"])
"""

        diagnostics = await provider.get_diagnostics(
            uri="file:///test.py",
            document_content=content
        )

        # Should detect error handling warnings
        error_diagnostics = [d for d in diagnostics if d.code == "ERROR_HANDLING"]
        assert len(error_diagnostics) == 3

        for diagnostic in error_diagnostics:
            assert diagnostic.severity == 2  # Warning

    @pytest.mark.asyncio
    async def test_get_diagnostics_vde_compliance(self, mock_lsp_context):
        """Test VDE compliance diagnostics."""
        provider = DiagnosticProvider(mock_lsp_context)
        await provider.initialize()

        content = """\
def complex_function():
    result = [x**2 for x in range(100) if x % 2 == 0]
    return reduce(lambda x, y: x + y, result)

class MyClass:
    pass
"""

        diagnostics = await provider.get_diagnostics(
            uri="file:///test.py",
            document_content=content
        )

        # Should detect complexity and documentation issues
        yagni_diagnostics = [d for d in diagnostics if d.code == "VDE_YAGNI"]
        doc_diagnostics = [d for d in diagnostics if d.code == "VDE_DOCUMENTATION"]

        assert len(yagni_diagnostics) >= 1  # List comprehension and reduce
        assert len(doc_diagnostics) >= 1   # Class and function without docs

    def test_contains_potential_secret_detection(self, mock_lsp_context):
        """Test secret detection logic."""
        provider = DiagnosticProvider(mock_lsp_context)

        # Test patterns that should be detected (after removing spaces)
        assert provider._contains_potential_secret('password = "secret"')  # becomes 'password="secret"'
        assert provider._contains_potential_secret('API_KEY = os.getenv("KEY")')  # becomes 'API_KEY=os.getenv("KEY")'
        assert provider._contains_potential_secret('token = get_token()')  # becomes 'token=get_token()'
        assert not provider._contains_potential_secret('result = calculate()')
        assert not provider._contains_potential_secret('count = len(items)')

    def test_is_overly_complex_detection(self, mock_lsp_context):
        """Test complexity detection logic."""
        provider = DiagnosticProvider(mock_lsp_context)

        assert provider._is_overly_complex('[x for x in items if condition]')
        assert provider._is_overly_complex('reduce(lambda x, y: x + y, items)')
        assert provider._is_overly_complex('map(str, items)')
        assert not provider._is_overly_complex('for item in items:')
        assert not provider._is_overly_complex('if condition:')

    def test_needs_documentation_detection(self, mock_lsp_context):
        """Test documentation need detection."""
        provider = DiagnosticProvider(mock_lsp_context)

        assert provider._needs_documentation('class MyClass:')
        assert provider._needs_documentation('def my_function():')
        assert provider._needs_documentation('    def method(self):')
        assert provider._needs_documentation('async def async_func():')
        assert not provider._needs_documentation('    return x')
        assert not provider._needs_documentation('x = 1')

    def test_requires_error_handling_detection(self, mock_lsp_context):
        """Test error handling requirement detection."""
        provider = DiagnosticProvider(mock_lsp_context)

        assert provider._requires_error_handling('open("file.txt")')
        assert provider._requires_error_handling('requests.get(url)')
        assert provider._requires_error_handling('subprocess.run(cmd)')
        assert provider._requires_error_handling('socket.connect(addr)')
        assert not provider._requires_error_handling('print("hello")')
        assert not provider._requires_error_handling('x = 1')


class TestCodeActionProvider:
    """Test CodeActionProvider functionality."""

    @pytest.mark.asyncio
    async def test_code_action_provider_initialization(self, mock_lsp_context):
        """Test CodeActionProvider initialization."""
        provider = CodeActionProvider(mock_lsp_context)
        await provider.initialize()

        assert provider.context == mock_lsp_context

    @pytest.mark.asyncio
    async def test_get_code_actions_with_protocols(self, mock_lsp_context):
        """Test code action generation with available protocols."""
        provider = CodeActionProvider(mock_lsp_context)
        await provider.initialize()

        range_obj = LSPRange(LSPPosition(1, 0), LSPPosition(1, 10))
        context = {}

        actions = await provider.get_code_actions(
            uri="file:///test.py",
            range_obj=range_obj,
            context=context
        )

        # Should include protocol execution actions
        protocol_actions = [a for a in actions if "Execute Protocol:" in a.title]
        assert len(protocol_actions) == 2  # Security Audit and CodeReview

        # Check action structure
        for action in protocol_actions:
            assert action.kind == "refactor.execute"
            assert "command" in action.command
            assert action.command["command"] == "aiagentsuite.executeProtocol"

    @pytest.mark.asyncio
    async def test_get_code_actions_standard_actions(self, mock_lsp_context):
        """Test standard code actions are always available."""
        provider = CodeActionProvider(mock_lsp_context)
        await provider.initialize()

        range_obj = LSPRange(LSPPosition(1, 0), LSPPosition(1, 10))
        context = {}

        actions = await provider.get_code_actions(
            uri="file:///test.py",
            range_obj=range_obj,
            context=context
        )

        # Should always include standard actions
        titles = [a.title for a in actions]
        assert "Log Architectural Decision" in titles
        assert "View AI Agent Constitution" in titles

    @pytest.mark.asyncio
    async def test_get_code_actions_protocol_error_handling(self, mock_lsp_context):
        """Test code actions handle protocol errors gracefully."""
        # Make protocol executor fail
        mock_lsp_context.protocol_executor.list_protocols.side_effect = Exception("Test error")

        provider = CodeActionProvider(mock_lsp_context)
        await provider.initialize()

        range_obj = LSPRange(LSPPosition(1, 0), LSPPosition(1, 10))
        context = {}

        actions = await provider.get_code_actions(
            uri="file:///test.py",
            range_obj=range_obj,
            context=context
        )

        # Should still return standard actions despite protocol error
        assert len(actions) >= 2  # At least the standard actions


class TestHoverProvider:
    """Test HoverProvider functionality."""

    @pytest.mark.asyncio
    async def test_hover_provider_initialization(self, mock_lsp_context):
        """Test HoverProvider initialization."""
        provider = HoverProvider(mock_lsp_context)
        await provider.initialize()

        assert provider.context == mock_lsp_context

    @pytest.mark.asyncio
    async def test_get_hover_framework_keywords(self, mock_lsp_context):
        """Test hover for framework keywords."""
        provider = HoverProvider(mock_lsp_context)
        await provider.initialize()

        # Test constitution keyword
        position = LSPPosition(line=0, character=10)  # Position in "constitution"
        hover = await provider.get_hover(
            uri="file:///test.py",
            position=position,
            document_content="This is constitution related code"
        )

        assert hover is not None
        assert "constitution" in hover.contents["value"].lower()
        assert hover.contents["kind"] == "markdown"

    @pytest.mark.asyncio
    async def test_get_hover_framework_functions(self, mock_lsp_context):
        """Test hover for framework functions."""
        provider = HoverProvider(mock_lsp_context)
        await provider.initialize()

        # Test getConstitution function
        position = LSPPosition(line=0, character=11)  # Position in "getConstitution"
        hover = await provider.get_hover(
            uri="file:///test.py",
            position=position,
            document_content="result = getConstitution()"
        )

        assert hover is not None
        assert "getConstitution" in hover.contents["value"]
        assert "constitution" in hover.contents["value"].lower()

    @pytest.mark.asyncio
    async def test_get_hover_no_match(self, mock_lsp_context):
        """Test hover returns None for non-matching words."""
        provider = HoverProvider(mock_lsp_context)
        await provider.initialize()

        position = LSPPosition(line=0, character=5)
        hover = await provider.get_hover(
            uri="file:///test.py",
            position=position,
            document_content="regular python code here"
        )

        assert hover is None

    @pytest.mark.asyncio
    async def test_get_hover_error_handling(self, mock_lsp_context):
        """Test hover handles errors gracefully."""
        provider = HoverProvider(mock_lsp_context)
        await provider.initialize()

        # Test with invalid position
        position = LSPPosition(line=10, character=100)  # Beyond content
        hover = await provider.get_hover(
            uri="file:///test.py",
            position=position,
            document_content="short line"
        )

        # Should not crash, may return None
        assert hover is None

    def test_get_word_at_position_basic(self, mock_lsp_context):
        """Test word extraction at position."""
        provider = HoverProvider(mock_lsp_context)

        content = "def getConstitution():\n    return constitution"
        position = LSPPosition(line=0, character=7)  # In "getConstitution"

        word = provider._get_word_at_position(content, position)
        assert word == "getConstitution"

    def test_get_word_at_position_edge_cases(self, mock_lsp_context):
        """Test word extraction at various edge cases."""
        provider = HoverProvider(mock_lsp_context)

        # Empty line
        assert provider._get_word_at_position("", LSPPosition(0, 0)) is None

        # Position beyond line length
        assert provider._get_word_at_position("short", LSPPosition(0, 10)) is None

        # Position beyond content
        assert provider._get_word_at_position("line1\nline2", LSPPosition(5, 0)) is None

        # Valid positions
        content = "word1 word2 word3"
        assert provider._get_word_at_position(content, LSPPosition(0, 0)) == "word1"
        assert provider._get_word_at_position(content, LSPPosition(0, 6)) == "word2"
        assert provider._get_word_at_position(content, LSPPosition(0, 12)) == "word3"


class TestLSPIntegration:
    """Test LSP components working together."""

    @pytest.mark.asyncio
    async def test_multiple_providers_initialization(self, mock_lsp_context):
        """Test multiple providers can be initialized together."""
        providers = [
            CompletionProvider(mock_lsp_context),
            DiagnosticProvider(mock_lsp_context),
            CodeActionProvider(mock_lsp_context),
            HoverProvider(mock_lsp_context)
        ]

        # Initialize all providers
        await asyncio.gather(*[provider.initialize() for provider in providers])

        # All should be initialized successfully
        for provider in providers:
            assert provider.context == mock_lsp_context

    @pytest.mark.asyncio
    async def test_lsp_workflow_simulation(self, mock_lsp_context):
        """Test a simulated LSP workflow with multiple providers."""
        # Initialize providers
        completion_provider = CompletionProvider(mock_lsp_context)
        diagnostic_provider = DiagnosticProvider(mock_lsp_context)
        code_action_provider = CodeActionProvider(mock_lsp_context)
        hover_provider = HoverProvider(mock_lsp_context)

        await asyncio.gather(
            completion_provider.initialize(),
            diagnostic_provider.initialize(),
            code_action_provider.initialize(),
            hover_provider.initialize()
        )

        # Simulate a document with issues
        document_content = '''\
def insecure_function():
    password = "hardcoded_secret"
    api_key = "secret_key"
    open("file.txt")
    return getConstitution()

class UndocumentedClass:
    pass
'''

        # Get diagnostics
        diagnostics = await diagnostic_provider.get_diagnostics(
            uri="file:///test.py",
            document_content=document_content
        )

        # Should find security issues, error handling issues, and documentation issues
        assert len(diagnostics) >= 4

        # Get completions
        position = LSPPosition(line=4, character=11)  # In "getConstitution"
        completions = await completion_provider.get_completions(
            uri="file:///test.py",
            position=position,
            document_content=document_content
        )

        assert len(completions) > 0

        # Get hover information
        hover = await hover_provider.get_hover(
            uri="file:///test.py",
            position=position,
            document_content=document_content
        )

        assert hover is not None

        # Get code actions
        range_obj = LSPRange(LSPPosition(1, 4), LSPPosition(1, 20))  # password line
        code_actions = await code_action_provider.get_code_actions(
            uri="file:///test.py",
            range_obj=range_obj,
            context={}
        )

        assert len(code_actions) > 0

    @pytest.mark.asyncio
    async def test_provider_error_isolation(self, mock_lsp_context):
        """Test that one provider error doesn't affect others."""
        # Make protocol executor fail for all providers that use it
        mock_lsp_context.protocol_executor.list_protocols.side_effect = Exception("Protocol error")

        providers = [
            CompletionProvider(mock_lsp_context),
            CodeActionProvider(mock_lsp_context)
        ]

        await asyncio.gather(*[provider.initialize() for provider in providers])

        # Both should still function despite protocol errors
        completions = await providers[0].get_completions(
            uri="file:///test.py",
            position=LSPPosition(0, 0),
            document_content="test"
        )
        assert isinstance(completions, list)

        actions = await providers[1].get_code_actions(
            uri="file:///test.py",
            range_obj=LSPRange(LSPPosition(0, 0), LSPPosition(0, 1)),
            context={}
        )
        assert isinstance(actions, list)