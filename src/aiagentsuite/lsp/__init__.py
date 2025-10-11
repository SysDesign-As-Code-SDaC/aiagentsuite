"""
AI Agent Suite LSP Extension Components

Provides code actions, completions, and diagnostics for LSP integration.
Implements the bridge between TypeScript LSP extensions and Python framework.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
import asyncio
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class LSPPosition:
    """Represents a position in a document."""
    line: int
    character: int

    def to_dict(self) -> Dict[str, int]:
        return {"line": self.line, "character": self.character}


@dataclass
class LSPRange:
    """Represents a range in a document."""
    start: LSPPosition
    end: LSPPosition

    def to_dict(self) -> dict:
        return {
            "start": self.start.to_dict(),
            "end": self.end.to_dict()
        }


@dataclass
class Diagnostic:
    """Represents a diagnostic message."""
    range: LSPRange
    severity: int  # 1=Error, 2=Warning, 3=Info, 4=Hint
    source: str
    message: str
    code: Optional[str] = None
    related_information: Optional[List[Dict]] = None

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "range": self.range.to_dict(),
            "severity": self.severity,
            "source": self.source,
            "message": self.message
        }
        if self.code:
            result["code"] = self.code
        if self.related_information:
            result["relatedInformation"] = self.related_information
        return result


@dataclass
class CompletionItem:
    """Represents a completion item."""
    label: str
    kind: int  # LSP completion item kinds
    detail: str
    documentation: Optional[str] = None
    insert_text: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "label": self.label,
            "kind": self.kind,
            "detail": self.detail
        }
        if self.documentation:
            result["documentation"] = self.documentation
        if self.insert_text:
            result["insertText"] = self.insert_text
        return result


@dataclass
class CodeAction:
    """Represents a code action."""
    title: str
    kind: str
    diagnostics: Optional[List[Diagnostic]] = None
    edit: Optional[Dict[str, Any]] = None
    command: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "title": self.title,
            "kind": self.kind
        }
        if self.diagnostics:
            result["diagnostics"] = [d.to_dict() for d in self.diagnostics]
        if self.edit:
            result["edit"] = self.edit
        if self.command:
            result["command"] = self.command
        return result


@dataclass
class Hover:
    """Represents hover information."""
    contents: Union[str, Dict[str, Any]]
    range: Optional[LSPRange] = None

    def to_dict(self) -> Dict[str, Any]:
        result = {"contents": self.contents}
        if self.range:
            result["range"] = self.range.to_dict()
        return result


class LSPContext:
    """Context information for LSP operations."""

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


class LSPProvider(ABC):
    """Abstract base class for LSP providers."""

    def __init__(self, context: LSPContext):
        self.context = context

    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the provider."""
        pass


class CompletionProvider(LSPProvider):
    """Provides code completions."""

    async def initialize(self) -> None:
        logger.info("CompletionProvider initialized")

    async def get_completions(
        self,
        uri: str,
        position: LSPPosition,
        document_content: str
    ) -> List[CompletionItem]:
        """Get completions for the given position."""
        completions = []

        # Framework function completions
        framework_functions = [
            ("getConstitution", "Get the master AI agent constitution"),
            ("executeProtocol", "Execute a framework protocol"),
            ("logDecision", "Log an architectural decision"),
            ("getMemoryContext", "Access memory bank context"),
            ("listProtocols", "List available protocols")
        ]

        for func_name, description in framework_functions:
            completions.append(CompletionItem(
                label=f"{func_name}()",
                kind=2,  # Function kind
                detail="AI Agent Suite",
                documentation=description,
                insert_text=f"{func_name}()"
            ))

        # Protocol-specific completions
        try:
            protocols = await self.context.protocol_executor.list_protocols()
            for protocol_name in protocols.keys():
                completions.append(CompletionItem(
                    label=f"executeProtocol('{protocol_name}')",
                    kind=2,  # Function kind
                    detail="Execute Protocol",
                    documentation=f"Execute the {protocol_name} protocol",
                    insert_text=f"executeProtocol('{protocol_name}')",
                ))
        except Exception as e:
            logger.warning(f"Failed to get protocol completions: {e}")

        # VDE principle suggestions based on code analysis
        if self._is_function_definition(document_content, position):
            completions.append(CompletionItem(
                label="vde_compliant",
                kind=17,  # Snippet kind
                detail="VDE Decorator",
                documentation="Mark function as VDE principle compliant",
                insert_text="@vde_compliant\n${1:def function_name}($2):\n    $0"
            ))

        return completions

    def _is_function_definition(self, content: str, position: LSPPosition) -> bool:
        """Check if position is in a function definition context."""
        lines = content.splitlines()
        if position.line >= len(lines):
            return False

        current_line = lines[position.line][:position.character]
        return "def " in current_line or "@" in current_line


