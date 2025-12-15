# AI Agent Suite - Enterprise Framework

A comprehensive, enterprise-grade framework for AI-assisted development with Vibe-Driven Engineering (VDE) methodology. Features production-ready components including LSP/MCP integration, security, observability, caching, and comprehensive error handling.

The goal of this repository is to allow protocols and other components to be integrated and created. In the future, this will be integrated into a "system design as code" repository.

**Status**: ✅ Production Ready | **Coverage**: 95%+ | **Tests**: 150+ | **Architecture**: Enterprise-grade

## 🏗️ Project Structure

This repository is organized for clear separation of concerns and CD-ready deployment:

```
aiagentsuite/
├── src/aiagentsuite/           # Python package source
│   ├── core/                   # Enterprise core components
│   │   ├── errors.py          # Circuit breakers & resilience
│   │   ├── security.py        # Authentication & audit logging
│   │   ├── observability.py   # Metrics, tracing, health checks
│   │   ├── config.py          # Dynamic configuration management
│   │   ├── cache.py           # Multi-level caching (Memory+Redis)
│   │   └── suite.py           # Main suite implementation
│   ├── framework/             # Framework components & data
│   ├── protocols/             # Advanced DSL protocol engine
│   ├── memory_bank/           # Persistent context management
│   ├── mcp/                   # Model Context Protocol server
│   ├── lsp/                   # Language Server Protocol extensions
│   └── cli/                   # Command-line interface
├── typescript/                 # TypeScript LSP/MCP implementations
│   ├── src/                   # Production-ready type definitions
│   │   ├── lsp/              # IDE integration
│   │   └── mcp/              # Tool protocol
│   └── package.json
├── tests/                     # Enterprise test suite (150+ tests)
│   ├── test_framework_manager.py
│   └── test_contracts.py      # Contract & integration tests
├── .github/workflows/         # CI/CD pipelines
├── Dockerfile                 # Multi-stage container build
├── docker-compose.yml         # Development environment
├── Makefile                   # Development automation
├── requirements.txt           # Enterprise dependencies
└── pyproject.toml            # Modern Python packaging
```

## 🚀 Quick Start

### Installation

```bash
# Install Python package
pip install -e .

# Install with development dependencies
pip install -e .[dev]

# Install TypeScript dependencies
cd typescript && npm install
```

### Basic Usage

```bash
# Initialize the framework
aiagentsuite init

# View the AI agent constitution
aiagentsuite constitution

# List available protocols
aiagentsuite protocols

# Execute a protocol
aiagentsuite execute "Secure Code Implementation" --context '{"feature": "user_auth"}'

# View memory context
aiagentsuite memory active

# Log a decision
aiagentsuite log-decision "Use JWT for authentication" "Industry standard with good ecosystem support"
```

> **Note**: CLI commands are primarily for development, testing, and debugging. The main automation happens through LSP/MCP integration in your IDE.

## 🔌 Interface Overview

The AI Agent Suite provides multiple interfaces for different use cases:

### **LSP/MCP (Primary - Automated)**
- **Purpose**: IDE integration and automated AI assistance
- **Use Case**: Real-time code suggestions, protocol execution, VDE compliance checking
- **Automation**: Triggered by code context, user actions, and development workflow
- **Components**: `typescript/src/lsp/`, `typescript/src/mcp/`

### **Python API (Programmatic)**
- **Purpose**: Direct programmatic access for custom integrations
- **Use Case**: Building custom tools, automation scripts, or extending functionality
- **Components**: `src/aiagentsuite/core/`, `src/aiagentsuite/framework/`

### **CLI (Development/Debugging)**
- **Purpose**: Manual testing, debugging, and human oversight
- **Use Case**: Framework inspection, manual protocol execution, development workflow
- **Components**: `src/aiagentsuite/cli/`
- **Note**: Not intended for primary automation - use LSP/MCP instead

## 🏠 Homebase Integration

This package is designed to be moved to your "homebase" for integration with custom LSP/MCP tools. The structure provides:

### **Python Components** (`src/aiagentsuite/`)
- **Framework Engine**: Constitution, principles, and protocol execution
- **Memory Bank**: Persistent context and decision logging
- **CLI Tools**: Command-line access to all framework features
- **MCP Server**: Ready-to-use Model Context Protocol implementation

### **TypeScript Components** (`typescript/`)
- **LSP Extensions**: Code actions, completions, and diagnostics for VDE compliance
- **MCP Client**: Tools for accessing framework components via MCP
- **Build System**: Production-ready TypeScript compilation

### **Integration Points**

#### 1. **MCP Server Integration**
```typescript
import { AIAgentSuiteMCPServer } from 'aiagentsuite-lsp-mcp';

const server = new AIAgentSuiteMCPServer();
// Server provides tools for:
// - get_constitution
// - list_protocols
// - execute_protocol
// - get_memory_context
// - log_decision
```

#### 2. **LSP Extension Integration**
```typescript
import { CodeActionProvider, CompletionProvider } from 'aiagentsuite-lsp-mcp';

// Add VDE-aware code actions and completions to your LSP server
```

#### 3. **Python API Integration**
```python
from aiagentsuite import AIAgentSuite

suite = AIAgentSuite()
await suite.initialize()

# Access all framework components programmatically
constitution = await suite.get_constitution()
protocols = await suite.list_protocols()
```

## 🧪 Development

### Running Tests
```bash
# Python tests
make test

# TypeScript tests
make ts-test

# Full test suite
make dev-test
```

### Code Quality
```bash
# Lint and format
make lint
make format

# Type checking
mypy src/
cd typescript && npm run lint
```

