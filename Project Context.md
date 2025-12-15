# **Project Context - AiAgentSuite**

*This file provides stable, high-level details of the AiAgentSuite project to AI agents for necessary domain knowledge.*

## **1. Primary Business Objective**

**Objective**: AiAgentSuite is a comprehensive enterprise AI agent framework built to provide robust, secure, and observable agent-based solutions with strong development discipline. It is designed to be integrated into custom development tools, especially those using LSP (Language Server Protocol) or MCP (Model Context Protocol).

The goal of this repository is to allow protocols and other components to be integrated and created. In the future, this will be integrated into a "system design as code" repository.

**Key Features**:
- Automate or augment software development processes with AI agents
- Secure-by-design architecture with built-in audit logging
- Observability and tracing for all agent actions
- Extensible protocol system for complex reasoning and tasks
- Persistent memory context for stateful agents
- LSP and MCP integration for IDEs and development tools
- Strong development discipline via Vibe-Driven Engineering (VDE)

## **2. Core Technologies**

**Primary Languages**: 
- Python (core framework, protocols, memory bank)
- TypeScript (LSP extension, MCP integration)

**Frontend Framework**: 
- VS Code Extension API (via TypeScript LSP)
- MCP Client interfaces

**Backend Framework**: 
- Python core libraries (pydantic, opentelemetry, etc.)
- MCP Server implementation

**Database(s)**: 
- File-based persistence for Memory Bank (markdown/json)
- Redis (optional, for caching/distributed state)

**Key Libraries/SDKs**: 
- **Python**: Pydantic, OpenTelemetry, PyTest, Rich
- **TypeScript**: VS Code Language Server, MCP SDK
- **Security**: OWASP guidelines
- **Build**: Setuptools, npm

## **3. Architectural Style**

**Style**: Modular Framework with Protocol-Driven Architecture

**High-Level Description**: 
AiAgentSuite uses a modular architecture where core services, protocols, and integration adapters are isolated:

- **Core**: Security, observability, config, caching, error handling
- **Protocols**: DSL engine for agent reasoning and communication
- **Framework**: Organization, onboarding, testing, and philosophy
- **Memory Bank**: Persistent context management
- **LSP & MCP**: Integration adapters for external tools

## **4. Coding Standards & Conventions**

**Code Style**: 
- **Python**: PEP 8 compliance, Black formatter, type hints required
- **TypeScript**: ESLint, Prettier, strict mode

**Testing Framework**: 
- **Python**: pytest with comprehensive coverage requirements (>80%)
- **TypeScript**: Jest/Mocha for LSP/MCP tests

**Key Conventions**: 
- Follow "Secure Code Implementation" protocol
- Trunk-based branching model
- All code PR-reviewed with automated checks
- Documentation updated with code changes

## **5. Directory Structure Pointers**

**Core Components**:
- `src/aiagentsuite/core/`: Core enterprise components
- `src/aiagentsuite/protocols/`: Protocol engine and definitions
- `src/aiagentsuite/memory_bank/`: Persistent context management
- `src/aiagentsuite/framework/`: Framework logic and data

**Integration**:
- `src/aiagentsuite/lsp/`: Python-side LSP extensions
- `src/aiagentsuite/mcp/`: Python-side MCP server
- `typescript/`: TypeScript implementation for LSP/MCP

**Documentation**:
- `README.md`: Main project documentation
- `src/aiagentsuite/framework/data/`: Detailed framework docs

## **6. Security Requirements**

**Critical Security Considerations**:
- Input validation and sanitization
- Secure-by-default coding practices
- Automated security checks in CI/CD
- Audit logging for all sensitive operations

## **7. Performance Requirements**

**Performance Targets**:
- Low latency for protocol execution
- Efficient memory usage for long-running agents
- Scalable observability without significant overhead

## **8. Deployment Models**

**Supported Deployment Options**:
- Library import into Python applications
- Standalone MCP server
- VS Code Extension (via TypeScript integration)

## **9. Integration Points**

**External Integrations**:
- IDEs (VS Code, Cursor) via LSP/MCP
- Automation pipelines (CI/CD)
- "System design as code" repositories (future)

## **10. Development Workflow**

**Development Process**:
- Follow VDE (Vibe-Driven Engineering) principles
- Use protocols for complex tasks (e.g., Feature Development, Security Audit)
- Update Memory Bank with decisions and progress
- Verify changes with comprehensive tests

This context provides the foundation for AI agents to understand the AiAgentSuite project's architecture, requirements, and development standards.