class DiagnosticProvider(LSPProvider):
    """Provides diagnostics for VDE compliance."""

    async def initialize(self) -> None:
        logger.info("DiagnosticProvider initialized")

    async def get_diagnostics(
        self,
        uri: str,
        document_content: str
    ) -> List[Diagnostic]:
        """Analyze document for VDE compliance issues."""
        diagnostics = []

        try:
            lines = document_content.splitlines()
            for line_num, line in enumerate(lines):
                # Check for hard-coded secrets
                if self._contains_potential_secret(line):
                    diagnostics.append(Diagnostic(
                        range=LSPRange(
                            start=LSPPosition(line=line_num, character=0),
                            end=LSPPosition(line=line_num, character=len(line))
                        ),
                        severity=1,  # Error
                        source="aiagentsuite",
                        message="Potential security issue: hard-coded secret detected",
                        code="SECURITY_SECRET"
                    ))

                # Check for VDE principle violations
                vde_issues = await self._check_vde_compliance(line, line_num)
                diagnostics.extend(vde_issues)

                # Check for missing error handling
                if self._requires_error_handling(line):
                    diagnostics.append(Diagnostic(
                        range=LSPRange(
                            start=LSPPosition(line=line_num, character=0),
                            end=LSPPosition(line=line_num, character=len(line))
                        ),
                        severity=2,  # Warning
                        source="aiagentsuite",
                        message="Consider adding error handling for this operation",
                        code="ERROR_HANDLING"
                    ))

        except Exception as e:
            logger.error(f"Failed to generate diagnostics: {e}")

        return diagnostics

    def _contains_potential_secret(self, line: str) -> bool:
        """Check if line contains potential secrets."""
        secret_indicators = [
            "password=", "secret=", "key=", "token=",
            "PASSWORD=", "SECRET=", "KEY=", "TOKEN=",
            "api_key=", "API_KEY=", "auth_token=", "AUTH_TOKEN="
        ]
        line_no_spaces = line.replace(" ", "").replace("\t", "")
        return any(indicator in line_no_spaces for indicator in secret_indicators)

    async def _check_vde_compliance(self, line: str, line_num: int) -> List[Diagnostic]:
        """Check line for VDE principle violations."""
        diagnostics = []

        try:
            # Check for YAGNI violations (complex unnecessary code)
            if self._is_overly_complex(line):
                diagnostics.append(Diagnostic(
                    range=LSPRange(
                        start=LSPPosition(line=line_num, character=0),
                        end=LSPPosition(line=line_num, character=len(line))
                    ),
                    severity=3,  # Info
                    source="aiagentsuite",
                    message="Consider if this complexity violates YAGNI principle",
                    code="VDE_YAGNI"
                ))

            # Check for missing documentation
            if self._needs_documentation(line):
                diagnostics.append(Diagnostic(
                    range=LSPRange(
                        start=LSPPosition(line=line_num, character=0),
                        end=LSPPosition(line=line_num, character=len(line))
                    ),
                    severity=3,  # Info
                    source="aiagentsuite",
                    message="Consider adding documentation for this component",
                    code="VDE_DOCUMENTATION"
                ))

        except Exception as e:
            logger.warning(f"VDE compliance check failed: {e}")

        return diagnostics

    def _is_overly_complex(self, line: str) -> bool:
        """Check if line indicates overly complex code."""
        complexity_indicators = [
            "lambda", "[x for", "{x:", "::",
            "reduce(", "map(", "filter(",
            "nested if", "nested for"
        ]
        return any(indicator in line for indicator in complexity_indicators)

    def _needs_documentation(self, line: str) -> bool:
        """Check if line needs documentation."""
        doc_indicators = [
            "class ", "def ", "async def ",
            "    def ", "    async def "
        ]
        return any(indicator in line for indicator in doc_indicators)

    def _requires_error_handling(self, line: str) -> bool:
        """Check if line requires error handling."""
        risky_operations = [
            "open(", "requests.", "urllib.", "subprocess.",
            "socket.", "database", "api.", "client."
        ]
        return any(operation in line for operation in risky_operations)


