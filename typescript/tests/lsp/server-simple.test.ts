/**
 * Simple tests for AI Agent Suite LSP Server
 */

describe('LSP Server', () => {
  test('should have server file', () => {
    // Test that the server file exists and can be read
    const fs = require('fs');
    const path = require('path');
    
    const serverPath = path.join(__dirname, '../../src/lsp/server.ts');
    expect(fs.existsSync(serverPath)).toBe(true);
    
    const content = fs.readFileSync(serverPath, 'utf8');
    expect(content).toContain('createConnection');
    expect(content).toContain('TextDocuments');
    expect(content).toContain('onInitialize');
  });

  test('should have proper TypeScript structure', () => {
    // Test that the server file has proper TypeScript structure
    const fs = require('fs');
    const path = require('path');
    
    const serverPath = path.join(__dirname, '../../src/lsp/server.ts');
    const content = fs.readFileSync(serverPath, 'utf8');
    
    // Check for key LSP server components
    expect(content).toContain('import');
    expect(content).toContain('connection.onInitialize');
    expect(content).toContain('connection.onCompletion');
    expect(content).toContain('connection.onHover');
  });
});
