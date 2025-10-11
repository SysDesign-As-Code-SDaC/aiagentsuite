# Multi-stage Docker build for AI Agent Suite

# Python base stage
FROM python:3.10-slim as python-base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy Python requirements
COPY requirements.txt pyproject.toml setup.py MANIFEST.in ./
COPY src/ ./src/

# Install Python dependencies
RUN pip install -e .[dev]

# TypeScript build stage
FROM node:18-slim as typescript-build

WORKDIR /app/typescript

# Copy TypeScript package files
COPY typescript/package*.json ./
COPY typescript/tsconfig.json ./
COPY typescript/src/ ./src/

# Install dependencies and build
RUN npm ci && npm run build

# Final production stage
FROM python:3.10-slim as production

# Install Node.js for runtime LSP/MCP components
RUN apt-get update && apt-get install -y \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# Create app user
RUN useradd --create-home --shell /bin/bash app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    NODE_ENV=production

# Create app directory
WORKDIR /app

# Copy Python installation from python-base
COPY --from=python-base /usr/local/lib/python3.10/site-packages/ /usr/local/lib/python3.10/site-packages/
COPY --from=python-base /usr/local/bin/ /usr/local/bin/

# Copy built TypeScript from typescript-build
COPY --from=typescript-build /app/typescript/dist/ ./typescript/dist/
COPY --from=typescript-build /app/typescript/package*.json ./typescript/

# Copy application source
COPY src/ ./src/
COPY README.md LICENSE ./

# Install production Node.js dependencies
WORKDIR /app/typescript
RUN npm ci --only=production

# Change ownership and switch to app user
WORKDIR /app
RUN chown -R app:app /app
USER app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "from aiagentsuite.core.suite import AIAgentSuite; print('Health check passed')" || exit 1

# Default command
CMD ["aiagentsuite", "--help"]