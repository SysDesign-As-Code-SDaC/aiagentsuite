# ContextGuard - Comprehensive Dependency Map

## Overview
This document provides a complete dependency map of the ContextGuard codebase, showing relationships between components, external dependencies, and architectural layers.

## Architecture Layers

```
┌─────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                       │
├─────────────────────────────────────────────────────────────┤
│  VS Code Extension (TypeScript)  │  Desktop App (Python)    │
│  - extension.ts                  │  - main.py               │
│  - ContextGuardService           │  - enhanced_main.py      │
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
│  - ContextGuard endpoints       │  - Agent Manager          │
│  - Memory management            │  - Archimedes System      │
│  - Context drift analysis       │  - Neuromorphic Engine    │
│  - RAG processing               │  - HAL Client             │
│                                 │  - Orchestrator Client    │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                    CORE LAYER                               │
├─────────────────────────────────────────────────────────────┤
│  ContextGuard Core (Python)     │  Protocol Servers         │
│  - guard.py                     │  - MCP Protocol           │
│  - ContextGuard class           │  - LSP Protocol           │
│  - Memory management            │  - Unix Socket IPC        │
│  - Context tracking             │  - Shared memory          │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                    DATA LAYER                               │
├─────────────────────────────────────────────────────────────┤
│  Local Storage                  │  External Services        │
│  - SQLite (development)         │  - TokenGuard             │
│  - PostgreSQL (production)      │  - HAL (Windows ML)       │
│  - In-memory cache              │  - Orchestrator           │
│  - Configuration files          │  - AI Models              │
└─────────────────────────────────────────────────────────────┘
```

## Component Dependencies

### 1. Core Components

#### `src/contextguard/guard.py`
- **Dependencies**: None (base class)
- **Dependents**: 
  - `src/contextguard/server.py`
  - `src/unified_service/main.py`
  - `tests/test_guard.py`
- **Purpose**: Core context management and memory storage
- **Key Methods**: `add_to_memory()`, `get_from_memory()`, `clear_memory()`, `memory_snapshot()`

#### `src/contextguard/server.py`
- **Dependencies**: 
  - `fastapi` (web framework)
  - `pydantic` (data validation)
  - `requests` (HTTP client)
  - `src/contextguard/guard.py` (ContextGuard class)
- **Dependents**: 
  - `src/unified_service/main.py`
  - `tests/test_server.py`
- **Purpose**: FastAPI web server with REST endpoints
- **Key Endpoints**: `/memory`, `/analyze`, `/rag`, `/neuromorphic-analysis`

#### `src/contextguard/mcp_server.py`
- **Dependencies**: 
  - `src/contextguard/guard.py`
  - MCP protocol libraries
- **Dependents**: `src/unified_service/main.py`
- **Purpose**: Model Context Protocol server implementation

### 2. Unified Service Components

#### `src/unified_service/main.py`
- **Dependencies**: 
  - `fastapi`, `uvicorn` (web server)
  - `pydantic` (data models)
  - `yaml` (configuration)
  - `src/contextguard/guard.py`
  - `src/contextguard/server.py`
  - All unified service modules
- **Dependents**: `tests/test_unified_service.py`
- **Purpose**: Main unified service orchestrator
- **Key Features**: Agent management, protocol servers, IPC

#### `src/unified_service/models.py`
- **Dependencies**: 
  - `pydantic` (data models)
  - `datetime`, `uuid` (utilities)
- **Dependents**: 
  - `src/unified_service/main.py`
  - `src/unified_service/agent_manager.py`
- **Purpose**: Data models and schemas

#### `src/unified_service/agent_manager.py`
- **Dependencies**: 
  - `src/unified_service/models.py`
  - `datetime`, `uuid` (utilities)
- **Dependents**: `src/unified_service/main.py`
- **Purpose**: Agent lifecycle management

#### `src/unified_service/archimedes.py`
- **Dependencies**: 
  - `asyncio` (async operations)
  - `logging` (logging)
- **Dependents**: `src/unified_service/main.py`
- **Purpose**: Metacognitive prompt system

#### `src/unified_service/neuromorphic_engine.py`
- **Dependencies**: 
  - `asyncio` (async operations)
  - `logging` (logging)
- **Dependents**: `src/unified_service/main.py`
- **Purpose**: Neuromorphic compression engine

#### `src/unified_service/hal_client.py`
- **Dependencies**: 
  - `httpx` (HTTP client)
  - `asyncio` (async operations)
