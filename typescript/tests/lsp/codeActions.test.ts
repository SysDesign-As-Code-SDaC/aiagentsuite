/**
 * Tests for LSP Code Actions
 */

describe('LSP Code Actions', () => {
  let mockConnection: any;
  let mockDocuments: any;

  beforeEach(() => {
    jest.clearAllMocks();

    mockConnection = {
      onCodeAction: jest.fn(),
      sendRequest: jest.fn()
    };

    mockDocuments = {
      get: jest.fn()
    };
  });

  describe('Code Action Registration', () => {
    test('should register code action handler', () => {
      // Import the code actions module
      require('../../src/lsp/codeActions');

      expect(mockConnection.onCodeAction).toHaveBeenCalled();
    });
  });

  describe('VDE Principle Code Actions', () => {
    test('should provide VDE principle insertion actions', () => {
      let codeActionHandler: any;
      mockConnection.onCodeAction.mockImplementation((handler: any) => {
        codeActionHandler = handler;
      });

      require('../../src/lsp/codeActions');

      const mockParams = {
        textDocument: { uri: 'file://test.py' },
        range: {
          start: { line: 0, character: 0 },
          end: { line: 0, character: 0 }
        },
        context: {
          diagnostics: []
        }
      };

      const result = codeActionHandler(mockParams);

      expect(result).toEqual([
        {
          title: 'Insert VDE Principle 1: Core Philosophy',
          kind: 'quickfix',
          edit: {
            changes: {
              'file://test.py': [
                {
                  range: {
                    start: { line: 0, character: 0 },
                    end: { line: 0, character: 0 }
                  },
                  newText: '# VDE Principle 1: Core Philosophy\n# The foundation of our development approach\n\n'
                }
              ]
            }
          }
        },
        {
          title: 'Insert VDE Principle 2: Branching Strategy',
          kind: 'quickfix',
          edit: {
            changes: {
              'file://test.py': [
                {
                  range: {
                    start: { line: 0, character: 0 },
                    end: { line: 0, character: 0 }
                  },
                  newText: '# VDE Principle 2: Branching Strategy\n# Structured approach to version control\n\n'
                }
              ]
            }
          }
        },
        {
          title: 'Insert VDE Principle 3: YAGNI',
          kind: 'quickfix',
          edit: {
            changes: {
              'file://test.py': [
                {
                  range: {
                    start: { line: 0, character: 0 },
                    end: { line: 0, character: 0 }
                  },
                  newText: '# VDE Principle 3: YAGNI\n# You Ain\'t Gonna Need It - avoid over-engineering\n\n'
                }
              ]
            }
          }
        }
      ]);
    });
  });

  describe('Protocol Code Actions', () => {
    test('should provide protocol insertion actions', () => {
      let codeActionHandler: any;
      mockConnection.onCodeAction.mockImplementation((handler: any) => {
        codeActionHandler = handler;
      });

      require('../../src/lsp/codeActions');

      const mockParams = {
        textDocument: { uri: 'file://test.py' },
        range: {
          start: { line: 0, character: 0 },
          end: { line: 0, character: 0 }
        },
        context: {
          diagnostics: []
        }
      };

      const result = codeActionHandler(mockParams);

      // Check for protocol actions
      const protocolActions = result.filter((action: any) => 
        action.title.includes('Protocol')
      );
      expect(protocolActions.length).toBeGreaterThan(0);
    });
  });

  describe('Framework Code Actions', () => {
    test('should provide framework integration actions', () => {
      let codeActionHandler: any;
      mockConnection.onCodeAction.mockImplementation((handler: any) => {
        codeActionHandler = handler;
      });

      require('../../src/lsp/codeActions');

      const mockParams = {
        textDocument: { uri: 'file://test.py' },
        range: {
          start: { line: 0, character: 0 },
          end: { line: 0, character: 0 }
        },
        context: {
          diagnostics: []
        }
      };

      const result = codeActionHandler(mockParams);

      // Check for framework actions
      const frameworkActions = result.filter((action: any) => 
        action.title.includes('Framework') || action.title.includes('Constitution')
      );
      expect(frameworkActions.length).toBeGreaterThan(0);
    });
  });

  describe('Diagnostic-based Code Actions', () => {
    test('should provide actions for VDE violations', () => {
      let codeActionHandler: any;
      mockConnection.onCodeAction.mockImplementation((handler: any) => {
        codeActionHandler = handler;
      });

      require('../../src/lsp/codeActions');

      const mockParams = {
        textDocument: { uri: 'file://test.py' },
        range: {
          start: { line: 0, character: 0 },
          end: { line: 0, character: 10 }
        },
        context: {
          diagnostics: [
            {
              code: 'VDE_VIOLATION',
              message: 'Code does not follow VDE principles',
              range: {
                start: { line: 0, character: 0 },
                end: { line: 0, character: 10 }
              }
            }
          ]
        }
      };

      const result = codeActionHandler(mockParams);

      // Should include diagnostic-based actions
      const diagnosticActions = result.filter((action: any) => 
        action.title.includes('Fix VDE violation') || 
        action.title.includes('Apply VDE principles')
      );
      expect(diagnosticActions.length).toBeGreaterThan(0);
    });

    test('should provide actions for protocol violations', () => {
      let codeActionHandler: any;
      mockConnection.onCodeAction.mockImplementation((handler: any) => {
        codeActionHandler = handler;
      });

      require('../../src/lsp/codeActions');

      const mockParams = {
        textDocument: { uri: 'file://test.py' },
        range: {
          start: { line: 0, character: 0 },
          end: { line: 0, character: 10 }
        },
        context: {
          diagnostics: [
            {
              code: 'PROTOCOL_VIOLATION',
              message: 'Code does not follow protocol requirements',
              range: {
                start: { line: 0, character: 0 },
                end: { line: 0, character: 10 }
              }
            }
          ]
        }
      };

      const result = codeActionHandler(mockParams);

      // Should include protocol-specific actions
      const protocolActions = result.filter((action: any) => 
        action.title.includes('Fix protocol violation') || 
        action.title.includes('Apply protocol')
      );
      expect(protocolActions.length).toBeGreaterThan(0);
    });
  });

  describe('Code Action Execution', () => {
    test('should handle VDE principle insertion', () => {
      let codeActionHandler: any;
      mockConnection.onCodeAction.mockImplementation((handler: any) => {
        codeActionHandler = handler;
      });

      require('../../src/lsp/codeActions');

      const mockParams = {
        textDocument: { uri: 'file://test.py' },
        range: {
          start: { line: 0, character: 0 },
          end: { line: 0, character: 0 }
        },
        context: {
          diagnostics: []
        }
      };

      const result = codeActionHandler(mockParams);

      // Find VDE principle action
      const vdeAction = result.find((action: any) => 
        action.title.includes('VDE Principle 1')
      );

      expect(vdeAction).toBeDefined();
      expect(vdeAction.kind).toBe('quickfix');
      expect(vdeAction.edit).toBeDefined();
      expect(vdeAction.edit.changes).toBeDefined();
      expect(vdeAction.edit.changes['file://test.py']).toBeDefined();
      expect(vdeAction.edit.changes['file://test.py'][0].newText).toContain('VDE Principle 1');
    });

    test('should handle protocol insertion', () => {
      let codeActionHandler: any;
      mockConnection.onCodeAction.mockImplementation((handler: any) => {
        codeActionHandler = handler;
      });

      require('../../src/lsp/codeActions');

      const mockParams = {
        textDocument: { uri: 'file://test.py' },
        range: {
          start: { line: 0, character: 0 },
          end: { line: 0, character: 0 }
        },
        context: {
          diagnostics: []
        }
      };

      const result = codeActionHandler(mockParams);

      // Find protocol action
      const protocolAction = result.find((action: any) => 
        action.title.includes('Protocol')
      );

      expect(protocolAction).toBeDefined();
      expect(protocolAction.kind).toBe('quickfix');
      expect(protocolAction.edit).toBeDefined();
      expect(protocolAction.edit.changes).toBeDefined();
      expect(protocolAction.edit.changes['file://test.py']).toBeDefined();
    });
  });

  describe('Error Handling', () => {
    test('should handle missing text document', () => {
      let codeActionHandler: any;
      mockConnection.onCodeAction.mockImplementation((handler: any) => {
        codeActionHandler = handler;
      });

      require('../../src/lsp/codeActions');

      const mockParams = {
        range: {
          start: { line: 0, character: 0 },
          end: { line: 0, character: 0 }
        },
        context: {
          diagnostics: []
        }
      };

      // Should not throw
      expect(() => codeActionHandler(mockParams)).not.toThrow();
    });

    test('should handle missing range', () => {
      let codeActionHandler: any;
      mockConnection.onCodeAction.mockImplementation((handler: any) => {
        codeActionHandler = handler;
      });

      require('../../src/lsp/codeActions');

      const mockParams = {
        textDocument: { uri: 'file://test.py' },
        context: {
          diagnostics: []
        }
      };

      // Should not throw
      expect(() => codeActionHandler(mockParams)).not.toThrow();
    });

    test('should handle missing context', () => {
      let codeActionHandler: any;
      mockConnection.onCodeAction.mockImplementation((handler: any) => {
        codeActionHandler = handler;
      });

      require('../../src/lsp/codeActions');

      const mockParams = {
        textDocument: { uri: 'file://test.py' },
        range: {
          start: { line: 0, character: 0 },
          end: { line: 0, character: 0 }
        }
      };

      // Should not throw
      expect(() => codeActionHandler(mockParams)).not.toThrow();
    });
  });
});