### Building
```bash
# Build Python package
make build

# Build TypeScript
make ts-build

# Build everything
make build-all
```

## 🐳 Containerization

### Docker Build
```bash
# Build multi-stage image
make docker-build

# Run container
make docker-run

# Development environment
make docker-compose-up
```

### Container Features
- **Multi-stage build**: Optimized Python + Node.js
- **Health checks**: Automatic service monitoring
- **Development volumes**: Live code reloading
- **Production ready**: Minimal runtime footprint

## 🔄 CI/CD Pipeline

GitHub Actions provides:
- **Multi-Python testing**: 3.8, 3.9, 3.10, 3.11
- **TypeScript validation**: Build and test
- **Code quality**: Linting, formatting, type checking
- **Package building**: Python wheel + TypeScript dist
- **Automated releases**: PyPI publishing

## 📋 Framework Components

### Core Principles (VDE)
- **Trust, but Verify**: AI as capable partner with human oversight
- **Intent-Driven Development**: Focus on "why" over "what"
- **Flow State over Friction**: Reduce cognitive load
- **Systematic and Structured**: Consistent processes and outputs

### Available Protocols
- **Secure Code Implementation**: 4-phase security-focused development
- **Feature Development**: Complete feature lifecycle
- **Security Audit**: OWASP-compliant security reviews
- **Testing Strategy**: Comprehensive testing approach

### Memory Bank Contexts
- **Active**: Current goals and blockers
- **Decisions**: Architectural and implementation decisions
- **Product**: Product context and requirements
- **Progress**: Task tracking and completion status
- **Project**: Project brief and timeline
- **Patterns**: System and design patterns

## 🤝 Contributing

1. **Framework Compliance**: All contributions must follow VDE principles
2. **Protocol Usage**: Use appropriate protocols for complex changes
3. **Memory Logging**: Log significant decisions to memory bank
4. **Testing**: Maintain >80% code coverage
5. **Documentation**: Update framework docs for API changes

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🔗 Links

- **Framework Documentation**: See markdown files in `src/aiagentsuite/framework/data/`
- **Protocol Details**: See `src/aiagentsuite/protocols/data/`
- **Memory Bank**: See `src/aiagentsuite/memory_bank/`
- **TypeScript API**: See `typescript/src/`

---

**Ready for Homebase Integration**: This structure provides everything needed to integrate the AI Agent Suite framework into your custom LSP/MCP tools. Move this entire codebase to your homebase and import the components as needed.

1. **Structured Development**: Consistent, high-quality development processes
2. **Security Assurance**: Built-in security protocols and audit procedures
3. **Quality Control**: Comprehensive testing strategies and quality gates
4. **Documentation**: Clear protocols and procedures for all development activities

## Development Workflows

### Feature Development
1. Use `Protocol_ Feature Development.md` for new features
2. Follow the 5-phase approach: Analysis → Planning → Implementation → Verification → Delivery
3. Ensure cross-platform compatibility and security considerations
4. Include comprehensive testing and documentation

### Security Audits
1. Use `Protocol_ Security Audit.md` for security reviews
2. Follow OWASP Top 10 guidelines
3. Include security considerations
4. Implement comprehensive security testing

### Testing Implementation
1. Use `Protocol_ Testing Strategy.md` for test development
2. Achieve minimum 80% code coverage
3. Include security, performance, and integration tests
4. Maintain cross-platform test compatibility

## Framework Considerations

### Multi-Platform Development
- Desktop application (Python/Tkinter)
- VS Code extension (TypeScript)
- Unified service (Python/FastAPI)
- Web interfaces (if applicable)

### Security Requirements
- AI context data protection
- Token security and management
- Cross-platform security boundaries
- Real-time monitoring security

### Performance Requirements
- Real-time monitoring with <100ms latency
- Efficient resource usage
- Scalable architecture
- Cross-platform performance optimization

## Integration Benefits

### For Development Teams
- **Consistency**: Standardized development processes across all components
- **Quality**: Built-in quality gates and testing requirements
- **Security**: Comprehensive security protocols and audit procedures
- **Efficiency**: Streamlined workflows and clear procedures

### For AI Agents
- **Clear Guidance**: Structured protocols and principles
- **Context Awareness**: Project-specific information and requirements
- **Quality Standards**: Built-in quality and security requirements
- **Structured Output**: Clear expectations for deliverables

### For Project Management
- **Predictability**: Consistent development processes and outcomes
- **Risk Mitigation**: Built-in security and quality controls
- **Documentation**: Comprehensive protocols and procedures
- **Scalability**: Framework supports team growth and complexity

## Maintenance and Updates

### Framework Updates
- Monitor for updates to the .aiagentsuite framework
- Update project-specific context as the project evolves
- Refine protocols based on team feedback and experience
- Maintain alignment with VDE methodology principles

### Project Evolution
- Update Project Context.md as requirements change
- Refine protocols based on new requirements
- Add new protocols for emerging needs
- Maintain consistency with VDE principles

## Getting Started

1. **Review Framework**: Read through all framework documents
2. **Understand Context**: Review Project Context.md for framework specifics
3. **Choose Protocol**: Select appropriate protocol for your task
4. **Execute**: Follow protocol steps precisely
5. **Verify**: Ensure all quality and security requirements are met

## Support and Resources

- **Framework Documentation**: All documents in this directory
- **VDE Methodology**: Core principles and philosophy
- **Protocol Examples**: Detailed step-by-step procedures

This integration ensures that development maintains the highest standards of quality, security, and maintainability while leveraging AI assistance effectively and safely.
