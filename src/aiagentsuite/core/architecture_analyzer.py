"""
ARCHITECTURE ANALYZER - AST-Based Code Intelligence

Leverages Python AST to create comprehensive class/function maps,
dependency analysis, integration maps, and Mermaid documentation.

Features:
- AST-powered code analysis
- Automatic dependency mapping
- Integration discovery
- Mermaid diagram generation
- Human & LLM readable documentation
- Real-time architecture documentation

Usage:
    analyzer = ArchitectureAnalyzer()
    analyzer.analyze_project("src/")
    analyzer.generate_documentation("docs/ARCHITECTURE.md")
    analyzer.generate_mermaid_diagrams("docs/diagrams/")
"""

import ast
import os
import json
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any, Optional
from dataclasses import dataclass
from collections import defaultdict, deque


@dataclass
class ClassInfo:
    """Information about a class."""
    name: str
    file_path: str
    line_number: int
    bases: List[str]
    methods: List[str]
    properties: List[str]
    decorators: List[str]
    docstring: Optional[str]
    dependencies: Set[str]
    integrations: Set[str]


@dataclass
class FunctionInfo:
    """Information about a function."""
    name: str
    file_path: str
    line_number: int
    parameters: List[str]
    decorators: List[str]
    docstring: Optional[str]
    dependencies: Set[str]
    complexity: int


@dataclass
class ModuleInfo:
    """Information about a module."""
    name: str
    file_path: str
    classes: Dict[str, ClassInfo]
    functions: Dict[str, FunctionInfo]
    imports: Set[str]
    exports: Set[str]
    dependencies: Set[str]


@dataclass
class IntegrationInfo:
    """Information about integrations between components."""
    from_component: str
    to_component: str
    interaction_type: str  # 'import', 'inheritance', 'composition', 'method_call', etc.
    file_path: str
    line_number: int
    context: str


