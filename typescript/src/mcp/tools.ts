/**
 * MCP Tools for AI Agent Suite
 *
 * Defines the tools available through the Model Context Protocol.
 */

import { MCPTool } from './server';

export const AIAGENTSUITE_TOOLS: MCPTool[] = [
  {
    name: 'get_constitution',
    description: 'Retrieve the master AI agent constitution that governs all AI agent behavior and decision-making processes.',
    inputSchema: {
      type: 'object',
      properties: {},
      required: []
    }
  },
  {
    name: 'list_protocols',
    description: 'List all available development protocols in the AI Agent Suite framework.',
    inputSchema: {
      type: 'object',
      properties: {},
      required: []
    }
  },
  {
    name: 'execute_protocol',
    description: 'Execute a specific protocol with given context following the VDE methodology.',
    inputSchema: {
      type: 'object',
      properties: {
        protocol_name: {
          type: 'string',
          description: 'Name of the protocol to execute'
        },
        context: {
          type: 'object',
          description: 'Context data for protocol execution',
          additionalProperties: true
        }
      },
      required: ['protocol_name']
    }
  },
  {
    name: 'get_memory_context',
    description: 'Retrieve specific context from the memory bank (active, decisions, product, progress, project, patterns).',
    inputSchema: {
      type: 'object',
      properties: {
        context_type: {
          type: 'string',
          enum: ['active', 'decisions', 'product', 'progress', 'project', 'patterns'],
          description: 'Type of context to retrieve'
        }
      },
      required: ['context_type']
    }
  },
  {
    name: 'update_memory_context',
    description: 'Update or append to memory bank context.',
    inputSchema: {
      type: 'object',
      properties: {
        context_type: {
          type: 'string',
          enum: ['active', 'decisions', 'product', 'progress', 'project', 'patterns'],
          description: 'Type of context to update'
        },
        content: {
          type: 'string',
          description: 'New content to set'
        },
        append: {
          type: 'string',
          description: 'Content to append (alternative to content)'
        }
      },
      required: ['context_type']
    }
  },
  {
    name: 'log_decision',
    description: 'Log an architectural or implementation decision to the memory bank.',
    inputSchema: {
      type: 'object',
      properties: {
        decision: {
          type: 'string',
          description: 'The decision being made'
        },
        rationale: {
          type: 'string',
          description: 'Rationale behind the decision'
        },
        context: {
          type: 'object',
          description: 'Additional context for the decision',
          additionalProperties: true
        }
      },
      required: ['decision', 'rationale']
    }
  },
  {
    name: 'get_principle',
    description: 'Retrieve a specific VDE principle (Core Philosophy, Branching Strategy, YAGNI).',
    inputSchema: {
      type: 'object',
      properties: {
        principle_name: {
          type: 'string',
          enum: ['Core Philosophy', 'Branching Strategy', 'YAGNI'],
          description: 'Name of the principle to retrieve'
        }
      },
      required: ['principle_name']
    }
  },
  {
    name: 'get_project_context',
    description: 'Retrieve the project-specific context and requirements.',
    inputSchema: {
      type: 'object',
      properties: {},
      required: []
    }
  }
];