class CodeActionProvider(LSPProvider):
    """Provides code actions and quick fixes."""

    async def initialize(self) -> None:
        logger.info("CodeActionProvider initialized")

    async def get_code_actions(
        self,
        uri: str,
        range_obj: LSPRange,
        context: Dict[str, Any]
    ) -> List[CodeAction]:
        """Get code actions for the given range and context."""
        actions = []

        # Check for available protocols to execute
        try:
            protocols = await self.context.protocol_executor.list_protocols()
            for protocol_name, protocol_info in protocols.items():
                actions.append(CodeAction(
                    title=f"Execute Protocol: {protocol_name}",
                    kind="refactor.execute",
                    command={
                        "title": f"Execute {protocol_name}",
                        "command": "aiagentsuite.executeProtocol",
                        "arguments": [protocol_name, {"context": "current"}]
                    }
                ))
        except Exception as e:
            logger.warning(f"Failed to get protocol code actions: {e}")

        # Log decision action
        actions.append(CodeAction(
            title="Log Architectural Decision",
            kind="refactor.rewrite",
            command={
                "title": "Log Decision",
                "command": "aiagentsuite.logDecision",
                "arguments": ["Decision to be logged", "Rationale"]
            }
        ))

        # Get constitution action
        actions.append(CodeAction(
            title="View AI Agent Constitution",
            kind="refactor.rewrite",
            command={
                "title": "View Constitution",
                "command": "aiagentsuite.showConstitution"
            }
        ))

        return actions


class HoverProvider(LSPProvider):
    """Provides hover information."""

    async def initialize(self) -> None:
        logger.info("HoverProvider initialized")

    async def get_hover(
        self,
        uri: str,
        position: LSPPosition,
        document_content: str
    ) -> Optional[Hover]:
        """Get hover information for the given position."""
        try:
            word = self._get_word_at_position(document_content, position)

            # Framework keyword hovers
            if word and word.lower() in ["constitution", "protocol", "vde", "principle"]:
                return Hover(
                    contents={
                        "kind": "markdown",
                        "value": f"**{word}**: Part of the AI Agent Suite framework for VDE development."
                    }
                )

            # Function hovers
            if word and word in ["getConstitution", "executeProtocol", "logDecision"]:
                descriptions = {
                    "getConstitution": "Retrieves the master AI agent constitution for guidance",
                    "executeProtocol": "Executes a specific VDE protocol with given context",
                    "logDecision": "Logs an architectural or implementation decision to memory bank"
                }
                return Hover(
                    contents={
                        "kind": "markdown",
                        "value": f"**{word}**\n\n{descriptions[word]}"
                    }
                )

        except Exception as e:
            logger.warning(f"Failed to generate hover: {e}")

        return None

    def _get_word_at_position(self, content: str, position: LSPPosition) -> Optional[str]:
        """Get the word at the given position."""
        lines = content.splitlines()
        if position.line >= len(lines):
            return None

        line = lines[position.line]
        if position.character >= len(line):
            return None

        # Find word boundaries
        start = position.character
        end = position.character

        # Move start left to find word boundary
        while start > 0 and (line[start - 1].isalnum() or line[start - 1] == "_"):
            start -= 1

        # Move end right to find word boundary
        while end < len(line) and (line[end].isalnum() or line[end] == "_"):
            end += 1

        if start < end:
            return line[start:end]

        return None


__all__ = [
    "LSPContext",
    "LSPPosition",
    "LSPRange",
    "Diagnostic",
    "CompletionItem",
    "CodeAction",
    "Hover",
    "CompletionProvider",
    "DiagnosticProvider",
    "CodeActionProvider",
    "HoverProvider"
]
