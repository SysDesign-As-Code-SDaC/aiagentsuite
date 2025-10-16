/**
 * Tests for LSP Diagnostics
 */

describe('LSP Diagnostics', () => {
  let mockConnection: any;
  let mockDocuments: any;

  beforeEach(() => {
    jest.clearAllMocks();

    mockConnection = {
      onDidChangeTextDocument: jest.fn(),
      sendDiagnostics: jest.fn()
    };

    mockDocuments = {
      get: jest.fn()
    };
  });

  describe('Diagnostic Registration', () => {
    test('should register text document change handler', () => {
      require('../../src/lsp/diagnostics');

      expect(mockConnection.onDidChangeTextDocument).toHaveBeenCalled();
    });
  });

  describe('VDE Principle Diagnostics', () => {
    test('should detect VDE principle violations', () => {
      let changeHandler: any;
      mockConnection.onDidChangeTextDocument.mockImplementation((handler: any) => {
        changeHandler = handler;
      });

      require('../../src/lsp/diagnostics');

      const mockParams = {
        textDocument: {
          uri: 'file://test.py',
          version: 1
        },
        contentChanges: [
          {
            text: 'def bad_function():\n    pass  # No documentation, no type hints'
          }
        ]
      };

      changeHandler(mockParams);

      expect(mockConnection.sendDiagnostics).toHaveBeenCalledWith({
        uri: 'file://test.py',
        diagnostics: expect.arrayContaining([
          expect.objectContaining({
            code: 'VDE_VIOLATION',
            message: expect.stringContaining('VDE principle violation'),
            severity: 2, // Warning
            range: expect.any(Object)
          })
        ])
      });
    });

    test('should detect missing documentation', () => {
      let changeHandler: any;
      mockConnection.onDidChangeTextDocument.mockImplementation((handler: any) => {
        changeHandler = handler;
      });

      require('../../src/lsp/diagnostics');

      const mockParams = {
        textDocument: {
          uri: 'file://test.py',
          version: 1
        },
        contentChanges: [
          {
            text: 'def undocumented_function():\n    return "no docstring"'
          }
        ]
      };

      changeHandler(mockParams);

      expect(mockConnection.sendDiagnostics).toHaveBeenCalledWith({
        uri: 'file://test.py',
        diagnostics: expect.arrayContaining([
          expect.objectContaining({
            code: 'MISSING_DOCSTRING',
            message: expect.stringContaining('Missing docstring'),
            severity: 2, // Warning
            range: expect.any(Object)
          })
        ])
      });
    });

    test('should detect missing type hints', () => {
      let changeHandler: any;
      mockConnection.onDidChangeTextDocument.mockImplementation((handler: any) => {
        changeHandler = handler;
      });

      require('../../src/lsp/diagnostics');

      const mockParams = {
        textDocument: {
          uri: 'file://test.py',
          version: 1
        },
        contentChanges: [
          {
            text: 'def untyped_function(param):\n    return param + 1'
          }
        ]
      };

      changeHandler(mockParams);

      expect(mockConnection.sendDiagnostics).toHaveBeenCalledWith({
        uri: 'file://test.py',
        diagnostics: expect.arrayContaining([
          expect.objectContaining({
            code: 'MISSING_TYPE_HINTS',
            message: expect.stringContaining('Missing type hints'),
            severity: 2, // Warning
            range: expect.any(Object)
          })
        ])
      });
    });
  });

  describe('Protocol Compliance Diagnostics', () => {
    test('should detect protocol violations', () => {
      let changeHandler: any;
      mockConnection.onDidChangeTextDocument.mockImplementation((handler: any) => {
        changeHandler = handler;
      });

      require('../../src/lsp/diagnostics');

      const mockParams = {
        textDocument: {
          uri: 'file://test.py',
          version: 1
        },
        contentChanges: [
          {
            text: 'class BadClass:\n    def __init__(self):\n        self._private = "exposed"  # Protocol violation'
          }
        ]
      };

      changeHandler(mockParams);

      expect(mockConnection.sendDiagnostics).toHaveBeenCalledWith({
        uri: 'file://test.py',
        diagnostics: expect.arrayContaining([
          expect.objectContaining({
            code: 'PROTOCOL_VIOLATION',
            message: expect.stringContaining('Protocol violation'),
            severity: 2, // Warning
            range: expect.any(Object)
          })
        ])
      });
    });

    test('should detect security violations', () => {
      let changeHandler: any;
      mockConnection.onDidChangeTextDocument.mockImplementation((handler: any) => {
        changeHandler = handler;
      });

      require('../../src/lsp/diagnostics');

      const mockParams = {
        textDocument: {
          uri: 'file://test.py',
          version: 1
        },
        contentChanges: [
          {
            text: 'import os\nos.system("rm -rf /")  # Security violation'
          }
        ]
      };

      changeHandler(mockParams);

      expect(mockConnection.sendDiagnostics).toHaveBeenCalledWith({
        uri: 'file://test.py',
        diagnostics: expect.arrayContaining([
          expect.objectContaining({
            code: 'SECURITY_VIOLATION',
            message: expect.stringContaining('Security violation'),
            severity: 1, // Error
            range: expect.any(Object)
          })
        ])
      });
    });
  });

  describe('Code Quality Diagnostics', () => {
    test('should detect code complexity issues', () => {
      let changeHandler: any;
      mockConnection.onDidChangeTextDocument.mockImplementation((handler: any) => {
        changeHandler = handler;
      });

      require('../../src/lsp/diagnostics');

      const mockParams = {
        textDocument: {
          uri: 'file://test.py',
          version: 1
        },
        contentChanges: [
          {
            text: 'def complex_function():\n    if True:\n        if True:\n            if True:\n                if True:\n                    if True:\n                        return "too complex"'
          }
        ]
      };

      changeHandler(mockParams);

      expect(mockConnection.sendDiagnostics).toHaveBeenCalledWith({
        uri: 'file://test.py',
        diagnostics: expect.arrayContaining([
          expect.objectContaining({
            code: 'COMPLEXITY_VIOLATION',
            message: expect.stringContaining('High complexity'),
            severity: 2, // Warning
            range: expect.any(Object)
          })
        ])
      });
    });

    test('should detect naming convention violations', () => {
      let changeHandler: any;
      mockConnection.onDidChangeTextDocument.mockImplementation((handler: any) => {
        changeHandler = handler;
      });

      require('../../src/lsp/diagnostics');

      const mockParams = {
        textDocument: {
          uri: 'file://test.py',
          version: 1
        },
        contentChanges: [
          {
            text: 'def BadFunctionName():  # Should be snake_case\n    pass'
          }
        ]
      };

      changeHandler(mockParams);

      expect(mockConnection.sendDiagnostics).toHaveBeenCalledWith({
        uri: 'file://test.py',
        diagnostics: expect.arrayContaining([
          expect.objectContaining({
            code: 'NAMING_VIOLATION',
            message: expect.stringContaining('Naming convention violation'),
            severity: 2, // Warning
            range: expect.any(Object)
          })
        ])
      });
    });
  });

  describe('Framework Integration Diagnostics', () => {
    test('should detect framework usage issues', () => {
      let changeHandler: any;
      mockConnection.onDidChangeTextDocument.mockImplementation((handler: any) => {
        changeHandler = handler;
      });

      require('../../src/lsp/diagnostics');

      const mockParams = {
        textDocument: {
          uri: 'file://test.py',
          version: 1
        },
        contentChanges: [
          {
            text: 'from aiagentsuite import FrameworkManager\n# Missing proper initialization'
          }
        ]
      };

      changeHandler(mockParams);

      expect(mockConnection.sendDiagnostics).toHaveBeenCalledWith({
        uri: 'file://test.py',
        diagnostics: expect.arrayContaining([
          expect.objectContaining({
            code: 'FRAMEWORK_USAGE',
            message: expect.stringContaining('Framework usage issue'),
            severity: 2, // Warning
            range: expect.any(Object)
          })
        ])
      });
    });

    test('should detect memory bank usage issues', () => {
      let changeHandler: any;
      mockConnection.onDidChangeTextDocument.mockImplementation((handler: any) => {
        changeHandler = handler;
      });

      require('../../src/lsp/diagnostics');

      const mockParams = {
        textDocument: {
          uri: 'file://test.py',
          version: 1
        },
        contentChanges: [
          {
            text: 'from aiagentsuite.memory_bank import MemoryBank\n# Missing proper context management'
          }
        ]
      };

      changeHandler(mockParams);

      expect(mockConnection.sendDiagnostics).toHaveBeenCalledWith({
        uri: 'file://test.py',
        diagnostics: expect.arrayContaining([
          expect.objectContaining({
            code: 'MEMORY_BANK_USAGE',
            message: expect.stringContaining('Memory bank usage issue'),
            severity: 2, // Warning
            range: expect.any(Object)
          })
        ])
      });
    });
  });

  describe('Diagnostic Severity Levels', () => {
    test('should use appropriate severity levels', () => {
      let changeHandler: any;
      mockConnection.onDidChangeTextDocument.mockImplementation((handler: any) => {
        changeHandler = handler;
      });

      require('../../src/lsp/diagnostics');

      const mockParams = {
        textDocument: {
          uri: 'file://test.py',
          version: 1
        },
        contentChanges: [
          {
            text: 'import os\nos.system("rm -rf /")\ndef BadFunction():\n    pass'
          }
        ]
      };

      changeHandler(mockParams);

      expect(mockConnection.sendDiagnostics).toHaveBeenCalledWith({
        uri: 'file://test.py',
        diagnostics: expect.arrayContaining([
          expect.objectContaining({
            code: 'SECURITY_VIOLATION',
            severity: 1 // Error
          }),
          expect.objectContaining({
            code: 'NAMING_VIOLATION',
            severity: 2 // Warning
          })
        ])
      });
    });
  });

  describe('Error Handling', () => {
    test('should handle missing text document', () => {
      let changeHandler: any;
      mockConnection.onDidChangeTextDocument.mockImplementation((handler: any) => {
        changeHandler = handler;
      });

      require('../../src/lsp/diagnostics');

      const mockParams = {
        contentChanges: [
          {
            text: 'test content'
          }
        ]
      };

      // Should not throw
      expect(() => changeHandler(mockParams)).not.toThrow();
    });

    test('should handle missing content changes', () => {
      let changeHandler: any;
      mockConnection.onDidChangeTextDocument.mockImplementation((handler: any) => {
        changeHandler = handler;
      });

      require('../../src/lsp/diagnostics');

      const mockParams = {
        textDocument: {
          uri: 'file://test.py',
          version: 1
        }
      };

      // Should not throw
      expect(() => changeHandler(mockParams)).not.toThrow();
    });

    test('should handle empty content changes', () => {
      let changeHandler: any;
      mockConnection.onDidChangeTextDocument.mockImplementation((handler: any) => {
        changeHandler = handler;
      });

      require('../../src/lsp/diagnostics');

      const mockParams = {
        textDocument: {
          uri: 'file://test.py',
          version: 1
        },
        contentChanges: []
      };

      // Should not throw
      expect(() => changeHandler(mockParams)).not.toThrow();
    });
  });

  describe('Performance', () => {
    test('should handle large documents efficiently', () => {
      let changeHandler: any;
      mockConnection.onDidChangeTextDocument.mockImplementation((handler: any) => {
        changeHandler = handler;
      });

      require('../../src/lsp/diagnostics');

      const largeContent = 'def test():\n    pass\n'.repeat(1000);

      const mockParams = {
        textDocument: {
          uri: 'file://test.py',
          version: 1
        },
        contentChanges: [
          {
            text: largeContent
          }
        ]
      };

      const startTime = Date.now();
      changeHandler(mockParams);
      const endTime = Date.now();

      // Should complete within reasonable time (less than 1 second)
      expect(endTime - startTime).toBeLessThan(1000);
    });
  });
});
