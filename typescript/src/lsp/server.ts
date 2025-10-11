/**
 * AI Agent Suite LSP Server
 *
 * Provides language server capabilities for VDE principle compliance,
 * protocol-driven development, and framework integration.
 */

import {
  createConnection,
  TextDocuments,
  ProposedFeatures,
  InitializeParams,
  DidChangeConfigurationNotification,
  CompletionItem,
  CompletionItemKind,
  TextDocumentPositionParams,
  Hover,
  Diagnostic,
  DiagnosticSeverity
} from 'vscode-languageserver/node';

import { TextDocument } from 'vscode-languageserver-textdocument';

// Create a connection for the server
const connection = createConnection(ProposedFeatures.all);

// Create a simple text document manager
const documents: TextDocuments<TextDocument> = new TextDocuments(TextDocument);

let hasConfigurationCapability = false;
let hasWorkspaceFolderCapability = false;

connection.onInitialize((params: InitializeParams) => {
  const capabilities = params.capabilities;

  // Does the client support the `workspace/configuration` request?
  hasConfigurationCapability = !!(
    capabilities.workspace && !!capabilities.workspace.configuration
  );

  // Does the client support workspace folders?
  hasWorkspaceFolderCapability = !!(
    capabilities.workspace && !!capabilities.workspace.workspaceFolders
  );

  return {
    capabilities: {
      textDocumentSync: 1, // Full sync
      completionProvider: {
        resolveProvider: true,
        triggerCharacters: ['.']
      },
      hoverProvider: true,
      codeActionProvider: true,
      diagnosticProvider: {
        interFileDependencies: false,
        workspaceDiagnostics: false
      }
    }
  };
});

connection.onInitialized(() => {
  if (hasConfigurationCapability) {
    // Register for all configuration changes
    connection.client.register(DidChangeConfigurationNotification.type, undefined);
  }
});

// Handle completion requests
connection.onCompletion(
  (_textDocumentPosition: TextDocumentPositionParams): CompletionItem[] => {
    return [
      {
        label: 'getConstitution',
        kind: CompletionItemKind.Function,
        detail: 'Get AI Agent Constitution',
        documentation: 'Access the master AI agent constitution for guidance'
      },
      {
        label: 'executeProtocol',
        kind: CompletionItemKind.Function,
        detail: 'Execute Framework Protocol',
        documentation: 'Execute a specific VDE protocol with given context'
      },
      {
        label: 'logDecision',
        kind: CompletionItemKind.Function,
        detail: 'Log Architectural Decision',
        documentation: 'Log an architectural or implementation decision'
      }
    ];
  }
);

// Handle completion resolve requests
connection.onCompletionResolve((item: CompletionItem): CompletionItem => {
  return item;
});

// Handle hover requests
connection.onHover((params: TextDocumentPositionParams): Hover | null => {
  const document = documents.get(params.textDocument.uri);
  if (!document) {
    return null;
  }

  // Basic hover implementation - could be enhanced to detect framework keywords
  const word = getWordAtPosition(document, params.position);
  if (word === 'constitution' || word === 'protocol') {
    return {
      contents: {
        kind: 'markdown',
        value: `**${word}**: Part of the AI Agent Suite framework for VDE development.`
      }
    };
  }

  return null;
});

// Handle diagnostics
connection.onDocumentDiagnostic(() => {
  // Basic diagnostic implementation - could check for VDE principle violations
  return {
    kind: 'full',
    items: []
  };
});

// Utility function to get word at position
function getWordAtPosition(document: TextDocument, position: { line: number; character: number }): string {
  const line = document.getText({
    start: { line: position.line, character: 0 },
    end: { line: position.line, character: Number.MAX_VALUE }
  });

  const wordRegex = /\b\w+\b/g;
  let match;
  while ((match = wordRegex.exec(line)) !== null) {
    const start = match.index;
    const end = start + match[0].length;
    if (position.character >= start && position.character <= end) {
      return match[0];
    }
  }

  return '';
}

// Make the text document manager listen on the connection
documents.listen(connection);

// Listen on the connection
connection.listen();