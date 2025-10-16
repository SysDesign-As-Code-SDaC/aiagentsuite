"""
AI Agent Suite CLI - Command Line Interface
"""

import asyncio
import click
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

from ..core.suite import AIAgentSuite

console = Console()


@click.group()
@click.option('--workspace', '-w', default='.', help='Workspace path containing framework files')
@click.pass_context
def main(ctx, workspace: str) -> None:
    """AI Agent Suite CLI - Development/Debugging Tool (LSP/MCP handles automation)"""
    ctx.ensure_object(dict)
    ctx.obj['workspace'] = Path(workspace)


@main.command()
@click.pass_context
def init(ctx) -> None:
    """Initialize the AI Agent Suite (for development/testing)"""
    workspace_path = ctx.obj['workspace']

    async def _init() -> None:
        suite = AIAgentSuite(workspace_path)
        await suite.initialize()
        console.print("[green]SUCCESS[/green] AI Agent Suite initialized successfully!")

    asyncio.run(_init())


@main.command()
@click.pass_context
def constitution(ctx) -> None:
    """Display the AI agent constitution (for reference/verification)"""
    workspace_path = ctx.obj['workspace']

    async def _show_constitution() -> None:
        suite = AIAgentSuite(workspace_path)
        await suite.initialize()
        constitution = await suite.get_constitution()

        panel = Panel.fit(
            constitution,
            title="[bold blue]Master AI Agent Constitution[/bold blue]",
            border_style="blue"
        )
        console.print(panel)

    asyncio.run(_show_constitution())


@main.command()
@click.pass_context
def protocols(ctx) -> None:
    """List available protocols (for development reference)"""
    workspace_path = ctx.obj['workspace']

    async def _list_protocols() -> None:
        suite = AIAgentSuite(workspace_path)
        await suite.initialize()
        protocols = await suite.list_protocols()

        table = Table(title="Available Protocols")
        table.add_column("Protocol Name", style="cyan", no_wrap=True)
        table.add_column("Phases", style="magenta")
        table.add_column("Description", style="green")

        for name, info in protocols.items():
            table.add_row(
                name,
                str(info.get("phases", 0)),
                info.get("description", "No description")
            )

        console.print(table)

    asyncio.run(_list_protocols())


@main.command()
@click.argument('protocol_name')
@click.option('--context', '-c', help='JSON context for protocol execution')
@click.pass_context
def execute(ctx, protocol_name: str, context: str) -> None:
    """Execute a protocol manually (for testing/debugging)"""
    workspace_path = ctx.obj['workspace']

    async def _execute_protocol() -> None:
        suite = AIAgentSuite(workspace_path)
        await suite.initialize()

        # Parse context if provided
        context_data = {}
        if context:
            import json
            context_data = json.loads(context)

        try:
            result = await suite.execute_protocol(protocol_name, context_data)

            # Display result
            result_text = Text()
            result_text.append(f"Protocol: {result['protocol']}\n", style="bold blue")
            result_text.append(f"Execution ID: {result['execution_id']}\n", style="cyan")
            result_text.append(f"Duration: {result['duration']:.2f}s\n", style="magenta")
            result_text.append(f"Phases: {result['phases_completed']}/{result['total_phases']}\n", style="green")

            if result.get('errors'):
                result_text.append(f"Errors: {len(result['errors'])}\n", style="red")

            panel = Panel.fit(
                result_text,
                title=f"[bold green]Protocol Execution: {protocol_name}[/bold green]",
                border_style="green"
            )
            console.print(panel)

        except ValueError as e:
            console.print(f"[red]Error:[/red] {e}")

    asyncio.run(_execute_protocol())


@main.command()
@click.argument('context_type', type=click.Choice(['active', 'decisions', 'product', 'progress', 'project', 'patterns']))
@click.pass_context
def memory(ctx, context_type: str) -> None:
    """Inspect memory bank context (for debugging/verification)"""
    workspace_path = ctx.obj['workspace']

    async def _show_memory() -> None:
        suite = AIAgentSuite(workspace_path)
        await suite.initialize()

        context = await suite.get_memory_context(context_type)

        panel = Panel.fit(
            context['content'],
            title=f"[bold purple]Memory Context: {context_type.title()}[/bold purple]",
            border_style="purple"
        )
        console.print(panel)
        console.print(f"[dim]Last modified: {context['last_modified']}[/dim]")

    asyncio.run(_show_memory())


@main.command()
@click.argument('decision')
@click.argument('rationale')
@click.option('--context', '-c', help='JSON context for the decision')
@click.pass_context
def log_decision(ctx, decision: str, rationale: str, context: str) -> None:
    """Log a decision manually (for development/testing)"""
    workspace_path = ctx.obj['workspace']

    async def _log_decision() -> None:
        suite = AIAgentSuite(workspace_path)
        await suite.initialize()

        # Parse context if provided
        context_data = {}
        if context:
            import json
            context_data = json.loads(context)

        await suite.log_decision(decision, rationale, context_data)
        console.print(f"[green]SUCCESS[/green] Decision logged: {decision}")

    asyncio.run(_log_decision())


if __name__ == '__main__':
    main()