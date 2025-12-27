"""
AI Agent Suite TUI Application
"""

import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Header, Footer, Static, DataTable, Button, Label, TabbedContent, TabPane, Log
from textual.binding import Binding
from textual import work

from ..core.suite import AIAgentSuite


class SystemStatus(Static):
    """Widget to display system status."""

    def compose(self) -> ComposeResult:
        yield Label("System Status", classes="section-title")
        yield DataTable(id="status-table")

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.add_columns("Service", "Status", "Details")
        # Mock data for now - in real implementation this would fetch from EnterpriseDashboard
        table.add_rows([
            ("LSP Server", "✅ Running", "Port: 3000"),
            ("MCP Server", "✅ Running", "Port: 3001"),
            ("Redis", "✅ Connected", "Keys: 42"),
            ("Postgres", "✅ Connected", "Users: 1"),
            ("Prometheus", "❌ Stopped", "Connection refused"),
        ])


class ProtocolList(Static):
    """Widget to list and execute protocols."""

    def compose(self) -> ComposeResult:
        yield Label("Available Protocols", classes="section-title")
        yield DataTable(id="protocol-table")
        yield Horizontal(
            Button("Refresh", id="refresh-btn", variant="primary"),
            Button("Execute Selected", id="exec-btn", variant="success", disabled=True),
            classes="button-bar"
        )
        yield Log(id="protocol-log", highlight=True)

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.cursor_type = "row"
        table.add_columns("Name", "Phases", "Description")

    @work
    async def load_protocols(self, app_instance: 'AgentSuiteApp') -> None:
        try:
            protocols = await app_instance.suite.list_protocols()
            rows = []
            for name, info in protocols.items():
                rows.append((name, str(info.get("phases", 0)), info.get("description", "N/A")))

            # Update UI on main thread
            self.app.call_from_thread(self._update_protocol_table, rows)
        except Exception as e:
            self.app.call_from_thread(self._log_error, f"Error loading protocols: {e}")

    def _update_protocol_table(self, rows: List[Any]) -> None:
        table = self.query_one(DataTable)
        table.clear()
        table.add_rows(rows)
        self.query_one("#protocol-log").write(f"Loaded {len(rows)} protocols.")

    def _log_error(self, message: str) -> None:
        self.query_one("#protocol-log").write(message)

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        self.query_one("#exec-btn").disabled = False

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "refresh-btn":
            self.load_protocols(self.app)
        elif event.button.id == "exec-btn":
            table = self.query_one(DataTable)
            if table.cursor_row is not None:
                protocol_name = table.get_row_at(table.cursor_row)[0]
                self.execute_protocol(protocol_name)

    @work
    async def execute_protocol(self, protocol_name: str) -> None:
        self.app.call_from_thread(self._log_message, f"Executing protocol: {protocol_name}...")

        try:
            # Simple execution without context for now
            result = await self.app.suite.execute_protocol(protocol_name, {})
            self.app.call_from_thread(self._log_execution_result, protocol_name, result)
        except Exception as e:
             self.app.call_from_thread(self._log_error, f"Execution failed: {e}")

    def _log_message(self, message: str) -> None:
        self.query_one("#protocol-log").write(message)

    def _log_execution_result(self, protocol_name: str, result: Dict[str, Any]) -> None:
        log = self.query_one("#protocol-log")
        log.write(f"Protocol {protocol_name} completed!")
        log.write(f"Duration: {result['duration']:.2f}s")
        log.write(f"Phases completed: {result.get('phases_completed', 0)}")
        if result.get('errors'):
            log.write(f"Errors: {result['errors']}")


class MemoryView(Static):
    """Widget to view memory bank."""

    def compose(self) -> ComposeResult:
        yield Label("Memory Bank Context", classes="section-title")
        yield Horizontal(
            Button("Active Context", id="mem-active"),
            Button("Decisions", id="mem-decisions"),
            Button("Product Context", id="mem-product"),
            classes="button-bar"
        )
        yield Static(id="memory-content", classes="box")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        context_type = event.button.id.replace("mem-", "")
        self.load_memory(context_type)

    @work
    async def load_memory(self, context_type: str) -> None:
        try:
            # Map button IDs to valid context types if necessary
            # For now assuming 'active', 'decisions', 'product' work
            context = await self.app.suite.get_memory_context(context_type)
            self.app.call_from_thread(self._update_memory_content, context['content'])
        except Exception as e:
             self.app.call_from_thread(self._update_memory_content, f"Error loading memory: {e}")

    def _update_memory_content(self, content: str) -> None:
        self.query_one("#memory-content").update(content)


class AgentSuiteApp(App):
    """AI Agent Suite TUI Application."""

    CSS = """
    .section-title {
        text-align: center;
        text-style: bold;
        padding: 1;
        background: $primary;
        color: $text;
        width: 100%;
    }

    .button-bar {
        height: 3;
        margin: 1 0;
        align: center middle;
    }

    Button {
        margin: 0 1;
    }

    .box {
        border: solid $accent;
        padding: 1;
        height: 1fr;
    }

    Log {
        height: 1fr;
        border: solid $secondary;
        background: $surface;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("d", "toggle_dark", "Toggle Dark Mode"),
    ]

    def __init__(self, workspace_path: Path):
        super().__init__()
        self.workspace_path = workspace_path
        self.suite = AIAgentSuite(workspace_path)

    async def on_mount(self) -> None:
        await self.suite.initialize()
        # Initial load for protocol list if it's the active tab
        self.query_one(ProtocolList).load_protocols(self)

    def compose(self) -> ComposeResult:
        yield Header()
        yield TabbedContent(
            TabPane("Protocols", ProtocolList()),
            TabPane("System Status", SystemStatus()),
            TabPane("Memory Bank", MemoryView()),
        )
        yield Footer()


if __name__ == "__main__":
    app = AgentSuiteApp(Path("."))
    app.run()
