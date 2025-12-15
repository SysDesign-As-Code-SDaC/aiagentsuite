# AiAgentSuite - Comprehensive Dependency Map

**Last Updated**: 2025-05-20
**Version**: 2.1.0
**Status**: Production

This document provides a complete dependency map of the AiAgentSuite codebase, showing relationships between components, external dependencies, and architectural layers.

## 🎯 High-Level Architecture

The system follows a multi-platform microservices architecture with a unified service layer:

```
┌─────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                       │
├─────────────────────────────────────────────────────────────┤
│  VS Code Extension (TypeScript)  │  Desktop App (Python)    │
│  - extension.ts                  │  - main.py               │
│  - AiAgentSuiteService           │  - enhanced_main.py      │
│  - EnhancedContextTracker        │  - simple_main.py        │
│  - AST Detector                  │  - auto_start.py         │
│  - Bias Detector                 │  - simple_monitor.py     │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                    API LAYER                                │
├─────────────────────────────────────────────────────────────┤
│  FastAPI Server (Python)        │  Unified Service (Python) │
│  - server.py                    │  - main.py                │
│  - AiAgentSuite endpoints       │  - Agent Manager          │
│  - Memory management            │  - Archimedes System      │
│  - Context drift analysis       │  - Neuromorphic Engine    │
│  - RAG processing               │  - HAL Client             │
│                                 │  - Orchestrator Client    │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                    CORE LAYER                                │
├─────────────────────────────────────────────────────────────┤
│  AiAgentSuite Core (Python)     │  Protocol Servers         │
│  - guard.py                     │  - MCP Protocol           │
│  - AiAgentSuite class           │  - LSP Protocol           │
│  - Memory management            │  - Unix Socket IPC        │
│  - Context tracking             │  - Shared memory          │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                    DATA LAYER                               │
├─────────────────────────────────────────────────────────────┤
│  Storage & Persistence                                      │
│  - SQLite / PostgreSQL                                      │
│  - JSON Logs                                                │
│  - Vector Store (RAG)                                       │
└─────────────────────────────────────────────────────────────┘
```

## 📦 Component Dependencies

### 1. Core Library (`src/aiagentsuite/`)
**Dependencies**:
- `pydantic`: Data validation
- `psutil`: System resource monitoring
- `aiohttp`: Async HTTP requests
- `python-jose`: JWT token handling
- `passlib`: Password hashing
- `numpy`: Numerical operations (bias detection)

**Key Files**:
- `src/aiagentsuite/core/security.py`: Security implementation
- `src/aiagentsuite/core/observability.py`: Metrics and tracing
- `src/aiagentsuite/protocols/`: Protocol definitions

### 2. Desktop Application (`src/desktop_app/`)
**Dependencies**:
- `tkinter`: GUI framework
- `src.aiagentsuite`: Core library
- `requests`: HTTP client
- `sv_ttk`: Modern UI theme

**Key Files**:
- `src/desktop_app/main.py`: Entry point
- `src/desktop_app/gui.py`: UI implementation
- `src/desktop_app/monitor.py`: Monitoring logic

### 3. VS Code Extension (`typescript/`)
**Dependencies**:
- `vscode`: VS Code API
- `axios`: HTTP client
- `ws`: WebSocket client
- `tree-sitter`: AST parsing

**Key Files**:
- `typescript/src/extension.ts`: Entry point
- `typescript/src/lsp/server.ts`: Language Server
- `typescript/src/mcp/server.ts`: MCP Server

### 4. Unified Service (`src/unified_service/`)
**Dependencies**:
- `fastapi`: Web framework
- `uvicorn`: ASGI server
- `sqlalchemy`: ORM
- `src.aiagentsuite`: Core library

**Key Files**:
- `src/unified_service/main.py`: Service entry point
- `src/unified_service/api.py`: API endpoints

## 🔄 Data Flow Dependencies

### 1. Context Tracking Flow
1. **Source**: VS Code Extension / Desktop App
2. **Transport**: HTTP / WebSocket
3. **Processing**: Unified Service / Core Library
4. **Analysis**: Bias Detection / Security Check
5. **Storage**: Database / Logs

### 2. Protocol Execution Flow
1. **Trigger**: LSP Code Action / MCP Tool Call
2. **Execution**: Protocol Engine (`src/aiagentsuite/protocols/`)
3. **Context**: Memory Bank (`src/aiagentsuite/memory_bank/`)
4. **Result**: Returned to Client

## 🛠️ Build & Configuration Dependencies

### Python Build
- `pyproject.toml`: Build configuration
- `setup.py`: Legacy build script
- `requirements.txt`: Runtime dependencies
- `requirements-dev.txt`: Development dependencies

### TypeScript Build
- `typescript/package.json`: NPM dependencies
- `typescript/tsconfig.json`: TypeScript configuration

### Docker Build
- `Dockerfile`: Multi-stage build definition
- `docker-compose.yml`: Service orchestration

## 🔗 External Service Dependencies
- **OpenAI API** (Optional): For advanced context analysis
- **Anthropic API** (Optional): For protocol assistance
- **PostgreSQL**: Production database
- **Redis**: Caching layer

This dependency map provides a comprehensive view of how all AiAgentSuite components interact and depend on each other, enabling better understanding of the system architecture and facilitating maintenance and development.