class ASTVisitor(ast.NodeVisitor):
    """Custom AST visitor for code analysis."""

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.current_class: Optional[str] = None
        self.current_function: Optional[str] = None
        self.classes: Dict[str, ClassInfo] = {}
        self.functions: Dict[str, FunctionInfo] = {}
        self.imports: Set[str] = set()
        self.calls: List[Tuple[str, int]] = []
        self.current_context = []

    def visit_Import(self, node: ast.Import) -> None:
        """Handle import statements."""
        for alias in node.names:
            self.imports.add(alias.name.split('.')[0])
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Handle from import statements."""
        if node.module:
            self.imports.add(node.module.split('.')[0])
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Handle class definitions."""
        self.current_class = node.name
        self.current_context.append(f"class_{node.name}")

        # Extract base classes
        bases = []
        for base in node.bases:
            if isinstance(base, ast.Name):
                bases.append(base.id)
            elif isinstance(base, ast.Attribute):
                bases.append(f"{base.value.id}.{base.attr}")

        # Extract decorators
        decorators = []
        for decorator in node.decorator_list:
            decorators.append(self._get_decorator_name(decorator))

        # Extract docstring
        docstring = ast.get_docstring(node)

        # Initialize class info
        class_info = ClassInfo(
            name=node.name,
            file_path=self.file_path,
            line_number=node.lineno,
            bases=bases,
            methods=[],
            properties=[],
            decorators=decorators,
            docstring=docstring,
            dependencies=set(),
            integrations=set()
        )

        self.classes[node.name] = class_info
        self.generic_visit(node)
        self.current_context.pop()
        self.current_class = None

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Handle function definitions."""
        self.current_function = node.name
        self.current_context.append(f"function_{node.name}")

        # Extract parameters
        parameters = []
        for arg in node.args.args:
            parameters.append(arg.arg)

        # Extract decorators
        decorators = []
        for decorator in node.decorator_list:
            decorators.append(self._get_decorator_name(decorator))

        # Extract docstring
        docstring = ast.get_docstring(node)

        # Calculate complexity (simple cyclomatic complexity)
        complexity = self._calculate_complexity(node)

        function_info = FunctionInfo(
            name=node.name,
            file_path=self.file_path,
            line_number=node.lineno,
            parameters=parameters,
            decorators=decorators,
            docstring=docstring,
            dependencies=set(),
            complexity=complexity
        )

        self.functions[node.name] = function_info

        if self.current_class:
            self.classes[self.current_class].methods.append(node.name)

        self.generic_visit(node)
        self.current_context.pop()
        self.current_function = None

    def visit_Call(self, node: ast.Call) -> None:
        """Handle function/method calls."""
        if isinstance(node.func, ast.Name):
            self.calls.append((node.func.id, node.lineno))
        elif isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name):
                self.calls.append((f"{node.func.value.id}.{node.func.attr}", node.lineno))

        self.generic_visit(node)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        """Handle annotated assignments (properties)."""
        if self.current_class and isinstance(node.target, ast.Name):
            self.classes[self.current_class].properties.append(node.target.id)
        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign) -> None:
        """Handle assignments."""
        if self.current_class and len(node.targets) == 1:
            if isinstance(node.targets[0], ast.Name):
                # Simple heuristic for properties
                if not node.targets[0].id.startswith('_'):
                    self.classes[self.current_class].properties.append(node.targets[0].id)
        self.generic_visit(node)

    def _get_decorator_name(self, decorator: ast.expr) -> str:
        """Extract decorator name from AST node."""
        if isinstance(decorator, ast.Name):
            return decorator.id
        elif isinstance(decorator, ast.Attribute):
            return f"{decorator.value.id}.{decorator.attr}"
        elif isinstance(decorator, ast.Call):
            if isinstance(decorator.func, ast.Name):
                return decorator.func.id
            elif isinstance(decorator.func, ast.Attribute):
                return f"{decorator.func.value.id}.{decorator.func.attr}"
        return str(decorator)

    def _calculate_complexity(self, node: ast.FunctionDef) -> int:
        """Calculate cyclomatic complexity for a function."""
        complexity = 1  # Base complexity

        class ComplexityVisitor(ast.NodeVisitor):
            def __init__(self):
                self.complexity = 1

            def visit_If(self, node):
                self.complexity += 1
                self.generic_visit(node)

            def visit_For(self, node):
                self.complexity += 1
                self.generic_visit(node)

            def visit_While(self, node):
                self.complexity += 1
                self.generic_visit(node)

            def visit_With(self, node):
                self.complexity += 1
                self.generic_visit(node)

            def visit_Try(self, node):
                self.complexity += len(node.handlers)
                self.generic_visit(node)

            def visit_And(self, node):
                self.complexity += 1
                self.generic_visit(node)

            def visit_Or(self, node):
                self.complexity += 1
                self.generic_visit(node)

        visitor = ComplexityVisitor()
        visitor.visit(node)
        return visitor.complexity


class ArchitectureAnalyzer:
    """Main architecture analyzer using AST."""

    def __init__(self, project_root: Optional[str] = None):
        self.project_root = Path(project_root or Path.cwd())
        self.modules: Dict[str, ModuleInfo] = {}
        self.integrations: List[IntegrationInfo] = []
        self.global_calls: Dict[str, List[Tuple[str, int]]] = defaultdict(list)

    def analyze_project(self, source_path: str = "src/") -> None:
        """
        Analyze the entire project using AST.

        Args:
            source_path: Path to source code directory
        """
        source_path = self.project_root / source_path

        # Find all Python files
        python_files = []
        for root, dirs, files in os.walk(source_path):
            for file in files:
                if file.endswith('.py') and not file.startswith('__'):
                    python_files.append(Path(root) / file)

        # Analyze each file
        for file_path in python_files:
            self.analyze_file(file_path)

        # Build integration map
        self._build_integrations()

        # Analyze dependencies
        self._analyze_dependencies()

    def analyze_file(self, file_path: Path) -> None:
        """Analyze a single Python file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source_code = f.read()

            # Parse AST
            tree = ast.parse(source_code, filename=str(file_path))

            # Extract module name
            module_name = self._get_module_name(file_path)

            # Create visitor and analyze
            visitor = ASTVisitor(str(file_path))
            visitor.visit(tree)

            # Create module info
            module_info = ModuleInfo(
                name=module_name,
                file_path=str(file_path),
                classes=visitor.classes,
                functions=visitor.functions,
                imports=visitor.imports,
                exports=set(),
                dependencies=set()
            )

            # Store global calls
            for call, line in visitor.calls:
                self.global_calls[call].append((str(file_path), line))

            # Extract exports (public classes and functions)
            for class_name, class_info in visitor.classes.items():
                if not class_name.startswith('_'):
                    module_info.exports.add(class_name)

            for func_name, func_info in visitor.functions.items():
                if not func_name.startswith('_'):
                    module_info.exports.add(func_name)

            self.modules[module_name] = module_info

        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")

    def _get_module_name(self, file_path: Path) -> str:
        """Get module name from file path."""
        relative_path = file_path.relative_to(self.project_root)

        # Convert path to module name
        parts = []
        for part in relative_path.parts:
            if part.endswith('.py'):
                parts.append(part[:-3])
            else:
                parts.append(part)

        return '.'.join(parts)

    def _build_integrations(self) -> None:
        """Build integration map between components."""
        # Analyze inheritance relationships
        for module_name, module_info in self.modules.items():
            for class_name, class_info in module_info.classes.items():
                for base in class_info.bases:
                    # Find where base class is defined
                    for other_module, other_info in self.modules.items():
                        if base in other_info.classes or base in other_info.functions:
                            integration = IntegrationInfo(
                                from_component=f"{module_name}.{class_name}",
                                to_component=f"{other_module}.{base}",
                                interaction_type="inheritance",
                                file_path=class_info.file_path,
                                line_number=class_info.line_number,
                                context=f"{class_name} extends {base}"
                            )
                            self.integrations.append(integration)
                            break

        # Analyze method calls and imports
        for module_name, module_info in self.modules.items():
            for class_name, class_info in module_info.classes.items():
                for method in class_info.methods:
                    if method in self.global_calls:
                        for call_file, call_line in self.global_calls[method]:
                            if call_file != class_info.file_path:
                                # Cross-module call
                                call_module = self._get_module_by_file(call_file)
                                integration = IntegrationInfo(
                                    from_component=f"{call_module}",
                                    to_component=f"{module_name}.{class_name}.{method}",
                                    interaction_type="method_call",
                                    file_path=call_file,
                                    line_number=call_line,
                                    context=f"Calls {method} on {class_name}"
                                )
                                self.integrations.append(integration)

    def _analyze_dependencies(self) -> None:
        """Analyze module dependencies."""
        for module_name, module_info in self.modules.items():
            # Direct imports
            for import_name in module_info.imports:
                # Try to match imports to known modules
                for other_module in self.modules.keys():
                    if import_name in other_module:
                        module_info.dependencies.add(other_module)
                        break

            # Indirect dependencies through classes
            for class_info in module_info.classes.values():
                for base in class_info.bases:
                    for other_module, other_info in self.modules.items():
                        if base in other_info.classes:
                            module_info.dependencies.add(other_module)

    def _get_module_by_file(self, file_path: str) -> str:
        """Get module name by file path."""
        for module_name, module_info in self.modules.items():
            if module_info.file_path == file_path:
                return module_name
        return "unknown"

    def generate_documentation(self, output_path: str) -> None:
        """
        Generate comprehensive architecture documentation.

        Args:
            output_path: Path to output documentation file
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("# AI Agent Suite - Architecture Documentation\n\n")
            f.write("Automatically generated from AST analysis.\n\n")
            f.write(f"Analysis Date: {os.popen('date').read().strip()}\n\n")
            f.write(f"Total Modules: {len(self.modules)}\n")
            f.write(f"Total Classes: {sum(len(m.classes) for m in self.modules.values())}\n")
            f.write(f"Total Functions: {sum(len(m.functions) for m in self.modules.values())}\n")
            f.write(f"Total Integrations: {len(self.integrations)}\n\n")

            # Modules overview
            f.write("## 📦 Module Overview\n\n")
            for module_name, module_info in sorted(self.modules.items()):
                f.write(f"### {module_name}\n\n")
                f.write(f"**File:** `{module_info.file_path}`\n\n")

                if module_info.classes:
                    f.write("**Classes:**\n")
                    for class_name, class_info in module_info.classes.items():
                        f.write(f"- `{class_name}` ({len(class_info.methods)} methods, {len(class_info.properties)} properties)\n")
                        if class_info.docstring:
                            f.write(f"  > {class_info.docstring.split('.')[0]}.\n")
                        if class_info.bases:
                            f.write(f"  > Inherits: {', '.join(class_info.bases)}\n")
                    f.write("\n")

                if module_info.functions:
                    f.write("**Functions:**\n")
                    for func_name, func_info in module_info.functions.items():
                        complexity_indicator = "🟢" if func_info.complexity <= 5 else "🟡" if func_info.complexity <= 10 else "🔴"
                        f.write(f"- `{func_name}({', '.join(func_info.parameters)})` {complexity_indicator} (complexity: {func_info.complexity})\n")
                        if func_info.docstring:
                            f.write(f"  > {func_info.docstring.split('.')[0]}.\n")
                    f.write("\n")

                if module_info.dependencies:
                    f.write("**Dependencies:**\n")
                    for dep in sorted(module_info.dependencies):
                        f.write(f"- {dep}\n")
                    f.write("\n")

            # Integrations
            f.write("## 🔗 Component Integrations\n\n")
            for integration in self.integrations:
                f.write(f"- **{integration.interaction_type}**: `{integration.from_component}` → `{integration.to_component}`\n")
                f.write(f"  - File: `{integration.file_path}:{integration.line_number}`\n")
                f.write(f"  - Context: {integration.context}\n\n")

    def generate_mermaid_diagrams(self, output_dir: str) -> None:
        """
        Generate Mermaid diagrams for architecture visualization.

        Args:
            output_dir: Directory to save Mermaid diagrams
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Module dependency diagram
        self._generate_module_dependency_diagram(output_dir / "module_dependencies.md")

        # Class inheritance diagram
        self._generate_class_inheritance_diagram(output_dir / "class_inheritance.md")

        # Integration flow diagram
        self._generate_integration_flow_diagram(output_dir / "integration_flow.md")

        # Architecture overview diagram
        self._generate_architecture_overview_diagram(output_dir / "architecture_overview.md")

    def _generate_module_dependency_diagram(self, output_path: Path) -> None:
        """Generate module dependency diagram."""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("# Module Dependencies\n\n")
            f.write("```mermaid\ngraph TD\n")

            # Create subgraph for each package
            packages = defaultdict(list)
            for module_name in self.modules.keys():
                package = module_name.split('.')[0] if '.' in module_name else module_name
                packages[package].append(module_name)

            for package, modules in packages.items():
                f.write(f"    subgraph {package}\n")
                for module in modules:
                    safe_name = module.replace('.', '_').replace('-', '_')
                    display_name = module.split('.')[-1]
                    f.write(f"        {safe_name}[{display_name}]\n")
                f.write("    end\n\n")

            # Add edges
            for module_name, module_info in self.modules.items():
                source_safe = module_name.replace('.', '_').replace('-', '_')
                for dep in module_info.dependencies:
                    target_safe = dep.replace('.', '_').replace('-', '_')
                    f.write(f"    {source_safe} --> {target_safe}\n")

            f.write("```\n")

    def _generate_class_inheritance_diagram(self, output_path: Path) -> None:
        """Generate class inheritance diagram."""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("# Class Inheritance\n\n")
            f.write("```mermaid\ngraph TD\n")

            # Add all classes
            for module_name, module_info in self.modules.items():
                for class_name, class_info in module_info.classes.items():
                    safe_class = f"{module_name}_{class_name}".replace('.', '_')
                    label = f"{class_name}<br/><small>{module_name}</small>"
                    f.write(f"    {safe_class}(\"{label}\")\n")

            f.write("\n")

            # Add inheritance relationships
            for module_name, module_info in self.modules.items():
                for class_name, class_info in module_info.classes.items():
                    child_safe = f"{module_name}_{class_name}".replace('.', '_')
                    for base in class_info.bases:
                        # Find base class
                        for other_module, other_info in self.modules.items():
                            if base in other_info.classes:
                                parent_safe = f"{other_module}_{base}".replace('.', '_')
                                f.write(f"    {child_safe} --> {parent_safe}\n")
                                break

            f.write("```\n")

    def _generate_integration_flow_diagram(self, output_path: Path) -> None:
        """Generate integration flow diagram."""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("# Integration Flow\n\n")
            f.write("```mermaid\ngraph LR\n")

            # Add components
            components = set()
            for integration in self.integrations:
                from_comp = integration.from_component.split('.')[0]
                to_comp = integration.to_component.split('.')[0]
                components.add(from_comp)
                components.add(to_comp)

            for comp in components:
                f.write(f"    {comp}({comp})\n")

            f.write("\n")

            # Add flows
            interaction_counts = defaultdict(int)
            for integration in self.integrations:
                from_comp = integration.from_component.split('.')[0]
                to_comp = integration.to_component.split('.')[0]
                interaction_type = integration.interaction_type
                interaction_counts[(from_comp, to_comp, interaction_type)] += 1

            for (from_comp, to_comp, interaction_type), count in interaction_counts.items():
                label = f"{interaction_type}<br/>({count})" if count > 1 else interaction_type
                f.write(f"    {from_comp} --> |{label}| {to_comp}\n")

            f.write("```\n")

    def _generate_architecture_overview_diagram(self, output_path: Path) -> None:
        """Generate high-level architecture overview."""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("# Architecture Overview\n\n")
            f.write("```mermaid\ngraph TB\n")

            # Architecture layers
            f.write("    %% Input Layer\n")
            f.write("    AI_Editor[\"🤖 AI Editor<br/>Cursor/VSCode\"]\n")
            f.write("    AI_Model[\"🧠 AI Model<br/>GPT/Claude/etc.\"]\n\n")

            f.write("    %% Interface Layer\n")
            f.write("    LSP[\"🔌 LSP Server<br/>Language Server Protocol\"]\n")
            f.write("    MCP[\"🔌 MCP Server<br/>Model Context Protocol\"]\n\n")

            f.write("    %% Enterprise Layer\n")
            f.write("    Core[\"🎯 Core Engine<br/>Business Logic\"]\n")
            f.write("    Verification[\"🔒 Formal Verification<br/>Theorem Proving\"]\n")
            f.write("    Chaos[\"⚡ Chaos Engineering<br/>Failure Simulation\"]\n")
            f.write("    Patterns[\"🏗️ Enterprise Patterns<br/>CQRS/Event Sourcing\"]\n\n")

            f.write("    %% Infrastructure Layer\n")
            f.write("    Observability[\"📊 Observability Stack<br/>Prometheus/Jaeger\"]\n")
            f.write("    Database[\"💾 Database Layer<br/>PostgreSQL/Redis\"]\n")
            f.write("    Cache[\"🚀 Cache Layer<br/>Redis/Memory\"]\n\n")

            # Flow connections
            f.write("    %% Data Flow\n")
            f.write("    AI_Editor --> LSP\n")
            f.write("    AI_Model --> MCP\n")
            f.write("    LSP --> Core\n")
            f.write("    MCP --> Core\n")
            f.write("    Core --> Verification\n")
            f.write("    Core --> Chaos\n")
            f.write("    Core --> Patterns\n")
            f.write("    Verification --> Database\n")
            f.write("    Chaos --> Database\n")
            f.write("    Patterns --> Cache\n")
            f.write("    Core --> Observability\n")
            f.write("    Core --> Database\n")
            f.write("    Core --> Cache\n")

            f.write("```\n")


