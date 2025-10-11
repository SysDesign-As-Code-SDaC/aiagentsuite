# **Project Context - ContextGuard**

*This file provides stable, high-level details of the ContextGuard project to AI agents for necessary domain knowledge.*

## **1. Primary Business Objective**

**Objective**: ContextGuard is a comprehensive AI context monitoring and security system that tracks, analyzes, and protects AI interactions across multiple platforms. The system provides real-time monitoring, security threat detection, token usage optimization, and bias detection across VS Code extensions, desktop applications, and web services.

**Key Features**:
- Real-time AI context monitoring and analysis
- Security threat detection and prevention (OWASP compliance)
- Multi-platform support (VS Code extension, desktop app, web services)
- Token usage tracking and optimization
- Bias detection and mitigation
- Unified service architecture for centralized management
- Desktop monitoring for local development environments

## **2. Core Technologies**

**Primary Languages**: 
- Python (backend services, desktop app, core library)
- TypeScript (VS Code extension, web interfaces)
- JavaScript (legacy components, build scripts)

**Frontend Framework**: 
- VS Code Extension API with TypeScript
- Desktop App using Python Tkinter
- Web interfaces (if applicable)

**Backend Framework**: 
- Python FastAPI for REST APIs
- Flask for legacy services
- Unified service architecture

**Database(s)**: 
- SQLite for local/development storage
- PostgreSQL for production deployments
- In-memory caching for real-time operations

**Key Libraries/SDKs**: 
- **Python**: FastAPI, SQLAlchemy, Pydantic, PyInstaller, pytest
- **TypeScript**: VS Code API, Tree-sitter (AST parsing), Jest
- **Security**: OWASP guidelines, input validation libraries
- **Build**: PyInstaller for executables, Webpack for extension

## **3. Architectural Style**

**Style**: Microservices with unified service architecture

**High-Level Description**: 
ContextGuard uses a modular microservices architecture where each component can run independently or as part of a unified service:

- **Core Library** (`src/contextguard/`): Shared Python library with core functionality
- **Desktop App** (`src/desktop_app/`): Local monitoring application for development environments
- **VS Code Extension** (`contextguard-preview/`): IDE integration for real-time monitoring
- **Unified Service** (`src/unified_service/`): Centralized service combining all components
- **Web Services**: REST APIs for centralized management and monitoring

The architecture supports both distributed and unified deployment models, allowing flexibility for different use cases.

## **4. Coding Standards & Conventions**

**Code Style**: 
- **Python**: PEP 8 compliance, Black formatter, type hints required for all functions
- **TypeScript**: ESLint configuration, Prettier formatting, strict mode enabled
- **JavaScript**: ESLint with consistent formatting rules

**Testing Framework**: 
- **Python**: pytest with comprehensive coverage requirements (>80%)
- **TypeScript**: Jest for unit and integration tests
- **Integration**: End-to-end testing for cross-platform functionality

**Key Conventions**: 
- All functions must have comprehensive docstrings (Python) or TSDoc (TypeScript)
- Security-first approach: all user inputs must be validated and sanitized
- Comprehensive error handling with structured logging
- Conventional commits for all changes (feat, fix, docs, etc.)
- No sensitive data in logs, error messages, or configuration files
- Regular dependency updates and security patches

## **5. Directory Structure Pointers**

**Core Components**:
- `src/contextguard/`: Core Python library with shared functionality
- `src/desktop_app/`: Desktop monitoring application
- `src/unified_service/`: Unified service implementation
- `contextguard-preview/`: VS Code extension source code

**Configuration & Build**:
- `config/`: Configuration files for different deployment modes
- `build/`: PyInstaller build artifacts
- `dist/`: Final executable distributions

**Testing & Quality**:
- `tests/`: Comprehensive test suite covering all components
- `contextguard-preview/tests/`: Extension-specific tests
- `contextguard-preview/coverage/`: Test coverage reports

**Documentation**:
- `README.md`: Main project documentation
- `BUILD_INSTRUCTIONS.md`: Build and deployment instructions
- `IMPLEMENTATION_SUMMARY.md`: Technical implementation details

## **6. Security Requirements**

**Critical Security Considerations**:
- All AI interaction data must be handled securely
- No sensitive information in logs or error messages
- Secure token storage and transmission
- Input validation for all external data sources
- Regular security audits and vulnerability assessments
- OWASP Top 10 compliance for all web interfaces

## **7. Performance Requirements**

**Performance Targets**:
- Real-time monitoring with <100ms latency
- Efficient token usage tracking without performance impact
- Scalable architecture supporting multiple concurrent users
- Resource optimization for desktop applications
- Minimal memory footprint for VS Code extension

## **8. Deployment Models**

**Supported Deployment Options**:
- **Local Development**: Desktop app for individual developers
- **Team Environment**: Unified service for team-wide monitoring
- **Enterprise**: Centralized web services with database backend
- **Portable**: Standalone executables for offline use

## **9. Integration Points**

**External Integrations**:
- VS Code Extension API for IDE integration
- AI service APIs for context analysis
- Database connections for persistent storage
- Web APIs for centralized management
- File system monitoring for local development

## **10. Development Workflow**

**Development Process**:
- Feature branches for all development work
- Pull request reviews required for all changes
- Automated testing on all commits
- Security review for sensitive changes
- Documentation updates for all new features
- Regular dependency updates and security patches

This context provides the foundation for AI agents to understand the ContextGuard project's architecture, requirements, and development standards when working on any component of the system.