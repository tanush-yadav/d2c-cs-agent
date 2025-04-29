#!/usr/bin/env node

/**
 * Entry point for the Shopify MCP server
 */
import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { registerAllTools } from './tools/index.js';
import Logger from './utils/logger.js';

const logger = new Logger('Main');

/**
 * Initialize and start the MCP server
 */
async function main(): Promise<void> {
  logger.info('Starting Shopify MCP server');

  // Create MCP server
  const server = new McpServer({
    name: 'shopify-tools',
    version: '1.0.1',
  });

  try {
    // Register all tools with the server
    registerAllTools(server);

    // Start the server with stdio transport
    const transport = new StdioServerTransport();
    await server.listen(transport);

    logger.info('Shopify MCP server started successfully');
  } catch (error) {
    logger.error('Error starting Shopify MCP server', {
      error: error instanceof Error ? error.message : String(error),
      stack: error instanceof Error ? error.stack : undefined,
    });
    process.exit(1);
  }
}

// Start the server
main().catch(error => {
  console.error('Unhandled error in main process:', error);
  process.exit(1);
});