def main():
    """CLI entry point for architecture analysis."""
    import argparse

    parser = argparse.ArgumentParser(description="Analyze codebase architecture using AST")
    parser.add_argument("source_path", help="Path to source code directory")
    parser.add_argument("--output-docs", default="docs/ARCHITECTURE.md", help="Output documentation file")
    parser.add_argument("--output-diagrams", default="docs/diagrams", help="Output diagrams directory")
    parser.add_argument("--json-output", help="Output JSON analysis file")

    args = parser.parse_args()

    # Analyze project
    analyzer = ArchitectureAnalyzer()
    print(f"🔍 Analyzing codebase in {args.source_path}...")
    analyzer.analyze_project(args.source_path)

    # Generate documentation
    print(f"📝 Generating documentation to {args.output_docs}...")
    analyzer.generate_documentation(args.output_docs)

    # Generate diagrams
    print(f"🖼️  Generating diagrams to {args.output_diagrams}...")
    analyzer.generate_mermaid_diagrams(args.output_diagrams)

    # Save JSON if requested
    if args.json_output:
        print(f"💾 Saving JSON analysis to {args.json_output}...")
        analysis_data = {
            "modules": {
                name: {
                    "file_path": info.file_path,
                    "classes": {c_name: {
                        "name": c_info.name,
                        "line_number": c_info.line_number,
                        "bases": list(c_info.bases),
                        "methods": c_info.methods,
                        "properties": c_info.properties,
                        "decorators": c_info.decorators,
                        "docstring": c_info.docstring,
                        "dependencies": list(c_info.dependencies),
                        "integrations": list(c_info.integrations)
                    } for c_name, c_info in info.classes.items()},
                    "functions": {f_name: {
                        "name": f_info.name,
                        "line_number": f_info.line_number,
                        "parameters": f_info.parameters,
                        "decorators": f_info.decorators,
                        "docstring": f_info.docstring,
                        "complexity": f_info.complexity
                    } for f_name, f_info in info.functions.items()},
                    "imports": list(info.imports),
                    "exports": list(info.exports),
                    "dependencies": list(info.dependencies)
                } for name, info in analyzer.modules.items()
            },
            "integrations": [{
                "from_component": i.from_component,
                "to_component": i.to_component,
                "interaction_type": i.interaction_type,
                "file_path": i.file_path,
                "line_number": i.line_number,
                "context": i.context
            } for i in analyzer.integrations]
        }

        with open(args.json_output, 'w', encoding='utf-8') as f:
            json.dump(analysis_data, f, indent=2, ensure_ascii=False)

    print("✅ Architecture analysis complete!")
    print(f"📊 Analyzed {len(analyzer.modules)} modules")
    print(f"🔗 Found {len(analyzer.integrations)} integrations")
    print(f"📚 Documentation: {args.output_docs}")
    print(f"🖼️  Diagrams: {args.output_diagrams}")


if __name__ == "__main__":
    main()
