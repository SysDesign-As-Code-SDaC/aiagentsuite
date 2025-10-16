/**
 * Tests for LSP Completions
 */

describe('LSP Completions', () => {
  let mockConnection: any;
  let mockDocuments: any;

  beforeEach(() => {
    jest.clearAllMocks();

    mockConnection = {
      onCompletion: jest.fn(),
      onCompletionResolve: jest.fn()
    };

    mockDocuments = {
      get: jest.fn()
    };
  });

  describe('Completion Registration', () => {
    test('should register completion handler', () => {
      require('../../src/lsp/completions');

      expect(mockConnection.onCompletion).toHaveBeenCalled();
    });

    test('should register completion resolve handler', () => {
      require('../../src/lsp/completions');

      expect(mockConnection.onCompletionResolve).toHaveBeenCalled();
    });
  });

  describe('VDE Principle Completions', () => {
    test('should provide VDE principle completions', () => {
      let completionHandler: any;
      mockConnection.onCompletion.mockImplementation((handler: any) => {
        completionHandler = handler;
      });

      require('../../src/lsp/completions');

      const mockParams = {
        textDocument: { uri: 'file://test.py' },
        position: { line: 0, character: 0 }
      };

      const result = completionHandler(mockParams);

      const vdeCompletions = result.filter((item: any) => 
        item.label.includes('VDE Principle')
      );

      expect(vdeCompletions).toHaveLength(3);
      expect(vdeCompletions[0].label).toBe('VDE Principle 1: Core Philosophy');
      expect(vdeCompletions[1].label).toBe('VDE Principle 2: Branching Strategy');
      expect(vdeCompletions[2].label).toBe('VDE Principle 3: YAGNI');
    });

    test('should have correct completion properties', () => {
      let completionHandler: any;
      mockConnection.onCompletion.mockImplementation((handler: any) => {
        completionHandler = handler;
      });

      require('../../src/lsp/completions');

      const mockParams = {
        textDocument: { uri: 'file://test.py' },
        position: { line: 0, character: 0 }
      };

      const result = completionHandler(mockParams);

      const vdeCompletion = result.find((item: any) => 
        item.label.includes('VDE Principle 1')
      );

      expect(vdeCompletion).toHaveProperty('label');
      expect(vdeCompletion).toHaveProperty('kind', 1); // Text
      expect(vdeCompletion).toHaveProperty('detail');
      expect(vdeCompletion).toHaveProperty('documentation');
      expect(vdeCompletion.detail).toBe('Vibe-Driven Engineering Core Philosophy');
      expect(vdeCompletion.documentation).toBe('The foundation of our development approach');
    });
  });

  describe('Protocol Completions', () => {
    test('should provide protocol completions', () => {
      let completionHandler: any;
      mockConnection.onCompletion.mockImplementation((handler: any) => {
        completionHandler = handler;
      });

      require('../../src/lsp/completions');

      const mockParams = {
        textDocument: { uri: 'file://test.py' },
        position: { line: 0, character: 0 }
      };

      const result = completionHandler(mockParams);

      const protocolCompletions = result.filter((item: any) => 
        item.label.includes('Protocol')
      );

      expect(protocolCompletions.length).toBeGreaterThan(0);
      
      // Check for specific protocols
      const protocolLabels = protocolCompletions.map((item: any) => item.label);
      expect(protocolLabels).toContain('Protocol: Code Review');
      expect(protocolLabels).toContain('Protocol: Testing');
      expect(protocolLabels).toContain('Protocol: Documentation');
    });

    test('should have correct protocol completion properties', () => {
      let completionHandler: any;
      mockConnection.onCompletion.mockImplementation((handler: any) => {
        completionHandler = handler;
      });

      require('../../src/lsp/completions');

      const mockParams = {
        textDocument: { uri: 'file://test.py' },
        position: { line: 0, character: 0 }
      };

      const result = completionHandler(mockParams);

      const protocolCompletion = result.find((item: any) => 
        item.label.includes('Protocol: Code Review')
      );

      expect(protocolCompletion).toHaveProperty('label');
      expect(protocolCompletion).toHaveProperty('kind', 1); // Text
      expect(protocolCompletion).toHaveProperty('detail');
      expect(protocolCompletion).toHaveProperty('documentation');
      expect(protocolCompletion.detail).toBe('Code review protocol for quality assurance');
    });
  });

  describe('Framework Completions', () => {
    test('should provide framework completions', () => {
      let completionHandler: any;
      mockConnection.onCompletion.mockImplementation((handler: any) => {
        completionHandler = handler;
      });

      require('../../src/lsp/completions');

      const mockParams = {
        textDocument: { uri: 'file://test.py' },
        position: { line: 0, character: 0 }
      };

      const result = completionHandler(mockParams);

      const frameworkCompletions = result.filter((item: any) => 
        item.label.includes('Framework') || 
        item.label.includes('Constitution') ||
        item.label.includes('Memory')
      );

      expect(frameworkCompletions.length).toBeGreaterThan(0);
      
      // Check for specific framework completions
      const frameworkLabels = frameworkCompletions.map((item: any) => item.label);
      expect(frameworkLabels).toContain('Framework: Constitution');
      expect(frameworkLabels).toContain('Framework: Memory Bank');
      expect(frameworkLabels).toContain('Framework: Protocol Executor');
    });

    test('should have correct framework completion properties', () => {
      let completionHandler: any;
      mockConnection.onCompletion.mockImplementation((handler: any) => {
        completionHandler = handler;
      });

      require('../../src/lsp/completions');

      const mockParams = {
        textDocument: { uri: 'file://test.py' },
        position: { line: 0, character: 0 }
      };

      const result = completionHandler(mockParams);

      const frameworkCompletion = result.find((item: any) => 
        item.label.includes('Framework: Constitution')
      );

      expect(frameworkCompletion).toHaveProperty('label');
      expect(frameworkCompletion).toHaveProperty('kind', 1); // Text
      expect(frameworkCompletion).toHaveProperty('detail');
      expect(frameworkCompletion).toHaveProperty('documentation');
      expect(frameworkCompletion.detail).toBe('AI Agent Suite Constitution');
    });
  });

  describe('Completion Resolve', () => {
    test('should resolve completion with additional details', () => {
      let resolveHandler: any;
      mockConnection.onCompletionResolve.mockImplementation((handler: any) => {
        resolveHandler = handler;
      });

      require('../../src/lsp/completions');

      const mockCompletion = {
        label: 'VDE Principle 1: Core Philosophy',
        kind: 1,
        detail: 'Vibe-Driven Engineering Core Philosophy',
        documentation: 'The foundation of our development approach'
      };

      const result = resolveHandler(mockCompletion);

      expect(result).toEqual({
        ...mockCompletion,
        insertText: '# VDE Principle 1: Core Philosophy\n# The foundation of our development approach\n\n',
        insertTextFormat: 2, // Snippet
        additionalTextEdits: []
      });
    });

    test('should resolve protocol completion with snippet', () => {
      let resolveHandler: any;
      mockConnection.onCompletionResolve.mockImplementation((handler: any) => {
        resolveHandler = handler;
      });

      require('../../src/lsp/completions');

      const mockCompletion = {
        label: 'Protocol: Code Review',
        kind: 1,
        detail: 'Code review protocol for quality assurance',
        documentation: 'Structured approach to code review'
      };

      const result = resolveHandler(mockCompletion);

      expect(result).toHaveProperty('insertText');
      expect(result).toHaveProperty('insertTextFormat', 2); // Snippet
      expect(result.insertText).toContain('Protocol: Code Review');
    });

    test('should resolve framework completion with snippet', () => {
      let resolveHandler: any;
      mockConnection.onCompletionResolve.mockImplementation((handler: any) => {
        resolveHandler = handler;
      });

      require('../../src/lsp/completions');

      const mockCompletion = {
        label: 'Framework: Constitution',
        kind: 1,
        detail: 'AI Agent Suite Constitution',
        documentation: 'Master constitution for AI agents'
      };

      const result = resolveHandler(mockCompletion);

      expect(result).toHaveProperty('insertText');
      expect(result).toHaveProperty('insertTextFormat', 2); // Snippet
      expect(result.insertText).toContain('Framework: Constitution');
    });
  });

  describe('Context-aware Completions', () => {
    test('should provide different completions based on document type', () => {
      let completionHandler: any;
      mockConnection.onCompletion.mockImplementation((handler: any) => {
        completionHandler = handler;
      });

      require('../../src/lsp/completions');

      // Test Python file
      const pythonParams = {
        textDocument: { uri: 'file://test.py' },
        position: { line: 0, character: 0 }
      };

      const pythonResult = completionHandler(pythonParams);

      // Test Markdown file
      const markdownParams = {
        textDocument: { uri: 'file://test.md' },
        position: { line: 0, character: 0 }
      };

      const markdownResult = completionHandler(markdownParams);

      // Both should return completions
      expect(pythonResult.length).toBeGreaterThan(0);
      expect(markdownResult.length).toBeGreaterThan(0);
    });

    test('should provide completions based on position', () => {
      let completionHandler: any;
      mockConnection.onCompletion.mockImplementation((handler: any) => {
        completionHandler = handler;
      });

      require('../../src/lsp/completions');

      // Test at beginning of line
      const beginParams = {
        textDocument: { uri: 'file://test.py' },
        position: { line: 0, character: 0 }
      };

      const beginResult = completionHandler(beginParams);

      // Test in middle of line
      const middleParams = {
        textDocument: { uri: 'file://test.py' },
        position: { line: 0, character: 10 }
      };

      const middleResult = completionHandler(middleParams);

      // Both should return completions
      expect(beginResult.length).toBeGreaterThan(0);
      expect(middleResult.length).toBeGreaterThan(0);
    });
  });

  describe('Error Handling', () => {
    test('should handle missing text document', () => {
      let completionHandler: any;
      mockConnection.onCompletion.mockImplementation((handler: any) => {
        completionHandler = handler;
      });

      require('../../src/lsp/completions');

      const mockParams = {
        position: { line: 0, character: 0 }
      };

      // Should not throw and return empty array
      const result = completionHandler(mockParams);
      expect(Array.isArray(result)).toBe(true);
    });

    test('should handle missing position', () => {
      let completionHandler: any;
      mockConnection.onCompletion.mockImplementation((handler: any) => {
        completionHandler = handler;
      });

      require('../../src/lsp/completions');

      const mockParams = {
        textDocument: { uri: 'file://test.py' }
      };

      // Should not throw and return empty array
      const result = completionHandler(mockParams);
      expect(Array.isArray(result)).toBe(true);
    });

    test('should handle resolve with missing completion', () => {
      let resolveHandler: any;
      mockConnection.onCompletionResolve.mockImplementation((handler: any) => {
        resolveHandler = handler;
      });

      require('../../src/lsp/completions');

      // Should not throw and return the completion as-is
      const result = resolveHandler({});
      expect(result).toEqual({});
    });
  });
});