- **Dependents**: `src/unified_service/main.py`
- **Purpose**: HAL (Windows ML) client integration

#### `src/unified_service/orchestrator_client.py`
- **Dependencies**: 
  - `httpx` (HTTP client)
  - `asyncio` (async operations)
- **Dependents**: `src/unified_service/main.py`
- **Purpose**: Orchestrator service client

#### `src/unified_service/ipc.py`
- **Dependencies**: 
  - `asyncio` (async operations)
  - `socket` (Unix sockets)
  - `multiprocessing` (shared memory)
- **Dependents**: `src/unified_service/main.py`
- **Purpose**: Inter-process communication

#### `src/unified_service/lsp_protocol.py`
- **Dependencies**: 
  - `asyncio` (async operations)
  - LSP protocol libraries
- **Dependents**: `src/unified_service/main.py`
- **Purpose**: Language Server Protocol implementation

#### `src/unified_service/mcp_protocol.py`
- **Dependencies**: 
  - `asyncio` (async operations)
  - MCP protocol libraries
- **Dependents**: `src/unified_service/main.py`
- **Purpose**: Model Context Protocol implementation

### 3. Desktop Application Components

#### `src/desktop_app/main.py`
- **Dependencies**: 
  - `tkinter` (GUI framework)
  - `threading` (multithreading)
  - `requests` (HTTP client)
- **Dependents**: `tests/test_desktop_app.py`
- **Purpose**: Main desktop application

#### `src/desktop_app/enhanced_main.py`
- **Dependencies**: 
  - `tkinter` (GUI framework)
  - `threading` (multithreading)
  - `requests` (HTTP client)
- **Dependents**: `tests/test_desktop_app.py`
- **Purpose**: Enhanced desktop application with advanced features

#### `src/desktop_app/simple_main.py`
- **Dependencies**: 
  - `tkinter` (GUI framework)
  - `threading` (multithreading)
- **Dependents**: `tests/test_desktop_app.py`
- **Purpose**: Simplified desktop application

#### `src/desktop_app/simple_monitor.py`
- **Dependencies**: 
  - `tkinter` (GUI framework)
  - `threading` (multithreading)
- **Dependents**: `tests/test_desktop_app.py`
- **Purpose**: Simple monitoring application

#### `src/desktop_app/auto_start.py`
- **Dependencies**: 
  - `tkinter` (GUI framework)
  - `threading` (multithreading)
- **Dependents**: `tests/test_desktop_app.py`
- **Purpose**: Auto-start functionality

### 4. VS Code Extension Components

#### `contextguard-preview/src/extension.ts`
- **Dependencies**: 
  - `vscode` (VS Code API)
  - `./services/ContextGuardService`
  - `./services/EnhancedContextTracker`
- **Dependents**: None (entry point)
- **Purpose**: Main extension entry point

#### `contextguard-preview/src/services/ContextGuardService.ts`
- **Dependencies**: 
  - `vscode` (VS Code API)
  - `./clients/ContextGuardClient`
- **Dependents**: 
  - `contextguard-preview/src/extension.ts`
  - `tests/ContextGuardService.test.ts`
- **Purpose**: ContextGuard service integration

#### `contextguard-preview/src/services/EnhancedContextTracker.ts`
- **Dependencies**: 
  - `vscode` (VS Code API)
  - `./services/ContextGuardService`
- **Dependents**: 
  - `contextguard-preview/src/extension.ts`
  - `tests/EnhancedContextTracker.test.ts`
- **Purpose**: Enhanced context tracking

#### `contextguard-preview/src/clients/ContextGuardClient.ts`
- **Dependencies**: 
  - HTTP client libraries
- **Dependents**: 
  - `contextguard-preview/src/services/ContextGuardService.ts`
  - `tests/ContextGuardClient.test.ts`
- **Purpose**: HTTP client for backend communication

#### `contextguard-preview/src/ast-detector/`
- **Dependencies**: 
  - `web-tree-sitter` (AST parsing)
  - Language grammars (WASM files)
- **Dependents**: 
  - `contextguard-preview/src/services/`
  - `tests/ast-analysis.test.ts`
- **Purpose**: Abstract Syntax Tree analysis

#### `contextguard-preview/src/bias-detector/`
- **Dependencies**: 
  - Bias detection algorithms
  - Math algorithms
- **Dependents**: 
  - `contextguard-preview/src/services/`
  - `tests/bias-detection.test.ts`
- **Purpose**: Bias detection and analysis

