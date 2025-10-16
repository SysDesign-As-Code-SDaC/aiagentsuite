/**
 * Tests for AI Agent Suite LSP Server
 */

import { createConnection, ProposedFeatures } from 'vscode-languageserver/node';
import { TextDocuments } from 'vscode-languageserver/node';
import { TextDocument } from 'vscode-languageserver-textdocument';

// Mock the modules
jest.mock('vscode-languageserver/node');
jest.mock('vscode-languageserver-textdocument');

describe('LSP Server', () => {
  let mockConnection: any;
  let mockDocuments: any;

  beforeEach(() => {
    // Reset all mocks
    jest.clearAllMocks();

    // Create mock connection
    mockConnection = {
      onInitialize: jest.fn(),
      onInitialized: jest.fn(),
      onDidChangeConfiguration: jest.fn(),
      onDidChangeTextDocument: jest.fn(),
      onDidOpenTextDocument: jest.fn(),
      onDidCloseTextDocument: jest.fn(),
      onCompletion: jest.fn(),
      onCompletionResolve: jest.fn(),
      onHover: jest.fn(),
      sendDiagnostics: jest.fn(),
      listen: jest.fn(),
      sendNotification: jest.fn(),
      sendRequest: jest.fn()
    };

    // Create mock documents
    mockDocuments = {
      onDidChangeContent: jest.fn(),
      onDidOpen: jest.fn(),
      onDidClose: jest.fn(),
      get: jest.fn(),
      all: jest.fn()
    };

    // Mock the createConnection function
    (createConnection as jest.Mock).mockReturnValue(mockConnection);
    (TextDocuments as jest.Mock).mockImplementation(() => mockDocuments);
  });

  describe('Server Initialization', () => {
    test('should create connection with proposed features', () => {
      // Import the server module to trigger initialization
      require('../../src/lsp/server');

      expect(createConnection).toHaveBeenCalledWith(ProposedFeatures.all);
    });

    test('should set up document manager', () => {
      require('../../src/lsp/server');

      expect(TextDocuments).toHaveBeenCalledWith(TextDocument);
    });

    test('should register initialize handler', () => {
      require('../../src/lsp/server');

      expect(mockConnection.onInitialize).toHaveBeenCalled();
    });

    test('should register initialized handler', () => {
      require('../../src/lsp/server');

      expect(mockConnection.onInitialized).toHaveBeenCalled();
    });

    test('should register configuration change handler', () => {
      require('../../src/lsp/server');

      expect(mockConnection.onDidChangeConfiguration).toHaveBeenCalled();
    });

    test('should register text document handlers', () => {
      require('../../src/lsp/server');

      expect(mockConnection.onDidChangeTextDocument).toHaveBeenCalled();
      expect(mockConnection.onDidOpenTextDocument).toHaveBeenCalled();
      expect(mockConnection.onDidCloseTextDocument).toHaveBeenCalled();
    });

    test('should register completion handlers', () => {
      require('../../src/lsp/server');

      expect(mockConnection.onCompletion).toHaveBeenCalled();
      expect(mockConnection.onCompletionResolve).toHaveBeenCalled();
    });

    test('should register hover handler', () => {
      require('../../src/lsp/server');

      expect(mockConnection.onHover).toHaveBeenCalled();
    });
  });

  describe('Initialize Handler', () => {
    test('should return server capabilities', () => {
      let initializeHandler: any;
      mockConnection.onInitialize.mockImplementation((handler: any) => {
        initializeHandler = handler;
      });

      require('../../src/lsp/server');

      const mockParams = {
        capabilities: {
          workspace: {
            configuration: true,
            workspaceFolders: true
          }
        }
      };

      const result = initializeHandler(mockParams);

      expect(result).toEqual({
        capabilities: {
          textDocumentSync: 1,
          completionProvider: {
            resolveProvider: true,
            triggerCharacters: ['.', '@', '#']
          },
          hoverProvider: true,
          diagnosticProvider: {
            interFileDependencies: false,
            workspaceDiagnostics: false
          }
        }
      });
    });

    test('should handle missing workspace capabilities', () => {
      let initializeHandler: any;
      mockConnection.onInitialize.mockImplementation((handler: any) => {
        initializeHandler = handler;
      });

      require('../../src/lsp/server');

      const mockParams = {
        capabilities: {}
      };

      const result = initializeHandler(mockParams);

      expect(result).toEqual({
        capabilities: {
          textDocumentSync: 1,
          completionProvider: {
            resolveProvider: true,
            triggerCharacters: ['.', '@', '#']
          },
          hoverProvider: true,
          diagnosticProvider: {
            interFileDependencies: false,
            workspaceDiagnostics: false
          }
        }
      });
    });
  });

  describe('Completion Handler', () => {
    test('should provide VDE principle completions', () => {
      let completionHandler: any;
      mockConnection.onCompletion.mockImplementation((handler: any) => {
        completionHandler = handler;
      });

      require('../../src/lsp/server');

      const mockParams = {
        textDocument: { uri: 'file://test.py' },
        position: { line: 0, character: 0 }
      };

      const result = completionHandler(mockParams);

      expect(result).toEqual([
        {
          label: 'VDE Principle 1: Core Philosophy',
          kind: 1, // Text
          detail: 'Vibe-Driven Engineering Core Philosophy',
          documentation: 'The foundation of our development approach'
        },
        {
          label: 'VDE Principle 2: Branching Strategy',
          kind: 1,
          detail: 'Git branching and commit strategy',
          documentation: 'Structured approach to version control'
        },
        {
          label: 'VDE Principle 3: YAGNI',
          kind: 1,
          detail: 'You Ain\'t Gonna Need It',
          documentation: 'Avoid over-engineering and focus on current needs'
        }
      ]);
    });

    test('should provide protocol completions', () => {
      let completionHandler: any;
      mockConnection.onCompletion.mockImplementation((handler: any) => {
        completionHandler = handler;
      });

      require('../../src/lsp/server');

      const mockParams = {
        textDocument: { uri: 'file://test.py' },
        position: { line: 0, character: 0 }
      };

      const result = completionHandler(mockParams);

      // Check that protocol completions are included
      const protocolCompletions = result.filter((item: any) => 
        item.label.includes('Protocol')
      );
      expect(protocolCompletions.length).toBeGreaterThan(0);
    });

    test('should provide framework completions', () => {
      let completionHandler: any;
      mockConnection.onCompletion.mockImplementation((handler: any) => {
        completionHandler = handler;
      });

      require('../../src/lsp/server');

      const mockParams = {
        textDocument: { uri: 'file://test.py' },
        position: { line: 0, character: 0 }
      };

      const result = completionHandler(mockParams);

      // Check that framework completions are included
      const frameworkCompletions = result.filter((item: any) => 
        item.label.includes('Framework') || item.label.includes('Constitution')
      );
      expect(frameworkCompletions.length).toBeGreaterThan(0);
    });
  });

  describe('Hover Handler', () => {
    test('should provide VDE principle hover information', () => {
      let hoverHandler: any;
      mockConnection.onHover.mockImplementation((handler: any) => {
        hoverHandler = handler;
      });

      require('../../src/lsp/server');

      const mockParams = {
        textDocument: { uri: 'file://test.py' },
        position: { line: 0, character: 0 }
      };

      const result = hoverHandler(mockParams);

      expect(result).toEqual({
        contents: {
          kind: 'markdown',
          value: '**AI Agent Suite Framework**\n\nThis framework provides VDE principles, protocols, and tools for AI-assisted development.'
        }
      });
    });
  });

  describe('Diagnostic Handler', () => {
    test('should send empty diagnostics on text change', () => {
      let textChangeHandler: any;
      mockConnection.onDidChangeTextDocument.mockImplementation((handler: any) => {
        textChangeHandler = handler;
      });

      require('../../src/lsp/server');

      const mockParams = {
        textDocument: { uri: 'file://test.py' },
        contentChanges: []
      };

      textChangeHandler(mockParams);

      expect(mockConnection.sendDiagnostics).toHaveBeenCalledWith({
        uri: 'file://test.py',
        diagnostics: []
      });
    });
  });

  describe('Configuration Handler', () => {
    test('should handle configuration changes', () => {
      let configHandler: any;
      mockConnection.onDidChangeConfiguration.mockImplementation((handler: any) => {
        configHandler = handler;
      });

      require('../../src/lsp/server');

      const mockParams = {
        settings: {
          aiagentsuite: {
            enableVDE: true,
            enableProtocols: true
          }
        }
      };

      // Should not throw
      expect(() => configHandler(mockParams)).not.toThrow();
    });
  });

  describe('Document Handlers', () => {
    test('should handle document open', () => {
      let documentOpenHandler: any;
      mockConnection.onDidOpenTextDocument.mockImplementation((handler: any) => {
        documentOpenHandler = handler;
      });

      require('../../src/lsp/server');

      const mockParams = {
        textDocument: {
          uri: 'file://test.py',
          languageId: 'python',
          version: 1,
          text: 'print("Hello, World!")'
        }
      };

      // Should not throw
      expect(() => documentOpenHandler(mockParams)).not.toThrow();
    });

    test('should handle document close', () => {
      let documentCloseHandler: any;
      mockConnection.onDidCloseTextDocument.mockImplementation((handler: any) => {
        documentCloseHandler = handler;
      });

      require('../../src/lsp/server');

      const mockParams = {
        textDocument: {
          uri: 'file://test.py'
        }
      };

      // Should not throw
      expect(() => documentCloseHandler(mockParams)).not.toThrow();
    });
  });

  describe('Server Lifecycle', () => {
    test('should start listening for connections', () => {
      require('../../src/lsp/server');

      expect(mockConnection.listen).toHaveBeenCalled();
    });
  });
});
