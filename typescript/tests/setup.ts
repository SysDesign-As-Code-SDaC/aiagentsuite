/**
 * Jest setup file for AI Agent Suite TypeScript tests
 */

// Mock vscode-languageserver modules
jest.mock('vscode-languageserver/node', () => ({
  createConnection: jest.fn(() => ({
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
  })),
  ProposedFeatures: {
    all: 'all'
  },
  InitializeParams: {},
  DidChangeConfigurationNotification: {
    type: 'notification'
  },
  CompletionItemKind: {
    Text: 1,
    Method: 2,
    Function: 3,
    Constructor: 4,
    Field: 5,
    Variable: 6,
    Class: 7,
    Interface: 8,
    Module: 9,
    Property: 10,
    Unit: 11,
    Value: 12,
    Enum: 13,
    Keyword: 14,
    Snippet: 15,
    Color: 16,
    File: 17,
    Reference: 18,
    Folder: 19,
    EnumMember: 20,
    Constant: 21,
    Struct: 22,
    Event: 23,
    Operator: 24,
    TypeParameter: 25
  },
  DiagnosticSeverity: {
    Error: 1,
    Warning: 2,
    Information: 3,
    Hint: 4
  }
}));

jest.mock('vscode-languageserver-textdocument', () => ({
  TextDocument: jest.fn()
}));

// Mock MCP SDK
jest.mock('mcp-sdk', () => ({
  MCPServer: jest.fn().mockImplementation(() => ({
    start: jest.fn(),
    stop: jest.fn(),
    addTool: jest.fn(),
    addResource: jest.fn()
  }))
}));

// Global test utilities
global.createMockConnection = () => ({
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
});

global.createMockDocument = (uri: string, content: string) => ({
  uri,
  languageId: 'python',
  version: 1,
  getText: () => content,
  positionAt: jest.fn(),
  offsetAt: jest.fn()
});

global.createMockPosition = (line: number, character: number) => ({
  line,
  character
});

global.createMockRange = (startLine: number, startChar: number, endLine: number, endChar: number) => ({
  start: { line: startLine, character: startChar },
  end: { line: endLine, character: endChar }
});