### 5. Utility Components

#### `src/context_tracker.py`
- **Dependencies**: 
  - `threading` (multithreading)
  - `time` (timing)
- **Dependents**: Various components
- **Purpose**: Context tracking utilities

## External Dependencies

### Python Dependencies (requirements.txt)
- **Web Framework**: `fastapi>=0.104.0`, `uvicorn[standard]>=0.24.0`
- **Data Validation**: `pydantic>=2.0.0`
- **HTTP Client**: `httpx>=0.25.0`, `requests>=2.31.0`
- **File Handling**: `python-multipart>=0.0.6`, `aiofiles>=23.0.0`
- **Configuration**: `python-dotenv>=1.0.0`
- **Logging**: `structlog>=23.0.0`
- **Scientific Computing**: `numpy>=1.21.0`

### TypeScript Dependencies (package.json)
- **VS Code API**: `@types/vscode: ^1.80.0`
- **Testing**: `@types/jest: ^30.0.0`, `jest: ^30.2.0`
- **Linting**: `@typescript-eslint/eslint-plugin: ^8.42.0`
- **Build Tools**: `webpack: ^5.101.3`, `typescript: ^5.9.2`
- **AST Parsing**: `web-tree-sitter: ^0.25.9`

### Build Dependencies
- **Python**: `PyInstaller` (executable generation)
- **TypeScript**: `webpack`, `ts-loader` (bundling)
- **Testing**: `pytest` (Python), `Jest` (TypeScript)

## Data Flow Dependencies

### 1. Context Flow
```
User Input → VS Code Extension → ContextGuardService → Backend API → ContextGuard Core → Memory Storage
```

### 2. Analysis Flow
```
Code Changes → AST Detector → Bias Detector → Analysis Service → Context Drift Analysis → Recommendations
```

### 3. Communication Flow
```
VS Code Extension ↔ HTTP API ↔ FastAPI Server ↔ ContextGuard Core ↔ Memory/Storage
Desktop App ↔ HTTP API ↔ FastAPI Server ↔ ContextGuard Core ↔ Memory/Storage
Unified Service ↔ IPC ↔ Protocol Servers ↔ External Services
```

## Configuration Dependencies

### Configuration Files
- `config/unified_service.yaml` - Unified service configuration
- `contextguard-preview/package.json` - Extension configuration
- `requirements.txt` - Python dependencies
- `requirements.simple.txt` - Simple service dependencies
- `requirements.unified.txt` - Unified service dependencies

### Build Configuration
- `tsconfig.json` - TypeScript configuration
- `webpack.config.js` - Webpack bundling configuration
- `jest.config.js` - Jest testing configuration
- `eslint.config.mjs` - ESLint configuration

## Testing Dependencies

### Python Tests
- `tests/conftest.py` - pytest configuration
- `tests/test_*.py` - Individual test modules
- **Dependencies**: `pytest`, test fixtures, mock objects

### TypeScript Tests
- `contextguard-preview/tests/*.test.ts` - Jest test modules
- `contextguard-preview/tests/setup.ts` - Test setup
- **Dependencies**: `Jest`, `@types/jest`, test utilities

## Deployment Dependencies

### Executable Generation
- `build_exe.py` - PyInstaller build script
- `build_simple_exe.py` - Simple executable build
- `build_fixed_exe.py` - Fixed executable build
- **Dependencies**: `PyInstaller`, build configurations

### Docker Deployment
- `Dockerfile` - Main Docker configuration
- `Dockerfile.simple` - Simple service Docker
- `Dockerfile.unified` - Unified service Docker
- `docker-compose.*.yml` - Docker Compose configurations

### Kubernetes Deployment
- `k8s/deployment.yaml` - Kubernetes deployment
- `k8s/service.yaml` - Kubernetes service
- `k8s/configmap.yaml` - Kubernetes configuration

## Security Dependencies

### Input Validation
- All user inputs validated through Pydantic models
- AST parsing for code analysis
- Bias detection algorithms

### Communication Security
- HTTPS for external communications
- Unix domain sockets for local IPC
- Secure memory management

## Performance Dependencies

### Caching
- In-memory caching for real-time operations
- Shared memory for IPC
- Database connection pooling

### Optimization
- Neuromorphic compression engine
- Token optimization (TokenGuard integration)
- Async/await patterns for non-blocking operations

This dependency map provides a comprehensive view of how all ContextGuard components interact and depend on each other, enabling better understanding of the system architecture and facilitating maintenance and development.
