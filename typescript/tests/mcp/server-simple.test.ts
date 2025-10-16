/**
 * Simple tests for AI Agent Suite MCP Server
 */

import { AIAgentSuiteMCPServer } from '../../src/mcp/server';

describe('MCP Server', () => {
  let server: AIAgentSuiteMCPServer;

  beforeEach(() => {
    server = new AIAgentSuiteMCPServer();
  });

  describe('Server Initialization', () => {
    test('should create server instance', () => {
      expect(server).toBeInstanceOf(AIAgentSuiteMCPServer);
    });

    test('should have required tools', () => {
      const tools = server.listTools();

      expect(tools).toHaveLength(5);
      expect(tools.map((tool: any) => tool.name)).toEqual([
        'get_constitution',
        'list_protocols',
        'execute_protocol',
        'get_memory_context',
        'log_decision'
      ]);
    });

    test('should have proper tool schemas', () => {
      const tools = server.listTools();

      tools.forEach((tool: any) => {
        expect(tool).toHaveProperty('name');
        expect(tool).toHaveProperty('description');
        expect(tool).toHaveProperty('inputSchema');
        expect(typeof tool.name).toBe('string');
        expect(typeof tool.description).toBe('string');
        expect(typeof tool.inputSchema).toBe('object');
      });
    });
  });

  describe('Tool Execution', () => {
    test('should execute get_constitution tool', async () => {
      const result = await server.callTool('get_constitution', {});

      expect(result).toHaveProperty('content');
      expect(result.content).toHaveLength(1);
      expect(result.content[0]).toHaveProperty('type', 'text');
      expect(result.content[0]).toHaveProperty('text');
    });

    test('should execute list_protocols tool', async () => {
      const result = await server.callTool('list_protocols', {});

      expect(result).toHaveProperty('content');
      expect(result.content).toHaveLength(1);
      expect(result.content[0]).toHaveProperty('type', 'json');
      expect(result.content[0]).toHaveProperty('json');
      expect(result.content[0].json).toHaveProperty('protocols');
    });

    test('should execute execute_protocol tool', async () => {
      const result = await server.callTool('execute_protocol', {
        protocol_name: 'Test Protocol',
        context: { project: 'test' }
      });

      expect(result).toHaveProperty('content');
      expect(result.content).toHaveLength(1);
      expect(result.content[0]).toHaveProperty('type', 'json');
      expect(result.content[0].json).toHaveProperty('protocol', 'Test Protocol');
    });

    test('should execute get_memory_context tool', async () => {
      const result = await server.callTool('get_memory_context', {
        context_type: 'active'
      });

      expect(result).toHaveProperty('content');
      expect(result.content).toHaveLength(1);
      expect(result.content[0]).toHaveProperty('type', 'text');
      expect(result.content[0].text).toContain('active context');
    });

    test('should execute log_decision tool', async () => {
      const result = await server.callTool('log_decision', {
        decision: 'Use FastAPI for backend',
        rationale: 'Excellent performance and documentation',
        context: { project: 'test' }
      });

      expect(result).toHaveProperty('content');
      expect(result.content).toHaveLength(1);
      expect(result.content[0]).toHaveProperty('type', 'text');
      expect(result.content[0].text).toContain('Decision logged');
    });
  });

  describe('Error Handling', () => {
    test('should handle unknown tool', async () => {
      await expect(server.callTool('unknown_tool', {}))
        .rejects.toThrow('Unknown tool: unknown_tool');
    });

    test('should handle missing required parameters gracefully', async () => {
      // The current implementation doesn't validate required parameters
      const result = await server.callTool('execute_protocol', {});
      expect(result).toHaveProperty('content');
      expect(result.content[0].json.protocol).toBeUndefined();
    });

    test('should handle invalid context type gracefully', async () => {
      // The current implementation doesn't validate context types
      const result = await server.callTool('get_memory_context', {
        context_type: 'invalid_type'
      });
      expect(result).toHaveProperty('content');
      expect(result.content[0].text).toContain('invalid_type context');
    });
  });
});
