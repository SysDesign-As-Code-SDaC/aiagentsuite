/**
 * Tests for AI Agent Suite MCP Server
 */

describe('MCP Server', () => {
  let mockMCPServer: any;

  beforeEach(() => {
    // Reset all mocks
    jest.clearAllMocks();

    // Create mock MCP server
    mockMCPServer = {
      start: jest.fn(),
      stop: jest.fn(),
      addTool: jest.fn(),
      addResource: jest.fn(),
      handleRequest: jest.fn()
    };
  });

  describe('Server Initialization', () => {
    test('should create MCP server instance', () => {
      // Import the server module
      const { AIAgentSuiteMCPServer } = require('../../src/mcp/server');

      const server = new AIAgentSuiteMCPServer();
      expect(server).toBeDefined();
    });

    test('should have required tools', () => {
      const { AIAgentSuiteMCPServer } = require('../../src/mcp/server');

      const server = new AIAgentSuiteMCPServer();
      const tools = server.getTools();

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
      const { AIAgentSuiteMCPServer } = require('../../src/mcp/server');

      const server = new AIAgentSuiteMCPServer();
      const tools = server.getTools();

      tools.forEach((tool: any) => {
        expect(tool).toHaveProperty('name');
        expect(tool).toHaveProperty('description');
        expect(tool).toHaveProperty('inputSchema');
        expect(tool.inputSchema).toHaveProperty('type', 'object');
      });
    });
  });

  describe('Tool Definitions', () => {
    let server: any;

    beforeEach(() => {
      const { AIAgentSuiteMCPServer } = require('../../src/mcp/server');
      server = new AIAgentSuiteMCPServer();
    });

    test('get_constitution tool should have correct schema', () => {
      const tools = server.getTools();
      const constitutionTool = tools.find((tool: any) => tool.name === 'get_constitution');

      expect(constitutionTool.description).toBe('Get the master AI agent constitution');
      expect(constitutionTool.inputSchema.properties).toEqual({});
      expect(constitutionTool.inputSchema.required).toEqual([]);
    });

    test('list_protocols tool should have correct schema', () => {
      const tools = server.getTools();
      const protocolsTool = tools.find((tool: any) => tool.name === 'list_protocols');

      expect(protocolsTool.description).toBe('List all available protocols');
      expect(protocolsTool.inputSchema.properties).toEqual({});
      expect(protocolsTool.inputSchema.required).toEqual([]);
    });

    test('execute_protocol tool should have correct schema', () => {
      const tools = server.getTools();
      const executeTool = tools.find((tool: any) => tool.name === 'execute_protocol');

      expect(executeTool.description).toBe('Execute a specific protocol with context');
      expect(executeTool.inputSchema.properties).toHaveProperty('protocol_name');
      expect(executeTool.inputSchema.properties).toHaveProperty('context');
      expect(executeTool.inputSchema.required).toEqual(['protocol_name']);
    });

    test('get_memory_context tool should have correct schema', () => {
      const tools = server.getTools();
      const memoryTool = tools.find((tool: any) => tool.name === 'get_memory_context');

      expect(memoryTool.description).toBe('Get memory context of specified type');
      expect(memoryTool.inputSchema.properties).toHaveProperty('context_type');
      expect(memoryTool.inputSchema.required).toEqual(['context_type']);
    });

    test('log_decision tool should have correct schema', () => {
      const tools = server.getTools();
      const decisionTool = tools.find((tool: any) => tool.name === 'log_decision');

      expect(decisionTool.description).toBe('Log a decision with rationale and context');
      expect(decisionTool.inputSchema.properties).toHaveProperty('decision');
      expect(decisionTool.inputSchema.properties).toHaveProperty('rationale');
      expect(decisionTool.inputSchema.properties).toHaveProperty('context');
      expect(decisionTool.inputSchema.required).toEqual(['decision', 'rationale']);
    });
  });

  describe('Tool Execution', () => {
    let server: any;

    beforeEach(() => {
      const { AIAgentSuiteMCPServer } = require('../../src/mcp/server');
      server = new AIAgentSuiteMCPServer();
    });

    test('should execute get_constitution tool', async () => {
      const result = await server.executeTool('get_constitution', {});

      expect(result).toHaveProperty('content');
      expect(result.content).toHaveLength(1);
      expect(result.content[0]).toHaveProperty('type', 'text');
      expect(result.content[0].text).toContain('AI Agent Constitution');
    });

    test('should execute list_protocols tool', async () => {
      const result = await server.executeTool('list_protocols', {});

      expect(result).toHaveProperty('content');
      expect(result.content).toHaveLength(2);
      expect(result.content[0]).toHaveProperty('type', 'text');
      expect(result.content[1]).toHaveProperty('type', 'json');
      expect(result.content[1].json).toHaveProperty('protocols');
    });

    test('should execute execute_protocol tool', async () => {
      const result = await server.executeTool('execute_protocol', {
        protocol_name: 'Test Protocol',
        context: { project: 'test' }
      });

      expect(result).toHaveProperty('content');
      expect(result.content).toHaveLength(2);
      expect(result.content[0]).toHaveProperty('type', 'text');
      expect(result.content[1]).toHaveProperty('type', 'json');
      expect(result.content[1].json).toHaveProperty('protocol', 'Test Protocol');
    });

    test('should execute get_memory_context tool', async () => {
      const result = await server.executeTool('get_memory_context', {
        context_type: 'active'
      });

      expect(result).toHaveProperty('content');
      expect(result.content).toHaveLength(2);
      expect(result.content[0]).toHaveProperty('type', 'text');
      expect(result.content[1]).toHaveProperty('type', 'json');
      expect(result.content[1].json).toHaveProperty('type', 'active');
    });

    test('should execute log_decision tool', async () => {
      const result = await server.executeTool('log_decision', {
        decision: 'Use FastAPI for backend',
        rationale: 'Excellent performance and documentation',
        context: { project: 'test' }
      });

      expect(result).toHaveProperty('content');
      expect(result.content).toHaveLength(1);
      expect(result.content[0]).toHaveProperty('type', 'text');
      expect(result.content[0].text).toContain('Successfully logged decision');
    });
  });

  describe('Error Handling', () => {
    let server: any;

    beforeEach(() => {
      const { AIAgentSuiteMCPServer } = require('../../src/mcp/server');
      server = new AIAgentSuiteMCPServer();
    });

    test('should handle unknown tool', async () => {
      const result = await server.executeTool('unknown_tool', {});

      expect(result).toHaveProperty('content');
      expect(result.content).toHaveLength(1);
      expect(result.content[0]).toHaveProperty('type', 'text');
      expect(result.content[0].text).toContain('Unknown tool');
    });

    test('should handle missing required parameters', async () => {
      const result = await server.executeTool('execute_protocol', {});

      expect(result).toHaveProperty('content');
      expect(result.content).toHaveLength(1);
      expect(result.content[0]).toHaveProperty('type', 'text');
      expect(result.content[0].text).toContain('protocol_name is required');
    });

    test('should handle invalid context type', async () => {
      const result = await server.executeTool('get_memory_context', {
        context_type: 'invalid_type'
      });

      expect(result).toHaveProperty('content');
      expect(result.content).toHaveLength(1);
      expect(result.content[0]).toHaveProperty('type', 'text');
      expect(result.content[0].text).toContain('context_type must be one of');
    });

    test('should handle missing decision parameters', async () => {
      const result = await server.executeTool('log_decision', {
        decision: 'Test decision'
        // Missing rationale
      });

      expect(result).toHaveProperty('content');
      expect(result.content).toHaveLength(1);
      expect(result.content[0]).toHaveProperty('type', 'text');
      expect(result.content[0].text).toContain('decision and rationale are required');
    });
  });

  describe('Resource Management', () => {
    let server: any;

    beforeEach(() => {
      const { AIAgentSuiteMCPServer } = require('../../src/mcp/server');
      server = new AIAgentSuiteMCPServer();
    });

    test('should list available resources', async () => {
      const resources = await server.listResources();

      expect(Array.isArray(resources)).toBe(true);
      expect(resources.length).toBeGreaterThan(0);
      
      // Should have constitution resource
      const constitutionResource = resources.find((r: any) => r.uri === 'framework://constitution');
      expect(constitutionResource).toBeDefined();
      expect(constitutionResource.name).toBe('AI Agent Constitution');
      expect(constitutionResource.mimeType).toBe('text/markdown');
    });

    test('should read constitution resource', async () => {
      const content = await server.readResource('framework://constitution');

      expect(content).toBeDefined();
      expect(content.uri).toBe('framework://constitution');
      expect(content.mimeType).toBe('text/markdown');
      expect(content.text).toContain('AI Agent Constitution');
    });

    test('should read principle resource', async () => {
      const content = await server.readResource('framework://principles/core_philosophy');

      expect(content).toBeDefined();
      expect(content.uri).toBe('framework://principles/core_philosophy');
      expect(content.mimeType).toBe('text/markdown');
      expect(content.text).toContain('Core Philosophy');
    });

    test('should return null for unknown resource', async () => {
      const content = await server.readResource('framework://unknown/resource');

      expect(content).toBeNull();
    });
  });

  describe('Server Lifecycle', () => {
    let server: any;

    beforeEach(() => {
      const { AIAgentSuiteMCPServer } = require('../../src/mcp/server');
      server = new AIAgentSuiteMCPServer();
    });

    test('should start server', async () => {
      await server.start();

      // Server should be running
      expect(server.isRunning()).toBe(true);
    });

    test('should stop server', async () => {
      await server.start();
      await server.stop();

      // Server should be stopped
      expect(server.isRunning()).toBe(false);
    });

    test('should handle multiple start/stop cycles', async () => {
      await server.start();
      expect(server.isRunning()).toBe(true);

      await server.stop();
      expect(server.isRunning()).toBe(false);

      await server.start();
      expect(server.isRunning()).toBe(true);

      await server.stop();
      expect(server.isRunning()).toBe(false);
    });
  });

  describe('Concurrent Operations', () => {
    let server: any;

    beforeEach(() => {
      const { AIAgentSuiteMCPServer } = require('../../src/mcp/server');
      server = new AIAgentSuiteMCPServer();
    });

    test('should handle concurrent tool executions', async () => {
      const promises = [
        server.executeTool('get_constitution', {}),
        server.executeTool('list_protocols', {}),
        server.executeTool('get_memory_context', { context_type: 'active' })
      ];

      const results = await Promise.all(promises);

      expect(results).toHaveLength(3);
      results.forEach(result => {
        expect(result).toHaveProperty('content');
        expect(Array.isArray(result.content)).toBe(true);
      });
    });

    test('should handle concurrent resource reads', async () => {
      const promises = [
        server.readResource('framework://constitution'),
        server.readResource('framework://principles/core_philosophy'),
        server.listResources()
      ];

      const results = await Promise.all(promises);

      expect(results).toHaveLength(3);
      expect(results[0]).toBeDefined(); // constitution
      expect(results[1]).toBeDefined(); // principle
      expect(Array.isArray(results[2])).toBe(true); // resource list
    });
  });
});
